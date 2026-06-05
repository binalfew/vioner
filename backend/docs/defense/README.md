# VioNER Defense — Slide Deck

Reproducible Marp-based defense slide deck for the M.Sc. thesis
*Knowledge Discovery from Free Text: A BERT-Based System for Extracting
Violent-Event Information from African News Reports*.

## Contents

| File | Purpose |
|:--|:--|
| `slides.md` | Source of truth — 31 main slides + 12 backup, with speaker notes inline as HTML comments. |
| `theme.css` | Custom Marp theme (navy + amber editorial palette, projection-safe type sizes). |
| `build_slides.py` | Build script — wraps marp-cli, emits `slides.pptx` and `slides.pdf`. |
| `speaker_notes.md` | Standalone full talking script (≈ 120-150 words per slide). Print double-sided for rehearsal. |
| `qa_kit.md` | 41 anticipated panel questions with prepared answers and backup-slide flips. |
| `formulas_explained.md` | Every formula in the thesis (focal loss, class weights, F1, Cohen's κ, …) explained term-by-term with worked numeric examples. |
| `problem_domain.md` | Study guide for the problem statement — stakes, current solutions, the four-part gap, and how VioNER closes it. Includes per-system gap analysis, three elevator pitches, and Q&A scripts for problem-statement defense. |
| `solution_architecture.md` | Study guide for the solution side — what VioNER is, the design-science methodology, the conceptual and technical contributions, the four-layer architecture, the trade-offs, the three iteration loops, and Q&A scripts for solution-and-architecture defense. |
| `experimental_results.md` | Study guide for Chapter 6 — every table and number explained in plain English with worked examples. Walks through F1 calculations, the ablation table row by row, KB operational metrics, UAT scores, and error analysis. Includes Q&A scripts for results-defense and a quick-reference table for every number on every slide. |
| `concepts_explained.md` | Beginner glossary — every ML/NER jargon term in the thesis explained with a one-sentence definition, a real-world analogy, a worked example, and what panellists mean when they say it. Covers F1, cross-entropy, focal loss, BERT, BIO encoding, epoch, val loss, Cohen's κ, and ~30 other concepts. One-page cheat sheet at the end. |
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

31 main slides + section dividers, ≈29 minutes inside the 30-min slot.

| Checkpoint | Slide | Target elapsed |
|:--|:--|:--|
| Outline complete | 2 | 1:15 |
| Cost-of-pipeline slide done | 5 | 4:00 |
| Day-in-life narrative done | 6 | 5:30 |
| Problem section done | 7 | 7:00 |
| RQs presented | 9 | 8:45 |
| Methodology delivered | 10 | 10:20 |
| Related work + gap done | 14 | 14:30 |
| Approach section done | 25 | 23:00 |
| Headline result delivered | 27 | 24:00 |
| UAT delivered | 34 | 27:00 |
| Contributions | 36 | 28:00 |
| Thanks | 39 | 29:30 |

If you hit slide 27 by minute 25 you are running 1 min slow — tighten
transitions, drop one example per remaining slide. If by minute 27, drop
a backup-card flip and shorten the future-work commentary.

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
