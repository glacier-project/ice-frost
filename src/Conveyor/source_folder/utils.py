from enum import Enum

class Events(Enum):
    pallet_arrived = 1
    pallet_released = -1

class ControllerCommand(Enum):
    move = "move"
    create = "create"
    update = "update"

class SwitchAction(Enum):
    advance = "advance"
    cross = "cross"
    go_to_bay = "go_to_bay"
    double_advance = "double_advance"

class SwitchName(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    H = "H"
    I = "I"
    L = "L"
    M = "M"

class InterchangeName(Enum):
    LD = "LD"
    IC = "IC"
    HB = "HB"

class SegmentName(Enum):
    Segment1 = "Segment1"
    Segment2 = "Segment2"
    Segment3 = "Segment3"
    Segment4_0 = "Segment4_0"
    Segment4_1 = "Segment4_1"
    Segment5 = "Segment5"
    Segment6 = "Segment6"
    Segment7 = "Segment7"
    Segment8 = "Segment8"

class Mutex(Enum):
    EM = "EM"
    FA = "FA"