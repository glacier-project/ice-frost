#!/usr/bin/env python3
"""Live conveyor viewer based on pallet position updates.

This script tails the pallet update CSV produced by MetaConveyor
(when SAVE_PUPDATES=true) and renders a real-time animation.

Default CSV pattern:
  pallet_distance_metric_log_*.csv

Usage examples:
  python script/live_conveyor_view.py
  python script/live_conveyor_view.py --file pallet_distance_metric_log_xxx.csv
  python script/live_conveyor_view.py --search-dir . --refresh-ms 150
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib import patches
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: matplotlib. Install it with 'pip install matplotlib'."
    ) from exc


# Physical layout copied from the benchmark model in
# benchmarks/pallet-selection/python_utils/plot_conveyor.py.
#
# Coordinates follow the benchmark graph orientation:
#   A -> B -> C -> D -> M -> L -> I -> H -> 40 -> A
# with bay nodes placed exactly as in the benchmark static plot.

POSITION_ANCHORS: Dict[str, Tuple[float, float]] = {
    "S1": (1.0, 2.0),
    "S2": (3.0, 2.0),
    "S3": (5.0, 2.0),
    "S4_1": (7.0, 1.5),
    "S4_2": (7.5, 0.5),
    "S5": (6.5, 0.0),
    "S6": (5.0, 0.0),
    "S7": (3.0, 0.0),
    "S8": (1.0, 1.0),
    "WH": (8.0, 1.0),
    "QC_1": (6.0, 4.0),
    "QC_2": (7.0, 5.0),
    "QC_3": (8.0, 6.0),
    "RBTC_1": (4.0, 4.0),
    "RBTC_2": (3.0, 5.0),
    "RBTC_3": (2.0, 6.0),
    "MILL_1": (2.0, 4.0),
    "MILL_2": (1.0, 5.0),
    "MILL_3": (0.0, 6.0),
    "SPEA_1": (0.0, 1.0),
    "UNDEFINED": (-1.0, -0.7),
}

POSITION_LABELS: Dict[str, str] = {
    "S1": "S1", "S2": "S2", "S3": "S3", "S4_1": "S4a", "S4_2": "S4b",
    "S5": "S5", "S6": "S6", "S7": "S7", "S8": "S8",
    "WH": "WH",
    "SPEA_1": "SPEA",
    "MILL_1": "M1", "MILL_2": "M2", "MILL_3": "M3",
    "RBTC_1": "RB1", "RBTC_2": "RB2", "RBTC_3": "RB3",
    "QC_1": "QC1", "QC_2": "QC2", "QC_3": "QC3",
    "UNDEFINED": "???",
}

RING_OFFSETS = [
    (0.00, 0.00),
    (0.13, 0.00),
    (-0.13, 0.00),
    (0.00, 0.13),
    (0.00, -0.13),
    (0.10, 0.10),
    (-0.10, 0.10),
    (0.10, -0.10),
    (-0.10, -0.10),
    (0.18, 0.00),
]

CATEGORY_COLORS = {
    "main": "#2A6F97",
    "warehouse": "#8E6C8A",
    "qc": "#C77D11",
    "rbtc": "#2B9348",
    "mill": "#BC4749",
    "spea": "#7B2CBF",
    "unknown": "#6C757D",
}


def _node_category(position: str) -> str:
    if position in {"S1", "S2", "S3", "S4_1", "S4_2", "S5", "S6", "S7", "S8"}:
        return "main"
    if position == "WH":
        return "warehouse"
    if position.startswith("QC"):
        return "qc"
    if position.startswith("RBTC"):
        return "rbtc"
    if position.startswith("MILL"):
        return "mill"
    if position.startswith("SPEA"):
        return "spea"
    return "unknown"


@dataclass
class PalletState:
    pallet_id: int
    position: str
    timestamp_ms: int


class CsvUpdateTail:
    """Incremental CSV reader that follows appended rows."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._handle = None
        self._reader = None
        self._size = 0

    def _open_if_needed(self) -> None:
        if self._handle is not None:
            return
        self._handle = open(self.file_path, "r", newline="")
        self._reader = csv.DictReader(self._handle)
        self._size = os.path.getsize(self.file_path)

    def read_new(self) -> List[PalletState]:
        if not os.path.exists(self.file_path):
            return []

        self._open_if_needed()

        current_size = os.path.getsize(self.file_path)
        if current_size < self._size:
            self.close()
            self._open_if_needed()
        self._size = current_size

        updates: List[PalletState] = []
        assert self._reader is not None
        for row in self._reader:
            try:
                updates.append(
                    PalletState(
                        pallet_id=int(row["pallet_id"]),
                        position=row["pallet_position"],
                        timestamp_ms=int(row["timestamp"]),
                    )
                )
            except (KeyError, ValueError):
                continue
        return updates

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None
            self._reader = None


