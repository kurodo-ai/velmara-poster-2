#!/usr/bin/env python3
"""Deliver the finished Velmara poster to the output directory.

The artwork is rendered ahead of time by src/make_image.py and stored
next to this script as entry.png. All this entrypoint does — using
nothing beyond the standard library — is copy that file into the
directory named by the MAKEFUN_OUTPUT_DIR environment variable, or
/output when the variable is not set.
"""

import os
import shutil
import sys

POSTER_NAME = "entry.png"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def output_dir():
    """Where the poster has to end up."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def deliver():
    """Copy entry.png into the output directory; return an exit code."""
    source = os.path.join(SCRIPT_DIR, POSTER_NAME)
    if not os.path.isfile(source):
        raise SystemExit("entry.png is missing; run src/make_image.py first")
    if os.path.getsize(source) == 0:
        raise SystemExit("entry.png is empty")

    target_dir = output_dir()
    os.makedirs(target_dir, exist_ok=True)
    destination = os.path.join(target_dir, POSTER_NAME)
    shutil.copyfile(source, destination)

    # Confirm the copy arrived whole before calling it delivered.
    written = os.path.getsize(destination)
    if written != os.path.getsize(source):
        raise SystemExit("copied entry.png is incomplete")
    print(f"handed in entry.png ({written} bytes) -> {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
