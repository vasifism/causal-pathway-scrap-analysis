from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .reporting import build_markdown_summary, export_outputs
from .scoring import build_defect_burden, build_intervention_ranking, build_pathway_scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a causal pathway showcase pipeline on an injection molding CSV dataset."
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--out",
        default="outputs",
        help="Directory for exported results.",
    )
    return parser.parse_args()


def run(csv_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(csv_path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    defect_burden = build_defect_burden(df)
    pathway_scores = build_pathway_scores(df)
    intervention_ranking = build_intervention_ranking(pathway_scores)

    summary_markdown = build_markdown_summary(
        source_df=df,
        defect_burden=defect_burden,
        pathway_scores=pathway_scores,
        intervention_ranking=intervention_ranking,
    )

    export_outputs(
        out_dir=out_dir,
        defect_burden=defect_burden,
        pathway_scores=pathway_scores,
        intervention_ranking=intervention_ranking,
        summary_markdown=summary_markdown,
    )

    print("Showcase run completed.")
    print(f"Input: {csv_path}")
    print(f"Outputs written to: {out_dir.resolve()}")


def main() -> None:
    args = parse_args()
    run(Path(args.csv).expanduser().resolve(), Path(args.out).expanduser().resolve())


if __name__ == "__main__":
    main()
