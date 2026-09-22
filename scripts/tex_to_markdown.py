#!/usr/bin/env python3
"""Convert a resume/CV .tex file into the house-style plain-text Markdown
described in README.md (for pasting into LinkedIn, job application forms,
etc).

Usage:
    python scripts/tex_to_markdown.py resume/resume.tex
    python scripts/tex_to_markdown.py cv/cv.tex

Writes a .md file next to the source .tex file.

This is a small hand-rolled parser, not a generic LaTeX-to-Markdown engine
(e.g. pandoc). The source documents only ever use a handful of custom
macros -- \\rsection, \\jobline, \\subline, the rlist/publist list
environments, plus a couple of plain tabular tables -- so a general-purpose
converter would need just as much custom filtering to hit this specific
house style as this script does directly, without the extra dependency.

Known simplification: within the Education section, \\jobline's second
argument is a location ("Boulder, CO") rather than a date, so it's rendered
with an em dash instead of the usual middle dot. Every other section is
assumed to use \\jobline's second argument as a date.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

EM_DASH = "\u2014"  # —
EN_DASH = "\u2013"  # –
MIDDOT = "\u00b7"  # ·


# ---------------------------------------------------------------- inline text

def _substitute(text: str, keep_emphasis: bool, hfill_sep: str = MIDDOT) -> str:
    """Character-level substitutions documented in README.md.

    keep_emphasis=True preserves \\textbf/\\textit as markdown emphasis
    (used for standalone sub-heading lines); keep_emphasis=False strips
    them to plain text (used inside list items, per README's "strip all
    LaTeX commands" rule for bullet content).

    hfill_sep is the separator \\hfill collapses to -- normally a middle
    dot, but an em dash inside Education, where \\hfill separates a title
    from a location rather than a date (see render_jobline's docstring
    note for the same rule applied to \\jobline).
    """
    if keep_emphasis:
        text = re.sub(r"\\textbf\{([^{}]*)\}", r"**\1**", text)
        text = re.sub(r"\\textit\{([^{}]*)\}", r"*\1*", text)
    else:
        text = re.sub(r"\\text(?:bf|it)\{([^{}]*)\}", r"\1", text)

    text = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", text)
    text = text.replace(r"\hfill", f" {hfill_sep} ")
    text = text.replace("---", EM_DASH)
    # digit--digit -> en dash, no surrounding space ("2016--2021", "5--10")
    text = re.sub(r"(?<=\d)\s*--\s*(?=\d)", EN_DASH, text)
    # remaining word--word -> en dash, with surrounding space
    text = re.sub(r"\s--\s", f" {EN_DASH} ", text)
    text = text.replace("``", '"').replace("''", '"')
    text = text.replace(r"\%", "%").replace(r"\&", "&").replace(r"\$", "$")
    text = re.sub(r"\\ ", " ", text)  # escaped space
    text = re.sub(r"\\noindent", "", text)
    text = re.sub(r"\\par\b", "", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def inline(text: str) -> str:
    """Substitution for list-item / citation text (formatting stripped)."""
    return _substitute(text, keep_emphasis=False)


def block_text(text: str, hfill_sep: str = MIDDOT) -> str:
    """Substitution for standalone paragraph/heading text (formatting kept)."""
    return _substitute(text, keep_emphasis=True, hfill_sep=hfill_sep)


# -------------------------------------------------------------------- header

_CENTER_RE = re.compile(r"\\begin\{center\}(.*?)\\end\{center\}", re.S)
_LINEBREAK_RE = re.compile(r"\\\\(?:\[[^\]]*\])?")


def parse_header(body: str) -> tuple[str, str]:
    """Return (markdown_header, body_with_header_removed)."""
    m = _CENTER_RE.search(body)
    if not m:
        raise ValueError(r"Could not find \begin{center}...\end{center} header block")
    raw, remaining = m.group(1), body[m.end():]

    lines = [" ".join(seg.split()) for seg in _LINEBREAK_RE.split(raw)]
    lines = [l for l in lines if l]
    if not lines:
        raise ValueError("Empty header block")

    name = re.sub(r"\{\\LARGE\\bfseries\s+(.*?)\}", r"\1", lines[0]).strip()
    out = [f"# {name}", ""]
    for line in lines[1:]:
        line = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", line)
        line = re.sub(r"\\?\s*\$\|\$\\?\s*", " | ", line)
        out.append(" ".join(line.split()))

    return "\n".join(out), remaining


# --------------------------------------------------------------- item lists

def parse_items(content: str) -> list[str]:
    parts = re.split(r"\\item\b", content)
    return [inline(" ".join(part.split())) for part in parts[1:]]


def parse_tabular(content: str) -> list[str]:
    lines = []
    for row in _LINEBREAK_RE.split(content.strip()):
        row = row.strip()
        if not row:
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)&", row)]
        if len(cells) == 3:
            left, _mid, right = cells
            lines.append(f"{inline(left)} {EM_DASH} {inline(right)}")
        elif len(cells) == 2:
            left, right = cells
            bf = re.match(r"\\textbf\{([^{}]*)\}$", left)
            if bf:
                lines.append(f"**{inline(bf.group(1))}:** {inline(right)}")
            else:
                lines.append(f"{inline(left)} {EM_DASH} {inline(right)}")
        else:
            lines.append(inline(row.replace("&", " ")))
    return lines


# --------------------------------------------------------------- tokenizing

_TOKEN_RE = re.compile(
    r"\\rsection\{(?P<rsection>[^{}]*)\}"
    r"|\\jobline\{(?P<job1>[^{}]*)\}\{(?P<job2>[^{}]*)\}"
    r"|\\subline\{(?P<subline>[^{}]*)\}"
    r"|\\begin\{rlist\}(?P<rlist>.*?)\\end\{rlist\}"
    r"|\\begin\{publist\}(?P<publist>.*?)\\end\{publist\}"
    r"|\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\}(?P<tabular>.*?)\\end\{tabular\}"
    r"|\\vspace\{[^{}]*\}",
    re.S,
)


def tokenize(body: str) -> list[tuple]:
    events: list[tuple] = []
    pos = 0
    for m in _TOKEN_RE.finditer(body):
        gap = body[pos:m.start()]
        if gap.strip():
            events.append(("text", gap))
        pos = m.end()

        if m.group("rsection") is not None:
            events.append(("rsection", m.group("rsection")))
        elif m.group("job1") is not None:
            events.append(("jobline", m.group("job1"), m.group("job2")))
        elif m.group("subline") is not None:
            events.append(("subline", m.group("subline")))
        elif m.group("rlist") is not None:
            events.append(("rlist", parse_items(m.group("rlist"))))
        elif m.group("publist") is not None:
            events.append(("publist", parse_items(m.group("publist"))))
        elif m.group("tabular") is not None:
            events.append(("tabular", parse_tabular(m.group("tabular"))))
        # bare \vspace{...} carries no group -> silently dropped

    tail = body[pos:]
    if tail.strip():
        events.append(("text", tail))
    return events


def render_text_block(raw: str) -> str:
    # Note: unlike \jobline (see render_jobline), \hfill inside plain prose
    # always collapses to a middle dot, even in Education -- there it
    # separates a course-load label from a date range ("Engineering
    # Science Focus \hfill 2016--2021"), not a title from a location. The
    # one spot this reads slightly wrong is a hand-written
    # "\noindent\textbf{X}\hfill Y" location line (e.g. "High School"),
    # which prints as "**High School** · Tehran, Iran" instead of an em
    # dash -- rare enough, and ambiguous enough without a \jobline macro
    # to key off of, that it's left as a known simplification.
    lines = []
    for seg in _LINEBREAK_RE.split(raw):
        seg = " ".join(seg.split())
        if seg:
            lines.append(block_text(seg))
    return "\n".join(lines)


def render_jobline(title: str, date: str, subline: str | None, section: str | None) -> str:
    title = block_text(title)
    date = block_text(date)
    if subline is not None:
        inst = block_text(subline)
        return f"**{title}** {EM_DASH} {inst} {MIDDOT} {date}" if date else f"**{title}** {EM_DASH} {inst}"
    if not date:
        return f"**{title}**"
    # See module docstring: Education's second jobline argument is a
    # location, not a date, so it reads better with an em dash.
    sep = EM_DASH if section and section.strip().lower() == "education" else MIDDOT
    return f"**{title}** {sep} {date}"


def render_body(events: list[tuple]) -> str:
    blocks: list[str] = []
    current_section: str | None = None
    i, n = 0, len(events)
    while i < n:
        kind = events[i][0]
        if kind == "rsection":
            title = block_text(events[i][1])
            current_section = title
            blocks.append("---")
            blocks.append(f"## {title.upper()}")
            i += 1
        elif kind == "jobline":
            _, title, date = events[i]
            subline = None
            if i + 1 < n and events[i + 1][0] == "subline":
                subline = events[i + 1][1]
                i += 2
            else:
                i += 1
            line = render_jobline(title, date, subline, current_section)
            # A jobline with no subline is sometimes followed directly by
            # plain continuation text (e.g. Education entries) rather than
            # a bullet list -- keep those on consecutive lines, not split
            # across a blank line, to match the source's single "entry".
            if subline is None and i < n and events[i][0] == "text":
                rendered = render_text_block(events[i][1])
                i += 1
                line = f"{line}\n{rendered}" if rendered else line
            blocks.append(line)
        elif kind == "subline":
            # Orphan subline (not expected from these macros, but don't crash).
            blocks.append(f"{EM_DASH} {block_text(events[i][1])}")
            i += 1
        elif kind == "rlist":
            blocks.append("\n".join(f"- {item}" for item in events[i][1]))
            i += 1
        elif kind == "publist":
            blocks.append("\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(events[i][1])))
            i += 1
        elif kind == "tabular":
            blocks.append("\n".join(events[i][1]))
            i += 1
        elif kind == "text":
            rendered = render_text_block(events[i][1])
            if rendered:
                blocks.append(rendered)
            i += 1
        else:
            i += 1
    return "\n\n".join(blocks)


# ------------------------------------------------------------------- driver

def strip_comments(text: str) -> str:
    """Drop LaTeX '% comment' text, but leave escaped '\\%' alone."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def tex_to_markdown(tex_path: Path) -> str:
    raw = strip_comments(tex_path.read_text(encoding="utf-8"))

    doc_match = re.search(r"\\begin\{document\}(.*)\\end\{document\}", raw, re.S)
    if not doc_match:
        raise ValueError(rf"No \begin{{document}}...\end{{document}} found in {tex_path}")
    body = re.sub(r"\\pagestyle\{[^{}]*\}", "", doc_match.group(1))

    header_md, rest = parse_header(body)
    body_md = render_body(tokenize(rest))

    return f"{header_md}\n\n{body_md}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tex_file", type=Path, help="Path to the .tex file to convert")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output .md path (default: alongside the source, same stem)",
    )
    args = parser.parse_args()

    try:
        markdown = tex_to_markdown(args.tex_file)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from None
    out_path = args.output or args.tex_file.with_suffix(".md")
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
