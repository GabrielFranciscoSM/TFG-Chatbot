import pandas as pd
from datasets import load_dataset


class DatasetLoader:
    """Helper class to load and format datasets for clustering."""

    def load_dialogsum(self):
        # DialogSum: Conversations with clear topics
        print("Loading DialogSum...")
        ds = load_dataset("knkarthick/dialogsum", split="train", trust_remote_code=True)
        df = pd.DataFrame(ds)
        # We use 'dialogue' as the text and 'topic' as the ground truth label
        return df[["dialogue", "topic"]].rename(
            columns={"dialogue": "text", "topic": "label"}
        )

    def load_stackoverflow(self, limit=5000):
        # Stack Overflow: Technical Q&A
        # Using a cleaned subset for efficiency
        print("Loading Stack Overflow subset...")
        ds = load_dataset(
            "codesearchnet", "python", split="train", trust_remote_code=True
        )
        df = pd.DataFrame(ds).head(limit)
        # Using docstrings/comments as the technical text
        return (
            df[["docstring"]]
            .rename(columns={"docstring": "text"})
            .assign(label="Technical")
        )

    def load_esquad(self):
        # ESQAD: Spanish Education Q&A
        print("Loading ESQAD (Spanish)...")
        ds = load_dataset("mrm8488/es_quad", split="train", trust_remote_code=True)
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
