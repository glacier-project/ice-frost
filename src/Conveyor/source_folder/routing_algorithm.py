from utils import BayAction, SwitchAction, BayName, SwitchName
from bay_routing_algorithm import check_bay_available, compute_bay_route
# Constants: Define the main matrix and bay mapping
MAIN_MATRIX = [
    [SwitchName.M.value, SwitchName.L.value, SwitchName.I.value, SwitchName.H.value, BayName.LU.value, SwitchName.F.value],
    [SwitchName.E.value, SwitchName.D.value, SwitchName.C.value, SwitchName.B.value, 'Empty', SwitchName.A.value]
]

BAY_MATRIX = [
    [BayName.Bay2_1.value, BayName.Bay2_2.value, BayName.Bay2_3.value],
    [BayName.Bay3_1.value, BayName.Bay3_2.value, BayName.Bay3_3.value],
    [BayName.Bay4_1.value, BayName.Bay4_2.value, BayName.Bay4_3.value]
]

BAY_MAPPING = {
    0: 'L',
    1: 'I',
    2: 'H'
}

# Helper function to get matrix coordinates for a given value
def get_coordinates(value):
    for row_index, row in enumerate(MAIN_MATRIX):
        for col_index, element in enumerate(row):
            if element == value:
                return (row_index, col_index)
    return None

# Get corresponding MAIN_MATRIX letter for a bay code
def get_bay_coordinates(value):
    if value == BayName.Bay1_1.value:
        return SwitchName.M.value  # Special case

    for row_index, row in enumerate(BAY_MATRIX):
        if value in row:
            return BAY_MAPPING[row_index]
    return None

# Core movement logic: determines next direction or action
def get_action(current_position, destination):
    # Get coordinates in MAIN_MATRIX, handling bay positions
    current_coords = get_coordinates(current_position) or get_coordinates(get_bay_coordinates(current_position))
    destination_coords = get_coordinates(destination) or get_coordinates(get_bay_coordinates(destination))

    # Safety check
    if not current_coords or not destination_coords:
        return None

    # Same position => already at bay
    if current_coords == destination_coords:
        return SwitchAction.go_to_bay

    curr_row, curr_col = current_coords
    dest_row, dest_col = destination_coords

    # Movement within same row
    if curr_row == dest_row:
        return SwitchAction.advance if curr_col < dest_col else SwitchAction.cross

    # Movement from top to bottom row
    if curr_row == 0 and dest_row == 1:
        if current_position == SwitchName.M.value or curr_col < dest_col:
            return SwitchAction.advance
        else:
            return SwitchAction.cross

    # Movement from bottom to top row
    if curr_row == 1 and dest_row == 0:
        if curr_col > dest_col:
            return SwitchAction.advance
        else:
            return SwitchAction.cross

    raise Exception(f"Error in get_action: current_position={current_position}, destination={destination}")


# High-level routing function
def calculate_next_action(position: str, destination: str, bay_status: list | None, pallet_id: int):
    if position == None:
        raise Exception("Error in calculate_next_action: position is None")
    
    if position == BayName.LU.value:
        return BayAction.none if destination == BayName.LU.value else BayAction.back
    
    if position not in SwitchName.values() and position != BayName.LU.value:
        return compute_bay_route(position, destination, bay_status, pallet_id)
    if destination == "0":
        if position == SwitchName.E.value or position == SwitchName.H.value:
            return SwitchAction.cross
        return SwitchAction.advance

    # Fast-path: Direct mapping of matrix position to bay row
    if (position == "L" and destination.startswith("Bay2")) or \
       (position == "I" and destination.startswith("Bay3")) or \
       (position == "H" and destination.startswith("Bay4")):
        return check_bay_available(bay_status, int(destination[-1]), pallet_id)
    
    if (position == "M" or position == "E") and destination == BayName.Bay1_1.value:        
        if bay_status[0] == 0 and position == "M":
            bay_status[0] = pallet_id
            return SwitchAction.go_to_bay
        else:
            return SwitchAction.cross if position == "E" else SwitchAction.advance

    return get_action(position, destination)
