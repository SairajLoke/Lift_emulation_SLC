import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import time

from lift_utils import MIN_FLOOR, MAX_FLOOR, LIFT_CALL, FLOOR_REQUEST
from sai_slc_driver import run_slc_driver
from lift_utils import LIFT_SYSTEM

import traceback

def run_merged_gui(request_list, lift_obj: LIFT_SYSTEM, stop_event=None):
    root = None
    direction_relative = {True: "Above", False: "Below"}
    direction_name = {True: "Up", False: "Down"}

    try:
        def save_to_file():
            with open("request_list.json", "w") as f:
                json.dump(request_list, f, indent=4)
            messagebox.showinfo("Saved", "Requests saved to request_list.json")

        def add_request():
            raw_input = floor_entry.get().strip()
            if not raw_input.isdigit():
                messagebox.showerror("Invalid input", "Floor number must be a positive integer.")
                return
            floor = int(raw_input)
            direction = dir_var.get()
            if floor < MIN_FLOOR or floor > MAX_FLOOR:
                messagebox.showerror("Invalid input", f"Floor must be between {MIN_FLOOR} and {MAX_FLOOR}")
                return
            req_msg = (LIFT_CALL, floor, direction)
            lift_obj.previous_required_direction = direction
            request_list.append(req_msg)
            floor_entry.delete(0, tk.END)

        def add_floor_request():
            raw_input = floor_req_entry.get().strip()
            if not raw_input.isdigit():
                messagebox.showerror("Invalid input", "Floor number must be a positive integer.")
                return
            floor = int(raw_input)
            if floor < MIN_FLOOR or floor > MAX_FLOOR:
                messagebox.showerror("Invalid input", f"Floor must be between {MIN_FLOOR} and {MAX_FLOOR}")
                return
            if (lift_obj.previous_required_direction == (floor > lift_obj.current_floor)) or \
                (len(request_list) != 0) or \
                    (lift_obj.current_state_index == 0)  or \
                        (lift_obj.previous_required_direction ==None): 
                #NOTE: above conditions cover:
                 # allow invalid direction floor reqs if at least 1 valid floor num
                 # allow invalid direction floor reqs if lift is in waiting state after floor waiting time exceeded
                    #waiting state will allow invalid direction floor reqs

                req_msg = (FLOOR_REQUEST, floor, lift_obj.previous_required_direction)
                request_list.append(req_msg)
            else:
                messagebox.showerror("Invalid input", f"At least 1 floor must be {direction_relative[floor > lift_obj.current_floor]} floor {floor} , as requested direction is {direction_name[lift_obj.previous_required_direction]},\
                                     Please wait till the floor request is over and waiting state starts")
                return
            floor_req_entry.delete(0, tk.END)

        def add_weight_in_lift():
            raw_input = weight_entry.get().strip()
            if not raw_input.isdigit():
                messagebox.showerror("Invalid input", "Weight must be a positive integer.")
                return
            weight = int(raw_input)
            if lift_obj.door_closed:
                messagebox.showerror("Invalid input", "Weight change only available when door is open.")
                return
            lift_obj.current_weight += weight
            weight_entry.delete(0, tk.END)

        def subtract_weight_in_lift():
            raw_input = weight_entry.get().strip()
            if not raw_input.isdigit():
                messagebox.showerror("Invalid input", "Weight must be a positive integer.")
                return
            weight = int(raw_input)
            if lift_obj.door_closed:
                messagebox.showerror("Invalid input", "Weight change only available when door is open.")
                return
            elif lift_obj.current_weight < weight:
                messagebox.showerror("Invalid input", "Total Weight cannot be negative.")
                return
            lift_obj.current_weight = max(0, lift_obj.current_weight - weight)
            weight_entry.delete(0, tk.END)

        def update_listbox():
            listbox.delete(0, tk.END)
            display_items = []
            for idx, (type_, floor, direction) in enumerate(request_list):
                if type_ == LIFT_CALL:
                    dir_text = "Up" if direction else "Down"
                    text = f"{idx+1}. LC F: {floor}, {dir_text}"
                elif type_ == FLOOR_REQUEST:
                    text = f"{idx+1}. FR F: {floor}"
                else:
                    text = f"{idx+1}. Unknown"
                listbox.insert(tk.END, text)
                display_items.append(text)

            root.after(500, update_listbox)
            bottom_display.config(state=tk.NORMAL)
            bottom_display.delete("1.0", tk.END)
            bottom_display.insert(tk.END, " | ".join(display_items))
            bottom_display.config(state=tk.DISABLED)

        def update_lift_state():
            for key, label in value_labels.items():
                label.config(text=str(getattr(lift_obj, key)))
            state_text = lift_obj.state_name_map.get("a" + str(lift_obj.current_state_index), "")
            state_label.config(text=f"{state_text}")
            weight_progress['value'] = lift_obj.current_weight
            # value_labels["motors_stopped"].config(text=str(lift_obj.motors_stopped))
            root.after(500, update_lift_state)

        # Setup GUI
        root = tk.Tk()
        root.title("Elevator Control Panel & State Viewer")

        main_frame = ttk.Frame(root, padding=10)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # LEFT PANEL
        floor_req_frame = ttk.LabelFrame(main_frame, text="Floor Requests (Inside Lift)", padding=10)
        floor_req_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N)

        ttk.Label(floor_req_frame, text="Floor Number:").grid(column=0, row=0, sticky=tk.W)
        floor_req_entry = ttk.Entry(floor_req_frame)
        floor_req_entry.grid(column=1, row=0)
        ttk.Button(floor_req_frame, text="Add Floor Request", command=add_floor_request).grid(column=1, row=1, pady=10)

        ttk.Label(floor_req_frame, text="Lift Weight (kg):").grid(column=0, row=2, sticky=tk.W)
        weight_entry = ttk.Entry(floor_req_frame)
        weight_entry.grid(column=1, row=2)
        ttk.Button(floor_req_frame, text="Add Weight to Lift", command=add_weight_in_lift).grid(column=1, row=3, pady=5)
        ttk.Button(floor_req_frame, text="Subtract Weight from Lift", command=subtract_weight_in_lift).grid(column=1, row=4, pady=5)

        # MIDDLE PANEL
        input_frame = ttk.LabelFrame(main_frame, text="Lift Calls (From Floors)", padding=10)
        input_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)

        ttk.Label(input_frame, text="Floor Number:").grid(column=0, row=0, sticky=tk.W)
        floor_entry = ttk.Entry(input_frame)
        floor_entry.grid(column=1, row=0)
        ttk.Label(input_frame, text="Direction:").grid(column=0, row=1, sticky=tk.W)

        dir_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(input_frame, text="Up", variable=dir_var, value=True).grid(column=1, row=1, sticky=tk.W)
        ttk.Radiobutton(input_frame, text="Down", variable=dir_var, value=False).grid(column=2, row=1, sticky=tk.W)

        ttk.Button(input_frame, text="Add Request", command=add_request).grid(column=1, row=2, pady=10)
        ttk.Button(input_frame, text="Save to File", command=save_to_file).grid(column=1, row=3, pady=10)

        ttk.Label(input_frame, text="Current Requests:").grid(column=0, row=4, sticky=tk.W)
        listbox = tk.Listbox(input_frame, height=10, width=50)
        listbox.grid(column=0, row=5, columnspan=3, pady=5)

        # RIGHT PANEL
        state_frame = ttk.LabelFrame(main_frame, text="Lift System State", padding=10)
        state_frame.grid(row=0, column=2, padx=10, pady=10, sticky=tk.N)

        fields = [
            "current_floor", "target_floor", "door_closed", "is_idle",
            "current_weight", "idle_time", "floor_request_wait_time",
            "loop_counter", "cycles", "table_index"
        ]
        value_labels = {}
        for idx, field in enumerate(fields):
            ttk.Label(state_frame, text=field.replace('_', ' ').capitalize() + ":").grid(row=idx, column=0, sticky=tk.W)
            value = ttk.Label(state_frame, text="--")
            value.grid(row=idx, column=1)
            value_labels[field] = value

        # Adjusted layout to avoid overlaps
        weight_row = len(fields)
        fsm_row = weight_row + 1
        motor_row = fsm_row + 1
        separator_row = motor_row + 1
        constants_start = separator_row + 1

        ttk.Label(state_frame, text="Weight Load:").grid(row=weight_row, column=0, sticky=tk.W)
        weight_progress = ttk.Progressbar(state_frame, orient='horizontal', length=120, mode='determinate', maximum=lift_obj.MAX_WEIGHT)
        weight_progress.grid(row=weight_row, column=1)

        ttk.Label(state_frame, text="Current FSM State:").grid(row=fsm_row, column=0, sticky=tk.W)
        state_label = ttk.Label(state_frame, text="--", font=("Arial", 12, "bold"))
        state_label.grid(row=fsm_row, column=1)

        # ttk.Label(state_frame, text="Motors Stopped:").grid(row=motor_row, column=0, sticky=tk.W) #servos..so even tho they r on they r holding their position
        # motors_label = ttk.Label(state_frame, text="--")
        # motors_label.grid(row=motor_row, column=1)
        # value_labels["motors_stopped"] = motors_label

        ttk.Separator(state_frame, orient='horizontal').grid(row=separator_row, columnspan=2, sticky="ew", pady=10)

        constants = {
            "HOME_FLOOR": lift_obj.HOME_FLOOR,
            "MAX_IDLE_TIME (s)": lift_obj.MAX_IDLE_TIME,
            "MAX_FLOOR_REQUEST_WAIT_TIME (s)": lift_obj.MAX_FLOOR_REQUEST_WAIT_TIME,
            "MAX_WEIGHT (kg)": lift_obj.MAX_WEIGHT,
        }
        for idx, (label, val) in enumerate(constants.items(), start=constants_start):
            ttk.Label(state_frame, text=label + ":", foreground="black", font=('Arial', 10, 'bold')).grid(row=idx, column=0, sticky=tk.W)
            ttk.Label(state_frame, text=str(val), foreground="black", font=('Arial', 10, 'bold')).grid(row=idx, column=1)

        # Bottom View
        bottom_display = tk.Text(root, height=2, wrap=tk.NONE)
        bottom_display.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=5)
        bottom_display.config(state=tk.DISABLED)

        update_lift_state()
        update_listbox()

        def check_for_exit():
            if stop_event and stop_event.is_set():
                root.quit()
            else:
                root.after(2000, check_for_exit)

        check_for_exit()
        root.mainloop()

    except Exception as e:
        print(f"Error in merged GUI: {e}")
        traceback.print_exc()
        if root:
            root.quit()



