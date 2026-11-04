# ICE
This project models the ICE laboratory [(ICE)](https://www.icelab.di.univr.it/) with the **Frost** platform:
each machine is a **FrostReactor** that reproduces the behaviour and the data model of its real OPC UA
server, and the machines are connected through the **FrostLink**. A recipe (`resources/scheduler_tasks/`)
is run by the Frost scheduler, which sends **Frost messages** to the machines and waits for their answers.
The same recipe can run on the simulated machines or on the real plant over OPC UA.

## Layout

| Path | What |
|---|---|
| `src/CellConveyor.lf`, `src/Conveyor/` | conveyor and its belt (see `src/conveyor_readme.md`) |
| `src/Cell1.lf`, `Cell2.lf`, `Cell4.lf`, `Cell5.lf` | cells: flying probe tester, milling, robotic cell, quality cell (`src/fmu/QualityCell.fmu`) |
| `src/Kairos.lf`, `Etensil.lf`, `Warehouse.lf` | RB-Kairos missions, eTensil screwdriver, vertical warehouse |
| `src/base/` | base reactors: `MetaConveyor` (conveyor data model), `MissionMachine` (machines running named missions) |
| `src/Main.lf` | lego demo on the simulated machines, configured by `resources/frost_config.yml` |
| `src/OpcuaMain.lf` | lego demo on the real plant (conveyor, cell 4, cell 5 over OPC UA), configured by `resources/frost_config_ua.yml` |
| `resources/data_model/` | machine data models (`opcua_*.yml`: connectors to the real servers) |

## Building

Frost is consumed as a Lingua Franca package, vendored as a submodule under
`lf-packages/frost`. Clone with submodules:

```sh
git clone --recurse-submodules https://github.com/glacier-project/ice-frost.git
```

If you cloned before `v0.1.0`, the submodule moved from `frost/` to
`lf-packages/frost/` — resync it:

```sh
git submodule sync --recursive
git submodule update --init --recursive
```

Install the Python dependencies and build, from the repository root:

```sh
pip install -r requirements.txt
lfc src/Main.lf
python src-gen/Main/Main.py
```

## Real plant

`script/build_ua.sh` builds and runs `OpcuaMain`. The OPC UA endpoints come from the environment
(`ICE_CONVEYOR_IP/PORT`, `ICE_CELL4_IP/PORT`, `ICE_CELL5_IP/PORT`, e.g. in a `.envrc` loaded by direnv).
It drives the real machines.

## Dockerfile
To build the Docker image, run inside the directory:

```sh
docker build -t ice-frost-app .
docker run --rm -it --entrypoint /bin/bash ice-frost-app
```