def load_updates(file_path: str) -> List[PalletState]:
    updates: List[PalletState] = []
    with open(file_path, "r", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                updates.append(
                    PalletState(
                        pallet_id=int(row["pallet_id"]),
                        position=row["pallet_position"],
                        timestamp_ms=int(row["timestamp"]),
                    )
                )
            except (KeyError, ValueError):
                continue
    return updates


def find_latest_log(search_dir: str) -> Optional[str]:
    pattern = os.path.join(search_dir, "**", "pallet_distance_metric_log_*.csv")
    candidates = glob.glob(pattern, recursive=True)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


# Ring node coordinates (actual graph nodes, not segment midpoints)
_RING_NODES: Dict[str, Tuple[float, float]] = {
    "A": (7.0, 0.0), "B": (6.0, 0.0), "C": (4.0, 0.0), "D": (2.0, 0.0),
    "M": (0.0, 2.0), "L": (2.0, 2.0), "I": (4.0, 2.0), "H": (6.0, 2.0),
    "WH_node": (8.0, 1.0),
    "QC_n1": (6.0, 4.0), "QC_n2": (7.0, 5.0), "QC_n3": (8.0, 6.0),
    "RBTC_n1": (4.0, 4.0), "RBTC_n2": (3.0, 5.0), "RBTC_n3": (2.0, 6.0),
    "MILL_n1": (2.0, 4.0), "MILL_n2": (1.0, 5.0), "MILL_n3": (0.0, 6.0),
    "SPEA_node": (0.0, 1.0),
}

NODE_LABELS: Dict[str, Tuple[float, float, str, str]] = {
    "A": (7.0, -0.34, "A", "center"),
    "B": (6.0, -0.34, "B", "center"),
    "C": (4.0, -0.34, "C", "center"),
    "D": (2.0, -0.34, "D", "center"),
    "M": (0.0, 2.28, "M", "center"),
    "L": (2.0, 2.28, "L", "center"),
    "I": (4.0, 2.28, "I", "center"),
    "H": (6.0, 2.28, "H", "center"),
    "SPEA_node": (-0.25, 1.0, "Z", "right"),
    "MILL_n1": (2.0, 4.28, "P", "center"),
    "RBTC_n1": (4.0, 4.28, "O", "center"),
    "QC_n1": (6.0, 4.28, "N", "center"),
}


def draw_base(ax: plt.Axes) -> None:
    ax.clear()
    ax.set_facecolor("#F0F4F8")

    # Plant border (simple rectangle, avoids bezier/FancyBboxPatch crash)
    border = patches.Rectangle(
        (-0.8, -0.9), 12.0, 7.9,
        linewidth=1.2, edgecolor="#A8B0B7", facecolor="#F8FAFC", zorder=0,
    )
    ax.add_patch(border)

    lane = "#2A6F97"
    thin = "#90B8D4"

    # Benchmark model geometry.
    ax.plot([0, 2, 4, 6], [2, 2, 2, 2], color=lane, linewidth=8, solid_capstyle="round", zorder=1)
    ax.plot([6, 8, 7], [2, 1, 0], color=lane, linewidth=8, solid_capstyle="round", zorder=1)
    ax.plot([7, 6, 4, 2], [0, 0, 0, 0], color=lane, linewidth=8, solid_capstyle="round", zorder=1)
    ax.plot([2, 0], [0, 2], color=lane, linewidth=8, solid_capstyle="round", zorder=1)

    # Bay stems connected back to their belt letters / junctions.
    ax.plot([6, 6, 7, 8], [2, 4, 5, 6], color=CATEGORY_COLORS["qc"], linewidth=4, solid_capstyle="round", zorder=1)
    ax.plot([4, 4, 3, 2], [2, 4, 5, 6], color=CATEGORY_COLORS["rbtc"], linewidth=4, solid_capstyle="round", zorder=1)
    ax.plot([2, 2, 1, 0], [2, 4, 5, 6], color=CATEGORY_COLORS["mill"], linewidth=4, solid_capstyle="round", zorder=1)
    ax.plot([2, 0], [0, 1], color=CATEGORY_COLORS["spea"], linewidth=4, solid_capstyle="round", zorder=1)

    # Direction arrows on conveyor lanes
    _arrow = lambda x1, y1, x2, y2: ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops={"arrowstyle": "-|>", "lw": 1.6, "color": "#F1FAEE"},
        zorder=2,
    )
    # Top rail M -> L -> I -> H
    _arrow(0.6, 2.0, 1.3, 2.0)
    _arrow(2.6, 2.0, 3.3, 2.0)
    _arrow(4.6, 2.0, 5.3, 2.0)
    # H -> 40 -> A
    _arrow(6.4, 1.8, 7.2, 1.3)
    _arrow(7.8, 0.8, 7.2, 0.3)
    # Bottom rail A -> B -> C -> D
    _arrow(6.8, 0.0, 6.2, 0.0)
    _arrow(5.4, 0.0, 4.7, 0.0)
    _arrow(3.4, 0.0, 2.7, 0.0)
    # D -> M
    _arrow(1.6, 0.4, 1.0, 1.0)
    # Bay branches (from belt toward bay endpoints)
    _arrow(6.0, 2.7, 6.0, 3.5)   # QC stem
    _arrow(6.3, 4.3, 6.8, 4.8)   # QC_1 -> QC_2
    _arrow(7.2, 5.3, 7.7, 5.8)   # QC_2 -> QC_3
    _arrow(4.0, 2.7, 4.0, 3.5)   # RBTC stem
    _arrow(3.7, 4.3, 3.2, 4.8)   # RBTC_1 -> RBTC_2
    _arrow(2.8, 5.3, 2.3, 5.8)   # RBTC_2 -> RBTC_3
    _arrow(2.0, 2.7, 2.0, 3.5)   # MILL stem
    _arrow(1.7, 4.3, 1.2, 4.8)   # MILL_1 -> MILL_2
    _arrow(0.8, 5.3, 0.3, 5.8)   # MILL_2 -> MILL_3
    _arrow(1.6, 0.2, 0.8, 0.7)   # SPEA branch

    # Conveyor node letters at segment endpoints/junctions
    for node_key, (x, y, label, align) in NODE_LABELS.items():
        node_x, node_y = _RING_NODES[node_key]
        ax.scatter([node_x], [node_y], s=26, color=thin, edgecolors="white", linewidths=0.7, zorder=3)
        ax.text(x, y, label, fontsize=8, color="#243B53", ha=align, va="center", fontweight="bold", zorder=4)

    # Bay node markers and labels
    for pos, (x, y) in POSITION_ANCHORS.items():
        if pos in ("UNDEFINED", "WH"):
            continue  # WH drawn separately below
        cat = _node_category(pos)
        ax.scatter([x], [y], s=60, color=CATEGORY_COLORS[cat], edgecolors="white",
                   linewidths=0.8, zorder=3)
        lbl = POSITION_LABELS.get(pos, pos)
        # Place label below for bottom-rail positions, above for everything else
        dy = -0.28 if y <= 0.2 else 0.26
        ax.text(x, y + dy, lbl, fontsize=7, color="#1B263B", ha="center", zorder=4)

    # WH inline-station node
    ax.scatter([8.0], [1.0], s=90, color=CATEGORY_COLORS["warehouse"],
               edgecolors="white", linewidths=1.0, zorder=3)
    ax.text(8.2, 1.0, "WH", fontsize=7, color="#1B263B", ha="left", va="center", zorder=4)

    # Zone header labels
    ax.text(-0.25, 1.35, "SPEA", fontsize=8, color=CATEGORY_COLORS["spea"], fontweight="bold", ha="right")
    ax.text(2.4, 6.55, "MILL", fontsize=8, color=CATEGORY_COLORS["mill"], fontweight="bold", ha="center")
    ax.text(3.6, 6.55, "RBTC", fontsize=8, color=CATEGORY_COLORS["rbtc"], fontweight="bold", ha="center")
    ax.text(7.6, 6.55, "QC", fontsize=8, color=CATEGORY_COLORS["qc"], fontweight="bold", ha="center")
    ax.text(8.25, 0.45, "Load/\nUnload", fontsize=6.5, color=CATEGORY_COLORS["warehouse"],
            fontweight="bold", ha="left", va="center")

    ax.set_xlim(-1.2, 9.4)
    ax.set_ylim(-1.1, 7.0)
    ax.axis("off")


