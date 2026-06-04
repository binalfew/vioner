---
marp: true
theme: vioner-defense
paginate: true
size: 16:9
lang: en
title: VioNER — Knowledge Discovery from Free Text
author: Binalfew Kassa
math: katex
style: |
  /* Inline style hook; theme.css carries the heavy lifting. */
---

<!-- _class: title -->
<!-- _paginate: false -->

# Knowledge Discovery from Free Text
## A BERT-Based System for Extracting Violent-Event Information from African News Reports

---

**Binalfew Kassa**
M.Sc. Thesis Defense · Department of Computer Science · Addis Ababa University

Advisor: *[Advisor Name]*  ·  May 2026

<!--
Open with the title. Greet the panel by name. One sentence: "Good morning, distinguished examiners. I'm Binalfew Kassa, and the work I'll be presenting today builds an end-to-end system for extracting structured information about violent events in Africa from English-language news reports." Pause. Do NOT read the title slide. Move to outline within 30 seconds.
-->

---

## Outline

1. **Problem** — the information bottleneck in African conflict monitoring
2. **Research questions** — what this thesis set out to answer
3. **Gap** — where existing tools stop short
4. **Approach** — entity schema, taxonomy, BERT, knowledge base
5. **System** — architecture and processing pipeline
6. **Results** — what the evaluation shows
7. **System in use** — UI screens and user-acceptance testing
8. **Contributions, limitations, future work**

<!--
Walk the panel through the structure in roughly 45 seconds. Emphasise that the talk has three centres of gravity: the problem framing, the methodological choices, and the evaluation. Mention that there is a backup deck after slide 26 with deeper detail on anything they want to drill into. Cue them to interrupt with clarifying questions even during the talk. Then move on. Do not linger.
-->

---

<!-- _class: divider -->

# 1. The Problem
## Why African conflict monitoring needs structured extraction

---

## A continent-scale information bottleneck

> Over **30,000 violent events** are reported across African news outlets every year. The analyst pipeline that turns this stream into structured records is **manual, slow, and inconsistent**.

- AU Continental Early Warning System, ACLED, and humanitarian agencies all rely on hand-coding free-text articles into structured event records.
- The binding constraint on continental situation awareness is **analyst time**, not data availability.
- Even a partial reduction in the cost of producing one structured record translates almost one-to-one into **faster, broader, more consistent monitoring**.

<!--
This slide sets the stakes. The panel needs to believe two things by the end of it: (1) the problem is real, large, and operational — not just academic; (2) reducing analyst time is the right place to apply machine learning. Mention AU-CEWS by name because it grounds the problem in an actual continental institution. Don't get drawn into ACLED-vs-GDELT methodology comparisons here — that's slide 6's job. Aim for 60 seconds.
-->

---

## The structured-record requirement

**Raw input** — free text article:
> *"On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least 12 soldiers."*

**Required output** — 5W1H structured record:

| Slot | Value |
|:--|:--|
| WHO (perpetrator) | Al-Shabaab |
| WHO (victim) | military convoy / soldiers |
| WHAT (action) | armed attack |
| WHEN | Tuesday |
| WHERE | near Mogadishu (Somalia) |
| HOW (casualties) | at least 12 killed |

*Generic NER misses the African actor and the operational role distinctions.*

<!--
This is the slide that makes the problem concrete. Read the example sentence verbatim — it lands harder than paraphrasing it. Walk the table top to bottom slowly; one beat per row. End with the punchline: generic off-the-shelf NER tagged Al-Shabaab as ORGANISATION (technically correct, operationally useless) and missed the convoy as a victim entirely. That gap is what this thesis closes. Around 75 seconds.
-->

---

<!-- _class: divider -->

# 2. Research Questions
## The four questions this thesis answers

---

## Research questions

**RQ1.** Which entity types in African violent-event news reports can be **reliably grounded** in source text, and what is an appropriate BIO schema?

**RQ2.** How effectively can a fine-tuned BERT model recognise the chosen entities, and what **loss function and sampling strategy** balance per-entity performance under severe class imbalance?

**RQ3.** To what extent does a curated **knowledge base** of African armed groups, conflict locations, and a hierarchical taxonomy improve trustworthiness and downstream utility?

**RQ4.** What **system architecture** allows the model, the KB, and the analytics layer to be operated together by users without machine-learning expertise?

<!--
Four questions, one per beat. RQ1 is about schema design — what we even try to tag. RQ2 is the modelling core — how well the model performs. RQ3 is the KB layer — what curated knowledge buys beyond the model alone. RQ4 is the systems contribution — the often-skipped step that turns a model into an operational capability. Tell the panel that every result slide later in the talk will be marked with the RQ it answers, so they can track the evidence. About 90 seconds.
-->

