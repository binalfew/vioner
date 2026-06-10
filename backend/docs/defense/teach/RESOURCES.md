# Focal Loss & VioNER Defense Resources

## Knowledge — primary

- [Paper: "Focal Loss for Dense Object Detection" — Lin et al., ICCV 2017](https://arxiv.org/abs/1708.02002)
  The original focal loss paper. Source of the γ = 2 default. Use for: defending the γ choice and any "where does this come from?" question.
- [Paper: "Rethinking the Inception Architecture for Computer Vision" — Szegedy et al., CVPR 2016](https://arxiv.org/abs/1512.00567)
  Introduces label smoothing with β = 0.1. Use for: defending the label-smoothing component of the production loss.

## Knowledge — internal defense kit (authoritative for the thesis)

- [concepts_explained.md](../concepts_explained.md)
  Beginner glossary with analogies and worked examples. Section D1 has the full focal-loss treatment including the dimmer-switch intuition and class-weight composition.
- [formulas_explained.md](../formulas_explained.md)
  Full math reference. Section A.4 is the focal-loss equation with worked numbers. Section A.6 covers the production loss with smoothing.
- [experimental_results.md](../experimental_results.md)
  Walks through every Chapter 6 results table. Table 6.8 is the focal-loss ablation; the +11 F1 lift on VICTIM is documented there.
- [VioNER_Defense_Slides_study_guide.md](../VioNER_Defense_Slides_study_guide.md)
  Slide 12 covers the training recipe; slide 18 covers the ablation.
- [qa_kit.md](../qa_kit.md)
  41 prepared panel Q&A entries including focal-loss-specific defences.

## Wisdom (Communities)

- [r/MachineLearning](https://reddit.com/r/MachineLearning)
  High-signal subreddit. Good for sanity-checking how to phrase loss-function design choices in the NER literature.
- AAU CS Department — internal cohort
  Real-world: defense panel members and senior students who have defended similar work. Use for: dry-run questions, calibration on AAU panel norms.

## Gaps

- No published African NLP focal-loss baseline directly comparable. The +11 F1 comparison is internal-ablation only. If a panellist asks "where does this stand against other African NER systems?" — point to slide 6's landscape and explain why no head-to-head benchmark is currently available.
