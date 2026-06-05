# VioNER Defense — Speaker Notes (Teaching Format)

**How to use this document.** Each slide block has five parts:

1. **WHAT'S ON SCREEN** — describes the slide so you know what the panel is looking at.
2. **WHY THIS SLIDE EXISTS** — the panel value; why it sits at this point in the arc.
3. **WHAT TO SAY** — the verbatim script. Every technical term is explained inline. Read the words in italics aloud; the rest is staging.
4. **IF THEY PROBE** — the 2–4 most likely interruption questions with one-line ready answers.
5. **PIVOT TO NEXT SLIDE** — a one-sentence transition so you don't end a slide on dead air.

**Pacing.** 31 main slides + dividers ≈ **29 minutes** inside your 30-minute slot. If you finish slide 15 (Approach divider) by **minute 13** you are on track. If by minute 15 you are running slow — tighten transitions, trim one example per remaining slide.

**Rehearsal mantra.** Pause-then-speak. The pause makes you sound considered. The script gives you the words. The probe answers cover the ambushes. The pivot moves you forward.

---

## Slide 1 — Title [30 s]

**What's on screen.** Title page: thesis title, your name, advisor, AAU CS Department, date.

**Why this slide exists.** First impression. The panel decides in the first 60 seconds whether you sound confident or rattled.

**What to say (verbatim):**

> *"Good morning, distinguished examiners. I'm Binalfew Kassa. The thesis I'll be defending today builds an end-to-end system for extracting structured information about violent events in Africa from English-language news reports. The work was supervised by [Advisor's name]. I'll speak for about thirty minutes, then I welcome your questions."*

Stand still. Eye contact. Do not read the slide title back at the panel — they can already see it.

**If they probe (rare on title slide):**
- **"How long will you speak?"** — *"About thirty minutes for the presentation, then I'm happy to take questions for as long as you need."*

**Pivot to next slide.**

> *"Here is what we'll cover."*

---

## Slide 2 — Outline [45 s]

**What's on screen.** Eight-item outline: problem, research questions, gap, approach, system, results, system in use, conclusions.

**Why this slide exists.** Sets the panel's mental map. Tells them when to expect each kind of evidence (problem first, results in the middle, contributions at the end). Lets them park questions until the right section.

**What to say (verbatim):**

> *"The talk has eight sections. We begin with the problem — why African conflict monitoring is bottlenecked today. Then the four research questions this thesis answers. Then a related-work landscape showing where prior systems stop and where this work starts. The middle of the talk is the approach: the entity schema, the BERT model, the knowledge base, and the deployable platform. We then move into results — what the validation set says, what the ablation says, what the user-acceptance test says. We close with contributions, limitations, and future work."*

> *"There are also twelve backup slides after the main deck. If you ask me a question whose answer lives in the backup, I'll flip there. You are welcome to interrupt with clarifying questions during the talk."*

**If they probe:**
- **"Will you take questions during the talk or only at the end?"** — *"Either is fine — I'll pause for clarifying questions whenever you raise a hand, and we'll do deeper questions after the close."*

**Pivot to next slide.**

> *"Let's begin with the problem."*

---

## Slide 3 — Section divider: Problem [10 s]

**What's on screen.** Full-bleed divider — "1. The Problem · Why African conflict monitoring needs structured extraction".

**Why this slide exists.** Cleanly signals the start of the problem section.

**What to say.**

> *"The problem this thesis addresses is operational, not theoretical. Let me show you what it costs in practice."*

**Pivot.** Click forward.

---

## Slide 4 — A continent-scale information bottleneck [70 s]

**What's on screen.** A big-quote block stating "over 30,000 violent events reported per year", three bullets naming AU-CEWS, ACLED, and humanitarian agencies as the consumers of structured records, and an italic line saying analyst time is the binding constraint.

**Why this slide exists.** The panel needs to believe two things by the end: (a) the problem is real and at scale; (b) the bottleneck is human time, not data availability. Without this, the whole thesis sounds like an academic exercise.

**What to say (verbatim):**

> *"Across the African continent, news outlets report tens of thousands of violent events every year. Armed clashes, attacks on civilians, election violence, communal disputes, state repression — all of it ends up in news articles."*

> *"The institutions that need this information in structured form are well-known. The African Union's Continental Early Warning System, known as AU-CEWS — which sits a short drive from this campus — is mandated by the AU to monitor and report on conflict across the continent. ACLED, the Armed Conflict Location and Event Data project, is the global gold standard for African conflict data. UCDP is the Uppsala-based equivalent. Humanitarian agencies — OCHA, the IFRC, MSF — all rely on this stream of news being converted into structured event records."*

> *"Today, that conversion is almost entirely manual. An analyst reads each article, decides what type of event it is, identifies the perpetrator, the victims, the location, the date, the casualty count, cross-references against an actor list, and types the result into a database."*

> *"The binding constraint on continental situation awareness during a fast-moving crisis is the time it takes an analyst to do that — not the data being unavailable. Reducing that time by even a fraction translates almost one-to-one into faster, broader, and more consistent monitoring."*

**If they probe:**
- **"Where does the 30,000-events figure come from?"** — *"That's an aggregate from ACLED's African coverage; the exact figure varies by year but has been above 30,000 every year since 2020."*
- **"Is this only relevant to AU-CEWS?"** — *"No — humanitarian agencies, research groups, and national governments all have analogous pipelines. AU-CEWS is the most institutionally visible consumer but it's not the only one."*
- **"Why not just use ACLED's output directly?"** — *"ACLED is hand-coded, so its quality is high but its throughput is limited by exactly the same analyst-time bottleneck. We address the upstream extraction, not the downstream curation."*

**Pivot to next slide.**

> *"Let me quantify what 'bottleneck' actually means."*

---

## Slide 5 — The cost of the manual pipeline [65 s]

**What's on screen.** Five-row table: 30,000 events/year, 15–25 minutes per article, ≈10,000 analyst-hours required for full coverage, ≈5 FTE pure-coding analysts, days-to-weeks time-to-record during surge. Below the table, an italic punchline: *every minute saved per article ≈ 500 analyst-hours recovered per year.*

**Why this slide exists.** Without numbers, "the analyst is slow" is just an assertion. With this table, the panel sees scale and immediately understands why automation here is high-leverage. The punchline gives them the headline they'll quote later.

**What to say (verbatim):**

> *"Some numbers to make the bottleneck concrete. About thirty thousand violent events are reported across African news outlets every year. The mean time for an analyst to convert one article into a structured database record — including reading, cross-referencing the actor, and logging the row — is fifteen to twenty-five minutes. Multiply that out and the annual burden to cover the full feed is roughly ten thousand analyst-hours."*

> *"In full-time-equivalent terms, that's about five analysts whose entire job is pure coding — that is, just converting articles into records, doing nothing else. During a surge week, like the early days of the Sudan conflict in April 2023, time-to-record can blow out to days or weeks. That delay is the difference between an early-warning system that warns and one that just records history."*

> *"The leverage point is the bottom line. Every minute saved per article translates into about five hundred analyst-hours recovered per year. That is what makes this a worthwhile machine-learning problem rather than a curiosity."*

**If they probe:**
- **"Are those numbers from your own study or from the literature?"** — *"The fifteen-to-twenty-five-minute figure is consistent with ACLED's own coder-throughput documentation; the FTE arithmetic is a simple multiplication. Section 1.2 of the thesis cites the sources."*
- **"Is full coverage even the goal? Couldn't analysts just triage?"** — *"They do triage, but the triage itself takes time, and the cost of triage scales with article volume. The number quantifies the upper bound on what full coverage would demand."*

**Pivot.**

> *"The numbers tell one story; here's what the same problem looks like inside one analyst's day."*

---

## Slide 6 — A day in the analyst's life [70 s]

**What's on screen.** A diary-style timeline: 08:30 forty-two articles in the queue; 09:00 opens article 1; 09:20 record complete (1 of 42); 12:00 lunch (7 done); 17:00 end of day (15 of 42); tomorrow another 42. Bottom: the structural problem — the inbound rate exceeds the analyst rate.

**Why this slide exists.** Humanises the bottleneck. The panel is composed of professors and external examiners — they may not have first-hand experience of operational analyst work. This slide makes the abstraction visceral.

**What to say (verbatim):**

> *"Now let me walk you through what that bottleneck feels like on the inside. This is a synthesised day in the life of an early-warning analyst — composite of the workflow described to me during user acceptance testing."*