# import tkinter as tk
# from tkinter import ttk, messagebox
# import threading
# import json
# import time

# from lift_utils import MIN_FLOOR, MAX_FLOOR, LIFT_CALL, FLOOR_REQUEST  # Added FLOOR_REQUEST
# from sai_slc_driver import run_slc_driver
# from lift_utils import LIFT_SYSTEM

# import traceback

# def run_merged_gui(request_list, lift_obj,  stop_event=None):
#     root = None
#     direction_relative = {True: "Above", False: "Below"}
#     direction_name = {True: "Up", False: "Down"}
#     try:
#         def save_to_file():
#             with open("request_list.json", "w") as f:
#                 json.dump(request_list, f, indent=4)
#             messagebox.showinfo("Saved", "Requests saved to request_list.json")

#         def add_request():
#             raw_input = floor_entry.get().strip()
#             if not raw_input.isdigit():
#                 messagebox.showerror("Invalid input", "Floor number must be a positive integer.")
#                 return
#             floor = int(raw_input)
#             direction = dir_var.get()
#             if floor < MIN_FLOOR or floor > MAX_FLOOR:
#                 messagebox.showerror("Invalid input", f"Floor must be between {MIN_FLOOR} and {MAX_FLOOR}")
#                 return
#             req_msg = (LIFT_CALL, floor, direction)  # Changed from set to tuple
#             lift_obj.previous_required_direction = direction
#             request_list.append(req_msg)
#             # update_listbox()
#             floor_entry.delete(0, tk.END)

