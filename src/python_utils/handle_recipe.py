import yaml
import uuid
import sys
from machine_data_model.protocols.frost_v1.frost_message import FrostMessage
from machine_data_model.protocols.frost_v1.frost_header import *
from machine_data_model.protocols.frost_v1.frost_payload import VariablePayload, MethodPayload

class Condition:
    def __init__(self, machine: str, header: str, node: str, value: str):
        self.machine = machine
        self.header = header
        self.node = node
        self.value = value

    def __str__(self):
        return f"Machine: {self.machine}, Header: {self.header}, Node: {self.node}, Value: {self.value}"

    def __repr__(self):
        return self.__str__()

    def check_condition(self, machine: str, header: str, node: str, value: str):
        return self.machine == machine and self.header == header and self.node == node

    def check_condition(self, message: FrostMessage) -> bool:
        if self.machine != message.sender:
            return False
        
        if self.header == MsgNamespace.METHOD.value and self.node in message.payload.ret:
            return self.value == message.payload.ret[self.node]
        elif self.header == MsgNamespace.VARIABLE.value:
            return True

        return False

def get_conditions(path: str) -> list:
    '''
    This function reads a YAML file and returns a list of dictionaries containing the conditions
    specified in the YAML file.
    Args:
        path (str): The path to the YAML file
    Returns:
        list: A list of dictionaries containing the conditions specified in the YAML file
    '''

    list_of_conditions = []
    with open(path, 'r') as file:
        recipe = yaml.safe_load(file)
        if not isinstance(recipe, dict) or "conditions" not in recipe or not isinstance(recipe["conditions"], list):
            raise ValueError("YAML file must contain a 'conditions' list")
        for item in recipe["conditions"]:
            if not isinstance(item, dict) or "node" not in item or "value" not in item:
                raise ValueError("Each condition must be a dictionary with 'node' and 'value' keys")
            condition = Condition(
                machine=item["machine"],
                header=item["header"],
                node=item["node"],
                value=item["value"]
            )
            list_of_conditions.append(condition)
    return list_of_conditions

def get_messages(path: str) -> list:
    '''
    This function reads a YAML file and returns a list of FrostMessage objects
    Args:
        path (str): The path to the YAML file
    Returns:
        list: A list of FrostMessage messages
    '''
    list_of_messages = []
    with open(path, 'r') as file:
        recipe = yaml.safe_load(file)
        if not isinstance(recipe, dict) or "steps" not in recipe or not isinstance(recipe["steps"], list):
            raise ValueError("YAML file must contain a 'steps' list")
        for item in recipe["steps"]:
            sender = item["sender"]
            target = item["target"]
            identifier = uuid.uuid4()
            header = FrostHeader(
                type=MsgType[item["header"]["type"]],
                version=tuple(item["header"]["version"]),
                namespace=MsgNamespace[item["header"]["namespace"]],
                msg_name=(
                    VariableMsgName[item["header"]["msg_name"]]
                    if item["header"]["namespace"] == "VARIABLE"
                    else MethodMsgName[item["header"]["msg_name"]]
                    if item["header"]["namespace"] == "METHOD"
                    else None
                )
            )
            payload=None
            if header.namespace is None:
                raise ValueError(f"Unsupported namespace: {item['header']['namespace']}")
            if "payload" in item:
                if header.namespace == MsgNamespace.VARIABLE:
                    payload = VariablePayload(
                        node=item["payload"]["node"],
                        value=item["payload"]["value"]
                    )
                elif header.namespace == MsgNamespace.METHOD:
                    payload = MethodPayload(
                        node=item["payload"]["node"],
                        args=item["payload"]["args"]
                    )
            else:
                payload = None
            message = FrostMessage(
                sender=sender,
                target=target,
                identifier=identifier,
                header=header,
                payload=payload
            )
            list_of_messages.append(message)

    return list_of_messages