> *"Eight-thirty in the morning. The analyst opens the overnight RSS feed: forty-two new articles waiting. Nine o'clock, they open article one. Reading, identifying actors, identifying victims, finding the location, parsing the date phrasing, extracting casualty figures, cross-referencing the actor name against an internal armed-group list, and logging the event into a spreadsheet. Twenty minutes later, the first record is complete."*

> *"Lunchtime, twelve o'clock — seven articles done. End of day at five — fifteen of the forty-two complete. The other twenty-seven queue overnight. And tomorrow morning, the overnight feed brings another forty-two."*

> *"This is not a slow analyst. The structural problem is the inbound rate exceeds any sustainable analyst rate. During a crisis, the backlog grows to weeks. That backlog is the gap VioNER is designed to close."*

**If they probe:**
- **"Did you actually observe analysts?"** — *"During UAT, two early-warning analysts described their workflow in detail. The diary is composited from those interviews, not a single observation log."*
- **"What's the analyst's actual time per record? Could it be faster?"** — *"With practice it can drop to ten minutes for routine articles, but complex multi-event articles take longer. Fifteen-to-twenty-five is the working mean."*

**Pivot.**

> *"That is the problem in human terms. Now let's look at what the analyst's output is supposed to look like."*

---

## Slide 7 — The structured-record requirement [80 s]

**What's on screen.** A real article sentence on the left — *"On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least 12 soldiers."* On the right, the same content rendered as a 6-row 5W1H table: perpetrator = Al-Shabaab; victim = military convoy / soldiers; action = armed attack; date = Tuesday; location = near Mogadishu (Somalia); casualties = at least 12 killed. Bottom line: §1.3 decomposes this into three sub-problems — domain-specific NER, severe class imbalance, operational packaging.

**Why this slide exists.** Makes the abstract notion of "structured extraction" concrete. The panel sees exactly what input we read and exactly what output we have to produce. This slide also tees up the methodology slide that follows the research questions.

**What to say (verbatim):**

> *"To make this concrete, here is a single sentence drawn from a real news article."*

Read the sentence slowly.

> *"On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least twelve soldiers."*

> *"What an operational analyst needs is the structured record on the right. Six fields, one per 5W1H slot. The WHO is Al-Shabaab as the perpetrator, but also the soldiers as the victim. The WHAT is an armed attack. The WHEN is Tuesday. The WHERE is near Mogadishu, in Somalia. The HOW captures the casualty count with its qualifier — 'at least twelve killed', not just 'twelve killed', because the qualifier is operationally meaningful."*

> *"When we ran this exact sentence through off-the-shelf NER models — spaCy and HuggingFace's standard English NER head — Al-Shabaab came back as the generic ORGANIZATION class. Technically correct, operationally useless. The convoy and the soldiers were not tagged as victims at all, because standard NER schemas don't distinguish perpetrators from victims. That gap is what this thesis closes."*

> *"Section 1.3 of the thesis decomposes that single gap into three sub-problems: domain-specific NER — generic models don't know African armed groups; severe class imbalance — seventy-eight percent of tokens carry no entity label at all; and operational packaging — published models leave the user-facing layer undone. The rest of the talk addresses each of these in turn."*

**Quick term explanations.**
- *NER* — Named Entity Recognition; the NLP task of tagging spans of text with category labels like PERSON, LOCATION, DATE.
- *5W1H* — journalistic framing for who, what, when, where, why, how.
- *spaCy / HuggingFace* — open-source NLP libraries with pre-trained NER models.

**If they probe:**
- **"Why those six fields and not more?"** — *"Those are the six 5W1H slots an early-warning analyst needs. We dropped MOTIVE (the WHY) from the supervised schema because it's almost never present verbatim — that's covered on the entity-schema slide."*
- **"Is Al-Shabaab in spaCy's training data?"** — *"It appears in some pretraining corpora but isn't a labelled NER class. The off-the-shelf head returns ORG, which loses the operationally-relevant 'armed group' distinction."*

**Pivot.**

> *"Those three sub-problems frame the four research questions next."*

---

## Slide 8 — Section divider: Research Questions [10 s]

**What's on screen.** Divider — "2. Research Questions · The four questions this thesis answers".

**Why this slide exists.** Marks the transition from problem to scoped questions.

**What to say.**

> *"Four research questions structure the work."*

**Pivot.** Click forward.

---

## Slide 9 — Research questions [90 s]

**What's on screen.** Four numbered questions, in bold paragraph form: RQ1 schema choice; RQ2 model + loss; RQ3 KB value; RQ4 system architecture for non-ML users.

**Why this slide exists.** Locks down the scope. Everything later in the talk is evidence against one of these four. The panel uses this as the rubric to score the thesis.

**What to say (verbatim):**

> *"Four research questions, each tied to one of the sub-problems on the previous slide."*

> *"RQ1 is the schema question. Not all of the entities an analyst cares about can be reliably grounded in source text — some, like motive or intent, are usually inferred rather than written. So the first question is: which entity types CAN we reliably tag from text, and what BIO encoding scheme — that is, the standard way of marking the beginning, inside, and outside of an entity span — fits those choices."*

> *"RQ2 is the modelling question. Given the chosen schema, how well does a fine-tuned BERT model perform on this task? And crucially, under severe class imbalance, what loss function and sampling strategy produce balanced per-entity performance? By severe class imbalance, I mean that about seventy-eight percent of all tokens carry no entity label at all, while the operationally important entities — victims, casualties, action verbs — are in single digits each."*

> *"RQ3 is the knowledge-base question. A model alone, even a good one, can't tell you that 'Al-Shabaab in eastern DRC' is geographically implausible because Al-Shabaab operates in Somalia, not DRC. RQ3 asks how much a curated knowledge base of African armed groups, conflict locations, and a hierarchical taxonomy improves the trustworthiness and downstream utility of extracted records."*

> *"RQ4 is the systems question — the one that's often skipped in event-extraction papers. What system architecture lets the model, the KB, and the analytics layer be operated together by users who are not machine-learning specialists?"*

> *"Every results slide later in the talk will be marked with the RQ it answers, so you can track the evidence."*

**Quick term explanations.**
- *BERT* — Bidirectional Encoder Representations from Transformers; the 2018 Google language model used as the backbone here.
- *Fine-tuning* — taking a pre-trained model and training it further on task-specific data.
- *BIO encoding* — Begin / Inside / Outside; the standard way of representing entity spans token-by-token.
- *Loss function* — the mathematical objective the model minimises during training.

**If they probe:**
- **"Why only four RQs?"** — *"Each maps to one of the three sub-problems plus the systems contribution. Adding more would dilute the focus."*
- **"Why not include explainability or fairness?"** — *"Both are real concerns and surface in the threats-to-validity section; they were out of scope for a thesis focused on extraction methodology."*

**Pivot.**

> *"Before answering each, let me say one thing about how I went about it methodologically."*

---

## Slide 10 — Methodological frame: design science [95 s]

**What's on screen.** Two columns. Left: the Hevner/Peffers design-science cycle diagram — four nodes labelled Build, Evaluate, Learn, Refine, arrows in a closed loop. Right: a table of three iteration loops — Corpus (Oct→Nov 2025), Schema (Nov→Dec 2025), Loss (Jan→Feb 2026) — each with what changed and the empirical trigger.

**Why this slide exists.** This is the methodology defence. AAU panels probe methodology hard. Without this slide, you're vulnerable to "is this just engineering?" Showing the cycle plus three concrete iteration loops proves the work is design science, not a one-shot build.

**What to say (verbatim):**

> *"Before going into related work and the approach, one slide on methodology. The thesis is framed as design science in the Hevner-and-Peffers tradition — the citations are at the bottom of the slide."*

> *"What design science means in practice is the cycle on the left. You build an artefact — schema, model, KB, system. You evaluate it empirically — metrics, ablations, user testing. You learn from where it falls short. You refine and iterate. The contribution is the artefact, the lessons from each loop, and the final state — not a single experiment."*

> *"The reason this is design science rather than a controlled empirical study is the nature of the claim. A controlled study fits when the contribution is a falsifiable statement about a single technique — say, 'focal loss outperforms cross-entropy on token classification.' That's not the claim here. The claim is that an integrated artefact — schema plus model plus KB plus interface — measurably improves on hand-coding for African violent-event extraction. Design science is the established frame for that kind of contribution."*

