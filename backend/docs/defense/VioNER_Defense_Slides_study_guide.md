# VioNER Defense — Study Guide for the 22-Slide Deck

A study companion to `VioNER_Defense_Slides.pptx`. For each slide, this guide gives you:

1. **What's on the screen** — the visual you're presenting
2. **What to say (verbatim)** — the polished delivery script
3. **Why this slide is in the talk** — its purpose in the arc
4. **Key terms and numbers** — quick reference for unfamiliar jargon
5. **If a panellist asks...** — anticipated probes with prepared answers
6. **Pivot to next slide** — the bridge sentence

Read top to bottom once to internalise the arc. Then practice slide-by-slide using just the verbatim script, falling back to the "If a panellist asks" section when you anticipate probes. The night before, skim only the "What to say" and "Pivot" blocks across all 22 slides — that's your delivery rehearsal.

---

## Pacing target across all 22 slides

| Section | Slides | Target time | Cumulative |
|:--|:--|:--|:--|
| Opening | 1-2 | 1:30 | 1:30 |
| Problem & stakes | 3-5 | 4:30 | 6:00 |
| Competitive landscape & gaps | 6-7 | 3:00 | 9:00 |
| The solution | 8-9 | 3:30 | 12:30 |
| The contributions | 10-15 | 9:00 | 21:30 |
| Evidence | 16-19 | 5:00 | 26:30 |
| Errors & limits | 20-21 | 2:00 | 28:30 |
| Close | 22 | 1:00 | 29:30 |

**Slack:** ~30 seconds in the 30-min slot. If you hit slide 15 by minute 21 you're on track.

---

## Slide 1 — Title

**Duration target:** 45 seconds

### What's on the screen
Title page: *"VioNER — Violent-event Named Entity Recognition"*, subtitle (system description), your name, advisor, AAU CS Department, date.

### What to say (verbatim)

> *"Good morning, distinguished examiners. I'm Binalfew Kassa. The thesis I'm presenting today is VioNER — Violent-event Named Entity Recognition. It's an end-to-end, deployable system that converts English-language news about violent events in Africa into structured, queryable 5W1H records."*

> *"In the next thirty minutes I'll cover the problem, the four-part contribution, the evidence, and the limits I own honestly. The headline result I want to plant early: micro F1 of 0.909 on held-out data, with rare-entity recovery that actually saves analyst time."*

> *"The frame for the whole talk: a real operational bottleneck, methodologically open in the literature, closed by an integrated artefact I built and evaluated end-to-end."*

### Why this slide is in the talk
First impressions decide whether the panel feels you're confident or rattled. Plant the headline number (0.909) early so the rest of the talk has something to converge to. Frame as *operational bottleneck → methodological gap → integrated artefact* so the panel knows the shape of the argument before details start.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **NER** | Named Entity Recognition — tagging spans of text with what they refer to (person, location, date, etc.) |
| **5W1H** | Journalistic framing — WHO, WHAT, WHEN, WHERE, WHY, HOW |
| **Micro F1 = 0.909** | The headline extraction-quality metric on a 10,000-example held-out validation set |

### If a panellist asks...

- **"How long will you speak?"** → *"About thirty minutes, then I welcome your questions for as long as you need."*
- **"What's the single most important result?"** → *"The micro F1 of 0.909 plus the rare-entity ablation showing VICTIM F1 moves from 0.708 to 0.817 with focal loss and class weights."*

### Pivot to next slide

> *"Here is the roadmap for the next thirty minutes."*

---

## Slide 2 — Roadmap

**Duration target:** 45 seconds

### What's on the screen
The 7-section talk outline: stakes → competitive landscape → four contributions → evidence → limits → deployment path.

### What to say (verbatim)

> *"This is the roadmap. I move from why the problem matters, to why existing tools don't close it, to the four contributions, then the evidence — model metrics, the ablation, KB impact, and user testing — and finally the limits and deployment path."*

> *"One thread ties the whole talk together: each contribution closes one operational gap, and dropping any single piece breaks the chain. The contribution is the integration, not any one component."*

### Why this slide is in the talk
Sets the panel's mental map. Tells them when to expect each kind of evidence so they can park questions until the right section. The "each piece closes a gap" framing is the through-line they'll hear repeatedly.

### Key terms and numbers on this slide

| Term | Means |
|:--|:--|
| **Integration** | The integrated artefact (schema + model + KB + taxonomy + platform) is the contribution; no single piece alone is |
| **Ablation** | A controlled experiment that turns one ingredient off to measure its individual contribution |

### If a panellist asks...

- **"Will you take questions during or only after?"** → *"Either works. I'll pause for clarifying questions when you raise a hand; deeper questions are usually better after the close."*
- **"Why is the integration the contribution?"** → *"Because no published academic work in this domain has integrated all four pieces end-to-end. The empty cell on slide 6 shows that explicitly."*

### Pivot to next slide

> *"Let's begin with why this problem matters operationally."*

---

## Slide 3 — The operational stakes

**Duration target:** 75 seconds

### What's on the screen
Continent-scale numbers (~30,000 events/year, 20+ active conflicts, all 54 countries) plus named institutional consumers: AU-PSC, AU-CEWS, ECOWAS, IGAD, UN OCHA, UNHCR.

### What to say (verbatim)

> *"The operational stakes. About thirty thousand African violent events are reported and coded each year. Twenty-plus active armed conflicts in any given year. All fifty-four countries tracked, roughly thirty with mass-casualty events in 2024."*

> *"This is the operational backbone for the AU Peace and Security Council, the AU early-warning system, ECOWAS, IGAD, UN OCHA, and UNHCR. The point I want to land: this is not an academic curiosity — reduced extraction cost benefits every one of those consumers."*

### Why this slide is in the talk
Establishes problem reality and scale. Without this, the rest of the talk sounds like an academic exercise. Named institutions ground the claim in specific real-world consumers, not abstract "users".

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **AU-PSC** | African Union Peace and Security Council |
| **AU-CEWS** | AU Continental Early Warning System — mandated by Article 12 of the PSC Protocol |
| **ECOWAS** | Economic Community of West African States |
| **IGAD CEWARN** | Intergovernmental Authority on Development; Conflict Early Warning Mechanism |
| **30,000 events/year** | ACLED's African coverage figure; consistent at 28-35k since 2020 |

### If a panellist asks...

- **"Where does the 30k figure come from?"** → *"That's ACLED's African coverage — consistent at 28 to 35 thousand every year since 2020. The order of magnitude is what matters; the exact number varies slightly by data year."*
- **"Why does VioNER matter to AU-CEWS specifically?"** → *"AU-CEWS is mandated by Article 12 of the PSC Protocol to monitor continental conflict. Their analyst capacity is the binding constraint on coverage. Any reduction in per-article cost translates directly into more theatres covered with the same staff."*
- **"Is this only for AU-CEWS?"** → *"No — humanitarian agencies, research groups, and national peace ministries all have analogous pipelines. AU-CEWS is just the most institutionally visible consumer."*

### Pivot to next slide

> *"Let me quantify what 'bottleneck' actually means."*

---

## Slide 4 — The bottleneck, quantified

**Duration target:** 90 seconds

### What's on the screen
Per-article time (15-25 min), the analyst workflow steps (read, identify, cross-reference, narrow location, extract casualties, classify, log), annual analyst-hours (~10,000), FTE equivalent (~5.5).

