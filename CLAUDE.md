# Resume & CV — Editing Workflow

Operating instructions for editing `resume.tex`/`cv.tex` in this repo.
For a plain repo-layout overview, see README.md.

## Files

```
resume/
├── resume.tex          ← master resume: curated, concise, updated only at checkpoints
├── resume_draft.tex    ← working copy, created at the start of an editing session
├── resume.pdf          ← built via scripts/tex_to_pdf.py, never hand-edited
└── resume.md           ← built via scripts/tex_to_markdown.py, never hand-edited
cv/
├── cv.tex               ← master CV: cumulative, complete, append-only
├── cv_draft.tex          ← working copy, created alongside resume_draft.tex
├── cv.pdf
└── cv.md
scripts/
├── tex_to_pdf.py         ← compile a .tex file to PDF (latexmk/pdflatex)
└── tex_to_markdown.py    ← convert a .tex file to the house-style Markdown
```

## Resume vs. CV

- **Resume** (`resume.tex`): curated, concise, 1–2 pages. Bullets are
  selected and worded for impact against a target job/domain. Older or
  less relevant experience may be trimmed.
- **CV** (`cv.tex`): cumulative and complete. Every role, project,
  publication, talk, and achievement is preserved in full, forever.
  **Append-only** — never remove or shorten an entry.

## Session mechanics

`main` is protected: it only takes changes through a pull request. CI
(`.github/workflows/build.yml`) installs TeX and rebuilds `resume.pdf`,
`cv.pdf`, `resume.md`, and `cv.md` directly onto every PR branch, so by
the time a PR is merged `main` already carries the finished build as
part of the merge commit — there's no separate post-merge build step,
and nothing is ever pushed to `main` directly.

### Starting a session
When the user wants to add or edit content:
1. Create or switch to a feature branch off `main`, e.g.
   `git checkout -b update/<short-description> origin/main`.
2. Copy `resume.tex` → `resume_draft.tex` and `cv.tex` → `cv_draft.tex`.
3. Confirm: "Drafts created from master files on branch `<branch>`.
   Working on `resume_draft.tex` and `cv_draft.tex`."
4. All edits happen in the draft files. Never touch the master `.tex`
   files until a checkpoint is confirmed. Draft `.tex`/`.pdf`/`.md` files
   are gitignored and never committed.

### Checkpoints
At a natural stopping point, or when the user is happy with the drafts, ask:
> "Ready to save to master? I'll copy both drafts into `resume.tex` and
> `cv.tex`, commit, and push the branch."

Only after explicit confirmation:
1. Copy `resume_draft.tex` → `resume.tex`, `cv_draft.tex` → `cv.tex`.
2. Delete both draft files.
3. Commit `resume/resume.tex` and `cv/cv.tex` on the feature branch and
   push it.
4. Open a pull request into `main` (skip if one is already open for this
   branch), then stop. **Never merge it — merging is the repo owner's
   call alone.** Tell the user it's ready and share the link. CI builds
   `resume.pdf`, `cv.pdf`, `resume.md`, and `cv.md` and commits them onto
   the PR branch automatically — no local build needed; the user can
   review the actual rendered output in the PR diff before merging it
   themselves. The branch already carries the finished build, so once
   they merge, nothing further runs. A local build
   (`scripts/tex_to_pdf.py`, `scripts/tex_to_markdown.py`) is still
   available any time an on-demand preview is wanted, but is no longer
   required.

### Aborting
If the user says to discard changes: delete both draft files, confirm
"Drafts discarded. Master files unchanged," and stop. If a feature branch
was created for the session and holds no other unmerged work, ask whether
to delete it too.

---

## Adding a new experience

This is the core workflow: the user describes something they did (a new
role, a project, a promotion) and it needs to land in the CV in full and
in the resume in brief. Work it in three stages.

### 1. Extract the description
The description is the minimum viable one-line entry: which role/position
it falls under, whether that role is current or past, and a one-sentence
context for what the experience actually was. This is usually already
present in what the user tells you — pull it from there rather than
re-asking, but confirm anything ambiguous (dates, whether it's a new role
vs. part of an existing one, current vs. past).

