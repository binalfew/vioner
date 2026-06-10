# Ablation table now the focus — methodological defence, not just a result

The user has progressed beyond *understanding* focal loss (LR-0001) into the methodological territory of defending the §6.6 ablation as *empirical evidence for the loss-function contribution*. This is a different skill: explaining a controlled experiment, defending its design, and using its numbers as the empirical claim that justifies the production loss choice.

## Implications for this and future sessions

- The next lesson must distinguish between *the result* (production VICTIM F1 = 0.817) and *the evidence* (the four-row table showing each ingredient's marginal contribution).
- The complementarity inequality (row 4 > max(row 2, row 3)) is the conceptual key — it's what proves the ingredients aren't redundant.
- The statistical-significance defence (3 seeds, ±0.4 F1 variance, paired bootstrap p < 0.01) needs to land cleanly in one sentence — the user has no prior in NER statistical methodology.
- The "why these four and not more" question is the hardest of the predicted attacks; needs a structured answer that distinguishes structural ablation from sensitivity analysis.

## What this does NOT yet establish

- The user has not demonstrated mastery of the lesson-1 material in a live drill yet. If a future session shows the lesson-1 pitch isn't holding under pressure, fall back to drilling it before piling on more.
