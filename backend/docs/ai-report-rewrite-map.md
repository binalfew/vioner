# Turnitin AI Report — Flagged-Passage Map and Rewrite Plan

Source: `AI Similarity.pdf` (submission trn:oid:::1:3591348584, 30% / 124 segments, 0% AI-paraphrased).
Page numbers below are **thesis** page numbers (the report's own pages are offset by ~15).

The flagged material falls into three buckets. Bucket C is where the score actually
lives and where hand-rewriting pays off. Bucket A is evidence the detector is blunt —
raise it with the advisor rather than rewriting.

---

## Bucket A — Boilerplate false positives (do NOT rewrite; discuss with advisor)

These are flagged but are either mandated wording or non-authorial reference text:

- **Signed Declaration Sheet** (p.80) — the fixed AAU template sentence is flagged as AI.
- **Dedication + Acknowledgements** (p.i–ii) — flagged in full.
- **Acronym expansions** (p.x–xi) — e.g. "Bidirectional Encoder Representations from
  Transformers", "Politically Motivated Violent Events (ontology)".
- **Annex F questionnaire items** (p.78–79) — standard Likert/task wording.
- **Annex C table cells** (p.71) — armed-group aliases ("al-shabab, al shabaab…").
- **Demo case inputs** in 6.9 (p.51–52) — short synthetic news sentences.

These alone are several hundred words of the 30%. The advisor should see that the
metric includes the university's own declaration template.

## Bucket B — Enumerated / parallel-structure lists (restructure, don't paraphrase)

The detector keys on runs of identically-shaped bullets. Fix by varying structure:
merge some bullets into prose, vary openers, fold pairs together — not by synonym swaps.

| Location | Pages | What's flagged |
|---|---|---|
| 1.4.2 Specific Objectives | 5–6 | nearly all ten bullets |
| 1.6.2 Out of Scope | 8 | intro line + most bullets |
| 4.8 API route groups | 36 | most `/api` bullets + closing line |
| Annex A guidelines | 65–66 | most Include/Exclude lists |
| Annex D screenshot captions | 73 | D.1–D.4 captions |

## Bucket C — Authorial prose blocks (the real target: rewrite these yourself)

Highest-yield first. ≈ word counts are for the flagged portion only.

### Priority 1 — large contiguous blocks (~3,800 words total)

| Section | Pages | Flagged content |
|---|---|---|
| 7.1 Summary | 57 | "What was built, in one paragraph…", "What the numbers say…", "The ten specific objectives…" — three full paragraphs (~330 w) |
| 6.11 Error Analysis | 53–54 | opening + the 38% / quarter / 19% / 7% pattern paragraphs + "The error analysis motivates three…" (~400 w) |
| 6.10 User Acceptance Testing | 52–53 | opening paragraph, "All five completed…", "Constructive feedback focused on three points…" (~250 w) |
| 6.3 Training Dynamics commentary | 47 | "Two observations stand out…" and "Convergence this fast…" — both full paragraphs (~260 w) |
| 4.1 Design Principles | 23–24 | intro + principles 1, 3, 4, 5, 6 ("The first is… The sixth is…") (~450 w) |
| 4.5 Knowledge Base Design | 30 | first three paragraphs (~280 w) |
| 5.4–5.6 Implementation | 40–41 | 5.4 second para, 5.5 nearly全部 (incl. "Ignored positions…", "Class weights are computed…"), 5.6 opener (~430 w) |
| 5.7–5.8 Frontend / Deployment | 42–43 | "The Training screen lists… Annex D.", 5.8 first para + env-variables sentences (~300 w) |
| Ch.5 opener | 37 | whole intro paragraph (~70 w) |
| Ch.1 §1.1–1.2 | 1–3 | Ch.1 opener, 1.1 first para, "While these initiatives…", "The AU-CEWS operates…", "Individually these are small judgements…", "The two gaps interact…", "A vanilla cross-entropy…", "The third is more architectural…", "The shape of the thesis…" (~550 w) |
| 2.1 Information/Event Extraction | 11 | first three paragraphs (~300 w) |
| 6.12 Discussion | 54–55 | opening paragraph + "The second finding…" opener + "That makes the reported metrics…" (~250 w) |

### Priority 2 — scattered single paragraphs / sentences (~1,500 words total)

- 1.3 operational packaging sentence ("A trained model on its own is not an operational capability…") — p.4
- 1.5 Methods: "The work begins with the annotation schema…" block — p.6
- 1.8 Organization: "After that, two chapters cover…", "Evaluation comes next." — p.10
- 2.3: DistilBERT/XLM-RoBERTa sentences — p.14
- 2.4 opener: "NER under BIO is, almost by construction…" — p.14
- 3.4: "The extra depth costs some classification accuracy…", "A learned hierarchical classifier could in principle…" — p.20
- 4.2 closing: "The boundary between extraction (NER) and post-processing is deliberate…" — p.25
- 4.3 opener + "The grounding rule (Section 4.1) does most of the work…" — p.25–26
- 4.4 closing sentence ("A learned hierarchical classifier could replace…") — p.29
- 4.6 intro tail + 4.6.1 Preprocessing paragraph (fully flagged) — p.31
- 4.6.5 Training Hyperparameters paragraph (fully flagged) — p.32
- 4.6.6 first two sentences — p.33
- 4.7: "Confidence thresholds are calibrated per category…" — p.35
- 5.1 tail: "On the front end, React 19…" — p.38
- 5.2 opener: "ACLED publishes its data through an open API…" — p.38
- 6.2: dataset caption sentences, "The substantive story is in the entity-level distribution…", "One level up, the imbalance worsens…" — p.44–45
- 6.4 opener — p.48
- 6.5: "ACTOR, CITY, and DATE form a strong cluster…" — p.49
- 6.6: "Each ingredient helps on its own…" — p.50
- 6.13 opener — p.55
- 7.4: "First, treat the extraction output as a triage layer…" (full para), "Second, keep the knowledge base alive." — p.59–60
- 6.9: "Cases 1 and 2 demonstrate…" closing paragraph — p.52
- Annex B/C/D intro sentences — p.67, 71, 73
- Figure captions 6.1, 6.2 and Table 6.3/6.5 captions — p.46–47

### NOT flagged (leave alone — don't touch these)

Abstract; 1.3 problem statement body; 1.4.1; 1.6.3 Limitations; 1.7; Ch.2 §2.2, 2.5,
2.6, 2.7; Ch.3 §3.1–3.3, 3.5 + Table 3.1 bullets; 4.2 body; 4.4 body; 4.6.2–4.6.4,
4.6.7; 4.7 body; 5.3; 6.1; 6.7; 6.8; 6.13 body (internal/external/conclusion validity);
7.2 (all four RQ answers); 7.3; 7.5; References; Annex B taxonomy tree; Annex E.

---

## Rewrite method (per block, in your own words)

1. Read the flagged block once. Close the file.
2. Say the content out loud as if answering an examiner — record or type what you said.
3. Replace the block with what you actually said, then restore precision (numbers,
   section cross-references, citation markers) by checking — not copying — the original.
4. Break the rhythm deliberately: one short sentence per paragraph; merge two bullets
   into one prose sentence; start one sentence with a subordinate clause.
5. Add one concrete first-hand detail per major block (what failed, what surprised you,
   why you chose the threshold) — autobiographical specifics rarely flag.

Work order: 7.1 → 6.10/6.11 → 4.1 → 5.4–5.8 → Ch.1 → 2.1 → the Priority-2 list.
Re-check after the Priority-1 pass; you may already be under 20% before touching
Priority 2.
