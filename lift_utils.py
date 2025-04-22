


#  "LIFT_CALL"/ "FLOOR_REQUEST"
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
