# -*- coding: utf-8 -*-

from pynput import keyboard
import threading
import time
import pickle
from collections import deque

from lift_utils import  MIN_FLOOR, MAX_FLOOR, LIFT_CALL, FLOOR_REQUEST
from lift_utils import TABLE_ELEMENTS_NEXT_STATE_MAPPING , LIFT_SYSTEM, ControlMemory

#global variables---------------------------------------------------------
BDD_TABLE_PATH = "data/table_next_state_mapping.pkl"


    

def slc_state_machine_driver(request_list, LIFT, BDD_Table, control_memory): #ControlMemory):
    
    try :
        print("\n\nO----------    New Cycle    ---------O")
        print(f"Request: {request_list}")
            
        is_state = 0 #bool to if it's a state or action node
        index = BDD_Table[LIFT.table_index].node_index    #state/ variable subscript number 
        
        
        while True : # may be ? LIFT.loop_counter < LIFT.MAX_EXECUTION_TIME:, no separate do while loop in python 
            node = BDD_Table[LIFT.table_index]
            print(f"Visiting node {LIFT.table_index}: Type={node.node_type}, Index={node.node_index}, Successors=({node.successor_0}, {node.successor_1})")
            time.sleep(1)
            state = node.node_type + str(node.node_index)
            print(f"[============= In state/var: {state}, {LIFT.state_name_map[state]} =================]")
            # print(" Current condition:", LIFT.condition)
            if LIFT.condition == None:
                print("Condition is None, exiting current cycle.")
                break
            
            if node.node_type == 'x':
                if LIFT.condition[node.node_index] == 0:
                    LIFT.table_index = node.successor_0
                else:
                    LIFT.table_index = node.successor_1

            elif node.node_type == 'a':
                is_state = 1
                # print(f"\n---- Action node {LIFT.table_index}: Executing action {LIFT.state_name_map[state]} ----")
                # if control_memory[index].control is not None:
                #     print("Executing control:", control_memory[index].control)
                    # Simulate output action, e.g., Y1, Y2, etc.
                LIFT.current_floor += 1
                LIFT.table_index = node.successor_1
                #-------------------------------------------
                if LIFT.current_floor > 2*MAX_FLOOR:
                    if (len(request_list)>0):
                        request_list.pop(0)  # Remove the first request
                    LIFT.current_floor = 0
                #------------------------------------------


            index = BDD_Table[LIFT.table_index].node_index
            print(" Current state index:", LIFT.table_index)
            
            # print('control_memory:', control_memory.control_memory_array[index])
            # print('control_memory:', control_memory.control_memory_array[index].imm_transition)
            
            if (is_state == 0 and not control_memory.control_memory_array[index].imm_transition):  
                #the while in the handbook is for continuing..this logic is for breaking
                print(f"****** No immediate transition, waiting for next condition to change ******")
                break
            
            
            LIFT.loop_counter += 1 
            
        LIFT.cycles += 1
        print("--- End Cycle ---")
        
    except Exception as e:
        print(f"Error in state machine driver: {e}")
        raise




def run_slc_driver(request_list, LIFT):
    try:
        # Initializing the SLC system and loadin the BDD table
        # LIFT = LIFT_SYSTEM() 
        control_memory = ControlMemory(LIFT.state_name_map)
        
        with open(BDD_TABLE_PATH, "rb") as f:
            BDD_Table = pickle.load(f)
        print("BDD Table loaded successfully.")
        print(BDD_Table)
        
        
        # Runnin THE LIFT SYSTEM 
        while True:
            #inputs / env updates-----------------
            LIFT.update_condition(request_list)  # Update the condition based on the request list
            #-------------------------------------
            
            #task execution----------------------------- 
            start_time = time.time()  
            slc_state_machine_driver(request_list, LIFT, BDD_Table, control_memory)
            execution_time = time.time() - start_time
            print(f"Execution time: {execution_time:.2f} seconds")
            #-------------------------------------------
            print("Executed number of cycles:", LIFT.cycles)
            print("Executed number of loops in previous cycle:", LIFT.loop_counter)
            
            remaining_time = 2.0 - execution_time  
            if remaining_time > 0:
                time.sleep(remaining_time)
                
                
        # CLEAN UP
        # print("Stopping SLC driver.")
        
        
                
    except Exception as e:
        print(f"Stopping SLC driver. due to {e}")

