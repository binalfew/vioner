# Teaching preferences (observed across sessions)

## Learning style

- **Analogies first, math second.** Theory lands when grounded in a concrete real-world parallel (drug trial → ablation baseline; dimmer switch → focal factor; classroom of 100 students → focal weighting).
- **Worked numerical examples beat abstract formulas.** Always show the arithmetic with real VioNER numbers — never leave a formula floating without numbers underneath.
- **Build up step by step.** Avoid dropping notation (Σ, subscripts, multiple symbols at once) without explaining each piece first.
- **Carry one running example through related material.** Don't switch examples mid-thread — it breaks tracking.

## What confuses

- New jargon used before it's defined (e.g., using "F1" before introducing F1, using "class" without saying class = label).
- Compound formulas without component breakdown (each symbol needs a name first).
- Procedure lists without WHY for each step (the rationale matters more than the steps).

## What works

- "Why each ingredient solves a specific problem" framing for compound concepts.
- Stage-based maps (annotation → training → validation → inference) — anchors what's used where.
- "What would go wrong without this step?" sub-bullets — makes the rationale concrete.
- Defense-day one-sentence delivery scripts at the end of each section.

## Style preferences

- Tables liberally for comparison, decision rules, anticipated questions.
- Direct, concrete sentences over hedge-heavy academic prose.
- No emoji in written material.
- Pretty, printable HTML for lessons (serif body, generous whitespace, clean math typography).

## Full-deck recital script

Lesson 0020 (`lessons/0020-full-deck-speaker-notes.html`) is the single word-for-word recital script for all 22 slides — scripts only, no coaching, pivots included, ~28 min total. The user explicitly asked for "no fuss" recitable speaker notes; keep that document free of meta-commentary if it's ever updated. Coaching meta-lines from the study guide ("If asked...", "Defend the small size:", "Close with calm confidence") were stripped or naturalised into spoken form.

## Slide-numbering source of truth

The user's deck follows `backend/docs/defense/VioNER_Defense_Slides_study_guide.md` — NOT `slides.md` or `speaker_notes.md`. Those latter two are an older/longer deck that includes BIO encoding, system architecture, and pipeline as standalone slides. The study-guide deck is the 22-slide version actually being delivered. **Always confirm slide content against the study guide before building a lesson.**

Verified mapping from study guide:
- 10 = grounding-validated 8-entity schema
- 11 = 4-level taxonomy AND the corpus (50k = 35k stratified ACLED + 15k augmented)
- 12 = training recipe (focal × class weights — complementarity claim)
- 13 = curated knowledge base
- 14 = the platform
- 15 = inference pipeline (worked example)
- 16 = headline results
- 17 = per-entity F1
- 18 = the ablation
- 19 = KB operational impact and user testing
- 20 = error analysis
- 21 = limitations
- 22 = five contributions (close)