### What to say (verbatim)

> *"The bottleneck, quantified. Each article takes a trained analyst fifteen to twenty-five minutes — read, identify actors, cross-reference against an internal armed-group list, narrow location from country to city, extract casualties with qualifiers, classify the event type, and log."*

> *"At thirty thousand events that's about ten thousand analyst-hours per year — roughly five and a half full-time analysts whose entire job is article-to-row conversion."*

> *"Key framing: VioNER does not replace analysts — it turns an article-READING task into an article-REVIEWING task. Reviewing is lower cognitive load than coding from blank, so per-article time drops. Even halving it frees three analysts to cover under-monitored theatres."*

### Why this slide is in the talk
Without numbers, "the analyst is slow" is just assertion. With this table the panel sees scale and immediately understands why automation here is high-leverage. The "review not replace" framing is the most important sentence in this slide — it pre-empts any "you're trying to replace people" objection.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **15-25 min/article** | Mean coding time, consistent with ACLED's published coder-throughput documentation |
| **10,000 analyst-hours/yr** | 30,000 × 20 min ÷ 60 |
| **5.5 FTE** | 10,000 / 1,800 (working hours per FTE-year) |
| **FTE** | Full-Time Equivalent — one person working full-time for a year |

### If a panellist asks...

- **"Where do the 15-25 minutes come from?"** → *"Consistent with ACLED's published coder-throughput documentation and confirmed during UAT interviews with two early-warning analysts. With practice it can drop to 10 minutes for routine articles; complex multi-event articles can take 45+ minutes."*
- **"How does VioNER save time concretely?"** → *"By turning reading-from-blank into reviewing-pre-extracted-output. Conservative estimates from comparable NLP-assisted coding workflows in other domains suggest 40-60% time reduction. We don't claim to have measured that in production yet — recommendation 1 in section 7.4 is the controlled pilot study."*
- **"Are you sure analysts won't just be replaced?"** → *"The output is explicitly framed as a triage layer — analysts review and edit before any record is published. The recommendation in section 7.4 explicitly says to treat output as triage, not final."*

### Pivot to next slide

> *"That's the operational problem. The technical problem — why this is harder than generic NER — is the next slide."*

---

## Slide 5 — Why automating this is hard

**Duration target:** 75 seconds

### What's on the screen
Four challenge buckets: domain entities, severe class imbalance, geographic ambiguity, 5W1H grouping with role distinction.

### What to say (verbatim)

> *"Why automating this is harder than generic NER. Four things."*

> *"One — domain entities. Generic models tag Al-Shabaab as a generic ORGANIZATION, don't know JNIM or RSF, and the African armed-group landscape is dynamic — groups splinter, rebrand, recombine."*

> *"Two — severe class imbalance. Seventy-eight percent of tokens are non-entity O, and the operationally critical entities — victim, action, casualties — are the rarest, just a few percent each."*

> *"Three — geographic ambiguity. 'Fighting in Goma' could be city, district, or region. This is why DISTRICT is the weakest entity in the final results."*

> *"Four — 5W1H grouping with perpetrator-versus-victim distinction is not standard NER output. And multi-event articles pack several incidents into one piece, which means the model has to segment as well as extract."*

### Why this slide is in the talk
Pre-empts the "why didn't anyone solve this already?" question. Each challenge motivates a specific contribution: domain entities → KB; class imbalance → focal loss; geographic ambiguity → confusion matrix + future-work CRF; 5W1H grouping → schema design.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Class imbalance** | Some classes have vastly more training examples than others — 78% O vs 3% VICTIM here |
| **JNIM, RSF** | Jama'at Nasr al-Islam wal Muslimin (Sahel jihadist coalition); Rapid Support Forces (Sudanese paramilitary) |
| **Multi-event article** | A single news article that describes more than one separate violent incident |

### If a panellist asks...

- **"How do you know generic NER tags Al-Shabaab as ORG?"** → *"Backup B9 shows the comparison — generic BERT NER models trained on general news tag Al-Shabaab as ORG with ~78% recall. They don't have a perpetrator-versus-victim distinction at all."*
- **"How rare is VICTIM exactly?"** → *"About 5,500 spans in a corpus of 50,000 examples, which works out to roughly 1-2% of tokens. ACTOR has about 47,000 spans, nearly 10x more."*
- **"What's the multi-event approach?"** → *"Sentence-level segmentation in section 4.7 of the thesis. Each sentence is processed independently, and the post-NER 5W1H grouper bundles per-sentence extractions. Cross-sentence event-linking is medium-priority future work."*

### Pivot to next slide

> *"Given those challenges, where do existing systems land?"*

---

## Slide 6 — The competitive landscape

**Duration target:** 90 seconds

### What's on the screen
The 2×2 matrix or systems-comparison table: ACLED, UCDP, ICEWS, GDELT, generic NER, prior African NLP, LLMs. Empty cell highlighted in the lower-right.

### What to say (verbatim)

> *"The competitive landscape as a matrix."*

> *"ACLED and UCDP are the gold standard but hand-coded — they are the TARGET of this work, not competitors. I train on ACLED open data."*

> *"ICEWS and GDELT are automated, but they use generic CAMEO schemas, not Africa-tuned 5W1H, and they're closed or noisy."*

> *"Generic NER doesn't know African armed groups. Prior African NLP — Masakhane, AfriBERTa — stops at the model boundary, no operational packaging."*

> *"LLMs are disqualified on four operational grounds: closed weights, per-call cost, no auditability, and data sovereignty — sending conflict metadata to a US commercial API is a non-starter for many AU member states."*

> *"VioNER occupies the empty cell: African, automated, open, and operational."*

### Why this slide is in the talk
Positions VioNER against the landscape with named systems. The "empty cell" is the gap claim made visible. Naming LLM disqualifiers explicitly pre-empts the "why not just use GPT-4?" question that almost always comes up.

### Key terms and numbers on this slide

| Term | Means |
|:--|:--|
| **ACLED** | Armed Conflict Location & Event Data — hand-coded African conflict database |
| **UCDP** | Uppsala Conflict Data Program — hand-coded with stricter inclusion |
| **ICEWS** | Integrated Crisis Early Warning System — Lockheed/DARPA, closed |
| **GDELT** | Global Database of Events, Language and Tone — pattern-based, planetary scale |
| **CAMEO schema** | Conflict and Mediation Event Observations — generic event-coding scheme |
| **Masakhane, AfriBERTa** | African-language NLP projects/models |

### If a panellist asks...

- **"Why not use GPT-4 or Claude directly?"** → *"Four operational disqualifiers: closed weights mean the vendor can update silently and break our reproducibility; per-call cost scales with volume; we can't audit the inference path; and data sovereignty rules it out for AU member states. LLMs remain a credible future baseline to compare against, but not a substitute for an auditable on-prem system."*
- **"How does VioNER compare against ICEWS?"** → *"Direct comparison isn't possible — ICEWS uses CAMEO event codes, VioNER uses 5W1H structured records. Different output schemas. Backup B9 compares against generic BERT NER models on the entity-tag overlap."*
- **"Isn't ACLED's hand-coding actually better quality?"** → *"Yes — and that's why I train on it. ACLED is the target, not the competitor. The bottleneck is throughput, not quality."*

### Pivot to next slide

> *"Each shortfall in that landscape maps to one of four operational gaps."*