### 2. Extract the details
The details are what make the entry *useful for other roles* — the tools
used, the breadth and depth of knowledge applied, and anything that maps
this specific task onto broader skills, other companies, or the industry
at large. This is mainly on you to draw out, not the user to volunteer:

- **Never assume.** If you can infer a tool, technique, or scope from
  context, don't write it down as fact — ask.
- Pose every gap as a question. Batch related questions rather than
  interrogating one at a time.
- The user often knows *what* they did but not how it maps to the bigger
  picture — how it reads against other roles, industries, or job titles.
  Identifying that mapping is your job, worked out through the same Q&A,
  not by guessing at the framing yourself.

Do not move to step 3 until you have a clear, confirmed picture — both
the description and the details.

### 3. Write it in
- **CV**: add the full entry — description plus every relevant detail —
  to `cv_draft.tex`. Never trim or reword it down; this is the complete
  record.
- **Resume**: add a brief version, then run the resume decision process
  below before finalizing where and how it lands.

---

## Updating the resume

Adding to the CV is just an append. Updating the resume is a judgment
call, because the resume has a page budget and a target. Work through
this every time new experience is added to the resume:

1. **Give an honest market read.** Before touching the file, tell the
   user plainly what kinds of positions their *current* resume would
   actually be competitive for, in the current job market — no
   sugarcoating, no false optimism.
2. **Ask about intent.** Is the user applying within the same domain, a
   slight shift in domain or job type, or a large change?
3. **Pick a scope based on the answer:**
   - **Same domain** → just add the new experience and lightly
     reorganize as needed to keep the resume to two pages.
   - **Slight shift** → re-read the whole CV, then propose a *surgical*
     reorganization and rewording of the existing resume alongside the
     new entry.
   - **Large change** → re-read the whole CV, then propose a broader
     *overhaul* of the resume that incorporates the new entry.

### Approval rules
- **Surgical changes** (reordering, rewording, or trimming *existing*
  resume content — this covers the "same domain" and "slight shift"
  paths, and every follow-up round after an overhaul): show the diff
  first. Only write it to `resume_draft.tex` after the user approves it.
- **Overhaul changes**: draft the full rewritten resume directly — a
  diff isn't the right review format for a rewrite this size. Then ask
  the user to read the result (the rebuilt PDF/Markdown) and give
  feedback. Expect this to be followed by one or more rounds of surgical
  refinement, each gated by the diff-approval rule above.

---

## Content rules

- Do not invent, embellish, or infer experience the user hasn't provided.
- Do not remove bullets from the resume without explicit instruction.
- When tailoring for a job posting: adjust wording and emphasis only —
  identify the most relevant existing bullets and strengthen/reorder them
  to match the posting's language. No new claims. Tailoring edits apply
  to `resume_draft.tex` only; the CV is never tailored.
- If the user adds something to the CV without mentioning the resume, ask
  whether it should also be reflected there.
- Preserve all dates exactly as written.
- Keep bullet tense consistent within each role — check the existing
  pattern before editing.
- **CV is append-only.** Never remove or shorten a `cv.tex` entry.
- **Resume may be trimmed.** Older or less relevant entries may be
  dropped from `resume.tex` at the user's direction; the full record
  always stays in `cv.tex`.

---

## LaTeX conventions used in these files

- Section header: `\rsection{}`
- Job/role line, title left / date right: `\jobline{Title}{Date}`
- Sub-institution line: `\subline{}`
- Bullet list: `\begin{rlist} \item ... \end{rlist}`
- Publication list (CV only, numbered): `\begin{publist} \item ... \end{publist}`
- Escape special characters: `\$`, `\%`, `\&`, `\#`
- En dash for ranges: `--` (renders as –)
- Smart quotes: `` ``quoted'' `` (renders as "quoted")

`scripts/tex_to_markdown.py` understands exactly this macro set. If you
introduce a new one, update that script too, or the Markdown export will
silently drop it.