---

<!-- _class: divider -->

# 3. Related Work and the Gap
## Where prior systems stop and this thesis starts

---

## The related-work landscape

|                          | Generic news domain | Conflict / African context |
|:------------------------|:-------------------|:--------------------------|
| **Classical NER (CRF, LSTM)** | Stanford NER, spaCy | EpiTator (health-events) |
| **Transformer NER (BERT, RoBERTa)** | huggingface defaults | *African NLP work, but few violence-specific* |
| **Structured event databases** | ICEWS, GDELT | **ACLED**, UCDP (hand-coded) |
| **End-to-end deployed extraction** | enterprise products | *— mostly absent in academic literature —* |

<!--
This 2x2 is the most efficient way to position the work. Walk across the rows top-to-bottom. The two cells that matter are bottom-right (ACLED/UCDP are hand-coded, which is exactly the bottleneck this thesis attacks) and the empty cell below it (academic event-extraction work in the African context stops at the model boundary; the operational packaging is missing). VioNER fills that empty cell. Do not name competitors aggressively — examiners often have favourites. About 80 seconds.
-->

---

## The gap this thesis closes

> Most African event-extraction work **stops at the model boundary**. The artefact published is the model; the operational layer — schema, KB, validation, UI, deployment — is treated as an implementation footnote.

This thesis treats the **operational layer as a first-class research output**:

1. A schema chosen for **grounding rate**, not theoretical neatness
2. A **focal-loss + class-weight** training recipe that protects rare entities
3. A curated KB that **validates and enriches** extractions post-hoc
4. A **deployable web platform** for non-ML users

<!--
This is the slide that says what's new. State the gap claim out loud — "stops at the model boundary" — then read each numbered item slowly. The panel will likely probe item 1 (why these eight entities, not the proposal's twenty-six) and item 3 (does the KB actually move the needle). Slide 8 and slide 14 answer both. Don't rush. 75 seconds.
-->

---

<!-- _class: divider -->

# 4. Approach
## Schema · Taxonomy · BIO · Model · Knowledge Base

---

## Entity schema: eight grounded entity types

The original proposal called for **26 entity types**. A grounding pilot in November 2025 measured how many of each could be located **verbatim** in source text. Types below 80% grounding were dropped.

| Group | Entities retained | Dropped (recovered downstream) |
|:--|:--|:--|
| WHO | ACTOR, VICTIM | ORGANIZATION → KB lookup |
| WHAT | ACTION | EVENT_TYPE → taxonomy classifier |
| WHEN | DATE | TIME, DURATION, FREQUENCY |
| WHERE | REGION, CITY, DISTRICT | COUNTRY → KB lookup |
| HOW | CASUALTIES | INJURED, DISPLACEMENT, DAMAGE |
| WHY | *(none supervised)* | MOTIVE, TRIGGER |

**Result:** 8 entities → 17 BIO labels. Every entity type is **reliably supervisable**.

<!--
This slide answers RQ1. The story to tell: I started with the proposal's 26-type schema, ran a grounding pilot, and discovered that types like MOTIVE and TRIGGER were almost never present verbatim — annotators were inferring them from context. Training on inferred-not-grounded labels would have introduced systematic noise. So those types were dropped from the NER schema and recovered downstream: EVENT_TYPE from the action verb plus the taxonomy classifier; COUNTRY from a KB lookup off the most-specific WHERE entity. Eight grounded entities train cleanly, and the taxonomy and KB pick up the rest. The panel may push on this — "you reduced the schema; isn't that a weakening of the contribution?" Reply: it's a strengthening, because every label now has a ground-truth signal. 100 seconds.
-->

---

## Four-level hierarchical taxonomy

![h:430 center](assets/taxonomy_summary.png)

Levels 0–2 shown. **~95 terminal categories** at Level 3; full tree in Annex B and backup slide B5.

Synthesises ACLED, UCDP, and PMVE — adds African-specific extensions (**pastoralist–farmer clashes**, **communal cattle raiding**).

<!--
Show the figure. Walk left to right: the root (Violent Events Taxonomy), the four Level-1 families (Political, Criminal, Communal, State), then the Level-2 children. Tell the panel that the taxonomy isn't just a relabelling of ACLED — it adds two African-specific categories that none of the existing frameworks cover at this granularity. Pastoralist-farmer clashes alone account for a measurable fraction of Sahel reporting and don't sit cleanly in ACLED's "Violence against civilians" bucket. The L3 leaves are in Annex B; you can flip to backup B5 if asked. 80 seconds.
-->

---

## BIO encoding: why this scheme

**Example.** Sentence: *"Al-Shabaab fighters attacked a convoy"*

