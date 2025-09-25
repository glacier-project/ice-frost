from utils import  BayName

def new_destination(dest, length_pos):
    
    # Immediate move to bay if destination is 'Z'
    if dest == BayName.Bay1_1.value:
        return [False, True, dest]

    # If position has only one item
    if length_pos == 1:
        if dest == BayName.LU.value:
            return [False, False, dest]  # Hold
        elif dest is None:
            return [True, False, None]   # Add new
        else:
            return [False, True, dest]   # Move current

    # If two items in queue
    if length_pos == 2:
        if dest == BayName.LU.value:
            return [False, False, dest]  # Hold
        elif dest is None:
            return [True, False, None]   # Add new
        else:
            return [False, True, dest]   # Move current