---

## Slide 7 — The four operational gaps

**Duration target:** 90 seconds

### What's on the screen
Four-row table: Gap 1 (fast structured 5W1H), Gap 2 (rare-entity recovery), Gap 3 (trust + canonicalisation), Gap 4 (analyst-deployable system).

### What to say (verbatim)

> *"The four operational gaps — the heart of the contribution. I state them operationally, in terms of what the analyst CAN'T get today."*

> *"Gap one: fast, structured, role-distinguished 5W1H output. ACLED has it slowly; automated tools give flat or wrong-shape output."*

> *"Gap two: automated tools recover dates and locations but miss victims, casualties, action verbs."*

> *"Gap three: output isn't sanity-checked against world knowledge or canonicalised across surface forms."*

> *"Gap four: no system an analyst can actually deploy and run without ML expertise."*

> *"If asked 'why four and not three?' — no existing system fills all four, and each is independently necessary for the analyst's job. A perfectly structured output that arrives too late is useless; a fast output that misses victims is useless."*

### Why this slide is in the talk
The heart of the problem statement. Every contribution later in the talk closes one of these gaps. The "independently necessary" framing defends why this is a four-part contribution rather than a single one.

### Key terms and numbers on this slide

| Term | Means |
|:--|:--|
| **Role distinction** | The distinction between perpetrator (ACTOR) and victim (VICTIM); generic NER collapses both into ORG/PER |
| **Surface form** | The exact text used to mention an entity — e.g., "Al-Shabaab" vs "al-shabaab" vs "Al-Shabaab fighters" |
| **Canonicalisation** | Mapping all surface forms of the same entity to a single canonical identifier |
| **World knowledge** | Facts about the world (Al-Shabaab operates in Somalia) that a model doesn't have from text alone |

### If a panellist asks...

- **"Why four and not three or five?"** → *"Each gap is a distinct kind of failure with a distinct fix. Dropping any one breaks the chain: a perfect schema with a slow model is useless; a fast model with no KB produces noise. They are independently necessary."*
- **"Are all four gaps real, or did you construct them to fit your contributions?"** → *"All four are observable in the landscape on slide 6. Gap 1 is ACLED's slowness; Gap 2 is what generic NER misses; Gap 3 is what ICEWS/GDELT don't do; Gap 4 is what the academic literature consistently skips."*
- **"Which gap is most important?"** → *"Operationally, gap 1 — without fast structured output, nothing else helps the analyst. But for the contribution claim, gap 2 (the loss recipe) has the cleanest empirical evidence."*

### Pivot to next slide

> *"With the gaps framed, here's VioNER's response in one slide."*

---

## Slide 8 — VioNER in one slide

**Duration target:** 75 seconds

### What's on the screen
The five-component summary: 8-entity schema, fine-tuned BERT model, curated KB, 4-level taxonomy, deployable platform. Latency callout (~150 ms vs 15-25 min).

### What to say (verbatim)

> *"VioNER in one slide. Five components."*

> *"One — the eight-entity grounding-validated schema. Two — a fine-tuned BERT NER model. Three — a curated knowledge base. Four — a four-level event taxonomy. Five — a deployable web platform."*

> *"End-to-end latency is about a hundred and fifty milliseconds per article on a single CPU core, versus fifteen to twenty-five minutes of manual coding."*

> *"The point I want you to hold: the model is one component. The schema, the KB, the taxonomy, and the platform are what turn a checkpoint on a laptop into a capability an analyst can actually drive."*

### Why this slide is in the talk
The first time the panel sees what VioNER actually IS. Note that this slide does NOT include the headline F1 numbers — they come in slide 16 with proper context. Saying "the model is one component" sets up the integration framing that the rest of the talk builds on.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Fine-tuned BERT** | A pretrained BERT model further trained on the VioNER task |
| **Curated KB** | A hand-built lookup table of armed groups, cities, countries, weapons |
| **4-level taxonomy** | Hierarchical classification of event types (Level 1: family; Level 2: subcategory; Level 3: leaf) |
| **150 ms per article** | End-to-end inference latency on CPU |
| **Checkpoint** | A saved snapshot of trained model weights |

### If a panellist asks...

- **"Why five components and not fewer?"** → *"Each closes one of the four operational gaps; the platform doubles as both the delivery vehicle and the empirical evidence (UAT)."*
- **"What's the most novel component?"** → *"The integration. In isolation, each component has precedent — what's new is combining all four for African violent-event extraction and evaluating end-to-end."*
- **"Is 150 ms fast enough?"** → *"For analyst-paste-an-article use cases, yes — the analyst gets results back before they can look up. For real-time streaming at high throughput, batched inference or GPU deployment would help; that's lower-priority future work."*

### Pivot to next slide

> *"Before the contributions in detail, one slide on methodology — design science and the three iteration loops that produced these components."*

---

## Slide 9 — Design science + three iteration loops

**Duration target:** 90 seconds

### What's on the screen
The Hevner/Peffers design-science cycle (Build → Evaluate → Learn → Refine) plus three iteration loop cards: Corpus, Schema, Loss.

### What to say (verbatim)

> *"Methodology: design science — build, evaluate, learn, refine. I'll walk the three loops by what each one DID, matching the cards on screen."*

> *"Corpus loop: refined the training data from a raw event dump into a curated, diversity-balanced subset, so the model learns from varied phrasing rather than a handful of over-represented common events."*

> *"Schema loop: narrowed the entity set to only what an annotator can locate word-for-word in the source — clean, auditable labels."*

> *"Loss loop: reshaped the training objective to concentrate on the rare, operationally critical entities — victim, action, casualties — rather than the easy majority."*

> *"The point I want to land: each loop was a design decision validated by measurement, not preference. That's what makes this genuine design science."*

> *"If a panellist presses for numbers behind a loop, I have them in reserve — the corpus moved from about two hundred and twelve thousand to a fifty thousand diversity sample; annotator agreement on the grounded schema reached kappa zero point seven eight; the loss change lifted VICTIM by eleven F1 points."*

### Why this slide is in the talk
Defends the methodology before the contribution claims. Pre-empts "is this just engineering?" by showing iteration evidence. The "measurement not preference" line is the key sentence.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Design science** | Research paradigm where the contribution is a built-and-evaluated artefact (Hevner 2004, Peffers 2007) |
| **Iteration loop** | Build → Evaluate → Learn → Refine cycle, repeated as needed |
| **Cohen's κ = 0.78** | Inter-annotator agreement on the grounded 8-entity schema |
| **212k → 50k** | The corpus reduction from full ACLED extract to stratified diversity sample |
| **+11 F1 on VICTIM** | The empirical lift from the loss-function change |

### If a panellist asks...

- **"Why design science and not a controlled experiment?"** → *"Controlled experiments fit single-technique claims. VioNER's claim is about an integrated artefact — schema + model + KB + UI — evaluated across multiple criteria. Design science is the established frame for that kind of contribution. The §6.6 ablation is the embedded controlled experiment within the larger design-science programme."*
- **"How do you know each loop was empirically driven?"** → *"Each closed with a specific measured signal. Corpus loop: rare-entity F1 dropped on the full ACLED extract. Schema loop: grounding pilot scored EVENT_TYPE at 58%. Loss loop: ablation in §6.6 quantified +11 F1 on VICTIM. None was preference-driven."*
- **"What if a loop had failed?"** → *"Each loop's exit criterion was empirical. If the schema loop hadn't produced higher F1 than the proposal schema, I would have kept iterating. The criterion was the criterion."*

