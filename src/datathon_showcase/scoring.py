from __future__ import annotations

from typing import Any

import pandas as pd

from .config import CYCLE, DEFECT, ENERGY, PATHWAYS, TARGET, focus_defect_label, get_direction_hint


def is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def quantile_effect(df: pd.DataFrame, variable: str, target: str = TARGET) -> dict[str, Any] | None:
    if variable not in df.columns or target not in df.columns:
        return None

    x = safe_numeric(df[variable])
    y = safe_numeric(df[target])

    valid = ~(x.isna() | y.isna())
    if valid.sum() < 30:
        return None

    x = x[valid]
    y = y[valid]

    q25 = float(x.quantile(0.25))
    q50 = float(x.quantile(0.50))
    q75 = float(x.quantile(0.75))

    low_mask = x <= q25
    high_mask = x >= q75

    low_scrap = float(y[low_mask].mean())
    high_scrap = float(y[high_mask].mean())
    corr = float(x.corr(y))
    gap = abs(high_scrap - low_scrap)

    if variable == "cooling_time_s":
        recommended_direction = "contextual"
    else:
        recommended_direction = "decrease" if low_scrap < high_scrap else "increase"
    
    return {
        "variable": variable,
        "rows_used": int(valid.sum()),
        "q25": q25,
        "q50": q50,
        "q75": q75,
        "low_scrap": low_scrap,
        "high_scrap": high_scrap,
        "corr": corr,
        "effect_gap": gap,
        "recommended_direction": recommended_direction,
    }


def estimate_tradeoffs(df: pd.DataFrame, variable: str, q25: float, q75: float) -> tuple[float | None, float | None]:
    x = safe_numeric(df[variable])

    cycle_delta = None
    energy_delta = None

    if CYCLE in df.columns:
        cycle = safe_numeric(df[CYCLE])
        cycle_delta = float(cycle[x >= q75].mean() - cycle[x <= q25].mean())

    if ENERGY in df.columns:
        energy = safe_numeric(df[ENERGY])
        energy_delta = float(energy[x >= q75].mean() - energy[x <= q25].mean())

    return cycle_delta, energy_delta


def defect_subset(df: pd.DataFrame, focus_defect: str | None) -> pd.DataFrame:
    if focus_defect is None:
        return df.copy()

    if DEFECT not in df.columns:
        return df.copy()

    subset = df[df[DEFECT] == focus_defect].copy()
    if len(subset) < 30:
        return df.copy()
    return subset


def build_pathway_scores(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for pathway_name, pathway in PATHWAYS.items():
        sub = defect_subset(df, pathway["focus_defect"])

        for lever in pathway["levers"]:
            if lever.variable not in sub.columns:
                continue
            if not is_numeric(sub[lever.variable]):
                continue

            effect = quantile_effect(sub, lever.variable)
            if effect is None:
                continue

            cycle_delta, energy_delta = estimate_tradeoffs(
                sub,
                lever.variable,
                effect["q25"],
                effect["q75"],
            )

            rows.append(
                {
                    "pathway": pathway_name,
                    "path_description": pathway["description"],
                    "focus_defect": focus_defect_label(pathway["focus_defect"]),
                    "variable": lever.variable,
                    "actionable": lever.actionable,
                    "interpretation_note": lever.note,
                    "direction_hint": get_direction_hint(lever.variable),
                    "rows_used": effect["rows_used"],
                    "corr": effect["corr"],
                    "q25": effect["q25"],
                    "q50": effect["q50"],
                    "q75": effect["q75"],
                    "low_scrap": effect["low_scrap"],
                    "high_scrap": effect["high_scrap"],
                    "effect_gap": effect["effect_gap"],
                    "recommended_direction": effect["recommended_direction"],
                    "cycle_delta_high_minus_low": cycle_delta,
                    "energy_delta_high_minus_low": energy_delta,
                }
            )

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values(
            by=["actionable", "effect_gap"],
            ascending=[False, False],
        ).reset_index(drop=True)

    return result


def build_intervention_ranking(pathway_scores: pd.DataFrame) -> pd.DataFrame:
    if pathway_scores.empty:
        return pathway_scores.copy()

    ranked = pathway_scores[pathway_scores["actionable"]].copy()

    if ranked.empty:
        return ranked

    ranked["tradeoff_flag"] = ranked.apply(make_tradeoff_flag, axis=1)
    ranked["showcase_priority"] = ranked.apply(priority_score, axis=1)

    ranked = ranked.sort_values(
        by=["showcase_priority", "effect_gap"],
        ascending=[False, False],
    ).reset_index(drop=True)

    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    return ranked


def make_tradeoff_flag(row: pd.Series) -> str:
    flags: list[str] = []

    cycle_delta = row.get("cycle_delta_high_minus_low")
    energy_delta = row.get("energy_delta_high_minus_low")

    if cycle_delta is not None and not pd.isna(cycle_delta) and abs(float(cycle_delta)) > 1.0:
        flags.append("cycle-time sensitivity")

    if energy_delta is not None and not pd.isna(energy_delta) and abs(float(energy_delta)) > 0.5:
        flags.append("energy sensitivity")

    if row["variable"] == "cooling_time_s":
        flags.append("context-dependent tuning")

    if row["variable"] == "injection_pressure_bar":
        flags.append("watch fill-quality risk")

    if row["variable"] == "maintenance_days_since_last":
        flags.append("planning-level action")

    return ", ".join(flags) if flags else "no major flag"


def priority_score(row: pd.Series) -> float:
    score = float(row["effect_gap"])

    if row["variable"] == "dryer_dewpoint_c":
        score += 2.0
    elif row["variable"] == "mold_temperature_c":
        score += 1.5
    elif row["variable"] == "injection_pressure_bar":
        score += 1.2
    elif row["variable"] == "maintenance_days_since_last":
        score += 0.5

    if row["actionable"]:
        score += 1.0

    return score


def build_defect_burden(df: pd.DataFrame) -> pd.DataFrame:
    if DEFECT not in df.columns or TARGET not in df.columns:
        return pd.DataFrame()

    agg_dict: dict[str, tuple[str, str]] = {
        "intervals": (TARGET, "size"),
        "mean_scrap": (TARGET, "mean"),
        "median_scrap": (TARGET, "median"),
    }

    if "scrap_count" in df.columns:
        agg_dict["total_scrap_count"] = ("scrap_count", "sum")
    else:
        agg_dict["total_scrap_count"] = (TARGET, "sum")

    out = (
        df.groupby(DEFECT, dropna=False)
        .agg(**agg_dict)
        .sort_values(by=["total_scrap_count", "mean_scrap"], ascending=[False, False])
        .reset_index()
    )
    return out
