# Replacement Text for Flagged Sections — Final.docx

How to use this file:

1. Each entry gives the **location**, the **first words of the flagged passage** (search for
   them in Word to find the spot), and the **replacement text**. Replace the whole flagged
   block with the replacement, nothing more.
2. Every number, threshold, citation marker, and cross-reference was checked against the
   thesis text — do not "fix" them while pasting.
3. Bucket A items (declaration sheet, dedication/acknowledgements, acronym expansions,
   Annex F questionnaire, Annex C table cells, the 6.9 demo inputs) are **not** in this
   file. Do not rewrite them; raise them with your advisor as detector false positives.
4. One numbering note: the 4.8 fix introduces a new table. Chapter 4 currently ends at
   Table 4.5, so the new one is **Table 4.6** — confirm nothing else claims that number
   after you insert it.
5. Unflagged paragraphs adjacent to these blocks are untouched on purpose. Leave them.

---

## Chapter 1

### 1a. Chapter 1 opener (p.1)

**Replace the paragraph beginning:** "The research problem addressed by this thesis sits at the intersection of three pressures…"

**With:**

> More news about violent events in Africa is published every day than the analysts responsible for tracking it can read. Early-warning work depends on converting that reporting into structured records quickly, and the people doing the converting are the bottleneck. That tension is the research problem of this thesis. This chapter traces where the problem comes from and why it matters, states it formally, derives objectives and methods from it, and ends with a map of the remaining chapters.

### 1b. Section 1.1, first paragraph (p.1)

**Replace the paragraph beginning:** "The volume of digital news content describing violent events on the African continent has grown faster…"

**With:**

> Reporting on African violent events keeps growing, and human capacity to read and code it has not kept pace. Attacks, clashes, raids, bombings, displacement — accounts of all of these arrive daily from wire services, mainstream outlets, regional newspapers, and a widening set of online sources [1]. Almost everything in that stream is prose written for a human reader. A monitoring operation, though, needs records it can query, count, and compare over time, which means somebody — or something — has to convert each narrative into structured form before any systematic analysis can begin.

### 1c. Section 1.1, "While these initiatives…" (p.2)

**Replace the sentence:** "While these initiatives have demonstrated the value of structured event data, the underlying collection processes remain heavily manual or rely on coarse-grained automation that may miss nuance or African-specific patterns."

**With:**

> These projects prove how valuable structured event data is. What they have not solved is collection: the records are still produced largely by hand, or by coarse automation that tends to miss nuance and the patterns specific to African conflict.

### 1d. Section 1.1, AU-CEWS paragraph (p.2)

**Replace the paragraph beginning:** "The African Union Continental Early Warning System (AU-CEWS) operates within this landscape…"

**With:**

> Within this landscape sits the African Union Continental Early Warning System (AU-CEWS), the continental mechanism for monitoring conflict and crisis dynamics across AU member states. Its Africa Media Monitor tool aggregates the news; situation analyses, briefings, and early-warning products are written from what it collects. The bottleneck is in between. Monitored content still has to be transformed into structured, analysable form, and that step caps the throughput of everything downstream.

### 1e. Section 1.2, "Individually these are small judgements…" (p.2–3)

**Replace the two sentences:** "Individually these are small judgements. Aggregated across hundreds of records a week, they make trend analysis unreliable — was the spike real, or did the new shift simply code things differently?"

**With:**

> Each of these calls is small on its own. Stack them up across a few hundred records a week and trend analysis starts to wobble: when the numbers spike, nobody can say with confidence whether violence actually rose or whether a new shift simply coded things differently.

### 1f. Section 1.2, "The two gaps interact" paragraph (p.3)

**Replace the paragraph beginning:** "The two gaps interact. Closing the throughput gap by hiring more analysts…"

**With:**

> Worse, the two gaps feed each other. Hire more analysts to clear the backlog and you add more pairs of hands making slightly different judgements, so consistency suffers. Tighten the coding manual to fix consistency and every record takes longer, so the backlog grows back. This is what makes a machine-learning approach attractive here: a model applies the same judgement to every article it reads, and it can read far more of the inflow than any roster of humans, so it presses on both gaps at once.

### 1g. Section 1.2, "A vanilla cross-entropy…" (p.3)

**Replace the two sentences:** "A vanilla cross-entropy fine-tune on this distribution will quietly under-recover the rare classes… lifts VICTIM by eleven F1 points over plain cross entropy in this setting."

**With:**

> Fine-tune on that distribution with ordinary cross entropy and the failure is quiet: overall accuracy looks excellent while the rare classes go under-recovered, because the loss is dominated by tokens the model already gets right. The standard counter is focal loss [12] paired with inverse-frequency class weighting. It works here — Section 6.6 shows the combination lifting VICTIM by eleven F1 points over plain cross entropy.

### 1h. Section 1.2, "The third is more architectural" paragraph (p.3)

**Replace the paragraph beginning:** "The third is more architectural. An extraction system that produces records analysts cannot trust…"

**With:**

> The last observation is about architecture rather than modelling. If analysts cannot trust the records a system produces, the system has added work, not removed it — every extraction becomes one more thing to verify from scratch. Auditability is therefore the minimum bar. An analyst who opens an extracted record needs three things visible: the text each entity came from, the model's confidence in it, and whether the actor or location matches a known real-world referent. A curated knowledge base of African armed groups, conflict-affected cities, and weapon categories, running alongside the model, supplies exactly that audit trail. It has a useful side effect too: plausible-sounding nonsense — M23 attacking Maiduguri, the RSF operating in Mozambique — gets caught before a human reviewer ever sees it.

### 1i. Section 1.2, "The shape of the thesis…" paragraph (p.3)

**Replace the paragraph beginning:** "The shape of the thesis follows from all this…"

**With:**

> Taken together, these observations dictate what the thesis had to become. On the academic side it contributes a fine-tuned BERT model, an annotated dataset for African violent-event NER, and a four-level taxonomy built for the African context. On the practical side it delivers a working web application — training, inference, event management, and analytics behind one interface — usable by an analyst who has never run a Python script.

### 1j. Section 1.3, operational-packaging sentences (p.4)

**Replace the sentences beginning:** "The third is operational packaging. A trained model on its own is not an operational capability. To be useful, the model must be exposed…" (stop before "Most prior academic work…")

**With:**

> The third sub-problem is operational packaging. A model checkpoint by itself does nothing for an analyst. Making it useful means a documented API in front of it, a curated knowledge base beside it, a workflow around it covering article ingestion, event storage, and analytics, and an interface that someone without machine-learning training can operate.

### 1k. Section 1.5, "The work begins with the annotation schema…" paragraph (p.6)

