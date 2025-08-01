# Introduction
The conveyor belt is a composition of reactors instantiated by conveyor.lf. The conveyor belt has several components like segments, switches etc...
The controller sends commands to those components and handles their events.

In frost we instantiated that conveyor reactor inside Cell_Conveyor.lf
The pallets are moving automatically on the long ring.
```
Segment1 -> Segment2 -> Segment3
   |           |            |
   |           |            |
Segment8 <- Segment7 <- Segment6
```

```
   Z         P         O         N
   |         |         |         |
   |         |         |         |
   M ------- L ------- I ------- H ------- G--- F
   |         |         |         |              |
   |         |         |         |              |
   E ------- D ------- C ------- B ------------ A
```

## SendPallet to a destination
For assigning a destination use the CompositeMethodNode setPalletDestination. 

Path:
```plaintext
"Cell_Conveyor/ConveyorHMI/ConveyorDataExchange/Commands/ConveyorCommandsPointer/setDestination"
```
It needs the palletNumber and destination both as integer.

## Allowed Destinations
Use that node for sending a pallet to a destination and for moving the pallet to the main belt.
Destinations:

```
0 = use this as destination when you want to send a pallet to the main belt

Single position Bay
11 = SPEA, in the conveyor model is BAY Z
5 = LoadUnloadBay, in the model is BAY G

MultiplePositionBay
2 = Milling, in the conveyor model is BAY P
3 = Assebly, in the conveyor model is BAY O
4 = Quality, in the conveyor model is BAY N
```
MultiplePositionBay have 3 available position (1, 2, 3).

To send a pallet in a specific position compose the bay number with the position number.

Example: Send pallet to position 2 in the quality cell (cell5) -> 42 (4 -> Quality, 2->position)

```
Message Example:
- sender: "Scheduler"
    target: "Cell_Conveyor"
    header:
      type: "REQUEST"
      version: [1, 0, 0]
      namespace: "METHOD"
      msg_name: "INVOKE"
    payload:
      node: "CellConveyor/ConveyorHMI/ConveyorDataExchange/Commands/ConveyorCommandsPointer/setPalletDestination"
      args: [4, 42]
```

Please check out the recipe in "recipes/recipes/conveyor.yaml" for other examples.


 * Note: You don't need to free a pallet before sending it to a new destination