### Pivot to next slide

> *"Now the contributions in detail. Starting with the schema."*

---

## Slide 10 — The grounding-validated 8-entity schema

**Duration target:** 75 seconds

### What's on the screen
Two-card layout: left card explains the grounding principle; right card lists the 8 entities mapped to 5W1H slots.

### What to say (verbatim)

> *"Contribution one — the grounding-validated eight-entity schema, and how it maps to the analyst's 5W1H record."*

> *"Lead with the principle on the left card: every entity in the schema is one the model can point to word-for-word in the article, so the analyst can audit each extracted span against the source. Nothing inferred or invented."*

> *"Then the eight types and what they represent. WHO splits into ACTOR and VICTIM — perpetrator versus those harmed, the role distinction generic NER lacks. WHAT is ACTION. WHEN is DATE. WHERE splits into REGION, CITY, DISTRICT. HOW is CASUALTIES — counts with their qualifiers preserved."*

> *"That role-distinguished 5W1H mapping is the contribution — it's the shape of output an analyst can use directly."*

> *"If asked how the schema was arrived at, I can speak to the grounding pilot and the annotator-agreement evidence. But the slide stays on what the eight entities capture, not the selection statistics."*

### Why this slide is in the talk
First substantive contribution. The "every entity is verifiably in the source text" claim is what makes the model's output trustworthy. The role distinction (ACTOR vs VICTIM) is the operational differentiator from generic NER.

### Key terms and numbers on this slide

| Term | Means |
|:--|:--|
| **Grounding** | The fraction of an entity's mentions that can be located *verbatim* in source text |
| **Inferred entity** | An entity that annotators add based on background knowledge rather than reading from text (motive, intent) |
| **Auditable** | Each extracted span points back to a specific token range in the source article |
| **Role distinction** | Perpetrator vs victim — both are "WHO" but serve distinct operational purposes |

### If a panellist asks...

- **"Why these eight and not the proposal's 26?"** → *"The grounding pilot in November 2025 measured per-entity grounding rate. These eight all cleared 80%; eighteen others — including MOTIVE, TRIGGER, EVENT_TYPE — fell below 60% because annotators were inferring them. Training on inferred labels would have introduced systematic noise."*
- **"Where did the dropped entities go?"** → *"EVENT_TYPE comes back through the rule-based taxonomy classifier from the ACTION verb. COUNTRY comes back through KB lookup from the most-specific WHERE entity. The output schema the analyst sees still has those categories — only the training signal changed."*
- **"What's the IAA on this schema?"** → *"Cohen's κ = 0.78 on a 200-document pilot — substantial agreement on the Landis-Koch scale. That's reported in §5.2 and slide 24 of the deck."*

### Pivot to next slide

> *"On top of the schema sits the taxonomy and the training data."*

---

## Slide 11 — The 4-level taxonomy and the corpus

**Duration target:** 75 seconds

### What's on the screen
Left side: taxonomy structure (Level 1 families, Level 2 subcategories, ~95 Level 3 leaves). Right side: corpus composition (35k stratified ACLED + 15k augmented = 50k).

### What to say (verbatim)

> *"The four-level taxonomy and the corpus."*

> *"The taxonomy: four Level-1 families — Political, Criminal, Communal, State Violence Against Civilians — with about sixteen Level-2 subcategories and roughly ninety-five Level-3 leaves. It synthesises ACLED, UCDP, and PMVE at Level 1 for cross-database aggregation, and adds African-specific extensions like pastoralist-farmer clashes and communal cattle raiding that no existing framework carves out at this depth."*

> *"The corpus: fifty thousand examples — thirty-five thousand stratified ACLED examples plus fifteen thousand template-augmented examples targeting the rare classes. Stratified sampling oversamples rare entity types; augmentation lifts rare-class minimums to a level the model can learn from."*

### Why this slide is in the talk
Combines contribution 2 (taxonomy) with the data-pipeline setup. The taxonomy's African-specific extensions are the differentiating claim; the 50,000-example corpus is the data foundation for everything in the evidence section.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **4-level taxonomy** | Hierarchical tree — Level 0 (root) → Level 1 (4 families) → Level 2 (~16) → Level 3 (~95 leaves) |
| **PMVE** | Political Violence and Mass Violence Events ontology |
| **Stratified sampling** | Sampling that preserves or rebalances class proportions — here, oversamples rare entities |
| **Template augmentation** | Synthetic examples generated by filling slot-templates with real-vocabulary entities |
| **Pastoralist-farmer clashes** | Conflicts between herders and farmers, especially in the Sahel — an African-specific category |

### If a panellist asks...

- **"Why 95 leaves?"** → *"Operational granularity. Cross-country count studies query at Level 1 (where ACLED's six categories also live). Operational targeting queries at Level 2 or 3. A flat 95-category schema would be unqueryable; the hierarchy makes it both compact and detailed."*
- **"Why not just use ACLED's existing taxonomy?"** → *"ACLED's six categories are sufficient for cross-country counts but not for operational targeting — distinguishing election violence from post-election violence, or pastoralist-farmer clashes from generic ethnic clashes, matters for the analyst. VioNER's taxonomy synthesises three existing frameworks and adds African-specific extensions."*
- **"Why is 30% of the corpus synthetic?"** → *"To lift the rare-class minimums. VICTIM appears in single-percentage-point shares in raw ACLED; without augmentation the model can't learn it. Limitation 2 in §7.5 acknowledges this and proposes real-news expansion as future work."*

### Pivot to next slide

> *"With the schema and corpus in place, the training recipe is where the modelling contribution lives."*

---

## Slide 12 — The training recipe (focal × weights)

**Duration target:** 90 seconds

### What's on the screen
The focal-loss + class-weights production loss, with two cards showing the role of each ingredient. Maybe a curve showing how the focal factor suppresses easy tokens.

### What to say (verbatim)

> *"The training recipe — focal loss times class weights. Two ingredients."*

> *"Inverse-frequency class weights rebalance ACROSS classes. Rare classes get a large weight, capped at ten to avoid gradient blow-up. A VICTIM token ends up about a hundred and thirty times more loss-impactful than an O token."*

> *"Focal loss, with gamma equal to two, rebalances ACROSS difficulty. The (one minus p) squared factor suppresses tokens the model already gets right, so the optimiser concentrates on the hard ones — which is where the rare entities live."*

> *"The key claim is complementarity: the two attack different parts of the imbalance problem, so the combination beats either alone."*

> *"If asked why cap at ten: without it, the rarest class weight hits about twenty-two and destabilises early training. The cap was empirical."*

### Why this slide is in the talk
The modelling contribution made visible. The "complementarity" claim is what justifies using both ingredients; the ablation on slide 18 is the evidence.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Focal loss** | Cross-entropy with a $(1-p_y)^\gamma$ focusing factor that suppresses easy tokens (see `formulas_explained.md` §4) |
| **γ (gamma) = 2** | The focal-loss focusing parameter |
| **Inverse-frequency class weights** | Per-class multipliers proportional to 1/frequency, capped at 10 |
| **Complementarity** | The claim that the two ingredients attack different aspects of imbalance, so the combination beats either alone |
| **130×** | VICTIM tokens contribute ~130× the loss-weight of O tokens under the production recipe |

