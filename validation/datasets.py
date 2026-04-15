import pandas as pd
from datasets import load_dataset


class DatasetLoader:
    """Helper class to load and format datasets for clustering."""

    def load_dialogsum(self):
        # DialogSum: Conversations with clear topics
        print("Loading DialogSum...")
        ds = load_dataset("knkarthick/dialogsum", split="train")
        df = pd.DataFrame(ds)
        # We use 'dialogue' as the text and 'topic' as the ground truth label
        return df[["dialogue", "topic"]].rename(
            columns={"dialogue": "text", "topic": "label"}
        )

    def load_stackoverflow(self, limit=5000):
        # Technical code/documentation corpus (CodeSearchNet Python subset)
        print("Loading Stack Overflow subset...")
        ds = load_dataset("code_search_net", "python", split="train")
        df = pd.DataFrame(ds).head(limit)
        # Keep compatibility across schema versions
        text_col = next(
            (
                c
                for c in [
                    "func_documentation_string",
                    "docstring",
                    "whole_func_string",
                    "func_code_string",
                ]
                if c in df.columns
            ),
            None,
        )
        if text_col is None:
            raise ValueError(
                f"No text-like column found in code_search_net columns: {list(df.columns)}"
            )

        out = (
            df[[text_col]].rename(columns={text_col: "text"}).assign(label="Technical")
        )
        out = out.dropna(subset=["text"])
        out = out[out["text"].astype(str).str.strip().str.len() > 0]
        return out.reset_index(drop=True)

    def load_esquad(self):
        # Spanish QA fallback with stable parquet-backed source
        print("Loading ESQAD (Spanish)...")
        ds = load_dataset("google/xquad", "xquad.es", split="validation")
        df = pd.DataFrame(ds)
        # Using the 'question' field for clustering
        return (
            df[["question"]]
            .rename(columns={"question": "text"})
            .assign(label="Education_ES")
        )


def present_datasets():
    loader = DatasetLoader()

    datasets = {
        "DialogSum (EN)": loader.load_dialogsum().head(5),
        "Stack Overflow (EN)": loader.load_stackoverflow(limit=5).head(5),
        "ESQAD (ES)": loader.load_esquad().head(5),
    }

    for name, df in datasets.items():
        print(f"\n{'='*20} {name} {'='*20}")
        print(f"Total Rows in Sample: {len(df)}")
        print(df[["text"]].head(3))  # Showing first 3 rows
        print("-" * 50)
