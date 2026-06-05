# VioNER Defense — The Solution: Architecture and Methodology

A study document for understanding **how VioNER actually solves the problem**, end to end. This is the companion piece to `problem_domain.md`:

- `problem_domain.md` answers: *what's the problem, what existing systems fail to deliver, and what gaps need closing.*
- `solution_architecture.md` (this file) answers: *what VioNER is, how it's designed, how it works, and why each design choice was the right one.*

If `problem_domain.md` is the *what* and *why this thesis matters*, this document is the *how*.

---

## How to use this document

| Pass | Purpose |
|:--|:--|
| **Read 1** — full pass | Get the system into your head end-to-end |
| **Read 2** — Parts 2, 4, 5 | The methodology, the training recipe, the architecture — the technical core |
| **Read 3** — Parts 6, 7, 10 | How each piece closes its gap, the trade-offs, the defense Q&A |
| **Defence eve** — Part 1 + Part 10 | The one-page summary and the prepared answers |

Each Part stands alone. You can jump to whichever section a panel question targets.

---

# Part 1 · The solution at a glance

## What VioNER is, in one paragraph

> VioNER (Violent-event NER) is an end-to-end deployable system that takes English-language news articles about violent events in Africa and produces **structured 5W1H records** the analyst can use directly. The system has five components: an eight-entity BIO schema, a fine-tuned BERT NER model, a curated knowledge base of African armed groups and conflict locations, a four-level event taxonomy, and a web platform that lets a non-ML analyst drive the whole pipeline. The model achieves **0.909 micro F1** on a held-out validation set, with the rare-entity classes (VICTIM, ACTION, CASUALTIES) recovered well enough to actually save analyst time.

## What VioNER is *not*

To anticipate scope questions:

- It is **not** a replacement for analysts. The thesis explicitly frames the output as a triage layer that analysts review.
- It is **not** multilingual. The current system handles English-language reporting only; multilingual extension is the highest-priority future-work item.
- It is **not** a learned hierarchical event classifier. The taxonomy step is rule-based; a learned version is future work item 2.
- It is **not** a real-time streaming pipeline. Batch processing at ~150 ms per article is the current target. Streaming is lower-priority future work.

These limits are stated honestly in §1.6 and §7.5 of the thesis. Owning them is part of defending the solution.

## The end-to-end story — from article to record

Walk through what happens when an analyst pastes a single article into the inference page:

```
Article text submitted to UI
         │
         ▼  React frontend → FastAPI /api/inference route
         │
         ▼  Tokeniser (WordPiece) splits text into sub-word units
         │
         ▼  BERT forward pass → 17-label softmax per token
         │
         ▼  BIO decoder collapses contiguous B/I sequences into spans
         │
         ▼  Confidence filter drops spans below per-category threshold
         │
         ▼  5W1H grouper buckets surviving spans into WHO/WHAT/WHEN/WHERE/HOW
         │
         ▼  KB validates ACTOR–CITY pairs; enriches with canonical names
         │
         ▼  Taxonomy classifier assigns Level 1 → 2 → 3 path from ACTION verb
         │
         ▼  Event record persisted to PostgreSQL
         │
         ▼  UI renders 5W1H entity chips with KB metadata and flags
         │
         ▼  Analyst reviews, edits, approves
```

Total time on a single CPU core: about **150 milliseconds per article**. That's the per-article cost VioNER replaces the 15-25 minutes of manual coding.

## The five contributions, one paragraph each

These are the five things the thesis leaves behind. Each is independently reusable.

### Contribution 1 — The 8-entity grounding-validated schema

A BIO schema of eight entity types (ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES) chosen so every label is verifiably present in source text. The schema was reduced from a 26-entity proposal after a November 2025 grounding pilot revealed which entities annotators could reliably tag verbatim. Result: 17 BIO labels (8 entities × B/I + O), Cohen's κ = 0.78 substantial agreement, clean training signal. *(Closes Gap 1 — see Part 6.)*

### Contribution 2 — The 4-level hierarchical taxonomy

A taxonomy of African violent events with ~95 terminal categories at Level 3, organised into four Level-1 families (Political, Criminal, Communal, State Violence Against Civilians) with Level-2 and Level-3 sub-categories. Synthesises ACLED, UCDP, and PMVE — and adds African-specific extensions (pastoralist–farmer clashes, communal cattle raiding) that no existing framework covers at this depth. *(Closes part of Gap 3.)*

### Contribution 3 — The training recipe: focal loss + class weights

A specific training configuration — focal loss with γ = 2.0 combined with inverse-frequency class weights, clipped at 10 — that recovers the operationally-critical rare entities. Section 6.6 of the thesis ablates this against three alternatives and quantifies the gain: VICTIM F1 +11 points over plain cross-entropy, ACTION F1 +7, no other entity hurt. *(Closes Gap 2.)*

### Contribution 4 — The curated knowledge base

A curated KB of ~150 active African armed groups (with aliases, country of operation, group type), ~200 conflict-affected cities (with country and region mappings), all 54 African countries, and 38 weapon categories. Used in two roles in the inference pipeline: validation (flag geographically-implausible extractions) and enrichment (canonicalise actor surface forms). *(Closes Gap 3.)*

### Contribution 5 — The deployable web platform

A complete end-to-end system: React + TypeScript front-end, FastAPI service with seven route groups, PostgreSQL event store, Docker Compose orchestration. A non-ML analyst can run inference, browse events, view analytics, train new models, monitor training progress, and administer the KB — all without writing code. UAT validates: five participants, six tasks, all completed. *(Closes Gap 4.)*

## How each contribution maps to one of the four operational gaps

| Operational gap from `problem_domain.md` | VioNER contribution that closes it |
|:--|:--|
| **Gap 1:** No fast, structured, role-distinguished 5W1H output | Contribution 1 — the 8-entity schema; also Contribution 3 (the trained model that runs the schema fast) |
| **Gap 2:** Automated tools miss the operationally-critical rare entities | Contribution 3 — the focal loss + class weights training recipe |
| **Gap 3:** Output isn't trustworthy or aggregatable | Contribution 4 — the curated KB (validation + enrichment); also Contribution 2 (taxonomy for sanity-checking event types) |
| **Gap 4:** No analyst-usable end-to-end system exists | Contribution 5 — the deployable platform; UAT validates that non-ML users can drive it |

> **Read this table together with the recap table in `problem_domain.md` Part 5.** The two tables together show the full problem-and-solution correspondence — gap on one side, VioNER contribution on the other.

---

# Part 2 · The methodological frame — design science

## Why design science (not survey, not case study, not controlled experiment)

