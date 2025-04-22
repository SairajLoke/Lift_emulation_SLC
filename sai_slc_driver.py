# -*- coding: utf-8 -*-

from pynput import keyboard
import threading
import time
import pickle
from collections import namedtuple
from collections import deque

from lift_utils import  MIN_FLOOR, MAX_FLOOR, LIFT_CALL, FLOOR_REQUEST, TABLE_ELEMENTS_NEXT_STATE_MAPPING #REQUEST_MSG,

#global variables---------------------------------------------------------
BDD_TABLE_PATH = "data/table_next_state_mapping.pkl"
LOOP_TIME = 20
# Simulated BDD Table and Control Memory Structures
BDDNode = namedtuple('BDDNode', ['node_type', 'node_index', 'successor0', 'successor1'])

# TODO to look into control memory
# ControlMemoryEntry = namedtuple('ControlMemoryEntry', ['control', 'imm_transition'])


# Key mappings to input signals
key_input_map = {
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9, '0': 10
}

#-------------------------------------------------------------------------

# def on_press(key):
#     try:
#         if key.char in key_input_map:
#             x[key_input_map[key.char]] = 1
#     except AttributeError:
#         pass
# def on_release(key):
#     try:
#         if key.char in key_input_map:
#             x[key_input_map[key.char]] = 0
#     except AttributeError:
#         pass
# listener = keyboard.Listener(on_press=on_press, on_release=on_release)
# listener.start()

# Sample BDD Table and control memory (replace with actual data)
# BDD_Table = [
#     BDDNode('x', 1, 1, 2),
#     BDDNode('a', 0, 0, 3),
#     BDDNode('a', 0, 0, 0),
#     BDDNode('x', 2, 2, 1),
# ]



def slc_state_machine_driver(request_list):
    state = 0
    i = 0  # persistent variable i (initially 0)

    # Load
    with open(BDD_TABLE_PATH, "rb") as f:
        BDD_Table = pickle.load(f)
    index = BDD_Table[i].node_index
    print("BDD Table loaded successfully.")
    print(BDD_Table)

    print("\n--- New Cycle ---")
    # print("Inputs:", x[1:])
    cntr = 0
    while cntr < LOOP_TIME:
        node = BDD_Table[i]
        # request = request_list.pop(0) if request_list else None
        # request = request_list[0] if request_list else None

        print(f"Request: {request_list}")
        print(f"Visiting node {i}: Type={node.node_type}, Index={node.node_index}, Successors=({node.successor_0}, {node.successor_1})")
        time.sleep(1)
        cntr+= 1
        continue

        if node.N_type == 'x':
            if x[node.N_index] == 0:
                i = node.successor0
            else:
                i = node.successor1

        elif node.N_type == 'a':
            state = 1
            print(f"Action node {i}: Executing action")
            # if control_memory[index].control is not None:
            #     print("Executing control:", control_memory[index].control)
                # Simulate output action, e.g., Y1, Y2, etc.
            i = node.successor1

        index = BDD_Table[i].N_index

        if not (state == 0 and not control_memory[index].imm_transition):
            break

    print("--- End Cycle ---")


def run_slc_driver(request_list):
    try:
        # while True:
        slc_state_machine_driver(request_list)
            # time.sleep(1)  # simulate time delay
    except Exception as e:
        print(f"Exiting program.{e}")
