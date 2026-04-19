from pathlib import Path

from src.datathon_showcase.run_showcase import run


def main() -> None:
    project_root = Path(__file__).resolve().parent
    csv_path = project_root / "data" / "synthetic_injection_molding_demo.csv"
    out_dir = project_root / "outputs"

    run(csv_path=csv_path, out_dir=out_dir)


if __name__ == "__main__":
    main()