> *"On the right are three iteration loops over five months. The corpus loop: the first training corpus was the full two-hundred-twelve-thousand-event ACLED extract. Rare-entity F1 actually dropped — because the heavy repetition of common phrasing drowned out the rare classes. That empirical signal triggered the redesign to stratified diversity sampling on a fifty-thousand-example subset."*

> *"The schema loop: the November grounding pilot showed EVENT_TYPE could be located verbatim in only fifty-eight percent of cases. That number killed the twenty-six-entity schema in the proposal and led to the eight-entity version you'll see in a few slides."*

> *"The loss loop: the focal-versus-cross-entropy ablation, which you'll see in the results, quantified the benefit at eleven F1 points on the VICTIM entity. Three loops, three empirical decisions. That's what makes this design science rather than just engineering."*

**Quick term explanations.**
- *Design science* — a research paradigm where the contribution is a designed artefact, evaluated empirically. Hevner 2004 and Peffers 2007 are the canonical references.
- *Ablation* — a controlled experiment that turns one ingredient on or off to measure its individual contribution.
- *F1* — a single number combining precision (correctness) and recall (completeness); the standard NER metric. Range 0–1, higher is better.

**If they probe:**
- **"Why design science rather than a case study or survey?"** — *"Case studies produce interpretation; surveys produce attitudes. Neither produces a reusable artefact, which is what this work delivers."* (Q38 in the Q&A kit goes deeper.)
- **"What if a loop had failed — would you have changed methodology?"** — *"Each loop's exit criterion was empirical. If the schema loop had not produced a higher per-entity F1 than the proposal schema, we would have kept iterating. The criterion was the criterion."*

**Pivot.**

> *"With the methodology grounded, let's see where this work sits in the existing literature."*

---

## Slide 11 — Section divider: Related Work [10 s]

**What's on screen.** Divider — "3. Related Work and the Gap · Where prior systems stop and this thesis starts".

**What to say.**

> *"Where prior systems stop, and where this work starts."*

**Pivot.** Click forward.

---

## Slide 12 — The related-work landscape [80 s]

**What's on screen.** A 2×2 matrix. Rows: classical NER, transformer NER, structured event databases, end-to-end deployed extraction. Columns: generic news domain vs conflict / African context. Stanford NER and spaCy sit top-left; ICEWS and GDELT sit middle; ACLED and UCDP bottom-right; the very bottom-right cell — academic deployed extraction in the African context — is conspicuously empty.

**Why this slide exists.** Positions the work at a glance. The empty cell is the gap; everything that follows is about filling it.

**What to say (verbatim):**

> *"This matrix positions the work. Two axes: across the top, generic news domain versus the conflict and African context. Down the side, the modelling family — from classical sequence labellers up through transformer NER, then structured event databases, then end-to-end deployed extraction systems."*

> *"Stanford NER and spaCy occupy the top-left cell — generic, well-known, not tuned for African content. The HuggingFace BERT NER models occupy the next row — strong on generic news, but weak on African armed-group names that didn't appear in their pretraining corpora."*

> *"ICEWS and GDELT are large structured event databases for general news. ACLED and UCDP are the African and conflict-domain analogues — but both are hand-coded. They produce gold-standard data but at the cost of exactly the analyst time we are trying to reduce."*

> *"The cell I want you to look at is the bottom-right one. End-to-end deployed extraction in the African context, in the academic literature, is essentially absent. Academic models get published; the operational layer — schema, KB, validation, UI, deployment — does not. That is the empty cell this thesis fills."*

**Quick term explanations.**
- *Stanford NER, spaCy* — classical and modern open-source NER tools.
- *ICEWS* — Integrated Crisis Early Warning System, a US government event database.
- *GDELT* — Global Database of Events, Language, and Tone.
- *ACLED, UCDP* — Armed Conflict Location & Event Data; Uppsala Conflict Data Program. Both hand-coded.

**If they probe:**
- **"Where would you put GDELT-Africa?"** — *"GDELT covers African events but with low precision and no fine-grained structured 5W1H — it sits in the middle row, generic column for that reason."*
- **"What about LLM-based extraction since 2024?"** — *"Recent work — GPT-4 and Claude prompt-engineering for event extraction — is not on the matrix because it post-dates this thesis. We treat it as a comparison baseline in future work, not as prior work this builds on."*

**Pivot.**

> *"Let me make the prior-work picture more concrete with named systems."*

---

## Slide 13 — What has been tried — and where each falls short [75 s]

**What's on screen.** A five-row table: ICEWS, GDELT, ACLED, prior African NER (Masakhane/AfriBERTa), generic BERT NER (spaCy, HuggingFace heads). Each row has what the system does and why it falls short for VioNER's specific use case. Italic punchline at the bottom: none combine Africa-tuned extraction with operational packaging.

**Why this slide exists.** The 2×2 on the previous slide is shape; this slide is detail. The panel asks "have you actually read the prior work?" and this slide demonstrates that you have, with named systems and concrete shortfalls.

**What to say (verbatim):**

> *"To make the prior-work picture concrete, let me walk through the five most relevant named systems."*

> *"ICEWS, developed by Lockheed Martin under DARPA funding, does automated event extraction from global news. Strong on geopolitical signal at scale, but the schema is generic, the pipeline is closed, and Africa-specific event types are not first-class. Falls short for our use case for those reasons."*

> *"GDELT does planetary-scale event tracking — but the extraction relies heavily on lexical sentiment patterns. Low precision, no structured 5W1H. Useful for trend analysis, not for record-level event coding."*

> *"ACLED is the gold standard for African conflict event data. The catch — and it's a fundamental catch — is that ACLED is hand-coded. The quality is excellent because human analysts read every article. That hand-coding is exactly the bottleneck this thesis is trying to reduce."*

> *"Prior African NER work — Masakhane's collaborative African-language datasets, AfriBERTa, AfroLM — has produced strong language coverage and token-level entity tagging. But it stops at the model. No knowledge-base layer, no operational packaging, no analyst-facing interface."*

> *"Generic BERT NER — the HuggingFace heads, spaCy's transformer models — is strong on English entities but doesn't know that Al-Shabaab is an armed group, doesn't know that Mogadishu is in Somalia, and doesn't produce 5W1H groupings."*

> *"The bottom line is the italic line — none combine Africa-tuned extraction with operational packaging. That combination is the wedge this thesis drives in."*

**Quick term explanations.**
- *Masakhane* — community NLP project building African-language NLP resources.
- *AfriBERTa, AfroLM* — pretrained transformer models for African languages.

**If they probe:**
- **"Why didn't you build on AfriBERTa?"** — *"AfriBERTa's pretraining corpus is dominated by African-language text; the English representations aren't necessarily stronger than bert-base-cased for the English-only task here. AfriBERTa becomes the natural backbone for the multilingual extension in future work."*
- **"What about Stanford CoreNLP?"** — *"Comparable to spaCy here — strong general-English NER, weak on domain-specific actors and locations. We baseline against it in backup B9."*

**Pivot.**

> *"With the prior work surveyed, here is the gap stated formally."*

---

## Slide 14 — The four-part gap this thesis closes [85 s]

**What's on screen.** Quote: "most African event-extraction work stops at the model boundary." Then a four-row table — each row is one gap: grounding-based schema, imbalance-aware training, curated KB layer, deployable platform. Each row has columns for "what it means concretely" and "how VioNER addresses it".

**Why this slide exists.** Four-part gap = four contributions later. This slide is the contract: panel will hold you to addressing each of the four somewhere in the rest of the talk.

**What to say (verbatim):**

> *"Most African event-extraction work stops at the model boundary. The schema, the imbalance handling, the knowledge base, and the deployable interface are treated as implementation footnotes rather than research outputs. This thesis treats them as the contribution."*

> *"Gap one: grounding-based schema. Most published NER schemas tag what annotators infer — motive, intent, sub-event type. Training on inference produces noisy labels because annotators inferred differently. This thesis tags only what is verbatim in the source text. The eight-entity schema is the result, and you'll see it in detail in a few slides."*

> *"Gap two: imbalance-aware training. Seventy-eight percent of all tokens carry no entity label. Plain cross-entropy treats those as equal to actual entity tokens, so the gradient signal for the rare entities — victims, casualties, action verbs — gets drowned out. This thesis uses focal loss combined with inverse-frequency class weights to recover the rare-class signal."*

