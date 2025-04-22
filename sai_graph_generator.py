# -*- coding: utf-8 -*-

# to install graphviz and python graphviz
# sudo apt-get install graphviz
# pip install graphviz

from graphviz import Digraph
from collections import defaultdict

#tobe careful wrt
# bool values of conditionals


# Store transitions for each state
state_transition_map = defaultdict(list) #for automating the state transition equations 
def add_transition(from_state, to_state, label): #label=condition
    dot.edge(from_state, to_state, label=label)
    state_transition_map[from_state].append((to_state, label))


# States
WAITING = "a0"
IDLE = "a1"
QUEUE_UPDATED = "a2"
DOOR_CLOSED = "a3"
TARGET_SET = "a4"
QUEUE_POPPED = "a5"
DOOR_OPENED = "a6"
MOTORS_MOVING = "a7"
UPDATED_CURRFLOOR = "a8"
AWAIT_FLOOR_REQUESTS = "a9"
OVERLOADED = "a10"
REDUNDANT_CALL_REMOVED = "a11"
MOTORS_STOPPED = "a12"


state_output_map = { #state to output mapping
    WAITING: "-",
    IDLE: "Y1",
    QUEUE_UPDATED: "Y2",
    DOOR_CLOSED: "Y3",
    TARGET_SET: "Y4",
    QUEUE_POPPED: "Y5",
    DOOR_OPENED: "Y6",
    MOTORS_MOVING: "Y7",
    UPDATED_CURRFLOOR: "Y8",
    AWAIT_FLOOR_REQUESTS: "Y9",
    OVERLOADED: "Y10",
    REDUNDANT_CALL_REMOVED: "Y11",  
    MOTORS_STOPPED: "Y12",  
}

# Inputs
IS_CALLED = "x1"  # Lift Summon Request
IS_IDLE_TIMED = "x2"  # IDLE time check 
IS_DOOR_CLOSED = "x3"  # Door Close Request
IS_TARGET_REACHED = "x4"  # Target Floor Request
IS_LIFT_IDLE = "x5" 
IS_VALID_STOP = "x6" 
IS_OVERLOADED = "x7"  
IS_VALID_FLOOR_REQUESTS = "x8"  # Move Motors by 1Floor
IS_FLOORREQ_WAITTIME_OUT = "x9"  # Underload
IS_QUEUE_EMPTY = "x10"  # Wait for Floor Requests & Put Requests in a Queue


#Operations
NOT = "!" #¬"
# AND = "∧" not using implicitly assumed 
# OR = "∨"


# Create a directed graph
dot = Digraph("SAI LiftStateMachine", format="png")
dot.attr(rankdir="LR", fontsize="12")
dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue", fontname="Helvetica")


for state, output in state_output_map.items():
    dot.node(state, f"{state} / {output}")



# Define transitions using logical expressions
# from a0
add_transition(WAITING, WAITING, label=f"{NOT}{IS_CALLED} {NOT}{IS_IDLE_TIMED}")
add_transition(WAITING, IDLE,    label=f"{NOT}{IS_CALLED} {IS_IDLE_TIMED}")
add_transition(WAITING, QUEUE_UPDATED, label=f"{IS_CALLED}")

#from a1
add_transition(IDLE, DOOR_CLOSED, label=f"{NOT}{IS_DOOR_CLOSED}")
add_transition(IDLE, TARGET_SET,  label=f"{IS_DOOR_CLOSED}  {NOT}{IS_QUEUE_EMPTY}")
add_transition(IDLE, WAITING,     label=f"{IS_DOOR_CLOSED}  {IS_QUEUE_EMPTY}")

#from a2
add_transition(QUEUE_UPDATED, DOOR_CLOSED, label=f"{NOT}{IS_DOOR_CLOSED} ")
add_transition(QUEUE_UPDATED, TARGET_SET,  label=f"{IS_DOOR_CLOSED}  {NOT}{IS_QUEUE_EMPTY}")
add_transition(QUEUE_UPDATED, WAITING, label=f"{IS_DOOR_CLOSED}  {IS_QUEUE_EMPTY}")