#         def add_floor_request():
#             raw_input = floor_req_entry.get().strip()
#             if not raw_input.isdigit():
#                 messagebox.showerror("Invalid input", "Floor number must be a positive integer.")
#                 return
#             floor = int(raw_input)
#             if floor < MIN_FLOOR or floor > MAX_FLOOR:
#                 messagebox.showerror("Invalid input", f"Floor must be between {MIN_FLOOR} and {MAX_FLOOR}")
#                 return
            
#             if (lift_obj.previous_required_direction == (floor > lift_obj.current_floor)) or\
#                 (len(request_list) != 0) : #allow invalid direction floor reqs if atleast 1 valid floor num 
#                 req_msg = (FLOOR_REQUEST, floor, lift_obj.previous_required_direction)
#                 request_list.append(req_msg)
#             else:
#                 messagebox.showerror("Invalid input", f"Atleast 1 Floor must be {direction_relative[floor>lift_obj.current_floor]} and {floor}, as requested diretion is {direction_name[lift_obj.previous_required_direction]}")
#                 return
            
#             floor_req_entry.delete(0, tk.END)



#         def add_weight_in_lift():
#             raw_input = weight_entry.get().strip()
#             if not raw_input.isdigit():
#                 messagebox.showerror("Invalid input", "Weight must be a positive integer.")
#                 return
#             weight = int(raw_input)
#             if (lift_obj.door_closed ) :
#                 messagebox.showerror("Invalid input", "Weight change only available when door is open.")
#                 return
#             else:
#                 lift_obj.current_weight += weight
#             weight_entry.delete(0, tk.END)