**Replace the paragraph beginning:** "The work begins with the annotation schema. The starting point is the twenty-six-type schema in the proposal…"

**With:**

> Everything starts from the annotation schema. The proposal's twenty-six-type schema is the input; a pilot study is the filter. A sample of articles is annotated by hand to measure, per entity type, how often the value can be located verbatim in the source text. Types whose grounding rate falls below an acceptable threshold leave the NER schema and are recovered downstream instead — EVENT_TYPE rebuilt by the taxonomy classifier from the action verb plus context, COUNTRY by a knowledge-base look-up from the most specific WHERE entity. What remains is a narrower schema in which every type can be reliably supervised.

### 1l. Section 1.4.2 Specific Objectives (p.5–6) — *structural fix: bullets → grouped prose*

**Replace the intro line and all ten bullets** ("Translating the general objective into concrete deliverables, the work breaks down as follows." plus the list)

**With:**

> Translating the general objective into deliverables produces ten concrete items of work, grouped here by theme.
>
> Two objectives concern positioning and foundations. The literature on information extraction, event extraction, named entity recognition, and transformer language models — together with the conflict-event-coding tradition — is surveyed, and the present work is located against both bodies of work. From there the annotation schema is settled: eight entities (ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES) in BIO format, each chosen for how reliably it can be grounded in source text rather than for theoretical neatness, and each carrying explicit inclusion and exclusion rules.
>
> Two more concern the knowledge artefacts. A four-level taxonomy of violent events is built to fit African conflict patterns, with roughly ninety-five terminal categories and an explicit decision rule wherever two categories overlap, so the choice never falls back on annotator intuition. Beside it, a knowledge base — African armed groups, conflict cities and regions, weapon types, and the taxonomy itself — is curated and wired into the pipeline as a validation layer that sits on top of the raw NER output rather than inside the model.
>
> Data and training form the third group. The corpus objective: around fifty thousand examples drawn from ACLED event descriptions, assembled in two stages — stratified diversity sampling first, then template-based augmentation to plug vocabulary gaps and lift the rare classes off the floor. The training objective: a bert-base-cased fine-tune driven by focal loss with inverse-frequency class weighting, gradient clipping, a warmup-plus-plateau learning-rate schedule, and early stopping on validation loss.
>
> The platform accounts for two further objectives. A FastAPI back-end exposes the trained model and the KB through routes covering training management, inference, event storage, analytics, and KB administration; a React front-end lets a non-expert fine-tune models, run inference on documents, browse stored events, and read the analytics views without needing to know what a checkpoint is.
>
> The final pair closes the loop. Evaluation runs end to end — the held-out validation split gives the headline metrics, a handful of real-world articles gives the qualitative check, and the user-acceptance test gives the third perspective, with all three reported. And the limits of the current implementation are acknowledged explicitly, with a concrete future-work programme that includes learned hierarchical classification at inference time and natural-language question answering against the event store.

### 1m. Section 1.6.2 Out of Scope (p.8) — *structural fix: bullets → prose*

**Replace the intro line and all seven bullets** ("The following are explicitly outside the scope of this thesis…" plus the list)

**With:**

> Several capabilities are deliberately excluded, each named here with its reason; all are identified as priority future work in Chapter 7. The model and pipeline handle English text only — Arabic, French, Portuguese, Amharic, Swahili, and other African languages would require multilingual training data the project did not have. Articles are processed on demand or in batch, not as a real-time stream, because sub-second pipeline latency at scale is an engineering programme of its own. No predictive forecasting of future violence is attempted; the system describes what was reported, not what comes next. Ingestion is manual, with articles uploaded or submitted for inference rather than pulled automatically from third-party feeds. Queries against the event store go through structured filters in the analytics interface — free-text natural-language question answering is not supported. The taxonomy is applied through deterministic post-NER rules informed by knowledge-base look-ups, since a supervised hierarchical classifier needs labelled data at a scale future work must first assemble. Finally, production-grade hardening (high availability, multi-region replication, advanced authentication, audit logging) stays outside what a research prototype needs to demonstrate.

### 1n. Section 1.8, second and third paragraphs (p.10)

**Replace the paragraph beginning:** "After that, two chapters cover the system itself…"

**With:**

> The system itself occupies the next two chapters. Design lives in Chapter 4: architecture, entity schema, hierarchical taxonomy, knowledge base, training pipeline, inference pipeline, and the web application binding them together. Chapter 5 then documents construction — technology stack, data preparation, training implementation, the focal-loss code, back-end services, front-end, containerised deployment. Splitting the what-and-why from the how was a deliberate editorial decision; a reader who wants the design without the implementation can stop at the end of Chapter 4.

**Replace the paragraph beginning:** "Evaluation comes next. Chapter 6 reports dataset statistics…"

**With:**

> Chapter 6 evaluates. It reports dataset statistics, training dynamics, overall and per-entity performance, the focal-loss ablation, the knowledge-base layer's impact, latency measurements, an end-to-end demonstration on real articles, user-acceptance feedback, and an error analysis, closing with discussion, threats to validity, and a short account of experiments tried first and abandoned.

---

## Chapter 2

### 2a. Section 2.1, first three paragraphs (p.11)

**Replace the paragraph beginning:** "Information Extraction (IE) [4] is a broad field…"

**With:**

> Information Extraction (IE) [4] names a family of techniques rather than a single one: named entity recognition, relation extraction, coreference resolution, and event extraction all live under the umbrella, each pulling a different kind of structure out of unstructured text. Textbooks draw them as stages in a pipeline. Current research increasingly blurs those stages, training joint or end-to-end models that solve two or more sub-tasks inside one network. This thesis stays on the pipeline side of that divide; at the scale this work operates at, being able to inspect and debug each stage is worth more than whatever marginal accuracy a joint model might add. Section 4.2 turns that preference into a concrete architecture.

**Replace the paragraph beginning:** "Event extraction is the sub-task of central concern. Ahn's definition [3]…"

**With:**

> The sub-task that matters most here is event extraction. The working definition is Ahn's [3]: an event is a verb or nominal predicate plus the participants, location, and time it involves. The Automatic Content Extraction program [14] gave that view its first formal treatment in the early 2000s, publishing a typology of event types with their arguments, and two decades of supervised event-extraction research descend from that typology. The Text Analysis Conference Knowledge Base Population track carried the line forward on larger, more diverse benchmarks.

**Replace the paragraph beginning:** "The journalistic 5W1H frame [15] is a less rigid alternative…"

**With:**

> There is a looser alternative to enumerated event types: the journalist's 5W1H frame [15]. Rather than deciding in advance which event types exist, it asks the same six questions of every reported event — who, what, whom, where, when, how. News text suits this unusually well, since journalists are trained to answer those questions within the opening paragraph and analysts read for precisely those slots. That is the frame this thesis adopts. Event-type classification still happens, but as a post-NER step against the taxonomy of Section 4.4, which keeps any fixed inventory of event types out of the supervised learning problem altogether.

