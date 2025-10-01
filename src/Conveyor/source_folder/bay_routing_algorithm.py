from utils import SwitchAction
 
#  Determines routing direction and final bay target for a given position and destination
def compute_bay_route(position, destination, bay):
    position_index = position[1]
    # Default destination fallback
    if not destination or len(destination) == 1:
        if position_index == "1":
            return SwitchAction.cross, f"{bay}1"
        elif position_index == "2":
            return SwitchAction.cross, f"{bay}2"
        elif position_index == "3":
            return SwitchAction.advance, f"{bay}3"
        
    dest_row, dest_col = destination[0], destination[1]

    # Routing logic based on current position in bay
    if position_index == "1":
        if dest_row != position[0]:
            return SwitchAction.cross, f"{bay}1"
        elif dest_col in ["2", "3"]:
            return SwitchAction.advance, f"{bay}1"

    elif position_index == "2":
        if dest_row != position[0]:
            return SwitchAction.cross, f"{bay}2"
        elif dest_col == "1":
            return SwitchAction.cross, f"{bay}2"
        elif dest_col == "3":
            return SwitchAction.advance, f"{bay}2"

    elif position_index == "3":
        return SwitchAction.advance, f"{bay}3"

    # Fallback error
    raise Exception(f"Error in compute_bay_route: position={position}, destination={destination}, bay={bay}")


# Checks if the first `val` bays in the buffer are occupied (True)
def check_bay_available(buffer, val):
    return all(buffer[i] == 0 for i in range(val))

# Marks a bay slot as unoccupied (False)
def leave_bay(buffer, val):
    buffer[val - 1] = 0

# Updates bay occupancy based on the slot `n` and movement direction (`route`)
def update_bay_positions(bay_buffer, slot, route):
    index = slot - 1  # Convert to 0-based index

    if index == 0:
        if route == SwitchAction.cross:
            bay_buffer[0] = True

    elif index == 1:
        bay_buffer[1] = True
        if route == SwitchAction.cross:
            bay_buffer[0] = False
        else:
            bay_buffer[2] = False

    elif index == 2:
        bay_buffer[2] = True
        bay_buffer[1] = False
