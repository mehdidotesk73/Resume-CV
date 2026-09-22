# Resume & CV

LaTeX source for my resume and CV, with build tooling to produce PDFs and
plain-text Markdown (for LinkedIn, job application forms, etc).

## Layout

```
resume/     resume.tex, its built resume.pdf / resume.md, and .build/ (LaTeX byproducts)
cv/         cv.tex, its built cv.pdf / cv.md, and .build/
Versions/   dated PDF snapshots
scripts/    build tooling (see below)
```

## Building

Requires a TeX distribution (MiKTeX or TeX Live) with `pdflatex` or
`latexmk` on PATH.

```
python scripts/tex_to_pdf.py resume/resume.tex
python scripts/tex_to_pdf.py cv/cv.tex
python scripts/tex_to_markdown.py resume/resume.tex
python scripts/tex_to_markdown.py cv/cv.tex
```

Each writes its output next to the source file.

## Editing

See CLAUDE.md for the editing workflow (draft files, checkpoints, and how
new experience gets added to the CV in full and the resume in brief).
It's written as operating instructions for an AI assistant, but the same
draft → checkpoint mechanics apply if you're editing by hand.
