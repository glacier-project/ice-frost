def compute_bay_route(position, destination, bay):
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
    
    raise Exception(f"Error in Bay_Routing {position}, {destination}, {bay}")

def check_bay_available(buff, val):
    for i in range(0, val):
        if not buff[i]:
            return False
    return True

def leave_bay(buff, val):    
    buff[val-1] = False

def update_bay_positions(Bay, n, route):
    n = n - 1
    if n == 0:
        if route == "CROSS":
            Bay[n] = True
    if n == 1:
        Bay[n] = True
        if route == "CROSS":
            Bay[0] = False
        else:
            Bay[2] = False
    if n == 2:
        Bay[2] = True
        Bay[1] = False