A thesis methodology has to match what the thesis is producing. VioNER produces an **artefact** — a designed, built, evaluated system that future researchers and operational consumers can pick up and use. The methodological frame that matches "build an artefact and evaluate it empirically at each stage" is **design science** in the Hevner et al. (2004) and Peffers et al. (2007) tradition.

The alternatives don't fit:

| Methodology | Why it doesn't fit VioNER |
|:--|:--|
| **Survey** | Surveys produce measured attitudes or practices across a population. The contribution of a survey is descriptive understanding. VioNER's contribution is a built artefact, not a finding about what people think. |
| **Case study** | Case studies produce interpretation of an existing system or phenomenon. The unit of analysis is the case. VioNER builds a new artefact — there is no pre-existing case to interpret. |
| **Controlled empirical experiment** | Suitable when the claim is a falsifiable statement about a single technique. VioNER's claim is about an integrated system (schema + model + KB + UI), not a single technique. |

Design science specifically supports work that **builds an artefact, evaluates it empirically across multiple criteria, iterates based on the evaluation, and contributes the artefact plus the lessons learned to the literature**. That triad — build, evaluate, iterate — describes VioNER exactly.

## The design-science cycle

The cycle has four steps, repeated as many times as needed:

```
   Build  ───────►  Evaluate
     ▲                  │
     │                  ▼
   Refine  ◄────────  Learn
```

- **Build** — produce an artefact (a schema, a model, a system layer)
- **Evaluate** — measure how well it works against the requirements
- **Learn** — diagnose where it falls short; identify root causes
- **Refine** — redesign the artefact based on what the evaluation revealed

Then go around again. The contribution is the artefact at convergence *plus* the lessons each iteration produced.

## Three iteration loops as evidence

The thesis explicitly documents three iteration loops over five months. Each one closed with empirical evidence rather than preference. **This is what makes VioNER's methodology defensible as design science** — not just one shot, but iterated improvement validated by measurement at each step.

| Loop | What changed | Empirical trigger | When |
|:--|:--|:--|:--|
| **Corpus iteration** | Full 212k-event ACLED extract → 50k stratified diversity subset | Rare-entity F1 dropped on the full extract because of phrasing repetition | Oct → Nov 2025 |
| **Schema iteration** | 26-entity proposal schema → 8-entity grounded schema | Grounding pilot showed EVENT_TYPE at 58% grounding rate | Nov → Dec 2025 |
| **Loss iteration** | Plain cross-entropy → focal loss + class weights | Ablation table in §6.6 showed +11 F1 on VICTIM | Jan → Feb 2026 |

Each loop produced both an improved artefact *and* a publishable lesson. Together they make the methodology rigorous.

## Where this is in the thesis

| Topic | Thesis section |
|:--|:--|
| Design science as methodological frame | §1.5 |
| Corpus iteration history | §5.3 (stratified sampling rationale), §6.12 (discussion) |
| Schema iteration history | §4.3 (resulting schema), §5.2 (annotation protocol) |
| Loss iteration / ablation | §6.6 (ablation tables and discussion) |
| Threats to validity | §6.13 |

---

# Part 3 · The conceptual contributions

These four conceptual choices define *what VioNER produces*. Each is a research output independent of the implementation.

## 3.1 — The 8-entity grounding-validated schema

### What it is

A BIO schema with eight entity types, mapped to the 5W1H slots:

| 5W1H slot | Entity types | What gets tagged |
|:--|:--|:--|
| WHO | **ACTOR**, **VICTIM** | Perpetrator group/individual; those harmed |
| WHAT | **ACTION** | The act of violence (verb phrase) |
| WHEN | **DATE** | Time expressions |
| WHERE | **REGION**, **CITY**, **DISTRICT** | Administrative region, named city, sub-region |
| HOW | **CASUALTIES** | Killed/injured counts with qualifiers |

In BIO encoding (Begin / Inside / Outside), this produces **17 labels**: O + 8 × (B-, I-).

### Why this specific schema

Two reasons:

1. **Each entity is reliably groundable in source text.** The grounding pilot in November 2025 measured per-entity grounding rate (the fraction of mentions that can be located *verbatim* in source text). These eight all cleared 80%; eighteen others — including MOTIVE, TRIGGER, EVENT_TYPE — fell below 60% and were dropped. Training on grounded labels gives the model clean supervision; training on inferred labels would produce annotator-dependent noise.

2. **Each entity maps directly to an operational consumer need.** The 5W1H framing is what AU-CEWS analysts, ACLED coders, and humanitarian agencies actually use. ACE-2005's event-argument framework would be equivalent under relabelling but less interface-legible.

### Where in the thesis

§4.3 (schema definition + grounding pilot), Annex A (per-entity inclusion/exclusion rules).

## 3.2 — The 4-level hierarchical taxonomy

### What it is

A tree-structured classification of African violent events, four levels deep:

```
Level 0 (root)        Violent Events Taxonomy
Level 1 (4 families)  Political | Criminal | Communal | State Violence Against Civilians
Level 2 (~16)         Terrorism, Election Violence, Coup, Armed Robbery, Kidnapping,
                      Ethnic Clash, Religious Violence, Pastoralist-Farmer Clash,
                      Extrajudicial Killing, etc.
Level 3 (~95)         Bombing, Ambush, Armed Assault, Hostage-Taking, Soft-Target Attack,
                      Cattle Raiding, Mass Arrest, Forced Disappearance, etc.
```

### Why this design

Three reasons:

