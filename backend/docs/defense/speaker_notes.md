# VioNER Defense — Speaker Notes

**Format:** one block per slide. Numbers in brackets are the **target seconds** at a steady delivery pace (≈150 words/minute). Sum across all 26 main slides ≈ **27 minutes**, leaving 3 minutes of slack. Print this file double-sided in 11pt and tab it to slide numbers for the talk.

Pace discipline: if you finish slide 12 by the **10-minute mark**, you are on track. If you finish slide 12 by minute 13 you are running 20% slow — start tightening transitions, drop one example per slide, do not skip slides.

---

## Slide 1 — Title [30 s]

> "Good morning, distinguished examiners. I'm Binalfew Kassa. The work I'll be presenting today builds an end-to-end system for extracting structured information about violent events in Africa from English-language news reports. The thesis is supervised by [Advisor], and the talk will run roughly twenty-five minutes followed by your questions."

Stand still. Look up, then down at notes, then up again. Do not read the title. Move on within 30 seconds.

---

## Slide 2 — Outline [45 s]

> "The talk has eight beats. We'll begin with the problem — why African conflict monitoring needs this kind of system. Then the research questions and the gap in prior work. Most of the middle of the talk is the approach: how the schema, the BERT model, the knowledge base, and the deployable platform fit together. We then move into the evaluation results — what the validation set says, what the ablation says, and what the user-acceptance test says. We close with contributions, limitations, and future work."

> "There is a twelve-slide backup deck after slide 26. If you ask me a question whose answer lives in the backup, I'll flip to it. You are also welcome to interrupt with clarifying questions during the talk."

---

## Slide 3 — Section divider: Problem [10 s]

> "We begin with the problem."

Pause. Click forward.

---

## Slide 4 — A continent-scale information bottleneck [70 s]

> "Across the African continent, news outlets report tens of thousands of violent events every year — armed clashes, attacks on civilians, political repression, communal violence. The AU's Continental Early Warning System, ACLED, UCDP, and dozens of humanitarian agencies all need this stream of news converted into structured, queryable event records."

> "Today, that conversion is almost entirely manual. An analyst reads an article, decides what kind of event it is, identifies the perpetrator, the victims, the location, the date, the casualty count, and types those into a database. The binding constraint on continental situation awareness during a fast-moving crisis is the time it takes an analyst to do that, not the data being unavailable."

> "Even a partial reduction in the cost of producing one structured record from one news article translates almost one-to-one into faster, broader, and more consistent monitoring. That is the operational case for building VioNER at all."

---

## Slide 5 — The structured-record requirement [75 s]

> "To make this concrete: here is a single sentence drawn from a real news article."

Read the example slowly.

> "'On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least 12 soldiers.'"

> "An operational analyst needs that sentence turned into the record on the right. Six fields, one per 5W1H slot. The WHO is Al-Shabaab — but also the soldiers, who are the victims. The WHAT is an armed attack. The WHEN is Tuesday. The WHERE is near Mogadishu, in Somalia. The HOW captures the casualty count with its qualifier."

> "When we ran this exact sentence through off-the-shelf NER models — spaCy and HuggingFace's English NER head — Al-Shabaab came back as the generic ORGANIZATION class, which is technically correct and operationally useless. The convoy and the soldiers were not tagged as victims at all because the standard NER schemas don't distinguish perpetrators from victims. That gap is what this thesis closes."

---

## Slide 6 — Section divider: Research Questions [10 s]

> "Four research questions structure the work."

---

## Slide 7 — Research questions [90 s]

> "RQ1 is the schema question. Not all of the entities an analyst cares about can be reliably grounded in source text — some, like motive, are usually inferred rather than written. So the first question is: which entity types CAN we reliably tag, and what BIO schema fits those choices."

> "RQ2 is the modelling question. Given the chosen schema, how well does a fine-tuned BERT model perform, and crucially under severe class imbalance — 78 % of all tokens are not entities at all — what loss function and sampling strategy produce balanced per-entity performance."

> "RQ3 is the knowledge-base question. A model alone, even a good one, doesn't validate its own outputs. RQ3 asks how much a curated KB of African armed groups, conflict locations, and a hierarchical taxonomy improves the trustworthiness and downstream utility of extracted records."

> "RQ4 is the systems question — the one that is often skipped in event-extraction papers. What system architecture lets the model, the KB, and the analytics layer be operated together by users who are not machine-learning specialists."

> "I'll tag each results slide with the RQ it answers."

---

## Slide 8 — Section divider: Related Work [10 s]

> "Where prior systems stop, this thesis starts."

