# VioNER Defense — Slide Deck

Reproducible Marp-based defense slide deck for the M.Sc. thesis
*Knowledge Discovery from Free Text: A BERT-Based System for Extracting
Violent-Event Information from African News Reports*.

## Contents

| File | Purpose |
|:--|:--|
| `slides.md` | Source of truth — 26 main slides + 12 backup, with speaker notes inline as HTML comments. |
| `theme.css` | Custom Marp theme (navy + amber editorial palette, projection-safe type sizes). |
| `build_slides.py` | Build script — wraps marp-cli, emits `slides.pptx` and `slides.pdf`. |
| `speaker_notes.md` | Standalone full talking script (≈ 120-150 words per slide). Print double-sided for rehearsal. |
| `qa_kit.md` | 15 anticipated panel questions with prepared answers and backup-slide flips. |
| `assets/` | Symlinks to figures and screenshots from `../thesis/figures/`. |
| `slides.pptx` | Generated — editable in PowerPoint. (Created by build.) |
| `slides.pdf` | Generated — safe projector fallback. (Created by build.) |

## One-time setup

Marp uses the `marp-cli` tool, which is a Node.js package:

```bash
npm install -g @marp-team/marp-cli
```

Verify the install:

```bash
marp --version
```

## Build the deck

From this directory:

```bash
python build_slides.py
```

This produces both `slides.pptx` (editable, speaker notes preserved) and
`slides.pdf` (projector fallback).

Other modes:

```bash
python build_slides.py --pptx-only   # just the PPTX
python build_slides.py --pdf-only    # just the PDF
python build_slides.py --watch       # rebuild PPTX on slides.md change
```

## Edit the slides

`slides.md` is plain Marp markdown. Each slide is separated by `---`.
Speaker notes are HTML comments (`<!-- ... -->`) and flow into the
PowerPoint speaker-notes pane.

Slide-class hooks defined in `theme.css`:

| Class marker | Variant |
|:--|:--|
| `<!-- _class: title -->` | Title and final-thanks slides |
| `<!-- _class: divider -->` | Section dividers |
| `<!-- _class: stat -->` | Hero-stat slide (one big number) |
| `<!-- _class: two-col -->` | Two-column layout |
| `<!-- _class: backup -->` | Backup-deck dividers |

To add a slide, copy an existing one and edit. To re-order, cut and paste
between `---` markers. Page numbers regenerate automatically.

## Print the speaker notes for rehearsal

```bash
# Render speaker_notes.md to PDF for printing
pandoc speaker_notes.md -o speaker_notes.pdf \
    -V geometry:margin=0.75in \
    -V fontsize=11pt \
    -V mainfont="Source Sans 3"
```

Print double-sided. Each slide gets its own block; tab the printout to
slide numbers so you can find sections during rehearsal.

## Rehearsal pacing target

| Checkpoint | Slide | Target elapsed |
|:--|:--|:--|
| Outline complete | 2 | 1:15 |
| Problem section done | 5 | 4:30 |
| RQs presented | 7 | 6:30 |
| Approach section done | 20 | 18:30 |
| Headline result delivered | 22 | 19:30 |
| UAT delivered | 29 | 24:00 |
| Contributions | 31 | 25:30 |
| Thanks | 34 | 27:00 |

If you hit slide 22 by minute 22 you are running 3 min slow — tighten
transitions, drop one example per remaining slide.

## Re-generating assets

The figures and screenshots are symlinked from `../thesis/figures/`. To
regenerate them after editing:

```bash
# from project root
cd backend/docs/thesis/figures
python build_figures.py        # taxonomy, architecture, process flow
python build_screenshots.py    # 7 Annex D UI mockups
```

The symlinks in `assets/` will pick up the regenerated PNGs automatically.

## Defense-day checklist

- [ ] Test projector connection 30 minutes early
- [ ] Both `slides.pptx` AND `slides.pdf` open and ready
- [ ] Speaker notes printed double-sided, tabbed
- [ ] Water bottle
- [ ] Phone on silent
- [ ] First sentence of each slide memorised (the openings, not the whole notes)
- [ ] Q&A kit reviewed the night before (not the morning of)
