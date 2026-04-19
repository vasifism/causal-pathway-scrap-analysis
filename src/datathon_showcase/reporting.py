from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PATHWAYS, TARGET


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def top_line(df: pd.DataFrame, column: str) -> str:
    if df.empty or column not in df.columns:
        return "not available"
    return str(df.iloc[0][column])


def render_table(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)


def build_markdown_summary(
    source_df: pd.DataFrame,
    defect_burden: pd.DataFrame,
    pathway_scores: pd.DataFrame,
    intervention_ranking: pd.DataFrame,
) -> str:
    lines: list[str] = []

    lines.append("# Causal Pathway Showcase Summary")
    lines.append("")
    lines.append("## Dataset snapshot")
    lines.append("")
    lines.append(f"- Rows: **{len(source_df):,}**")
    lines.append(f"- Columns: **{len(source_df.columns):,}**")
    lines.append(f"- Target KPI: **{TARGET}**")
    lines.append("")

    if TARGET in source_df.columns:
        target = pd.to_numeric(source_df[TARGET], errors="coerce")
        lines.append(f"- Mean scrap rate: **{target.mean():.3f}**")
        lines.append(f"- Median scrap rate: **{target.median():.3f}**")
        lines.append(f"- Standard deviation: **{target.std():.3f}**")
        lines.append("")

    lines.append("## Method")
    lines.append("")
    lines.append(
        "This showcase implements a causal pathway-based intervention workflow. "
        "A predefined DAG is used to organize the process into defect-generating mechanisms, "
        "controllable levers are isolated inside each pathway, and the data is used to estimate "
        "directional intervention relevance through quartile-based comparisons."
    )
    lines.append("")

    lines.append("## Pathways evaluated")
    lines.append("")
    for name, info in PATHWAYS.items():
        lines.append(f"- **{name.title()}**: `{info['description']}`")
    lines.append("")

    lines.append("## Defect burden")
    lines.append("")
    if defect_burden.empty:
        lines.append("Defect burden could not be computed from the available columns.")
    else:
        lines.append(render_table(defect_burden))
        lines.append("")
        lines.append(
            f"Top defect by aggregate burden: **{top_line(defect_burden, defect_burden.columns[0])}**."
        )
    lines.append("")

    lines.append("## Top intervention candidates")
    lines.append("")
    if intervention_ranking.empty:
        lines.append("No actionable intervention candidates were identified.")
    else:
        top = intervention_ranking.head(5).copy()
        display_cols = [
            "rank",
            "pathway",
            "variable",
            "recommended_direction",
            "direction_hint",
            "effect_gap",
            "tradeoff_flag",
        ]
        lines.append(render_table(top[display_cols]))
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    if intervention_ranking.empty:
        lines.append(
            "The dataset did not contain enough supported actionable variables to generate a ranked story."
        )
    else:
        winner = intervention_ranking.iloc[0]
        lines.append(
            f"The strongest showcase intervention in this run is **{winner['variable']}** "
            f"inside the **{winner['pathway']}** pathway. "
            f"The estimated direction is **{winner['recommended_direction']}**, "
            f"and the variable carries the operational note: *{winner['interpretation_note']}*."
        )
    lines.append("")

    lines.append("## Why this repository is useful in a datathon")
    lines.append("")
    lines.append(
        "The value of this project is not only in the tables it produces, but in the structure it demonstrates: "
        "starting from a causal story, translating that story into ranked interventions, and presenting a result "
        "that is operationally interpretable."
    )
    lines.append("")

    return "\n".join(lines)


def export_outputs(
    out_dir: Path,
    defect_burden: pd.DataFrame,
    pathway_scores: pd.DataFrame,
    intervention_ranking: pd.DataFrame,
    summary_markdown: str,
) -> None:
    ensure_output_dir(out_dir)

    if not defect_burden.empty:
        defect_burden.to_csv(out_dir / "defect_burden.csv", index=False)

    if not pathway_scores.empty:
        pathway_scores.to_csv(out_dir / "pathway_scores.csv", index=False)

    if not intervention_ranking.empty:
        intervention_ranking.to_csv(out_dir / "intervention_ranking.csv", index=False)

    (out_dir / "showcase_summary.md").write_text(summary_markdown, encoding="utf-8")
