#!/usr/bin/env python3
"""Build VioNER defense slides from Marp markdown.

Produces both PPTX (editable in PowerPoint, slide notes preserved) and PDF
(safe projector fallback). Marp-CLI is the canonical Marp renderer; it must
be installed once on the build machine:

    npm install -g @marp-team/marp-cli

Usage:
    python build_slides.py             # build both pptx and pdf
    python build_slides.py --pptx-only # build pptx only
    python build_slides.py --pdf-only  # build pdf only
    python build_slides.py --watch     # rebuild on slides.md change

Outputs are written next to this file as slides.pptx and slides.pdf.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLIDES_MD = HERE / "slides.md"
THEME_CSS = HERE / "theme.css"
PPTX_OUT = HERE / "slides.pptx"
PDF_OUT = HERE / "slides.pdf"


def _require_marp() -> str:
    """Locate marp-cli or fail with an actionable message."""
    marp = shutil.which("marp")
    if marp:
        return marp
    print(
        "ERROR: marp-cli is not on PATH.\n"
        "Install it once with:\n"
        "    npm install -g @marp-team/marp-cli\n"
        "Or run via npx:\n"
        "    npx @marp-team/marp-cli@latest slides.md -o slides.pptx",
        file=sys.stderr,
    )
    sys.exit(1)


def _check_inputs() -> None:
    """Fail fast if expected input files are missing."""
    missing = []
    if not SLIDES_MD.exists():
        missing.append(str(SLIDES_MD))
    if not THEME_CSS.exists():
        missing.append(str(THEME_CSS))
    if missing:
        print(f"ERROR: required input(s) missing: {', '.join(missing)}",
              file=sys.stderr)
        sys.exit(1)


def _run_marp(marp: str, output: Path, fmt: str, watch: bool = False) -> None:
    """Invoke marp-cli to produce one output artefact."""
    cmd = [
        marp,
        str(SLIDES_MD),
        "--theme-set", str(THEME_CSS),
        "--allow-local-files",
        f"--{fmt}",
        "-o", str(output),
    ]
    if watch:
        cmd.append("--watch")

    print(f"  marp -> {output.name}")
    result = subprocess.run(cmd, cwd=HERE)
    if result.returncode != 0:
        print(f"ERROR: marp failed for {fmt} (exit {result.returncode})",
              file=sys.stderr)
        sys.exit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pptx-only", action="store_true",
                        help="Build PPTX only (skip PDF)")
    parser.add_argument("--pdf-only", action="store_true",
                        help="Build PDF only (skip PPTX)")
    parser.add_argument("--watch", action="store_true",
                        help="Rebuild on slides.md change (PPTX only)")
    args = parser.parse_args()

    _check_inputs()
    marp = _require_marp()

    print(f"Building VioNER defense slides from {SLIDES_MD.name}")

    build_pptx = not args.pdf_only
    build_pdf = not args.pptx_only and not args.watch

    if build_pptx:
        _run_marp(marp, PPTX_OUT, "pptx", watch=args.watch)

    if build_pdf:
        _run_marp(marp, PDF_OUT, "pdf")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
