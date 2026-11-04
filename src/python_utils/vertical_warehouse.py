
import json
from enum import Enum

MIN_W = 2.960  # empty tray weight [kg]
MAX_W = 4.960  # max loaded tray weight [kg]


class Tray:
    def __init__(self, tray_id: int, weight: float = MIN_W):
        if not MIN_W <= weight <= MAX_W:
            raise ValueError(f"Tray weight {weight} outside [{MIN_W}, {MAX_W}] kg")
        self.tray_id = tray_id
        self.weight = weight

    @property
    def is_full(self) -> bool:
        return self.weight > MIN_W + 0.01


class Slot:
    def __init__(self, slot_id: str, x: float, y: float, slot_type: str):
        self.slot_id = slot_id
        self.x = x
        self.y = y
        self.slot_type = slot_type  # "storage" | "queue" | "bay"
        self.tray: Tray | None = None


class Platform:
    """Shuttle moving one step per tick. Speeds are calibration knobs."""

    def __init__(self, dt: float = 0.05, speed_y: float = 0.20, speed_x: float = 0.15):
        self.dt = dt
        self.speed_y = speed_y
        self.speed_x = speed_x
        self.curr_x = 0.0
        self.curr_y = 0.0
        self.held_tray: Tray | None = None

    @staticmethod
    def _step(curr: float, target: float, step: float) -> float:
        if abs(target - curr) <= step:
            return target  # snap: the planner compares positions with ==
        return curr + step if target > curr else curr - step

    def move_y(self, target: float):
        self.curr_y = self._step(self.curr_y, target, self.speed_y * self.dt)

    def move_x(self, target: float):
        self.curr_x = self._step(self.curr_x, target, self.speed_x * self.dt)

    def pick(self, slot: Slot) -> bool:
        if self.held_tray is not None or slot.tray is None:
            return False
        self.held_tray, slot.tray = slot.tray, None
        return True

    def place(self, slot: Slot) -> bool:
        if self.held_tray is None or slot.tray is not None:
            return False
        slot.tray, self.held_tray = self.held_tray, None
        return True


class VerticalWarehouse:
    """20 rows x 2 columns. Right column: rows 0-2 queue, row 3 bay, rest storage."""

    X_LEFT = -0.7
    X_RIGHT = 0.7
    SLOT_HEIGHT = 0.16725
    NUM_ROWS = 20
    INITIAL_TRAYS = (  # (tray_id, slot_id, weight)
        (1, "storage_L_0", 3.5),
        (2, "storage_L_5", MIN_W),
        (3, "storage_R_7", MIN_W),
        (4, "storage_L_10", 3.0),
        (5, "storage_R_15", 3.1),
        (6, "queue_0", MIN_W),
        (8, "storage_L_9", 3.5),
    )

    def __init__(self, dt: float = 0.05):
        self.platform = Platform(dt)
        self.slots: list[Slot] = []
        for i in range(self.NUM_ROWS):
            y = i * self.SLOT_HEIGHT
            self.slots.append(Slot(f"storage_L_{i}", self.X_LEFT, y, "storage"))
            if i < 3:
                self.slots.append(Slot(f"queue_{i}", self.X_RIGHT, y, "queue"))
            elif i == 3:
                self.slots.append(Slot("in_view", self.X_RIGHT, y, "bay"))
            else:
                self.slots.append(Slot(f"storage_R_{i}", self.X_RIGHT, y, "storage"))
        self._by_id = {s.slot_id: s for s in self.slots}
        self.bay = self._by_id["in_view"]
        for tray_id, slot_id, weight in self.INITIAL_TRAYS:
            self._by_id[slot_id].tray = Tray(tray_id, weight)

    def slot(self, slot_id: str) -> Slot | None:
        return self._by_id.get(slot_id)

    def has_tray(self, tray_id: int) -> bool:
        return any(s.tray and s.tray.tray_id == tray_id for s in self.slots)

    def first_occupied_queue_slot(self) -> Slot | None:
        return next((s for s in self.slots if s.slot_type == "queue" and s.tray), None)

    def queue_occupancy(self) -> int:
        return sum(1 for s in self.slots if s.slot_type == "queue" and s.tray)

    @property
    def tray_in_bay(self) -> int:
        return self.bay.tray.tray_id if self.bay.tray else 0


FETCH, FETCH_ANY_EMPTY, SEARCH_TARGET, DELIVER, IDLE = (
    "FETCH", "FETCH_ANY_EMPTY", "SEARCH_TARGET", "DELIVER", "IDLE")
WAIT = ("wait",)


def _approach(cy: float, cx: float, slot: Slot, final: tuple) -> tuple:
    """Retract X to 0, travel on Y, extend X, then run `final` (pick/place)."""
    if cy != slot.y:
        return ("update_x", 0.0) if cx != 0.0 else ("update_y", slot.y)
    if cx != slot.x:
        return ("update_x", slot.x)
    return final


