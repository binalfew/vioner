# Mission: Defend the VioNER thesis at Addis Ababa University

## Why

I am defending my Masters thesis (VioNER — Violent-event Named Entity Recognition for African news) in front of a CS panel at Addis Ababa University. The mission is to deliver a confident defense that *the integration of schema + model + KB + taxonomy + platform is the contribution*, and to handle any technical follow-up without stumbling. The work is done; what I need now is **fluent delivery and bulletproof technical defensibility** of every modelling decision.

## Success looks like

- Deliver any one of the 22 slides in the deck in 60–90 seconds without rehearsal jitter.
- Answer the top-20 most likely panel questions in one or two sentences each, without "um"-ing.
- Defend every modelling decision (focal loss, γ = 2, class weight cap at 10, BIO over BIOES, 8 entities not 26) with both the *what* and the *why this and not the alternative*.
- Hold up the ablation result (+11 F1 on VICTIM) as the empirical claim that justifies the loss-function contribution.
- Close with calm confidence, not with apology.

## Constraints

- Defense is upcoming — the highest-leverage activity is delivery fluency, not new theory.
- Background is software engineering, not ML — I need analogies and concrete examples, not parametric math.
- No first-person voice allowed in any document the panel sees (AAU CS guideline).
- I have an extensive existing defense kit: `concepts_explained.md`, `formulas_explained.md`, `experimental_results.md`, `problem_domain.md`, `solution_architecture.md`, `qa_kit.md`, the 22-slide deck and its study guide. These are the authoritative knowledge bases.

## Out of scope

- New architectural changes to the system — implementation is frozen.
- New experiments or ablation runs — results table is final.
- Multilingual extension, learned taxonomy classifier, CRF on top of BERT — these are future work, defended *as future work* not pursued now.