1. **Hierarchical lets consumers query at the granularity they need.** Cross-country count studies query at Level 1 (where ACLED's six categories also live). Operational targeting queries at Level 2 or 3. A flat 95-category schema would be unqueryable.

2. **Synthesises three existing frameworks.** ACLED, UCDP, and PMVE each have their own event-typing schemes. VioNER's taxonomy is designed to be compatible with all three at Level 1 (so cross-database aggregation is possible) while adding the granularity each lacks.

3. **Adds African-specific extensions.** Pastoralist–farmer clashes and communal cattle raiding account for a measurable fraction of Sahel and Horn-of-Africa conflict reporting and don't fit cleanly into ACLED's "Violence against civilians" bucket. VioNER's taxonomy carves these out explicitly.

### Where in the thesis

§4.4 (taxonomy definition), Annex B (full leaf list with decision rules for awkward boundaries).

## 3.3 — The 5W1H structuring approach

### What it is

A post-NER step that converts the flat list of extracted BIO spans into a **structured record** organised by the 5W1H slots:

```json
{
  "WHO": {"perpetrator": "Al-Shabaab fighters",
          "victim":      "12 soldiers"},
  "WHAT": {"action": "attacked"},
  "WHEN": {"date_text": "Tuesday", "normalised": "2026-01-09"},
  "WHERE": {"city": "near Mogadishu", "country": "SOM"},
  "HOW":   {"casualties": {"killed": 12, "qualifier": "at least"}},
  "WHY":   null
}
```

### Why this design

The flat list of BIO spans is what the NER model produces. The structured record is what the analyst needs. The 5W1H step bridges the two by:

- Grouping spans by category (WHO, WHAT, etc.)
- Distinguishing perpetrator from victim (both are WHO, but operationally distinct)
- Normalising relative dates ("Tuesday" → "2026-01-09" based on article publish date)
- Parsing casualty counts and their qualifiers ("at least 12" → {killed: 12, qualifier: "at least"})
- Resolving country from the most-specific WHERE entity via KB lookup

WHY is intentionally null — motive was dropped from the supervised schema because of low grounding rate.

### Where in the thesis

§4.7 (post-NER structuring algorithm — Algorithm 4.5).

## 3.4 — The KB-validation-and-enrichment design

### What it is

A curated knowledge base used in two specific roles during inference:

1. **Validation** — when the model extracts an ACTOR and a location in the same sentence, the KB checks geographic plausibility. Mismatches (Al-Shabaab in Goma) produce a `geo_implausible` flag.

2. **Enrichment** — surface variants of the same actor ("Al Shabaab", "al-shabaab", "Al-Shabaab fighters") all canonicalise to a single KB entry with country code, group type, and canonical name attached.

### Why this design

Three reasons:

1. **Models don't have world knowledge.** A trained BERT can extract entity spans correctly and still produce records that are factually implausible because it has no information beyond text patterns. Validation against curated world knowledge is the bridge.

2. **Downstream analytics need canonical actors.** Without canonicalisation, "Al-Shabaab" attacks under five surface forms count as five different actors. Enrichment lets aggregation queries return the right totals.

3. **Using a single KB for both roles avoids duplication.** Validation and enrichment are usually treated as separate problems (entity linking vs fact-checking). Treating them as two uses of the same curated resource is the architectural choice.

### Where in the thesis

§4.5 (KB design), §6.7 (operational impact: 2.4% flag rate, 64.3% enrichment rate), Annex C (KB schema and composition).

---

# Part 4 · The technical contributions

These six choices define *how VioNER produces its output*. They are implementation decisions, each defensible against alternatives.

## 4.1 — BERT backbone choice (`bert-base-cased`)

### What it is

The base model is `bert-base-cased` — Google's 2018 transformer language model, the cased English variant, 110 million parameters, pretrained on Wikipedia + BookCorpus.

A new classification head with 17 output units (one per BIO label) is added on top. The whole network — backbone + head — is then fine-tuned end-to-end on VioNER's training corpus.

### Why this specific backbone

Five reasons:

1. **Well-documented for NER fine-tuning.** The bert-base-cased + linear-head + cross-entropy pattern is the established baseline in token-classification literature. Picking it isolates VioNER's *loss-function* contribution from any confound about backbone novelty.

2. **The right scale for the data volume.** With 50,000 training examples, a 110M-parameter model is in the over-parameterised regime where early stopping is the protection against overfitting. A larger backbone (bert-large, RoBERTa-large) would be over-parameterised further, costing training time without measurable per-entity F1 gain.

3. **Cost-deployable.** On a single CPU core, inference is ~150 ms per article. On Apple M2 Max with MPS acceleration, it's substantially faster. This matters because operational consumers may need to deploy on commodity hardware.

4. **The case-sensitive variant.** African armed groups frequently use capitalised forms ("Al-Shabaab", "JNIM", "RSF") that the uncased variant would lose. Cased is the right choice for the entity-mention task.

5. **bert-large-cased was tested as a control.** Macro F1 moved by less than a point; training time tripled. The improvement didn't justify the cost.

### Why NOT alternatives

- **bert-large** — tripled cost, sub-point F1 improvement
- **RoBERTa, DeBERTa** — newer, but not benchmarked specifically on African violent-event NER; would have confounded the loss-function contribution
- **AfroLM, XLM-RoBERTa** — multilingual; English representations not necessarily stronger than bert-base-cased; appropriate for the future multilingual extension (high-priority future work)
- **GPT-2, LLaMA** — generative architecture, less suited for token classification than encoder-only architectures

### Where in the thesis

§5.4 (training implementation), backup B1 (hyperparameter table).

## 4.2 — BIO encoding (not BIOES, not BILOU)

### What it is

The standard CoNLL-2000/2003 sequence-labelling scheme:
- **B-X** for the first token of an entity of type X
- **I-X** for subsequent tokens of the same entity
- **O** for tokens outside any entity

For VioNER with 8 entity types: 8×2 + 1 = **17 labels**.

### Why this specific encoding

BIO uses the **minimum number of labels needed** to express both span starts and continuations: $2k + 1$ for $k$ entity types. Alternatives add labels without buying capability for VioNER's use case:

| Encoding | Labels for 8 entities | What it adds | Useful here? |
|:--|--:|:--|:--|
| **IO** | 9 | Nothing (collapses begin/inside) | No — adjacent same-type entities can't be split |
| **BIO** | **17** | Begin/Inside distinction | **Yes — this is what VioNER uses** |
| **BIOES** | 33 | Explicit End and Single tags | No — doubles label space without operational gain |
| **BILOU** | 33 | Same as BIOES with different naming | No — same as BIOES |

The expressive gain of BIOES (explicit End and Single) only matters when adjacent same-type entities occur with no intervening token. In African news reporting this is rare (under 5% of cases per the pilot). BIO trades that small loss of expressiveness for half the label space — which materially helps the class-imbalance problem.

### Where in the thesis

§4.3 (BIO encoding rationale), §2.5 (NER evaluation conventions).

## 4.3 — The training recipe

### What it is

The exact configuration used to fine-tune `bert-base-cased`:

| Component | Value | Why |
|:--|:--|:--|
| Loss function | Focal loss with γ=2.0 + inverse-frequency class weights + label smoothing β=0.1 | Recovers rare entities (§6.6 ablation) |
| Class weight cap | 10 | Prevents gradient instability on rarest classes |
| Optimiser | AdamW with weight decay 0.01 | BERT fine-tuning standard |
| Learning rate | 5×10⁻⁵ | BERT NER literature default |
| Warmup ratio | 0.1 of total steps | Linear warmup → ReduceLROnPlateau |
| Gradient clipping | max-norm 1.0 | Stability |
| Batch size | 16 train, 32 eval | Hardware-bounded on M2 Max |
| Max sequence length | 128 tokens | Mean article 64; covers +2σ; sliding-window for longer |
| Max epochs | 10 | Convergence happens at epoch 2 |
| Early stopping | Validation loss, patience 2 | Standard practice |
| Random seed | 42 (plus 17 and 91 for variance) | Reproducibility |

### Why this specific configuration

Most values come from one of three sources: BERT-NER literature defaults, hardware constraints, or empirical grid search. The choices that constitute the **research contribution** are the loss-function family — focal loss + class weights + label smoothing — because the §6.6 ablation shows that this combination produces measurable rare-entity recovery that the other configurations don't.

### Why the loss function is the centrepiece

Read this together with `formulas_explained.md` Part A (which walks through every formula). The summary version:

| Loss configuration | VICTIM F1 | ACTION F1 |
|:--|--:|--:|
| Plain cross-entropy | 0.708 | 0.794 |
| Class-weighted CE | 0.776 | 0.834 |
| Focal loss alone | 0.792 | 0.842 |
| **Focal + weights (production)** | **0.817** | **0.866** |

The combination beats either ingredient alone — they are complementary. This is the empirical answer to RQ2.

### Where in the thesis

§5.5 (loss implementation), §6.6 (ablation), backup B1 (full hyperparameter table).

## 4.4 — The data pipeline

### What it is

The 50,000-example training corpus is produced by:

1. **Source extraction** — pull ACLED's open-data export (≈212,000 African events as of training).
2. **Stratified diversity sampling** — reduce to 35,000 examples, oversampling rare entity types.
3. **Template-based augmentation** — generate 15,000 additional synthetic examples targeting rare classes (VICTIM, ACTION, CASUALTIES).
4. **Splitting** — 80/20 train/validation, stratified on entity-type presence, **at the article level** (not sentence level), with hash-based deduplication before split.
5. **Annotation projection** — project ACLED's structured columns onto free-text notes to produce gold BIO labels.
6. **Pilot validation** — 200-document IAA pilot achieves Cohen's κ = 0.78.

### Why this specific pipeline

The composition reflects three empirical lessons:

1. **Naive random sampling from the full ACLED extract lowered rare-entity F1.** Phrasing repetition in common-event types drowned out the signal for rare types. This is the corpus iteration loop in Part 2.

2. **Templates lift rare-class minimums to a level the model can learn.** Without augmentation, VICTIM is in single-percentage-point share of total tokens and the loss-function tricks aren't enough.

3. **Article-level splits and hash deduplication prevent information leakage.** Sentence-level splits with duplicate articles could let validation sentences appear in training under different article IDs. The article-level + hash approach prevents this by construction.

### Where in the thesis

§5.2 (annotation), §5.3 (sampling + augmentation), §6.13 (residual leakage discussion).

## 4.5 — The post-NER 5W1H structuring algorithm

### What it is

After the BERT model produces per-token BIO predictions, a post-processing step (Algorithm 4.5 in the thesis) converts the flat span list into a structured 5W1H record. The algorithm has four phases:

| Phase | What happens |
|:--|:--|
| **Phase 1 — Token classification** | Forward pass through BERT → per-token softmax over 17 labels |
| **Phase 2 — BIO span construction** | Collapse contiguous B/I sequences into spans; compute averaged sub-token confidence per span |
| **Phase 3 — Confidence filtering and 5W1H grouping** | Drop spans below per-category confidence threshold; bucket surviving spans into WHO/WHAT/WHEN/WHERE/HOW |
| **Phase 4 — KB enrichment and taxonomy classification** | Lookup ACTORs and CITYs against the KB; classify the ACTION verb + actor context into Level 1–3 taxonomy path |

### Why this design

Three reasons:

1. **Confidence filtering is per-category, not global.** Different entity types have different uncertainty floors. CASUALTIES needs a higher threshold than DATE because misclassified casualty counts have higher operational cost.

2. **5W1H grouping is structural, not learned.** Once entity types are determined, the grouping into WHO/WHAT/WHEN/WHERE/HOW is mechanical. No further model is needed.

3. **KB and taxonomy steps come *after* the model.** Keeping these post-model means they can be updated without retraining. A new armed group added to the KB tomorrow improves canonicalisation immediately.

### Where in the thesis

§4.7 (algorithm description), backup B4 (algorithm overview).

## 4.6 — The rule-based taxonomy classifier

### What it is

A rule-based classifier that takes the extracted ACTION verb plus context and assigns a Level-1 → Level-2 → Level-3 path in the taxonomy. Roughly:

```
ACTION verb + actor context →  Level 1 family (Political / Criminal / Communal / State)
                              → Level 2 subcategory  (Terrorism / Election Violence / ...)
                              → Level 3 leaf         (Bombing / Ambush / Soft-Target Attack / ...)
```

Implemented as a series of conditional rules with explicit decision points for awkward boundaries.

### Why rule-based (and not learned)

Two reasons:

1. **Training data for a learned hierarchical classifier doesn't exist.** ACLED's structured columns don't directly provide event-type labels at the Level-3 granularity the taxonomy needs. Constructing a labelled dataset for that would have been a thesis in itself.

2. **Rule-based achieves coverage with auditability.** Every classification decision can be traced to a specific rule. When an analyst disagrees with a classification, they can see which rule fired and propose a refinement.

A learned hierarchical classifier is the second-highest-priority future-work item (§7.5). Rule-based is what shipped.

### Where in the thesis

§4.7 (post-NER processing including taxonomy classification).

## 4.7 — The KB validation-and-enrichment logic

### What it is

Two algorithms running on every inference request:

**Validation:**
```
For each (ACTOR span, CITY span) pair in the same sentence:
    actor_country = KB.lookup_actor_country(actor_canonical_form)
    city_country  = KB.lookup_city_country(city_canonical_form)
    if actor_country ≠ city_country:
        record.flags.append("geo_implausible")
```

**Enrichment:**
```
For each ACTOR span:
    matches = KB.fuzzy_match(span_text, threshold=0.85)
    if matches:
        canonical = matches[0].canonical
        record.who.perpetrator = {
            "text":      span_text,
            "kb_id":     matches[0].id,
            "canonical": canonical,
            "country":   matches[0].country,
            "type":      matches[0].group_type
        }
    else:
        record.who.perpetrator = {"text": span_text}
```

### Why this design

Three considerations:

1. **Validation never blocks extraction.** The flag is metadata; the record is still persisted. Analysts decide based on the flag whether to re-read.

2. **Enrichment never invents data.** If the KB doesn't match, the record carries the raw surface form. Nothing is fabricated.

3. **Fuzzy matching at threshold 0.85.** Tolerates capitalisation, spacing, hyphenation variations ("Al-Shabaab" / "Al Shabaab" / "al-shabaab"); doesn't conflate distinct groups.

### Where in the thesis

§4.5 (KB design), §4.7 (validation/enrichment logic), §6.7 (operational impact).

---

# Part 5 · The system architecture

The architecture is the *delivery vehicle*. The model and KB are the engines; the architecture is the rest of the car.

## 5.1 — Four-layer architecture

```
┌─────────────────────────────────────────────────┐
│  PRESENTATION LAYER                             │
│  React + TypeScript (single-page app)           │
│  Pages: Training | Inference | Events |         │
│         Analytics | KB Admin | Auth             │
└────────────────────┬────────────────────────────┘
                     │ HTTPS / JSON
                     ▼
┌─────────────────────────────────────────────────┐
│  SERVICE LAYER                                  │
│  FastAPI (Python async web framework)           │
│  Routes: /api/training  /api/inference          │
│          /api/events    /api/analytics          │
│          /api/kb        /api/auth  /api/system  │
└────────────────────┬────────────────────────────┘
                     │ in-process calls
                     ▼
┌─────────────────────────────────────────────────┐
│  COMPONENT LAYER (in-process)                   │
│  ┌──────────────────┐  ┌──────────────────┐     │
│  │  NER component   │  │  Knowledge base  │     │
│  │  (BERT + head)   │  │  (in-memory)     │     │
│  └──────────────────┘  └──────────────────┘     │
└────────────────────┬────────────────────────────┘
                     │ SQL
                     ▼
┌─────────────────────────────────────────────────┐
│  PERSISTENCE LAYER                              │
│  PostgreSQL 16                                  │
│  Tables: events, training_runs, articles,       │
│          users, kb_actors, kb_locations         │
└─────────────────────────────────────────────────┘
```

### Why four layers (and not fewer or more)

- **Three layers (no in-process component layer)** would put the model loading and KB queries inside the FastAPI route handlers, coupling business logic to the model. Separating the component layer makes the model and KB swappable.
- **Five layers (microservices)** would split the NER component and KB into separate processes with network calls between them. At VioNER's scale this adds latency and operational complexity without buying anything.
- **Four layers is the minimum that gives clean separation of concerns**: UI, API, model, storage.

## 5.2 — Technology stack — what and why

| Layer | Technology | Why this choice |
|:--|:--|:--|
| Frontend | **React + TypeScript** | Largest ecosystem in 2026; strongest TypeScript support; easy hiring/maintenance for whoever inherits the system |
| State management | React Router + Context | Built into React Router 7; no external state library needed at this scale |
| Frontend build | Vite | Fast dev rebuild; small production bundle |
| HTTP client | Native `fetch` + lightweight wrappers | No need for axios at this complexity |
| API framework | **FastAPI** | Async Python; built-in OpenAPI docs; type-checked request/response; matches PyTorch ecosystem |
| ML framework | **PyTorch 2.x + HuggingFace Transformers** | Industry standard for BERT fine-tuning; reproducible; well-documented |
| Database | **PostgreSQL 16** | Full-text search; JSONB indexing for the extracted_record column; concurrent-user safety |
| ORM | SQLAlchemy 2 | Type-checked queries; native async support |
| Migrations | Alembic | Reversible schema migrations; works with SQLAlchemy |
| Orchestration | **Docker Compose** | One-command stack startup; reproducible across machines |
| Real-time updates | WebSocket via FastAPI | Live training progress without polling |

### Why this stack and not alternatives

A few decisions worth defending:

| Decision | Alternative | Why this won |
|:--|:--|:--|
| React | Vue, Angular, Svelte | React's TypeScript ecosystem and community are the largest in 2026 |
| FastAPI | Flask, Django, Node.js | FastAPI's async-first design + native PyTorch integration; built-in OpenAPI docs are operationally useful |
| PostgreSQL | SQLite, MongoDB | Full-text + JSONB indexing needed for the analytics layer; concurrent-user safety; SQLite would handle volume but not the query layer well |
| Docker Compose | Kubernetes, bare-metal install | Docker Compose is the minimum-friction one-command deployment; Kubernetes would be enterprise plumbing not justified at this scale |
| WebSocket | Server-Sent Events, polling | WebSocket is bidirectional and supported natively by FastAPI; polling wastes bandwidth |

## 5.3 — The end-to-end inference pipeline

When the analyst submits one article, the system executes this sequence:

| # | Step | Component | Approximate time |
|:-:|:--|:--|--:|
| 1 | Article submitted via UI | Frontend | — |
| 2 | POST /api/inference with article body | Frontend → Backend | <5 ms |
| 3 | WordPiece tokenisation | NER component | ~3 ms |
| 4 | BERT forward pass | NER component | ~110 ms |
| 5 | BIO decode to spans | NER component | ~2 ms |
| 6 | Confidence filtering | NER component | <1 ms |
| 7 | 5W1H grouping | NER component | <1 ms |
| 8 | KB validation + enrichment | KB component | ~15 ms |
| 9 | Taxonomy classification | NER component | ~5 ms |
| 10 | Persist to PostgreSQL | Service + DB | ~10 ms |
| 11 | Response sent to UI | Backend → Frontend | <5 ms |
| 12 | UI renders entity chips | Frontend | — |

**Total per-article latency: ~150 ms on a single CPU core.** Sufficient for batch processing thirty thousand articles per year with substantial headroom.

## 5.4 — The training service and progress UI

Training is a separate API surface:

| Endpoint | Purpose |
|:--|:--|
| `POST /api/training/runs` | Start a new training run with specified config |
| `GET  /api/training/runs/{id}` | Get training-run status |
| `GET  /api/training/runs` | List training runs with filters |
| `WS   /ws/training/{id}` | WebSocket stream of live progress updates |

The training UI lets a non-ML user:

1. Pick a training dataset from a dropdown
2. Pick a loss configuration (with focal loss + class weights as the default)
3. Set hyperparameters via sliders/inputs (with sensible defaults)
4. Start the run
5. Watch the loss curve update live over WebSocket
6. See per-epoch validation F1 as it computes
7. Save the trained checkpoint or discard

This is what closes the *retraining* failure mode in Gap 4. A new armed group emerges → an analyst adds it to the KB → an analyst kicks off a retraining run from the UI → the new model is deployed. No ML engineer needed.

## 5.5 — Deployment and reproducibility

The full stack runs under Docker Compose. From a fresh checkout:

```
git clone <repo>
cd named-entity-recognition
docker-compose up -d
```

Three services start:

- `db` — PostgreSQL 16 with initial schema migrations applied
- `backend` — FastAPI with PyTorch + the trained checkpoint mounted
- `frontend` — React app served by Vite/nginx

Total disk: ~5 GB (BERT checkpoint dominates).
Total memory: ~3 GB at idle.
Startup time: ~30 seconds.

**The reproducibility claim is strong.** Anyone with the repo can stand up the system on commodity hardware. This is what makes Contribution 5 (the deployable platform) substantive — not "we built a system" in the abstract, but "we built a system anyone can reconstitute".

---

# Part 6 · How each piece closes its operational gap

This is the most important table in the document. It maps each piece of VioNER's solution back to the operational gap it closes from `problem_domain.md`.

| Gap | Operational shortfall | VioNER piece that closes it | How |
|:--|:--|:--|:--|
| **1** | No fast, structured, role-distinguished 5W1H output | **8-entity schema + trained BERT model** | Schema bakes role distinction (ACTOR ≠ VICTIM); model runs in ~150 ms per article |
| **2** | Automated tools miss rare entities | **Focal loss + class weights training recipe** | Recovers VICTIM at 0.82, ACTION at 0.87, CASUALTIES at 0.89 — making review-vs-rewrite finally save time |
| **3** | Output isn't trustworthy or aggregatable | **Curated KB + taxonomy + post-NER structuring** | KB flags implausible extractions (2.4% rate) and canonicalises surface variation (64.3% of ACTORs); taxonomy structures the event type |
| **4** | No analyst-usable end-to-end system | **Web platform: FastAPI + React + Postgres + Docker** | Non-ML users complete all six tasks in UAT; one-command deployment via Docker Compose |

## Why dropping any piece breaks the chain

The four contributions are *jointly necessary*. Drop any one and the system stops delivering value:

- Drop the schema → output isn't 5W1H-structured; analyst can't use it
- Drop the training recipe → rare entities under-recovered; analyst still has to read each article
- Drop the KB → output isn't trustworthy or aggregatable; analyst spends time deduplicating and verifying
- Drop the platform → trained model sits on a researcher's laptop; analyst never sees it

A panellist asking *"which piece is most important?"* gets the answer: **none individually; all four jointly**. That's why the contribution is the integrated artefact, not any single component.

---

# Part 7 · Trade-offs and roads not taken

For each major design decision, the alternative that was considered and the reason it lost.

## 7.1 — BERT vs LLM

| Approach | Pro | Con | Decision |
|:--|:--|:--|:--|
| Fine-tuned `bert-base-cased` | Reproducible, auditable, on-prem, cheap | Requires labelled training data | **Chosen** |
| GPT-4 / Claude prompt-engineering | High zero-shot quality; no training data needed | Closed weights; vendor-dependent; per-call cost; data sovereignty concerns | Rejected for production; remains a credible future baseline |

The decision is fundamentally about **operational deployability for the AU member-state consumer**. Closed-weight LLMs are non-starters where data sovereignty matters.

## 7.2 — BIO vs BIOES

Covered in Part 4.2. BIO won because BIOES doubles the label space without buying capability for VioNER's case.

## 7.3 — Focal loss vs alternatives

| Approach | VICTIM F1 | Decision |
|:--|--:|:--|
| Plain cross-entropy | 0.708 | Baseline |
| Class-weighted CE | 0.776 | Helps but insufficient |
| Focal loss alone | 0.792 | Helps but insufficient |
| Effective-number weighting (Cui et al. 2019) | ~0.78 (similar) | Tried; gave essentially the same result as inverse-frequency |
| Dice loss | Not tested | Future comparison |
| **Focal + class weights** | **0.817** | **Chosen** |

## 7.4 — Rule-based vs learned taxonomy classifier

| Approach | Pro | Con | Decision |
|:--|:--|:--|:--|
| Rule-based | Auditable, no separate training data needed | Doesn't scale gracefully as taxonomy grows | **Chosen for thesis scope** |
| Learned hierarchical | Better quality at scale; learns from data | Requires labelled training data the thesis doesn't have | Deferred to future work item 2 |

## 7.5 — Frontend framework choice

React beat Vue, Angular, and Svelte on ecosystem maturity and TypeScript support in 2026. The choice is conservative and low-risk for whoever inherits the system. The thesis doesn't claim React itself is a contribution; the integrated React-based UI is.

## 7.6 — PostgreSQL vs SQLite

SQLite would handle 30,000 events/year volume comfortably, but PostgreSQL's full-text search index over article bodies and JSONB indexing on the extracted_record column are operations SQLite handles weakly. Concurrent-user write safety also matters. PostgreSQL's Docker footprint is small enough that the trade-off is essentially free.

## 7.7 — Monolith vs microservices

A single FastAPI worker holding model and KB in memory is faster and simpler than a service mesh. Microservices would be appropriate at much higher request volume. At thirty thousand articles per year, the monolithic FastAPI is the right shape.

---

# Part 8 · The three iteration loops — methodology in action

Each loop is concrete evidence that VioNER's methodology is genuine design science, not retrospective storytelling. Each closed with an empirical signal, not preference.

## Loop 1 — The corpus iteration (October–November 2025)

### What was tried first

Pull the full ACLED African events extract — about 212,000 records — and train on the full corpus. The intuition: more data is always better.

### What the evaluation showed

Trained model achieved acceptable macro F1 (~0.85) but **rare-entity F1 was lower** than later runs on smaller corpora. VICTIM was particularly weak. Inspection of the training data revealed why: ACLED notes have heavy phrasing repetition for common event types (raids, IED incidents, civilian casualties in known theatres). The model was overfitting common phrasing patterns and under-learning the variation that characterises rare entities.

### What was learned

The metric that matters isn't corpus size; it's **diversity of phrasing relative to entity-type coverage**. A 50,000-example corpus with rare entities oversampled and phrasing diversified beats a 212,000-example corpus with massive repetition of common patterns.

### What was refined

The stratified diversity sampler in §5.3 of the thesis. Sample more aggressively from articles that contain rare entities; under-sample from articles with high-frequency common patterns. Result: a 35,000-example real-news subset that the model trains on better than the full 212k extract.

### Why this is design-science evidence

The decision wasn't *"smaller corpus is more elegant"*. It was an empirical signal — rare-entity F1 went down on the larger corpus — followed by diagnosis and redesign. That's a complete build-evaluate-learn-refine loop.

---

## Loop 2 — The schema iteration (November–December 2025)

### What was tried first

The proposal's 26-entity schema. Train on all 26, including MOTIVE, TRIGGER, EVENT_TYPE, ORGANIZATION_AFFILIATION, etc.

### What the evaluation showed

A grounding pilot — annotators trying to label a small sample — produced **Cohen's κ of 0.40** on the full 26-entity schema. That's *fair* agreement on the Landis-Koch scale, which is too low. Two annotators would label the same article meaningfully differently on the inferred entities.

### What was learned

For each entity type, the team measured grounding rate — the fraction of mentions that could be located *verbatim* in source text. EVENT_TYPE came in at 58%. MOTIVE at 41%. TRIGGER at 38%. These low rates meant annotators were *inferring* rather than *reading* — exactly the source of disagreement.

### What was refined

Drop every entity type below 80% grounding rate. The 8 that remained — ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES — were all above the threshold. The IAA pilot rerun on the reduced 8-entity schema achieved **κ = 0.78** — substantial agreement.

The dropped entities are recovered downstream: EVENT_TYPE through the taxonomy classifier, COUNTRY through KB lookup. So the operational schema the consumer sees is unchanged; the training schema is clean.

### Why this is design-science evidence

Not a methodological preference. An empirical signal (κ = 0.40 too low) → root-cause diagnosis (annotators inferring) → measurement (grounding rate per entity) → redesign (drop low-grounded types) → validation (κ = 0.78 on refined schema).

---

## Loop 3 — The loss iteration (January–February 2026)

### What was tried first

Plain cross-entropy. The standard NER loss. Training looked clean (validation loss decreasing through epoch 2). Macro F1 was acceptable. But VICTIM F1 was 0.708 — meaning the system missed about 29% of victim entities.

### What the evaluation showed

Per-entity analysis revealed the pattern. DATE, CITY, ACTOR were all above 0.92 F1. The rare entities were weak:

- VICTIM: 0.708
- CASUALTIES: 0.853
- ACTION: 0.794

For operational consumers, this was the wrong tier of weakness. Victims, casualty counts, and action verbs are exactly what analysts read articles for.

### What was learned

The training data has 78% O tokens. Plain cross-entropy weights all tokens equally. The gradient signal from the 22% entity tokens — and especially from the few-percent rare entity tokens — gets drowned out.

### What was refined

Three configurations were tested under identical conditions:

| Configuration | VICTIM F1 |
|:--|--:|
| Class-weighted CE | 0.776 |
| Focal loss alone | 0.792 |
| **Focal + class weights** | **0.817** |

The combination beat either alone. The thesis's contribution claim — that focal loss with inverse-frequency class weights is the right loss configuration for severe class imbalance in violent-event NER — rests on this ablation.

### Why this is design-science evidence

Empirical evaluation surfaced the problem (rare entities under-recovered). Diagnosis identified the cause (gradient signal drowned out). Multiple candidate solutions were tested (class weights alone, focal alone, both together). The winner was the combination. Three loops over three months; the winning configuration shipped.

---

# Part 9 · Reproducibility

A defensible system is one another researcher could rebuild. Here's the reproducibility claim.

## What's openly documented

| Artefact | Where |
|:--|:--|
| Source code (frontend + backend) | Repository |
| Schema (8-entity BIO) | Annex A of thesis |
| Taxonomy (4-level, ~95 leaves) | Annex B |
| KB structure | Annex C |
| Training recipe (hyperparameters, loss config) | §5.5 + backup B1 |
| Training data construction (sampling + augmentation) | §5.3 |
| Annotation protocol | §5.2 |
| Evaluation metrics | §2.5 |
| Inference algorithm | §4.7, backup B4 |
| Docker Compose configuration | Repository |

## What another researcher would need to rebuild VioNER

1. The repository (open)
2. The ACLED open-data export (publicly available)
3. The annotation guidelines from Annex A
4. Compute capacity: a single workstation with M2 Max or equivalent GPU
5. Time: roughly two weeks of engineering to reproduce the data pipeline + one weekend of training

That's it. No closed components, no proprietary data, no special hardware.

## What's not yet released

The KB content (150 armed groups, 200 cities) is partially curated and partially scraped. Public release requires checking each entry against source attributions and may not happen in full before defense. The KB *structure* is fully documented; the *content* will need separate release coordination.

## Receipts

| Reproducibility claim | Source |
|:--|:--|
| Source code reproducibility | Repository + this thesis |
| Training reproducibility (seeds, configs) | §5.5 + B1 |
| Run-to-run variance reported | §6.4 (±0.4 macro F1 across 3 seeds) |
| Ablation reproducibility | §6.6 (4 configurations under identical conditions) |
| Docker Compose deployment | Repository |

---

# Part 10 · Defending solution choices in Q&A

Likely panel questions about the architecture, methodology, and design choices — with prepared answers in the same plain conversational style as `qa_kit.md`.

### Q · "Why design science as the methodological frame?"

**Bottom line.** Because the contribution is an artefact, evaluated empirically at each stage, refined iteratively across multiple loops. That triad is the textbook definition of design science.

**Detail.** Survey methodology produces measured attitudes; case-study methodology produces interpretation of existing cases; controlled experiments produce falsifiable claims about single techniques. VioNER produces a built artefact — schema + model + KB + system — evaluated against multiple criteria (model F1, KB operational rates, UAT outcomes) and refined across three iteration loops documented in the thesis. Design science (Hevner et al. 2004, Peffers et al. 2007) is the established frame for that kind of contribution.

### Q · "Why bert-base-cased and not a larger or newer model?"

**Bottom line.** It gives the best quality-to-cost ratio for this task on the data volume available, and the bottleneck is not backbone capacity.

**Detail.** The data is 50,000 examples; bert-base at 110M parameters is in the over-parameterised regime where early stopping is the protection. Larger backbones tested (bert-large) gave sub-point F1 improvement at 3× training cost and 2× inference latency. The dominant errors are boundary mismatch and location-type confusion — both structural, not capacity-bound. RoBERTa or DeBERTa would have confounded the loss-function contribution. The deliberate choice is to isolate the methodological contribution rather than chase architectural novelty.

### Q · "Why a rule-based taxonomy classifier instead of a learned one?"

**Bottom line.** Training data for a learned hierarchical classifier at Level-3 granularity doesn't exist; constructing it would be a separate thesis. Rule-based ships now, learned is future-work item 2.

**Detail.** ACLED's structured columns provide labels at roughly Level-1 granularity (event_type field), not at Level 2 or 3. A learned classifier needs supervision at the level you want to predict. Constructing 50,000+ examples labelled at Level-3 with cross-coder consistency would be a thesis-scale annotation project. The rule-based version achieves coverage with auditability — every classification traces to a specific rule — and ships in this thesis. A two-stage learned classifier (Level 1 first, then Levels 2/3 conditional) is the natural next step and is named as future work.

### Q · "Why FastAPI and not Django or Node.js?"

**Bottom line.** FastAPI is async-first, integrates natively with PyTorch (both are Python), and ships with automatic OpenAPI documentation.

**Detail.** Async support is needed for the WebSocket training-progress feed. Native PyTorch integration means the model can be held in process memory without serialisation overhead between API and model layers. OpenAPI docs are valuable for whoever inherits the system. Django would have required adding async support; Node.js would have required serialising to and from the PyTorch process. FastAPI is the path-of-least-friction for this stack.

### Q · "Why PostgreSQL and not a NoSQL store?"

**Bottom line.** PostgreSQL's full-text search index and JSONB indexing both matter for the analytics layer, and concurrent-user safety is needed.

**Detail.** The events table has a free-text article column that needs full-text search, and an extracted_record JSONB column that needs index-based queries on nested fields ("all events where extracted_record.WHERE.country = SOM"). PostgreSQL handles both natively. MongoDB would handle JSONB-equivalent queries but doesn't have integrated full-text search at the same quality. SQLite would handle the volume but its full-text-search extension and concurrency are weaker. PostgreSQL is the no-regrets choice.

### Q · "How much of the system did you actually build vs adapt?"

**Bottom line.** The model fine-tuning code, the post-NER 5W1H structuring, the KB structure and content, the React UI, the FastAPI service layer, and the analytics queries were all built for this thesis. The BERT backbone, the transformers library, the React/FastAPI/PostgreSQL stack are off-the-shelf and credited as such.

**Detail.** A reasonable estimate: ~85% of the code in the repository was written specifically for this thesis. The remaining ~15% is library glue. The KB content is original curation; the taxonomy is original synthesis. The training-pipeline code is original (focal loss + class weights implementation, label smoothing implementation, stratified-sampling implementation). The annotation guidelines (Annex A) are original.

### Q · "Could a different team rebuild this from your repository?"

**Bottom line.** Yes — that's the reproducibility claim. The repository, plus ACLED open data, plus the documented annotation guidelines, are sufficient.

**Detail.** Section 9 of this document and §5.2-5.7 of the thesis enumerate everything needed. Compute is a single workstation. Time is approximately two weeks for the data pipeline plus a weekend for training. The Docker Compose stack starts on commodity hardware. The thesis explicitly aims for reproducibility, not just public release — that's why every iteration loop and every hyperparameter is documented.

### Q · "Why didn't you compare against ICEWS or GDELT empirically?"

**Bottom line.** Direct head-to-head comparison isn't possible because ICEWS and GDELT use different output schemas. Backup B9 compares against generic BERT NER (spaCy, HuggingFace heads) on the 4-entity overlap (PER ≈ ACTOR, LOC ≈ CITY, DATE).

**Detail.** ICEWS produces CAMEO event codes; VioNER produces 5W1H structured records. Comparing them apples-to-apples would require a translation layer that itself becomes a research question. GDELT's flat event flags similarly don't map cleanly. The defensible comparison is against the systems that *do* produce token-level entity tags — generic BERT NER — and backup B9 shows VioNER's 0.94 macro F1 vs spaCy's 0.75 and HuggingFace dslim's 0.82 on the entity-tag overlap.

### Q · "What's your single most important design decision?"

**Bottom line.** Dropping the 18 entities that didn't ground well. Everything else follows from that.

**Detail.** Without grounding-validated supervision, the model couldn't have produced trustworthy output. Without trustworthy output, the KB validation layer would be applying sanity checks to noise. Without trustworthy output, the UAT wouldn't have scored 4.6 on "5W1H structuring was clear". The schema-pruning decision in November 2025 is the upstream choice that made everything downstream work. If forced to name one decision as the thesis's foundational move, that's it.

### Q · "What if the panel disagrees with one of your architectural choices?"

**Bottom line.** Most choices are defensible-with-trade-offs rather than uniquely correct. The methodology is unchanged; only the implementation shifts.

**Detail.** React vs Vue, PostgreSQL vs MongoDB, FastAPI vs Django — these are *engineering* choices, not *research* contributions. The research contribution is the integrated artefact (schema + model + KB + UI evaluated end-to-end). Swapping React for Vue would change implementation, not contribution. The defensible answer to disagreement on architecture: "the choice is defended on engineering grounds — community size, integration cost, reproducibility — but the research contribution stands regardless of the technology stack."

---

# Appendix · Solution receipts (thesis section references)

For panel questions of the form *"where in the thesis does it say that?"*:

| Claim | Thesis section |
|:--|:--|
| 8-entity grounding-validated schema | §4.3, Annex A |
| 4-level taxonomy with ~95 leaves | §4.4, Annex B |
| 5W1H post-NER structuring algorithm | §4.7, backup B4 |
| KB design and structure | §4.5, Annex C |
| bert-base-cased fine-tuning | §5.4 |
| BIO encoding rationale | §4.3, §2.5 |
| Focal loss + class weights training recipe | §5.5 |
| Ablation: focal vs CE | §6.6, Table 6.8 |
| Stratified diversity sampling | §5.3 |
| Annotation protocol | §5.2 |
| Inter-annotator agreement (κ = 0.78) | §5.2 |
| Overall model performance (macro F1 0.887, micro F1 0.909) | §6.4 |
| Per-entity F1 | §6.5, Table 6.7 |
| Inference latency ~150 ms | §6.8 |
| FastAPI service architecture | §5.6 |
| React frontend architecture | §5.7 |
| Docker Compose deployment | §5.6 |
| UAT methodology and results | §6.10, Table 6.10 |
| Three iteration loops (corpus, schema, loss) | §1.5, §5.3, §6.6 |
| Design-science framing | §1.5 |
| Threats to validity | §6.13 |
| Contributions list | §7.3 |
| Limitations | §7.5 |
| Future work | §7.5 |

For panel questions of the form *"is this the published literature?"*, citation anchors:

- **BERT** — Devlin et al. 2019 (NAACL)
- **Focal loss** — Lin et al. 2017 (ICCV)
- **Inverse-frequency class weighting** — established in NLP literature; Cui et al. 2019 (CVPR) for effective-number refinement
- **Label smoothing** — Szegedy et al. 2016 (Inception paper)
- **AdamW optimiser** — Loshchilov & Hutter 2017
- **BIO encoding** — Tjong Kim Sang & De Meulder 2003 (CoNLL)
- **Span-level F1 (seqeval)** — Nakayama 2018
- **Design science** — Hevner et al. 2004 (MISQ); Peffers et al. 2007 (JMIS)
- **ACLED methodology** — Raleigh, Linke, Hegre, Karlsen 2010 (JPR)
- **GDELT** — Leetaru & Schrodt 2013
- **UAT sample size (Nielsen 5-user rule)** — Nielsen 1993

These citations live in the References section of the thesis.

---

# One last calibration note

The solution is real. The system runs. The metrics are measured. The reproducibility claim is defensible. When you explain *how VioNER solves the problem* in the room, you're not selling a future vision — you're describing a deployed artefact with documented evidence at every step. Speak with the calm authority of someone who built the thing. The architecture, the methodology, and the empirical record all support each other. Trust that, and answer accordingly.