#         def subtract_weight_in_lift():
#             raw_input = weight_entry.get().strip()
#             if not raw_input.isdigit():
#                 messagebox.showerror("Invalid input", "Weight must be a positive integer.")
#                 return
#             weight = int(raw_input)
#             if (lift_obj.door_closed ) :
#                 messagebox.showerror("Invalid input","Weight change only available when door is open.")
#                 return
#             elif(lift_obj.current_weight < weight):
#                 messagebox.showerror("Invalid input", "Total Weight cannot be negative.")
#                 return
#             else:
#                 lift_obj.current_weight = max(0, lift_obj.current_weight - weight)
#             weight_entry.delete(0, tk.END)


#         def update_listbox():
#             listbox.delete(0, tk.END)
#             display_items = []
#             for idx, (type_, floor, direction) in enumerate(request_list):
#                 if type_ == LIFT_CALL:
#                     dir_text = "Up" if direction else "Down"
#                     text = f"{idx+1}. LC F: {floor}, {dir_text}"
#                 elif type_ == FLOOR_REQUEST:
#                     text = f"{idx+1}. FR F: {floor}"
#                 else:
#                     text = f"{idx+1}. Unknown"
#                 listbox.insert(tk.END, text)
#                 display_items.append(text)
                
#             root.after(500, update_listbox) #should be less than the exect time of the lift system
            
#             # Update the horizontal request viewer
#             bottom_display.config(state=tk.NORMAL)
#             bottom_display.delete("1.0", tk.END)
#             bottom_display.insert(tk.END, " | ".join(display_items))
#             bottom_display.config(state=tk.DISABLED)

#         def update_lift_state():
#             for key, label in value_labels.items():
#                 label.config(text=str(getattr(lift_obj, key)))
#             state_text = lift_obj.state_name_map.get("a" + str(lift_obj.current_state_index), "")
#             state_label.config(text=f"{state_text}")
#             weight_progress['value'] = lift_obj.current_weight
#             value_labels["motors_stopped"].config(text=str(lift_obj.motors_stopped))


#             root.after(500, update_lift_state)

#         # Setup GUI
#         root = tk.Tk()
#         root.title("Elevator Control Panel & State Viewer")

#         main_frame = ttk.Frame(root, padding=10)
#         main_frame.grid(row=0, column=0, sticky=tk.NSEW)
#         # root.columnconfigure(0, weight=1)


#         # LEFT-MOST PANEL: Floor Request (Inside Elevator)
#         floor_req_frame = ttk.LabelFrame(main_frame, text="Floor Requests (Inside Lift)", padding=10)
#         floor_req_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N)

#         ttk.Label(floor_req_frame, text="Floor Number:").grid(column=0, row=0, sticky=tk.W)
#         floor_req_entry = ttk.Entry(floor_req_frame)
#         floor_req_entry.grid(column=1, row=0)

#         ttk.Button(floor_req_frame, text="Add Floor Request", command=add_floor_request).grid(column=1, row=1, pady=10)

#         # Weight Section
#         ttk.Label(floor_req_frame, text="Lift Weight (kg):").grid(column=0, row=2, sticky=tk.W)
#         weight_entry = ttk.Entry(floor_req_frame)
#         weight_entry.grid(column=1, row=2)
#         ttk.Button(floor_req_frame, text="Add Weight to Lift", command=add_weight_in_lift).grid(column=1, row=3, pady=5)
#         ttk.Button(floor_req_frame, text="Subtract Weight from Lift", command=subtract_weight_in_lift).grid(column=1, row=4, pady=5)
        


#         # MIDDLE PANEL: Lift Call Requests (From Floors)
#         input_frame = ttk.LabelFrame(main_frame, text="Lift Calls (From Floors)", padding=10)
#         input_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)

