# import re

# def parse_expression(expr):
#     match = re.match(r"a(\d+)\(([^)]*)\)", expr.strip())
#     if not match:
#         return None
#     target = int(match.group(1))
#     condition = match.group(2)
#     variables = condition.split() if condition != '-' else []
#     return (variables, target)

# def load_transitions(file_path):
#     transitions = {}
#     with open(file_path, 'r') as file:
#         for line in file:
#             line = line.strip().strip(';')
#             if not line or '=' not in line:
#                 continue
#             lhs, rhs = line.split('=')
#             func_name = lhs.strip()
#             expressions = [expr.strip() for expr in rhs.split(',')]
#             transitions[func_name] = expressions
#     return transitions

# def generate_slc_table(transitions):
#     node_id = 0
#     rows = []

#     for func_name, expressions in transitions.items():
#         for expr in expressions:
#             parsed = parse_expression(expr)
#             if parsed is None:
#                 continue
#             vars, target = parsed

#             if not vars:
#                 # Terminal node
#                 rows.append({
#                     'node_type': 'a',
#                     'node_index': target,
#                     'successor_0': 0,
#                     'successor_1': 0,
#                     'bdd': func_name
#                 })
#                 continue

#             # For now: only look at first variable
#             var = vars[0].replace('!', '')
#             node_type = 'x' if 'x' in var else 'a'

#             # Dummy successor values, for illustrative SLC table
#             successor_0 = node_id + 1
#             successor_1 = node_id + 2
#             rows.append({
#                 'node_type': node_type,
#                 'node_index': int(var[1:]),
#                 'successor_0': successor_0,
#                 'successor_1': successor_1,
#                 'bdd': func_name
#             })
#             node_id += 2
#     return rows

# def write_header(rows, output_path="slc_table.h"):
#     with open(output_path, 'w') as f:
#         f.write("struct TransitionRow {\n")
#         f.write("    char node_type;\n")
#         f.write("    int node_index;\n")
#         f.write("    int successor_0;\n")
#         f.write("    int successor_1;\n")
#         f.write("    const char* bdd;\n")
#         f.write("};\n\n")
#         f.write("const TransitionRow SLC_TABLE[] = {\n")
#         for row in rows:
#             f.write(f"    {{'{row['node_type']}', {row['node_index']}, {row['successor_0']}, {row['successor_1']}, \"{row['bdd']}\"}},\n")
#         f.write("};\n")

# # === Run the process ===
# if __name__ == "__main__":
#     transitions = load_transitions("moore_transitions.txt")
#     slc_rows = generate_slc_table(transitions)
#     write_header(slc_rows)
#     print("SLC table written to slc_table.h")
import re

class TransitionRow:
    def __init__(self, node_type, node_index, successor_0, successor_1, bdd):
        self.node_type = node_type
        self.node_index = node_index
        self.successor_0 = successor_0
        self.successor_1 = successor_1
        self.bdd = bdd

    def __repr__(self):
        return f"    {{'{self.node_type}', {self.node_index}, {self.successor_0}, {self.successor_1}, \"{self.bdd}\"}},"

def parse_expression(expr):
    match = re.match(r"a(\d+)\(([^)]*)\)", expr.strip())
    if not match:
        return None
    target = int(match.group(1))
    condition = match.group(2)
    variables = condition.split() if condition != '-' else []
    return variables, target

def load_transitions(file_path):
    transitions = {}
    with open(file_path, 'r') as f:
        for line in f:
            if '=' not in line:
                continue
            lhs, rhs = line.strip().strip(';').split('=')
            func_name = lhs.strip()
            print(f"Parsing func_name: {func_name} AND RHS: {rhs}")
            transitions[func_name] = [expr.strip() for expr in rhs.split(',')]
            print(f"Parsed transitions: {transitions[func_name]}")
    return transitions


node_idx_map = {} #to be used to get the idx of the node(a/x) afterwards


def traverse()

def build_table(transitions):
    table = []
    node_id = 0

    for func_name, expressions in transitions.items():
        print(f"Processing function: {func_name}")
        
        from_state = func_name.split('(')[0][2:]  # Extract a1 from F_a1, or a10 from  F_a10 , etc
        # node_idx_map[from_state] = node_id #used in assigning index afterwareds 
        # node_id += 1
        print(f"\tFrom state: {from_state}, Node ID: {node_id}")
        
        #Im assuming the order of x_idx is correct increasing so the tree can be built properly
        
        
        for expr in expressions:
            print(f"\tParsing expression: {expr}")
            vars, target = parse_expression(expr)
            print(f"\t...  vars: {vars}  targets: {target}")
            
            
            if not vars: # there happens tobe only 1 term in the expr ..like a1(-)
                # Terminal node
                table.append(TransitionRow('a', target, '-', f"a{target}", f"{func_name}"))  
                # two_node_idx_map[f""]
                #fill the successor_1 with the target for now, later in code I can get the idx of the target node in BDD table, due to node_idx_map[from_state] = node_id 
                
            else:
                # if vars assume sorted order 
                
                var_index = int(vars[0].replace('!', '').replace('x', ''))
                table.append(TransitionRow('x', var_index, node_id + 1, node_id + 2, f"{func_name}"))
                node_id += 2
                
                
    
    #update succs in the table
    
    
    
    return table

def write_header(table, filename="slc_table.h"):
    with open(filename, 'w') as f:
        f.write("struct TransitionRow {\n")
        f.write("    char node_type;\n")
        f.write("    int node_index;\n")
        f.write("    int successor_0;\n")
        f.write("    int successor_1;\n")
        f.write("    const char* bdd;\n")
        f.write("};\n\n")
        f.write("const TransitionRow SLC_TABLE[] = {\n")
        for row in table:
            f.write(f"{repr(row)}\n")
        f.write("};\n")

# Main
if __name__ == "__main__":
    transitions = load_transitions("moore_transitions.txt")
    print("-------------Loaded transitions: --------------")
    table = build_table(transitions)
    write_header(table)
    print(f"Wrote {len(table)} rows to sai_lift_slc_table.h")
