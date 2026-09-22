#!/usr/bin/env python3
"""Compile a .tex file to PDF using latexmk (preferred) or pdflatex.

Usage:
    python scripts/tex_to_pdf.py resume/resume.tex
    python scripts/tex_to_pdf.py cv/cv.tex --runs 1

The PDF is written next to the source .tex file, matching this repo's
existing layout (e.g. resume/resume.tex -> resume/resume.pdf). Build
byproducts (.aux/.log/.out) go into a .build/ subdirectory next to the
source, also matching the existing layout.

Requires a TeX distribution (TeX Live or MiKTeX) with latexmk or pdflatex
on PATH -- this is the one thing a pure-Python library can't substitute
for, since it has to actually typeset the document.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def find_engine() -> tuple[str, list[str]]:
    """Return (name, base_command) for the best available LaTeX build tool."""
    if shutil.which("latexmk"):
        return "latexmk", ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]
    if shutil.which("pdflatex"):
        return "pdflatex", ["pdflatex", "-interaction=nonstopmode", "-halt-on-error"]
    raise RuntimeError(
        "Neither 'latexmk' nor 'pdflatex' was found on PATH. "
        "Install a TeX distribution (TeX Live or MiKTeX) first."
    )


def build_pdf(tex_path: Path, runs: int = 2) -> Path:
    """Compile tex_path to a PDF placed next to it. Returns the PDF path."""
    tex_path = tex_path.resolve()
    if not tex_path.is_file():
        raise FileNotFoundError(tex_path)

    build_dir = tex_path.parent / ".build"
    build_dir.mkdir(exist_ok=True)

    engine, base_cmd = find_engine()
    # latexmk works out how many passes it needs on its own; plain pdflatex
    # doesn't, so we just run it a fixed number of times (2 is enough to
    # resolve hyperref's page-count references, which is all this doc uses).
    passes = 1 if engine == "latexmk" else runs

    for _ in range(passes):
        result = subprocess.run(
            [*base_cmd, f"-output-directory={build_dir}", str(tex_path)],
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log_path = build_dir / (tex_path.stem + ".log")
            tail = ""
            if log_path.exists():
                tail = "\n".join(log_path.read_text(errors="replace").splitlines()[-40:])
            raise RuntimeError(
                f"{engine} failed on {tex_path.name} (exit {result.returncode}).\n"
                f"--- last 40 lines of {log_path.name} ---\n{tail}"
            )

    built_pdf = build_dir / (tex_path.stem + ".pdf")
    if not built_pdf.exists():
        raise RuntimeError(f"{engine} reported success but {built_pdf} is missing.")

    final_pdf = tex_path.with_suffix(".pdf")
    shutil.copy2(built_pdf, final_pdf)
    return final_pdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tex_file", type=Path, help="Path to the .tex file to compile")
    parser.add_argument(
        "--runs", type=int, default=2,
        help="Number of pdflatex passes when latexmk isn't available (default: 2)",
    )
    args = parser.parse_args()

    try:
        pdf_path = build_pdf(args.tex_file, runs=args.runs)
    except (FileNotFoundError, RuntimeError) as exc:
        raise SystemExit(f"error: {exc}") from None
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
