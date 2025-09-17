def new_destination(dest, length_pos):
    """Determines the next conveyor action based on destination.
    Args:
        dest (str or None): The target destination ('Z', 'G', or None).
        length_pos (int): The number of items in the position queue.
    Returns:
        list: A list containing `[add_new, move_current, new_dest]`.
            - `looping` (bool): True to add a new item.
            - `bay` (bool): True to move the current item.
            - `new_dest` (str or None): The updated destination.
    """
    if dest == "Z":
        return [False, True, dest]
    if length_pos == 1: 
        if dest == "G":
            return [False, False, dest]
        elif dest == None:
            return [True, False, None]
        else:
            return [False, True, dest]
    elif length_pos == 2:
        if dest == "G":
            return [False, False, dest]           
        elif dest == None:
            return [True, False, None]
        else:            
            return [False, True, dest]

def schedule_with_priority(buffer:dict):
    temp = buffer["BAY"]
    str = "BAY"
    if temp is None:
        temp = buffer["IN_UP"]
        temp2 = buffer["IN_DOWN"]
        if not temp and not temp2:
            return None
        elif not temp:
            return "IN_DOWN"
        elif not temp2:
            return "IN_UP"
        else:
            if temp[0].action == "OUT" and temp2[0].action == "OUT":
                return "BOTH"
            elif temp[0].action == "OUT":
                return "IN_UP"
            elif temp2[0].action == "OUT":
                return "IN_DOWN"
            elif temp[0].action == "BAY":
                return "IN_UP"
            elif temp2[0].action == "CROSS" and temp2[0].bay == False:
                return "IN_DOWN"
            elif temp[0].action == "CROSS" and temp[0].bay == False:
                return "IN_UP"
            else:
                return "IN_DOWN"
    else:
        return str

