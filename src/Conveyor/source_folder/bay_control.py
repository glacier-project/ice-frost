def Bay_Control(buff, val):
    for i in range(0, val):
        if not buff[i]:
            return False
    return True

def Update_Truth_Table(buff, val):    
    buff[val-1] = False

def Update_Bay(Bay, n, route):
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