```
Al        B-ACTOR
-         I-ACTOR
Shabaab   I-ACTOR
fighters  I-ACTOR
attacked  B-ACTION
a         O
convoy    B-VICTIM
```

**Why BIO over BIOES?** Adjacent-but-distinct entities decode unambiguously with only `2k+1` labels (17 here vs 33 for BIOES) — half the head, smaller class-imbalance burden, same expressive power for the 95+ % of cases that matter here.

<!--
This is the slide that addresses advisor comment C444. The panel may not care deeply about BIO vs BIOES, but if they ask, the answer is precise: BIOES (begin/inside/outside/end/single) doubles the label space without giving us anything we need, because African news reports almost never have adjacent same-type entities with no intervening token. BIO is sufficient and trains faster. Read the code block carefully — the I-ACTOR continuation across the hyphen is the kind of case students often get wrong, and showing it right signals you've thought about this. 70 seconds.
-->

---

## System architecture (RQ4)

![h:520 center](assets/architecture.png)

<!--
Walk down the stack. React + TypeScript at the top — this is what the analyst sees. FastAPI in the middle — a thin Python service exposing seven route groups (training, inference, events, analytics, KB, auth, system). The NER component and the knowledge base are loaded once into the FastAPI process so inference is in-memory and fast. PostgreSQL at the bottom holds the persistent state: stored events, training runs, user accounts. Docker Compose orchestrates the whole thing for reproducible local deployment. The clean separation is what lets the panel believe a non-ML user can drive it. 70 seconds.
-->

---

## End-to-end processing pipeline

![h:520 center](assets/process_flow.png)

<!--
This is the per-document story. The analyst pastes an article. Step 2: WordPiece tokenisation produces the input the BERT head expects. Step 3: forward pass returns per-token softmax distributions over 17 labels. Step 4: BIO decode collapses token tags into spans. Step 5: confidence filtering drops spans whose averaged subtoken probability sits below a per-category threshold. Step 6: 5W1H grouping aggregates spans by category. Step 7: the KB validates ACTOR and CITY against curated reference data. Step 8: the taxonomy classifier assigns a Level-1 to Level-3 path from the ACTION verb. Step 9: persist. Step 10: render. End-to-end on CPU is ~150 ms per typical article. 90 seconds.
-->

---

## Training recipe: focal loss + class weights

**Backbone.** `bert-base-cased` fine-tuned end-to-end, 17-label token-classification head.

**Loss.** Focal Loss with inverse-frequency class weights:

$$\mathcal{L}_{\text{focal}}(y, \hat{y}) = -\sum_c w_c \cdot (1 - \hat{y}_c)^{\gamma} \log \hat{y}_c$$

with $\gamma = 2.0$, $w_c \propto 1/\text{freq}(c)$.

**Why both.** Class weights *raise the gradient* for rare classes; focal loss *suppresses easy-negative gradients*. The two are **complementary**, not redundant — Section 6.6 ablation confirms this empirically.

<!--
Loss function is the technical heart of the work. The intuition: 78% of all tokens are O (outside any entity). Plain cross-entropy treats those as equal to actual entity tokens, so the gradient signal for rare classes like VICTIM gets drowned out. Class weights scale up the rare-class gradients. Focal loss further down-weights the easy correct O predictions so the model spends more capacity on hard cases. Crucially, in the ablation on slide 18, focal alone gets us partway, weights alone get us partway, but the combination gets us further than either — they are complementary. This is RQ2's headline answer. 100 seconds.
-->

---

## Knowledge base as validation + enrichment layer (RQ3)

**Curated content.**
- ~150 African armed groups (canonical, aliases, country, group type)
- ~200 conflict-affected cities mapped to country and region
- 54 African countries; weapons catalogue

**Two roles in the pipeline.**

| Role | Mechanism | Effect |
|:--|:--|:--|
| **Validate** | confirm/flag spans against KB | 2.4 % flag rate on extracted events |
| **Enrich** | attach canonical name, country, type | 64.3 % ACTOR enrichment rate |

*Mismatches lower event confidence — surfaces records for analyst re-read.*

<!--
This slide answers RQ3. The KB is the layer most papers skip. It plays two roles. First, validation: when the model extracts "Al-Shabaab fighters" and "Goma" in the same sentence, the KB knows Al-Shabaab operates in Somalia, not eastern DRC; the validator flags the event as geographically implausible. That flag rate is 2.4 % — small in aggregate but exactly the events an analyst should re-read. Second, enrichment: "Al Shabaab", "al-shabaab", "Al-Shabaab militants" all canonicalise to a single key — 64.3 % of ACTOR mentions get enriched this way, which is what lets the analytics layer count correctly. 100 seconds.
-->

---

## Dataset and annotation protocol

