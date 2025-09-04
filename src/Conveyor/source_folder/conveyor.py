from enum import Enum
class PalletAction(Enum):
    OUT = 1
    CROSS = 2
    BAY = 3

class ConveyorMessage(Enum):
    ARRIVED = "ARRIVED"
    MOVE = "MOVE"
    FREE = "FREE"
    CREATE = "CREATE"
    RELEASED = "RELEASED"
    BAY_MOVE = "BAY_MOVE"
