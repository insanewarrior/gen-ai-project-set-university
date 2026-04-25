import json
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "data" / "exercises.json"

_VALID_SPORT_TYPES = {"grip", "armwrestling", "powerlifting", "general"}


def _load_exercises() -> dict:
    with open(_DATA_PATH, "r") as f:
        return json.load(f)


# Loaded at import time — once per Lambda cold start / uvicorn startup
_EXERCISES: dict = _load_exercises()


def get_exercises(sport_type: str | None = None) -> dict:
    if sport_type is None:
        return _EXERCISES
    if sport_type not in _VALID_SPORT_TYPES:
        raise ValueError(
            f"Unknown sportType: {sport_type}. Valid values: {', '.join(sorted(_VALID_SPORT_TYPES))}"
        )
    return {sport_type: _EXERCISES.get(sport_type, [])}