### If a panellist asks...

- **"Why focal loss + class weights and not just one?"** → *"They attack different aspects of the imbalance. Class weights rebalance across classes — VICTIM tokens become 130× more impactful than O. Focal loss rebalances within a class — easy-correct tokens get suppressed. The §6.6 ablation shows the combination beats either alone."*
- **"Why γ = 2?"** → *"Literature default from Lin et al. 2017. We tested γ = 1 (smaller gains) and γ = 3 (training instability). γ = 2 is the empirically stable choice."*
- **"Why cap at 10?"** → *"Without it, VICTIM's weight comes out around 22, which destabilises early training. Finding the right cap was empirical — 10 keeps rare classes elevated without destabilising."*
- **"Did you try other losses (dice, label smoothing only)?"** → *"Label smoothing β = 0.1 is in the production loss but contributes a marginal effect. Dice loss is a fair future comparison but wasn't tested — focal loss has more direct prior work in token classification under imbalance."*

### Pivot to next slide

> *"On top of the trained model sits the KB layer."*

---

## Slide 13 — The curated knowledge base

**Duration target:** 75 seconds

### What's on the screen
KB composition (150 groups, 200 cities, 54 countries, 38 weapons) plus the two roles (validate, enrich) with operational metrics (2.4% flag, 64.3% enrichment).

### What to say (verbatim)

> *"The curated knowledge base."*

> *"About a hundred and fifty active armed groups with aliases, country, and group type. Two hundred conflict cities mapped to country and region. All fifty-four countries. Thirty-eight weapon categories. Loaded once in-memory at server startup, consulted on every inference."*

> *"Two roles from one curated resource. Validation flags geographically implausible actor-location pairs — Al-Shabaab in Goma — at a two-point-four percent rate. Enrichment canonicalises actor surface forms so analytics aggregate correctly — sixty-four-point-three percent of ACTOR mentions get enriched."*

> *"Defend the small size: a hundred and fifty covers the ACTIVE landscape, not historical exhaustiveness. Including inactive groups would produce false-positive enrichments. Mean alias count per group is four-point-two, which is what matters for canonicalisation."*

> *"Validation never blocks extraction; enrichment never invents data."*

### Why this slide is in the talk
The KB contribution made visible with operational numbers. The "150 covers active landscape" defence is essential for the inevitable "why so small?" question.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **150 armed groups** | Active African armed groups in the curated KB |
| **Aliases** | Surface variants of a canonical group name — "Al Shabaab", "al-shabaab", "Al-Shabaab militants" |
| **2.4% flag rate** | Fraction of extracted events where the KB flags a geographic implausibility |
| **64.3% enrichment rate** | Fraction of ACTOR mentions that successfully match a canonical KB entry |
| **4.2 aliases/group** | Mean number of surface variants per canonical entry |

### If a panellist asks...

- **"Why only 150?"** → *"ACLED's full actor list has thousands of entries, many inactive or splinter-faction instances. 150 covers the active landscape. The mean alias count is 4.2, which is what matters for canonicalisation. Recommendation 2 in §7.4 says a part-time domain expert keeps the KB current."*
- **"What happens to the 35.7% of actors not enriched?"** → *"They carry the raw surface form. No fabrication. The record is still persisted; only the canonical fields are empty. New armed groups not yet in the KB are exactly this case."*
- **"Why does validation not block extraction?"** → *"The flag is metadata, not a veto. The record is persisted with the flag visible in the UI, prompting analyst re-read. Blocking extraction on plausibility would lose records describing genuinely unusual events."*

### Pivot to next slide

> *"All of this is delivered through the platform."*

---

## Slide 14 — The platform

**Duration target:** 75 seconds

### What's on the screen
The four-layer architecture: React/TypeScript frontend, FastAPI service, in-process components (model + KB), PostgreSQL store. Docker Compose orchestration.

### What to say (verbatim)

> *"The platform — the delivery vehicle."*

> *"React and TypeScript front-end. FastAPI service layer. In-process component layer holding model and KB. PostgreSQL sixteen event store. Docker Compose orchestration — one command stands it up."*

> *"Four layers is the minimum for clean separation. A monolithic FastAPI worker is faster and simpler than microservices at thirty thousand articles a year."*

> *"Defend the stack as engineering, not research claims. React for ecosystem and TypeScript support. FastAPI for async plus native PyTorch integration plus auto OpenAPI docs. PostgreSQL for full-text plus JSONB indexing the analytics layer needs."*

> *"The research contribution is the INTEGRATION evaluated end-to-end. Swapping React for Vue would change implementation, not contribution."*

### Why this slide is in the talk
Defends the systems contribution. The "engineering not research" framing pre-empts the "isn't this just web development?" question — the research is in the integration, not the individual choices.

### Key terms and numbers on this slide

| Term | Means |
|:--|:--|
| **FastAPI** | Modern async Python web framework |
| **In-process** | Components share memory with the API server, not separate processes |
| **PostgreSQL JSONB** | Indexed JSON storage that supports queries on nested fields |
| **OpenAPI** | Automatic API documentation generated from FastAPI route definitions |
| **Docker Compose** | Multi-container orchestration — one command starts the whole stack |

### If a panellist asks...

- **"Isn't this just engineering, not research?"** → *"The integration is the contribution. No published academic work in this domain has integrated all four pieces (schema + model + KB + UI) and evaluated end-to-end with UAT. The empty cell on the related-work landscape (slide 6) shows that explicitly. Section 7.3 lists this as contribution #5."*
- **"Why monolith and not microservices?"** → *"At 30,000 articles/year a single FastAPI worker holding the model in memory is faster and simpler than a service mesh. Microservices would be appropriate at much higher load — not at this scale."*
- **"Why React?"** → *"Largest community and strongest TypeScript ecosystem in 2026. Lowest-risk for whoever inherits the system. The choice is engineering pragmatism, not a research claim."*

### Pivot to next slide

> *"Here's what happens end-to-end when an article goes through the system."*

---

## Slide 15 — The inference pipeline (worked example)

**Duration target:** 90 seconds

### What's on the screen
The 10-step inference pipeline with the canonical sentence worked example. Entity chips colour-coded by 5W1H slot.

### What to say (verbatim)

> *"The end-to-end inference pipeline, with the worked example."*

> *"Article in. Tokenise. BERT forward pass. BIO decode to spans. Confidence filter. 5W1H grouping. KB validate-and-enrich. Taxonomy classify. Persist. Render chips."*

> *"The forward pass is about seventy-five percent of the hundred and fifty milliseconds. KB lookup is fifteen percent. Everything else is ten percent, because the KB is in-memory."*

> *"Worked example. 'Al-Shabaab attacked a convoy near Mogadishu on Tuesday, killing twelve soldiers.' Becomes: perpetrator Al-Shabaab. Victim twelve soldiers. Action attacked. Date Tuesday — normalised to a calendar date relative to publication. Location Mogadishu — resolved to Somalia. Casualties twelve, with the 'at least' qualifier preserved."*

