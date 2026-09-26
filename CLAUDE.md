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
Versions/
└── <slug>_resume.{tex,pdf,md}  ← position-specific tailored resume snapshots;
                                   built and committed by Claude directly, never
                                   touched by CI, and never affect resume.tex
scripts/
├── tex_to_pdf.py         ← compile a .tex file to PDF (latexmk/pdflatex)
└── tex_to_markdown.py    ← convert a .tex file to the house-style Markdown
```

## Resume vs. CV

- **Resume** (`resume.tex`): curated, concise, target length 1.5–2.5
  pages. Bullets are selected and worded for impact against a target
  job/domain. Older or less relevant experience may be trimmed.
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

### Parallel open PRs and the PDF-timestamp conflict
`pdflatex` embeds a build timestamp in every PDF it produces, so two
independent CI builds of the *same unchanged* `.tex` source still produce
byte-different `resume.pdf`/`cv.pdf`. This creates a predictable, fake
merge conflict whenever more than one PR is open at once:

1. PR A merges into `main`, carrying its own freshly CI-built PDFs.
2. Any other open PR (PR B) that already has its own CI-built PDFs now
   diverges from `main` at the binary level, even if the underlying
   `.tex` content never conflicts. GitHub reports this as a real merge
   conflict (`mergeable_state: "dirty"`) on `cv.pdf`/`resume.pdf`.

This is expected, not a sign anything went wrong. When it happens (the
user will typically see "This branch has conflicts that must be
resolved" on the PDF files), resolve it directly rather than asking the
user to:
1. `git fetch origin main <pr-branch>`, checkout the PR branch, and
   `git merge origin/main`.
2. The conflict will land only on the binary PDFs. Never hand-pick a
   side — regenerate both fresh from source:
   `python3 scripts/tex_to_pdf.py resume/resume.tex` and
   `python3 scripts/tex_to_pdf.py cv/cv.tex`.
3. Stage the real deliverables (`resume/resume.pdf`, `cv/cv.pdf`, and
   the tracked `.build/*.log` files) — leave any untracked
   `.fdb_latexmk`/`.fls`/`.build`-copy-of-the-PDF byproducts alone, they
   don't match this repo's tracked-file convention.
4. Verify page counts still hold (`pdfinfo <file>.pdf | grep Pages`)
   before committing, then commit and push.
5. CI will re-run on the push and, since its own rebuild also gets a
   fresh timestamp, will usually add one more bot commit on top
   (`"Rebuild PDF & markdown from .tex sources"`) — this is normal and
   self-resolving, not a new conflict to chase.

When multiple PRs are open together, resolve this lazily, not
preemptively. GitHub Actions never cross-triggers between PRs on its
own — nothing rebuilds PR B just because PR A merged — so there is no
CI cost to a conflict sitting unresolved on a PR nobody is about to
merge yet. Only spend a rebuild on a PR when it's next in line:

1. If the user hasn't stated a merge order for the open PRs, ask before
   touching any of them.
2. Fix and clear the conflict only on whichever PR is merging next.
   Leave every other open PR's conflict alone, even if it's already
   showing `dirty` — fixing it now just means redoing it again once an
   earlier PR merges ahead of it and shifts `main` a second time (this
   is exactly the rework that happened resolving #8 and #10 together
   before either had merged).
3. Once that PR merges, move to whichever PR is next: re-check its
   mergeable state (it may now show a fresh conflict against the just
   -updated `main` even if it didn't before), resolve it with the steps
   above, and tell the user it's ready.
4. Repeat per PR until the queue is empty. Don't wait for the user to
   notice and report each new conflict — proactively check the next
   PR in line as soon as the previous one merges.

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

## Position-specific tailored versions

Sometimes the user wants a resume tailored to one specific job posting
without touching the stable master `resume.tex` at all — no new
experience to add, nothing to permanently reorganize, just this one
application. This is a separate path from a normal checkpoint.

1. Start a session as usual: copy `resume.tex` → `resume_draft.tex`.
   The CV is never tailored, so there's no need for `cv_draft.tex` here.
2. Tailor per the rules under Content rules below (wording, emphasis,
   and reordering only — no new claims), showing the diff for approval
   before writing each change, same as any surgical edit.
3. Once approved, don't copy the draft into `resume.tex`. Instead:
   - Copy `resume_draft.tex` to `Versions/<slug>_resume.tex`, where
     `<slug>` identifies the position clearly (company and/or role —
     e.g. `Versions/jacobs-fde_resume.tex`).
   - Run `scripts/tex_to_pdf.py` and `scripts/tex_to_markdown.py`
     against that `Versions/` copy locally, producing
     `Versions/<slug>_resume.pdf` and `Versions/<slug>_resume.md`.
   - Check the built PDF's page count. **Snapshots target 2 pages,
     stricter than the master's 1.5–2.5.** If it runs over, follow the
     Trimming to a page target loop below before going further. Don't
     cut anything yourself; per Content rules below, bullets are never
     removed without explicit instruction.
   - Delete the ephemeral `resume_draft.tex`/`.pdf`/`.md` as normal.
4. Commit all three new `Versions/<slug>_resume.*` files on a feature
   branch and open a PR into `main` — same as every other change, Claude
   opens it and stops there; never merge it.

CI never touches `Versions/`: the build workflow only ever rebuilds
`resume.pdf`/`cv.pdf`/`resume.md`/`cv.md` from `resume.tex`/`cv.tex`.
Versioned tailored files are built and committed by Claude directly, and
stay fixed once merged until a future re-tailoring request updates them.

The user only downloads and uses resumes from `main` — never a
locally-generated file handed over outside of git — so even though a
tailored version doesn't touch the master, it still goes through the
same commit-and-PR path as everything else, not just a chat attachment.

If, instead, the user decides a tailored draft should *become* the new
master (rather than live as its own `Versions/` entry), that's just a
normal checkpoint: copy the draft into `resume.tex` as usual.

### Trimming to a page target

Whenever a resume — master or a `Versions/` snapshot — needs to come
back within its target, this is the standard loop, not an ad hoc
back-and-forth:

**1. Measure by content, not by page count.** The page-count number
`pdfinfo` reports is misleading on its own: a PDF at "3 pages" might be
two full pages plus one trailing word, or two pages plus most of a
third entry — the fix is completely different in each case.
   - Run `pdftotext -layout -f <last-page> -l <last-page> <file>.pdf -`
     to see exactly what spilled onto the overflow page.
   - For a precise number, compare total non-blank line counts
     (`pdftotext -layout <file>.pdf - | grep -c '[^[:space:]]'`)
     against a known-good version at the target length — this turns
     "3 pages" into a concrete "5 lines over" or "1 word over."

**2. Present a menu, apply nothing yet.** Once the overflow is known,
propose concrete candidates before touching any file, covering both
angles:
   - **Simplify** — reword or shorten an individual bullet without
     dropping any underlying claim.
   - **Combine** — merge two or more short, thematically related
     bullets into one. This often reclaims more space than trimming
     any single bullet, since each bullet carries fixed overhead (the
     marker, the line break) on top of its content — a cluster of
     short one-line bullets is a better target than one long bullet.

   Name specific bullets and give the exact proposed wording for each
   option, so the user approves text, not a vague intention.

**3. Apply only what's approved, nothing speculative.** Never apply a
trim "to see if it's enough" and ask after the fact. Apply exactly the
option(s) the user picked. Several approved trims from the same message
can be applied together in one pass — the rule is against testing
*unapproved* options, not against batching *approved* ones.

**4. Re-verify after every apply, don't assume.** Rebuild and re-run
the same precise measurement from step 1. A wording trim frequently
lands inside existing line-wrap slack and saves nothing visible — only
a cut that crosses a wrap boundary reclaims a physical line. If the
target isn't reached yet, report the new exact remaining overflow and
repeat from step 2.

**5. Commit real progress as it happens.** A round of approved trims
that measurably improves things but doesn't yet hit the target is still
committable — commit it and continue the loop on what's left. Only
discard uncommitted work if it was never approved (e.g. a speculative
test edit made before the user weighed in).

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
