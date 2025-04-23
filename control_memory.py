import time 
from lift_utils import LIFT_SYSTEM, LIFT_CALL, FLOOR_REQUEST
    
class ControlMemoryFunctions:
    '''TODO need to change this manually according to the state to control mapping'''
    def __init__(self):
        self.state_control_function_map = {       #states
            "a0": self.handle_waiting_state,            # WAITING
            "a1": self.handle_idle_state,               # IDLE
            "a2": self.handle_queue_updated_state,      # QUEUE_UPDATED
            "a3": self.handle_door_closed_state,        # DOOR_CLOSED
            "a4": self.handle_target_set_state,         # TARGET_SET
            "a5": self.handle_queue_popped_state,       # QUEUE_POPPED
            "a6": self.handle_door_opened_state,        # DOOR_OPENED
            "a7": self.handle_motors_moving_state,      # MOTORS_MOVING
            "a8": self.handle_updated_currfloor_state,  # UPDATED_CURRFLOOR
            "a9": self.handle_await_floor_requests_state, # AWAIT_FLOOR_REQUESTS
            "a10": self.handle_overloaded_state,        # OVERLOADED
            "a11": self.handle_redundant_call_removed_state, # REDUNDANT_CALL_REMOVED
            "a12": self.handle_motors_stopped_state     # MOTORS_STOPPED
        }
        
        self.state_index_map = {
            "WAITING": 0,
            "IDLE": 1,
            "QUEUE_UPDATED": 2,
            "DOOR_CLOSED": 3,
            "TARGET_SET": 4,
            "QUEUE_POPPED": 5,
            "DOOR_OPENED": 6,
            "MOTORS_MOVING": 7,
            "UPDATED_CURRFLOOR": 8,
            "AWAIT_FLOOR_REQUESTS": 9,
            "OVERLOADED": 10,
            "REDUNDANT_CALL_REMOVED": 11,
            "MOTORS_STOPPED": 12
        }
        
        self.dir ={
            1: "UP",
            0: "DOWN"
        }
    
    
    def handle_waiting_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Lift is in WAITING state...")
        # simply wait for lift call requests..not idle yet
        lift.idle_time = int(time.time() - lift.idle_start_time) 
        lift.current_state_index = self.state_index_map["WAITING"]
        if lift.previous_state_index != self.state_index_map["WAITING"]:
            lift.idle_start_time = time.time()
        
        print(f"lift idle time: {lift.idle_time} seconds ? {lift.MAX_IDLE_TIME} seconds")
        lift.previous_state_index = lift.current_state_index
        

    def handle_idle_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print(f"\n@@@ Lift is idle at floor {lift.current_floor}, Homing to floor {lift.target_floor}...")
        lift.target_floor = lift.HOME_FLOOR  
        lift.current_direction = lift.target_floor > lift.HOME_FLOOR 
        request_list.append((FLOOR_REQUEST, lift.target_floor, lift.current_direction))  
        lift.is_idle = True
        lift.current_state_index = self.state_index_map["IDLE"]
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0
             

    def handle_queue_updated_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Lift Not IDLE, Queue was updated, adding a new floor call request to the queue..., ")
        if len(request_list) == 0: #assuming check is done in the condition part
            raise ValueError("Request list is empty, cannot add new request.")
        #approp additiona of q requested queue is done in gui part
        lift.is_idle = False  
        lift.current_state_index = self.state_index_map["QUEUE_UPDATED"]
        
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0
        

    def handle_door_closed_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Lift Closing Door...")
        lift.door_closed = True
        lift.current_state_index = self.state_index_map["DOOR_CLOSED"]
        #-----------motor cmds----------------
        motor_controller.close_door()
        #TODO call a door closing music
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0


    def handle_target_set_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print(f"\n@@@ Lift Target floor set to {lift.target_floor}...by {request_list[0]}")
        if not len(request_list) == 0:
            raise ValueError("Request list is empty, cannot set target floor.")
        
        type, floor, direction = request_list[0]  # Assuming the first request is the target
        lift.target_floor = floor #assuming non-empty request list (check done in conditions)
        lift.current_direction = direction #or floor > lift.current_floor..same ig
        print(f"direction comparisons {floor > lift.current_floor} = {direction}")
        lift.current_state_index = self.state_index_map["TARGET_SET"]
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0
        

    def handle_queue_popped_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print(f"\n@@@ Lift Request Queue popped {request_list[0]}, processing next request...Remaining requests: {len(request_list)}")
        if len(request_list) == 0: # Assuming the request list is not empty checked in conditions
            raise ValueError("Request list is empty, cannot pop request.")
        request_list.pop(0)  # Remove the first request after processing it
        lift.current_state_index = self.state_index_map["QUEUE_POPPED"]
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0


    def handle_door_opened_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Lift Opening door...")
        lift.door_closed = False
        lift.current_state_index = self.state_index_map["DOOR_OPENED"]
        lift.floor_request_wait_start_time = time.time()  # Start the timer for floor request wait time
        #-----------motor cmds----------------
        motor_controller.open_door()
        #TODO call a door opening music
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0
        

    def handle_motors_moving_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print(f"\n@@@ Motors moving {self.dir[lift.current_direction]} towards target floor {lift.target_floor}...")
        lift.motors_stopped = False
        lift.current_state_index = self.state_index_map["MOTORS_MOVING"]
        #-----------motor cmds----------------
        motor_controller.move_up() if lift.current_floor < lift.target_floor else motor_controller.move_down()
        #TODO call a moving music
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0


    def handle_updated_currfloor_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        if lift.current_floor < lift.target_floor:
            lift.current_floor += 1
        elif lift.current_floor > lift.target_floor:
            lift.current_floor -= 1
        print(f"\n@@@ Updating current floor...to {lift.current_floor}")
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0


    def handle_await_floor_requests_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Waiting for dialpad floor requests...")
        # waits for new requests (queue is empty, no movement)
        lift.floor_request_wait_time = int(time.time() - lift.floor_request_wait_start_time)
        # lift.rather than sorting..i'll just pop it if i reach there on the way 
        
        lift.current_state_index = self.state_index_map["AWAIT_FLOOR_REQUESTS"]
        if len(request_list) == 0:
            print("No new floor requests, remaining idle.")
        else:
            print(f"Floor requests pending: {len(request_list)}.")
            
        lift.previous_state_index = lift.current_state_index #as reaches state 0


    def handle_overloaded_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print(f"\n@@@ Lift is overloaded! motors:  check: {lift.motors_stopped}")
        lift.current_state_index = self.state_index_map["OVERLOADED"]
        # TODO play alarm , Handle the overloaded situation, e.g., prevent movement, alarm, etc.
        # motor_controller.stop()  # already stopped at this moment
        print("Lift stopped due to overload.")
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0


    def handle_redundant_call_removed_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Redundant call removed...")
        # to remove redundant requests from the queue 
        if len(request_list) == 0:
            raise ValueError("Request list is empty, cannot remove redundant call.")
        
        for idx, (type, floor, direction) in enumerate(request_list):
            if floor == lift.current_floor:
                request_list.pop(idx)  # Remove the redundant request..prolly those requests which might come from lift calls...lift might anyways go there if that floor pressed inside the lift
                       
        print(f"Removed redundant request. Remaining requests: {len(request_list)}.")
        lift.current_state_index = self.state_index_map["REDUNDANT_CALL_REMOVED"]
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0
        
    def handle_motors_stopped_state(self, lift: LIFT_SYSTEM, request_list, motor_controller):
        print("\n@@@ Motors stopped.")
        lift.motors_stopped = True
        lift.current_state_index = self.state_index_map["MOTORS_STOPPED"]
        #-----------motor cmds----------------
        motor_controller.stop_motors()  
        # Lift has reached its destination or stopped due to an error
        print(f"Lift stopped at floor {lift.current_floor}.")
        
        lift.previous_state_index = lift.current_state_index #as reaches state 0


#I'm following the structure in the CS426 , gourinath sir's handbook 
class ControlMemoryEntry:
    def __init__(self, control=None, imm_transition=False):
        self.control = control  # This will hold function references that interact with motors
        self.imm_transition = imm_transition

class ControlMemory:
    ''' Need to manually change the control memory array according to the transition equations (for imm_transitions) '''
    def __init__(self):
        # Initialize the control memory functions
        self.control_memory_functions = ControlMemoryFunctions()  
        
        # Initialize control memory array, setting transition types for states
        self.control_memory_array = [
            ControlMemoryEntry(
                self.control_memory_functions.state_control_function_map[f"a{i}"], 
                True if i in [6, 7, 10, 12] else False
            ) for i in range(13)
        ]

        