---

## Slide 9 — The related-work landscape [80 s]

> "Two axes. Across the top, generic news domain versus the conflict and African context. Down the side, the modelling family — classical sequence models, transformer NER, structured event databases, and end-to-end deployed extraction systems."

> "Stanford NER and spaCy occupy the top-left cell — generic, well-known, not tuned for African content. The HuggingFace BERT-NER models occupy the second row left — strong on generic news, weak on African armed-group names that didn't appear in their pre-training corpus. ICEWS and GDELT are large structured event databases for general news; ACLED and UCDP are the African and conflict-domain analogues — but both are hand-coded."

> "The cell I want you to look at is the bottom-right one. End-to-end deployed extraction in the African context is, in the academic literature, essentially absent. The model gets published; the operational layer does not. That is the empty cell this thesis fills."

---

## Slide 10 — The gap this thesis closes [75 s]

> "The claim, then, is that most African event-extraction work stops at the model boundary. The artefact published is the model, and the operational layer — the schema choices, the knowledge base, the validation logic, the user interface, the deployment story — is treated as an implementation footnote not worth reporting."

> "This thesis treats the operational layer as a first-class research output. Four concrete pieces: a schema chosen for grounding rate rather than theoretical neatness; a focal-loss-plus-class-weight training recipe that protects rare entities; a curated knowledge base that validates AND enriches extractions; and a deployable web platform that a non-ML user can operate."

> "The next sections walk through each piece."

---

## Slide 11 — Section divider: Approach [10 s]

> "We move into the approach."

---

## Slide 12 — Entity schema [100 s]

> "RQ1 — the schema. The original proposal called for twenty-six entity types: motive, trigger, organisation, duration, frequency, and so on. In November 2025 I ran a grounding pilot — a small sample of articles annotated by hand — to measure, for each entity type, what fraction could be located VERBATIM in the source text rather than inferred from context."

> "Types whose grounding rate fell below eighty percent were dropped from the NER schema. The motive of an attack, for example, is almost never written down — annotators infer it. Training a model on inferred-not-grounded labels would introduce systematic noise, because the same article would get different motive labels from different annotators."

> "What remained were eight entities, shown in the left column: ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES. In BIO encoding that becomes seventeen labels."

> "The dropped types in the right column are recovered downstream — EVENT_TYPE by the taxonomy classifier from the action verb, COUNTRY by a KB look-up off the most specific WHERE entity. Eight grounded entities trained cleanly; the two that were dropped came back essentially for free at inference time. That trade was the single most important methodological choice of the thesis."

---

## Slide 13 — Four-level taxonomy [80 s]

> "RQ3 first ingredient — the taxonomy. Four levels, ninety-five terminal categories. Level zero is the root. Level one has four families: political violence, criminal violence, communal violence, and state violence against civilians. Level two breaks those into operational subcategories — terrorism, election violence, armed robbery, ethnic clashes, and so on. Level three carries the leaf categories: bombing, ambush, soft target attack."

> "The taxonomy synthesises ACLED, UCDP, and the PMVE ontology, but it adds two African-specific extensions that none of those frameworks cover at this depth: pastoralist-farmer clashes, and communal cattle raiding. Those two account for a measurable fraction of Sahel and Horn of Africa reporting and don't sit cleanly in ACLED's 'Violence against civilians' bucket."

> "The full tree is in Annex B; you can flip to backup slide B5 if you want to see it."

---

## Slide 14 — BIO encoding [70 s]

> "How are the labels actually applied? BIO encoding. B for the first token of an entity, I for continuation tokens, O for everything outside any entity. The code block shows the example: Al-Shabaab fighters becomes B-ACTOR followed by three I-ACTORs, including the hyphen subword."

> "We use BIO rather than BIOES because the African news corpus almost never has adjacent same-type entities with no intervening token. BIOES would double the label space from seventeen to thirty-three without buying anything for ninety-five percent of cases — and a larger label space worsens the class-imbalance problem we already have to handle."

---

## Slide 15 — System architecture [70 s]

> "RQ4 — the architecture. Four layers. React with TypeScript at the top — what the analyst sees. FastAPI in the middle — a thin Python service exposing seven route groups: training, inference, events, analytics, KB, auth, and system administration. The NER component and the knowledge base are loaded ONCE into the FastAPI process so that per-request inference is in-memory and fast. PostgreSQL at the bottom is the persistent state — stored events, training runs, user accounts."

> "Docker Compose orchestrates the three services. A clean separation means a domain analyst can install Docker, run one command, and have the full stack running locally."

---

