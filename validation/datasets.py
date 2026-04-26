import pandas as pd
from datasets import load_dataset
from sklearn.datasets import fetch_20newsgroups


class DatasetLoader:
    """Helper class to load and format datasets for clustering."""

    @staticmethod
    def _first_available_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
        for col in candidates:
            if col in df.columns:
                return col
        return None

    @staticmethod
    def _clean_text_frame(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["text"] = out["text"].astype(str).str.strip()
        out = out[out["text"].str.len() > 0]
        out = out.drop_duplicates(subset=["text"]).reset_index(drop=True)
        if "label" not in out.columns:
            out["label"] = "Unknown"
        out["label"] = out["label"].astype(str)
        return out[["text", "label"]]

    @staticmethod
    def _load_first_available_dataset(
        dataset_candidates: list[tuple[str, str | None]],
        split_candidates: list[str],
    ):
        last_error = None
        for dataset_name, subset_name in dataset_candidates:
            for split_name in split_candidates:
                try:
                    if subset_name is None:
                        ds = load_dataset(dataset_name, split=split_name)
                    else:
                        ds = load_dataset(dataset_name, subset_name, split=split_name)
                    return ds, dataset_name, subset_name, split_name
                except Exception as exc:
                    last_error = exc

        raise RuntimeError(
            "No se pudo cargar ninguno de los datasets/splits candidatos: "
            f"{dataset_candidates} con splits {split_candidates}. Error final: {last_error}"
        )

    def load_dialogsum(self):
        # DialogSum: Conversations with clear topics
        print("Loading DialogSum...")
        ds = load_dataset("knkarthick/dialogsum", split="train")
        df = pd.DataFrame(ds)
        # We use 'dialogue' as the text and 'topic' as the ground truth label
        out = df[["dialogue", "topic"]].rename(
            columns={"dialogue": "text", "topic": "label"}
        )
        return self._clean_text_frame(out)

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
        return self._clean_text_frame(out)

    def load_esquad(self):
        # Spanish QA fallback with stable parquet-backed source
        print("Loading ESQAD (Spanish)...")
        ds = load_dataset("google/xquad", "xquad.es", split="validation")
        df = pd.DataFrame(ds)
        # Using the 'question' field for clustering
        out = (
            df[["question"]]
            .rename(columns={"question": "text"})
            .assign(label="Education_ES")
        )
        return self._clean_text_frame(out)

    def load_banking77(self, limit=5000):
        # Intent dataset with short user queries; strongly aligned with FAQ intent clustering.
        print("Loading Banking77...")
        ds, dataset_name, subset_name, split_name = self._load_first_available_dataset(
            dataset_candidates=[
                ("mteb/banking77", None),
                ("PolyAI/banking77", None),
            ],
            split_candidates=["train", "test", "validation"],
        )
        print(f"Loaded {dataset_name} ({subset_name or 'default'}) split={split_name}")

        df = pd.DataFrame(ds)
        text_col = self._first_available_column(
            df, ["text", "query", "utterance", "sentence"]
        )
        if text_col is None:
            raise ValueError(
                f"No text-like column found in Banking77 columns: {list(df.columns)}"
            )

        label_text_col = self._first_available_column(
            df, ["label_text", "intent", "category", "label_name"]
        )
        label_col = self._first_available_column(df, ["label", "intent", "category"])

        out = df[[text_col]].rename(columns={text_col: "text"})
        if label_text_col is not None:
            out["label"] = df[label_text_col].astype(str)
        elif label_col is not None:
            out["label"] = "Intent_" + df[label_col].astype(str)
        else:
            out["label"] = "Banking77"

        if len(out) > limit:
            out = out.sample(n=limit, random_state=42).reset_index(drop=True)
        return self._clean_text_frame(out)

    def load_askubuntu(self, limit=5000):
        # Technical troubleshooting questions from Ubuntu domain.
        print("Loading AskUbuntu...")
        # First try mteb retrieval-format variant by reconstructing text from corpus + queries.
        try:
            corpus = load_dataset("mteb/askubuntuDupQuestions", "corpus", split="test")
            queries = load_dataset(
                "mteb/askubuntuDupQuestions", "queries", split="test"
            )
            df_corpus = pd.DataFrame(corpus)
            df_queries = pd.DataFrame(queries)

            corpus_text = (
                df_corpus[["title", "text"]]
                .fillna("")
                .astype(str)
                .agg(" ".join, axis=1)
                .str.strip()
            )
            queries_text = df_queries["text"].astype(str).str.strip()

            out = pd.concat(
                [
                    pd.DataFrame({"text": corpus_text, "label": "AskUbuntu_Corpus"}),
                    pd.DataFrame({"text": queries_text, "label": "AskUbuntu_Query"}),
                ],
                ignore_index=True,
            )

            if len(out) > limit:
                out = out.sample(n=limit, random_state=42).reset_index(drop=True)
            return self._clean_text_frame(out)
        except Exception:
            pass

        ds, dataset_name, subset_name, split_name = self._load_first_available_dataset(
            dataset_candidates=[
                ("taolei87/askubuntu", None),
                ("mteb/askubuntuDupQuestions", "top_ranked"),
                ("mteb/askubuntuDupQuestions", None),
            ],
            split_candidates=["train", "validation", "test"],
        )
        print(f"Loaded {dataset_name} ({subset_name or 'default'}) split={split_name}")

        df = pd.DataFrame(ds)

        title_col = self._first_available_column(
            df, ["title", "question_title", "q_title"]
        )
        body_col = self._first_available_column(df, ["body", "question_body", "q_body"])
        text_col = self._first_available_column(
            df, ["text", "question", "query", "utterance"]
        )

        if title_col is not None and body_col is not None:
            text_series = (
                df[title_col].astype(str).str.strip()
                + " "
                + df[body_col].astype(str).str.strip()
            )
        elif text_col is not None:
            text_series = df[text_col].astype(str)
        elif "question1" in df.columns and "question2" in df.columns:
            # Pair datasets are converted to a single question pool.
            text_series = pd.concat(
                [df["question1"], df["question2"]], ignore_index=True
            ).astype(str)
            df = pd.DataFrame({"text": text_series})
        else:
            raise ValueError(
                f"No usable text columns found in AskUbuntu columns: {list(df.columns)}"
            )

        if "text" in df.columns:
            out = df[["text"]].copy()
        else:
            out = pd.DataFrame({"text": text_series})

        label_col = self._first_available_column(df, ["tags", "tag", "topic", "label"])
        if label_col is not None:
            if out.shape[0] == df.shape[0]:
                out["label"] = df[label_col].astype(str)
            else:
                out["label"] = "AskUbuntu"
        else:
            out["label"] = "AskUbuntu"

        if len(out) > limit:
            out = out.sample(n=limit, random_state=42).reset_index(drop=True)
        return self._clean_text_frame(out)

    def load_clinc150(self, limit=5000):
        # Diverse intent benchmark suitable as a FAQ-intent proxy.
        print("Loading CLINC150...")
        ds, dataset_name, subset_name, split_name = self._load_first_available_dataset(
            dataset_candidates=[
                ("clinc_oos", "small"),
                ("clinc_oos", "plus"),
                ("clinc_oos", None),
            ],
            split_candidates=["train", "validation", "test"],
        )
        print(f"Loaded {dataset_name} ({subset_name or 'default'}) split={split_name}")

        df = pd.DataFrame(ds)
        text_col = self._first_available_column(
            df, ["text", "utterance", "query", "sentence"]
        )
        if text_col is None:
            raise ValueError(
                f"No text-like column found in CLINC150 columns: {list(df.columns)}"
            )

        label_text_col = self._first_available_column(
            df, ["intent", "intent_text", "label_text", "domain"]
        )
        label_col = self._first_available_column(df, ["label", "intent"])

        out = df[[text_col]].rename(columns={text_col: "text"})
        if label_text_col is not None:
            out["label"] = df[label_text_col].astype(str)
        elif label_col is not None:
            out["label"] = "Intent_" + df[label_col].astype(str)
        else:
            out["label"] = "CLINC150"

        if len(out) > limit:
            out = out.sample(n=limit, random_state=42).reset_index(drop=True)
        return self._clean_text_frame(out)

    def load_newsgroups20(
        self,
        categories: list[str] | None = None,
        limit: int | None = 5000,
        remove: tuple[str, ...] = ("headers", "footers", "quotes"),
    ):
        # Classic topic-modeling benchmark with 20 thematic newsgroup classes.
        print("Loading 20 Newsgroups...")
        train = fetch_20newsgroups(subset="train", categories=categories, remove=remove)
        test = fetch_20newsgroups(subset="test", categories=categories, remove=remove)

        texts = train.data + test.data
        labels = list(train.target) + list(test.target)
        target_names = train.target_names

        out = pd.DataFrame(
            {
                "text": [str(text) for text in texts],
                "label": [target_names[index] for index in labels],
            }
        )

        if limit is not None and len(out) > limit:
            out = out.sample(n=limit, random_state=42).reset_index(drop=True)
        return self._clean_text_frame(out)


def present_datasets():
    loader = DatasetLoader()

    dataset_builders = {
        "DialogSum (EN)": lambda: loader.load_dialogsum().head(5),
        "Stack Overflow (EN)": lambda: loader.load_stackoverflow(limit=5).head(5),
        "ESQAD (ES)": lambda: loader.load_esquad().head(5),
        "Banking77 (EN)": lambda: loader.load_banking77(limit=5).head(5),
        "AskUbuntu (EN)": lambda: loader.load_askubuntu(limit=5).head(5),
        "CLINC150 (EN)": lambda: loader.load_clinc150(limit=5).head(5),
        "20 Newsgroups (EN)": lambda: loader.load_newsgroups20(limit=5).head(5),
    }

    datasets = {}
    for name, builder in dataset_builders.items():
        try:
            datasets[name] = builder()
        except Exception as exc:
            print(f"Skipping {name}: {exc}")

    for name, df in datasets.items():
        print(f"\n{'='*20} {name} {'='*20}")
        print(f"Total Rows in Sample: {len(df)}")
        print(df[["text"]].head(3))  # Showing first 3 rows
        print("-" * 50)
