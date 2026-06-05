# VioNER Defense — The Problem Domain

A study document for understanding the thesis's problem statement deeply enough to defend it. Read this alongside the slides — it provides the **why** behind every claim on slides 3–14.

The defense will live or die on whether the panel believes three things:

1. **The problem is real, large, and operational** — not an academic curiosity.
2. **No current solution closes it** — the gap is genuine, not invented.
3. **VioNER closes it (or makes meaningful, defensible progress)** — and the evidence supports the claim.

This document arms you with the reasoning, the numbers, the named examples, and the prepared answers for each of those three.

---

## How to use this document

| Pass | Purpose |
|:--|:--|
| **Read 1** — full pass | Get the structure into your head; absorb the named examples |
| **Read 2** — Parts 5, 6, 7 | The gap, why others fail, why VioNER works — the persuasive core |
| **Read 3** — Part 10 | Defense-day answers to likely panel questions about the problem statement |
| **Defence eve** — Part 9 only | The three elevator-pitch versions of the problem statement |

Each Part stands alone — you can jump to whichever section a panel question targets.

---

# Part 1 · The stakes — why this matters

## What is "conflict monitoring"?

Conflict monitoring is the **systematic, ongoing collection and structuring of information about violent events** so that analysts, decision-makers, and humanitarian responders can answer questions like:

- *"How many fatalities were reported in eastern DRC last month, and which armed groups were involved?"*
- *"Is the rate of attacks on civilians in northern Mali increasing or decreasing relative to six months ago?"*
- *"Which towns in northern Nigeria have seen the most kidnapping incidents this quarter?"*
- *"What patterns of pastoralist–farmer clash are emerging in the Sahel?"*

These are questions that **cannot be answered from raw news articles**. They require the news to be converted into a structured, queryable database of events — one row per incident, with consistent columns for actor, location, date, and casualties.

## The continent-scale picture

Africa hosts a substantial share of the world's active armed conflicts. Drawing from public datasets:

| Indicator | Estimate | Source |
|:--|--:|:--|
| Violent events reported across African outlets per year | **~30,000+** | ACLED, every year since 2020 |
| Active armed conflicts on the continent | **20+** in any given year | UCDP |
| African countries with ACLED-tracked events in 2024 | **All 54** | ACLED African coverage |
| African countries with mass-casualty events in 2024 | **~30** | ACLED |
| Recent major conflict theatres | Sudan, eastern DRC, Sahel (Mali, Burkina, Niger), Cabo Delgado (Mozambique), Tigray and Amhara (Ethiopia), Somalia | Various |

This isn't a niche problem. It's the operational backbone of how the African Union, IGAD, ECOWAS, the United Nations, and humanitarian agencies make decisions about where to deploy peacekeepers, where to send relief, and where to focus diplomatic engagement.

## Who actually uses conflict monitoring outputs?

| Consumer | What they use the data for |
|:--|:--|
| **AU Peace and Security Council (AU-PSC)** | Mandates peacekeeping deployments under Article 12 of the PSC Protocol |
| **AU Continental Early Warning System (AU-CEWS)** | Continental situation-awareness reports to the AU-PSC |
| **ECOWAS Early Warning Directorate (ECPF)** | West African regional response coordination |
| **IGAD Conflict Early Warning Mechanism (CEWARN)** | Horn of Africa cross-border conflict tracking |
| **UN OCHA** | Humanitarian-response prioritisation (where to send food, medical, shelter) |
| **UNHCR** | Refugee-movement prediction; camp-capacity planning |
| **UN DPPA** | Mediation and good-offices missions |
| **Academic researchers** | Conflict-onset, conflict-recurrence, peace-process studies — published in *Journal of Peace Research*, *International Studies Quarterly*, etc. |
| **National governments** | Ministry of Peace (Ethiopia), Office of the National Security Adviser (Nigeria), etc. |
| **Civil society** | International Crisis Group, ACAPS, Conflict Armament Research |

**Reduced extraction cost benefits every one of these consumers.** That's the operational case, in one sentence.

## What goes wrong when monitoring fails?

Three concrete failure modes — useful examples for the defense:

### Failure mode 1 — Delayed response

> April 15, 2023 — fighting breaks out between the Sudanese Armed Forces (SAF) and the Rapid Support Forces (RSF) in Khartoum. ACLED records this initial day correctly. But the subsequent week sees over 200 reported attacks in Khartoum, Darfur, and elsewhere — most ACLED records on those events appear *days to weeks later* as analysts work through the backlog. UNHCR, OCHA, and the AU-PSC are operating on stale data during the critical first window when displacement and casualty trajectories diverge. *This is the bottleneck VioNER targets.*

### Failure mode 2 — Inconsistent coding

Without a structured extraction pipeline that uses canonical actor names, the same event reported in two outlets can appear in the database under different actor strings — "Al-Shabaab fighters", "al-shabaab militants", "Al Shabaab" — and downstream analytics over-counts incidents (because aggregation by actor string treats those as three distinct groups) or under-counts (because deduplication accidentally collapses them with unrelated events). *KB-based canonicalisation, contribution #4 of this thesis, prevents this.*

### Failure mode 3 — Selective coverage

Manual coding capacity is finite. When analysts are overwhelmed by surge events in one region (Sudan, 2023), coverage of slow-burning conflicts elsewhere (Cabo Delgado, eastern DRC) gets thinner — not because those situations matter less but because the analyst hours simply don't exist. *Automation here doesn't replace analysts; it lets the same staff cover more theatres.*

---

# Part 2 · How monitoring works today

## The end-to-end pipeline (current state)

```
News outlets publish articles    →    Aggregator/feed collects articles
                                                |
                                                ▼
                                    Analyst reads article
                                                |
                                                ▼
                            Analyst identifies: WHO, WHAT, WHEN,
                                                WHERE, HOW, casualties
                                                |
                                                ▼
                              Analyst cross-references actor
                              names against internal lists
                                                |
                                                ▼
                            Analyst logs row into database
                            (ACLED, UCDP, internal system)
                                                |
                                                ▼
                            Quality-control review (2nd analyst)
                                                |
                                                ▼
                              Public/internal database updated
```

Every step except the first two and the last is **manual analyst time**. The article-to-record conversion is the bottleneck.

## The institutional players

| System | Type | Annual events tracked | How produced |
|:--|:--|--:|:--|
| **ACLED** *(Armed Conflict Location & Event Data)* | Hand-coded | ~70,000 global / ~30,000 African | Network of regional analysts; each event coded by hand from primary news sources |
| **UCDP** *(Uppsala Conflict Data Program)* | Hand-coded | ~15,000 events (more selective inclusion criteria) | Uppsala-based analysts using structured protocols |
| **ICEWS** *(Integrated Crisis Early Warning System)* | Automated, closed | Hundreds of thousands of records | Lockheed-Martin pipeline, DARPA-funded; not Africa-tuned |
| **GDELT** *(Global Database of Events, Language, and Tone)* | Automated | Many millions of records | Pattern-based extraction from a global news firehose |
| **AU-CEWS** | Hand-coded internal | Not published | AU staff producing situation reports |
| **IGAD CEWARN** | Hybrid | Field-monitor reports + some news | Field-reported data with structured forms |

**Key point:** ACLED, the gold standard for African conflict data, is **fully manual**. Its quality is excellent because human analysts read every article. That manual coding is exactly the work this thesis automates the upstream portion of.

## The analyst workflow — minute by minute

This is the "Day in the analyst's life" slide expanded — useful if a panellist asks for detail.

| Step | Time | What the analyst does |
|:--|--:|:--|
| 1 | 0:00 | Open the article in the source-management tool |
| 2 | 0:30 | Read the headline and lead paragraph |
| 3 | 2:00 | Read the full article to identify the event(s) reported |
| 4 | 4:00 | Identify and classify the actor(s) — perpetrator(s) and victim(s) |
| 5 | 6:00 | Cross-reference the actor name against the internal armed-group list (catch aliases, spinoffs, name changes) |
| 6 | 8:00 | Identify location — narrow from country to region to city/district |
| 7 | 11:00 | Identify date and time — resolve relative expressions ("yesterday", "earlier this week") |
| 8 | 12:00 | Extract casualty figures with qualifiers ("at least", "approximately", "according to authorities") |
| 9 | 14:00 | Determine event type from a controlled taxonomy |
| 10 | 16:00 | Write event description in the structured-record form |
| 11 | 18:00 | Source-reliability check; flag if single-source uncorroborated |
| 12 | 20:00 | Save to database; queue for QC review |

Mean: **15–25 minutes per article**, depending on complexity. A multi-event article (e.g., a weekly roundup that mentions five incidents) can take **45+ minutes**.

## The economics

Multiply the per-article cost by the annual volume:

| Metric | Calculation | Result |
|:--|:--|--:|
| Annual events to code | (given) | 30,000 |
| Mean minutes per article | (above) | 20 |
| Annual analyst-minutes required | 30,000 × 20 | 600,000 |
| Annual analyst-hours | 600,000 / 60 | **10,000** |
| FTE equivalent (1,800 working hrs/yr) | 10,000 / 1,800 | **~5.5 FTE** |
| Annual cost at $50,000/FTE | 5.5 × $50,000 | **~$275,000/yr** |

The dollar figure is illustrative — ACLED, UCDP, and AU-CEWS budgets are not directly comparable to this. But the **labour mass** — 5+ full-time analysts whose entire job is reading articles and typing rows — is structurally accurate. **Even cutting that in half** (5.5 FTE → 2.5 FTE) **frees three analysts to cover theatres that are currently under-monitored.**

## What "even partial automation" buys

The thesis explicitly does **not** claim to replace analysts. It claims to make each analyst-minute more productive by handling the first-pass extraction. The analyst then reviews and corrects, rather than starting from blank.

A useful framing for the panel: **VioNER turns an article-reading task into an article-reviewing task**. The cognitive load of reviewing is lower than reading-from-scratch, and the per-article time drops correspondingly. Conservative estimates from comparable NLP-assisted-coding workflows in other domains suggest a 40–60 % time reduction is realistic.

---

# Part 3 · Why is automating this hard?

Six structural challenges that make conflict-event extraction **harder than generic NER** on Western news:

## Challenge 1 — Domain-specific entities not in pretraining corpora

Generic NER models — spaCy's `en_core_web_lg`, HuggingFace's `dslim/bert-base-NER` — were pretrained on Wikipedia, news, and books that mention some African armed groups but rarely as fine-grained entity classes with operationally-meaningful sub-types.

| Entity | What a generic model knows | What VioNER needs |
|:--|:--|:--|
| Al-Shabaab | "ORGANIZATION" | ACTOR with subtype = jihadist, country = SOM |
| Boko Haram | "ORGANIZATION" | ACTOR; also flag as faction-of with ISWAP |
| Rapid Support Forces (RSF) | "ORGANIZATION" (often missed if rendered as "RSF") | ACTOR with subtype = paramilitary, country = SDN |
| JNIM | Likely unknown — too new | ACTOR with full canonical name and Sahel country list |
| Fano | Likely unknown — Ethiopian context | ACTOR with subtype = communal-militia |

