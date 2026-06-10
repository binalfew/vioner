# Focal loss — mechanics already mastered

Across prior sessions the user has internalised the *mechanics* of focal loss: it is cross-entropy multiplied by a focusing factor $(1 - p_y)^\gamma$ that suppresses easy-correct tokens, and the production loss further multiplies by a per-class weight $\alpha_y$ and uses a smoothed target. They can walk through the worked example (Boko Haram killed civilians today) with the per-token arithmetic, and they understand the dimmer-switch intuition.

## Evidence

- Correctly identified focal loss as multiplication of CE by the focal factor (asked the question themselves and confirmed the row-by-row arithmetic).
- Understood the chain from loss → backprop → gradient → descent after the C3/C4 rewrite in `concepts_explained.md`.
- Internalised the stage map (annotation / training / validation / inference) and where each ingredient lives.
- Asked productive questions about *why* the formula has its specific shape (cap at 10, γ = 2, T/(C·f_c) not 1/f_c).

## Implications for next sessions

The gap is now **delivery fluency**, not theory. The user can *explain* focal loss but has not practised *defending* it under panel pressure. Next lessons should:

1. Compress understanding into short oral scripts (15–90 seconds).
2. Drill responses to the top 3-5 likely panel attacks on the loss choice.
3. Build a one-curve whiteboard sketch the user can produce from memory if pushed.
4. Move from "I know this" to "I can deliver this without notes."

This is the zone of proximal development for focal loss specifically.