| Source | Examples |
|:--|--:|
| ACLED open-data export (stratified diversity sample) | 35,000 |
| Template-based augmentation (rare-class coverage) | 15,000 |
| **Total fine-tuning corpus** | **50,000** |

**Splits.** 80 / 20 train/validation, stratified on entity-type presence.

**Annotation.** Two-stage gold pipeline projected from ACLED's structured columns onto free-text notes; spot-checked manually.

**Class imbalance.** ~78 % O · ~22 % entity. Within entities, ACTOR + CITY + DATE dominate; VICTIM, ACTION, CASUALTIES single-digit-%.

<!--
Three honest beats here. (1) Where the data comes from: ACLED open data, filtered by stratified diversity sampling rather than naive random sampling, because the full 212,000-event extract had so much repetition of common phrasings that rare entities got drowned out — I learned that the hard way in October 2025. (2) Why augmentation: template-based filling of the rare-class gap, ~15k synthetic examples to lift VICTIM, ACTION, CASUALTIES off the floor. (3) Class imbalance: the central modelling challenge — 78 % outside tokens, with the operationally most important entities being the rarest. This is what motivates focal loss + class weights from slide 13. 90 seconds.
-->

---

## Training configuration

| Hyperparameter | Value | Source |
|:--|:--|:--|
| Backbone | `bert-base-cased` | Domain default |
| Batch size | 16 | Architecture-driven (memory) |
| Learning rate | 5 × 10⁻⁵ | BERT-NER literature |
| Warmup ratio | 0.1 | Empirically established |
| Scheduler | Linear warmup → ReduceLROnPlateau | Empirically established |
| Focal γ | 2.0 | BERT-NER literature |
| Class weights | inverse-frequency | Empirically established |
| Max epochs | 10 | Empirically (best converges in 2) |
| Early stopping | val loss, patience 2 | Standard practice |

<!--
Show the table briefly. Tell the panel that values are categorised by source — defaults inherited from BERT-NER literature, architecture-driven choices like batch size, and values that came from empirical grid search. This is the slide that closes advisor comment C472. The full hyperparameter table is in backup B1 if they want to drill in. Crucially, the best model converges in 2 epochs — short training runs make it cheap to iterate. 75 seconds.
-->

---

<!-- _class: divider -->

# 5. Results
## Evidence for each research question

---

<!-- _class: stat -->

## Overall performance — held-out validation set

<div class="big">0.909</div>

<div class="caption">micro F1 across 190,075 gold spans · macro F1 = 0.887 · token accuracy = 96.7 %</div>

<!--
This is the headline number. Read it slowly. 0.909 micro F1 on a held-out 10,000-example validation set with 190,075 gold spans. Macro F1 is 0.887, which is the right number for assessing balance — because the macro average weights every entity type equally, including the rare ones. Token accuracy is 96.7 %, but that's the least informative of the three because the O class dominates. Don't oversell this slide. Move on within 30 seconds — the per-category breakdown on the next slide is what actually answers RQ2.
-->

---

## Per-entity F1 — held-out validation set

| Entity | Support | Precision | Recall | F1 |
|:--|--:|--:|--:|--:|
| DATE | 31,938 | 0.961 | 0.952 | **0.956** |
| CITY | 44,361 | 0.941 | 0.928 | **0.934** |
| ACTOR | 47,612 | 0.929 | 0.917 | **0.923** |
| REGION | 24,331 | 0.902 | 0.881 | **0.891** |
| CASUALTIES | 4,907 | 0.901 | 0.869 | **0.885** |
| ACTION | 9,963 | 0.881 | 0.852 | **0.866** |
| DISTRICT | 21,471 | 0.842 | 0.811 | **0.826** |
| VICTIM | 5,492 | 0.838 | 0.798 | **0.817** |
| **Macro** | — | **0.899** | **0.876** | **0.887** |

<!--
Walk the table top to bottom. DATE wins by a clear margin — date expressions follow a small set of recognisable patterns. ACTOR, CITY, DATE form a strong cluster: distinctive surface forms and rich training distribution. Then a middle tier — REGION, CASUALTIES, ACTION around 0.87-0.89, with compositional irregularity the main drag. The bottom of the table is the honest story: DISTRICT at 0.826 loses to mutual confusion with CITY and REGION; VICTIM at 0.817 is both the rarest entity and the one with the most variable phrasing ("civilians", "ten villagers including women and children", "Christian worshippers"). The macro F1 of 0.887 is the number to remember: every entity, including the rarest, is usable operationally. 100 seconds.
-->

---

## Ablation: focal loss + class weights vs alternatives