def next_action(slots, cy, cx, holding, phase, cmd, target_id=0, target_type="", locked_id=""):
    """Return the next atomic action: ("update_y", y) | ("update_x", x) |
    ("pick",) | ("place",) | ("lock", slot_id) | ("wait",)."""
    if cmd == SEARCH_TARGET and holding:
        free = next((s for s in slots if s.slot_type == target_type and s.tray is None), None)
        return ("lock", free.slot_id) if free else WAIT

    if cmd in (FETCH, FETCH_ANY_EMPTY) and not holding and phase == "fetch":
        if cmd == FETCH:
            src = next((s for s in slots if s.tray and s.tray.tray_id == target_id), None)
        else:
            src = next((s for s in slots if s.tray and not s.tray.is_full), None)
        return _approach(cy, cx, src, ("pick",)) if src else WAIT

    if cmd == DELIVER and holding and phase == "deliver" and locked_id:
        dst = next((s for s in slots if s.slot_id == locked_id), None)
        if dst and dst.tray is None and dst.slot_type == target_type:
            return _approach(cy, cx, dst, ("place",))

    return WAIT


# --- Mission controller -------------------------------------------------------

class MissionState(Enum):
    IDLE = "idle"
    FETCH = "fetch"
    DELIVER = "deliver"


class WarehouseController:
    """Runs one mission at a time (FETCH then DELIVER) with one planner step per tick.
    A request that arrives while a mission is running is rejected, not queued."""

    def __init__(self, warehouse: VerticalWarehouse):
        self.wh = warehouse
        self.set_idle()

    def set_idle(self):
        self.state = MissionState.IDLE
        self.source_slot: Slot | None = None
        self.dest_slot: Slot | None = None
        self.dest_type: str | None = None
        self.target_tray_id: int | None = None
        self.locked_target_id: str | None = None

    @property
    def is_busy(self) -> bool:
        return self.state != MissionState.IDLE or self.wh.platform.held_tray is not None

    def _start(self, src=None, dst=None, dst_type=None, tray_id=None) -> bool:
        self.set_idle()
        self.source_slot, self.dest_slot, self.dest_type, self.target_tray_id = src, dst, dst_type, tray_id
        self.state = MissionState.FETCH
        return True

    # Missions -----------------------------------------------------------------
    def extract(self, tray_id: int = 0) -> bool:
        """Bring tray `tray_id` to the bay. With tray_id == 0, take the first occupied queue slot."""
        if self.is_busy or self.wh.bay.tray is not None:
            return False
        if tray_id:
            return self.wh.has_tray(tray_id) and self._start(dst=self.wh.bay, tray_id=tray_id)
        src = self.wh.first_occupied_queue_slot()
        return src is not None and self._start(src=src, dst=self.wh.bay)

    def sendback(self) -> bool:
        """Return the tray in the bay to any free storage slot."""
        if self.is_busy or self.wh.bay.tray is None:
            return False
        return self._start(src=self.wh.bay, dst_type="storage")

    def fetch_any_empty(self) -> bool:
        if self.is_busy or self.wh.bay.tray is not None:
            return False
        return self._start(dst=self.wh.bay)

    def enqueue(self, tray_id: int) -> bool:
        """Move tray `tray_id` into a free queue slot."""
        if self.is_busy or not self.wh.has_tray(tray_id):
            return False
        return self._start(dst_type="queue", tray_id=tray_id)

    def clear_bay(self) -> bool:
        """The operator takes the tray out of the bay, so it leaves the warehouse."""
        if self.is_busy:
            return False
        self.wh.bay.tray = None
        return True

    def request_info_bay(self) -> str:
        n = self.wh.tray_in_bay
        return json.dumps({"status": "Occupied" if n else "Empty", "tray_id": n})

    # Tick ---------------------------------------------------------------------
    def _plan(self) -> tuple:
        plat = self.wh.platform
        if self.target_tray_id is not None:
            tid = self.target_tray_id
        elif self.source_slot and self.source_slot.tray:
            tid = self.source_slot.tray.tray_id
        else:
            tid = 0

        if self.dest_slot:
            ttype = self.dest_slot.slot_type
        elif self.locked_target_id:
            ttype = self.wh.slot(self.locked_target_id).slot_type
        else:
            ttype = self.dest_type or ""

        locked = self.locked_target_id or ""
        if self.state == MissionState.FETCH:
            cmd = FETCH if tid else FETCH_ANY_EMPTY
            phase = "fetch"
        elif self.state == MissionState.DELIVER:
            phase = "deliver"
            if self.dest_slot:
                cmd, locked = DELIVER, self.dest_slot.slot_id
            else:
                cmd = DELIVER if self.locked_target_id else SEARCH_TARGET
        else:
            cmd, phase = IDLE, "fetch"

        return next_action(self.wh.slots, plat.curr_y, plat.curr_x, plat.held_tray is not None,
                           phase, cmd, tid, ttype, locked)

    def tick(self) -> bool:
        """Run one step. Returns False on idle or on a failed action (the mission is aborted)."""
        if not self.is_busy:
            return False
        plat = self.wh.platform
        action = self._plan()
        kind = action[0]

        if kind == "lock":
            self.locked_target_id = action[1]
        elif kind == "update_y":
            plat.move_y(action[1])
        elif kind == "update_x":
            plat.move_x(action[1])
        elif kind == "pick":
            src = self.source_slot or next(
                s for s in self.wh.slots if s.x == plat.curr_x and s.y == plat.curr_y)
            if not plat.pick(src):
                self.set_idle()
                return False
            self.source_slot = src
            self.state = MissionState.DELIVER
        elif kind == "place":
            dst = self.dest_slot or self.wh.slot(self.locked_target_id)
            if not plat.place(dst):
                self.set_idle()
                return False
            self.set_idle()
        return True
