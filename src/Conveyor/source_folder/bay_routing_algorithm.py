from utils import SwitchAction, BayName, SwitchName, BayAction
 
def compute_intra_bay_route(position, destination, bay_status, pallet_id):
    bay_row = int(position[-1]) - 1  # Extract bay row from position (e.g., 'Bay2_1' -> 1)
    dest_row = int(destination[-1]) - 1  # Extract destination row similarly

    if bay_row - dest_row > 0:
        if check_availability(bay_status, bay_row, pallet_id):
            bay_status[bay_row - 1] = pallet_id  # Mark bay as occupied
            bay_status[bay_row] = 0  # Free the current bay
            return BayAction.back
    elif bay_row - dest_row < 0:
        if check_availability_from_to(buffer=bay_status, from_value=bay_row, to_value=dest_row, pallet_id=pallet_id):
            bay_status[dest_row - 1] = pallet_id  # Mark bay as occupied
            bay_status[bay_row] = 0  # Free the current bay
            return BayAction.forward
    
    return BayAction.none  # Bay is occupied

def check_availability_from_to(buffer:list, from_value:int, to_value:int, pallet_id:int):
    for i in range(from_value, to_value):
        if buffer[i] != 0 and buffer[i] != pallet_id:  # 0 means the slot is free
            return False  # Bay is occupied
    return True  # All checked slots are free

#  Determines routing direction and final bay target for a given position and destination
def compute_bay_route(position, destination, bay, pallet_id):
    if destination != "0" and position[:4] == destination[:4]:  # Same bay area (Bay1, Bay2, Bay3, Bay4)
        return compute_intra_bay_route(position, destination, bay, pallet_id)
    else:  # Different bay areas
        return BayAction.back 

def check_availability(buffer:list, val:int, pallet_id:int):
    for i in range(val):
        if buffer[i] != 0 and buffer[i] != pallet_id:  # 0 means the slot is free
            return False  # Bay is occupied
    return True  # All checked slots are free

# Checks if the first `val` bays in the buffer are occupied (True)
def check_bay_available(buffer, val, pallet_id):
    temp = check_availability(buffer, val, pallet_id)
    if not temp:
        return SwitchAction.cross  # Bay is occupied
   
    buffer[val-1] = pallet_id  # Mark the slot as occupied with pallet_id
    return SwitchAction.go_to_bay