| Entity | Plain CE | Weighted CE | Focal (γ=2) | **Focal + weights** |
|:--|--:|--:|--:|--:|
| ACTOR | 0.914 | 0.918 | 0.920 | **0.923** |
| ACTION | 0.794 | 0.834 | 0.842 | **0.866** *(+0.072)* |
| VICTIM | **0.708** | 0.776 | 0.792 | **0.817** *(+0.109)* |
| CASUALTIES | 0.853 | 0.871 | 0.872 | **0.885** |
| **Macro** | 0.855 | 0.873 | 0.878 | **0.887** |

> **VICTIM gains +11 F1 points** over plain CE. **ACTION gains +7**. No entity is hurt.

<!--
This is the ablation that answers RQ2 directly. Show that the combination of focal loss with inverse-frequency class weights isn't just decoration — it materially moves the entities that matter most operationally. VICTIM is up 10.9 F1 points; ACTION is up 7.2. The bonus point is that NO entity is hurt by this loss choice — focal loss doesn't trade common-class accuracy for rare-class accuracy, which would have been a regression. Each ingredient on its own helps a little; the two together help more than the sum of parts. That complementarity is what justifies the slightly more complex loss in production. 90 seconds.
-->

---

## Location confusion patterns (Table 6.11)

*Rows are gold; columns are predicted. Diagonal omitted (= correct).*

| Gold \ Predicted | CITY | REGION | DISTRICT |
|:--|--:|--:|--:|
| CITY | — | 0.05 | 0.04 |
| REGION | 0.08 | — | 0.06 |
| DISTRICT | 0.07 | 0.09 | — |

- **DISTRICT** is the hardest: confused with both CITY (0.07) and REGION (0.09)
- Hard cases: places that are both city and provincial capital — *Goma* (city) and *North Kivu* (province)
- Future work: explicit boundary refinement via a span-level CRF or biaffine head (backup B12)

<!--
The error analysis ran over 300 validation events that the model got wrong. The single biggest error category — 38 % — is boundary mismatch: right entity type, wrong span ("12 civilians" instead of "at least 12 civilians"). The second biggest is location-type confusion, which is what this table shows. DISTRICT is the toughest because many African districts share names with their main city or with the region they sit in. Goma is the canonical example — it's a city, a district capital, and effectively the centre of North Kivu province all at once. The model defaults to CITY for ambiguous cases, which is more often right than wrong, but it produces a consistent stream of confusions. The fix is in future work: a span-level CRF on top of the BERT representations. 90 seconds.
-->

---

<!-- _class: divider -->

# 6. System in Use
## The platform users actually interact with

---

## Inference and event-browsing screens

<div class="columns">
<div>

![w:100%](assets/screenshot_d1_inference.png)
*D.1 · Inference: paste article → 5W1H entity chips*

</div>
<div>

![w:100%](assets/screenshot_d5_event_browser.png)
*D.5 · Event browser: filter, sort, paginate*

</div>
</div>

<!--
Walk through both screens quickly. D.1 — analyst pastes an article into the left pane, gets colour-coded entity chips on the right, grouped by 5W1H category. This is the screen that closes the loop on the analyst's primary task. D.5 — once events are persisted, the analyst can filter by date range, country, taxonomy level, perpetrator. Pagination, sortable columns, exportable CSV. These screens were tested in UAT and scored 4.6 / 5 on the "5W1H structuring was clear" item. 80 seconds.
-->

---

## Training and analytics screens

<div class="columns">
<div>

![w:100%](assets/screenshot_d4_training_detail.png)
*D.4 · Live training: loss curve + per-epoch log*

</div>
<div>

![w:100%](assets/screenshot_d7_analytics.png)
*D.7 · Analytics: KPI cards + temporal trends*

</div>
</div>

<!--
D.4 — a non-ML user kicks off a training run, picks the dataset, the loss function, hyperparameters. They watch the loss curve update via WebSocket as epochs complete. The training service runs the job asynchronously; the user can navigate away and come back. D.7 — analytics dashboard pulls aggregated stats from the event store: events per country, per taxonomy bucket, per actor, per month. This is the screen that turns the extracted records back into operational insight. Both screens were demonstrated in UAT with positive responses; the most common request was an exportable PDF brief from D.7, which is now in future work. 90 seconds.
-->

---

## User acceptance test (n = 5, Likert 1–5)

| Statement | Mean | Std |
|:--|:--:|:--:|
| Extracted entities matched expectations | **4.4** | 0.5 |
| 5W1H structuring was clear | **4.6** | 0.5 |
| Confidence scores were useful for triage | 4.2 | 0.4 |
| KB enrichment added value | **4.6** | 0.5 |
| Training screen was easy to use | 4.0 | 0.7 |
| Analytics answered analyst-style questions | 4.2 | 0.4 |

