# Rewrite Worksheet — Priority-1 Flagged Blocks

How to use each card:
1. **Don't reopen the flagged paragraph.** Work only from this card.
2. Read the *Facts to cover*. Answer the *Say it* prompt out loud, as if Dr. Fekade
   asked it in the defense. Record yourself or type while talking.
3. Paste your spoken version into the docx in place of the old block.
4. Check every number against the Facts list (they're verbatim from your Chapter 6).
5. Rhythm check: at least one sentence under 8 words; no two consecutive sentences
   starting the same way; no "The first is… The second is…" chains.

When a card is done, tick it. Send me the new text and I'll verify numbers and
cross-references against the rest of the document.

---

## ☐ 1. Section 7.1 — "What was built" paragraph (p.57)

**Facts to cover (telegraphic, not prose):**
- 8-entity grounded schema: ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES — BIO format
- 4-level taxonomy, ~95 terminal categories; sources: ACLED + UCDP + PMVE + African-specific extensions
- 50,000-example corpus from ACLED notes; stratified diversity sampling + template augmentation; skewed label distribution
- bert-base-cased fine-tune; focal loss γ=2; inverse-frequency class weights
- KB: ~150 armed groups, ~200 conflict cities, 54 countries with regions
- FastAPI service (training, inference, events, analytics, KB admin) + React/TypeScript front-end + Docker Compose

**Say it:** "In one minute, what did you actually deliver?" — answer as inventory,
but in your voice. Try organizing it differently from the original (e.g., model → data
→ knowledge → platform, or start from the platform and work down).

## ☐ 2. Section 7.1 — "What the numbers say" paragraph (p.57)

**Facts:**
- macro F1 0.887, micro F1 0.909, held-out validation
- best val loss at epoch 2; overfits after; early stopping catches it
- focal + class weights: VICTIM +11 F1 points, ACTION +7 vs plain CE
- KB canonicalises ~2/3 of high-confidence ACTOR spans (64.3%); flags ~1 in 40 multi-entity events (2.4%) geographically implausible
- inference: hundreds of ms per article
- UAT mean 4.4/5 across six task dimensions

**Say it:** "Give me the headline numbers and what each one means for an analyst."

## ☐ 3. Section 7.1 — "ten specific objectives" sentence (p.57)

**Facts:** objectives of §1.4 addressed: Ch.2 lit review; Ch.4+5 schema/taxonomy/data/
training; §4.5+5.6 KB; §5.6+5.7 back/front-end; Ch.6 evaluation; §1.6+Ch.7 limitations.

**Say it:** One or two sentences mapping objectives → chapters, in any order you like.

## ☐ 4. Section 6.11 — Error Analysis (p.53–54, four pattern paragraphs + closer)

**Facts:**
- method: 300 validation events with ≥1 mistake, read individually; 5 patterns by frequency
- ~38%: boundary mismatch — right type, wrong span ("at least 12 civilians" → "12 civilians"); mostly VICTIM/CASUALTIES; strict scoring counts these as full misses
- ~25%: location-type confusion REGION↔CITY↔DISTRICT; Goma = city AND de-facto centre of North Kivu; model defaults to CITY
- ~19%: missed entities — unusual victim phrasings ("Christian worshippers", "internally displaced schoolgirls"); passive-voice verbs ("were ambushed")
- ~12%: spurious entities — vague WHEN ("this morning", "earlier") tagged DATE; threshold 0.85 would remove most at ~1.2 F1 recall cost
- ~7%: confidence drops just below category threshold
- feeds future work: span-level CRF boundary refinement; KB facts as training features; negative WHEN examples (§7.5)

**Say it:** "Walk me through how your model fails." Tell it like a story of reading
300 errors — what you expected to find and what you actually found.

## ☐ 5. Section 6.10 — User Acceptance Testing (p.52–53)

**Facts:**
- n=5: 2 early-warning analysts (primary), 1 academic conflict researcher, 2 NLP-familiar developers (interface sanity check)
- deployed instance; 6 tasks: inference on 3 articles, browse events, analytics query, train model, monitor run, review flagged event
- all 5 completed all 6; Likert results Table 6.10; full questionnaire Annex F
- feedback: want exportable PDF brief; drag-and-drop upload; per-entity metrics during training → last two scoped into Ch.7

**Say it:** "Who tested it, what did they do, and what did they ask for?"

## ☐ 6. Section 6.3 — training dynamics commentary (p.47, two paragraphs)

**Facts:**
- val loss bottoms at epoch 2 then rises while train loss falls = overfitting; early stopping patience 5, threshold 0.001
- subtle bit: token accuracy keeps rising after val loss worsens — focal loss makes model more confident on already-correct examples (lifts accuracy) while calibration on minority boundaries degrades (raises loss)
- reading both curves set the patience value; accuracy alone → longer run, worse model
- 2-epoch convergence expected: BERT pre-training does most of the work; 50k corpus saturates the fine-tuning signal fast

**Say it:** "Your validation loss goes up but accuracy goes up too — explain." (You
rehearsed exactly this for slide 16.)

## ☐ 7. Section 4.1 — Design Principles (p.23–24; principles 1, 3, 4, 5, 6 + intro)

**Facts:**
- six principles; some upfront, some emerged during development
- (1) grounded supervision: entity must be findable verbatim by an annotator on a reliable majority of occurrences; November pilot killed EVENT_TYPE ("ambush" vs "raid" — inferred, not written) and COUNTRY (implied by city); grounding rates < 60%; both moved to post-NER
- (3) hybrid statistics + knowledge: model generalises surface forms (ENDF = Ethiopian National Defense Force = Ethiopian troops); KB does lookups (Beledweyne → country), canonicalisation, geographic plausibility
- (4) confidence first-class (emerged in UAT): per-span confidence from averaged sub-token softmax; category thresholds (DATE 0.80, WHAT 0.60); shown on hover; hiding uncertainty = analyst trusts a wrong casualty figure
- (5) operational packaging: not a notebook; documented HTTP API, UI on top, one Docker Compose command; usable without Python
- (6) reproducibility as working discipline: datasets/runs/deployment rebuild from scripts; seeds fixed where possible, random state logged where not

**Say it:** One principle at a time: "Why is this a rule in your system, and what
happened that made it one?" Vary the framing per principle — story for one,
consequence-first for another. Avoid numbering language entirely.

## ☐ 8. Section 4.5 — Knowledge Base Design (p.30, first three paragraphs)

**Facts:**
- in-memory KB beside the model; three dictionaries: armed groups, locations, weapons
- PostgreSQL-at-startup considered, rejected: lookup volume high at inference, in-memory wins on latency; cost = edits need service restart (§5.6 handles gracefully)
- groups: ~150 entries; canonical name, news aliases, country, region (E/W/N/S/Central), type {militia, terrorist, rebel, government}; favours currently-active groups (Al-Shabaab, Boko Haram, M23, RSF, JNIM, ISGS, Wagner, ENDF, TPLF); full list Annex C
- locations: ~200 conflict cities + all 54 countries + primary regions; city → country + parent admin unit (Maiduguri → Nigeria/Borno; Goma → DRC/North Kivu; Mogadishu → Somalia/Banaadir); CITY spans auto-enriched at inference

**Say it:** "What's inside the knowledge base and why is it in memory?" (Your slide-13
two-guarantees rehearsal covers this.)

## ☐ 9. Sections 5.4–5.6 — training loop, loss code, backend (p.40–41)

**Facts (5.4 ¶2):** dataset class: tokenizer with is_split_into_words, word indices,
Algorithm 4.1 alignment; -100 ignored by both CE and focal; loop: forward-backward,
no-grad validation per epoch, grad clip L2 1.0, linear warm-up then ReduceLROnPlateau
(0.5, patience 2); early stop counts epochs since improvement; resume + extend-epochs.

**Facts (5.5):** two classes: FocalLoss (Alg. 4.4) + class-weighted CE (ablation
baseline §6.6); logits [N,C], targets [N], flattened pre-softmax (contiguous 2D faster);
-100 masked BEFORE softmax (numerical stability with padding); smoothing applied to
target distribution, focal modulator respects smoothed label; per-class weights = 1D
tensor on logits' device; w_c = T/(C·max(f_c,1)), f_c clipped ≥1; O-class weight logged;
Annex E has distribution + weights.

**Facts (5.6 opener):** FastAPI app, route handlers by feature; Figure 5.1 module map:
entry point → routers → services → pipeline → DB.

**Say it:** "Open the training file and tell me what happens, in order." You wrote
this code — narrate it the way you'd walk a colleague through it, with the one or two
gotchas you actually hit (e.g., why mask before softmax).

## ☐ 10. Sections 5.7–5.8 — screens & deployment (p.42–43)

**Facts (5.7):** Training screen: run list + control panel; detail view subscribes to
WebSocket — live progress bar, current epoch, recent losses, scrolling log. Events
screen: paginated, full-text search, filters (date, country, region, taxonomy level),
CSV export. Analytics: events per region, top actors/locations, time series, casualty
totals. KB screens: role-gated CRUD on groups/locations/taxonomy, mutations audited.
Screenshots Annex D.

**Facts (5.8):** one Compose file, three services: Postgres 16 + volume; Python
back-end with model checkpoint mounted; Node front-end building/serving Vite. Health-
checked startup order (DB first). Env-driven config: DATABASE_URL, model path, CORS
origins, JWT secret, feature flags; example env file in repo.

**Say it:** "Demo the app to me without touching the keyboard" / "How do I stand this
up from a clean machine?"

## ☐ 11. Chapter 5 opener (p.37)

**Facts:** Ch.4 = what/why; Ch.5 = how: stack, data prep, training, focal-loss code,
backend+API, frontend, containerised deployment; code listings short, full source in repo.

**Say it:** Two sentences, your phrasing. Maybe kill the symmetry with Ch.4 entirely.

## ☐ 12. Chapter 1 — opener, 1.1 ¶1, and the gap paragraphs (p.1–3)

**Facts (opener + 1.1 ¶1):** three pressures: news volume on African violent events
grows faster than analyst reading capacity; early-warning depends on timely conversion
to structured records; chapter covers background → motivation → problem → objectives →
methods → roadmap. Sources: wire services, mainstream outlets, regional papers, online
media [1].

**Facts (1.2 gap paragraphs):** consistency gap: two analysts diverge on small
judgements ("violence against civilians" vs "battle"; city vs district; attribute
fatality or mark unknown); aggregated weekly → trend analysis unreliable (was the spike
real or new shift coding differently?). The two gaps interact: more analysts widens
consistency gap; tighter coding rules slows everyone, widens throughput gap; ML system
pushes on both at once.

**Facts (three observations, ¶ "A vanilla cross-entropy…" and "The third is more
architectural…"):** vanilla CE under-recovers rare classes while accuracy looks high;
focal loss [12] + inverse-frequency weights = standard counter; §6.6: VICTIM +11 F1.
Architectural: untrusted extraction adds load; minimum bar = auditable output — which
text, what confidence, does actor/location match a known referent; KB provides audit
trail + catches plausible nonsense (M23 attacking Maiduguri, RSF in Mozambique).
Thesis shape: academic = model + dataset + 4-level taxonomy; practical = web app.

**Say it:** This is your motivation story — the morning queue at AU-CEWS. Tell it
fresh; don't echo the old paragraph structure. The unflagged 1.2 paragraphs around
these already carry your voice — match them.

## ☐ 13. Section 2.1 — first three paragraphs (p.11)

**Facts:** IE = umbrella (NER, relation extraction, coreference, event extraction);
pipeline vs joint/end-to-end; thesis picks pipeline — debuggability beats marginal
accuracy at this scale; §4.2 concretises. Event extraction: Ahn's definition [3] —
verb/nominal predicate + participants + location + time; ACE [14] formalised typology
early 2000s; TAC-KBP continued with larger benchmarks. 5W1H frame [15]: sidesteps
event-type enumeration by asking six questions; near-perfect fit for news (journalists
trained to answer them in first paragraph); thesis adopts 5W1H, defers event-type to
post-NER taxonomy (§4.4) — keeps fixed inventory out of the supervised problem.

**Say it:** "Position your work inside information extraction in 60 seconds."

## ☐ 14. Section 6.12 — Discussion opener (p.54–55)

**Facts:** most important retrospective finding: dropping EVENT_TYPE + COUNTRY was
right; proposal had 26 types; November grounding pilot: EVENT_TYPE matched source text
only sporadically (analysts inferring, not reading); 8 grounded entities trained well;
dropped two recovered cheaply downstream (verbs+taxonomy classifier; single KB lookup);
26-type schema would let rare types drag everything. Also flagged: "That makes the
reported metrics a fair estimate of in-distribution performance…" → augmented examples
in both splits; no guarantee on out-of-distribution (translated, citizen journalism,
social media); §7.5 prioritises real-news expansion to find where estimate breaks.

**Say it:** "Looking back, what call mattered most, and what's the honest caveat on
your numbers?"

---

## List-shaped fixes (Bucket B) — structural notes, no card needed

- **1.4.2 Objectives:** collapse 10 parallel bullets into ~5 grouped sentences or vary
  each opener (verb-first / outcome-first / constraint-first). Keep all deliverables.
- **1.6.2 Out of Scope:** turn the bullet list into a short prose paragraph naming the
  exclusions and the one-line reason each is excluded.
- **4.8 API routes:** present routes as a table (path | purpose) — tables aren't
  flagged — or fold into two prose sentences.
- **Annex A:** keep Include/Exclude semantics but vary sentence shape per entity;
  or convert to two-column tables.
- **Annex D captions:** one clause each, varied structure.

## After each pass

Re-export the PDF, resubmit if your institution allows draft checks, and send me the
rewritten sections. I check: every number against Tables 6.3–6.10, cross-references,
terminology consistency (e.g., "bert-base-cased", "ACLED notes", entity names in caps),
and that nothing in the unflagged text now contradicts your new wording.