The list of African armed groups is **dynamic** — groups splinter, recombine, rebrand. The Allied Democratic Forces (ADF) in eastern DRC pledged allegiance to the Islamic State in 2019 and is now sometimes referred to as ISCAP (Islamic State Central Africa Province). Generic NER carries none of this domain knowledge.

## Challenge 2 — Severe class imbalance from the source distribution

In a corpus of African conflict reporting tokenised at the BIO label level, the distribution is **dramatically skewed**:

| BIO label group | Approximate token share |
|:--|--:|
| O (non-entity) | **~78 %** |
| ACTOR / CITY / DATE (high-support) | ~15 % |
| REGION / DISTRICT (medium-support) | ~5 % |
| **VICTIM / ACTION / CASUALTIES (low-support)** | **~2 %** |

The operationally most important entities — victims, the action verb, and casualty counts — are the rarest. A naïve model optimises for overall accuracy, which means optimising for O. Without explicit imbalance handling, the model gets very good at O and mediocre at exactly what matters.

## Challenge 3 — Geographic ambiguity in African administrative divisions

African geography has structural ambiguity that confuses surface-form NER:

| Place | Why ambiguous |
|:--|:--|
| **Goma** | A city in eastern DRC; also the de facto seat of North Kivu province; sometimes "Goma" refers to the surrounding territory |
| **Mogadishu** | A city; also Banadir Region's seat; Banadir is itself sometimes called "Mogadishu" |
| **Kinshasa** | A city; also a province (the city is its own province — "city-province") |
| **Kano** | A city; also Kano State (Nigeria) |
| **Lagos** | A city; also Lagos State (Nigeria) |

"Fighting in Goma" — is Goma the CITY, the DISTRICT, or the REGION? The thesis tags it as CITY by default (more often right than wrong) but the consistent confusions show up in the location confusion matrix (Table 6.11). This is why DISTRICT is the weakest entity by F1.

## Challenge 4 — 5W1H grouping is not standard NER output

Standard NER returns flat entity lists: `[(Al-Shabaab, ORG), (Mogadishu, LOC), (Tuesday, DATE), (12 soldiers, NUM)]`. That's not what an operational consumer wants.

Operational consumers want **structured 5W1H records**:

```json
{
  "WHO_perpetrator": "Al-Shabaab",
  "WHO_victim": "12 soldiers",
  "WHAT_action": "attack",
  "WHEN": "Tuesday",
  "WHERE": "near Mogadishu (Somalia)",
  "HOW_casualties": {"killed": 12, "qualifier": "at least"}
}
```

The role distinctions — *perpetrator* vs *victim*, both of which a generic NER tags as ORG/PER — are essential and absent from generic NER schemas. The thesis introduces these role distinctions at the entity-type level (ACTOR, VICTIM are distinct entity types) so the structuring is baked in, not bolted on afterwards.

## Challenge 5 — Multi-event articles

African news often packages multiple incidents into one article:

> *"In separate developments this week, JNIM fighters attacked an army outpost in central Mali on Monday, killing eight soldiers; the same group is suspected of involvement in Tuesday's roadside bombing in Niger that wounded four; meanwhile in northern Burkina Faso, Friday's reported clash between security forces and unidentified gunmen left at least five dead."*

One article, three events, three different actor-location-date combinations. Generic NER returns one flat entity list and the consumer has to disambiguate which entities belong to which event. The thesis's segmentation step (§4.7 in the thesis) addresses multi-event articles via sentence-level event segmentation — but this is hard in general and is one of the remaining limitations.

## Challenge 6 — Out-of-distribution variations

Even within English, conflict reporting varies in style:

| Source type | Stylistic features |
|:--|:--|
| Reuters/AP wire copy | Formal, terse, follows house style |
| AllAfrica / African outlet syndicated | Variable formality; sometimes translated from French |
| Local outlet (e.g., Daily Trust, Punch) | More colloquial; specific local terminology |
| Citizen-journalism social media | Compressed, abbreviated, hashtag-heavy |
| Wire-service press releases (gov, NGO) | Bureaucratic register |

The training corpus draws primarily from ACLED's curated notes, which are themselves drawn from a mix of these but skew towards wire-service patterns. Out-of-distribution sources — citizen journalism in particular — are a known generalisation limit and are flagged in the thesis's threats-to-validity section (§6.13).

---

# Part 4 · The landscape of current solutions

Each major existing system, with what it does well and where it falls short for this specific use case.

## Solution 1 — ACLED (the hand-coded gold standard)

| Aspect | Detail |
|:--|:--|
| **What it does** | Hand-coded structured event database covering all of Africa (and globally elsewhere) |
| **What it does well** | Quality is excellent. Coders use rigorous protocols, source diversity, multi-coder review. Coverage is uniform across countries. The taxonomy is well-defined. |
| **What it falls short on** | **Throughput.** Hand-coding 30,000 African events per year requires a large analyst workforce, fast turnover during surge events is limited, and the cost scales linearly with coverage. ACLED's actor list is comprehensive but it is updated less frequently than would be operationally ideal. |
| **Relationship to VioNER** | ACLED is the *target*, not the *competitor*. The thesis uses ACLED open data as the training corpus, and the goal is to produce records that have ACLED-grade structure with substantially lower per-record analyst time. |

## Solution 2 — UCDP (the more selective hand-coded database)

| Aspect | Detail |
|:--|:--|
| **What it does** | Uppsala-based hand-coded database with stricter inclusion criteria (25+ battle deaths per year per dyad) |
| **What it does well** | Long historical horizon (back to 1989); rigorous dyadic conflict-coding methodology; strong academic citations |
| **What it falls short on** | Same fundamental bottleneck as ACLED (hand-coded), plus a higher inclusion threshold that excludes lower-intensity events that operational consumers still care about |
| **Relationship to VioNER** | Complementary — UCDP for long-horizon academic studies, VioNER + ACLED for operational monitoring |

## Solution 3 — ICEWS (the automated, closed, generic-news pipeline)

| Aspect | Detail |
|:--|:--|
| **What it does** | Automated event extraction from global news, developed by Lockheed Martin under DARPA funding (now sponsored by the US government) |
| **What it does well** | Scale. Hundreds of thousands of records covering global news. Established pipeline. |
| **What it falls short on** | **Africa is not the target domain.** Schema is generic-geopolitical (CAMEO event codes), not 5W1H structured for African violent events. Pipeline is closed — you cannot inspect what it does, audit failure modes, or extend it. African armed groups are not first-class entities. |
| **Relationship to VioNER** | ICEWS exists in a different cell of the landscape matrix (generic, automated, closed). VioNER occupies the African, automated, **open and operational** cell. |

## Solution 4 — GDELT (the planetary-scale automated tracker)

| Aspect | Detail |
|:--|:--|
| **What it does** | Planetary-scale tracking of "events" defined via a CAMEO-derived schema, extracted from a global news firehose |
| **What it does well** | Massive scale (many millions of records). Real-time updates. Open access. |
| **What it falls short on** | **Precision and structure.** Extraction is heavily pattern-and-sentiment based. The "events" GDELT identifies often correspond to mentions or statements rather than concrete incidents. The 5W1H structure is absent — you get coordinates and CAMEO codes, not perpetrator-victim-action triples. Researchers using GDELT for conflict analysis routinely report substantial false-positive noise. |
| **Relationship to VioNER** | GDELT is a useful aggregator-of-news-mentions, not a competitor for structured event extraction. VioNER produces records that GDELT does not. |

## Solution 5 — Generic NER (spaCy, HuggingFace BERT-NER, Stanford CoreNLP)

| Aspect | Detail |
|:--|:--|
| **What it does** | Token-level entity tagging for generic PERSON / ORGANIZATION / LOCATION / DATE / MONEY / etc. |
| **What it does well** | Robust on Western news. Easy to deploy. Well-documented. Strong on entity types that overlap with pretraining (PERSON, well-known organisations). |
| **What it falls short on** | African armed groups are absent or generic-ORG. No 5W1H role distinction (perpetrator vs victim). No taxonomy. No KB. No event-extraction post-processing. |
| **Relationship to VioNER** | A useful **baseline** — backup slide B9 shows that VioNER's macro F1 is 0.94 vs generic BERT-NER's 0.82 on the four-entity overlap. |

## Solution 6 — Prior African NLP work (Masakhane, AfriBERTa, AfroLM)

| Aspect | Detail |
|:--|:--|
| **What it does** | Builds African-language NLP resources: parallel corpora, language-specific pretrained models, language-coverage benchmarks |
| **What it does well** | Pioneering work on African-language NLP. Builds the foundations multilingual extension will rely on. Strong community model. |
| **What it falls short on** | **Stops at the model boundary.** Excellent token-level entity tagging models; minimal operational packaging. No published end-to-end deployed systems for African violent-event extraction. |
| **Relationship to VioNER** | Complementary. VioNER builds the operational layer that Masakhane-style work can plug into. The thesis explicitly cites multilingual extension via AfroLM as future work item #1. |

## Solution 7 — LLM-based extraction (GPT-4, Claude, Gemini)

| Aspect | Detail |
|:--|:--|
| **What it does** | Prompt-engineered extraction from articles using large general-purpose language models |
| **What it does well** | High zero-shot quality. Can produce structured output via prompting. Handles language variation gracefully. |
| **What it falls short on** | **Four operational disqualifiers.** (1) Closed weights — vendor can update model silently, breaking reproducibility. (2) Per-call cost scales with volume. (3) Auditability — you cannot inspect the inference path or guarantee output schema. (4) Data sovereignty — sending conflict-reporting metadata to a US commercial API is non-starter for many AU member states. |
| **Relationship to VioNER** | LLM-based extraction is a credible **future baseline** to compare against, not a substitute. The thesis's contribution is the **deployable, auditable, reproducible, on-prem** baseline that LLM work must beat to displace. |

## Solution 8 — Internal bespoke pipelines (national governments, NGOs)

Several governments and NGOs have built internal extraction pipelines. They tend to be:

- Closed (not published)
- Specific to one country or one consumer
- Hand-rolled rules + spreadsheets + Excel macros
- Not benchmarked

These are not *competitors* in any literature-survey sense, but they are the **practical alternative** that operational consumers default to. A defensible thesis answers: "if you don't use VioNER, you build one of these in-house, at higher long-term cost."

---

# Part 5 · The four-part gap — stated and defended

This is the heart of the problem statement. Read this part slowly. The defense of every contribution in the thesis comes back to one of these four gaps.

## What "gap" means here — important framing

Each of the four gaps below is **an operational shortfall in what existing conflict-monitoring systems deliver to their consumers** — the AU-CEWS analyst, the humanitarian coordinator, the academic conflict researcher. The gaps are stated in terms of *what the analyst can't get today*, not in terms of *what ML technique is missing*. That distinction matters: most existing systems (ACLED, GDELT, ICEWS, hand-coded national pipelines) don't use machine learning the way VioNER does, so saying "they don't handle class imbalance" is incoherent — it's not a comparison they would even make sense of.

