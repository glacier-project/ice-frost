# Conveyor

The simulated conveyor is `CellConveyor.lf`, which extends `base/MetaConveyor.lf` (the data model of the
conveyor OPC UA server) and instantiates the belt of `Conveyor/conveyor.lf`: segments, switches,
interchanges and bays, orchestrated by `Conveyor/controller.lf`. Pallets with no destination keep looping
on the ring. Against the real plant, `OpcuaConveyor.lf` uses the same `MetaConveyor` on the real server.

### Layout
```
Data model
  Bay 1        Bay 2        Bay 3       Bay 4    LoadUnloadZone
   |            |          |            |             |
   ◼ Segment1  ◼ Segment2 ◼  Segment3 ◼  Segment4  ◼
   |            |          |            |             |
   ◼  Segment8 ◼ Segment7 ◼  Segment6 ◼  Segment5  ◼

Model (switches)
   Z         P         O         N
   |         |         |         |
   M ------- L ------- I ------- H ------- G--- F
   |         |         |         |              |
   E ------- D ------- C ------- B ------------ A
```

### Timings

Travel and transfer times are parameters of the belt reactors, set per reactor in
`resources/frost_config.yml` (`conveyor` → `conveyor_belt` → `Segment_N: segment_time` [ms], interchanges
`interchange_time`, ...). The values in the `.lf` files are only defaults.

---

## Sending a pallet to a destination

Call the method `setPalletDestination`:

```plaintext
Objects/ConveyorHMI/ConveyorDataExchange/Commands/ConveyorCommandsPointer/setPalletDestination
```

- `palletNumber` (integer, 1..10)
- `destination` (integer, see below)

It returns `False` (and logs an error) for an unknown pallet or an invalid destination, and nothing moves.
The same check applies to any write of `Objects/ConveyorHMI/ConveyorObjects/Pallets/Pallet<N>/destination`.
A pallet does not need to be freed before it gets a new destination.

## Destinations

A destination is `bay * 8 + position`:

| Code | Place |
| --- | --- |
| `0` | Main belt |
| `9` | Bay 1, SPEA (cell 1), single position |
| `17`, `18`, `19` | Bay 2, milling (cell 2), positions 1, 2, 3 |
| `25`, `26`, `27` | Bay 3, assembly (cell 4), positions 1, 2, 3 |
| `33`, `34`, `35` | Bay 4, quality (cell 5), positions 1, 2, 3 |
| `40` (or `41`) | Load/unload bay (`40` is the code the line uses) |

Position 1 is the bay entrance. A pallet can move between positions of the same bay (e.g. `34` -> `35`),
one position at a time, only into free positions.

Example: pallet 4 to position 2 of the quality bay (cell 5) is `setPalletDestination(4, 34)` (`4 * 8 + 2`):

```yaml
sender: "scheduler"
target: "conveyor"
header:
  type: "REQUEST"
  version: [1, 0, 0]
  namespace: "METHOD"
  msg_name: "INVOKE"
payload:
  node: "Objects/ConveyorHMI/ConveyorDataExchange/Commands/ConveyorCommandsPointer/setPalletDestination"
  args: [4, 34]
```

A complete recipe: `resources/scheduler_tasks/demo-lego-scheduler.yml`.
