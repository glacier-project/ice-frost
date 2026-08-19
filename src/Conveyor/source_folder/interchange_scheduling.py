from utils import SwitchAction, InterchangeInputs


def schedule_with_priority(status: dict, actions: dict) -> list[InterchangeInputs]:
    
    if status[InterchangeInputs.BAY] != None:
        return [InterchangeInputs.BAY]

    in_up = status.get(InterchangeInputs.UPPER_SEGMENT)
    in_down = status.get(InterchangeInputs.LOWER_SEGMENT)

    up_action = None
    down_action = None
    if in_up != None:
        up_action = actions[in_up]
    if in_down != None:
        down_action = actions[in_down]

    if in_up == None and in_down == None:
        return None
    
    if in_up == None:
        return [InterchangeInputs.LOWER_SEGMENT]
    if in_down == None:
        return [InterchangeInputs.UPPER_SEGMENT]

    if up_action == SwitchAction.advance and down_action == SwitchAction.advance:
        return [InterchangeInputs.UPPER_SEGMENT, InterchangeInputs.LOWER_SEGMENT]
    
    if up_action == SwitchAction.go_to_bay and down_action == SwitchAction.advance:
        return [InterchangeInputs.UPPER_SEGMENT, InterchangeInputs.LOWER_SEGMENT]

    if down_action == SwitchAction.go_to_bay:
        return [InterchangeInputs.LOWER_SEGMENT]

    if up_action == SwitchAction.cross:
        return [InterchangeInputs.UPPER_SEGMENT]
    if down_action == SwitchAction.cross:
        return [InterchangeInputs.LOWER_SEGMENT]

    raise Exception(f"Error in schedule_with_priority: unable to schedule interchange, status={status}, actions={actions}")

