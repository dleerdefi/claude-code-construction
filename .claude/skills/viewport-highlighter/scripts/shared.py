"""Shared utilities for skill output scripts."""

from pathlib import Path


def safe_output_path(output: str) -> Path:
    """Return a non-colliding output path.

    If the target file already exists, appends _v2, _v3, etc. to the stem.
    Skills must never overwrite existing files — this ensures prior work is preserved.
    """
    out = Path(output)
    if out.exists():
        stem, suffix = out.stem, out.suffix
        v = 2
        while out.exists():
            out = out.parent / f"{stem}_v{v}{suffix}"
            v += 1
    return out
