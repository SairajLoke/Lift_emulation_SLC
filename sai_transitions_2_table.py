import re
import pickle
import os
from collections import defaultdict

TRANSITIONS_FILE_PATH = "data/moore_transitions.txt"
AND = "&"
serial_counter = 0
states_vars_serial_num = {}
var_serial_num = {}
curr_function_name = None

TABLE_NEXT_STATE_MAPPING = []

from lift_utils import TABLE_ELEMENTS_NEXT_STATE_MAPPING


def parse_transition_function(line):
    global serial_counter, states_vars_serial_num, curr_function_name

    # "F_a1(Y1) = a3(!x3), a4(x3 ∧ !x10), a0(x3 ∧ x10)"  # Example input line
    # TODO also need to handle the case where there are no conditions (e.g., "F_a1(Y1) = a3(-)")

    # Extract the function name and the transitions
    head, expressions = line.split("=")
    func_name = head.strip().split('(')[0].strip()
    from_state = func_name.split("_")[1] 

    #same state actually has multiple entries in the table at diff serial num..
    # but the entry row for all instances is the same except BDD entry
    # so below line  not needed 
    states_vars_serial_num[from_state] = serial_counter #not to change the counter here
    curr_function_name = func_name #set the current function name for the state
    #sets the serial number for the state's successive conditional variable's serial number or
        # the next state serial number in the table (if direct transition)

    # Parse each state transition
    transitions = []
    for part in expressions.split(","):
        match = re.match(r"(a\d+)\((.+)\)", part.strip())
        if not match:
            raise ValueError(f"Invalid transition format: {part}")
        state, condition = match.groups()
        # condition = condition.replace("∧", "and")  # normalize AND
        literals = [lit.strip() for lit in condition.split(AND) ]
        transitions.append((state, literals))
        print(f"Parsed transition: {state} -> {literals}")
    
    return func_name, transitions

def extract_vars(sub_transitions):
    # Get all unique x variables from conditions
    var_set = set()
    print(f"Sub-transitions: {sub_transitions}")
    for state_name, literals in sub_transitions:
        for lit in literals : #and lit.strip() != '-'
            if lit == "-":
                continue
            var = lit.replace("!", "")
            var_set.add(var)
    # Sort by natural order (x3, x10, etc.)

    print(f"Extracted variables: {var_set}")
    return sorted(var_set, key=lambda v: int(v[1:]))


def build_tree(transitions, vars_order, node_map={}):
    global serial_counter

    if len(vars_order) == 0:
        print("Direct transition found, no variables left to split.")
        state = transitions[0][0]
        # if state not in node_map:
        node_map[state] = {"serial": serial_counter, "state": state} # for json visualization
        serial_counter += 1

        TABLE_NEXT_STATE_MAPPING.append(TABLE_ELEMENTS_NEXT_STATE_MAPPING(
            serial_num=node_map[state]["serial"],
            node_type='a',
            node_index= int(node_map[state]["state"].replace("a", "")),
            successor_0='-', #need to update these after all the indexing is done
            successor_1=state, #bascially change the state to the state's index in table
            BDD_NAME= curr_function_name #as leaf...the successors are the same as the state itself...also serial os state 
        ))

        return node_map[state]


    # Recursively buildin the tree
    if all(len(cond) == 0 for _, cond in transitions):
        # All transitions are resolved (leaf)
        print("Leaf node reached with transitions:", transitions)
        state = transitions[0][0]
        # if state not in node_map:
        node_map[state] = {"serial": serial_counter, "state": state}
        # state_serial_num[state] = serial_counter not here..butrather start of every new transition line from that state ...
        serial_counter += 1

        #update table entry
        TABLE_NEXT_STATE_MAPPING.append(TABLE_ELEMENTS_NEXT_STATE_MAPPING(
            serial_num=node_map[state]["serial"],
            node_type='a',
            node_index= int(node_map[state]["state"].replace("a", "")),
            successor_0='-', #need to update these after all the indexing is done
            successor_1=state, #bascially change the state to the state's index in table
            BDD_NAME= curr_function_name #as leaf...the successors are the same as the state itself...also serial os state 
        ))

        return node_map[state]
    
    
    current_var = None
    for var in vars_order:
        if any(var in lit or f"!{var}" in lit      for _, cond in transitions for lit in cond):
            current_var = var
            break
    if current_var is None:
        raise ValueError("No variable left to split, but unresolved transitions remain.")
    
    # Index the decision node
    node_index = serial_counter
    # var_serial_num[current_var] = node_index not useful ig..coz same variable can comeupt multiple times in different transition lines
    serial_counter += 1
    

    true_branch = []
    false_branch = []
    
    for state, cond in transitions:
        matched = False
        for lit in cond:
            if lit == current_var:
                true_branch.append((state, [l for l in cond if l != lit]))
                matched = True
                break
            elif lit == f"!{current_var}":
                false_branch.append((state, [l for l in cond if l != lit]))
                matched = True
                break
        if not matched:
            # If the variable isn't in the condition, include in both branches
            true_branch.append((state, cond.copy()))
            false_branch.append((state, cond.copy()))
    
    false_tree =  build_tree(false_branch, vars_order, node_map)
    true_tree = build_tree(true_branch, vars_order, node_map)

    TABLE_NEXT_STATE_MAPPING.append(TABLE_ELEMENTS_NEXT_STATE_MAPPING(
        serial_num=node_index,
        node_type='x',
        node_index=int(current_var.replace("x", "")),
        successor_0= false_tree["serial"],  # To be filled later
        successor_1= true_tree["serial"],  # To be filled later
        BDD_NAME=curr_function_name
    ))

    return {
        "serial": node_index,
        "var": current_var,
        "false": false_tree,
        "true": true_tree,
    }


