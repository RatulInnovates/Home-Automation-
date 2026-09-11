from pathlib import Path
import json
from datetime import datetime, timezone

STATE_FILE = Path(__file__).resolve().parent / "smart_door_state.json"


def _default_state():
    return {
        "last_motion_at": None,
        "last_person": None,
        "gas_alarm": False,
        "fan_on": False,
        "light_on": False,
        "recent_activity": [],
    }


def _timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_state():
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps(_default_state(), indent=2), encoding="utf-8")

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = _default_state()

    default = _default_state()
    for key, value in default.items():
        if key not in data:
            data[key] = value

    if not isinstance(data.get("recent_activity", []), list):
        data["recent_activity"] = []

    return data


def write_state(data):
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_activity(kind, message, **fields):
    state = read_state()

    event = {
        "time": _timestamp(),
        "kind": kind,
        "message": message,
    }
    event.update(fields)

    state["recent_activity"] = [event] + state.get("recent_activity", [])[:9]

    if kind == "motion":
        state["last_motion_at"] = event["time"]
    if kind == "entry" and fields.get("person"):
        state["last_person"] = fields["person"]

    write_state(state)


def set_output(name, value):
    state = read_state()
    state[f"{name}_on"] = bool(value)
    write_state(state)


def set_gas_alarm(value):
    state = read_state()
    state["gas_alarm"] = bool(value)
    write_state(state)
