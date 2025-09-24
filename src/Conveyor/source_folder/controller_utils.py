from utils import SwitchAction, BayName

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


def schedule_with_priority(buffer: dict):
    
    bay_buffer = buffer.get(SwitchAction.go_to_bay)
    if bay_buffer is not None:
        return SwitchAction.go_to_bay

    in_up = buffer.get("IN_UP")
    in_down = buffer.get("IN_DOWN")

    # If both inputs are empty
    if not in_up and not in_down:
        return None

    # Only one has items
    if not in_up:
        return "IN_DOWN"
    if not in_down:
        return "IN_UP"

    # Both have items: determine priority based on actions
    up_action = in_up[0].action
    down_action = in_down[0].action

    # Both want to go OUT → allow BOTH
    if up_action == SwitchAction.advance and down_action == SwitchAction.advance:
        return SwitchAction.double_advance

    # Prioritize OUT actions
    if up_action == SwitchAction.advance:
        return "IN_UP"
    if down_action == SwitchAction.advance:
        return "IN_DOWN"

    # Prioritize BAY over CROSS
    if up_action == SwitchAction.go_to_bay:
        return "IN_UP"
    
    if down_action == SwitchAction.cross and not in_down[0].bay:
        return "IN_DOWN"

    if up_action == SwitchAction.cross and not in_up[0].bay:
        return "IN_UP"

    # Fallback
    return "IN_DOWN"