### 2b. Section 2.3, BERT-variant sentences (p.14)

**Replace the sentences:** "Several BERT variants and successors have been proposed. RoBERTa [21] improves on BERT… XLM-RoBERTa [23] extends the multilingual setting with strong performance on non-English text." (keep the final sentence about bert-base-cased as is)

**With:**

> BERT has spawned a family of successors. RoBERTa [21] keeps the architecture but trains harder — no next-sentence prediction, longer schedules, larger batches, dynamic masking. DistilBERT [22] goes the other way, distilling the model into something smaller and faster at a modest cost in accuracy. For multilingual work, XLM-RoBERTa [23] is the strong option on non-English text.

### 2c. Section 2.4 opener (p.14)

**Replace the paragraph beginning:** "NER under BIO is, almost by construction, a deeply imbalanced classification problem…"

**With:**

> Imbalance is not an accident of this dataset; BIO-encoded NER produces it by construction. In any ordinary sentence most tokens belong to no entity at all, so O dominates — roughly seventy-eight percent of all tokens in the corpus of Chapter 5. The entity tokens that remain are uneven among themselves. ACTOR, CITY, DATE, REGION, and DISTRICT occur often enough to learn well; VICTIM, ACTION, and CASUALTIES are at once the entities most in need of recovery and the ones a naive learner serves worst.

---

## Chapter 3

### 3a. Section 3.4, "The extra depth costs…" sentence (p.20)

**Replace the sentence beginning:** "The extra depth costs some classification accuracy at the deepest level…"

**With:**

> Depth has a price: telling a Level 4 "Roadside Ambush" from a "Complex Ambush" is far harder than picking a Level 1 category, so accuracy at the deepest level suffers. For an operational tool the trade is still worth making, because the analyst can simply stop descending at whatever level of granularity they trust.

### 3b. Section 3.4, "A learned hierarchical classifier could in principle…" paragraph (p.20)

**Replace the paragraph beginning:** "A learned hierarchical classifier could in principle replace the rule-based taxonomy assignment…"

**With:**

> In principle, the rule-based taxonomy assignment used today could give way to a learned hierarchical classifier. Classical approaches [37] divide into top-down cascades — one classifier per level, conditioned on the parent label — and global models that predict the entire path at once. Cascades are easier to debug and to train incrementally; a global model can recover from a wrong upper-level call. Either would improve on the rule-based fallback, and Section 7.5 puts the cascade variant first.

---

## Chapter 4

### 4a. Section 4.1 intro (p.23)

**Replace the paragraph beginning:** "Six principles shaped the design. Some were committed to at the start…"

**With:**

> Six principles shaped the design of VioNER. A couple were commitments made before any code existed; the rest earned their place during development, usually after something went wrong. No priority order is implied in what follows — in practice these operated as habits, applied whenever a design question came up.

### 4b. Section 4.1, grounded supervision (p.23)

**Replace the paragraph beginning:** "The first is grounded supervision. Every entity type in the schema must be something a human annotator can find verbatim…"

**With:**

> Grounded supervision came first, and it was learned the hard way. The rule: no entity type enters the schema unless a human annotator can find it verbatim in the source text on a reliable majority of occurrences. The proposal's original twenty-six-type schema looked clean on paper. Then came the November pilot. Hand-annotating a sample, the immediate casualty was EVENT_TYPE — was a given incident an "ambush" or a "raid"? Often both. Often neither, because the article never used either word; the annotator was inferring a label the text did not contain. COUNTRY failed for a different reason: writers rarely state the country when a city or region name already implies it. Grounding rates for both came in under 60 percent, and a model trained on labels that cannot consistently be located in the text is being trained on noise. Both types were removed from the NER schema and reassigned to the post-NER taxonomy step.

*(Leave the "The second is modular pipeline" paragraph untouched — it is not flagged, and it still reads correctly after this change.)*

### 4c. Section 4.1, hybrid statistics and knowledge (p.24)

**Replace the paragraph beginning:** "The third is hybrid statistics and knowledge. The learned model generalises over surface forms…"

**With:**

> Statistics and knowledge each get the jobs they are good at. The learned model handles generalisation over surface forms — recognising that "ENDF", "Ethiopian National Defense Force", and "Ethiopian troops" all name the same kind of actor is exactly what a fine-tuned encoder does well. Lookups are a different matter. Which country is "Beledweyne" in? What is the canonical name behind "JNIM"? Could this actor plausibly be operating in that location? Those are questions a deterministic knowledge base answers more reliably than any classifier, so it answers them.

### 4d. Section 4.1, confidence first-class (p.24)

**Replace the paragraph beginning:** "The fourth, which emerged during user-acceptance testing, is that confidence has to be first-class…"

**With:**

> Confidence became a first-class output only after watching real users. User-acceptance testing made it clear that a bare extraction invites misplaced trust, so every span the NER component emits now carries a confidence score, computed by averaging its sub-token softmax probabilities, and downstream code filters by category-specific thresholds — 0.80 for DATE, 0.60 for WHAT. The UI shows the number on hover. The reasoning is blunt: an analyst told the model was unsure about a casualty figure will check it; an analyst shown that figure as if it were ground truth probably will not.

### 4e. Section 4.1, operational packaging (p.24)

**Replace the paragraph beginning:** "The fifth is operational packaging. The deliverable is not a notebook…"

**With:**

> The deliverable was never going to be a notebook. From early on the target was a documented HTTP API with the analyst-facing UI on top, the whole stack starting from a single Docker Compose command, so that someone who has never run a Python script can still drive it.

### 4f. Section 4.1, reproducibility (p.24)

**Replace the paragraph beginning:** "The sixth is reproducibility, which is a working discipline rather than a checkbox…"

**With:**

> Reproducibility was treated as a working discipline rather than a box ticked at submission time. Every dataset, training run, and the deployment itself rebuilds from documented scripts and configuration. Seeds are fixed wherever the code allows. Where they cannot be — the diversity sampler uses the default random generator — the random state is logged instead, so the same subset can be reconstructed later.

### 4g. Section 4.2 closing sentence (p.25)

**Replace the sentence beginning:** "The boundary between extraction (NER) and post-processing is deliberate…"

**With:**

> Drawing a hard line between extraction (NER) and post-processing is deliberate. It lets the supervised learning problem stay narrow — just the schema of Section 4.3 — while the final output stays rich, because deterministic knowledge is layered onto the NER result afterwards.

### 4h. Section 4.3 opener (p.25–26)

