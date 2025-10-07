from machine_data_model.protocols.frost_v1.frost_message import FrostMessage
from machine_data_model.protocols.frost_v1.frost_header import FrostHeader, MsgType, MsgNamespace, VariableMsgName, MethodMsgName
from machine_data_model.protocols.frost_v1.frost_payload import FrostPayload, VariablePayload, MethodPayload


def convert_to_frost_message(correlation_id: str, message: dict, sender: str, target: str) -> FrostMessage:
    """
    Converts a ICE request message to a FrostMessage.

    Args:
        correlation_id (str): The correlation ID for the message.
        message (dict): The ICE request message containing method, args, and kwargs.
        sender (str): The sender of the message.
        target (str): The target of the message.
    Returns:
        FrostMessage: The converted FrostMessage object.
    Raises:
        ValueError: If the request type is unknown.
    """

    request_type = message["method"]
    if request_type == "read":
        return FrostMessage(
            sender=sender,
            target=target,
            correlation_id=correlation_id,
            header=FrostHeader(
                type=MsgType.REQUEST,
                version=(1, 0, 0),
                namespace=MsgNamespace.VARIABLE,
                msg_name=VariableMsgName.READ,
            ),
            payload=VariablePayload(node=message["args"][0]),
        )
    elif request_type == "write":
        return FrostMessage(
            sender=sender,
            target=target,
            correlation_id=correlation_id,
            header=FrostHeader(
                type=MsgType.REQUEST,
                version=(1, 0, 0),
                namespace=MsgNamespace.VARIABLE,
                msg_name=VariableMsgName.WRITE,
            ),
            payload=VariablePayload(node=message["args"][0], value=message["args"][1]),
        )
    elif request_type == "method":
        return FrostMessage(
            sender=sender,
            target=target,
            correlation_id=correlation_id,
            header=FrostHeader(
                type=MsgType.REQUEST,
                version=(1, 0, 0),
                namespace=MsgNamespace.METHOD,
                msg_name=MethodMsgName.INVOKE,
            ),
            payload=MethodPayload(node=message["args"][0], 
            kwargs=message["kwargs"]),
        )
    
    raise ValueError(f"Unknown request type: {request_type}")



def convert_to_ice_message(message: FrostMessage) -> dict:
    """
    Converts a FrostMessage to an ICE response message.

    Args:
        message (FrostMessage): The FrostMessage to convert.
    
    Returns:
        dict: The converted ICE response message.

    Raises:
        ValueError: If the FrostMessage type is not supported.
    """
    assert message.header.type == MsgType.RESPONSE, "Only FrostMessage of type RESPONSE can be converted to ICE message"

    response ={
        "key": message.correlation_id,
        "body": {}
    }
    
    if message.header.namespace == MsgNamespace.VARIABLE:
        assert isinstance(message.payload, VariablePayload), "FrostMessage payload must be VariablePayload for VARIABLE namespace"
        if message.header.msg_name == VariableMsgName.READ:
            response["body"] = {
                "result": True,
                "value": [message.payload.value],
                "returns": {},
            }
        elif message.header.msg_name == VariableMsgName.WRITE:
            response["body"] = {
                "method": "write",
                "value": [message.payload.value],
                "returns": {},
            }
    elif message.header.namespace == MsgNamespace.METHOD:
        assert isinstance(message.payload, MethodPayload), "FrostMessage payload must be MethodPayload for METHOD namespace"
        ret = list(message.payload.ret.values())[0][1]
        if message.header.msg_name == MethodMsgName.INVOKE:
            response["body"] = {
                "method": "method",
                "value": [ret],
                "returns": {},
            }
    else:
        raise ValueError(f"Unsupported FrostMessage type: {message.header.namespace}.{message.header.msg_name}")
    
    return response