## Slide 16 — End-to-end processing pipeline [90 s]

> "And here is what happens when an analyst pastes one article into that UI. Step one: the article hits the FastAPI inference route. Step two: WordPiece tokenisation produces the sub-word input BERT expects. Step three: forward pass through the fine-tuned BERT returns per-token softmax distributions over the seventeen labels. Step four: a BIO decoder collapses contiguous B-I sequences into spans. Step five: confidence filtering drops spans whose averaged sub-token probability sits below a per-category threshold."

> "Step six: 5W1H grouping bucketises spans into the six output categories. Step seven: the KB validates ACTOR and CITY against curated reference data. Step eight: the taxonomy classifier assigns a Level-1 to Level-3 path from the ACTION verb and the actor context. Step nine: the structured record is persisted to PostgreSQL. Step ten: the UI renders it for the analyst."

> "End-to-end on a single CPU core, this takes about a hundred and fifty milliseconds per typical article."

---

## Slide 17 — Training recipe [100 s]

> "RQ2 — the modelling core. Backbone is bert-base-cased, a hundred and ten million parameters, fine-tuned end-to-end with a seventeen-label token-classification head."

> "The loss function is the key design choice. We use focal loss with inverse-frequency class weights. The intuition: seventy-eight percent of all tokens are outside any entity. Plain cross-entropy treats those as equal to actual entity tokens, so the gradient signal for the rare classes — VICTIM, CASUALTIES, ACTION — gets drowned out by the easy O predictions."

> "Class weights raise the gradient for rare classes. Focal loss with gamma equal to two further down-weights the easy correctly-predicted O tokens so the model spends more capacity on hard cases. The two together are complementary. Section 6.6 of the thesis shows the ablation: focal alone gets us partway, weights alone get us partway, but the combination gets us further than the sum of those two parts. That complementarity is the answer to the second half of RQ2."

---

## Slide 18 — Knowledge base [100 s]

> "RQ3 second ingredient — the knowledge base. We curated roughly a hundred and fifty African armed groups with their canonical names, aliases, country and region of operation, and group type. Two hundred conflict-affected cities mapped to country and region. All fifty-four African countries. A weapons catalogue."

> "The KB plays two roles. First, validation. When the model extracts 'Al-Shabaab fighters' and 'Goma' in the same sentence, the KB knows Al-Shabaab operates in Somalia, not eastern DRC. The validator flags that event as geographically implausible. The flag rate is two-point-four percent — small in aggregate, but those are exactly the events an analyst should re-read before trusting."

> "Second, enrichment. 'Al Shabaab', 'al-shabaab', 'Al-Shabaab militants' all canonicalise to a single key. Sixty-four-point-three percent of extracted ACTOR mentions get enriched this way, which is what lets the analytics layer aggregate by actor correctly."

---

## Slide 19 — Dataset and annotation [90 s]

> "Where the data came from. The fine-tuning corpus has fifty thousand examples. Thirty-five thousand of them are real ACLED open-data records, but filtered by stratified diversity sampling, not naive random sampling, because the full two-hundred-twelve-thousand-event extract had so much repetition of common phrasings that the rare entities got drowned out. I learned that the hard way in October 2025 — the first model trained on the full extract scored lower on rare-entity F1 than later models on smaller, more diverse corpora."

> "The remaining fifteen thousand examples are template-based augmentation specifically targeting the rare classes — VICTIM, ACTION, CASUALTIES — to lift them off the floor."

> "Splits are eighty-twenty train and validation, stratified on entity-type presence. Class imbalance is seventy-eight percent O versus twenty-two percent entity tokens — and within entities the operationally most important categories are the rarest. That is what motivates the focal-loss recipe on the previous slide."

---

## Slide 20 — Training configuration [75 s]

> "Hyperparameters. Categorised by source. The backbone, the focal loss gamma, and the learning rate are inherited from the BERT-NER literature. Batch size and max sequence length are architecture-driven — bounded by memory on the training hardware. The warmup ratio, the class-weight scheme, and the early-stopping configuration came out of empirical grid search."

> "The headline number on this slide is the epoch count — the best validation checkpoint converges in just two epochs. Short training runs made it cheap to iterate during development. Backup slide B1 has the full table; backup B2 has per-epoch loss and accuracy."

---

## Slide 21 — Section divider: Results [10 s]

> "Results."

---

## Slide 22 — Overall performance [30 s]

> "Headline number: zero-point-nine-zero-nine micro F1, on the held-out validation set, across one hundred ninety thousand gold spans. Macro F1 of zero-point-eight-eight-seven. Token accuracy of ninety-six-point-seven percent — informative but secondary because the O class dominates."