**Replace the paragraph beginning:** "The schema is the single most consequential design choice in the thesis…"

**With:**

> No design choice in this thesis matters more than the schema. Get it wrong and the supervised learning problem fights the model the whole way; get it right and the model has a fair chance. Most of the work is done by the grounding rule of Section 4.1 — an entity type belongs in the schema if and only if a human annotator can find it verbatim in the source text on a reliable majority of occurrences, and whatever fails that test moves downstream into post-processing. The pilot left eight survivors, organised under the 5W1H categories in Table 4.1.

### 4i. Section 4.4 closing sentence (p.29)

**Replace the sentence:** "A learned hierarchical classifier could replace this rule-based step in future work."

**With:**

> Future work could swap a learned hierarchical classifier into the place this rule-based step currently occupies.

### 4j. Section 4.5, first three paragraphs (p.30)

**Replace the paragraph beginning:** "The knowledge base lives in memory next to the model and is built from three dictionaries…"

**With:**

> Three dictionaries make up the knowledge base — armed groups, locations, and weapons — and the whole structure lives in memory beside the model. A PostgreSQL-backed design loaded at startup was considered for a while. It lost on latency: inference hits the KB hard, and a dictionary lookup in process memory beats a database round trip every time. The price is that edits to the KB only take effect after a service restart, a wrinkle the analyst-facing flows in Section 5.6 are built to absorb.

**Replace the paragraph beginning:** "The armed-groups dictionary has roughly 150 entries…"

**With:**

> Roughly 150 armed groups are catalogued. An entry records the canonical name, the aliases under which news outlets report the group, the country of operation, the broader region (East, West, North, Southern, or Central Africa), and a type drawn from {militia, terrorist, rebel, government}. Currently and recently active groups were deliberately favoured over historical ones — Al-Shabaab, Boko Haram, M23, RSF, JNIM, ISGS, the Wagner Group, ENDF, TPLF — and the structure keeps adding a newly emerged actor cheap. Annex C reproduces the full inventory.

**Replace the paragraph beginning:** "The locations dictionary records about 200 conflict-affected cities…"

**With:**

> The locations dictionary holds about 200 conflict-affected cities plus all 54 African countries with their primary regions. Every city maps upward to a country and a parent administrative unit: "Maiduguri" resolves to Nigeria / Borno, "Goma" to DRC / North Kivu, "Mogadishu" to Somalia / Banaadir. That mapping does two jobs at inference time. An extracted CITY automatically picks up its country and region. And when an ACTOR's known country of operation disagrees with the country derived from the location in the same sentence — "M23 attacking Maiduguri" being the canonical example — the event gets flagged for analyst review.

### 4k. Section 4.6 intro (p.31)

**Replace the paragraph beginning:** "The pipeline takes raw ACLED event records on one end…"

**With:**

> Raw ACLED event records go in one end of the pipeline; a fine-tuned BERT model comes out the other. Five stages sit between: preprocessing the records into tokenised examples, sampling and augmenting the corpus, aligning word-level labels onto BERT's sub-word tokens, configuring the loss, and running checkpointed training with early stopping. The subsections below take them in order.

### 4l. Section 4.6.1 Preprocessing (p.31)

**Replace the paragraph beginning:** "The raw input arrives as a JSONL file of ACLED records…"

**With:**

> Input arrives as a JSONL file of ACLED records. Only some fields matter — event_id, event_date, the free-text notes description, fatalities, actor1, location, and admin1; the rest of what ACLED carries goes unused. Two passes follow. The notes field is tokenised on whitespace and punctuation first. Then each structured column is projected onto BIO labels: the column's value is located inside the tokenised notes and the matching positions are tagged with that column's entity type, while every unmatched token stays O. Out comes another JSONL file in which each record carries four parallel fields: tokens, labels, text, and entities.

### 4m. Section 4.6.5 Training Hyperparameters (p.32)

**Replace the paragraph beginning:** "The principal hyperparameters are listed in Table 4.5. Values were set by a combination…"

**With:**

> Table 4.5 lists the principal hyperparameters. Most were never candidates for tuning. The learning rate (2 × 10⁻⁵), AdamW, weight decay of 0.01, and 500 warmup steps are the standard BERT fine-tuning recipe; γ = 2.0 is the value the original focal-loss work recommends [12]; label smoothing of 0.1 and gradient clipping at 1.0 are conventional regularisation defaults. The batch size of 16 with gradient accumulation of 2 — an effective batch of 32 — was simply the largest configuration that fit in the training workstation's unified memory. Ten epochs is a ceiling, not a plan: early stopping on validation loss (patience 5) ends every practical run well before it.

### 4n. Section 4.6.6, first two sentences (p.33)

**Replace:** "The custom loss combines focal loss with inverse-frequency class weighting and optional label smoothing. Algorithm 4.4 summarises its behaviour."

**With:**

> Focal loss, inverse-frequency class weighting, and optional label smoothing combine into a single custom loss, summarised as Algorithm 4.4.

### 4o. Section 4.7, confidence-thresholds paragraph (p.35)

**Replace the paragraph beginning:** "Confidence thresholds are calibrated per category: WHO and WHOM at 0.70…"

**With:**

> Each category carries its own confidence threshold — 0.70 for WHO, WHOM, and WHERE, 0.75 for HOW, 0.80 for WHEN, and 0.60 for WHAT — set by inspecting validation-set errors rather than by formula. WHEN sits highest for a practical reason: a wrong date is glaring, since the analyst can check it against the article timestamp in seconds, so aggressive filtering there is cheap. WHAT sits lowest because context props it up — even a low-confidence "attacked" is worth keeping when the surrounding sentence leaves no doubt that violence occurred.

### 4p. Section 4.8 API routes (p.36) — *structural fix: bullets → table*

**Replace the line** "The back-end exposes the following route groups, all under /api:" **and the nine bullets**

**With:**