### Why this slide is in the talk
Makes the abstract pipeline concrete. The worked example is what the panel will remember — colour-coded entity chips make the 5W1H structure visible.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Tokenise (WordPiece)** | Split text into sub-word units for BERT |
| **BIO decode** | Collapse contiguous B/I sequences into entity spans |
| **Confidence filter** | Drop spans whose averaged sub-token probability is below threshold |
| **5W1H grouping** | Bucket spans into WHO/WHAT/WHEN/WHERE/HOW |
| **150 ms total** | End-to-end CPU latency |

### If a panellist asks...

- **"Why is BERT 75% of the latency?"** → *"BERT-base has 110M parameters. The forward pass involves matrix multiplications across all of them. The other steps — tokenisation, BIO decode, KB lookup — are comparatively trivial."*
- **"What happens if KB lookup fails?"** → *"The record is still persisted with the raw surface form. No fabrication. KB failure doesn't block extraction."*
- **"What does 'normalised' mean for the date?"** → *"Relative dates like 'Tuesday' or 'yesterday' get resolved to a calendar date using the article's publication date as the anchor. If the article was published on a Friday, 'Tuesday' becomes the previous Tuesday's date."*
- **"How is the casualty qualifier preserved?"** → *"The post-processor parses '12' as the count and 'at least' as the qualifier into a structured field. Downstream consumers see {killed: 12, qualifier: 'at least'}, not the bare number."*

### Pivot to next slide

> *"With the system explained, we move to the evidence."*

---

## Slide 16 — Headline results

**Duration target:** 75 seconds

### What's on the screen
Hero number — micro F1 0.909. Plus macro F1 0.887, token accuracy 96.7%, validation loss at epoch 2.

### What to say (verbatim)

> *"Headline results. All on a held-out ten-thousand-example validation set covering one hundred and ninety thousand gold spans."*

> *"Micro F1 zero-point-nine-zero-nine. Macro F1 zero-point-eight-eight-seven. Token accuracy ninety-six-point-seven percent. Best checkpoint at epoch two with validation loss zero-point-zero-zero-seven-four."*

> *"I lead with F1, not accuracy, because seventy-eight percent of tokens are O — a degenerate 'predict O everywhere' model already scores seventy-eight percent accuracy and learns nothing."*

> *"Micro exceeds macro by about two points because the high-support entities — DATE, CITY, ACTOR — also have the highest F1."*

> *"If asked is 0.909 good — CoNLL-2003 general-news NER is around 0.92 on four entities with mild imbalance. This is eight entities with severe imbalance — competitive on a harder distribution."*

> *"All numbers are strict span-level — exact boundaries and type — reported for honesty."*

### Why this slide is in the talk
The headline number planted in slide 1 is now contextualised. The "why F1 not accuracy" framing pre-empts the "isn't 96.7% accuracy enough?" question.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Held-out** | Data not seen during training; used only for evaluation |
| **190,075 gold spans** | Total entity spans across all 8 types in the validation set |
| **Micro F1 0.909** | F1 computed from pooled TP/FP/FN counts (weights by entity frequency) |
| **Macro F1 0.887** | Average of per-entity F1s (weights every entity equally) |
| **Strict span-level** | Exact-match: both type AND exact boundaries required for a TP |
| **CoNLL-2003** | The canonical English NER benchmark for comparison |

### If a panellist asks...

- **"Why is micro higher than macro?"** → *"Micro weights by support — the high-frequency entities (DATE, CITY, ACTOR) dominate. Macro averages equally. Since the high-frequency entities also have the highest F1, micro comes out higher."*
- **"Why not relaxed-match span scoring?"** → *"Relaxed-match would be 1.5-2 F1 points higher but operationally misleading — a partial-match span doesn't save analyst time, they still have to edit. Strict matches what the consumer actually experiences."*
- **"Is 0.909 strong?"** → *"Strong for this distribution. CoNLL-2003 sets the benchmark at ~0.92 on 4 entities with mild imbalance. VioNER does 0.91 on 8 entities with severe imbalance — competitive on a harder problem."*
- **"How can I trust these numbers aren't overfit?"** → *"Article-level split, hash-based deduplication before split, augmentation template pools partitioned between train and validation. Section 6.13 lists residual leakage risks honestly."*

### Pivot to next slide

> *"The per-entity breakdown is where the operational story lives."*

---

## Slide 17 — Per-entity F1

**Duration target:** 90 seconds

### What's on the screen
Bar chart or table of 8 entities ranked by F1: DATE 0.956 down to VICTIM 0.817. Macro avg = 0.887.

### What to say (verbatim)

> *"Per-entity F1 — the reliability map."*

> *"DATE strongest at zero-point-nine-five-six. Then CITY zero-point-nine-three-four. ACTOR zero-point-nine-two-three. REGION zero-point-eight-nine-one. CASUALTIES zero-point-eight-eight-five. ACTION zero-point-eight-six-six. DISTRICT zero-point-eight-two-six. VICTIM zero-point-eight-one-seven."*

> *"Read it operationally. Dates and locations are essentially solved — trust them. Actors are mostly solved — spot-check for new groups. Casualties are mostly solved — verify the qualifier. Actions need occasional addition for passive voice. Districts and victims need the most correction."*

> *"Precision exceeds recall on every row — standard NER. When uncertain the model defaults to O, trading a missed entity for fewer false alarms. That's the right trade for analyst review."*

> *"If asked why VICTIM is weakest — low support (five thousand four hundred and ninety-two spans vs forty-seven thousand for ACTOR), plus extreme phrasing variability."*

### Why this slide is in the talk
Translates F1 numbers into operational reliability for each field. The "read it operationally" framing gives the analyst a usability map: what to trust, what to verify, what to correct.

### Key terms and numbers on this slide

| Entity | F1 | Operational reading |
|:--|--:|:--|
| DATE | 0.956 | Trust |
| CITY | 0.934 | Trust |
| ACTOR | 0.923 | Spot-check new groups |
| REGION | 0.891 | Occasional correction |
| CASUALTIES | 0.885 | Verify qualifier |
| ACTION | 0.866 | Add passive-voice misses |
| DISTRICT | 0.826 | Often confused with CITY/REGION |
| VICTIM | 0.817 | Most-corrected entity |

### If a panellist asks...

- **"Why is VICTIM weakest?"** → *"Low support — 5,492 gold spans vs 47,612 for ACTOR — plus extreme phrasing variability. Anything from 'civilians' to 'Christian worshippers' to 'the bus driver's family' can be a victim. The ablation on slide 18 shows the focal-loss recipe lifted VICTIM by 11 F1 over plain CE; the remaining gap is structural noise."*
- **"Why is precision higher than recall everywhere?"** → *"Standard NER behaviour. When uncertain the model defaults to O — the safe choice. This trades fewer false positives for more missed entities, which is right for analyst review workflows."*
- **"Why is DISTRICT confused with CITY?"** → *"Many African districts share names with their main city or with their region. Goma is the canonical example — city, district capital, regional centre all simultaneously. The model defaults to CITY because that's more often right. The confusion matrix on slide 20 shows the pattern."*

### Pivot to next slide

> *"To prove the loss-function choice was the right one, here's the ablation."*

---

## Slide 18 — The ablation

**Duration target:** 90 seconds

### What's on the screen
Table 6.8 — four loss configurations on the rare entities. VICTIM and ACTION rows highlighted with +0.109 / +0.072 deltas.

### What to say (verbatim)

> *"The ablation — the single most important table in the thesis."*

> *"Four loss configurations. Identical conditions. Only the loss changes."*

