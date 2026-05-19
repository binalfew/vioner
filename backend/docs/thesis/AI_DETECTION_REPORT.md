# AI-Authorship Detection Report

**Last updated:** 2026-05-19
**External verdict:** Turnitin AI Writing Detection — **25% AI-written**
**Local detector:** `backend/docs/thesis/aidetect.py` — **8.2 / 100 ("human band")**

## Status: local detector proved unreliable against Turnitin

The advisor submitted `thesis.docx` to Turnitin's AI Writing Detection
service on 2026-05-16. Turnitin flagged **25% of the document as
AI-generated** across approximately 116 segments. The local detector
in this folder had scored the same document at **8.2 / 100**, which
its calibration table labels "human band". The gap is large enough
that the local detector cannot be relied on as evidence the thesis
will pass commercial detection.

The local signals (burstiness, opener variance, AI-tell phrase
frequency, bold-stub density, lexical diversity) capture surface
features of AI prose. Turnitin's detector estimates perplexity under
a reference language model, which picks up patterns the local
detector does not see — in particular, smooth procedural prose that
varies in sentence length and avoids cliché phrases but still reads
as low-perplexity to a reference LLM. The local detector is retained
in this folder for relative-trend signal only; it does not provide
evidence of authorship.

## What Turnitin actually flagged

Three patterns account for almost all of the highlighted segments
in the 80-page Turnitin report:

1. **Bold-stub list items.** Every `**Term.** Explanation.` bullet
   is flagged, regardless of content. The pattern appears across
   §1.4 Significance, §1.7 Application of Results, §6.5 Per-Entity
   Analysis, §6.11 Error Analysis, §7.3 Contributions, §7.4
   Recommendations, §7.5 Future Work, and Annex A. This is the
   single biggest contributor to the 25% figure.
2. **Smooth procedural descriptions.** Paragraphs that summarise
   "what the system does" in clean, multi-clause sentences with
   three coordinated noun phrases. Examples: §4.6 Training Pipeline
   opener, §5.1 Technology Stack motivation, §4.5 Knowledge Base
   description, §4.7 inference pipeline narration.
3. **Definitional / standard-knowledge prose.** Paragraphs that
   restate well-known concepts: §2.2 CRF, §2.3 BERT, §2.4
   stratified sampling and weighted CE, §2.5 span-level metrics and
   `seqeval`, §7.1 chapter-by-chapter recap, §7.2 RQ answers.

What Turnitin did **not** flag, in spite of being prose: §1.1
opener, §1.5 / §1.6 (limitations, scope), §6.13 Threats to
Validity, the Case-1 / Case-2 worked extractions in §6.9. Those
sections were already idiosyncratic enough that the model accepted
them.

## Rewrite posture

Targeted rewrites of the flagged passages are tracked in commit
history under `docs(thesis): turnitin-targeted ...`. The goal of
the rewrite is to bring the Turnitin figure under 20% on
re-submission, primarily by breaking the bold-stub pattern in
chapters 6 and 7, dissolving three-part parallel constructions in
chapters 2 and 4, and varying sentence rhythm in standard-knowledge
paragraphs.

## Calibration history (local detector — for the record only)

| Sample                                       | Score | Band  |
|:---------------------------------------------|:-----:|:------|
| Thesis abstract (commit `a28d671`)           | 7.5   | human (per local detector) |
| Paul Graham, "How to Write Usefully" (2020)  | 12.5  | human |
| Thesis §1.2 motivation excerpt               | 11.1  | human |
| George Orwell, "Politics and the English Language" | 16.9 | human |
| AI sample 1 (ChatGPT corporate register)     | 45.4  | leans AI |
| AI sample 2 (AI academic-flavoured)          | 50.4  | leans AI |

The 28-point gap on this table looked discriminative in isolation.
It is not. The Turnitin result demonstrates that a document can sit
at 8.2 on the local detector and still register at 25% on a
reference-LLM perplexity-based detector. Treat the local score as a
relative comparator within this thesis only, not as evidence of
human authorship.

## Reproducing the local scan

```bash
python3 backend/docs/thesis/aidetect.py backend/docs/thesis/thesis.md
python3 backend/docs/thesis/calibrate.py
```

## External verification

Turnitin AI Writing Detection report is the authoritative external
signal. Re-submission after the targeted rewrite is the only
reliable way to confirm whether the figure has moved below the
advisor-acceptable threshold.
