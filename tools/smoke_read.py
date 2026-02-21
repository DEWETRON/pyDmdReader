#!/usr/bin/env python3
"""Minimal runtime smoke check for an installed pyDmdReader wheel."""

from pathlib import Path
import sys

import pyDmdReader


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    dmd_path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "tests" / "data" / "simple.dmd"
    if not dmd_path.exists():
        raise SystemExit(f"Smoke DMD file not found: {dmd_path}")

    with pyDmdReader.DmdReader(str(dmd_path)) as dmd:
        if not dmd.channel_names:
            raise SystemExit("No channels found in smoke DMD file")
        first_channel = dmd.channel_names[0]
        data = dmd.read_dataframe(first_channel)
        if data.empty:
            raise SystemExit("Smoke read returned empty dataframe")
        print(f"SMOKE_OK channel={first_channel} rows={len(data)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