> **The gaps are operational. The solutions are technical.** Each gap section below describes (a) what the analyst can't get from existing systems, and (b) how VioNER delivers what's missing operationally. The technical methodology (loss functions, training recipes, KB structure, deployment stack) is the *how*, not the *what* — it goes inside the solution section, not the gap statement.

## Why "four-part" and not "one gap" or "seven gaps"?

The thesis frames the contribution as **four** distinct gaps because each corresponds to a different *operational deficiency* in existing systems that consumers face today.

| # | Gap (operational framing) | What the analyst can't get from existing systems |
|:-:|:--|:--|
| 1 | **Structured, role-distinguished 5W1H output, fast** | Automated systems give flat or wrong-schema records; hand-coded systems give the right structure but only slowly |
| 2 | **Recovery of the operationally-critical rare entities** | Automated systems recover dates and locations well but systematically miss victims, casualty counts, and action verbs |
| 3 | **Records you can trust and aggregate** | Existing automated output isn't sanity-checked against world knowledge and isn't canonicalised across surface variations |
| 4 | **A system the analyst can actually deploy and run** | Closed systems aren't installable; open ML systems require engineering; LLM systems require API/prompt setup and have data sovereignty issues |

The four together close the loop from raw news text to operational use. **If any single one is missing, the chain delivers no value.** A perfectly structured output that arrives too late is useless. A fast output that misses victims is useless. An output that captures everything but produces duplicate-actor noise is useless. A pipeline that works but no analyst can install is useless.

If a panellist asks *"why four and not three?"* — the answer is that no existing system fills all four, and each is independently necessary for the consumer's job.

The structure for each gap below is the same: a vignette **from the analyst's perspective** of what they can't get → a plain-English statement of the operational shortfall → what goes wrong in the analyst's workflow → a table mapping each major existing system to its operational shortfall → what VioNER **delivers operationally** to close the gap → **how VioNER does this technically** (the implementation details — focal loss, KB structure, etc. live HERE, not in the gap statement) → why the technical fix is non-obvious → an analogy → empirical receipts → a panel-question answer.

---

## Gap 1 — Grounding-based schema

> **Operational framing:** no existing system delivers structured, role-distinguished 5W1H records through automated extraction at usable speed. The analyst can't get the shape of output they need from any tool that's also fast enough to matter.

### Picture this (from the analyst's perspective)

You're an early-warning analyst at AU-CEWS sitting down to your morning workload. 42 articles came in overnight. You want to use the available extraction tools to triage them — but here's what you find as you cycle through your options.

**Option A: Open GDELT.** Thousands of events flagged for the day. Each record is a coordinate, a CAMEO event code, a sentiment score, and a list of articles where the event was mentioned. There is **no perpetrator name**. There is **no victim**. There is **no casualty count**. To convert any of this into the record your team needs, you'd have to go back to the source articles and extract everything yourself. You close GDELT.

**Option B: Open ACLED.** Beautiful, fully structured 5W1H records — perpetrator, victim, action, location, date, casualties — exactly the schema you need. But the most recent record is from **two weeks ago**. ACLED's analysts are still working through their backlog. Two weeks ago is operationally useless for the article on your desk right now.

**Option C: Run a generic BERT NER demo on the article.** Output: *"Al-Shabaab"* tagged ORG. *"Mogadishu"* tagged LOC. *"12"* tagged NUM. *"Tuesday"* tagged DATE. There's no distinction between perpetrator and victim — Al-Shabaab is just an "organisation". The casualty count "12" is tagged with no role context. The convoy and the soldiers aren't tagged at all. You still have to read the article carefully to extract the 5W1H record yourself.

**Option D: Try an LLM with prompt engineering.** You write a prompt asking for perpetrator, victim, location, date, and casualties. Output varies. Some articles give great structured records. Others give hallucinated fields. There's no way to audit whether each field is *grounded* in the article or invented. Your team's records have to be defensible to the AU Peace and Security Council; you can't ship hallucinated fields.

After an hour, you give up and go back to manual coding.

### Stating the operational gap in everyday language

> **No existing system gives the analyst structured 5W1H records — with role distinctions like perpetrator-vs-victim — through automated extraction at usable speed.** ACLED has the right structure but only at human-coding speed. Automated alternatives (GDELT, generic NER, LLM prompting) drop the structure, drop the role distinctions, or produce output the analyst can't trust.

### What goes wrong in the analyst's workflow without a fix

The analyst's morning looks like this:

1. They try the automated tool. Output is unstructured, wrong-shape, or untrustworthy. They can't use it directly.
2. They fall back to manual coding. 20 minutes per article. 42 articles. They get through 15.
3. The other 27 articles queue overnight.
4. Tomorrow another 42 arrive.

The automated tool's existence **didn't change the analyst's day**. Their cost per record is unchanged because the tool's output doesn't fit their workflow.

### Which existing systems have this gap (and how it shows up operationally)

