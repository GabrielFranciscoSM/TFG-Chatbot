from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from validation.datasets import DatasetLoader


def summarize_dataset(name: str, df: pd.DataFrame) -> dict:
    work = df.copy()
    work["text"] = work["text"].astype(str).str.strip()
    work = (
        work[work["text"].str.len() > 0]
        .drop_duplicates(subset=["text"])
        .reset_index(drop=True)
    )
    work["char_len"] = work["text"].str.len()
    work["tok_len"] = work["text"].str.findall(r"\w+").str.len()

    return {
        "dataset": name,
        "n_rows": int(len(work)),
        "n_labels": int(work["label"].nunique()),
        "char_len_mean": float(work["char_len"].mean()),
        "char_len_p50": float(work["char_len"].median()),
        "char_len_p90": float(work["char_len"].quantile(0.9)),
        "tok_len_mean": float(work["tok_len"].mean()),
        "tok_len_p50": float(work["tok_len"].median()),
        "tok_len_p90": float(work["tok_len"].quantile(0.9)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quick comparison for FAQ-oriented clustering datasets"
    )
    parser.add_argument(
        "--limit", type=int, default=5000, help="Max rows to load per dataset"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("validation/results/dataset_exploration"),
        help="Directory to write summary tables",
    )
    args = parser.parse_args()

    loader = DatasetLoader()
    dataset_loaders = {
        "esquad": lambda: loader.load_esquad(),
        "banking77": lambda: loader.load_banking77(limit=args.limit),
        "askubuntu": lambda: loader.load_askubuntu(limit=args.limit),
        "clinc150": lambda: loader.load_clinc150(limit=args.limit),
        "dialogsum": lambda: loader.load_dialogsum().head(args.limit),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    failed_rows = []
    for name, load_fn in dataset_loaders.items():
        print(f"Loading {name}...")
        try:
            df = load_fn()
            summary_rows.append(summarize_dataset(name, df))
            sample_path = args.output_dir / f"{name}_sample.csv"
            df.head(200).to_csv(sample_path, index=False, encoding="utf-8")
            print(
                f"  OK: rows={len(df)} labels={df['label'].nunique()} sample={sample_path}"
            )
        except Exception as exc:
            failed_rows.append({"dataset": name, "error": str(exc)})
            print(f"  ERROR: {exc}")

    summary_df = (
        pd.DataFrame(summary_rows).sort_values("dataset").reset_index(drop=True)
    )
    summary_path = args.output_dir / "dataset_summary.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8")
    print(f"\nSummary written to: {summary_path}")

    if failed_rows:
        failed_df = pd.DataFrame(failed_rows)
        failed_path = args.output_dir / "dataset_failures.csv"
        failed_df.to_csv(failed_path, index=False, encoding="utf-8")
        print(f"Some datasets failed. Details: {failed_path}")


if __name__ == "__main__":
    main()
