from enum import Enum

class Events(Enum):
    pallet_arrived = 1

class Pallet_Action(Enum):
    OUT = "OUT"
    CROSS = "CROSS"
    BAY = "BAY"
    BOTH = "BOTH"

class Switch_Name(Enum):
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

class Segment_Name(Enum):
    AB = "AB"
    BC = "BC"
    CD = "CD"
    DE = "DE"
    ML = "ML"
    LI = "LI"
    IH = "IH"
    HG = "HG"
    GF = "GF"

class Bay_Name(Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    O1 = "O1"
    O2 = "O2"
    O3 = "O3"
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"

class Bay_Action(Enum):
    Move_in_bay = "Move_in_bay"
    Move = "Move"