from enum import Enum

class Events(Enum):
    pallet_arrived = 1
    pallet_released = -1

class ControllerCommand(Enum):
    move = 0
    create = 1
    update = 2
    double_advance = 3
    up_advance = 4
    down_advance = 5

class SwitchAction(Enum):
    advance = 0
    cross = 1
    go_to_bay = 2

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

class SegmentName(Enum):
    Segment1 = "Segment1"
    Segment2 = "Segment2"
    Segment3 = "Segment3"
    Segment4_1 = "Segment4_1"
    Segment4_2 = "Segment4_2"
    Segment5 = "Segment5"
    Segment6 = "Segment6"
    Segment7 = "Segment7"
    Segment8 = "Segment8"

class BayName(Enum):
    Bay1_1 = "Bay1_1"
    Bay2_1 = "Bay2_1"
    Bay2_2 = "Bay2_2"
    Bay2_3 = "Bay2_3"
    Bay3_1 = "Bay3_1"
    Bay3_2 = "Bay3_2"
    Bay3_3 = "Bay3_3"
    Bay4_1 = "Bay4_1"
    Bay4_2 = "Bay4_2"
    Bay4_3 = "Bay4_3"
    LU = "LoadUnloadZone"

class Mutex(Enum):
    EM = "EM"
    FA = "FA"

class InterchangeName(Enum):
    LD = "LD"
    IC = "IC"
    HB = "HB"