> "Per-category detail on the next slide."

---

## Slide 23 — Per-entity F1 [100 s]

> "Walk the table top to bottom. DATE wins by a clear margin at point-nine-five-six F1 — date expressions in conflict reporting follow a small set of recognisable patterns: 'on Monday', 'January 15th', 'earlier this week'. CITY at point-nine-three-four and ACTOR at point-nine-two-three round out the strong cluster of three high-volume entities with distinctive surface forms."

> "Middle tier: REGION at point-eight-nine-one, CASUALTIES at point-eight-eight-five, ACTION at point-eight-six-six. The dip here correlates more with the entity's compositional irregularity than with sheer training volume — REGION names that double as cities, CASUALTIES that mix numerals and words, ACTION verbs in passive voice."

> "Bottom of the table is the honest story. DISTRICT at point-eight-two-six loses most of its accuracy to confusion with CITY and REGION — Table 6.11, next slide. VICTIM at point-eight-one-seven is both the rarest entity in the corpus AND the one with the most variable phrasing."

> "Macro F1 of point-eight-eight-seven means every entity, including the rarest, is recognised well enough to be useful operationally."

---

## Slide 24 — Ablation [90 s]

> "This is the ablation that answers RQ2 directly. Four loss configurations: plain cross-entropy, weighted cross-entropy, focal loss alone, and focal loss with class weights. Identical data, identical scheduler, identical early-stopping, identical random seeds — only the loss function changes."

> "Read the rare-entity rows. VICTIM moves from point-seven-zero-eight under plain cross-entropy to point-eight-one-seven under focal-plus-weights — a gain of eleven F1 points. ACTION gains seven. CASUALTIES gains three."

> "Each ingredient on its own helps a little. The two together help more than the sum of parts. That complementarity is what justifies the slightly more complex loss in production."

> "Crucially: NO entity is hurt by this loss choice. We do not pay for VICTIM's gain in ACTOR or DATE accuracy — a trade-off that would have been operationally unacceptable for analyst workflows that depend on ACTOR and DATE."

---

## Slide 25 — Location confusion patterns [90 s]

> "The error analysis ran over three hundred validation events that the model got wrong. The single biggest error category — thirty-eight percent — is boundary mismatch: the model gets the entity type right but the span slightly wrong, usually clipping a qualifier."

> "Second biggest is location-type confusion, shown in this matrix. Rows are gold labels, columns are predictions, diagonal omitted because it represents correct predictions, not errors. DISTRICT is the hardest — eight percent confused with CITY and nine percent with REGION."

> "The hard cases involve places that are simultaneously a city, a district capital, and the de-facto centre of a region. Goma is the canonical example: city, district capital, and centre of North Kivu province. 'Fighting in Goma' can be labelled any of the three without more context. The model defaults to CITY, which is more often right than wrong, but it produces a consistent stream of confusions."

> "The fix is in high-priority future work: a span-level CRF on top of the BERT representations to refine boundaries and resolve the ambiguity."

---

## Slide 26 — Section divider: System in use [10 s]

> "How the system actually feels in the analyst's hands."

---

## Slide 27 — Inference and event browser [80 s]

> "Two screens side by side. On the left, the inference screen — the analyst pastes an article into the left pane and gets colour-coded entity chips on the right, grouped by 5W1H category. Confidence is shown per chip. KB-enriched actors show their canonical name and country flag. KB-flagged events are highlighted in amber."

> "On the right, the event browser. Once events are persisted, the analyst can filter by date range, country, taxonomy level, perpetrator. Sortable columns, pagination, CSV export. These two screens are what the analyst spends most of their time in."

---

## Slide 28 — Training and analytics [90 s]

> "The other two surfaces. Training screen, left — a non-ML user picks the dataset, the loss function, and the hyperparameters from drop-downs. They kick off a run and watch the loss curve update live over a WebSocket. The training service runs the job asynchronously; the user can navigate away and come back."

> "Analytics dashboard, right. Aggregated views over the event store: events per country, per taxonomy bucket, per actor, per month. KPI cards at the top, temporal trend charts below. This is the screen that turns the extracted records back into operational insight. The most common UAT feedback was a request for exportable PDF briefs, which is now in future work."

---

## Slide 29 — User acceptance test [100 s]

> "Numbers from the test. Five participants — two early-warning analysts, who are the primary intended audience; one academic conflict researcher, secondary audience; and two NLP developers unfamiliar with the application domain, included as a fairness sanity check. All five completed all six tasks: inference on three supplied articles, browse the event store, run an analytics query, train a model, monitor it to completion, and review a flagged event."