**All 5 participants completed all 6 tasks.** *(2 EW analysts · 1 academic · 2 NLP developers)*

<!--
This is the slide that closes RQ4. Five participants — two early-warning analysts (the primary intended audience), one academic conflict researcher (secondary), and two NLP developers unfamiliar with the application domain (a fairness check). All five completed all six tasks: run inference on three supplied articles, browse the event store, run an analytics query, train a model on a supplied dataset, monitor training to completion, review a flagged event. The Likert numbers all clear 4.0. The two highest items — 5W1H structuring clarity (4.6) and KB enrichment value (4.6) — are exactly the two things this thesis claims as differentiating contributions. The lowest is training-screen ease at 4.0; constructive feedback there fed directly into future work. 100 seconds.
-->

---

<!-- _class: divider -->

# 7. Contributions, Limitations, Future Work

---

## Contributions

1. **An eight-entity BIO schema with grounding-based inclusion rules** — every label is verifiably present in source text (Annex A).
2. **A four-level taxonomy of African violent events** (~95 terminal categories) extending ACLED / UCDP / PMVE with African-specific extensions.
3. **A reproducible training recipe** — focal loss + inverse-frequency weights — that lifts VICTIM by **+11 F1**, ACTION by **+7 F1**, without hurting other entities.
4. **A curated knowledge base** (150 armed groups · 200 cities · 54 countries · weapons) used for validation **and** enrichment.
5. **A deployable web platform** — FastAPI + React + PostgreSQL, end-to-end documented and reproducible under Docker Compose.

<!--
This is the slide that gets quoted in the panel's decision. Each item is a self-contained artefact: the schema, the taxonomy, the training recipe, the knowledge base, the system. Tell the panel which artefacts are reusable beyond this dissertation — all five, but especially the taxonomy and the KB, which any other researcher working on humanitarian protection, conflict early-warning, or peace and security analysis can pick up without rebuilding. The fifth item — the system — is the contribution the related-work landscape on slide 6 said was missing. 100 seconds.
-->

---

## Limitations (honest)

1. **English-language only.** A large share of African conflict reporting is in French, Arabic, Portuguese, and African languages. Monolingual extractor leaves that signal on the floor.
2. **~30 % of training data is template-augmented.** Validation drawn from the same combined corpus → estimates in-distribution performance, not out-of-distribution.
3. **No comparison against a learned event-type head.** EVENT_TYPE is recovered post-hoc by a rule-based taxonomy classifier; a learned hierarchical classifier was scoped out.
4. **Knowledge-base coverage decays without curation.** Armed groups change names, splinter, recombine. A stale KB does worse than no KB.

<!--
This is the most important slide for surviving Q&A. Owning the limitations first disarms hostile questions later — examiners cannot attack what you have already conceded. Be specific. English-only is the biggest gap, multilingual extension is the first item in high-priority future work. Template augmentation: be honest that 30 % synthetic is a real caveat — the validation metrics are a fair estimate of in-distribution performance, but don't guarantee out-of-distribution behaviour on social media or translated text. The third item is the one a panel methodologist will probe most aggressively — the learned hierarchical classifier was scoped out, but is the second high-priority future-work item. 110 seconds.
-->

---

## Future work — three highest-priority directions

| # | Direction | Rationale |
|:--|:--|:--|
| 1 | **Multilingual extension** (XLM-R / AfroLM) | Closes the largest operational gap |
| 2 | **Learned hierarchical event classifier** (replaces rule-based taxonomy step) | Scales as the taxonomy grows |
| 3 | **Natural-language QA over the event store** (templated SQL or fine-tuned Seq2Seq) | Closes the loop for non-technical analysts |

*Medium / lower priority items in Chapter 7.5: active-learning loop · coreference resolution · PDF-brief generator · streaming · multimodal · predictive analytics.*

<!--
Three priorities, each tied back to a limitation. Multilingual is item 1 because it closes the biggest operational gap — about half of African conflict reporting is in non-English languages. Item 2, the learned hierarchical classifier, addresses limitation 3 and would scale as the taxonomy grows beyond ~95 leaves. Item 3, natural-language QA, is the user-facing capability that closes the loop for non-technical analysts who want to ask "show me all events attributed to JNIM in the last 30 days" without writing SQL. The fact that the future work is mostly incremental engineering rather than fundamental research is itself a contribution claim: the hard methodological choices were made in this thesis. 90 seconds.
-->

---

<!-- _class: title -->

# Thank you

## Questions welcome

---

**Binalfew Kassa**
M.Sc. Thesis Defense · AAU Department of Computer Science · May 2026

*Code, thesis, and supplementary materials available on request.*

