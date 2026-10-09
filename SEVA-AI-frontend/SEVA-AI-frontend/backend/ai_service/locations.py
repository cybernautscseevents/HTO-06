import json
from functools import lru_cache
from pathlib import Path


LOCATION_FILE = Path(__file__).resolve().parent.parent / "location_data.json"


@lru_cache(maxsize=1)
def get_locations():
    with LOCATION_FILE.open(encoding="utf-8") as location_file:
        return json.load(location_file)


def canonical_state(value):
    normalized = str(value or "").strip().casefold()
    return next(
        (item["state"] for item in get_locations() if item["state"].casefold() == normalized),
        None,
    )


def canonical_district(state, value):
    selected_state = canonical_state(state)
    if not selected_state:
        return None
    normalized = str(value or "").strip().casefold()
    state_data = next(item for item in get_locations() if item["state"] == selected_state)
    return next(
        (district for district in state_data["districts"] if district.casefold() == normalized),
        None,
    )
