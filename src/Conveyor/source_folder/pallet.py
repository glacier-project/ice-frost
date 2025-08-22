from material import Material

class Pallet:
    def __init__(self, pallet_id:str, position:str):
        self.x_dimension:int = 24
        self.y_dimension:int  = 24
        self.pallet_id:int = pallet_id
        self.destination:str = None
        self.position:str = position
        self.action:str = None
        self.bay:bool = None
        self.object1:Material = None
        self.object2:Material = None
        self.object3:Material = None
        self.reserved:bool = False
        self.type:str = ""