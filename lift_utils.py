

LIFT_CALL = "LIFT_CALL"
FLOOR_REQUEST = "FLOOR_REQUEST"
MIN_FLOOR = 0
MAX_FLOOR = 4

# class REQUEST_MSG:
#     def __init__(self, type, floor, direction):
#         self.type =None
#         self.floor = floor
#         self.direction = direction

#     def __repr__(self):
#         return f"REQUEST_MSG(type={self.type}, floor={self.floor}, direction={self.direction})"

#     # def to_dict(self):
#     #     return {
#     #         "floor": self.floor,
#     #         "direction": self.direction
#     #     }

# -------  used for generating BDD table-------------------
class TABLE_ELEMENTS_NEXT_STATE_MAPPING:
    serial_num=0
    node_type='_' #'a', 'x'
    node_index=0
    successor_0 = None
    successor_1 = None
    BDD_NAME = None

    def __init__(self, serial_num, node_type, node_index, successor_0, successor_1, BDD_NAME):
        self.serial_num = serial_num
        self.node_type = node_type
        self.node_index = node_index
        self.successor_0 = successor_0
        self.successor_1 = successor_1
        self.BDD_NAME = BDD_NAME

    def __repr__(self):
        return (f"TABLE_ELEMENTS_NEXT_STATE_MAPPING("
                f"serial_num={self.serial_num}, "
                f"node_type='{self.node_type}', "
                f"node_idx={self.node_index}, "
                f"successor_0={self.successor_0}, "
                f"successor_1={self.successor_1}, "
                f"BDD_NAME='{self.BDD_NAME}')")


#--------used for slc_driver-------------------

from collections import namedtuple
class LIFT_SYSTEM:
            
    def __init__(self):
        #constants in this system=-----------------
        self.HOME_FLOOR = 0
        self.MAX_IDLE_TIME = 5*60 #seconds 
        self.MAX_FLOOR_REQUEST_WAIT_TIME = 1*60 #seconds #at the end of the served floors it will wait for this time before closing the doors
        self.MAX_WEIGHT = 700 #kg
        # self.MAX_CAPACITY = 10 around 68 kg avg ig generallyh...

        #vairables---------------------------------
        self.table_index = 0  # persistent variable i (initially 0) ????????
        self.current_state_index = 0
        self.current_direction = 0
        self.current_floor = 0
        self.target_floor = 0
        
        #condistionals...
        self.idle_time = 0 #TODO to update this somewhere
        self.is_idle = 0
        self.current_weight = 0
        self.floor_request_wait_time = 0
        self.door_closed = 0
        
        #trackers
        self.loop_counter = 0
        self.cycles = 0
        
        self.state_name_map = {
            "a0": "WAITING",
            "a1": "IDLE",
            "a2": "QUEUE_UPDATED",
            "a3": "DOOR_CLOSED",
            "a4": "TARGET_SET",
            "a5": "QUEUE_POPPED",
            "a6": "DOOR_OPENED",
            "a7": "MOTORS_MOVING",
            "a8": "UPDATED_CURRFLOOR",
            "a9": "AWAIT_FLOOR_REQUESTS",
            "a10": "OVERLOADED",
            "a11": "REDUNDANT_CALL_REMOVED",
            "a12": "MOTORS_STOPPED"
        }

        self.condition = None 
        
    def update_condition(self, request_list):
        self.target_floor = request_list[0][1] if len(request_list) > 0 else self.target_floor
        
        # Update conditions based on the request list
        self.condition = {
            1: len(request_list) > 0,  # IS_CALLED
            2: self.idle_time > self.MAX_IDLE_TIME,  # IS_IDLE_TIMED
            3: self.door_closed,  # IS_DOOR_CLOSED
            4: self.current_floor == self.target_floor,  # IS_TARGET_REACHED  
            5: self.is_idle,  # IS_LIFT_IDLE
            6: 0,# ie self.current_floor in request_list,  # IS_VALID_STOP..not stopping for now
            7: 0, #self.current_weight > self.MAX_WEIGHT,  # IS_OVERLOADED    
            8: len(request_list) > 0, #maybe something else could be done #self.current_floor in request_list,  # IS_VALID_FLOOR_REQUESTS
            9: self.floor_request_wait_time > self.MAX_FLOOR_REQUEST_WAIT_TIME,  # IS_FLOORREQ_WAITTIME_OUT
            10: len(request_list) == 0,  # IS_QUEUE_EMPTY             
        }
        
        

BDDNode = namedtuple('BDDNode', [ 'serial', 'node_type', 'node_index', 'successor_0', 'successor_1', 'BDD_name'])

# TODO to look into control memory
# ControlMemoryEntry = namedtuple('ControlMemoryEntry', ['control', 'imm_transition'])


class ControlMemoryEntry:
    def __init__(self, control=None, imm_transition=False, node_index=None, control_name=None):
        self.control = control
        self.imm_transition = imm_transition
        self.node_index = node_index  # Initialize node_index to None
        self.control_name = control_name #Initialize control_name to None
        
    
class ControlMemory:
    '''TODO need to change this manually according to the transition equations(for imm_transitions)'''
    def __init__(self, state_name_map):
        self.state_name_map = state_name_map
        self.control_memory_array = [
            ControlMemoryEntry(control=f"Y{i}", imm_transition=0, node_index=i, control_name=f"Y{i}") for i in range(0,13) #0 is ignored 
        ]
        self.control_memory_array[6].imm_transition = 1
        self.control_memory_array[7].imm_transition = 1
        self.control_memory_array[10].imm_transition = 1
        self.control_memory_array[12].imm_transition = 1
    # def functional calls to control the motor???