# Advisor Comments — Reference

Source: `thesis-commened.docx` (16 comments by *Accreditation*, dated
2026-05-20 and 2026-05-23). This file captures every comment verbatim,
the location it was anchored to, the work it implied, and the
resolution applied to `thesis.md`.

Use this file as the single point of reference when checking whether a
revision pass has actually closed an advisor item.

| ID | Anchor                                                                 | Comment (verbatim)                                                                                                                  | Resolution                                                                                                                                  |
|----|------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| C59  | Table of Contents heading                                            | Generate automatically                                                                                                              | TOC is a real Word `TOC` field scoped to bookmark `TOC_RANGE`. Right-click the placeholder line and choose **Update Field** on first open. |
| C418 | §4.2 high-level architecture ASCII box                                 | Draw formally - GPT based - do the same to all                                                                                      | Replaced with `figures/architecture.png`, rendered from `figures/architecture.dot` via Graphviz.                                            |
| C438 | §4.2 sequence-of-calls ASCII diagram                                   | SAME COMMENT. define it as process flow                                                                                             | Replaced with `figures/process_flow.png` (Graphviz), framed as a process-flow with numbered steps.                                          |
| C444 | §4.3 BIO encoding example                                              | Properly … why it is bag of words … and how is it extracted                                                                         | Added a "Why BIO" subsection explaining the choice over BIOES/IOB1 and an "Extraction procedure" paragraph that walks the gold-standard label assignment end to end. |
| C453 | §4.4 VIOLENT EVENTS TAXONOMY ASCII tree                                | Please provide figure and generic definition - what are the component of your taxonomy - i.e. what is a node and how is it related with other | Replaced with `figures/taxonomy_summary.png` and added a "Taxonomy graph definition" paragraph defining node, edge, level, and leaf semantics. |
| C469 | §4.6 Algorithm 4.1 prose lead-in                                       | For each algorithm, you have to provide us textual description about what it does … (to make it easy to read - add line number and explain code block about what it does) | Every algorithm now has a prose lead-in, numbered lines, and a per-block explanation paragraph after the code listing.                      |
| C470 | "Algorithm 4.1: Sub-word label alignment for BIO tagging" caption      | Algorithm label should be at the top not bottom                                                                                     | All five algorithm captions moved above the code listing.                                                                                   |
| C472 | Table 4.5: Training hyperparameters                                    | How do you set values for the parameters                                                                                            | Added a "Choice of hyperparameter values" paragraph explaining the source of each setting (BERT-base defaults, prior NER work, empirical grid). |
| C478 | §4.7 Algorithm 4.5 (post-NER 5W1H structuring)                         | Make it formal. Where is the body of the algorithm                                                                                  | Rewrote Algorithm 4.5 with a formal Input/Output/Procedure structure, numbered lines, and a closing explanatory paragraph.                  |
| C510 | §5.8 Containerised Deployment heading                                  | Not needed                                                                                                                          | §5.8 deleted; the §5 chapter overview was updated to remove the cross-reference; TOC entry removed.                                         |
| C531 | §6.3 training/validation loss ASCII chart                              | This should be in tabular format                                                                                                    | Replaced with Table 6.5b (Per-epoch loss values).                                                                                           |
| C532 | §6.3 validation accuracy ASCII chart                                   | Do the same                                                                                                                         | Replaced with Table 6.5c (Per-epoch validation accuracy).                                                                                   |
| C625 | §6.9 End-to-End Demonstration opening (and applies globally)           | I am sure you did not check the guideline as use of personal pronoun is not allowed. …                                              | Global sweep: every `I/we/my/our/me/us` recast in impersonal/passive voice. This reverses the prior humanisation pass.                      |
| C663 | §6.11 location-entity confusion matrix (ASCII grid)                    | Table                                                                                                                               | Replaced with Table 6.11 (Confusion patterns between location entity types).                                                                |
| C747 | Annex B: Hierarchical Taxonomy of African Violent Events               | Show in the events in hierarchical manner - graph                                                                                   | Added `figures/taxonomy_annex.png` (full-detail Graphviz hierarchy) at the top of Annex B; the original prose list is retained below as a flat reference. |
| C915 | Annex D: System Screenshots                                            | ??? I don't see screenshots                                                                                                         | Captured six application screens with Playwright (Login, Training, Inference, Events, Analytics, KB) and embedded in Annex D.               |

---

## Cross-cutting notes

* The first-person rewrite (C625) is **the largest single edit** in this
  pass — roughly every other paragraph in chapters 1-7 contained at
  least one personal pronoun. The previous "humanisation" iterations
  were rolled back to comply with the AAU CS guideline.
* All new figures live under `backend/docs/thesis/figures/` with their
  source `.dot` / `.py` checked in so they can be regenerated.
* The build script `build_thesis.py` now passes images through pandoc
  unchanged; no extra wiring was needed.