> *"Gap three: curated KB layer. Even a perfect NER model can't tell you that an Al-Shabaab attack in eastern DRC is geographically implausible. Models don't carry world knowledge; they only see text. This thesis pairs the model with a curated knowledge base of a hundred-and-fifty armed groups and two-hundred conflict cities, used both to validate suspicious extractions and to enrich them with canonical identifiers."*

> *"Gap four: deployable platform. Most academic event-extraction work ships a checkpoint — a model file — and stops. This thesis ships a FastAPI service, a React-and-TypeScript front-end, and a PostgreSQL store, all of which a non-ML-user can operate end-to-end. That is what makes this work usable rather than just publishable."*

> *"Each of the four gets its own approach slide later in the talk."*

**Quick term explanations.**
- *Cross-entropy* — the standard classification loss; penalises wrong predictions in proportion to model confidence.
- *Focal loss* — a 2017 modification of cross-entropy that down-weights easy correct predictions, focusing capacity on hard cases.
- *Inverse-frequency class weights* — multipliers in the loss that compensate for rare classes by giving them larger gradients.
- *FastAPI / React / PostgreSQL* — Python web framework / JavaScript UI framework / relational database. Mainstream stack.

**If they probe:**
- **"Is the gap really four-part, or is it really just one gap?"** — *"They're separable. A team could address any one and not the others. The contribution claim is that addressing all four together is what produces a usable system."*
- **"Which of the four is the most novel?"** — *"The combination is the novelty; in isolation, gap two (focal-loss-plus-weights) has the most directly comparable prior work and shows the largest measurable effect (eleven F1 points on VICTIM)."*

**Pivot.**

> *"Each of those four gaps gets its own treatment in the approach section, which we move into now."*

---

## Slide 15 — Section divider: Approach [10 s]

**What's on screen.** Divider — "4. Approach · Schema · Taxonomy · BIO · Model · Knowledge Base".

**What to say.**

> *"How the four gaps are addressed in design."*

**Pivot.** Click forward.

---

## Slide 16 — Entity schema: eight grounded entity types [100 s]

**What's on screen.** Table with two columns — entities retained vs entities dropped — grouped by 5W1H category. Bottom: "8 entities → 17 BIO labels. Every entity type reliably supervisable."

**Why this slide exists.** RQ1 answer. The panel will ask why eight, not twenty-six; this slide answers visually.

**What to say (verbatim):**

> *"RQ1 — the schema. The original proposal called for twenty-six entity types, covering everything an analyst might care about — motive, intent, organisation, duration, frequency, geographic descriptors, weapons, and so on."*

> *"In November 2025, before committing the training compute, I ran what I called a grounding pilot. A sample of articles was annotated by hand, and for each entity type, I measured the fraction that could be located verbatim in the source text — that is, the analyst could point at a specific phrase as the gold annotation."*

> *"Types whose grounding rate fell below eighty percent were dropped from the supervised schema. The reasoning: training a model on labels that annotators inferred rather than read would introduce systematic noise, because two annotators would infer differently for the same article. MOTIVE was the worst offender — the motive of an attack is almost never written in the article; analysts infer it from prior knowledge of the actor."*

> *"What remained were eight entities, in the left column: ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES. In BIO encoding — which marks the beginning, inside, and outside of each entity — that's seventeen labels: two for each of the eight entities, plus the outside-of-any-entity O label."*

> *"The dropped types in the right column are not lost; they're recovered downstream. EVENT_TYPE is reconstructed by the taxonomy classifier from the action verb plus context. COUNTRY is recovered by a knowledge-base lookup from the most specific WHERE entity. So we get eight clean training signals plus two free downstream entities. That trade was the single most consequential methodological choice of the thesis."*

**If they probe:**
- **"Isn't dropping eighteen entities a weakening of the contribution?"** — *"It's a strengthening — every retained label has verifiable ground truth, which makes the trained model trustworthy. Q1 in the kit elaborates."*
- **"How did you decide the eighty-percent threshold?"** — *"It was the elbow of the grounding-rate distribution — types clustered above eighty percent or below sixty percent, with little in between. Q15 elaborates."*
- **"What if the panel disagrees with the threshold?"** — *"The methodology is unchanged; only the retained set shifts. The threshold is reported as a design parameter, not a discovered constant."*

**Pivot.**

> *"With the entity schema settled, the four-level taxonomy gives us the structured event categories on top."*

---

## Slide 17 — Four-level hierarchical taxonomy [80 s]

**What's on screen.** The taxonomy figure: root, four Level-1 families (Political, Criminal, Communal, State), Level-2 subcategories shown. Caption noting ~95 leaves at Level 3.

**Why this slide exists.** RQ3 first ingredient. Shows the structured-event categories that downstream classification assigns to.

**What to say (verbatim):**

> *"This is the four-level hierarchical taxonomy. The root at the left is the abstract Violent Events category. Level one — the four coloured families — divides events into Political Violence, Criminal Violence, Communal Violence, and State Violence against Civilians. Level two breaks each family into operational subcategories: under Political Violence you get terrorism, election violence, coup-and-regime change; under Criminal Violence you get armed robbery, kidnapping for ransom; and so on."*

> *"At Level three — not shown here for space reasons but in Annex B and backup slide B5 — there are roughly ninety-five terminal leaf categories. Bombing. Ambush. Cattle raiding. Soft-target attack."*

> *"The taxonomy synthesises ACLED, UCDP, and the PMVE — the Political Violence and Mass Violence Events ontology — but it adds two African-specific extensions that none of those frameworks cover at this depth: pastoralist-farmer clashes, and communal cattle raiding. Both account for a measurable fraction of Sahel and Horn-of-Africa reporting and don't sit cleanly in ACLED's 'Violence against civilians' bucket."*

**Quick term explanations.**
- *Taxonomy* — a hierarchical classification system; here, a tree of event categories.
- *PMVE* — Political Violence and Mass Violence Events ontology, an academic event-typing framework.

**If they probe:**
- **"Why hierarchical rather than flat?"** — *"Operational consumers ask questions at different granularities. A flat hundred-category schema is hard to query; a hierarchy lets you roll up or drill down."*
- **"Who designed the categories?"** — *"Synthesised from ACLED + UCDP + PMVE with two African-specific extensions; reviewed by two domain experts during the pilot."*

**Pivot.**

> *"To train a model on this schema, we need to mark every token in every sentence with the right label. That's BIO encoding."*

---

## Slide 18 — BIO encoding: why this scheme [70 s]

**What's on screen.** An annotated example showing "Al-Shabaab fighters attacked a convoy" with tokens and their BIO labels. Below: a one-line justification of BIO over BIOES.

**Why this slide exists.** Closes the schema loop and addresses advisor comment C444. Also signals to the panel that we've thought about the label-encoding choice.

**What to say (verbatim):**

> *"How are the labels actually applied to tokens? With BIO encoding."*

> *"B for the first token of an entity, I for continuation tokens within the same entity, and O for everything outside any entity. The code block on the screen shows the worked example."*

> *"Al-Shabaab fighters becomes B-ACTOR followed by three I-ACTORs — including the hyphen subword, which is a real token in the BERT tokeniser. Attacked is the B-ACTION. The word 'a' is outside any entity, so it's O. Convoy is B-VICTIM."*

> *"We chose BIO over BIOES — which adds explicit End and Single tags — because the African news corpus almost never has adjacent same-type entities with no intervening token between them. BIOES would double the label space from seventeen to thirty-three without buying anything for ninety-five percent of cases — and a larger label space worsens the class-imbalance problem we already have to deal with."*

**Quick term explanations.**
- *Tokeniser* — splits raw text into sub-word units for the model. BERT uses WordPiece tokenisation.
- *BIOES* — Begin / Inside / Outside / End / Single; a more expressive but less commonly-used encoding.

**If they probe:**
- **"What if entities are nested?"** — *"Nested entities are out of scope; the eight chosen entities don't nest in our data."*
- **"Why not use a span-level head instead of BIO?"** — *"A span-level CRF or biaffine head is in future work — listed as item 4 in high-priority future work. BIO is the standard, well-understood baseline."*

**Pivot.**

> *"Now we move to the system that consumes these labels and produces the structured output."*

---

## Slide 19 — System architecture [70 s]

**What's on screen.** The architecture figure: four layers — React/TypeScript frontend (Presentation), FastAPI service (Service), NER component and KB (in-process), PostgreSQL (Persistence).