def _target_xy(position: str, pallet_id: int) -> Tuple[float, float]:
    anchor = POSITION_ANCHORS.get(position, POSITION_ANCHORS["UNDEFINED"])
    dx, dy = RING_OFFSETS[(pallet_id - 1) % len(RING_OFFSETS)]
    return (anchor[0] + dx, anchor[1] + dy)


def _lerp(a: Tuple[float, float], b: Tuple[float, float], t: float) -> Tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def place_pallets(ax: plt.Axes, pallet_xy: Dict[int, Tuple[float, float]], max_pallets: int) -> None:
    cmap = plt.get_cmap("tab10")
    for pallet_id in range(1, max_pallets + 1):
        x, y = pallet_xy[pallet_id]
        color = cmap((pallet_id - 1) % 10)
        ax.scatter([x], [y], s=300, color=color, edgecolors="white", linewidths=1.5, zorder=5)
        ax.text(x, y, str(pallet_id), ha="center", va="center", color="white", fontsize=8, zorder=6, fontweight="bold")


def _draw_frame(
    ax: plt.Axes,
    pallet_xy: Dict[int, Tuple[float, float]],
    pallet_states: Dict[int, PalletState],
    max_pallets: int,
    title: str,
) -> None:
    draw_base(ax)
    place_pallets(ax, pallet_xy, max_pallets)
    latest_ts = max((state.timestamp_ms for state in pallet_states.values()), default=0)
    active_nodes = len({state.position for state in pallet_states.values() if state.position != "UNDEFINED"})
    ax.set_title(
        f"{title} | t={latest_ts} ms | active_nodes={active_nodes}",
        fontsize=12,
        fontweight="bold",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Live conveyor pallet movement viewer")
    parser.add_argument("--file", type=str, default="", help="Explicit CSV file to follow")
    parser.add_argument("--search-dir", type=str, default=".", help="Directory used to auto-find newest CSV")
    parser.add_argument("--refresh-ms", type=int, default=200, help="Refresh period in milliseconds")
    parser.add_argument("--max-pallets", type=int, default=10, help="Expected pallet count for initial state")
    parser.add_argument("--speed", type=float, default=1.0, help="Replay speed multiplier for --file mode")
    parser.add_argument("--loop", action="store_true", help="Loop replay when using --file mode")
    args = parser.parse_args()

    pallet_states: Dict[int, PalletState] = {
        i: PalletState(i, "UNDEFINED", 0) for i in range(1, args.max_pallets + 1)
    }
    pallet_xy: Dict[int, Tuple[float, float]] = {
        i: _target_xy("UNDEFINED", i) for i in range(1, args.max_pallets + 1)
    }
    anim_from: Dict[int, Tuple[float, float]] = dict(pallet_xy)
    anim_to: Dict[int, Tuple[float, float]] = dict(pallet_xy)
    anim_start: Dict[int, float] = {i: time.time() for i in range(1, args.max_pallets + 1)}
    anim_duration_s = max(0.15, min(0.7, args.refresh_ms / 1000.0 * 1.6))

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("white")

    if args.file:
        replay_file = args.file
        updates = load_updates(replay_file)
        if not updates:
            raise SystemExit(f"No valid pallet updates found in {replay_file}")

        replay_start_ts = updates[0].timestamp_ms
        replay_wall_start = time.time()
        next_update_idx = 0

        def _tick_replay(_frame_idx: int) -> None:
            nonlocal replay_wall_start, next_update_idx

            now = time.time()
            elapsed_ms = (now - replay_wall_start) * 1000.0 * max(args.speed, 0.01)
            replay_ts = replay_start_ts + elapsed_ms

            while next_update_idx < len(updates) and updates[next_update_idx].timestamp_ms <= replay_ts:
                update = updates[next_update_idx]
                pallet_states[update.pallet_id] = update
                pid = update.pallet_id
                anim_from[pid] = pallet_xy[pid]
                anim_to[pid] = _target_xy(update.position, pid)
                anim_start[pid] = now
                next_update_idx += 1

            if next_update_idx >= len(updates) and args.loop:
                if all(pallet_xy[pid] == anim_to[pid] for pid in range(1, args.max_pallets + 1)):
                    for pid in range(1, args.max_pallets + 1):
                        pallet_states[pid] = PalletState(pid, "UNDEFINED", 0)
                        pallet_xy[pid] = _target_xy("UNDEFINED", pid)
                        anim_from[pid] = pallet_xy[pid]
                        anim_to[pid] = pallet_xy[pid]
                        anim_start[pid] = now
                    replay_wall_start = now
                    next_update_idx = 0

            for pid in range(1, args.max_pallets + 1):
                dt = now - anim_start[pid]
                if dt <= 0:
                    pallet_xy[pid] = anim_from[pid]
                    continue
                t = min(1.0, dt / anim_duration_s)
                t = t * t * (3.0 - 2.0 * t)
                pallet_xy[pid] = _lerp(anim_from[pid], anim_to[pid], t)

            file_label = os.path.basename(replay_file)
            _draw_frame(
                ax,
                pallet_xy,
                pallet_states,
                args.max_pallets,
                f"ICE Conveyor Replay | x{args.speed:g} | file={file_label}",
            )

        anim = FuncAnimation(fig, _tick_replay, interval=max(50, args.refresh_ms), cache_frame_data=False)
        plt.tight_layout()
        plt.show()
        del anim
        return

    log_file: Optional[str] = find_latest_log(args.search_dir)
    if log_file is None:
        print(
            "No pallet log file found yet. Waiting for a new "
            "pallet_distance_metric_log_*.csv ..."
        )

    tail: Optional[CsvUpdateTail] = CsvUpdateTail(log_file) if log_file else None

    no_update_cycles = 0

    def _tick(_frame_idx: int) -> None:
        nonlocal log_file, tail, no_update_cycles

        # If no file selected yet, keep polling until one appears.
        if log_file is None:
            latest = find_latest_log(args.search_dir)
            if latest:
                log_file = latest
                tail = CsvUpdateTail(log_file)

        if log_file and tail and not os.path.exists(log_file):
            latest = find_latest_log(args.search_dir)
            if latest and latest != log_file:
                tail.close()
                log_file = latest
                tail = CsvUpdateTail(log_file)

        updates = tail.read_new() if tail else []
        now = time.time()
        if updates:
            no_update_cycles = 0
            for update in updates:
                pallet_states[update.pallet_id] = update
                pid = update.pallet_id
                anim_from[pid] = pallet_xy[pid]
                anim_to[pid] = _target_xy(update.position, pid)
                anim_start[pid] = now
        else:
            no_update_cycles += 1
            if no_update_cycles % max(1, int(1200 / args.refresh_ms)) == 0:
                latest = find_latest_log(args.search_dir)
                if latest and latest != log_file:
                    if tail:
                        tail.close()
                    log_file = latest
                    tail = CsvUpdateTail(log_file)

        for pid in range(1, args.max_pallets + 1):
            dt = now - anim_start[pid]
            if dt <= 0:
                pallet_xy[pid] = anim_from[pid]
                continue
            t = min(1.0, dt / anim_duration_s)
            # smoothstep easing
            t = t * t * (3.0 - 2.0 * t)
            pallet_xy[pid] = _lerp(anim_from[pid], anim_to[pid], t)

        file_label = os.path.basename(log_file) if log_file else "waiting for log file"
        _draw_frame(
            ax,
            pallet_xy,
            pallet_states,
            args.max_pallets,
            f"ICE Conveyor Live View | file={file_label}",
        )

    anim = FuncAnimation(fig, _tick, interval=max(50, args.refresh_ms), cache_frame_data=False)
    plt.tight_layout()
    plt.show()
    if tail:
        tail.close()
    del anim


if __name__ == "__main__":
    main()