def single_transition_to_tree(transition):
    
    
    func_name, transitions = parse_transition_function(transition)
    print(f"Function name: {func_name}")
    print(f"Transitions: {transitions}")

    vars_order = extract_vars(transitions)
    tree = build_tree(transitions, vars_order)

    print(f"State serial numbers: {states_vars_serial_num}")
    # print(f"Variable serial numbers: {var_serial_num}")
    print(serial_counter)

    import json
    print(json.dumps(tree, indent=2))

    return tree


def load_transitions_from_file(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()
        return [line.strip().rstrip(';') for line in lines if line.strip()]
    
if __name__ == "__main__":

    # input_line = "F_a1(Y1) = a3(x3), a4(!x3 ∧ !x10), a0(!x3 ∧ x10)"
    
    # ALL_TRANSITIONS = [ #this is the example from Gourinath sirs handbook
    #     "F_a0(-) = a0(!x1), a1(x1)",
    #     "F_a1(Y1) = a1(!x2), a2(x2 & !x3 & !x4), a3(x2 & !x3 & x4), a6(x2 & x3)",
    #     "F_a2(Y2) = a4(-)",
    #     "F_a3(Y3) = a4(-)",
    #     "F_a4(Y4) = a4(!x3), a5(x3)",
    #     "F_a5(Y5) = a6(-)",
    #     "F_a6(Y6) = a0(-)",
    # ]
    ALL_TRANSITIONS = load_transitions_from_file(TRANSITIONS_FILE_PATH)
    

    for transition in ALL_TRANSITIONS:
        print(f"Processing transition: {transition}")
        single_transition_to_tree(transition)
        print("\n" + "="*50 + "\n")

    print("Final Table Entries:")
    sorted_table = sorted(TABLE_NEXT_STATE_MAPPING, key=lambda x: x.serial_num)

    #update the successors in the table entries
    #recursively traverse the tree and update the successors
    for entry in sorted_table:
        if(entry.node_type == 'a'):
            entry.successor_1 = states_vars_serial_num[entry.successor_1]
        print(f"Serial: {entry.serial_num} | Node Type: {entry.node_type} | Node Index: {entry.node_index} | Successor 0: {entry.successor_0} | Successor 1: {entry.successor_1} | BDD Name: {entry.BDD_NAME}")

    # Save
    os.makedirs("data", exist_ok=True)
    with open("data/table_next_state_mapping.pkl", "wb") as f:
        pickle.dump(TABLE_NEXT_STATE_MAPPING, f)