**Why this slide exists.** RQ4 answer. The panel needs to see the architecture before the per-component details make sense.

**What to say (verbatim):**

> *"RQ4 — the architecture. Four layers, deliberately conservative."*

> *"At the top, the presentation layer — a React and TypeScript single-page application. React is Facebook's UI framework; TypeScript adds static type checking to JavaScript. This is what the analyst actually sees in the browser: pages for training, inference, event browsing, analytics, and KB administration."*

> *"In the middle, the service layer — a FastAPI service. FastAPI is a modern Python web framework. Seven route groups: training management, inference, event storage, analytics, KB administration, authentication, and system health. The model and KB are loaded once into the FastAPI process so per-request inference is in-memory and fast — about a hundred-and-fifty milliseconds per article on CPU."*

> *"Below that, the NER component and the knowledge base sit in-process — they're not separate services. That choice keeps latency low and operational complexity down."*

> *"At the bottom, PostgreSQL — version sixteen. PostgreSQL is the open-source relational database. It holds events, training runs, and user accounts."*

> *"The whole stack is orchestrated by Docker Compose, which is a containerisation tool that lets a domain analyst run one command to start the entire system locally. That's what makes it operable by non-ML users."*

**Quick term explanations.**
- *React* — Facebook's JavaScript UI framework.
- *TypeScript* — Microsoft's strongly-typed superset of JavaScript.
- *FastAPI* — Python async web framework with built-in OpenAPI documentation.
- *Docker Compose* — multi-container orchestration tool; turns "install seventeen things" into "run one command".

**If they probe:**
- **"Why React rather than Vue or Angular?"** — *"React has the largest community and the strongest TypeScript ecosystem in 2026, so it's the lowest-risk choice for a thesis system that needs to remain maintainable."*
- **"Why a monolith rather than microservices?"** — *"At this scale a single FastAPI worker holding the model in memory is faster and simpler than a service mesh. Microservices would be appropriate at much higher load."*

**Pivot.**

> *"Here's what happens inside that architecture, one article at a time."*

---

## Slide 20 — End-to-end processing pipeline [90 s]

**What's on screen.** Ten-step vertical flow: article submission → tokenise → BERT forward → BIO decode → confidence filter → 5W1H group → KB validate → taxonomy classify → persist → render.

**Why this slide exists.** Shows the panel the per-document story without burying them in code.

**What to say (verbatim):**

> *"This is what happens when an analyst pastes one article into the inference page."*

> *"Step one: the article text hits the FastAPI inference route. Step two: WordPiece tokenisation — BERT's sub-word tokeniser — splits the text into the units BERT expects. A word like 'Al-Shabaab' becomes about four sub-word tokens."*

> *"Step three: forward pass through the fine-tuned BERT model. The output is, for each token, a probability distribution over the seventeen labels. Step four: a BIO decoder collapses contiguous B-I sequences into spans — so 'B-ACTOR I-ACTOR I-ACTOR I-ACTOR' becomes a single ACTOR span."*

> *"Step five: confidence filtering. For each span, we average the per-token confidence; spans below a per-category threshold get dropped. This is how we trade precision for recall."*

> *"Step six: 5W1H grouping. The surviving spans get bucketised into the six output categories — WHO, WHAT, WHEN, WHERE, HOW, WHY."*

> *"Step seven: KB validation. Each ACTOR and CITY is looked up in the knowledge base. Mismatches — like 'Al-Shabaab in eastern DRC' — get flagged with a geographic-implausibility tag."*

> *"Step eight: the taxonomy classifier assigns a Level-1 to Level-3 path from the ACTION verb and the actor context. So 'attack' plus 'Al-Shabaab' resolves to Political Violence → Terrorism → Armed Assault."*

> *"Step nine: the structured record is persisted to PostgreSQL. Step ten: the React UI renders it for the analyst, with colour-coded chips per category."*

> *"End-to-end on a single CPU core, this takes about a hundred-and-fifty milliseconds per typical article."*

**Quick term explanations.**
- *WordPiece* — BERT's specific sub-word tokenisation algorithm.
- *Forward pass* — one inference run through the model.
- *Softmax distribution* — a probability distribution that sums to 1, output of the model's final layer.

**If they probe:**
- **"What if step seven (KB) flags something? Does extraction stop?"** — *"No — the flag is metadata. The record still gets persisted but with a flag visible in the UI prompting analyst re-read."*
- **"Why 150 ms? What's the bottleneck?"** — *"BERT forward pass at about 75 % of latency. Q10 elaborates."*

**Pivot.**

> *"The heart of this pipeline is the BERT model and how it's trained — let me cover the training recipe next."*

---

## Slide 21 — Training recipe: focal loss + class weights [100 s]

**What's on screen.** Backbone choice, focal-loss equation, justification text.

**Why this slide exists.** RQ2 headline. This is the modelling contribution.

**What to say (verbatim):**

> *"RQ2 — the modelling core. The backbone is bert-base-cased. BERT — Bidirectional Encoder Representations from Transformers — is Google's 2018 language model; bert-base-cased is the cased English version, a hundred-and-ten million parameters. We fine-tune it end-to-end with a seventeen-label token-classification head — meaning a new layer on top that maps BERT's internal representations to our seventeen BIO labels."*

> *"The loss function is the key design choice. The equation on the screen is focal loss with inverse-frequency class weights. Let me explain it piece by piece."*

> *"The inner sum is over classes c. For each class, we have the model's predicted probability y-hat-c — how confident is the model that this token belongs to class c. The (one minus y-hat) raised to gamma is the focal-loss modulator. When the model is confident and correct — y-hat near one — that modulator goes to zero, so the loss contribution is tiny. When the model is uncertain or wrong, the modulator is large. The effect is that focal loss focuses learning on the hard cases."*

> *"The w-c term is the inverse-frequency class weight. Rare classes — VICTIM, CASUALTIES — get a larger weight; common classes — O, DATE — get a smaller weight. So we don't double-count the easy O predictions."*

> *"Why both ingredients? Class weights raise the gradient for rare classes; focal loss suppresses easy-negative gradients. They attack different aspects of the imbalance problem. Section 6.6 of the thesis — and the ablation slide later in this talk — shows empirically that the two together produce larger gains than either alone. That's the answer to the second half of RQ2."*

**Quick term explanations.**
- *Gradient* — the direction the model parameters move during training; rare classes need stronger gradients to be learned.
- *Focal loss* — Lin et al. 2017; originally proposed for dense object detection.
- *Inverse-frequency weighting* — class weights proportional to one divided by class frequency.

**If they probe:**
- **"What value of gamma did you use?"** — *"Two-point-zero, the literature default. Backup B1 has the full hyperparameter table."*
- **"Did you try label smoothing?"** — *"Yes, with beta 0.1 — slightly worsened validation loss but had small regularising effect, so it was kept in production. Section 6.4 of the thesis discusses this."*

**Pivot.**

> *"The model handles the per-token tagging. The knowledge base is what we use to sanity-check and enrich the result."*

---

## Slide 22 — Knowledge base as validation + enrichment [100 s]

**What's on screen.** KB content summary (150 groups, 200 cities, 54 countries, weapons), two-row table showing the two roles (validate, enrich) with their mechanisms and effect rates.

**Why this slide exists.** RQ3 answer. The KB is what most published work skips; this slide shows the panel that we didn't.

**What to say (verbatim):**

> *"RQ3 — the knowledge base. We curated roughly a hundred-and-fifty African armed groups with their canonical names, aliases, country of operation, region of operation, and group type — jihadist, ethno-political, criminal, and so on. Two hundred conflict-affected cities mapped to country and region. All fifty-four African countries. A weapons catalogue with thirty-eight entries."*

> *"The KB plays two roles in the inference pipeline."*

> *"First role — validation. When the model extracts 'Al-Shabaab fighters' and 'Goma' in the same sentence, the KB knows Al-Shabaab operates in Somalia, not eastern DRC. The validator flags that event as geographically implausible. The flag rate over the validation set is two-point-four percent — small in aggregate, but those are exactly the events an analyst should re-read before trusting."*

> *"Second role — enrichment. 'Al Shabaab', 'al-shabaab', 'Al-Shabaab militants', 'al-Shabaab fighters' — all four surface forms canonicalise to a single KB entry, with the canonical name 'Al-Shabaab', country code SOM, and group type 'jihadist'. Sixty-four-point-three percent of extracted ACTOR mentions get enriched this way. That canonicalisation is what lets the analytics dashboard later in the talk count by actor correctly — otherwise the same group would be counted four times under four different surface forms."*