> "All six Likert items clear four-point-zero. The two highest items — 5W1H structuring clarity at four-point-six and KB enrichment value at four-point-six — are exactly the two things the thesis claims as differentiating contributions."

> "The lowest item is the training-screen ease at four-point-zero. Constructive feedback there — drag-and-drop file upload, per-entity validation metrics during training — fed directly into future work."

---

## Slide 30 — Section divider: Contributions [10 s]

> "Closing — contributions, limitations, future work."

---

## Slide 31 — Contributions [100 s]

> "Five concrete artefacts that this thesis leaves behind."

> "First, the eight-entity BIO schema with grounding-based inclusion rules — every label is verifiably present in source text. The schema lives in Annex A of the thesis and is reusable by any researcher working on African violent-event extraction."

> "Second, the four-level taxonomy with around ninety-five terminal categories, including African-specific extensions for pastoralist-farmer clashes and communal cattle raiding that ACLED, UCDP, and PMVE do not cover."

> "Third, the training recipe — focal loss plus inverse-frequency class weights — that lifts VICTIM by eleven F1 points and ACTION by seven without hurting other entities. Reproducible from the configurations in the repository."

> "Fourth, the curated knowledge base — a hundred and fifty armed groups, two hundred cities, fifty-four countries, weapons. Plays the dual validate-and-enrich role."

> "Fifth, the deployable web platform — FastAPI, React, PostgreSQL — packaged with Docker Compose and end-to-end documented. This is the contribution the related-work landscape said was missing."

---

## Slide 32 — Limitations [110 s]

> "I want to own the limitations explicitly because they will tell you where this work stops being useful."

> "One: English-language only. A large share of African conflict reporting is in French, Arabic, Portuguese, and African languages. A monolingual extractor — even a good one — leaves that signal on the floor. This is the single most important capability gap."

> "Two: roughly thirty percent of the training corpus is template-augmented. The validation split is drawn from the same combined corpus, which makes the metrics a fair estimate of IN-distribution performance but does not guarantee they hold up on translated articles, citizen journalism, or social-media excerpts."

> "Three: no head-to-head comparison against a learned hierarchical event-type classifier. EVENT_TYPE is recovered post-hoc by a rule-based taxonomy classifier; a learned version was scoped out of this thesis and is the second high-priority future-work item."

> "Four: knowledge-base coverage decays without curation. Armed groups change names, splinter, recombine. A stale KB does worse than no KB, because it actively misleads the validator. Operational deployments need a domain expert to keep it current."

---

## Slide 33 — Future work [90 s]

> "Three highest-priority directions, each tied back to a limitation."

> "First: multilingual extension using XLM-R or AfroLM as the backbone, fine-tuned on parallel corpora from African outlets and ACLED's multilingual coverage. This closes the biggest operational gap."

> "Second: a learned hierarchical event classifier to replace the rule-based taxonomy step. Two-stage — Level 1 first, then Levels 2 and 3 conditional on Level 1 — is the natural starting point. Rule-based was the right thing to ship; learned will scale as the taxonomy grows."

> "Third: natural-language QA over the event store. Templated SQL from semantic parses for the cheap path, fine-tuned Seq2Seq for the flexible path. This closes the loop for analysts who want to ask 'show me all events attributed to JNIM in the last thirty days' without writing SQL."

> "Medium- and lower-priority items are in Chapter 7.5 of the thesis."

---

## Slide 34 — Thank you [30 s]

> "Thank you for your attention. I welcome your questions."

Pause for at least two seconds before the first question lands. Do not rush to fill the silence. When a question comes, breathe before answering. If you don't know, say so explicitly and offer what you do know.

---

## Rehearsal plan

| Pass | Goal | Cadence |
|:--|:--|:--|
| 1 | Read this document straight through; check pacing | Voice-only, sitting |
| 2 | Stand and deliver with slides, no notes | Time yourself; aim for 27 min total |
| 3 | Record on phone; play back at 1.25× | Note where you slow down |
| 4 | Deliver to one trusted listener (a peer, not your advisor) | Ask them to interrupt with one mid-talk question |
| 5 | Full rehearsal with backup-slide flips on cued questions | Use the Q&A kit |

**Three days before the defense:** stop changing slides. Memorise the opening sentence of every slide. Sleep.

**Defense day:** drink water. Arrive thirty minutes early. Test the projector connection BEFORE the panel walks in. Open `slides.pdf` and `slides.pptx` both — PDF as the safe fallback if PowerPoint misbehaves.