| Existing system | What output it actually delivers to the analyst | Operational shortfall (what's missing) |
|:--|:--|:--|
| **ACLED** *(hand-coded)* | Structured 5W1H records, high quality | **Speed** — days to weeks of delay; surge events backlog further |
| **UCDP** *(hand-coded)* | Similar structured records | Same delay; more selective inclusion criteria |
| **GDELT** *(automated)* | Event flags with coordinates + CAMEO codes | **No 5W1H structure** — flat records; high noise; no perpetrator/victim distinction; analyst still has to read each source article |
| **ICEWS** *(closed)* | Structured event records via CAMEO | **Not analyst-installable**; generic schema not aligned to African violent-event 5W1H |
| **Generic BERT NER** *(spaCy, HF heads)* | Flat entity tags (PER / LOC / ORG / DATE) | **No role distinctions** — perpetrator and victim both collapse into ORG/PER; African armed groups often missed or mistagged |
| **Prior African NER** *(Masakhane, AfriBERTa)* | Similar flat tags in African languages | Same — no 5W1H role structure; research focus on language coverage, not event-extraction output shape |
| **LLM-based extraction** *(GPT-4 prompting)* | Whatever the prompt asks for | **Inconsistent** — hallucinations possible; not reproducible; not auditable; the analyst can't verify each field is grounded in the source |

**The collective operational gap:** no existing system delivers *fast + structured + role-distinguished + auditable* 5W1H records. ACLED has all but speed. The fast automated alternatives lack structure, role distinctions, or auditability. The analyst can't get what they need to do their job from any single system.

### What VioNER delivers to close this operational gap

VioNER gives the analyst structured 5W1H records with role distinctions through automated extraction at ~150 ms per article on CPU.

| Operational need | What VioNER actually delivers |
|:--|:--|
| 5W1H structure | Output organised by WHO / WHAT / WHEN / WHERE / HOW slots |
| Role distinction (perpetrator vs victim) | Two separate entity types — **ACTOR** vs **VICTIM** — instead of generic ORG/PER |
| Auditable | Every extracted span points back to a specific token range in the source article; nothing is invented |
| Fast | Automated extraction in ~150 ms per article on a single CPU core |

### How VioNER does this technically (implementation details)

*(The gap is operational; this is how VioNER's design closes it internally.)*

The thesis's technical answer is an **8-entity grounding-validated schema**:

- An 8-entity schema designed around the 5W1H operational requirement — ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES — with role distinctions baked in
- A **grounding pilot** in November 2025 that measured how reliably each candidate entity type could be located *verbatim* in source text; types below 80% grounding rate were dropped so that what the analyst sees is auditable against the source
- The pilot reached **Cohen's κ = 0.78** (substantial agreement) on the resulting schema — confirming the labels are reliable enough for the analyst to trust without second-guessing

The grounding pilot, the schema design, and the choice of 8 entities are *implementation choices VioNER made to deliver the operational capability*. The operational gap exists for the analyst either way; the question is whether any system fills it. The thesis's claim is that VioNER does, and §4.3 documents how.

### Why this fix is non-obvious

Three reasons this is real methodological work rather than a trivial choice:

1. **The 26-entity schema looks better on paper.** It offers richer output — more fields per extracted record. A reader of the proposal would naturally think *"more entities = better thesis"*. The non-obvious move was to **reduce** the schema empirically rather than expand it, because output the analyst can't trust is worse than output that's smaller but reliable.

2. **The grounding-rate metric isn't standard practice.** Most NER schema discussions focus on conceptual coverage — *"what entities does this domain need?"* — rather than on whether each entity is reliably groundable in source text. The grounding pilot is the methodological bridge between *what the analyst conceptually wants* and *what can be reliably automated*.

3. **The recovery mechanism for dropped entities required separate engineering.** Dropping EVENT_TYPE from the schema only works because EVENT_TYPE comes back through the rule-based taxonomy classifier; dropping COUNTRY only works because it comes back through KB lookup. Without those recovery mechanisms, schema reduction would be a capability loss the analyst would feel.

### Analogy

Think of an annotator as a witness in court. A trustworthy witness only testifies to what they **saw** — *"I saw a red car at the intersection at 3 PM"*. An inference-adding witness layers interpretation on top — *"I saw a red car at the intersection at 3 PM, and the driver looked nervous so they were probably the suspect"*. Two trustworthy witnesses agree on what they saw; two inference-adding witnesses disagree on what they inferred.

A schema that only includes grounded entities is the equivalent of asking witnesses to testify only to what they saw. The analyst-consumer trusts the resulting records the same way a court trusts a clean testimony — even though it captures less interpretation than an embellished one would.

### The empirical receipts

| Claim | Source in thesis |
|:--|:--|
| 8 entities retained, 18 dropped after pilot | §4.3 |
| Grounding-rate distribution was bimodal (clear elbow at 80%) | §4.3, §5.2 |
| Cohen's κ on retained 8-entity schema = **0.78** (substantial agreement) | §5.2 |
| EVENT_TYPE grounding rate was the worst, at **58 %** | §5.2 |
| Latency ~150 ms per article on CPU — the speed half of the gap closure | §6.8 |

### When a panellist asks "isn't this just removing the hard entities?"

> *"In one sense yes — removing entities whose labels we couldn't reliably supervise. But the output the analyst sees is unchanged: perpetrator, victim, action, when, where, casualties, event type. EVENT_TYPE comes back through the taxonomy classifier; COUNTRY comes back through KB lookup. What changed is that every label the model trains on is clean ground truth, so the analyst can audit each extracted span against the source article. The grounding pilot in section 4.3 of the thesis was the methodological step that revealed this trade. The result is an operational capability — fast, structured, auditable extraction — that ACLED achieves only at human-coding speed and other automated systems don't achieve at all."*

In November 2025, before committing to the proposal's 26-entity schema, the thesis ran a **grounding pilot**: a sample of articles was annotated by hand, and for each of the 26 entity types, the team measured the fraction that could be located **verbatim** in source text — using the exact words the article wrote.

The results clustered into two clear groups:

| Group | Entities | Decision |
|:--|:--|:--|
| **Above 80 % grounding rate** | ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES — **8 entities** | **Kept** — supervisable cleanly |
| **Below 60 % grounding rate** | MOTIVE, TRIGGER, EVENT_TYPE, INJURED, DURATION, FREQUENCY, COUNTRY, ORGANIZATION, AFFILIATION, TIME, DAMAGE, DISPLACEMENT, and 6 more — **18 entities** | **Dropped** — too noisy |

EVENT_TYPE, the worst offender, had a grounding rate of only **58 %** — annotators infer event type from action plus actor context rather than reading it off the page.

The 8 retained entities are all reliably supervisable. **The dropped 18 are not lost** — they're recovered downstream by different mechanisms:

- **EVENT_TYPE** comes back through the rule-based taxonomy classifier (Level 1 → 2 → 3 path inferred from the ACTION verb + actor context)
- **COUNTRY** comes back through a KB lookup from the most-specific WHERE entity
- **MOTIVE, TRIGGER, AFFILIATION**, etc. are simply out of scope for the system

Net effect on the consumer: they still see the categories they want — perpetrator, victim, action, when, where, casualties, event type. But every single training signal that the model learns from is clean.

### Why this fix is non-obvious

Three reasons this is real methodological work rather than a trivial choice:

1. **The 26-entity schema looks better on paper.** It offers richer output — more information per extracted record. A reader of the proposal would naturally think *"more entities = better thesis"*. The non-obvious move was to **reduce** the schema empirically rather than expand it.

2. **The grounding-rate metric isn't standard practice.** Most NER schema discussions focus on conceptual coverage — *"what entities does this domain need?"* — rather than on annotator agreement under verbatim grounding. The thesis introduces the grounding pilot as a methodological step: not just *what should we tag* but *what can we reliably tag in a way that produces consistent training signal*.

3. **The recovery mechanism for dropped entities required separate engineering.** Dropping EVENT_TYPE from the schema only works if EVENT_TYPE can be recovered downstream. The taxonomy classifier is the recovery mechanism, and designing it was itself a research choice. Without it, the schema reduction would have been a capability loss.

### Analogy

Think of an annotator as a witness in court. A trustworthy witness only testifies to what they *saw* — *"I saw a red car at the intersection at 3 PM"*. An untrustworthy witness adds inference — *"I saw a red car at the intersection at 3 PM, and the driver looked nervous so they were probably the suspect"*. Two trustworthy witnesses agree on what they saw; two inference-adding witnesses disagree on what they inferred.

A schema that only includes grounded entities is the equivalent of asking witnesses to testify only to what they saw. The result is more *reliable* even though it captures less *interpretation*.

### The empirical receipts

| Claim | Source in thesis |
|:--|:--|
| 8 entities retained, 18 dropped after pilot | §4.3 |
| Grounding-rate distribution was bimodal (clear elbow at 80%) | §4.3, §5.2 |
| Cohen's κ on retained 8-entity schema = **0.78** (substantial agreement) | §5.2 |
| EVENT_TYPE grounding rate was the worst, at **58 %** | §5.2 |

### When a panellist asks "isn't this just removing the hard entities?"

> *"In one sense yes — removing entities whose labels we couldn't reliably supervise. But the dropped entities are recovered downstream — EVENT_TYPE through the taxonomy classifier, COUNTRY through KB lookup. The output schema an operational consumer sees is unchanged: perpetrator, victim, action, when, where, casualties, event type. What changed is that every label the model trains on is clean ground truth, not annotator interpretation. The grounding pilot was the methodological step that revealed this trade. Section 4.3 of the thesis documents the pilot and the schema cut."*

---

## Gap 2 — Imbalance-aware training

> **Operational framing:** automated extraction tools recover the easy entities (date, location) well but systematically miss the operationally critical ones (victim, casualty count, action verb). So automation doesn't save the analyst the time they actually want saved — they still have to read each article for what matters most.

### Picture this (from the analyst's perspective)

You're an analyst evaluating whether a generic automated extraction tool would actually save you time. You take a representative sample of 50 articles and run them through a generic BERT NER demo. Then you tally what the tool recovered against what you needed:

| 5W1H slot you need | What the tool recovered |
|:--|:--|
| WHEN (date) — *"on Tuesday"* | ✓ correctly recovered in 48 / 50 articles |
| WHERE (city) — *"near Mogadishu"* | ✓ correctly recovered in 47 / 50 articles |
| WHO (perpetrator) — *"Al-Shabaab fighters"* | △ recovered in 42 / 50 (often tagged as generic ORG, sometimes missed) |
| WHO (victim) — *"12 soldiers"* | ✗ correctly recovered in 19 / 50 |
| WHAT (action) — *"attacked"* | ✗ recovered in 22 / 50 (often missed in passive-voice constructions) |
| HOW (casualties) — *"at least 12 killed"* | ✗ correctly recovered in 14 / 50 (the qualifier *"at least"* almost always dropped) |

You see the pattern. The tool handles **dates and locations** beautifully — but those are the *easy* entities. You could find those yourself by skimming a headline. The hard entities — *who got harmed, what was done, how many died* — are exactly the ones the tool systematically misses.

Your conclusion: *"This tool would tell me when and where every article describes an attack, but I'd still have to read every single one to know who got attacked and how many died. Those are the entities I'd otherwise read for. The tool isn't actually saving me time."*

You reject automation and continue manual coding.

### Stating the operational gap in everyday language

> **Existing automated extraction tools recover the easy entities (date, location) well but systematically miss the operationally critical rare entities (victims, casualty counts, action verbs).** This means automation doesn't save the analyst the time they'd actually want saved — because they still have to read each article to recover what matters most.

### What goes wrong in the analyst's workflow without a fix

The analyst evaluates a generic automated tool, sees the rare-entity recovery is poor, and rejects automation altogether. The conclusion they draw — *"automated tools aren't ready for this domain"* — blocks adoption of *any* system, including ones that **do** recover the rare entities, because their first experience was negative.

This is a real adoption barrier. Existing automated tools weren't designed for the African violent-event entity distribution; they were trained on general news where the entity distribution is different. They inherit the priorities of general news (PER, LOC, DATE) and shortchange the priorities of conflict reporting (VICTIM, ACTION, CASUALTIES). The analyst sees the consequence and writes off automation as a class.

### Which existing systems have this gap (and how it shows up operationally)

| Existing system | What entities it recovers well for the analyst | What it systematically misses |
|:--|:--|:--|
| **Generic BERT NER** *(spaCy, HF heads)* | PERSON, LOCATION, ORGANIZATION, DATE | Victim phrasings (*"civilians"*, *"schoolgirls"*); casualty counts with qualifiers (*"at least 12"*); action verbs in passive voice |
| **Prior African NER** *(Masakhane, AfriBERTa)* | Standard PER / LOC / ORG / DATE in African languages | Same — flat entities trained for language coverage, not for violent-event-domain rare entities |
| **GDELT** *(automated, pattern-based)* | Event flags with coordinates and date | Victims, casualty counts, descriptive actions — all reduced to CAMEO codes that drop the detail |
| **ICEWS** *(closed)* | Structured event records | **Closed** — can't audit which rare entities it misses; publicly-available output suggests CAMEO-coded extraction loses nuance the same way |
| **ACLED** *(hand-coded)* | Everything, including rare entities | Nothing — but **throughput is the bottleneck**; rare-entity recovery comes from humans reading each article, which is exactly the cost VioNER is supposed to reduce |
| **LLM-based extraction** *(GPT-4, Claude)* | Variable per article | **Inconsistent** — rare entities recovered well in some articles, hallucinated in others; no reliability guarantee the analyst can rely on |

**The collective operational gap:** no existing automated system has demonstrated reliable recovery of the operationally-critical rare entities (victims, casualty counts, action verbs) for African violent-event extraction. The hand-coded systems recover them by humans reading articles — which is the cost VioNER is meant to reduce. The automated alternatives don't recover them well enough for the analyst to skip the manual read.

### What VioNER delivers to close this operational gap

VioNER specifically recovers the rare entities at a rate that makes review-vs-rewrite finally save the analyst time:

| Rare entity | What VioNER recovers (F1) | What this means for the analyst |
|:--|--:|:--|
| ACTION | **0.866** | Most action verbs (active or passive voice) recovered correctly |
| CASUALTIES | **0.885** | Most casualty counts with their qualifiers (*"at least"*, *"approximately"*) recovered intact |
| VICTIM | **0.817** | Most victim phrasings recovered, including descriptive forms (*"twelve civilians"*) |

These numbers are on the held-out validation set; details in §6.5. **The analyst evaluating VioNER's output sees that the entities they care about most are recovered at a rate that makes review (reading the model's output and correcting) actually faster than rewrite (reading the article from scratch).**

### How VioNER does this technically (implementation details)

*(The gap is operational; this is how VioNER's training internally closes it.)*

The thesis's technical answer is a **specific training recipe** — focal loss combined with inverse-frequency class weights. The ablation in §6.6 of the thesis compares four training configurations and quantifies the rare-entity recovery:

| Training configuration | VICTIM F1 | ACTION F1 |
|:--|--:|--:|
| Plain cross-entropy *(what generic BERT NER uses)* | 0.708 | 0.794 |
| Class-weighted cross-entropy alone | 0.776 | 0.834 |
| Focal loss alone | 0.792 | 0.842 |
| **Focal loss + class weights** *(production)* | **0.817** | **0.866** |

The combination of focal loss with class weighting lifts VICTIM by **11 F1 points** and ACTION by **7** over the plain training that produces generic BERT NER models — without hurting any other entity. This is the implementation detail that produces the operational delivery the analyst sees.

The analyst doesn't need to know about focal loss. They need to know the rare entities are recovered. The technical recipe is how that recovery happens.

### Why this fix is non-obvious

Three reasons it took methodological work:

1. **Either ingredient alone is insufficient.** Class weights alone get VICTIM to 0.776 (+7). Focal loss alone gets to 0.792 (+8). The combination gets to 0.817 (+11) — more than either alone, more than a simple sum. The two ingredients are complementary, not redundant. A casual reader would assume one or the other is "enough"; the empirical answer is no.

2. **Naïve weighting destabilises training.** Without a cap on the per-class weights, the rarest classes (VICTIM, CASUALTIES) end up with weights large enough to blow up the gradient in early epochs. Finding the right cap (10 in this thesis) was empirical.

3. **The focal-loss focusing parameter has knobs that need tuning.** The literature default of γ = 2 happens to work; γ = 1 gives smaller gains; γ = 3 destabilises training. These had to be tested.

### Analogy

Imagine a classroom intercom system. Plain training is like a single loudspeaker that broadcasts the same volume to every student — the loud students (common entities, very numerous) drown out the quiet ones (rare entities). Class weights are like giving each rare-entity student a personal megaphone — their voice is amplified. Focal loss is like an intelligent listener that mutes any student already saying the right thing and pays attention only to those still struggling. Together, the intercom system finally hears the rare students clearly — which means the analyst finally hears the rare entities in VioNER's output.

### The empirical receipts

| Claim | Source in thesis |
|:--|:--|
| Rare-entity distribution in conflict reporting (VICTIM, ACTION, CASUALTIES collectively under 5% of tokens) | §5.5 |
| Generic NER under-recovers these rare entities (the gap) | §3.2 — related work on generic NER limitations |
| VICTIM F1: 0.708 (plain) → 0.817 (focal + weights) | §6.6, Table 6.8 |
| ACTION F1: 0.794 → 0.866 | §6.6, Table 6.8 |
| No entity hurt by the production training configuration | §6.6, full per-entity table |
| Run-to-run macro F1 variance ±0.4 points; gains exceed this by 25× | §6.4 + §6.6 |

### When a panellist asks "isn't this just standard NER training with a tweak?"

> *"The operational gap is that the analyst can't get reliable victim, casualty, and action-verb recovery from existing automated tools — that's what blocks them from adopting automation in this domain. The training recipe — focal loss with inverse-frequency class weights — is how VioNER closes that gap internally. The ablation in section 6.6 shows that the combination lifts VICTIM by 11 F1 points over the plain cross-entropy training that generic BERT NER models use, with no other entity hurt. Focal loss itself was published by Lin et al. in 2017 for object detection; what this thesis contributes is the empirical evidence — for African violent-event extraction specifically — that focal loss combined with class weights is the training configuration that recovers the operationally-critical rare entities at a rate analysts can rely on."*

Two modifications, applied together:

1. **Inverse-frequency class weights** — every token's loss gets multiplied by a per-class weight. Rare classes (VICTIM) get a big weight (~10); common classes (O) get a tiny weight (~0.075). This **rebalances across classes** — VICTIM tokens become ~130× more loss-impactful than O tokens.

2. **Focal loss** — every token's loss gets multiplied by an extra factor that shrinks toward zero when the model is already confident and correct on that token. The optimiser then effectively "skips" tokens it has already mastered, focusing capacity on hard ones. This **rebalances across difficulty within a class**.

Same identical training, only the loss function changes:

| Loss function | VICTIM F1 | ACTION F1 | Gain over baseline |
|:--|--:|--:|:-:|
| Plain cross-entropy (baseline) | 0.708 | 0.794 | — |
| Class-weighted CE alone | 0.776 | 0.834 | +0.068 / +0.040 |
| Focal loss alone | 0.792 | 0.842 | +0.084 / +0.048 |
| **Focal loss + class weights** *(production)* | **0.817** | **0.866** | **+0.109 / +0.072** |

VICTIM gain: **+10.9 F1 points**. ACTION gain: **+7.2 F1 points**. No other entity is hurt by this loss choice.

### Why this fix is non-obvious

Three reasons it took methodological work:

1. **Either ingredient alone is insufficient.** Class weights alone get you to VICTIM 0.776 (+7). Focal loss alone gets you to 0.792 (+8). The combination gets you to 0.817 (+11) — more than either alone, more than a simple sum of the two. The two ingredients attack **different aspects** of the imbalance problem and are *complementary, not redundant*. A casual reader would assume one or the other is "enough"; the empirical answer is no.

2. **Naïve class weighting destabilises training.** If you compute weight proportional to 1/frequency without a cap, VICTIM's weight comes out around 22 — enough to blow up the gradient in early epochs. The thesis **clips at 10**, which is enough to recover the rare-class signal without destabilisation. Finding the clip threshold was empirical.

3. **Focal loss has knobs that need tuning.** Gamma = 2 is the literature default from Lin et al. 2017, but the thesis tested gamma = 1 (smaller gains) and gamma = 3 (training instability). The gamma = 2 choice is empirical, not lifted unverified from the paper.

### Analogy

Imagine a classroom intercom system. Plain cross-entropy is like a single loudspeaker that broadcasts the same volume to every student — the loud students (O class, very numerous) drown out the quiet ones (rare entities). Class weights are like giving each rare-entity student a personal megaphone — their voice is now amplified. Focal loss is like an intelligent listener that **mutes any student who is already saying the right thing** and pays attention only to those still struggling. Together, the intercom system finally hears the rare students clearly.

### The empirical receipts

| Claim | Source in thesis |
|:--|:--|
| 78% of training tokens are O | §2.4, §5.5 |
| VICTIM F1: 0.708 (plain CE) → 0.817 (focal + weights) | §6.6, Table 6.8 |
| ACTION F1: 0.794 → 0.866 | §6.6, Table 6.8 |
| Each ingredient helps individually; combination helps more than sum | §6.6 — full ablation |
| No entity hurt by focal + weights | §6.6, full per-entity table |
| Run-to-run macro F1 variance is ±0.4 points; gains exceed this by 25× | §6.4 + §6.6 |

### When a panellist asks "isn't focal loss just a tweak — and it's been published since 2017?"

> *"Focal loss in isolation has been published since 2017 by Lin and colleagues, for object detection. The contribution here is not the theoretical introduction of focal loss; it's the empirical evidence that focal loss + inverse-frequency class weights, applied to African violent-event NER under this specific class distribution, lifts the rare entities by 7-11 F1 points without hurting common entities. The ablation in section 6.6 — four configurations under identical conditions — is the evidence. Without that ablation, the loss choice would be a methodological assertion without justification."*

---

## Gap 3 — Curated knowledge-base layer

### Picture this

A trained NER model extracts the following entities from one article:

- **ACTOR** = *"Al-Shabaab fighters"*
- **CITY** = *"Goma"*

A human analyst reading this output immediately notices something is wrong. Al-Shabaab operates in **Somalia** — they're active around Mogadishu, Kismayo, Baidoa, and southern Somali regions. Goma is in **eastern Democratic Republic of Congo**, 5,000+ kilometres away. An Al-Shabaab attack in Goma would be wildly out of character — either the article reports something extraordinary, or the article itself contains an error, or the model misextracted one of the two entities.

Whichever is true, the analyst should re-read the article before trusting the record.

**The model has no way to flag this.** It only sees text. It doesn't know what countries Al-Shabaab operates in. It can extract the two entities correctly *as named entities* and still produce a misleading record because it has no **world knowledge**.

Now imagine the same model, in different articles, extracts:

- **ACTOR** = *"Al Shabaab"*
- **ACTOR** = *"al-shabaab militants"*
- **ACTOR** = *"Al-Shabaab"*
- **ACTOR** = *"Al-Shabaab fighters"*
- **ACTOR** = *"al-Shabaab"*

Are these five the same organisation? An analyst reading them knows the answer is yes. The model — and any downstream analytics that aggregates by actor — would count them as **five different actors** unless something explicitly **canonicalises** them into the single canonical entry.

### Stating the gap in everyday language

> A trained NER model extracts entity spans from text. It does not know what country an actor operates in. It does not know that several surface forms refer to the same canonical entity. Operational consumers need both pieces of information — to sanity-check extractions and to aggregate them correctly downstream.

### What goes wrong without the fix — two failure modes

**Failure 1 — Unflagged implausible extractions.** The "Al-Shabaab in Goma" record gets persisted to the database with no warning attached. An analyst running a query later — *"all Al-Shabaab attacks this month"* — sees the spurious record and either:

- Trusts it and reports incorrect information up the chain, **or**
- Notices it and goes back to the source article to verify — which is the original analyst-time cost the system was supposed to reduce.

Either way, the system has failed to add value at this record.

**Failure 2 — Aggregation over surface variation.** Analyst runs a query: *"how many attacks did Al-Shabaab carry out in October?"* The database does exact string matching and reports:

- 18 records with actor = "Al-Shabaab"
- 4 records with actor = "al-shabaab"
- 7 records with actor = "Al Shabaab"
- 3 records with actor = "Al-Shabaab militants"
- 2 records with actor = "Al Shabaab fighters"

The naïve count says "18 attacks" because the query exact-matched the canonical form. The actual total is **34**. The analyst then either:

- Reports 18 (incorrect — undercounts by half), or
- Writes a longer SQL query with all the surface variations they can think of (missing the ones they don't think of, plus any future variations the model produces).

### Which existing systems have this gap (and how)?

| Existing system | What it does about KB validation/enrichment | Specific shortfall for African violent-event extraction |
|:--|:--|:--|
| **ICEWS** *(closed)* | Has an internal actor list used for entity resolution within the pipeline | Closed — the KB cannot be inspected, extended, or reused by other systems; coverage of African armed groups is uneven |
| **GDELT** *(automated)* | Limited canonicalisation; outputs mostly preserve raw surface mentions | Not designed for validation against world knowledge; downstream consumers must handle surface variation themselves |
| **ACLED** *(hand-coded)* | Maintains the most thorough African armed-group actor file in the public domain | Used for *manual coding by human analysts*, not as an automated layer attached to a trained model; no programmatic validate-and-enrich pipeline |
| **UCDP** *(hand-coded)* | Similar to ACLED — strong actor and dyad records | Same limitation: actor records aid human coders, not an automated extraction system |
| **Generic BERT NER** *(spaCy, HF heads)* | No KB layer at all | The model is the deliverable; world-knowledge validation is entirely the consumer's problem |
| **Prior African NER** *(Masakhane, AfriBERTa fine-tunes)* | Typically no KB layer attached to published models | Same limitation — research focus is on the model itself, not the surrounding KB infrastructure |
| **LLM-based extraction** | World knowledge is implicit in the model's pretraining weights | Not auditable; not extensible without retraining the LLM; opaque to consumers; can't be verified or corrected for specific African theatres |

**The collective gap:** no existing automated extraction system has a curated, queryable, validate-and-enrich KB layer **attached to the model and exposed through an analyst-facing API**. ACLED has the closest analogue (its actor file), but it is a human-facing reference, not a programmatic component that flags suspicious extractions and enriches canonical names automatically. VioNER's KB does both, and the §6.7 flag-rate and enrichment-rate numbers quantify the operational value.

### What this thesis does instead

A curated knowledge base of:

- **~150 African armed groups** — each with canonical name, aliases, country of operation, region of operation, group type (jihadist / paramilitary / criminal / communal-militia / etc.)
- **~200 conflict-affected cities** — mapped to country and region
- **54 African countries** — ISO 3166-1 codes
- **38 weapon categories** — from the UCDP weapons catalogue
- **The 4-level taxonomy** — Levels 0 through 3, around 95 leaf categories

The KB is loaded **once** into the FastAPI process when the server starts. It's consulted on every inference request and plays two specific roles:

**Role 1 — Validation.** When the model extracts an ACTOR and a location in the same sentence, the KB checks geographic plausibility. If "Al-Shabaab" (country = SOM) and "Goma" (country = COD) come together, the record gets a `geo_implausible` flag attached. The record is still persisted — the flag does not block extraction — but it is visible in the UI, prompting analyst re-read.

> **Result on the held-out validation set: 2.4 % of extracted events get a geographic-implausibility flag.** Small in aggregate, but those are exactly the events that benefit most from human review.

**Role 2 — Enrichment.** When the model extracts "Al Shabaab", "al-shabaab", "Al-Shabaab fighters", etc., the KB matches every surface form to a single canonical entry: name = "Al-Shabaab", country = SOM, group type = "jihadist". The persisted record then carries a `kb_id` field linking to the canonical entry. Downstream queries aggregate by `kb_id` and get the right count.

> **Result on the held-out validation set: 64.3 % of extracted ACTOR mentions get enriched this way.** That's the percentage that gets correct canonicalisation — and therefore correct aggregation by downstream analytics.

### Why this fix is non-obvious

Three reasons:

1. **A KB is curation work, not modelling work.** It looks "unglamorous" relative to architecture choices like loss function or backbone selection. The temptation in academic work is to skip the KB and assume *"surface variation will get handled downstream"*. That assumption never holds up operationally — downstream consumers don't get exact strings and don't know all the variations.

2. **Validation and enrichment are usually treated as separate problems.** Validation is usually framed as fact-checking; enrichment is usually framed as entity linking. Treating them as **two roles of the same KB** is a small but important architectural choice. It lets a single curated resource serve both purposes without duplicating effort.

3. **A small KB beats a large noisy KB.** 150 actively-curated armed groups, documented and reviewed by domain experts, delivers more operational value than 5,000 inactive or unverified entries scraped from public lists. The thesis's KB is small **on purpose** — to keep the validation signal clean.

### Analogy

Think of a librarian's authority file. When you search for "JFK", "John F. Kennedy", "John Fitzgerald Kennedy", "President Kennedy", or "Kennedy, John F." in a library catalog, you should get the same person back. The authority file is the curated table that maps surface variations to canonical entries. Without it, the catalog double-counts books written about Kennedy under different name forms and your library research is wrong.

A KB does the same for African armed groups. Without it, your conflict-monitoring analytics double- or triple-counts events under different spellings of the same actor. The librarian's authority file isn't glamorous; it's just operationally essential. The same is true of the KB.

### The empirical receipts

| Claim | Source in thesis |
|:--|:--|
| 150 armed groups, 200 cities, 54 countries, 38 weapons | §4.5, Annex C |
| 2.4 % geographic-implausibility flag rate | §6.7 |
| 64.3 % ACTOR enrichment rate | §6.7 |
| UAT Likert "KB enrichment added value" = **4.6 / 5** | §6.10, Table 6.10 (highest item in UAT) |
| Mean alias count per group = 4.2 | Backup B8 |

### When a panellist asks "150 entries is small — why not 10,000?"

> *"150 covers the active African armed-group landscape, not historical exhaustiveness. ACLED's full actor list includes thousands of entries — many of which are inactive, splinter factions that ceased operating, or location-specific instance combinations like 'Al-Shabaab faction in Kismayo'. The 150 in our KB are canonical names of currently or recently active groups with their aliases — and the mean alias count per group is 4.2, which is what matters for the canonicalisation task. A KB that includes inactive groups would produce false-positive enrichments. Maintenance is recommendation 2 in section 7.4 — a part-time domain expert keeps the KB current."*

---

## Gap 4 — Operational packaging (deployable platform)

### Picture this

You are an early-warning analyst at AU-CEWS. Your day starts with 42 new articles in the overnight RSS feed. You hear that a colleague at the Ministry of Peace has been using a new NLP model for African violent-event extraction. You ask them to share it.

They send you a Hugging Face checkpoint file (about 4 gigabytes), a Jupyter notebook, and a README that says:

> *"Create a conda environment, install these 47 Python packages, then run `python infer.py --input article.txt --output extracted.json`. The model expects input in pre-tokenised JSON format with a specific schema documented in section 3.2 of the accompanying paper."*

You are an **analyst**, not a Python developer. You have never used conda. You don't know what a Jupyter notebook is. You read the first line of the README, looked at the 47-package list, closed your laptop, and went back to manual coding.

**The model exists. It works. But it is not operationally usable**, because the gap between *"a trained model on a researcher's laptop"* and *"a system an analyst can actually drive during a crisis week"* is enormous, and almost no published academic work bridges it.

This is what *"stops at the model boundary"* means concretely. The published trained model is **one component** of a working extraction pipeline. The rest of the pipeline — the user interface, the validation layer, the persistent event store, the analytics, the retraining UI, the deployment configuration — is what makes the model actually deliver operational value. Most academic work skips that layer and considers the model the deliverable.

### Stating the gap in everyday language

> A trained model on a researcher's laptop is not an operational capability. The model has to be wrapped in software that a non-ML analyst can drive — an inference page, an event browser, an analytics dashboard, a training UI for retraining when needed. The wrapper is engineering, not research, which is why most academic work skips it. Without the wrapper, the research never reaches the consumer it was meant to help.

### What goes wrong without the fix — three failure modes

**Failure 1 — The analyst can't run the model.** Without an analyst-facing interface, the trained model sits on a server somewhere. The analyst has no way to paste an article and get a structured record back, so they continue manual coding. The model adds **zero operational value** even though it works perfectly in a notebook.

**Failure 2 — There's no event store.** Even if the analyst could somehow run inference, the output is a single JSON blob per article. To query *"all Al-Shabaab attacks this month"* requires a database. Without one, the analyst has to keep JSON files in a folder and write ad-hoc scripts to aggregate them. They give up after a week.

**Failure 3 — There's no retraining pipeline.** Six months later, a new armed group emerges or rebrands. The trained model doesn't know about it and starts misextracting. Without a UI to retrain on fresh data, the model **decays** until someone reruns the original notebook — which the analyst can't do.

### Which existing systems have this gap (and how)?

| Existing system | What it does for deployment | Specific shortfall for African violent-event extraction |
|:--|:--|:--|
| **ICEWS** *(closed)* | Proprietary internal pipeline run by Lockheed Martin / US government | Not installable by external users; not analyst-operable outside the closed pipeline |
| **GDELT** *(public API)* | Public API access to extracted data | Not an extraction tool — it consumes news and produces flat records; consumers can't run extraction on their own articles |
| **ACLED** *(data publisher)* | Publishes the data; no public extraction tool | Consumers download data, can't run extraction themselves; the extraction work is fully internal to ACLED's analyst team |
| **Generic BERT NER** *(spaCy, HuggingFace)* | Open libraries with `pip install` and code-level access | The library is one component; **building the analyst-facing UI, event store, KB layer, training UI, and analytics is the consumer's engineering problem** |
| **Prior African NER** *(Masakhane, AfriBERTa)* | Typically published as trained checkpoints + Jupyter notebook examples | Excellent for ML practitioners; **opaque to non-ML analysts** — no analyst-installable end-to-end system |
| **LLM-based extraction** *(GPT-4, Claude prompting)* | Requires API key, prompt engineering, custom UI, billing setup | Non-trivial engineering for the consumer; high per-call cost at scale; closed weights; data sovereignty concerns for AU member states |

**The collective gap:** no existing system provides a **deployable, non-ML-user-operable, end-to-end system for African violent-event extraction**. Hand-coded systems require analyst labour by definition. Closed automated systems are not installable. Open NLP libraries require substantial engineering to become operational. LLM-based extraction requires API keys, prompt engineering, and exposes data sovereignty concerns. VioNER's stack — FastAPI + React + PostgreSQL + Docker Compose with a documented UAT — is what fills this empty cell of the related-work landscape.

### What this thesis does instead

A complete end-to-end deployable system. Six layers, each chosen so a non-ML analyst can drive the whole thing.

| Layer | Technology | What it does |
|:--|:--|:--|
| **Front-end** | React + TypeScript | Pages for training, inference, event browser, analytics, KB administration. What the analyst opens in a browser. |
| **Service layer** | FastAPI (Python) | Seven REST API route groups. Loads the model once at startup; serves inference requests at ~150 ms each. |
| **Model** | Fine-tuned `bert-base-cased` | The trained NER head. |
| **Knowledge base** | In-process | Loaded with the model; consulted on every inference for validation + enrichment. |
| **Event store** | PostgreSQL 16 | Persistent storage with full-text and JSONB indexing for fast analyst queries. |
| **Orchestration** | Docker Compose | One command (`docker-compose up`) starts the whole stack. |

A non-ML analyst with this system can:

- **Paste an article** into the inference page → get colour-coded entity chips out, grouped by 5W1H category, with KB enrichment shown inline
- **Browse persisted events** with filters: date range, country, taxonomy bucket, actor, confidence threshold
- **View analytics dashboards** showing per-country, per-actor, per-taxonomy, per-month event counts and trends
- **Kick off a retraining run** from a UI form, watch the loss curve update live over WebSocket
- **Add a new armed group** to the KB through the KB admin page when a new theatre opens

All without writing code, opening a terminal, or knowing what a model checkpoint is.

### Why this fix is non-obvious

Two reasons:

1. **It looks like engineering, not research.** Building a FastAPI service and a React front-end is well-understood software development. The temptation in academic work is to say *"that's deployment, not contribution"* and skip it. The thesis's claim is the opposite: **the integration is the contribution**, because no published academic work has integrated all four pieces (schema + model + KB + UI) for African violent-event extraction. The related-work landscape on slide 12 shows the empty cell; this thesis fills it.

2. **Validating that it actually works requires UAT, which is hard to design for an academic project.** Most theses report model F1 numbers and stop there. This thesis ran a five-participant user-acceptance test with two early-warning analysts (the primary intended audience), one academic conflict researcher (secondary), and two NLP developers unfamiliar with the conflict domain (a fairness sanity check — would someone with technical literacy but no domain knowledge find the interface intuitive?). All five completed all six end-to-end tasks. UAT closes the loop from *"the model has F1 = 0.909"* to *"an analyst can actually use it"*.

### Analogy

Imagine someone hands you a car engine. It's a beautiful piece of engineering — high horsepower, low emissions, all the right specs. You can't drive it. To drive somewhere you need a chassis, wheels, steering, brakes, a seat, a dashboard, and a key.

Most academic event-extraction work hands the consumer an engine and calls it a finished product. This thesis hands the consumer a **car**: the engine (the trained model), the chassis (the architecture), the wheels (the API service), the dashboard (the React UI), and the key (the Docker Compose configuration). UAT is the test drive that confirms a non-expert can actually drive away in it.

### The empirical receipts

| Claim | Source in thesis |
|:--|:--|
| FastAPI + React + PostgreSQL + Docker Compose stack | §5.6, §5.7 |
| Seven API route groups documented | §5.6 |
| Inference latency ~150 ms on CPU | §6.8 |
| Five UAT participants, six tasks, all completed | §6.10, Table 6.10 |
| Likert "5W1H structuring was clear" = 4.6 / 5 | §6.10 |
| Likert "Training screen was easy" = 4.0 / 5 *(lowest item — drove future-work direction)* | §6.10 |

### When a panellist asks "isn't this just engineering, not research?"

> *"The engineering is the contribution here because no published academic work in this domain has produced the engineered artefact. The novelty is in the integration — schema + model + KB + UI evaluated end-to-end — not in any single technology choice. The related-work landscape on slide 12 identifies the gap explicitly: end-to-end deployed extraction in the African context is essentially absent from the academic literature. UAT with n=5 isn't inferential statistics, but it qualitatively validates that non-ML users can drive the full pipeline. That's a stronger contribution claim than 'model F1 = X' would be, because it ties the research output back to an actual consumer."*

---

## A quick recap of the four gaps

Memorise this four-cell table — it's the single most useful artefact in this whole document. **The gaps are stated operationally; the VioNER columns are how it closes them technically.**

| # | Gap *(operational shortfall in existing systems)* | What the analyst can't get today | What VioNER delivers operationally | How VioNER does it technically |
|:-:|:--|:--|:--|:--|
| 1 | **Grounding-based schema** | Fast, structured, role-distinguished 5W1H records — ACLED has them slowly, automated tools give flat or wrong-schema output | Auditable 5W1H records at ~150 ms/article with perpetrator-vs-victim role distinction | 8-entity schema, grounding pilot, κ = 0.78 (§4.3) |
| 2 | **Imbalance-aware training** | Reliable recovery of victims, casualty counts, and action verbs — generic NER recovers dates and locations but misses what matters | VICTIM, ACTION, CASUALTIES recovered at F1 0.82, 0.87, 0.89 | Focal loss + inverse-frequency class weights (§6.6 ablation) |
| 3 | **Curated KB layer** | Output that's canonicalised across surface forms AND sanity-checked against world knowledge | 64.3% ACTOR enrichment; 2.4% geo-implausibility flag rate for re-read prompts | 150-group + 200-city KB used for validate-and-enrich (§4.5, §6.7) |
| 4 | **Operational packaging** | A system an analyst can deploy and run without ML expertise | One-command Docker stack, analyst-facing UI for all six end-to-end tasks | FastAPI + React + PostgreSQL; UAT n=5, all six tasks completed (§5.6, §6.10) |

If a panellist asks *"what does VioNER contribute that existing systems don't?"* — read them the second and third columns of this table. That is the whole answer, compressed: each gap is something the analyst can't get from existing tools, and VioNER delivers it. The fourth column is the implementation — *how* — for when they want to drill down.

---

# Part 6 · Why each current solution fails to close the four-part gap

Stating the gaps is necessary but not sufficient. The panel will ask: *"Why doesn't [existing system] already close this gap?"* — system by system, gap by gap.

The matrix:

| System | Gap 1: Grounding | Gap 2: Imbalance | Gap 3: KB Layer | Gap 4: Deployment |
|:--|:-:|:-:|:-:|:-:|
| ACLED (hand-coded) | ✓ implicit | N/A (no model) | ~ partial | ✗ no analyst-facing system |
| UCDP (hand-coded) | ✓ implicit | N/A | ~ partial | ✗ |
| ICEWS (automated, closed) | ✗ | ? unknown | ✗ | ~ closed deployment |
| GDELT (automated) | ✗ | ✗ | ✗ | ~ public API only |
| Generic BERT NER | ✗ generic schema | ✗ | ✗ | ✗ |
| Prior African NLP | ? case-by-case | ? case-by-case | ✗ | ✗ |
| LLM-based extraction | ~ depends on prompt | N/A | ✗ | ✗ closed, non-reproducible |
| **VioNER** | **✓** | **✓** | **✓** | **✓** |

Reading this row by row: **no existing system addresses all four gaps**. The combination is the contribution.

## Per-gap detail: who comes closest, and why they still fall short

### Gap 1 (grounding) — ACLED comes closest

ACLED's coders implicitly apply grounding rules because they are humans reading actual articles. But ACLED does not publish a *machine-applicable* grounded schema. Building a grounded schema usable for supervised training of an NER model is a separate contribution.

### Gap 2 (imbalance) — Prior NLP literature is the comparison

Focal loss is widely used in object detection (Lin et al. 2017) and increasingly in NLP. But the **specific combination of focal loss + inverse-frequency class weights applied to African violent-event NER and evaluated against the right ablation baselines** is new. The ablation table in slide 29 is what no prior work has produced for this domain.

### Gap 3 (KB) — Some internal pipelines come closest

National-government and NGO pipelines do use actor lists. But these lists are typically:

- Not validated against the trained model's predictions
- Not used for enrichment beyond canonical-name lookup
- Not openly published or reusable

VioNER's KB is openly documented (Annex A, Annex B), used for both validation and enrichment, and queryable through an API.

### Gap 4 (deployment) — LLM-based prototypes come closest

It is possible to build a usable extraction system on top of GPT-4 today. But it would be:

- Closed (dependent on the LLM vendor's continuity)
- Per-request priced (not economical at 30,000 events/year)
- Non-reproducible (vendor can update model silently)
- Non-sovereign (data leaves on-premises)

VioNER's stack is open, on-prem, reproducible, and free to run after training.

---

# Part 7 · How VioNER addresses each gap — defended

This part exists for one purpose: to give you defensible, specific answers when the panel asks *"how do you know your solution actually closes the gap?"*

## Defending Gap 1 closure (grounding-based schema)

**Claim:** The eight-entity BIO schema is grounding-based.

**Evidence:**
- The grounding pilot in November 2025 explicitly measured per-entity grounding rate.
- The thesis reports the cut-off threshold (80 %) and the entities at it.
- Annex A documents the inclusion/exclusion rules for each retained entity.
- The IAA on the resulting schema is κ = 0.78 — substantial agreement.

**Question to anticipate:** "Could you have chosen the threshold differently?"  
**Answer:** "Yes, and the methodology is unchanged. Lowering to 70 % would bring back TIME and DURATION; raising to 90 % would drop DISTRICT. The 80 % choice was the elbow of the grounding-rate distribution — types clustered above 80 % or below 60 %, with little in between."

## Defending Gap 2 closure (imbalance handling)

**Claim:** Focal loss + inverse-frequency class weights lifts rare-entity F1 by 7-11 points without hurting common entities.

**Evidence:**
- Section 6.6 ablation table — VICTIM moves from 0.708 (plain CE) to 0.817 (focal + weights)
- All four configurations ablated under identical conditions (same data, same scheduler, same seeds)
- Per-entity F1 reported for every configuration
- No entity is hurt by the production configuration

**Question to anticipate:** "Is the gain statistically significant?"  
**Answer:** "Paired bootstrap at the article level with three seeds gives p < 0.01 for the VICTIM and ACTION gains. Run-to-run macro F1 variance is ±0.4. The +10.9 VICTIM gain exceeds that by 25×."

## Defending Gap 3 closure (KB validation + enrichment)

**Claim:** The curated KB measurably improves operational utility.

**Evidence:**
- 2.4 % flag rate on geographic implausibility — quantifiable signal for analyst re-read
- 64.3 % ACTOR enrichment rate — measurable benefit for downstream aggregation
- UAT scored "KB enrichment added value" at 4.6 / 5 — the highest item in the survey

**Question to anticipate:** "What happens when the KB doesn't know the actor?"  
**Answer:** "Extraction proceeds normally; only the enrichment fields are empty. The KB does not block extraction. For new theatres without KB coverage — e.g., Cabo Delgado in Mozambique — the NER component still extracts ASWJ mentions correctly; the enrichment fields stay blank until a domain expert adds the entry. This is recommendation 2 in section 7.4."

## Defending Gap 4 closure (deployable platform)

**Claim:** A non-ML analyst can drive the full pipeline end to end.

**Evidence:**
- UAT with n=5 participants: 2 EW analysts, 1 academic, 2 NLP developers unfamiliar with conflict domain
- All 5 completed all 6 tasks: inference, browsing, analytics, training, monitoring, reviewing
- 6 Likert items all ≥ 4.0
- 4.6 on "5W1H structuring was clear"
- 4.0 on "training screen was easy" — the lowest item, drove a future-work direction

**Question to anticipate:** "n=5 is small for a usability study."  
**Answer:** "For inferential statistics, yes. For qualitative usability validation, 5 is consistent with Nielsen's industry rule of thumb that 5 users find ~85 % of usability issues. The constructive feedback was internally consistent across participants — three of five asked for drag-and-drop upload, three asked for per-entity training metrics — which is a stronger signal than mean Likert scores at this sample size. A larger UAT is appropriate before production deployment but was out of thesis scope."

---

# Part 8 · What VioNER deliberately does NOT do

Owning the limits is a strength, not a weakness. The panel will probe these regardless; getting there first disarms them.

## Limit 1 — English only

VioNER does not handle French, Arabic, Portuguese, or African languages. A substantial fraction of African conflict reporting is in those languages. The thesis is explicit that this is the single largest operational gap.

**Why this is acceptable for a thesis:**
- Multilingual extension requires a different backbone (XLM-RoBERTa or AfroLM) and a parallel multilingual corpus — both are substantial separate efforts
- The methodological contributions (schema, loss recipe, KB, system) apply to the multilingual case
- Future work item #1 in §7.5

## Limit 2 — 30 % synthetic training data

Roughly 30 % of the 50,000-example corpus is template-based augmentation. The validation split is drawn from the same combined corpus, so the metrics reflect in-distribution performance, not out-of-distribution.

**Why this is acceptable:**
- Augmentation was the only way to lift rare-class F1 — VICTIM, ACTION, CASUALTIES appear in single-digit percentages in raw ACLED notes
- The thesis explicitly bounds the metrics this way (§6.12 discussion)
- Real-news expansion is in future work
- The headline ablation (focal vs CE) holds regardless of augmentation share — it is a *relative* comparison

## Limit 3 — No learned hierarchical event classifier

The taxonomy classification step (Level 1 → 2 → 3) is rule-based, not learned. A learned hierarchical classifier would be more scalable.

**Why this is acceptable:**
- A learned hierarchical classifier requires event-labelled training data that ACLED's schema doesn't provide directly
- Constructing that labelled set would be a thesis in itself
- Rule-based achieves coverage for the current taxonomy
- High-priority future work item #2

## Limit 4 — Knowledge-base coverage decays

The KB needs ongoing curation as armed groups change names, splinter, recombine. The thesis explicitly recommends part-time domain-expert curation (~1 day/week).

**Why this is acceptable:**
- All operational KBs need maintenance — this is not specific to VioNER
- The KB admin UI makes curation a low-burden task
- Recommendation 2 in §7.4 names the role explicitly

## Limit 5 — Single-language extraction across multi-event articles

The thesis handles multi-event articles via sentence-level segmentation, but cross-article event-linking (resolving that two articles describe the same incident) is not addressed.

**Why this is acceptable:**
- Coreference and event-linking are recognised as separate, mature subfields
- Medium-priority future work item

---

# Part 9 · Elevator pitches — three lengths

For when you need to compress the problem statement into a fixed window.

## 30-second pitch (introduction)

> *"This thesis builds an end-to-end system for extracting structured 5W1H information about violent events in Africa from English-language news. The problem it addresses is the manual-coding bottleneck at AU-CEWS, ACLED, and humanitarian agencies — about 30,000 events per year are currently hand-coded, taking thousands of analyst hours. The contribution is a deployable system that combines a grounding-based NER schema, focal-loss-based imbalance handling, a curated knowledge base for validation and enrichment, and a non-ML-user-operable interface. The headline result is that the trained model achieves 0.909 micro F1 on a held-out validation set, with the focal-loss-plus-class-weights recipe lifting the rare-entity VICTIM class by 11 F1 points over plain cross-entropy."*

## 60-second pitch (mid-talk recap)

> *"Conflict monitoring in Africa is operationally important — the AU's early-warning system, ACLED, and humanitarian agencies all need news articles converted into structured event records to do their jobs. Today that conversion is almost entirely manual: an analyst spends fifteen to twenty-five minutes per article. At thirty thousand articles per year, that's around five full-time analysts whose entire job is reading articles and typing rows."*

> *"Existing automated systems don't fill the gap. Generic NER tools don't know African armed groups. ICEWS and GDELT are automated but not Africa-tuned, not 5W1H structured. ACLED and UCDP are gold-standard but hand-coded — exactly the bottleneck this thesis addresses. Prior African NLP work stops at the model boundary — no operational packaging."*

> *"This thesis closes the gap in four ways: a grounding-based eight-entity schema, focal loss with class weights for severe imbalance, a curated knowledge base of African armed groups for validation and enrichment, and a deployable web platform. The result is 0.909 micro F1, validated by user testing with five participants including two early-warning analysts who completed all six end-to-end tasks."*

## 2-minute pitch (post-defense, in conversation)

> *"The work sits at the intersection of NLP — specifically named entity recognition — and operational conflict monitoring for the African continent. The starting observation is that AU-CEWS, ACLED, UCDP, OCHA, and many national governments all need structured event databases — perpetrator, victim, action, location, date, casualties — to make decisions about peacekeeping deployments, humanitarian responses, and continental situation awareness. Today, those databases are produced largely by manual coding. An analyst reads an article, identifies the entities, cross-references actor names against an internal list, and types a row. At African scale — about thirty thousand events per year reported — that's roughly five full-time analysts whose entire job is article-to-row conversion."*

> *"The literature has not closed this. Generic NER tools like spaCy and HuggingFace BERT-NER weren't trained on African armed groups, so they tag Al-Shabaab as a generic organisation rather than a jihadist actor in Somalia. Automated event databases like ICEWS and GDELT operate at scale but use generic schemas and don't produce 5W1H structured output. Prior African NLP work — Masakhane, AfriBERTa — has produced excellent language coverage but stops at the model. None of the published academic work combines African-tuned extraction with operational packaging."*

> *"This thesis contributes four things. One — an eight-entity BIO schema where every label is verifiably grounded in source text, chosen from a 26-entity proposal via a grounding-rate pilot. Two — a training recipe combining focal loss with inverse-frequency class weights, which lifts the rare VICTIM entity by eleven F1 points over plain cross-entropy without hurting common entities. Three — a curated knowledge base of around 150 African armed groups, 200 conflict cities, and 54 countries, used both to validate suspicious extractions and to enrich them with canonical identifiers. Four — a deployable FastAPI plus React plus PostgreSQL stack, with a user-acceptance test confirming non-ML users can drive it end-to-end. The integration of these four — not any single one — is the empirical contribution."*

> *"Honest limitations: it's English-only, thirty percent of the training data is synthetic, and the knowledge base needs ongoing curation. Multilingual extension is the highest-priority future work. But within scope — English-language extraction over African violent events — the system measurably reduces per-article analyst time and produces structured records analysts find trustworthy."*

---

# Part 10 · Defending the problem statement in Q&A

Likely panel questions about the problem domain — with prepared answers in the same plain conversational style as the defense kit.

### Q · "Is this problem really worth a thesis?"

**Bottom line.** The problem is operationally consequential at continental scale and methodologically open in the literature.

**Detail.** Operationally: AU-CEWS, ACLED, UCDP, OCHA, and national governments all depend on structured event databases that are currently hand-coded; the per-event cost is the binding constraint on coverage. Methodologically: no published academic work combines a grounding-based schema, imbalance-aware training, a curated KB layer, and a deployable end-to-end platform for African violent-event extraction. Each ingredient has been studied in isolation; the combination, evaluated empirically at this scale on this domain, is what this thesis contributes.

### Q · "Why violent events specifically — why not all events?"

**Bottom line.** Violent events have the clearest operational consumer base and the clearest evaluation criteria. Generalising to all events broadens the problem without sharpening any contribution.

**Detail.** Operational consumers for violent-event monitoring — AU-CEWS, ACLED, humanitarian agencies — exist as named institutions with documented mandates. "All events" would dilute the focus and make the schema less defensible. The thesis is deliberately narrow on event type and broad on technical contribution.

### Q · "Why English when most African conflict reporting is in other languages?"

**Bottom line.** English-only is a deliberate scope choice driven by training-data availability and computational scope. Multilingual extension is the highest-priority future-work item.

**Detail.** ACLED's English coverage is the largest single source of structured-labelled-text for fine-tuning. Building a multilingual training corpus — French, Arabic, Portuguese, and African languages — would require either a parallel corpus or independent labelling efforts in each language, both substantial multi-year efforts. The methodological contributions — schema design, loss recipe, KB structure, system architecture — apply directly to the multilingual case when those corpora become available. Future work item 1.

### Q · "Why not just use a large language model?"

**Bottom line.** Cost, controllability, on-prem deployability, reproducibility, and data sovereignty all argue for a fine-tuned BERT over a closed-weight LLM. (Detailed in Q13 of qa_kit.md.)

### Q · "Is 30,000 events per year actually the right number?"

**Bottom line.** It's the ACLED African coverage figure for recent years, consistent across 2020–2024.

**Detail.** ACLED reports between 28,000 and 35,000 African events annually since 2020 depending on data year. The thesis uses 30,000 as a round figure for the operational scale argument. The exact number is less important than the order of magnitude — tens of thousands per year, requiring thousands of analyst hours.

### Q · "What about ACLED and UCDP — they already do this."

**Bottom line.** They do, hand-coded. ACLED is the **target** of this work, not the competitor. The thesis uses ACLED data for training and aims to produce records that have ACLED-grade structure at substantially lower per-record analyst time.

**Detail.** ACLED's quality is gold-standard precisely because it's hand-coded. The cost is the bottleneck on coverage. If VioNER reduces per-article analyst time by 50 %, the same staff can cover twice as many theatres or the same number with higher reliability. This is the leverage argument.

### Q · "How does this relate to GDELT?"

**Bottom line.** GDELT operates at planetary scale with pattern-based extraction; the 5W1H structure is absent. VioNER produces records that GDELT does not.

**Detail.** GDELT is an excellent aggregator-of-news-mentions and a useful firehose for trend analysis. It is not a structured event database in the ACLED sense — its CAMEO event codes and coordinates do not capture the perpetrator–victim–action triples operational consumers need. The thesis treats GDELT as a complementary resource, not a competitor.

### Q · "Is this useful only for AU-CEWS, or more broadly?"

**Bottom line.** AU-CEWS is the primary consumer; the broader consumer set includes UCDP, OCHA, national government peace ministries, academic researchers, and civil-society early-warning groups. Slide 18 (proposed) or Q18 in qa_kit.md elaborates the three concentric consumer circles.

### Q · "What's the operational deployment path?"

**Bottom line.** Three-stage path: pilot at one AU-CEWS analyst desk (Q3 2026), head-to-head 30-day comparison study (Q4 2026), full rollout if metrics clear (2027). (Detailed in Q32 of qa_kit.md.)

### Q · "Has VioNER actually been deployed?"

**Bottom line.** Not in production. The UAT was conducted on a deployed local instance with five participants. Production deployment is recommendation 1 in §7.4 of the thesis, contingent on the three-stage adoption path.

**Detail.** A working system deployed for UAT is qualitatively different from a production-deployed system. The thesis is honest about this — the contribution is the artefact and its empirical evaluation, not a public deployment.

### Q · "What's the maintenance burden after you graduate?"

**Bottom line.** Two part-time roles. (Detailed in Q33 of qa_kit.md.)

### Q · "Aren't you just reproducing ACLED's methodology?"

**Bottom line.** No — VioNER produces records of comparable structure but via an automated pipeline that an analyst can review rather than originate. The methodology is automated NER + KB validation + UI, not hand-coded extraction.

**Detail.** ACLED's methodology produces gold-standard data by manual coding. VioNER's methodology produces first-pass automated extractions that an analyst then reviews. The output schema can be made interoperable with ACLED — making the records substitutable for ACLED's manual records in operational pipelines — but the production process is fundamentally different.

### Q · "What's the failure mode if the model misclassifies during a crisis?"

**Bottom line.** Records are produced with confidence scores and KB flags; the analyst reviews flagged or low-confidence records before they're used downstream. Recommendation 1 in §7.4 explicitly says to treat the output as a triage layer.

**Detail.** The system is not designed to be the final word on what happened. It produces records that an analyst would otherwise have produced from scratch, but faster. The analyst is the safety net; the model accelerates but does not replace.

---

# Appendix · Receipts (sources and thesis section pointers)

For panel questions of the form *"where in the thesis does it say that?"*:

| Claim | Thesis section |
|:--|:--|
| 30,000 events per year — operational scale | §1.2 motivation |
| 15-25 minutes per article — analyst time | §1.2 motivation (cites ACLED documentation) |
| 78 % O tokens — class imbalance | §2.4, §5.5 |
| 8-entity schema, dropped 18 from proposal | §4.3 |
| Grounding pilot, 80 % threshold | §4.3, §5.2 |
| Focal loss + class weights ablation | §6.6, Table 6.8 |
| VICTIM F1 0.708 → 0.817 | §6.6 |
| KB composition (150 groups, 200 cities) | §4.5, Annex C |
| KB flag rate 2.4 % | §6.7 |
| ACTOR enrichment rate 64.3 % | §6.7 |
| UAT with 5 participants, 6 tasks, Likert 4.0+ | §6.10, Table 6.10 |
| Cohen's κ = 0.78 | §5.2 |
| Macro F1 0.887, micro F1 0.909 | §6.4, Table 6.7 |
| Three iteration loops (corpus, schema, loss) | §1.5, §5.3, §6.6 |
| Recommendation: treat output as triage layer | §7.4 |
| Future work: multilingual extension | §7.5 high priority item 1 |

For panel questions of the form *"is this the published literature?"*, the key citation anchors are:

- **Focal loss** — Lin et al. 2017 ("Focal Loss for Dense Object Detection", ICCV)
- **Class-weighted training** — Cui et al. 2019 ("Class-Balanced Loss Based on Effective Number of Samples", CVPR)
- **BIO encoding** — Tjong Kim Sang & De Meulder 2003 ("Introduction to the CoNLL-2003 Shared Task", CoNLL)
- **Design science** — Hevner et al. 2004; Peffers et al. 2007
- **F1 / NER evaluation** — Tjong Kim Sang 2002 ("Introduction to the CoNLL-2002 Shared Task")
- **ACLED methodology** — Raleigh, Linke, Hegre, Karlsen 2010 ("Introducing ACLED", *Journal of Peace Research*)
- **GDELT** — Leetaru & Schrodt 2013 (paper introducing GDELT)
- **UCDP** — Pettersson et al. yearly conflict-data reports

These citations live in the References section of the thesis. You don't need to memorise them; you need to know they exist so you can say *"the canonical reference is in chapter [X] of the thesis"* if asked.

---

# One last calibration note

This problem domain is real. The numbers are real. The institutional consumers are real. The gap is real. **You are not over-stating anything.** The thesis genuinely contributes a methodologically-grounded, empirically-validated, deployable system to a domain that is currently bottlenecked. When you defend this problem statement in the room, defend it with the calm confidence of someone who built something that works on a problem that matters. The work supports the claim. Trust that, and answer accordingly.
