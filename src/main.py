"""Application entry point.

Phase 0 stub. Later phases will add:
  --prepare-data   Download and cache the Hugging Face dataset
  streamlit run    Launch the recommendation UI
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Zomato-inspired AI restaurant recommendation system",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    parser.add_argument(
        "--prepare-data",
        action="store_true",
        help="Download and cache the Hugging Face dataset",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the FastAPI backend server",
    )
    args = parser.parse_args(argv)

    if args.prepare_data:
        from src.data.store import get_restaurants
        print("Preparing data...")
        df = get_restaurants(force_refresh=True)
        print(f"Data preparation complete. {len(df)} records cached.")
        return 0

    if args.serve:
        import uvicorn
        from src.api.main import app
        print("Starting FastAPI backend...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return 0

    print("Project scaffold ready. Run with --prepare-data to download dataset.")
    print("Run with --serve to start the backend API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