**Quick term explanations.**
- *Knowledge base* — here, a structured collection of curated facts. Not a deep ontology, just lookup tables.
- *Canonical form* — the single agreed-upon name for an entity; aliases all map to it.
- *Country code* — ISO 3166-1 three-letter code (SOM = Somalia, ETH = Ethiopia).

**If they probe:**
- **"Where did the KB content come from?"** — *"ACLED's actor list curated down to active groups, plus manual review by domain experts. Backup B8 has the composition."*
- **"How do you keep the KB current?"** — *"That's recommendation 2 in §7.4 — needs a part-time domain expert. Stale KBs do more harm than no KB."*

**Pivot.**

> *"The model and the KB both need training data. Let's talk about where that came from."*

---

## Slide 23 — Dataset and annotation protocol [85 s]

**What's on screen.** Source breakdown (35k ACLED, 15k augmentation), split scheme, class imbalance summary.

**Why this slide exists.** Sets up the data-quality slide that follows. Panel needs the basic counts and source story.

**What to say (verbatim):**

> *"Where the training data came from. The fine-tuning corpus has fifty thousand examples. Thirty-five thousand of them are real ACLED open-data records, but filtered by stratified diversity sampling — not random sampling — because the full two-hundred-twelve-thousand-event extract had so much repetition of common phrasings that the rare entities got drowned out. That was the empirical trigger for the corpus iteration loop on the methodology slide."*

> *"The remaining fifteen thousand examples are template-based augmentation — synthetic sentences generated from templates, specifically targeting the rare classes — VICTIM, ACTION, CASUALTIES — to lift them off the floor."*

> *"Splits are eighty-twenty train and validation, stratified on entity-type presence so both halves see all eight entity types."*

> *"Class imbalance is the central modelling challenge: seventy-eight percent O versus twenty-two percent entity tokens. Within entities, ACTOR, CITY, and DATE dominate; VICTIM, ACTION, and CASUALTIES are in the single digits each. That's why focal loss matters."*

**Quick term explanations.**
- *Stratified sampling* — sampling with category proportions preserved or rebalanced; here, biased toward rare-entity coverage.
- *Template-based augmentation* — synthetic data generated from filled-in template sentences. Lower fidelity than real data but cheap and rare-class-balanced.

**If they probe:**
- **"Why ACLED rather than scraping news directly?"** — *"ACLED records come pre-paired with structured fields that we can project onto the free text as gold labels. Scraping raw news would require us to annotate from scratch."*

**Pivot.**

> *"The natural question now is whether fifty thousand is enough and whether the labels are clean enough. The next slide answers both."*

---

## Slide 24 — Data: enough, and good enough [95 s]

**What's on screen.** Two-column layout. Left column — volume defence: comparison to CoNLL-2003 (22k), MIT Movie NER (12k), OntoNotes (1.6M tokens), sample-size plateau note. Right column — quality defence: Cohen's κ = 0.78, six pilot rounds (0.40 → 0.22 disagreement), 10% spot-check 3.2 % errors corrected to ~1 %. Below: held-out integrity bullets.

**Why this slide exists.** Theme 3 from past students' intel — experimentation rigor. Defends both volume and quality. Without this slide, the panel will ask both questions independently.

**What to say (verbatim):**

> *"Two columns. Volume on the left, quality on the right."*

> *"Volume defence first. Fifty thousand fine-tuning examples is more than two times the size of CoNLL-2003, which is the canonical English NER benchmark. It's four times the size of MIT Movie NER, which is a similar narrow-domain NER task. It's smaller than OntoNotes 5.0, which has one-point-six million tokens — but OntoNotes is general-domain at a different scale and a different purpose."*

> *"More importantly, section 5.2 of the thesis reports a sample-size sensitivity analysis. I retrained at ten, twenty, thirty-five, and fifty thousand examples. Macro F1 plateaus around thirty-five thousand. Past that, additional data gives diminishing returns. Fifty thousand sits comfortably on the right side of that plateau."*

> *"Quality defence on the right. Cohen's kappa — the standard inter-annotator agreement metric, ranging from minus-one to plus-one — comes out at zero-point-seven-eight on a two-hundred-document pilot. On the Landis-Koch interpretation scale, that's substantial agreement. Six pilot rounds were needed to reach it. Disagreement fell from forty percent to twenty-two percent across those rounds. The annotation guidelines themselves grew from nine pages to thirty-one pages, mostly because edge cases kept surfacing that needed explicit rules."*

> *"A ten-percent stratified spot-check of the final corpus found three-point-two percent label errors; those were corrected; residual error after correction is estimated at about one percent by re-spot-checking."*

> *"Bottom of the slide — held-out integrity. The eighty-twenty split is at the article level, not at the sentence level, so no article appears in both halves. Articles are hashed and deduplicated before the split. The augmentation template pools are also partitioned: training templates and validation templates do not overlap. The panel asks 'could information leak between train and validation', and the answer is no, by construction."*

**Quick term explanations.**
- *Cohen's κ* — kappa; measures annotator agreement corrected for chance. >0.6 substantial, >0.8 almost perfect.
- *Stratified spot-check* — re-checking a sample drawn to preserve the rare-class proportions.
- *Held-out* — never seen during training.

**If they probe:**
- **"Why not higher κ?"** — *"At κ = 0.78 we hit the natural floor of language ambiguity. Reading down further would require constraining annotators to mechanical rules at the cost of edge-case quality."*
- **"What if validation leaked via duplicate sentences inside different articles?"** — *"Cross-article sentence overlap is below 0.4 % in the corpus; we measured it. That's the residual leakage risk reported in §6.13."*

**Pivot.**

> *"Finally, the training hyperparameters that take us from the recipe to the trained model."*

---

## Slide 25 — Training configuration [75 s]

**What's on screen.** Hyperparameter table — backbone, batch size, learning rate, warmup, scheduler, focal gamma, class weights, max epochs, early stopping. Each row tagged with where the value came from.

**Why this slide exists.** Addresses advisor comment C472 — "how do you set values for the parameters". Shows the panel that nothing here is magic.

**What to say (verbatim):**

> *"The hyperparameter table. Each value's source is in the right column."*

> *"The backbone, the focal-loss gamma, and the learning rate are inherited from the BERT-NER literature — these are well-established defaults. Batch size and max sequence length are architecture-driven, bounded by memory on the training hardware. The warmup ratio, the class-weight scheme, and the early-stopping configuration came out of empirical grid search."*

> *"The headline observation: the best validation checkpoint converges in just two epochs. Short training runs made it cheap to iterate during development. Backup slide B1 has the fully detailed table; backup B2 has per-epoch loss and accuracy."*

**Quick term explanations.**
- *Epoch* — one full pass through the training data.
- *Warmup ratio* — fraction of total steps during which learning rate linearly increases from zero.
- *Early stopping* — automatic training termination when validation metric stops improving.

**If they probe:**
- **"Why batch size sixteen?"** — *"Memory constraint on the M2 Max training box. Larger batches required more VRAM than available."*
- **"Why not warm-restart the learning rate?"** — *"With only two epochs to converge, warm restart wouldn't have had time to fire. ReduceLROnPlateau is a more natural fit for short training."*

**Pivot.**

> *"With approach and data complete, let's move to the results."*

---

## Slide 26 — Section divider: Results [10 s]

**What's on screen.** Divider — "5. Results · Evidence for each research question".

**What to say.**

> *"Results. Each slide tagged with the RQ it answers."*

**Pivot.** Click forward.

---

## Slide 27 — Overall performance [30 s]

**What's on screen.** Hero-stat slide: one big number — 0.909 micro F1 — with a single caption line.

**Why this slide exists.** Headline number, presented with weight. Don't rush past it.

**What to say (verbatim):**

> *"The headline number. Zero-point-nine-zero-nine micro F1, on the held-out validation set, across one-hundred-ninety-thousand gold spans. Macro F1 of zero-point-eight-eight-seven. Token accuracy of ninety-six-point-seven percent — informative but secondary because the O class dominates."*

> *"Per-category detail on the next slide."*

**If they probe (rare on stat slide):**
- **"Is this exact-match or relaxed?"** — *"Exact-match span — the strict CoNLL-2003 convention. Relaxed match would be 1.5 to 2 points higher."*

