from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


TARGET = "scrap_rate_pct"
DEFECT = "defect_type"
ENERGY = "energy_kwh_interval"
CYCLE = "cycle_time_s"


@dataclass(frozen=True)
class LeverSpec:
    variable: str
    actionable: bool
    note: str


PATHWAYS = {
    "moisture": {
        "description": (
            "ambient_humidity_pct -> dryer_dewpoint_c -> resin_moisture_pct "
            "-> splay_moisture -> scrap_rate_pct"
        ),
        "focus_defect": "splay_moisture",
        "levers": [
            LeverSpec(
                variable="dryer_dewpoint_c",
                actionable=True,
                note="Primary upstream operational lever in the moisture chain.",
            ),
            LeverSpec(
                variable="resin_moisture_pct",
                actionable=True,
                note="Mechanism variable close to defect formation.",
            ),
            LeverSpec(
                variable="ambient_humidity_pct",
                actionable=False,
                note="Context variable that explains regime dependence.",
            ),
        ],
    },
    "warpage": {
        "description": (
            "mold_temperature_c + cooling_time_s -> warpage -> scrap_rate_pct"
        ),
        "focus_defect": "warpage",
        "levers": [
            LeverSpec(
                variable="mold_temperature_c",
                actionable=True,
                note="Primary thermal lever for warpage risk.",
            ),
            LeverSpec(
                variable="cooling_time_s",
                actionable=True,
                note="Important but should be interpreted contextually.",
            ),
        ],
    },
    "flash": {
        "description": (
            "tool_wear_index + injection_pressure_bar + clamp_force_kn "
            "-> flash -> scrap_rate_pct"
        ),
        "focus_defect": "flash",
        "levers": [
            LeverSpec(
                variable="injection_pressure_bar",
                actionable=True,
                note="Most direct process lever inside the flash pathway.",
            ),
            LeverSpec(
                variable="tool_wear_index",
                actionable=False,
                note="Condition variable; explains when flash pathway becomes stronger.",
            ),
            LeverSpec(
                variable="clamp_force_kn",
                actionable=False,
                note="Structural machine context rather than a headline intervention.",
            ),
        ],
    },
    "stability": {
        "description": (
            "maintenance_days_since_last -> calibration_drift_index "
            "-> instability -> defects -> scrap_rate_pct"
        ),
        "focus_defect": None,
        "levers": [
            LeverSpec(
                variable="maintenance_days_since_last",
                actionable=True,
                note="Planning-level intervention lever.",
            ),
            LeverSpec(
                variable="calibration_drift_index",
                actionable=True,
                note="Operational health indicator linked to upstream maintenance quality.",
            ),
        ],
    },
}


DIRECTION_HINTS = {
    "dryer_dewpoint_c": "move colder / lower",
    "resin_moisture_pct": "move lower",
    "ambient_humidity_pct": "move lower when feasible",
    "mold_temperature_c": "move lower in warpage-prone contexts",
    "cooling_time_s": "tune contextually",
    "injection_pressure_bar": "move lower in flash-prone contexts",
    "tool_wear_index": "reduce through tooling maintenance",
    "clamp_force_kn": "machine capability constraint",
    "maintenance_days_since_last": "shorten the interval",
    "calibration_drift_index": "move lower",
}


def get_direction_hint(variable: str) -> str:
    return DIRECTION_HINTS.get(variable, "review direction from observed effect")


def focus_defect_label(value: Optional[str]) -> str:
    return value if value is not None else "multiple"
