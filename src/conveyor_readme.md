# Introduction

The conveyor belt system is composed of multiple reactors, instantiated via `conveyor.lf`. Key components include segments, switches, and more. The controller orchestrates commands and manages events for these components.

In Frost, the conveyor reactor is instantiated within `Cell_Conveyor.lf`. Pallets move automatically along the ring structure.

### Conveyor Layout
```
Data Model Version
  Bay 1        Bay 2        Bay 3       Bay 4  Bay G
   |            |          |            |       |
   |            |          |            |       |
   ◼ Segment1  ◼ Segment2 ◼  Segment3 ◼  Segment4  ◼
   |            |          |            |             |          
   |            |          |            |             |          
   ◼  Segment8 ◼ Segment7 ◼  Segment6 ◼  Segment5  ◼ 


Model Version
   Z         P         O         N
   |         |         |         |
   |         |         |         |
   M ------- L ------- I ------- H ------- G--- F
   |         |         |         |              |
   |         |         |         |              |
   E ------- D ------- C ------- B ------------ A
```

---

## Sending a Pallet to a Destination

To assign a destination, use the `CompositeMethodNode` method `setPalletDestination`.

**Path:**
```plaintext
Cell_Conveyor/ConveyorHMI/ConveyorDataExchange/Commands/ConveyorCommandsPointer/setDestination
```
**Parameters:**  
- `palletNumber` (integer)  
- `destination` (integer)

---

## Allowed Destinations

Use the node above to send a pallet to a destination or move it to the main belt.

**Destinations:**

- `0`: Main belt

**Single Position Bays:**
- `11`: SPEA (BAY Z)
- `5`: LoadUnloadBay (BAY G)

**Multiple Position Bays:**
- `2`: Milling (BAY P)
- `3`: Assembly (BAY O)
- `4`: Quality (BAY N)

Multiple position bays have three available positions (1, 2, 3).  
To target a specific position, combine the bay number and position number.

**Example:**  
Send a pallet to position 2 in the Quality cell (cell 5): `42` (`4` = Quality, `2` = position)

---

### Message Example

```yaml
sender: "Scheduler"
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

Refer to the recipe in `recipes/recipes/conveyor.yaml` for additional examples.

> **Note:** You do not need to free a pallet before assigning it a new destination.