> *"VICTIM. Plain cross-entropy zero-point-seven-zero-eight. Weighted CE zero-point-seven-seven-six. Focal alone zero-point-seven-nine-two. Focal-plus-weights zero-point-eight-one-seven. Plus ten-point-nine."*

> *"ACTION plus seven-point-two."*

> *"Two headline claims. One — complementarity. Each ingredient alone is insufficient; the combination beats both. Two — every entity is at least as good as baseline. No common-class regression."*

> *"On significance — three seeds, run-to-run variance about plus or minus zero-point-four F1, so the eleven-point gain exceeds variance by twenty-five times. Paired bootstrap at article level gives p below zero-point-zero-one."*

> *"This table is the empirical answer to the modelling research question. Without it, the loss choice would be assertion, not evidence."*

### Why this slide is in the talk
The single most quotable table in the thesis. Without it, the contribution claim about the loss function would be assertion rather than evidence. The "+11 F1 on VICTIM" is the most memorable number of the talk.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Identical conditions** | Same data, same scheduler, same random seed — only the loss differs |
| **Complementarity** | The combination beats either ingredient alone |
| **Run-to-run variance ±0.4** | Macro F1 variance across three random seeds |
| **Paired bootstrap** | Statistical test that estimates significance by resampling article-level errors |
| **p < 0.01** | The gain is significant at the 1% level |

### If a panellist asks...

- **"How do you know the ablation is fair?"** → *"Identical data, scheduler, random seeds, training epochs — only the loss function changes. Each of the four runs was retrained under the same protocol; no other factor varies."*
- **"Is +11 F1 statistically significant?"** → *"Yes — three seeds give run-to-run macro variance of ±0.4 F1. The +10.9 VICTIM gain exceeds that by 25×. Paired bootstrap at article level gives p < 0.01."*
- **"Why does focal loss + weights work better than either alone?"** → *"They attack different parts of the imbalance. Class weights rebalance across classes; focal loss rebalances within a class (easy vs hard tokens). The combination handles both axes; either alone handles only one."*

### Pivot to next slide

> *"Beyond model metrics, the KB has operational metrics, and the platform was tested by real users."*

---

## Slide 19 — KB operational impact and user testing

**Duration target:** 90 seconds

### What's on the screen
Left: KB metrics (64.3% enrichment, 2.4% flag rate). Right: UAT results (n=5, all 6 tasks completed, top Likert items at 4.6).

### What to say (verbatim)

> *"KB operational impact and user testing."*

> *"KB. Sixty-four-point-three percent of actor mentions get enriched with a canonical identifier. Two-point-four percent of events get a geo-implausibility flag — a small, targeted priority queue, not noise."*

> *"The unenriched thirty-six percent are new groups, generic phrasings like 'armed men', or below-threshold matches. The threshold is conservative — collapsing distinct groups under one canonical entry would be worse than leaving them unenriched."*

> *"Speed. About a hundred and fifty milliseconds versus fifteen to twenty-five minutes — a three to five times reduction once you add realistic review time."*

> *"UAT. Five participants. Two early-warning analysts, one academic, two NLP developers as a fairness check. All completed all six tasks. Every item cleared four-point-zero. The two highest at four-point-six were 5W1H clarity and KB enrichment — exactly the differentiating contributions."*

> *"On n equals five — qualitative, not inferential. Nielsen's rule is five users find about eighty-five percent of usability issues."*

