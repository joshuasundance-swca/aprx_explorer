import argparse
import os
from getpass import getpass

from aprx_explorer.data_models import GPHistory


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


def main() -> None:
    args = get_args()
    print(f"Reading {args.aprx}...")
    history = GPHistory.history_from_aprx(args.aprx)
    if args.summarize:
        from langchain_openai.chat_models import ChatOpenAI
        from summarize import add_summaries

        llm = ChatOpenAI(
            model=args.model,
            openai_api_key=args.openai_api_key or getpass("OpenAI API Key: "),  # type: ignore
        )
        history = add_summaries(history, llm)
    df = GPHistory.history_to_df(history)
    print(df["name"].value_counts())
    print(df[["start_time", "end_time", "run_duration"]].describe())
    _, ext = os.path.splitext(args.output)
    ext = ext.lower().strip(".")
    if ext == "csv":
        df.to_csv(args.output, index=False)
    elif ext in ("parquet", "pq"):
        df.to_parquet(args.output, index=False)
    print(f"Output saved to {args.output}")


if __name__ == "__main__":
    main()