> Table 4.6 summarises the route groups the back-end exposes, all under /api.
>
> Table 4.6: Back-end API route groups
>
> | Route group | Purpose |
> |---|---|
> | /auth/* | Authentication and demo-user provisioning |
> | /training/* | Start, monitor, list, and manage training runs; sub-routes for checkpoint management, training-data inspection, and post-training evaluation |
> | /inference/* | Synchronous inference on a single text or document |
> | /events/* | Store, query, and update extracted events |
> | /analytics/* | Aggregated views: events per region, per actor, per time period |
> | /kb/actors, /kb/locations, /kb/taxonomies | Knowledge-base resource management |
> | /system/* | Service health, version information, configuration introspection |
> | /history/* | Per-user activity: recent inferences, saved queries |
> | /ws/training/{session_id} | WebSocket channel for live training progress |

**Replace the closing line:** "The front-end mirrors these routes with a screen for each…"

**With:**

> Each route group has a corresponding screen in the front-end. Section 5.7 covers the implementation; Annex D carries the screenshots.

---

## Chapter 5

### 5a. Chapter 5 opener (p.37)

**Replace the paragraph beginning:** "Where Chapter 4 described what VioNER does and why, this chapter documents how it actually does it…"

**With:**

> Everything in this chapter answers some version of one question: how, concretely, was the design of Chapter 4 built? The answer runs through the technology stack, data preparation, the training procedure, the focal-loss implementation, the back-end services and their API surface, the front-end, and the containerised deployment. Listings are deliberately brief — the full source lives in the accompanying repository.

### 5b. Section 5.1, front-end sentences (p.38)

**Replace the sentences:** "On the front end, React 19 with React Router 7 offered file-based routing… Vite replaced Create React App because the latter is effectively unmaintained and Vite's iteration loop is faster."

**With:**

> For the front end, React 19 and React Router 7 brought file-based routing that mapped naturally onto the intended screen layout, and TailwindCSS with shadcn/ui covered components without dragging in a heavyweight design system. Create React App was abandoned in favour of Vite — CRA is effectively unmaintained at this point, and Vite iterates noticeably faster.

### 5c. Section 5.2 opener (p.38)

**Replace the text beginning:** "ACLED publishes its data through an open API. The full African extract…" (up to and including "…into BIO-tagged training data in four steps:")

**With:**

> The raw material comes from ACLED's open API. Pulling every event coded for the 54 African countries since coverage began yields 212,590 records — anything outside Africa is dropped at ingest — stored on disk as JSONL in the same shape ACLED's own export tooling emits. Four steps turn that extract into BIO-tagged training data:

### 5d. Section 5.4, second paragraph (p.40)

**Replace the paragraph beginning:** "Data flows through a dataset class whose item accessor runs the tokenizer…"

**With:**

> Data reaches the model through a dataset class. Its item accessor calls the tokenizer with is_split_into_words enabled, pulls out the word indices, and applies the sub-word alignment of Algorithm 4.1; special tokens get label -100, which the default cross entropy and the custom focal loss both skip. The loop itself holds no surprises. Each epoch runs forward-backward over the training set and a no-grad pass over validation, gradients are clipped at L2 norm 1.0, and the learning rate warms up linearly for the first warmup_steps optimisation steps before handing over to ReduceLROnPlateau (factor 0.5, patience 2 epochs). Early stopping is a counter of epochs since validation loss last improved; when it reaches the patience threshold the loop exits and the best checkpoint is restored. Interruptions are not a catastrophe — a resume path re-enters the loop at the right epoch from the prior run's configuration file, and an extend-epochs flag lets a finished run keep going, so training never restarts from zero.

### 5e. Section 5.5, first paragraph (p.40–41)

**Replace the paragraph beginning:** "The custom loss code defines two classes: a FocalLoss module implementing Algorithm 4.4…"

**With:**

> Two loss classes live in the custom loss module: FocalLoss, implementing Algorithm 4.4, and the class-weighted cross entropy that serves as the ablation baseline in Section 6.6. A few implementation decisions deserve a note because each was hit in practice. Logits come in shaped [N, C] and targets shaped [N], and both are flattened before any softmax — log-softmax runs faster on a contiguous 2D tensor, and token classification never needs more than per-token granularity anyway. Ignored positions (target = -100) are masked out before the softmax computation, not after; mask late and heavily padded batches let padding tokens leak into the normalisation, which destabilises the loss numerically. When label smoothing is enabled it is applied to the target distribution, and the focal modulating factor is computed against the smoothed label rather than the original one-hot. Per-class weights arrive as a 1D tensor already on the logits' device and are indexed directly.

### 5f. Section 5.5, second paragraph (p.41)

**Replace the paragraph beginning:** "Class weights are computed once at the start of training as w_c = T / (C · max(f_c, 1))…"

**With:**

> Weights are computed exactly once, before the first batch: w_c = T / (C · max(f_c, 1)), with T the total token count over the training set, C the number of classes, and f_c the count of class c, clipped to a minimum of one so the division can never blow up. The training script logs the resulting O-class weight together with the minimum and maximum, which makes the weighting auditable from the run log alone; Annex E reproduces the full distribution and the derived weights for the production run.

### 5g. Section 5.6 opener (p.41)

**Replace the paragraph beginning:** "The back-end is implemented as a FastAPI application with route handlers organised by feature. Figure 5.1 sketches…"

**With:**

> The back-end is a FastAPI application whose route handlers are organised by feature. How the modules hang together — entry point, then the API routers, then the service layer, then the training pipeline and database access underneath — is sketched in Figure 5.1.

### 5h. Section 5.7, screens paragraph (p.42)

**Replace the text from** "The Training screen lists historical runs and exposes a control panel…" **through** "…Screenshots are reproduced in Annex D." (leave the preceding Inference-screen sentence as is)

**With:**

> Training gets two views. The list shows historical runs alongside a control panel for launching a new one; the detail view subscribes to the training WebSocket and turns the stream into a live progress bar, the current epoch, the latest losses, and a scrolling log. The Events screen is a paginated browser over everything in the store, with full-text search, structured filters on date range, country, region, and taxonomy level, and CSV export for whatever the filters return. Analytics aggregates: events per region, top actors, top locations, incident counts over time, and casualty totals for a chosen period. The KB screens give appropriately-roled users create, update, and deactivate operations over armed groups, locations, and taxonomy categories; every mutation goes through the back-end and lands in the audit table. Annex D reproduces screenshots of each screen.

### 5i. Section 5.8, first paragraph (p.43)

**Replace the paragraph beginning:** "The whole system runs from a single Docker Compose file at the repository root…"

**With:**

> One Docker Compose file at the repository root brings up the entire system. It defines three services. PostgreSQL 16 runs with a persistent volume; the Python back-end image carries the source with the model checkpoint mounted alongside it; a Node image builds the Vite front-end and serves it. Health checks enforce startup order, so the back-end waits until the database actually accepts connections rather than racing it.

### 5j. Section 5.8, environment-variable sentences (p.43)

**Replace the sentences:** "Configuration is environment-variable-driven. The variables that matter day to day are the database URL… An example environment file in the repository documents the complete set." (keep the rest of the paragraph)

**With:**

> Everything configurable is configured through environment variables. Four of them matter day to day — the database URL, the model path, the allowed CORS origins, and the JWT secret — plus a handful of feature flags, one of which toggles database storage. The repository carries an example environment file documenting the complete set.

---

## Chapter 6

### 6a. Section 6.2, opening caption sentence (p.44)

**Replace:** "The pre-processed dataset, before any sampling decisions, is shown in Table 6.2."

**With:**

> Table 6.2 describes the pre-processed dataset as it stands before any sampling decisions are taken.

### 6b. Section 6.2, "The substantive story…" sentence (p.44)

**Replace:** "The substantive story is in the entity-level distribution rather than the headline counts. Table 6.3 shows each entity type as a share of the entity-token total — precisely the imbalance Section 2.4 anticipated."

**With:**

> Headline counts say little here; what matters is how the entity tokens are distributed. Table 6.3 breaks the total down per entity type, and what shows up is exactly the imbalance Section 2.4 anticipated.

### 6c. Section 6.2, "One level up…" sentences (p.45)

**Replace the sentences:** "One level up, the imbalance worsens: the O label accounts for roughly seventy-eight percent of all tokens. A naive cross-entropy fine-tune on this distribution reports deceptively high overall accuracy while quietly under-recovering exactly the rare entities an analyst cares about most. This is the distribution that motivates the ablation in Section 6.6."

**With:**

> Zoom out one level and it gets worse, because the O label alone covers roughly seventy-eight percent of all tokens. Train naively with cross entropy on numbers like these and the model posts a flattering overall accuracy while steadily failing on the rare entities — the ones an analyst actually cares about. The ablation in Section 6.6 exists because of this table.

### 6d. Figure 6.1 / 6.2 and Table 6.3 / 6.5 captions (p.46–47)

> **Figure 6.1:** Loss curves for training and validation by epoch; validation loss reaches its minimum at epoch 2, then rises modestly
>
> **Figure 6.2:** Validation accuracy at token level, per epoch, for the representative run
>
> **Table 6.3:** Distribution of entity tokens in the full pre-processed corpus
>
> **Table 6.5:** Training dynamics of the representative run, epoch by epoch

### 6e. Section 6.3, "Two observations stand out" paragraph (p.47)

**Replace the paragraph beginning:** "Two observations stand out. The validation loss bottoms out at epoch 2…"

**With:**

> Two things in Table 6.5 deserve attention. The obvious one: validation loss bottoms out at epoch 2, then creeps upward while training loss keeps falling. Textbook overfitting, and the early-stopping logic (patience 5, threshold 0.001) terminates the run within five further epochs. The less obvious one is that token-level validation accuracy keeps climbing even as validation loss deteriorates. No contradiction is involved. Focal loss with class weighting pushes the model to grow more confident on examples it already classifies correctly — that lifts accuracy — while its calibration on the minority-class boundaries it still gets wrong degrades, and that degradation is the cost the loss records. The patience value was set by reading the two curves against each other; trusting accuracy alone would have meant a longer run and a worse model.

### 6f. Section 6.3, "Convergence this fast" paragraph (p.47)

**Replace the paragraph beginning:** "Convergence this fast — at two epochs — is expected…"

**With:**

> Convergence at two epochs should not surprise anyone. The heavy lifting happened during BERT's pre-training: the encoder shows up to fine-tuning already fluent in English and needs comparatively little adaptation, and a 50,000-example corpus saturates the fine-tuning signal quickly besides. What the model does after epoch 2 is mostly memorise idiosyncratic training phrases — precisely the behaviour early stopping exists to cut off.

### 6g. Section 6.4 opener (p.48)

**Replace the paragraph beginning:** "Before the headline F1 numbers, the loss-function comparison is the cleanest way…"

**With:**

> The loss-function comparison makes a better entry point than the headline F1, because it shows directly whether the imbalance-handling choices earned their keep. Table 6.6 lists best validation metrics for four loss configurations trained under otherwise identical conditions: same data, same scheduler, same early stopping, same random seeds.

### 6h. Section 6.5, "ACTOR, CITY, and DATE form a strong cluster…" (p.49)

**Replace the sentence:** "ACTOR, CITY, and DATE form a strong cluster of entities with rich training distributions and distinctive surface forms."

**With:**

> A strong cluster forms around ACTOR, CITY, and DATE, all three backed by rich training distributions and distinctive surface forms.

### 6i. Section 6.6, "Each ingredient helps on its own…" sentence (p.50)

**Replace the sentence:** "Each ingredient helps on its own (weighted cross entropy lifts VICTIM by seven points, focal loss alone by nine), and the two together lift it by eleven; the combination is complementary rather than redundant, which justifies the slightly more complex production loss."

**With:**

> Neither ingredient is dead weight: on its own, weighted cross entropy buys VICTIM seven points and focal loss nine, while the pair together buys eleven. They are complementary rather than redundant, which is what justifies carrying the more complex loss into production.

### 6j. Section 6.9, closing paragraph (p.52)

**Replace the paragraph beginning:** "Cases 1 and 2 demonstrate correct extraction of canonical armed groups…"

**With:**

> Across the three cases the armed groups, casualty figures, and locations come out correctly and the taxonomy assignments are right, including the multi-actor communal incident of Case 3, where no clean perpetrator-target split exists. Case 1 shows the KB enrichment at its most visible: the surface form "Al Shabaab fighters" collapses to the canonical "Al-Shabaab" with its metadata attached.

### 6k. Section 6.10, opening paragraph (p.52–53)

**Replace the paragraph beginning:** "A small user-acceptance test was run with five participants…"

**With:**

> Five people took part in the user-acceptance test. Two were early-warning analysts, the system's primary audience; one was an academic conflict researcher; the remaining two were software developers comfortable with NLP but new to the application domain, included to check whether the interface makes sense to someone arriving cold. Each participant worked against a deployed instance through a six-task script — run inference on three supplied articles, browse the event store, run an analytics query, train a model on a supplied dataset, monitor a training run to completion, and review a flagged event. Nobody failed a task: all five finished all six. Table 6.10 aggregates the Likert responses, and Annex F reproduces the full questionnaire.

### 6l. Section 6.10, constructive-feedback sentences (p.53)

**Replace the sentences:** "Constructive feedback focused on three points: the analytics dashboard would benefit from an exportable PDF brief… The latter two are scoped into the future-work programme in Chapter 7."

**With:**

> The requests were as useful as the praise. Three came up: an exportable PDF brief out of the analytics dashboard, drag-and-drop file upload on the inference screen, and per-entity validation metrics streaming during training rather than overall loss alone. The latter two are scoped into the future-work programme in Chapter 7.

### 6m. Section 6.11, opening paragraph (p.53)

**Replace the paragraph beginning:** "To understand how the model fails, 300 validation-set events…"

**With:**

> The error analysis was done by brute force: 300 validation-set events on which the model made at least one mistake, read one by one. Five patterns account for essentially all of them, and they are described below in order of frequency.

### 6n. Section 6.11, boundary-mismatch paragraph (p.53)

**Replace the paragraph beginning:** "The largest single category, at roughly 38 percent of all errors, is boundary mismatch…"

**With:**

> Boundary mismatches dominate, at roughly 38 percent of all errors. The model identifies the right entity type but clips the span — "at least 12 civilians" becomes "12 civilians", "approximately 200 displaced" loses its "approximately". VICTIM and CASUALTIES absorb almost all of these, which fits their lower per-entity F1. Note what strict span-level scoring does here: every clipped qualifier counts as a complete miss, so the headline numbers read harsher than an analyst's actual experience of the output. "12 civilians" still carries the fact that matters.

### 6o. Section 6.11, location-confusion paragraph (p.53–54)

**Replace the paragraph beginning:** "Roughly a quarter of errors are type confusion among the three location entities…"

**With:**

> Another quarter of the errors are the three location types confused with one another — REGION for CITY, or REGION for DISTRICT (Figure 6.4). The genuinely hard cases involve places that are two things at once. Goma is a city; Goma is also, in practice, the centre of North Kivu; "fighting in Goma" supports either tag unless the sentence supplies more. Faced with ambiguity the model defaults to CITY, which is right more often than it is wrong but guarantees a steady trickle of confusions under strict scoring.

### 6p. Section 6.11, missed/spurious/confidence paragraph (p.54)

**Replace the paragraph beginning:** "About 19 percent of errors are missed entities, where the model produces no prediction…"

**With:**

> Missed entities — where the model predicts nothing at all — make up about 19 percent. The misses concentrate on victim phrasings the augmentation templates never covered and that ACLED notes phrase more generically ("Christian worshippers", "internally displaced schoolgirls"), and on passive-voice action verbs ("were ambushed", "were displaced"). Spurious entities run at 12 percent, and one source dominates: vague time expressions ("this morning", "earlier") tagged as DATE. Raising the WHEN threshold to 0.85 would eliminate most of them at a measured cost of about 1.2 F1 on legitimate DATE recall — a dial left for the operator to set. The remaining 7 percent are near misses of a different kind, where the model's answer is correct but its averaged sub-token confidence lands just under the category threshold. Lowering the threshold recovers them at some precision cost, the cleanest lever available to a recall-favouring deployment. Figure 6.4 shows the confusion pattern among the location entities.

### 6q. Section 6.11, closing paragraph (p.54)

**Replace the paragraph beginning:** "The error analysis motivates three concrete future-work directions…"

**With:**

> Three future-work directions fall straight out of this analysis. Boundary refinement wants an explicit mechanism — a span-level CRF over the BERT representations is the obvious candidate. The REGION/CITY ambiguity could be attacked at the model level by injecting KB facts as input features during training. And spurious WHEN extractions call for negative examples in the training data. Section 7.5 picks all three up.

### 6r. Section 6.12, opening paragraph (p.54–55)

**Replace the paragraph beginning:** "Several findings from the evaluation are worth stating plainly. The most important, in retrospect…"

**With:**

> Looking back over the evaluation, one finding outranks the rest: dropping EVENT_TYPE and COUNTRY from the supervised schema was the right call. The proposal had committed to a 26-type schema. What changed the plan was the November grounding pilot, where EVENT_TYPE values matched the source text only sporadically — analysts turned out to be inferring event types from context about as often as reading them off the page — and once that was visible the decision made itself. The eight grounded entities trained well. The two dropped types came back cheaply downstream, EVENT_TYPE from action verbs plus the taxonomy classifier and COUNTRY from a single KB look-up. Keeping all 26 would have let the rare types drag down everything else.

### 6s. Section 6.12, "The second finding…" opener (p.55)

**Replace the sentence:** "The second finding is that focal loss with inverse-frequency weighting genuinely helps the entities that matter operationally." (keep the rest of the paragraph)

**With:**

> Next in importance: focal loss with inverse-frequency weighting genuinely helps where it counts operationally.

### 6t. Section 6.12, "That makes the reported metrics…" sentences (p.55)

**Replace the sentences:** "That makes the reported metrics a fair estimate of in-distribution performance but does not guarantee they hold up on out-of-distribution reporting… to find out where this estimate breaks."

**With:**

> In-distribution, then, the reported metrics are a fair estimate. Out of distribution — machine-translated articles, citizen journalism, social-media excerpts — no such guarantee exists, and Section 7.5 puts annotated real-news expansion at the top of the list precisely to find out where the estimate breaks.

### 6u. Section 6.13, opening sentence (p.55)

**Replace:** "The threats are classified along the conventional construct, internal, external, and conclusion axes."

**With:**

> Four conventional axes organise the threats: construct, internal, external, and conclusion validity.

---

## Chapter 7

### 7a. Section 7.1, "What was built" paragraph (p.57)

**Replace the paragraph beginning:** "What was built, in one paragraph: an eight-entity grounded schema…"

**With:**

> The inventory of what was delivered runs from the schema outward. At the core sits an eight-entity grounded schema in BIO format: ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES. Feeding it is a 50,000-example training corpus built from ACLED notes through stratified diversity sampling and template augmentation, both aimed at a heavily skewed label distribution. The model trained on that corpus is a fine-tuned bert-base-cased with focal loss (γ = 2) and inverse-frequency class weights. Around the model sit two knowledge artefacts — a four-level hierarchical taxonomy of African violent events, roughly ninety-five terminal categories synthesised from ACLED, UCDP, and PMVE with African-specific extensions, and a curated knowledge base holding approximately 150 armed groups, 200 conflict-affected cities, and all 54 African countries with their regions. The outermost layer is the platform: a FastAPI service covering training, inference, event storage, analytics, and knowledge-base management, a React/TypeScript front-end over it, and a Docker Compose deployment that reproduces the whole stack.

### 7b. Section 7.1, "What the numbers say" paragraph (p.57)

**Replace the paragraph beginning:** "What the numbers say: macro F1 0.887 and micro F1 0.909…"

**With:**

> The numbers, and what each one means. Macro F1 reached 0.887 and micro F1 0.909 on the held-out validation set. Validation loss bottomed at epoch 2; the model overfits beyond that point, and early stopping catches it. The focal-loss and class-weighting combination earns its complexity, lifting VICTIM by eleven F1 points and ACTION by seven over plain cross entropy. The knowledge base canonicalises roughly two thirds of high-confidence ACTOR spans, and flags about one multi-entity event in forty as geographically implausible — few enough not to annoy, real enough to matter. Inference on a typical article completes in hundreds of milliseconds. User-acceptance testing returned a mean of 4.4 out of 5.0 across six task dimensions.

### 7c. Section 7.1, "ten specific objectives" paragraph (p.57)

**Replace the paragraph beginning:** "The ten specific objectives stated in Section 1.4 are addressed across Chapters 2, 4, and 5…"

**With:**

> Every one of the ten specific objectives in Section 1.4 has a home in the document: the literature review in Chapter 2; schema, taxonomy, data, and training across Chapters 4 and 5; the knowledge base in Sections 4.5 and 5.6; back-end and front-end in Sections 5.6 and 5.7; evaluation in Chapter 6; and limitations with future work in Section 1.6 and this chapter. The four research questions of Section 1.3 get explicit answers next.

### 7d. Section 7.4, first recommendation (p.59)

**Replace the paragraph beginning:** "First, treat the extraction output as a triage layer rather than a final product…"

**With:**

> The first recommendation is about expectations: use the extraction output as triage, never as a finished product. What the model reliably does is turn raw incoming news into something an analyst can work from far faster than from the articles themselves. What it cannot do is replace the analyst's judgement when a consequential decision hangs on an extraction. The confidence scores and the KB's inconsistency flags exist precisely to make that triage decision visible, so surface them in whatever workflow consumes the output. Treating the output as finished is the main failure mode to guard against.

### 7e. Section 7.4, second recommendation (p.59–60)

**Replace the paragraph beginning:** "Second, keep the knowledge base alive. Armed groups in Africa change names…"

**With:**

> Keep the knowledge base alive, too. African armed groups rename themselves, splinter, recombine, occasionally reconcile; country and region affiliations move. The KB's value tracks its currency directly — and a stale KB is worse than none, because it feeds the validator wrong answers with confidence. In practice, one or two part-time domain experts with access to the admin interface and a regular update cadence are enough to keep it in working order.

---

## Annexes

### A1. Annex A entity guidelines (p.65–66) — *structural fix: vary sentence shape per entity*

**Replace A.1 ACTOR Include/Exclude:**

> Tag as ACTOR: named organisations ("Boko Haram", "Al-Shabaab", "M23 rebels"); descriptive references such as "armed men", "gunmen", "militants", "insurgents", "attackers", "assailants", and "raiders"; state security forces, whether named ("ENDF", "FARDC") or generic ("police", "military", "army", "security forces"); specific individuals acting as the perpetrator ("the suicide bomber", "the assailant"); and ethnic or communal groups when they perpetrate violence ("Fulani herders", "ethnic militia"). Two things are never ACTORs: inanimate causes like "the bomb" or "the explosion", which are methods rather than actors, and agentless passive constructions — in "12 were killed", nothing is tagged.

**Replace A.2 VICTIM Include/Exclude:**

> VICTIM covers whoever the violence lands on. That includes specific individuals ("the mayor", "aid workers", "journalist Y"), groups ("civilians", "protesters", "worshippers", "students"), demographic descriptions ("women and children", "displaced persons"), and numeric victim counts ("12 people", "dozens of civilians"). Infrastructure counts as a victim when the violence targets it ("the power plant", "the bridge"). Perpetrators are excluded, as are third parties the violence did not affect.

**Replace A.3 ACTION Include/Exclude:**

> For ACTION, tag the verbs that carry the violence itself — "attacked", "killed", "ambushed", "raided", "abducted", "bombed", "stormed" — plus nominalised forms when they serve as the main predicate ("an attack", "the raid"). Reporting verbs like "said", "reported", and "claimed" describe the journalism, not the event, and stay untagged.

**Replace A.4 DATE Include/Exclude:**

> Temporal expressions are tagged as DATE whether absolute ("20 December 2024", "January 15"), relative ("yesterday", "last Tuesday", "earlier this week"), or day-of-week ("on Monday"). A year given as background context — "since 2017" — is not an event date and is left alone.

**Replace A.5 REGION / CITY / DISTRICT text:**

> Locations are annotated at the most specific level the text mentions, following the hierarchy: specific site < village/neighbourhood < city/town < district/county < state/province/region < country < sub-region. COUNTRY has no place in the model schema; the knowledge base resolves it deterministically from CITY and REGION.

**Replace A.6 CASUALTIES Include/Exclude:**

> Numeric harm goes under CASUALTIES: death counts with their descriptors ("killed 12", "3 dead", "5 fatalities"), injury counts ("wounded 7", "20 injured"), and displacement figures when phrased in the same casualty-style construction ("displacing 2,000"). Damage with no number attached — "extensive damage" — does not qualify.

### A2. Annex B intro (p.67)

**Replace the paragraph beginning:** "This annex reproduces, in full, the taxonomy developed during the literature-review phase…"

**With:**

> The taxonomy reproduced here, in full, is the working document developed during the literature-review phase and kept current throughout development; Section 4.4 treats it as the canonical reference. It synthesises ACLED [8], UCDP [9], and the PMVE ontology [29], then extends them with the African-specific categories — pastoralist-farmer clashes and communal cattle raiding above all — that none of the three covers at this depth. Where a Level 4 subtype exists it is listed; most branches stop at Level 3.

### A3. Annex C intro (p.71)

**Replace the text beginning:** "The knowledge base contains approximately 150 armed groups. The following entries are an illustrative excerpt…"

**With:**

> Around 150 armed groups are recorded in the knowledge base. What follows is an illustrative excerpt; backend/pipeline/kb.py holds the complete list.

### A4. Annex D intro (p.73)

**Replace the paragraph beginning:** "This annex collects representative screenshots of the deployed web application…"

**With:**

> The screenshots collected here show the deployed web application, one for each of the main route groups of Section 5.7. The printed submission reproduces them in greyscale; full-colour versions are on the accompanying CD, per Annex D of the AAU thesis guideline.

### A5. Annex D captions D.1–D.4 (p.73)

> **D.1 Inference screen.** Pasted text on the left; highlighted entities and the 5W1H breakdown on the right; hovering reveals each span's confidence.
>
> **D.2 Document upload for inference.** Shows the drag-and-drop area, processing status, and the resulting entity table.
>
> **D.3 The training run list.** Past runs in a sortable, filterable table — model, dataset, status, best epoch, final validation loss.
>
> **D.4 Live detail view of a training run.** Loss chart updating in real time, epoch progress bar, scrolling log output, and a cancel control.

---

## After pasting

1. Re-export the PDF and re-run the draft similarity check if your institution allows it.
2. Spot-check: Table 4.6 numbering (new table in 4.8), and that "the second is modular
   pipeline" in 4.1 still reads naturally after its neighbours changed (it does — the
   rewritten first principle opens with "Grounded supervision came first").
3. The unflagged 6.10 sentence about positive comments ("The most common qualitative
   comments were positive…") stays as is; the replacement in 6l starts right after it.
4. Read each pasted block aloud once. If a sentence trips your tongue, change it to
   whatever you actually said — your spoken fix is better camouflage than anything here.