#         ttk.Label(input_frame, text="Floor Number:").grid(column=0, row=0, sticky=tk.W)
#         floor_entry = ttk.Entry(input_frame)
#         floor_entry.grid(column=1, row=0)

#         ttk.Label(input_frame, text="Direction:").grid(column=0, row=1, sticky=tk.W)
#         dir_var = tk.BooleanVar(value=True)
#         ttk.Radiobutton(input_frame, text="Up", variable=dir_var, value=True).grid(column=1, row=1, sticky=tk.W)
#         ttk.Radiobutton(input_frame, text="Down", variable=dir_var, value=False).grid(column=2, row=1, sticky=tk.W)

#         ttk.Button(input_frame, text="Add Request", command=add_request).grid(column=1, row=2, pady=10)
#         ttk.Button(input_frame, text="Save to File", command=save_to_file).grid(column=1, row=3, pady=10)

#         ttk.Label(input_frame, text="Current Requests:").grid(column=0, row=4, sticky=tk.W)
#         listbox = tk.Listbox(input_frame, height=10, width=50)
#         listbox.grid(column=0, row=5, columnspan=3, pady=5)

#         # RIGHT PANEL: Lift State Viewer
#         state_frame = ttk.LabelFrame(main_frame, text="Lift System State", padding=10)
#         state_frame.grid(row=0, column=2, padx=10, pady=10, sticky=tk.N)

#         fields = [
#             "current_floor", "target_floor", "door_closed", "is_idle",
#             "current_weight", "idle_time", "floor_request_wait_time",
#             "loop_counter", "cycles", "table_index"
#         ]
#         value_labels = {}
#         for idx, field in enumerate(fields):
#             ttk.Label(state_frame, text=field.replace('_', ' ').capitalize() + ":").grid(row=idx, column=0, sticky=tk.W)
#             value = ttk.Label(state_frame, text="--")
#             value.grid(row=idx, column=1)
#             value_labels[field] = value

        
#         ttk.Label(state_frame, text="Weight Load:").grid(row=len(fields), column=0, sticky=tk.W)
#         weight_progress = ttk.Progressbar(state_frame, orient='horizontal', length=120, mode='determinate', maximum=lift_obj.MAX_WEIGHT)
#         weight_progress.grid(row=len(fields), column=1)

#         ttk.Label(state_frame, text="Motors Stopped:").grid(row=len(fields)+1, column=0, sticky=tk.W)
#         motors_label = ttk.Label(state_frame, text="--")
#         motors_label.grid(row=len(fields)+1, column=1)
#         value_labels["motors_stopped"] = motors_label


#         # FSM State label
#         ttk.Label(state_frame, text="Current FSM State:").grid(row=len(fields), column=0, sticky=tk.W)
#         state_label = ttk.Label(state_frame, text="--", font=("Arial", 12, "bold"))
#         state_label.grid(row=len(fields), column=1)

#         # Separator
#         ttk.Separator(state_frame, orient='horizontal').grid(row=len(fields)+1, columnspan=2, sticky="ew", pady=10)

#         # Constants Section (shown in bold or black)
#         constants = {
#             "HOME_FLOOR": 0,
#             "MAX_IDLE_TIME (s)": int(0.3 * 60),
#             "MAX_FLOOR_REQUEST_WAIT_TIME (s)": int(0.15 * 60),
#             "MAX_WEIGHT (kg)": 700,
#         }

#         for idx, (label, val) in enumerate(constants.items(), start=len(fields)+2):
#             ttk.Label(state_frame, text=label + ":", foreground="black", font=('Arial', 10, 'bold')).grid(row=idx, column=0, sticky=tk.W)
#             ttk.Label(state_frame, text=str(val), foreground="black", font=('Arial', 10, 'bold')).grid(row=idx, column=1)



#             # Bottom Panel: Horizontal Request List View
#         bottom_display = tk.Text(root, height=2, wrap=tk.NONE)
#         bottom_display.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=5)
#         bottom_display.config(state=tk.DISABLED)
        
#         # Periodic update
#         update_lift_state()
#         update_listbox()
#         def check_for_exit():
#             if stop_event and stop_event.is_set():
#                 root.quit()
#             else:
#                 root.after(2000, check_for_exit)
#         check_for_exit()

#         root.mainloop()


#     except Exception as e:
#         print(f"Error in merged GUI: {e}")
#         traceback.print_exc() 
#         if root:
#             root.quit()

        