**Pivot.** Click forward.

---

## Slide 28 — Per-entity F1 [100 s]

**What's on screen.** Eight-row table: support, precision, recall, F1 per entity, plus macro average.

**Why this slide exists.** The panel reads results tables top-to-bottom. This is where they decide whether the model works.

**What to say (verbatim):**

> *"Walk top to bottom. DATE wins by a clear margin at zero-point-nine-five-six F1. Date expressions in conflict reporting follow a small set of recognisable patterns — 'on Monday', 'January fifteenth', 'earlier this week'. CITY at zero-point-nine-three-four and ACTOR at zero-point-nine-two-three round out the strong cluster of three high-volume entities with distinctive surface forms."*

> *"Middle tier — REGION at zero-point-eight-nine-one, CASUALTIES at zero-point-eight-eight-five, ACTION at zero-point-eight-six-six. The dip here correlates more with the entity's compositional irregularity than with sheer training volume. REGION names that double as cities; CASUALTIES that mix numerals and words; ACTION verbs that appear in passive voice as well as active."*

> *"Bottom of the table is the honest story. DISTRICT at zero-point-eight-two-six loses most of its accuracy to confusion with CITY and REGION — you'll see the confusion matrix in two slides. VICTIM at zero-point-eight-one-seven is both the rarest entity in the corpus AND the one with the most variable phrasing — from a single word like 'civilians' to a long noun phrase like 'ten villagers including women and children'."*

> *"Macro F1 of zero-point-eight-eight-seven means every entity, including the rarest, is recognised well enough to be useful operationally. The micro F1 of zero-point-nine-zero-nine — weighted by frequency — is the right number when estimating overall throughput; the macro number is the right one for assessing balance."*

**Quick term explanations.**
- *Support* — number of gold spans for that entity in the validation set.
- *Precision* — of all my predictions, what fraction were correct.
- *Recall* — of all the gold spans, what fraction did I recover.
- *F1* — harmonic mean of precision and recall.
- *Micro / Macro F1* — micro weights by support, macro averages across classes equally.

**If they probe:**
- **"Why is VICTIM the worst?"** — *"Combination of low support (5,492 spans) and high phrasing variability. Augmentation moved it up eleven F1 points; the rest is structural noise."*

**Pivot.**

> *"The big question for RQ2 is whether the focal-loss recipe earned its keep. Here's the ablation."*

---

## Slide 29 — Ablation: focal loss + class weights vs alternatives [90 s]

**What's on screen.** Five-row table: rare entities + macro across four loss configurations (plain CE, weighted CE, focal alone, focal+weights). Highlighted deltas: +0.072 for ACTION, +0.109 for VICTIM.

**Why this slide exists.** The RQ2 evidence. Without this slide, the loss-function claim is hand-waving.

**What to say (verbatim):**

> *"This is the ablation that answers RQ2 directly. Four loss configurations, identical in every other respect — same data, same scheduler, same early-stopping, same random seeds, only the loss function changes."*

> *"Read the rare-entity rows. VICTIM moves from zero-point-seven-zero-eight under plain cross-entropy to zero-point-eight-one-seven under focal-plus-weights. That's a gain of ten-point-nine F1 points. ACTION gains seven-point-two."*

> *"Each ingredient on its own helps a little. Weighted cross-entropy alone lifts VICTIM by about seven points; focal loss alone by about eight; the combination lifts it by eleven. That's not arithmetic — the two together exceed the sum of their parts. That complementarity is the empirical answer to RQ2's second half."*

> *"Crucially — and this matters operationally — no entity is hurt by this loss choice. We do not pay for VICTIM's gain in ACTOR or DATE accuracy. A loss that traded common-class accuracy for rare-class accuracy would have been an operational regression."*

**If they probe:**
- **"Statistical significance?"** — *"Paired bootstrap at the article level, p < 0.01 for VICTIM and ACTION gains."* (Q22 elaborates.)
- **"What about γ = 1 or γ = 3?"** — *"Tried both. γ = 1 gives smaller gains; γ = 3 gives marginally larger but instability in early epochs. γ = 2 is the literature default and was the operationally-stable choice."*

**Pivot.**

> *"To understand where the model still falls short, let's look at the location-confusion matrix."*

---

## Slide 30 — Location confusion patterns (Table 6.11) [90 s]

**What's on screen.** 3×3 confusion matrix: gold rows × predicted columns, diagonal omitted. DISTRICT row shows 7 % CITY and 9 % REGION confusion.

**Why this slide exists.** Honest error analysis. Disarms the "what does it get wrong" probe.

**What to say (verbatim):**

> *"Where does the model fall short? Error analysis ran over three hundred validation events with at least one mistake. The single biggest error category — thirty-eight percent — is boundary mismatch: the model gets the entity type right but the span slightly wrong, usually clipping a qualifier."*

> *"Second biggest is location-type confusion, shown in this matrix. Rows are gold labels, columns are predictions, diagonal is omitted because it would just show correct predictions. DISTRICT is the hardest — eight percent confused with CITY, nine percent with REGION."*

> *"The hard cases involve places that are simultaneously a city, a district capital, and the de-facto centre of a region. Goma in eastern DRC is the canonical example: city, district capital, and effectively the centre of North Kivu province. 'Fighting in Goma' can be labelled any of the three without more context. The model defaults to CITY for ambiguous cases — more often right than wrong, but it produces a consistent stream of confusions."*

> *"The fix is in high-priority future work — a span-level CRF on top of the BERT representations to refine boundaries and resolve the city-versus-district ambiguity using sequence-level constraints."*

**Quick term explanations.**
- *CRF* — Conditional Random Field; a sequence model that adds explicit label-to-label transition constraints on top of per-token predictions.

**If they probe:**
- **"Why not fix this now?"** — *"A CRF on top of BERT is a non-trivial training-time change; doing it well requires a separate paper's worth of evaluation."*

**Pivot.**

> *"Now we leave the model and look at the system users actually interact with."*

---

## Slide 31 — Section divider: System in Use [10 s]

**What's on screen.** Divider — "6. System in Use · The platform users actually interact with".

**What to say.**

> *"What the analyst actually touches."*

**Pivot.** Click forward.

---

## Slide 32 — Inference and event-browsing screens [80 s]

**What's on screen.** Two screenshots side by side: D.1 inference screen (paste article → 5W1H entity chips), D.5 event browser (filter, sort, paginate).

**Why this slide exists.** Concrete UI evidence. Without screenshots, the platform claim is abstract.

**What to say (verbatim):**

> *"Two screens, side by side."*

> *"On the left, the inference screen. The analyst pastes an article into the left pane and gets colour-coded entity chips on the right, grouped by 5W1H category. Confidence shown per chip. KB-enriched actors show their canonical name and country flag. KB-flagged events are highlighted in amber so the analyst notices the geographic implausibility before trusting the record."*

> *"On the right, the event browser. Once events are persisted, the analyst filters by date range, country, taxonomy bucket, and perpetrator. Sortable columns, pagination, CSV export. These are the two screens the analyst spends most of their time in. Both scored four-point-six on the 5W1H-clarity Likert item in user-acceptance testing."*

**If they probe:**
- **"Did real analysts use it?"** — *"Yes — two early-warning analysts in UAT, plus three other participants. The numbers are on the UAT slide in a moment."*

**Pivot.**

> *"And here are the other two surfaces — training and analytics."*

---

## Slide 33 — Training and analytics screens [90 s]

**What's on screen.** Two screenshots: D.4 live training (loss chart + per-epoch log), D.7 analytics (KPI cards + temporal charts).

**What to say (verbatim):**

> *"Training screen on the left. A non-ML user picks the dataset, the loss function, and the hyperparameters from drop-downs. They kick off a run and watch the loss curve update live over a WebSocket connection — meaning the server pushes updates to the browser without polling. The training service runs the job asynchronously; the user can navigate away and come back."*

> *"Analytics dashboard on the right. Aggregated views over the event store: events per country, per taxonomy bucket, per actor, per month. KPI cards at the top, temporal trend charts below. This is the screen that turns the extracted records back into operational insight."*

> *"The most common UAT request was an exportable PDF brief from the analytics screen, which is now in future work."*

**Quick term explanations.**
- *WebSocket* — a two-way persistent connection between browser and server; lets the server push updates without the browser asking.
- *KPI card* — Key Performance Indicator card; a UI tile showing a single headline number.