### Why this slide is in the talk
Closes out contributions 4 and 5 (KB and platform) with operational evidence. The UAT result that the differentiating contributions (5W1H, KB) scored highest is internally coherent — what the thesis claims matters is what the participants found valuable.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **2.4% flag rate** | Fraction of events flagged by KB validation for analyst re-read |
| **64.3% enrichment rate** | Fraction of ACTOR mentions canonicalised via KB lookup |
| **3-5× speed reduction** | Per-article time including realistic review |
| **UAT** | User Acceptance Testing — pre-deployment validation by intended users |
| **n=5 (Nielsen's rule)** | Five users find ~85% of usability issues |
| **Likert 4.0+** | All items scored "agree to strongly agree" on average |

### If a panellist asks...

- **"Is 2.4% flag rate enough to be useful?"** → *"Yes — and small flag rates are operationally appropriate. The flag identifies the records most worth analyst re-read. 30% would be noise; 0.2% would miss systematic errors. 2.4% lands in the sweet spot."*
- **"Can you draw conclusions from n=5?"** → *"Qualitatively yes, inferentially no. Nielsen's rule supports n=5 for usability validation. Constructive feedback was internally consistent across participants — three of five asked for drag-and-drop file upload — which is a stronger signal than mean Likert scores at this sample size."*
- **"Why is the training-screen Likert lower (4.0) than the others?"** → *"Participants found it less intuitive than the inference screen. The constructive feedback — clearer hyperparameter explanations, dataset previews — fed directly into medium-priority future work."*
- **"What does 3-5× reduction actually translate to?"** → *"Conservative estimate based on comparable NLP-assisted coding workflows. Recommendation 1 in §7.4 is a controlled pilot study before production deployment to measure this directly."*

### Pivot to next slide

> *"Where does the model still fall short? Error analysis."*

---

## Slide 20 — Error analysis

**Duration target:** 60 seconds

### What's on the screen
Error breakdown — 5 categories with %: boundary mismatch 38%, location-type 24%, missed entities 19%, spurious entities 12%, confidence drops 7%. Confusion matrix snippet for location types.

### What to say (verbatim)

> *"Error analysis — structured diagnosis, not just 'it fails sometimes'."*

> *"From three hundred error-containing events. Boundary mismatch thirty-eight percent. Location-type confusion twenty-four percent. Missed entities nineteen percent. Spurious entities twelve percent. Confidence drops seven percent."*

> *"Boundary plus location together are sixty-two percent — both addressable by a span-level CRF on top of BERT, which is the high-priority future-work fix."*

> *"The location confusion is the Goma problem. When gold is DISTRICT, the model predicts CITY seven percent of the time and REGION nine percent. It defaults to CITY because it's more often right."*

> *"Frame each category by analyst cost. Boundary mismatch is least costly — right type, clipped span. Missed entities are most costly per error — add from scratch. Spurious entities are tunable via confidence thresholds."*

### Why this slide is in the talk
Honest engineering. The structured 5-category breakdown shows the failures aren't random — they're systematic and addressable. Each category points at a specific future-work fix.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **Boundary mismatch** | Right entity type, wrong span boundaries (e.g., "12 civilians" vs "at least 12 civilians") |
| **Location-type confusion** | DISTRICT predicted as CITY, or REGION predicted as DISTRICT, etc. |
| **CRF (Conditional Random Field)** | A sequence model that adds label-to-label transition constraints; the future-work fix for boundary errors |
| **Confidence drops** | Model predicted correctly but below the per-category threshold; filtered out |

### If a panellist asks...

- **"Why is boundary mismatch the biggest category?"** → *"Token-level NER doesn't have sequence-level boundary constraints. A span-level CRF or biaffine head on top of BERT would add those constraints — that's high-priority future work item 4."*
- **"Why is location confusion specifically the Goma problem?"** → *"Many African districts share names with their main city or region. Goma is city, district capital, and regional centre simultaneously. 'Fighting in Goma' doesn't disambiguate. The model defaults to CITY, which is more often right but produces consistent confusion."*
- **"Can you reduce spurious entities by tuning thresholds?"** → *"Yes — raising the WHEN threshold to 0.85 eliminates most 'this morning'-class errors at the cost of 1.2 F1 on legitimate DATE recall. That's a tunable operator choice, not a fixed system property."*

### Pivot to next slide

> *"With evidence covered, I want to own the limits honestly."*

---

## Slide 21 — Limitations

**Duration target:** 60 seconds

### What's on the screen
Four-row table of honest limitations: English-only, 30% synthetic, rule-based taxonomy, KB curation burden.

### What to say (verbatim)

> *"Limitations — I want to own them. Getting there first disarms the panel."*

> *"English-only. A large share of African reporting is in French, Arabic, Portuguese. Multilingual extension via XLM-RoBERTa or AfroLM is the highest-priority future work, and the methodology transfers directly."*

> *"About thirty percent of the corpus is template-augmented, so the metrics are in-distribution, not out-of-distribution. Real-news expansion is future work item three."*

> *"The taxonomy classifier is rule-based, not learned. A learned hierarchical classifier needs Level-3 labelled data that would be a thesis in itself."*

> *"The KB needs ongoing curation as groups rebrand. Recommendation is a part-time domain expert, about a day a week."*

> *"None of these undercut the in-scope contribution."*

### Why this slide is in the talk
Owning limitations explicitly disarms half of Q&A. Examiners cannot attack what you have already conceded. The closing line — "none of these undercut the in-scope contribution" — keeps the contribution claim intact while being honest about scope.

### Key terms and numbers on this slide

| Term | Means |
|:--|:--|
| **XLM-RoBERTa, AfroLM** | Multilingual transformer models suitable for the future multilingual extension |
| **In-distribution / Out-of-distribution** | Validation set drawn from the same combined corpus = in-distribution; truly new sources = out-of-distribution |
| **Rule-based taxonomy classifier** | Conditional rules from ACTION verb → taxonomy path; not learned from data |
| **KB curation** | The maintenance burden of keeping the knowledge base current as armed groups change |

### If a panellist asks...

- **"Which limitation worries you most?"** → *"English-only. A monolingual extractor leaves the French and Arabic signal on the floor, which is operationally significant. That's why multilingual extension is the highest-priority future-work item."*
- **"How much would 30% synthetic data move the numbers?"** → *"Conservative estimate: 2-4 F1 points downward on out-of-distribution news. I don't have exact numbers because I lack labelled out-of-distribution data — that's exactly what future-work item 3 (real-news expansion) is designed to measure."*
- **"Why didn't you build a learned taxonomy classifier?"** → *"Training one requires event-labelled data at Level 3 granularity, which ACLED's main schema doesn't provide. Constructing that labelled set would be a separate annotation-scale project. Rule-based ships now; learned is future-work item 2."*

### Pivot to next slide

> *"To close — the five contributions, restated."*

---

## Slide 22 — The five contributions (close)

**Duration target:** 75 seconds

### What's on the screen
Five-row contribution table summarising everything: schema (κ=0.78), taxonomy (African extensions), training recipe (+11 F1), KB (2.4%/64.3%), platform (UAT validated).

### What to say (verbatim)

> *"The five contributions, restated as the close."*

> *"One — the eight-entity grounding-validated schema. Kappa zero-point-seven-eight."*

> *"Two — the four-level taxonomy synthesising ACLED, UCDP, PMVE with African-specific extensions."*

> *"Three — the focal-loss-plus-class-weights recipe. Plus eleven F1 on VICTIM with no entity hurt."*

> *"Four — the curated KB doing validation and enrichment. Two-point-four percent flag and sixty-four-point-three percent enrichment."*

> *"Five — the deployable platform. UAT-validated with non-ML users completing all six tasks."*

> *"The thesis-level claim — the INTEGRATION of these five, schema plus model plus KB plus taxonomy plus platform, evaluated end-to-end — is the contribution. Because no single piece alone closes the operational loop."*

> *"Close with calm confidence. The work supports the claim. Thank you. Invite questions."*

### Why this slide is in the talk
The slide that gets quoted in the panel's decision. Each item is self-contained — the integration claim is the unifying argument. "Close with calm confidence" is a delivery cue, not a script line.

### Key terms and numbers on this slide

| Term / number | Means |
|:--|:--|
| **κ = 0.78** | Inter-annotator agreement on the grounded 8-entity schema |
| **+11 F1 on VICTIM** | The empirical lift from focal loss + class weights over plain CE |
| **2.4% / 64.3%** | KB flag rate and enrichment rate |
| **All 6 tasks completed** | UAT outcome for all 5 participants |
| **Integration** | The five-piece artefact, evaluated end-to-end, is the contribution |

### If a panellist asks...

- **"Which contribution is most novel?"** → *"The integration. In isolation, each piece has precedent. What's new is combining all five for African violent-event extraction and evaluating end-to-end with UAT."*
- **"What's the single biggest takeaway?"** → *"That grounding-based supervision, imbalance-aware training, curated KB validation, and a usable interface — combined and packaged — produce extracted records that analysts trust and that meaningfully reduce hand-coding cost."*
- **"If you only had one piece, which would you keep?"** → *"Contribution 3 — the focal-loss-plus-class-weights recipe. It has the cleanest reproducible empirical evidence, the most direct impact on operational utility (rare-entity recovery), and applies beyond African violent-event NER to any severe-imbalance token-classification task."*
- **"What advice would you give a student starting a similar project?"** → *"Three things. Run a grounding pilot before designing the schema. Build the KB and UI in parallel with the model, not after. Plan the limitations slide before the contributions slide."*

### Pivot to questions

After the close, **pause**. Make eye contact with each panel member. Wait for the first question. Don't rush to fill the silence.

When the first question lands:

1. Pause for one beat
2. If ambiguous, restate the question in your own words ("So you're asking whether...")
3. Answer with the bottom line first, then evidence
4. End by checking — "Does that answer the question, or would you like me to go deeper on one aspect?"

---

# Defense-day calibration

## Three reminders for the room

1. **The examiners chose your thesis to defend.** They have read it. They are not trying to catch you out — they are trying to assess whether you understand your own work.

2. **Speak with the calm authority of someone who built the thing.** The math is hard. You understood it well enough to ship a system that works. Trust that.

3. **When you don't know, say so.** A confident "I haven't tested that — the closest evidence I have is X" is worth more than a vague guess. Bluffing is the single most damaging behaviour in a defense.

## The pocket reference

If you only memorise three things from this guide, memorise these:

| What | Value | Where |
|:--|:--|:--|
| Headline F1 | **0.909 micro / 0.887 macro** | Slide 16 |
| The ablation result | **VICTIM +10.9 F1, ACTION +7.2 F1, no entity hurt** | Slide 18 |
| The contribution claim | **The integration of schema + model + KB + taxonomy + platform — evaluated end-to-end — is the contribution** | Slide 22 |

## The fallback line

If you blank on any answer:

> *"Let me come back to that — could you ask the next question and I'll return to this one?"*

This is completely acceptable. Examiners would rather you say this than watch you stumble. Your brain will usually reset on the next answer, and you can return to the first one with composure.

## One last thing

When the panel finishes and the chair invites your closing remarks, just thank them. No grand speech. The work has spoken. The data supports the claim. You've done the rest.

Good luck.
