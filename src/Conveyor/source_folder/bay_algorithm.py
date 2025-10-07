def Bay_Routing(position, destination, bay):
    if destination is None:
        destination = "A1"
    elif len(destination) == 1:
        destination = "A1"
    n = position[1]
    if "A1" == destination:
        if n == 1:
            return "CROSS", bay + "1"
        elif n == 2:
            return "CROSS", bay + "2"
        elif n == 3:
            return "OUT", bay + "3"    
    
    if position[1] == "1" :
        if destination[0] != position[0]:
            return "CROSS", bay + "1"
        elif destination[1] in ["2", "3"]:
            return "OUT", bay + "1"
            
    elif position[1] == "2" :
        if destination[0] != position[0]:
            return "CROSS", bay + "2"
        elif destination[1] == "1":
            return "CROSS", bay + "2"
        elif destination[1] == "3":
            return "OUT", bay + "2"
    
    elif position[1] == "3" :
            return "OUT", bay + "3"
    