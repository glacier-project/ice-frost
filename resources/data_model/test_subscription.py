from machine_data_model.builder.data_model_builder import DataModelBuilder
from machine_data_model.protocols.frost_v1.frost_message import FrostMessage
from machine_data_model.protocols.frost_v1.frost_header import MsgType, MsgNamespace, FrostHeader, VariableMsgName
from machine_data_model.protocols.frost_v1.frost_payload import VariablePayload
import uuid
from machine_data_model.protocols.frost_v1.frost_protocol_mng import FrostProtocolMng

conveyor_obj = "Cell_Conveyor/ConveyorHMI/ConveyorObjects/"
Pallets = "Pallets/"
Bayes = "Bayes/"
Segments = "Segments/"
Commands = "Commands/"
commands_pointer = "Cell_Conveyor/ConveyorHMI/ConveyorDataExchange/Commands/ConveyorCommandsPointer/"
IndexPosition = "IndexPosition"
setDestination = "setDestination"
PalletPosition = "PalletPosition{n}"
palletNum = "palletNum"
Pallet = "Pallet{n}"
Pallet1 = Pallet.format(n=1)
Pallet2 = Pallet.format(n=2)
Pallet3 = Pallet.format(n=3)
Pallet4 = Pallet.format(n=4)
Pallet5 = Pallet.format(n=5)
Pallet6 = Pallet.format(n=6)
Pallet7 = Pallet.format(n=7)
Pallet8 = Pallet.format(n=8)
Pallet9 = Pallet.format(n=9)
Pallet10 = Pallet.format(n=10)
Bay = "Bay{n}"
Bay1 = Bay.format(n=1)
Bay2 = Bay.format(n=2)
Bay3 = Bay.format(n=3)
Bay4 = Bay.format(n=4)
Bay5 = "LoadUnloadZone"
Segment = "Segment{n}"
Segment1 = Segment.format(n=1)
Segment2 = Segment.format(n=2)
Segment3 = Segment.format(n=3)
Segment4 = Segment.format(n=4)
Segment5 = Segment.format(n=5)
Segment6 = Segment.format(n=6)
Segment7 = Segment.format(n=7)
Segment8 = Segment.format(n=8)
FIFO = "FIFO"
size = "size"
item = "item{n}"

machine = "Cell_Conveyor"
variable_path = conveyor_obj + Segments + Segment1+ "/FIFO"

request = FrostMessage(
    sender="iceproxy",
    target=machine,
    identifier=str(uuid.uuid4()),
    header=FrostHeader(
        type=MsgType.REQUEST,
        version=(1, 0, 0),
        namespace=MsgNamespace.VARIABLE,
        msg_name=VariableMsgName.SUBSCRIBE,
    ),
    payload=VariablePayload(node=variable_path),
)

data_model = DataModelBuilder().get_data_model(data_model_path="src/models/Cell_Conveyor.yml")
protocol_mng = FrostProtocolMng(data_model=data_model)

print(f"Request: {request}")
response = protocol_mng.handle_request(request)
print(response)

item_0 = data_model.get_node(conveyor_obj + Segments + Segment1 + "/FIFO/item0")
item_0.value = 42

# update the value of the Segment1 variable
print(protocol_mng.get_update_messages())
