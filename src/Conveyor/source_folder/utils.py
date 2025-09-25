from enum import Enum

class Events(Enum):
    pallet_arrived = 1
    pallet_created = 1
    pallet_released = -1

class InterchangeInputs(Enum):
    BAY = "BAY"
    UPPER_SEGMENT = "UPPER_SEGMENT"
    LOWER_SEGMENT = "LOWER_SEGMENT"

class ControllerCommand(Enum):
    move = 0
    create = 1

class SegmentAction(Enum):
    advance = 0

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

    def values():
        return [item.value for item in SwitchName]

class SegmentName(Enum):
    Segment_1 = "Segment_1"
    Segment_2 = "Segment_2"
    Segment_3 = "Segment_3"
    Segment_4_1 = "Segment_4_1"
    Segment_4_2 = "Segment_4_2"
    Segment_5 = "Segment_5"
    Segment_6 = "Segment_6"
    Segment_7 = "Segment_7"
    Segment_8 = "Segment_8"

    def values():
        return [item.value for item in SegmentName]

class BayName(Enum):
    Bay2 = "Bay2"
    Bay3 = "Bay3"
    Bay4 = "Bay4"
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

    def values():
        return [item.value for item in BayName]

class InterchangeName(Enum):
    LD = "LD"
    IC = "IC"
    HB = "HB"
    EM = "EM"
    FA = "FA"