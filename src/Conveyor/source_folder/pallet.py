
class Pallet:
    def __init__(self, id:str, position:str):
        self.x_dimension:int = 24
        self.y_dimension:int  = 24
        self.id:int = id
        self.destination:str = None
        self.position:str = position
        self.action:str = None
        self.bay:bool = None
        self.object1 = None
        self.object2 = None
        self.object3 = None
        self.reserved:bool = False
        self.type:str = ""