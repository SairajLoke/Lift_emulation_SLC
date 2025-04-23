

LIFT_CALL = "LIFT_CALL"
FLOOR_REQUEST = "FLOOR_REQUEST"
MIN_FLOOR = 0
MAX_FLOOR = 4

import time 

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
                f"node_index={self.node_index}, "
                f"successor_0={self.successor_0}, "
                f"successor_1={self.successor_1}, "
                f"BDD_NAME='{self.BDD_NAME}')")


#--------used for slc_driver-------------------
from collections import namedtuple
class LIFT_SYSTEM:
            
    def __init__(self):
        #constants in this system=-----------------
        self.HOME_FLOOR = 0
        self.MAX_IDLE_TIME = int(0.3*60) #int(0.2*60) #seconds 
        self.MAX_FLOOR_REQUEST_WAIT_TIME = int(0.15*60) #seconds #at the end of the served floors it will wait for this time before closing the doors
        self.MAX_WEIGHT = 700 #kg
        # self.MAX_CAPACITY = 10 around 68 kg avg ig generallyh...

        #vairables---------------------------------
        self.table_index = 0  # persistent variable i (initially 0) ????????
        self.current_state_index = 0
        self.previous_state_index = 0
        self.current_direction = 0
        self.previous_required_direction = None #should be 0 as checked in relative floors
        self.current_floor = 0
        self.target_floor = 0
        # self.current_state_name = "WAITING"
        
        #condistionals...
        self.idle_time = 0 #TODO to update this somewhere
        self.idle_start_time = time.time()
        self.floor_request_wait_start_time = time.time()
        self.floor_request_wait_time = 0
        
        self.is_idle = False
        self.current_weight = 0
        self.door_closed = True 
        self.motors_stopped = True
        
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
        # self.target_floor = request_list[0][1] if len(request_list) > 0 else self.target_floor
        
        # Update conditions based on the request list
        # this is the x in the BDD
        self.condition = {
            1: len(request_list) > 0,  # IS_CALLED
            2: self.idle_time >= self.MAX_IDLE_TIME and not self.is_idle,  # IS_IDLE_TIMED #this removes unnecessary calls to homing when already idle
            3: self.door_closed,  # IS_DOOR_CLOSED
            4: self.current_floor == self.target_floor,  # IS_TARGET_REACHED  
            5: self.is_idle,  # IS_LIFT_IDLE
            6: self.current_floor in [req[1] for req in request_list if req[2] == self.current_direction] ,# ie self.current_floor in request_list with same direction request,  # IS_VALID_STOP..not stopping for now
            7: self.current_weight > self.MAX_WEIGHT,  # IS_OVERLOADED    
            8: len(request_list) > 0 and self.floor_request_wait_time > self.MAX_FLOOR_REQUEST_WAIT_TIME , #maybe something else could be done #self.current_floor in request_list,  # IS_VALID_FLOOR_REQUESTS
            9: self.floor_request_wait_time > self.MAX_FLOOR_REQUEST_WAIT_TIME,  # IS_FLOORREQ_WAITTIME_OUT
            10: len(request_list) == 0,  # IS_QUEUE_EMPTY             
        }
        
        

BDDNode = namedtuple('BDDNode', [ 'serial', 'node_type', 'node_index', 'successor_0', 'successor_1', 'BDD_name'])