#from a3
add_transition(DOOR_CLOSED, DOOR_CLOSED, label=f"{NOT}{IS_DOOR_CLOSED}")
add_transition(DOOR_CLOSED, WAITING,    label=f"{IS_DOOR_CLOSED}  {IS_QUEUE_EMPTY}")
add_transition(DOOR_CLOSED, TARGET_SET, label=f"{IS_DOOR_CLOSED}  {NOT}{IS_QUEUE_EMPTY}")

#from a4
add_transition(TARGET_SET, QUEUE_POPPED, label=f"{IS_TARGET_REACHED}")
add_transition(TARGET_SET, MOTORS_STOPPED,  label=f"{NOT}{IS_TARGET_REACHED}  {IS_VALID_STOP}")
add_transition(TARGET_SET, MOTORS_MOVING,label=f"{NOT}{IS_TARGET_REACHED}  {NOT}{IS_VALID_STOP}")

#from a5
add_transition(QUEUE_POPPED, WAITING,     label=f"{IS_LIFT_IDLE}")
add_transition(QUEUE_POPPED, MOTORS_STOPPED, label=f"{NOT}{IS_LIFT_IDLE}")

# from a12
add_transition(MOTORS_STOPPED, DOOR_OPENED, label=f"-")


#from a6
add_transition(DOOR_OPENED, AWAIT_FLOOR_REQUESTS, label=f"-")

#from a7
add_transition(MOTORS_MOVING, UPDATED_CURRFLOOR, label=f"-")


#from a8
add_transition(UPDATED_CURRFLOOR, QUEUE_POPPED, label=f"{IS_TARGET_REACHED}")
#prolly some commong state betw a4 a8
add_transition(UPDATED_CURRFLOOR, MOTORS_STOPPED, label=f"{NOT}{IS_TARGET_REACHED}  {IS_VALID_STOP}")
add_transition(UPDATED_CURRFLOOR, MOTORS_MOVING,  label=f"{NOT}{IS_TARGET_REACHED}  {NOT}{IS_VALID_STOP}")

#from a9 ( 4 outs)
add_transition(AWAIT_FLOOR_REQUESTS, OVERLOADED,             label=f"{IS_OVERLOADED}")
add_transition(AWAIT_FLOOR_REQUESTS, REDUNDANT_CALL_REMOVED, label=f"{NOT}{IS_OVERLOADED}  {IS_VALID_FLOOR_REQUESTS} ")
add_transition(AWAIT_FLOOR_REQUESTS, REDUNDANT_CALL_REMOVED, label=f"{NOT}{IS_OVERLOADED}  {NOT}{IS_VALID_FLOOR_REQUESTS}  {IS_FLOORREQ_WAITTIME_OUT}")
add_transition(AWAIT_FLOOR_REQUESTS, AWAIT_FLOOR_REQUESTS,   label=f"{NOT}{IS_OVERLOADED}  {NOT}{IS_VALID_FLOOR_REQUESTS}  {NOT}{IS_FLOORREQ_WAITTIME_OUT}")


#from a10
add_transition(OVERLOADED, AWAIT_FLOOR_REQUESTS, label=f"-")

#from a11
add_transition(REDUNDANT_CALL_REMOVED, WAITING,     label=f"{IS_DOOR_CLOSED}  {IS_QUEUE_EMPTY}")
add_transition(REDUNDANT_CALL_REMOVED, TARGET_SET,  label=f"{IS_DOOR_CLOSED}  {NOT}{IS_QUEUE_EMPTY} ")
add_transition(REDUNDANT_CALL_REMOVED, DOOR_CLOSED, label=f"{NOT}{IS_DOOR_CLOSED}")


# Optional: set ranks to keep layout neat
# with dot.subgraph() as s:
#     s.attr(rank='same')
#     s.node("a2")
#     s.node("a3")

# Save and optionally render
dot.render("moore_machine_sai_lift.dot", view=True)  # Creates lift_state_machine.dot and lift_state_machine.png



with open("moore_transitions.txt", "w") as f:
    for from_state in state_output_map:
        output = state_output_map[from_state]
        transitions = state_transition_map[from_state]
        if transitions:
            rhs = ", ".join([f"{dst}({cond})" for dst, cond in transitions])
            f.write(f"F_{from_state}({output}) = {rhs};\n\n")
        else:
            f.write(f"F_{from_state}({output}) = ;\n\n")