<!--
Thank the panel by name. Invite questions. Let the silence sit — do not rush to fill it. When the first question lands, breathe before answering; the worst defense answers are the ones rushed in the first three seconds. If you don't know the answer, say so explicitly and offer what you do know; bluffing is the single most damaging behaviour in a defense. Remember: backup slides B1–B12 follow this one. If a question needs supporting evidence, name the backup slide and present it. End of main deck.
-->

---

<!-- _class: backup -->

# Backup
## B1–B12 supporting detail for Q&A

---

## B1 · Full hyperparameter table

| Hyperparameter | Value |
|:--|:--|
| Backbone model | `bert-base-cased` (110M parameters) |
| Token-classification head | 17 labels (8 entities × BI + O) |
| Max sequence length | 128 tokens (mean article: 64) |
| Batch size | 16 (training), 32 (eval) |
| Optimizer | AdamW (β₁=0.9, β₂=0.999, ε=1e-8) |
| Learning rate | 5 × 10⁻⁵ |
| Weight decay | 0.01 |
| Warmup ratio | 0.1 of total steps |
| LR scheduler | Linear → ReduceLROnPlateau (factor 0.5, patience 1) |
| Gradient clipping | max-norm 1.0 |
| Focal loss γ | 2.0 |
| Class weights | inverse-frequency (per-label) |
| Max epochs | 10 |
| Early stopping | val loss, patience 2 |
| Random seed | 42 (also 17 and 91 for variance) |
| Hardware | Apple M2 Max (MPS), 32 GB |

---

## B2 · Per-epoch loss and validation accuracy

| Epoch | Train loss | Val loss | Token acc | Macro F1 |
|:--:|--:|--:|--:|--:|
| 1 | 0.0231 | 0.0118 | 95.2 % | 0.823 |
| **2** | **0.0094** | **0.0074** | **96.7 %** | **0.887** |
| 3 | 0.0061 | 0.0079 | 96.6 % | 0.885 |
| 4 | 0.0044 | 0.0089 | 96.5 % | 0.881 |
| 5 | 0.0033 | 0.0102 | 96.3 % | 0.875 |

Best model: **epoch 2** (early-stopped). Subsequent epochs over-fit the training set while validation loss climbs.

---

## B3 · Algorithm 4.1 — Sub-word label alignment for BIO

```
INPUT:  tokens     T = [t1, ..., tn]      (word-level tokens)
        labels     L = [l1, ..., ln]      (word-level BIO labels)
        tokenizer  WordPiece tokenizer
OUTPUT: aligned    L' = [l'1, ..., l'm]   (sub-word level, m >= n)

 1: L' <- []
 2: for i = 1 to n do
 3:    subwords <- tokenizer.tokenize(t_i)
 4:    for j = 1 to len(subwords) do
 5:       if j = 1 then
 6:          L'.append(l_i)                  // first subword carries label
 7:       else if l_i starts with "B-":
 8:          L'.append("I-" + l_i[2:])       // B- becomes I- for continuations
 9:       else:
10:          L'.append(l_i)                  // I- and O propagate as-is
11:    end for
12: end for
13: return L'
```

*The B-to-I transition (line 7-8) is the subtle case most implementations get wrong.*

---

## B4 · Algorithm 4.5 — Post-NER 5W1H structuring (overview)

**Phase 1 · Token classification.** Forward pass through fine-tuned BERT → per-token softmax over 17 labels.

**Phase 2 · BIO span construction.** Collapse contiguous B/I sequences into spans; compute averaged sub-token confidence per span.

**Phase 3 · Confidence filtering and 5W1H grouping.** Drop spans below per-category threshold; bucket surviving spans into WHO / WHAT / WHEN / WHERE / HOW.

**Phase 4 · KB enrichment and taxonomy.** Lookup ACTORs and CITYs against the KB → attach canonical names, country, group type; classify the ACTION verb plus context into Level 1–3 taxonomy path.

*Full pseudocode: §4.7 of the thesis.*

---

## B5 · Full taxonomy hierarchy (Annex B)

![h:540 center](assets/taxonomy_annex.png)

*~95 terminal categories. Colour by Level-1 family.*

---

## B6 · Per-entity precision, recall, F1 (all eight)

| Entity | Support | Precision | Recall | F1 | Δ vs plain CE |
|:--|--:|--:|--:|--:|--:|
| DATE | 31,938 | 0.961 | 0.952 | 0.956 | +0.003 |
| CITY | 44,361 | 0.941 | 0.928 | 0.934 | +0.005 |
| ACTOR | 47,612 | 0.929 | 0.917 | 0.923 | +0.009 |
| REGION | 24,331 | 0.902 | 0.881 | 0.891 | +0.012 |
| CASUALTIES | 4,907 | 0.901 | 0.869 | 0.885 | +0.032 |
| ACTION | 9,963 | 0.881 | 0.852 | 0.866 | **+0.072** |
| DISTRICT | 21,471 | 0.842 | 0.811 | 0.826 | +0.018 |
| VICTIM | 5,492 | 0.838 | 0.798 | 0.817 | **+0.109** |

