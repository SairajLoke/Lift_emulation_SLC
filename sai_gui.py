import tkinter as tk
from tkinter import ttk, messagebox
import json

from lift_utils import  MIN_FLOOR, MAX_FLOOR, LIFT_CALL #REQUEST_MSG,

def run_gui(floor_requests):
    # floor_requests = []

    def save_to_file():
        with open("floor_requests.json", "w") as f:
            json.dump(floor_requests, f, indent=4)
        messagebox.showinfo("Saved", "Requests saved to floor_requests.json")
    
    def add_request():
        # try:
        raw_input = floor_entry.get().strip()  # removes leading/trailing spaces
        if not raw_input.isdigit():
            messagebox.showerror("Invalid input", "Floor number must be a positive integer.")
            return
        
        floor = int(raw_input)
        direction = dir_var.get()
        if floor<MIN_FLOOR or floor>MAX_FLOOR:
            messagebox.showerror("Invalid input", f"Floor number must be between {MIN_FLOOR} and {MAX_FLOOR}")
            return
        
        req_msg = {LIFT_CALL, floor, direction}
        floor_requests.append(req_msg)
        update_listbox()
        print("Floor request added:", LIFT_CALL, floor, direction)
        floor_entry.delete(0, tk.END)

        # except ValueError:
        #     print(floor_entry.get())
        #     print(type(floor_entry.get()))
        #     print(dir_var.get())
        #     print(type(dir_var.get()))
        #     messagebox.showerror("Invalid input", "Floor number must be an integer--")

    def update_listbox():
        listbox.delete(0, tk.END)
        for idx, (type, floor, direction) in enumerate(floor_requests):
            dir_text = "Up" if direction else "Down"
            listbox.insert(tk.END, f"{idx+1}. TYPE: {type} Floor: {floor}, Direction: {dir_text}")

    # GUI setup
    root = tk.Tk()
    root.title("Floor Request Input")

    frame = ttk.Frame(root, padding=10)
    frame.grid()

    # Floor input
    ttk.Label(frame, text="Floor Number:").grid(column=0, row=0, sticky=tk.W)
    floor_entry = ttk.Entry(frame)
    floor_entry.grid(column=1, row=0)

    # Direction input
    ttk.Label(frame, text="Direction:").grid(column=0, row=1, sticky=tk.W)
    dir_var = tk.BooleanVar(value=True)
    ttk.Radiobutton(frame, text="Up", variable=dir_var, value=True).grid(column=1, row=1, sticky=tk.W)
    ttk.Radiobutton(frame, text="Down", variable=dir_var, value=False).grid(column=2, row=1, sticky=tk.W)

    # Add button
    ttk.Button(frame, text="Add Request", command=add_request).grid(column=1, row=2, pady=10)

    # Listbox to show requests
    ttk.Label(frame, text="Current Requests:").grid(column=0, row=3, sticky=tk.W)
    listbox = tk.Listbox(frame, height=10, width=40)
    listbox.grid(column=0, row=4, columnspan=3, pady=5)

    # Save button
    ttk.Button(frame, text="Save to File", command=save_to_file).grid(column=1, row=5, pady=10)

    root.mainloop()


if __name__ == "__main__":
    floor_requests = []  # Shared list for floor requests
    run_gui(floor_requests)