# AI Instructions — Resume & CV Management

## Files
```
resume/
├── resume.tex          ← master resume, curated and concise, only updated at checkpoints
├── resume_draft.tex    ← working copy of resume, created at start of each session
├── resume.pdf          ← auto-generated on save, do not edit
├── resume.md           ← markdown export, regenerated at every checkpoint
├── cv.tex              ← cumulative CV, complete record of all experience, never trimmed
├── cv_draft.tex        ← working copy of CV, created alongside resume_draft.tex
├── cv.pdf              ← auto-generated on save, do not edit
├── cv.md               ← markdown export, regenerated at every checkpoint
└── README.md           ← this file
```

## Resume vs CV distinction
- **Resume** (`resume.tex`): curated, concise, typically 1-2 pages. Bullets are selected and worded for impact. May omit older or less relevant experience.
- **CV** (`cv.tex`): cumulative and complete. Every role, project, publication, talk, and achievement is preserved in full. Nothing is ever removed. Grows over time.

## Workflow rules

### Starting a session
When the user asks to edit the resume:
1. Copy `resume.tex` to `resume_draft.tex` and `cv.tex` to `cv_draft.tex`
2. Confirm: "Drafts created from master files. Working on `resume_draft.tex` and `cv_draft.tex`."
3. Make all edits in the draft files only
4. Never touch `resume.tex` or `cv.tex` until a checkpoint is confirmed

### During editing
- All edits go to the draft files
- After each logical change, briefly summarize what was changed in each file
- Any new experience, bullet, role, publication, or achievement added to the resume must also be added to the CV
- The CV may contain additional detail, older roles, or entries not present in the resume — that is expected and correct
- If the user pastes a job posting and asks to tailor the resume:
  - Identify which existing bullets are most relevant
  - Strengthen or reorder them to match the posting's language
  - Do not fabricate new experience
  - Tailoring edits apply to `resume_draft.tex` only — the CV is not tailored
- If the user adds new experience directly to the CV without touching the resume, ask whether any of it should also be reflected in the resume

### Checkpoints
At a natural stopping point, or when the user says they are happy with changes, ask:
> "Ready to save to master? I'll copy both drafts into `resume.tex` and `cv.tex` and regenerate the markdown files."

Only overwrite master files after explicit confirmation. Then:
1. Copy `resume_draft.tex` → `resume.tex`
2. Copy `cv_draft.tex` → `cv.tex`
3. Regenerate `resume.md` from `resume.tex`
4. Regenerate `cv.md` from `cv.tex`
5. Delete both draft files

### Aborting
If the user says to discard changes, delete both draft files and confirm:
> "Drafts discarded. Master files and markdown unchanged."

---

## Markdown export format

The `.md` files are plain-text versions of the resume and CV intended for copying into LinkedIn, job application forms, and other plain-text fields. They are always regenerated from the master `.tex` files at checkpoints — never edited directly.

### Formatting rules for markdown export
- Section headers: `## SECTION NAME`
- Job/role line: `**Title** — Employer · Date range`
- Institution line: plain text, no formatting
- Bullets: standard `- ` markdown bullets
- Publications: numbered list `1.` with full citation in plain text
- Strip all LaTeX commands: no `\`, no `{}`, no `\textbf`, etc.
- Replace LaTeX en-dashes `--` with `–`
- Replace LaTeX quotes ` ``text'' ` with `"text"`
- Replace `\$` with `$`, `\%` with `%`, `\&` with `&`
- Keep blank lines between sections for readability
- Do not include a page break or PDF-specific spacing — the markdown is for copy-paste use, not print

---

## LaTeX conventions in this file

- Section headers: `\rsection{}`
- Job/role line with right-aligned date: `\jobline{Title}{Date}`
- Sub-institution line: `\subline{}`
- Bullet list: `\begin{rlist} \item ... \end{rlist}`
- Escape special characters: `\$`, `\%`, `\&`, `\#`
- En dash for date ranges: `--` renders as –
- Smart quotes: `` ``quoted'' `` renders as "quoted"

---

## Content rules
- Do not invent, embellish, or infer experience not provided by the user
- Do not remove bullets without explicit instruction
- When tailoring for a job posting, adjust wording and emphasis only — no new claims
- Preserve all dates exactly as written
- Keep bullet tense consistent within each role (check existing pattern before editing)
- **CV is append-only**: never remove or shorten entries in `cv.tex` — only add
- **Resume may be trimmed**: older or less relevant entries may be omitted from `resume.tex` at the user's direction, but the full record always stays in `cv.tex`