*Rare entities benefit the most — VICTIM by 11 F1 points.*

---

## B7 · Sample inference output (JSON)

```json
{
  "article_id": "art-20260112-007",
  "extracted": {
    "WHO": {
      "perpetrator": {"text": "Al-Shabaab fighters", "kb_id": "ag-007",
                      "canonical": "Al-Shabaab", "country": "SOM",
                      "type": "jihadist"},
      "victim": {"text": "12 soldiers", "confidence": 0.91}
    },
    "WHAT": {"action": "attacked", "event_type_l1": "Political Violence",
             "event_type_l2": "Terrorism", "event_type_l3": "Armed Assault"},
    "WHEN": {"date_text": "Tuesday", "normalised": "2026-01-09"},
    "WHERE": {"city": "near Mogadishu", "country": "SOM",
              "kb_match": true, "geo_consistent": true},
    "HOW": {"casualties": {"killed": 12, "qualifier": "at least"}},
    "confidence": 0.88,
    "flags": []
  }
}
```

---

## B8 · Knowledge-base composition

| KB collection | Records | Source |
|:--|--:|:--|
| African armed groups | 153 | ACLED actor list + manual curation |
| Aliases per group (mean) | 4.2 | Manual curation |
| Conflict-affected cities | 207 | ACLED location field, top-frequency |
| African countries | 54 | ISO 3166-1 |
| Weapons / weapon categories | 38 | UCDP weapons catalogue |
| Taxonomy nodes (Levels 0–3) | ~120 | This work (§4.4) |

---

## B9 · Comparison against off-the-shelf baselines

*Same held-out validation set, span-level F1 on the 4-entity overlap (PER, LOC, MISC, DATE):*

| System | PER (≈ACTOR) | LOC (≈CITY) | DATE | Macro F1 |
|:--|--:|--:|--:|--:|
| spaCy `en_core_web_lg` | 0.71 | 0.74 | 0.81 | 0.75 |
| Stanford CoreNLP NER | 0.69 | 0.72 | 0.80 | 0.74 |
| HuggingFace `dslim/bert-base-NER` | 0.78 | 0.81 | 0.86 | 0.82 |
| **VioNER (this work)** | **0.92** | **0.93** | **0.96** | **0.94** |

*Caveat: out-of-domain comparison — none of the baselines saw African armed groups in pre-training.*

---

## B10 · Annotation disagreement examples

| Sentence fragment | Annotator A | Annotator B | Resolution |
|:--|:--|:--|:--|
| "killing at least 12 civilians" | CASUALTIES = "12 civilians" | CASUALTIES = "at least 12 civilians" | Include qualifier → B |
| "in eastern DRC" | REGION = "eastern DRC" | COUNTRY (dropped) | Eastern descriptor → REGION |
| "the al-shabaab" | ACTOR | ACTOR (lowercase tagged) | Case-insensitive → A |
| "the bus driver's family" | VICTIM | not annotated | Surface-form rule → VICTIM |

*IAA (Cohen's κ on a 200-doc pilot): 0.78 — substantial agreement; below 0.85 perfect agreement floor.*

---

## B11 · Error analysis — false-positive examples

| Predicted span | Type | Why wrong |
|:--|:--|:--|
| "this morning" | DATE | Vague temporal phrase, no anchor — should be untagged |
| "the convoy" | VICTIM | Generic NP, no specific victim — should be untagged |
| "Goma" (in "Goma football team") | CITY | Correct token, wrong context (sports team metaphor) |
| "Kinshasa region" | REGION | Should be DISTRICT (Kinshasa is a city-province) |

*Raising the WHEN threshold to 0.85 eliminates most "this morning"-class errors at cost of 1.2 F1 on legitimate DATE recall.*

---

## B12 · Error analysis — false-negative examples

| Missed span | Type | Why missed |
|:--|:--|:--|
| "Christian worshippers" | VICTIM | Religious-group framing absent from training |
| "were ambushed" | ACTION | Passive-voice action verb under-represented |
| "internally displaced schoolgirls" | VICTIM | Compositional, specific, rare in ACLED notes |
| "the bus driver's family" | VICTIM | Possessive construction not in templates |

*Future-work target: span-level CRF + boundary refinement (§7.5 high priority item 4).*

---

<!-- _class: backup -->

# End of backup deck

*Main deck: slide 1–26. Backup: B1–B12. Speaker notes: `speaker_notes.md`. Q&A kit: `qa_kit.md`.*
