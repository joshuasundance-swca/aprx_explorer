import argparse
import os
from getpass import getpass

import pandas as pd

from aprx_explorer.data_models import GPHistory

try:
    from langchain_openai.chat_models import ChatOpenAI
    from aprx_explorer.summarize import add_summaries

    SUMMARIZE_AVAILABLE = True
    SUMMARIZE_IMPORTERROR = None
except ImportError as e:
    SUMMARIZE_AVAILABLE = False
    SUMMARIZE_IMPORTERROR = e


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract geoprocessing history objects from an ArcGIS Pro project file.",
    )
    parser.add_argument(
        "--openai_api_key",
        type=str,
        default="",
        help="Omit for a secure prompt",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4-0125-preview",
        help="Default: gpt-4-0125-preview",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Summarize the geoprocessing history objects.",
    )
    parser.add_argument("aprx", type=str, help="Path to an ArcGIS Pro project file.")
    parser.add_argument(
        "output",
        type=str,
        help="Path to save the output CSV or Parquet file.",
    )
    args = parser.parse_args()
    _, ext = os.path.splitext(args.output)
    if ext.lower() not in (".csv", ".parquet", ".pq"):
        raise ValueError(f"Unsupported file extension: {ext}")
    return args


def _main(
    aprx: str,
    output: str,
    summarize: bool = False,
    model: str = "gpt-4-0125-preview",
    openai_api_key: str = "",
) -> pd.DataFrame:
    print(f"Reading {aprx}...")
    history = GPHistory.history_from_aprx(aprx)
    if summarize:
        if SUMMARIZE_IMPORTERROR is not None:
            raise ImportError(
                "Dependencies for summarization are not installed. "
                "Use `pip install aprx_explorer[summarize]` to install them, "
                "or run without the `--summarize` flag.",
            ) from SUMMARIZE_IMPORTERROR
        llm = ChatOpenAI(
            model_name=model,
            openai_api_key=openai_api_key or getpass("OpenAI API Key: "),  # type: ignore
        )
        history = add_summaries(history, llm)
    df = GPHistory.history_to_df(history)
    print(df["name"].value_counts())
    print(df[["start_time", "end_time", "run_duration"]].describe())
    _, ext = os.path.splitext(output)
    ext = ext.lower().strip(".")
    if ext == "csv":
        df.to_csv(output, index=False)
    elif ext in ("parquet", "pq"):
        df.to_parquet(output, index=False)
    print(f"Output saved to {output}")
    return df


def main() -> None:
    args = get_args()
    _ = _main(
        aprx=args.aprx,
        output=args.output,
        summarize=args.summarize,
        model=args.model,
        openai_api_key=args.openai_api_key,
    )


if __name__ == "__main__":
    main()
