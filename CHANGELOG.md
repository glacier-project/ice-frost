# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2026-08-19

### Breaking

- **Frost is now consumed as a Lingua Franca package instead of via Lingo.**
  `Lingo.toml` and `Lingo.lock` are removed; the build is driven directly by
  `lfc src/Main.lf`.
- **The Frost submodule moved from `frost/` to `lf-packages/frost/`** and now
  tracks `glacier-project/frost` on the `dev` branch.

  Existing clones must resync:

  ```sh
  git submodule sync --recursive
  git submodule update --init --recursive
  rm -rf frost   # if the old checkout is still present
  ```

### Added

- Integration demo combining Demo Lego with Cell 4, running against the real plant.
- `MetaConveyor` reactor with a `conveyor_graph` state and a `DistanceMetric`
  for pallet routing.
- Conveyor viewer.
- `OpcuaVirtualConveyor` reactor and `script/build_sim.sh` / `script/build_ua.sh`
  build helpers.
- Quality-cell FMU for Cell 5 simulation.

### Changed

- Conveyor subsystem refactored: all bays reachable, `Bay1_1` and `LUBay` added,
  bay-switch handling and bay timings corrected.
- Data models updated to match the real OPC UA node layout.
- Frost submodule updated to `7ada4a1`.

### Fixed

- `FrostBase.lf` import resolution under `lfc` (#8).
- Single-bay handling in the conveyor controller.
- Conveyor destination changes and bay switch behaviour.
- Demo Lego recipe, scripts, and configuration files.
- Cell 5 and warehouse corrections.

[v0.1.0]: https://github.com/glacier-project/ice-frost/releases/tag/v0.1.0