**If they probe:**
- **"How long does training actually take?"** — *"About forty minutes on the M2 Max for the two-epoch best-checkpoint training. Backup B2 has per-epoch timings."*

**Pivot.**

> *"Five participants drove all four of those screens end to end during user-acceptance testing. Here's what they reported."*

---

## Slide 34 — User acceptance test [100 s]

**What's on screen.** Six-row Likert table (1–5 scale), bottom: all 5 participants completed all 6 tasks, with breakdown of participant types.

**Why this slide exists.** RQ4 evidence. The systems claim is empirical.

**What to say (verbatim):**

> *"Five participants. Two early-warning analysts — the primary intended audience. One academic conflict researcher — secondary audience. Two NLP developers unfamiliar with the application domain, included as a fairness sanity check: would someone with technical literacy but no conflict-domain knowledge find the interface intuitive?"*

> *"All five completed all six tasks: run inference on three supplied articles, browse the event store, run an analytics query, train a model on a supplied dataset, monitor training to completion, and review a flagged event."*

> *"All six Likert items clear four-point-zero on a five-point scale. The two highest items — 5W1H structuring clarity at four-point-six, and KB enrichment value at four-point-six — are exactly the two things this thesis claims as differentiating contributions. The lowest is training-screen ease at four-point-zero; constructive feedback there fed directly into future work."*

**Quick term explanations.**
- *Likert scale* — survey response on a 1–5 (or 1–7) scale from strongly disagree to strongly agree.
- *UAT* — User Acceptance Testing; pre-deployment validation by intended users.

**If they probe:**
- **"Is n = 5 enough?"** — *"For inferential statistics, no. For qualitative validation of usability, five is consistent with Nielsen's industry rule of thumb. Q31 elaborates."*
- **"Were participants paid?"** — *"No — all five were colleagues or research peers who volunteered."*

**Pivot.**

> *"Closing — what this thesis leaves behind."*

---

## Slide 35 — Section divider: Contributions [10 s]

**What's on screen.** Divider — "7. Contributions, Limitations, Future Work".

**What to say.**

> *"Contributions, then limitations, then future work."*

**Pivot.** Click forward.

---

## Slide 36 — Contributions [100 s]

**What's on screen.** Five numbered contribution items: schema, taxonomy, training recipe, KB, system.

**Why this slide exists.** This is the slide that gets quoted in the panel's decision.

**What to say (verbatim):**

> *"Five concrete artefacts."*

> *"One — an eight-entity BIO schema with grounding-based inclusion rules. Every label is verifiably present in source text. Documented in Annex A. Reusable by any researcher working on African violent-event extraction."*

> *"Two — a four-level taxonomy of African violent events, around ninety-five terminal categories, including African-specific extensions for pastoralist-farmer clashes and communal cattle raiding. Synthesises ACLED, UCDP, and PMVE."*

> *"Three — a reproducible training recipe: focal loss plus inverse-frequency class weights, which lifts VICTIM by eleven F1 points and ACTION by seven without hurting other entities. Reproducible from the configurations in the repository."*

> *"Four — a curated knowledge base: a hundred-and-fifty armed groups, two hundred cities, fifty-four countries, weapons. Plays the dual validate-and-enrich role."*

> *"Five — a deployable web platform: FastAPI, React, PostgreSQL, all packaged with Docker Compose. End-to-end documented and reproducible. This is the contribution the related-work landscape said was missing."*

**If they probe:**
- **"Which is the most novel?"** — *"The combination, not any single one. In isolation, contribution three (focal + weights) has the cleanest measurable effect."*

**Pivot.**

> *"And honestly, what this thesis does not do."*

---

## Slide 37 — Limitations [110 s]

**What's on screen.** Four numbered limitations: English-only, 30% synthetic, no learned hierarchical classifier comparison, KB decay.

**Why this slide exists.** Owning limitations explicitly disarms half of Q&A. Examiners cannot attack what you have already conceded.

**What to say (verbatim):**

> *"Four limitations, named honestly."*

> *"One — English-language only. A large share of African conflict reporting is in French, Arabic, Portuguese, and African languages. A monolingual extractor leaves that signal on the floor. This is the single largest capability gap."*

> *"Two — roughly thirty percent of the training corpus is template-augmented. The validation split is drawn from the same combined corpus, which makes the metrics a fair estimate of in-distribution performance but does not guarantee they hold up on translated articles, citizen journalism, or social-media excerpts."*

> *"Three — no head-to-head comparison against a learned hierarchical event-type classifier. EVENT_TYPE is recovered post-hoc by a rule-based taxonomy classifier; a learned version was scoped out and is the second high-priority future-work item."*

> *"Four — knowledge-base coverage decays without curation. Armed groups change names, splinter, recombine. A stale KB does worse than no KB, because it actively misleads the validator. Operational deployments need a domain expert to keep it current."*

**If they probe:**
- **"Which limitation worries you most?"** — *"Limitation one — multilingual. The operational consumer who needs French or Arabic coverage cannot use this system today."*
- **"How much would limitation two move your numbers?"** — *"Conservative estimate: 2-4 F1 points downward on out-of-distribution news. We don't know exactly because we lack the labelled out-of-distribution data."*

**Pivot.**

> *"Where the work goes next."*

---

## Slide 38 — Future work [90 s]

**What's on screen.** Three-row table: multilingual, learned hierarchical classifier, natural-language QA. Medium- and lower-priority items mentioned in caption.

**What to say (verbatim):**

> *"Three highest-priority directions, each tied back to a limitation."*

> *"First — multilingual extension. Use XLM-RoBERTa or AfroLM as the backbone instead of bert-base-cased; fine-tune on parallel African-news corpora. This closes the biggest operational gap. Architecture does not change; the training data and the encoder choice do."*

> *"Second — a learned hierarchical event classifier to replace the current rule-based taxonomy step. Two-stage — Level 1 first, then Levels 2 and 3 conditional on Level 1 — is the natural starting point. Rule-based was the right thing to ship for this thesis; learned will scale as the taxonomy grows beyond ninety-five leaves."*

> *"Third — natural-language QA over the event store. Templated SQL from semantic parses for the cheap path, fine-tuned Seq2Seq for the flexible path. This closes the loop for analysts who want to ask 'show me all events attributed to JNIM in the last thirty days' without writing SQL."*

> *"Medium- and lower-priority items — coreference resolution, active-learning loop, exportable PDF briefs, streaming ingestion — are in chapter 7.5 of the thesis."*

**Quick term explanations.**
- *XLM-RoBERTa* — Facebook's cross-lingual BERT variant.
- *Seq2Seq* — sequence-to-sequence model; converts one text sequence to another (e.g., natural-language question → SQL query).

**If they probe:**
- **"Why not all three at once?"** — *"Each is roughly a one-year effort. Multilingual is first because it has the largest operational payoff."*

**Pivot.**

> *"Thank you for your attention."*

---

## Slide 39 — Thank you [30 s]

**What's on screen.** Closing title slide — Thank you. Questions welcome. Name and date.

**What to say (verbatim):**

> *"Thank you for your attention. I welcome your questions."*

Stand still. Make eye contact with each panel member in turn. Do NOT rush to fill the silence — silence is fine. Wait for the first question.

**When the first question lands:**
1. Pause for one beat.
2. If ambiguous, restate the question in your own words ("So you're asking whether…").
3. Answer with the bottom line first, then evidence. Use the Q&A kit.
4. End by checking — "Does that answer the question, or would you like me to go deeper on one aspect?"

**The defence mantra.** Calm, honest, self-aware. A confident "we did not test that" is worth more than a vague "I think it would work."

---

## Rehearsal plan

| Pass | Goal | Cadence |
|:--|:--|:--|
| 1 | Read this document straight through; check pacing | Voice-only, sitting |
| 2 | Stand and deliver with slides, no notes | Time yourself; aim for 29 min total |
| 3 | Record on phone; play back at 1.25× | Note where you slow down or stumble |
| 4 | Deliver to one trusted listener (a peer, not your advisor) | Ask them to interrupt with one mid-talk question |
| 5 | Full rehearsal with backup-slide flips on cued questions | Use the Q&A kit |

**Three days before:** stop changing slides. Memorise the opening sentence of every slide. Sleep.

**Defense day:** water bottle. Arrive thirty minutes early. Test the projector before the panel walks in. Open both `slides.pdf` and `slides.pptx` — PDF is the safe fallback if PowerPoint misbehaves.
