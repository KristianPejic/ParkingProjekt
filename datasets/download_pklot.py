from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

try:
    import kagglehub  # type: ignore
except Exception as e:
    print("kagglehub is required. Install with: pip install kagglehub", file=sys.stderr)
    raise


def download_pklot() -> Path:
    """
    Download the PKLot dataset via KaggleHub.
    Returns the local cache path to the dataset contents.
    """
    print("Downloading PKLot dataset via KaggleHub (first run may take a while)...")
    path_str = kagglehub.dataset_download("ammarnassanalhajali/pklot-dataset")
    path = Path(path_str)
    print(f"Path to dataset files: {path}")
    return path


def copy_dataset(src: Path, dest: Path) -> None:
    """
    Optionally copy the dataset from KaggleHub cache into a local project directory.
    This is useful if you want a stable project-local path (e.g. datasets/pklot).
    """
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Copying dataset contents to: {dest}")
    # Copy directory tree (without overwriting existing identical files aggressively)
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    print("Copy complete.")


def main():
    parser = argparse.ArgumentParser(description="Download PKLot dataset using KaggleHub")
    parser.add_argument(
        "--copy-to",
        type=Path,
        default=Path("datasets/pklot"),
        help="Optional destination directory to copy the dataset to (default: datasets/pklot)",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Skip copying and only print the KaggleHub cache path",
    )
    args = parser.parse_args()

    cache_path = download_pklot()
    if not args.no_copy:
        copy_dataset(cache_path, args.copy_to)
        print(f"Local dataset available at: {args.copy_to.resolve()}")
    else:
        print(f"KaggleHub cache path: {cache_path.resolve()}")
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

try:
    import kagglehub  # type: ignore
except Exception as e:
    print("kagglehub is required. Install with: pip install kagglehub", file=sys.stderr)
    raise


def download_pklot() -> Path:
    """
    Download the PKLot dataset via KaggleHub.
    Returns the local cache path to the dataset contents.
    """
    print("Downloading PKLot dataset via KaggleHub (first run may take a while)...")
    path_str = kagglehub.dataset_download("ammarnassanalhajali/pklot-dataset")
    path = Path(path_str)
    print(f"Path to dataset files: {path}")
    return path


def copy_dataset(src: Path, dest: Path) -> None:
    """
    Optionally copy the dataset from KaggleHub cache into a local project directory.
    This is useful if you want a stable project-local path (e.g. datasets/pklot).
    """
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Copying dataset contents to: {dest}")
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    print("Copy complete.")


def main():
    parser = argparse.ArgumentParser(description="Download PKLot dataset using KaggleHub")
    parser.add_argument(
        "--copy-to",
        type=Path,
        default=Path("datasets/pklot"),
        help="Optional destination directory to copy the dataset to (default: datasets/pklot)",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Skip copying and only print the KaggleHub cache path",
    )
    args = parser.parse_args()

    cache_path = download_pklot()
    if not args.no_copy:
        copy_dataset(cache_path, args.copy_to)
        print(f"Local dataset available at: {args.copy_to.resolve()}")
    else:
        print(f"KaggleHub cache path: {cache_path.resolve()}")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
