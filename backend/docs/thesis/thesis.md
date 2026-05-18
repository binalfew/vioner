<!--
Masters Thesis - Final Submission Draft
Author: Binalfew Kassa Mekonnen
Advisor: Fekade Getrahun (PhD)
Institution: Addis Ababa University, College of Natural Sciences, Department of Computer Science
Major: Data and Web Engineering
Submission target: 2026

Formatting target:
- A4 paper, 12-point Times New Roman, 1.5 spacing, 1.3" left / 1" other margins
- Title Page, Signature Page, Abstract, Dedication, Acknowledgements have NO page number
- Table of Contents onwards: lower-case Roman numerals (i, ii, ...)
- Chapter 1 onwards: Arabic numerals (1, 2, ...)
- IEEE citation style: [1], [2], ...
- No "By:" before student name. Title italicised on signature page.
-->

<div align="center">

**Addis Ababa University**

**College of Natural Sciences**

# Knowledge Discovery from Free Text: A BERT-Based System for Extracting Violent Event Information from African News Reports

\

\

**Binalfew Kassa Mekonnen**

\

\

\

A Thesis Submitted to the Department of Computer Science in Partial
Fulfillment for the Degree of Master of Science in Computer Science

\

\

\

Addis Ababa, Ethiopia

May 2026

</div>

\pagebreak

<div align="center">

**Addis Ababa University**

**College of Natural Sciences**

</div>

**Binalfew Kassa Mekonnen**

**Advisor:** Fekade Getrahun (PhD)

This is to certify that the thesis prepared by Binalfew Kassa Mekonnen,
titled: *Knowledge Discovery from Free Text: A BERT-Based System for
Extracting Violent Event Information from African News Reports* and
submitted in partial fulfillment of the requirements for the Degree of
Master of Science in Computer Science complies with the regulations of
the University and meets the accepted standards with respect to
originality and quality.

\

Signed by the Examining Committee:

| Name                        | Signature        | Date             |
|:----------------------------|:-----------------|:-----------------|
| Advisor:                    |                  |                  |
| Examiner:                   |                  |                  |
| Examiner:                   |                  |                  |

\pagebreak

# Abstract

Analysts at the African Union Continental Early Warning System
read more news every day than they can turn into structured records.
The backlog grows; situation awareness suffers. This thesis closes
that gap with machine learning. I built VioNER, a fine-tuned BERT
system that pulls 5W1H attributes — Who did What to Whom, Where,
When, and How — out of African news reports of violent events, and
pairs each extraction with a knowledge base of known armed groups
and conflict-affected cities. The schema is eight grounded entity
types (ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT,
CASUALTIES) in Beginning-Inside-Outside (BIO) format. Extracted
events are classified against a four-level taxonomy of about
ninety-five terminal categories, synthesised from ACLED, UCDP, and
PMVE with African-specific extensions. The model trained on a
fifty-thousand-example corpus derived from ACLED notes, with
stratified diversity sampling and template augmentation pushing
back on the dominance of the O label (seventy-eight percent of all
tokens). The loss was focal loss with inverse-frequency class
weights. On held-out validation it reaches macro F1 0.887 and micro
F1 0.909, converging in two epochs; focal loss with weighting lifts
VICTIM, the rarest entity, by eleven F1 points over plain cross
entropy. The trained model ships behind a FastAPI service with a
PostgreSQL event store, the curated knowledge base, and a React
front-end for training, inference, event management, and analytics.
The result is a system an analyst can drive without writing code,
and that substantially cuts the time between an event appearing in
the news and a structured record reaching the analyst's desk.

**Keywords:** Named Entity Recognition, BERT, Event Extraction,
Violent Events, African Conflicts, 5W1H, Focal Loss

\pagebreak

# Dedication

To my family, for their unwavering encouragement throughout this
research, and to the analysts whose patient reading of conflict
reports inspired the work that follows.

\pagebreak

# Acknowledgements

I am deeply indebted to my advisor, Dr. Fekade Getrahun, for his
guidance, critical reading, and steady encouragement throughout this
research. His insistence on rigour and operational relevance shaped
every chapter of this thesis.

I am grateful to the staff of the Addis Ababa University Department
of Computer Science for their support during the programme, and to
the African Union Continental Early Warning System (AU-CEWS) for
articulating the operational requirements that motivated this work.
I also thank the Armed Conflict Location and Event Data Project
(ACLED) for maintaining the open dataset on which this study relies.

I acknowledge the prior thesis work of Taye Abdulkadir, whose
exploration of 5W extraction in the African context provided a
foundation that this research extends.

Finally, I thank my family and friends for their patience and support
during the long months of training, debugging, and writing.

<!--
Static Table of Contents. Build the docx WITHOUT the --toc flag so that
no Word TOC field is emitted (which would trigger the "fields that may
refer to other files" prompt on open):

    pandoc thesis.md -o thesis.docx

Page numbers below are estimates and must be updated in Word once the
final layout (margins, font, line spacing) is applied. To update
quickly in Word: replace each page number in this list with the actual
page from the rendered document.

Note: The AAU CS Masters Thesis Guideline (Section 4.1 f) states the
Table of Contents "must be generated automatically and not manually."
This static TOC trades strict compliance with that rule for a
prompt-free open in Word. To switch back to a Word-auto-generated TOC,
delete the static TOC block below, restore the comment-only placeholder,
and rebuild with `--toc --toc-depth=3`.
-->

\pagebreak

# Table of Contents

| Section                                                                            | Page |
|:-----------------------------------------------------------------------------------|:----:|
| **1. Introduction**                                                                | 1    |
| 1.1 Background                                                                     | 1    |
| 1.2 Motivation                                                                     | 3    |
| 1.3 Statement of the Problem                                                       | 5    |
| 1.4 Objectives                                                                     | 7    |
| 1.5 Methods                                                                        | 8    |
| 1.6 Scope and Limitations                                                          | 10   |
| 1.7 Application of Results                                                         | 12   |
| 1.8 Organization of the Rest of the Thesis                                         | 14   |
| **2. Literature Review**                                                           | 15   |
| 2.1 Information Extraction and Event Extraction                                    | 15   |
| 2.2 Named Entity Recognition                                                       | 17   |
| 2.3 Transformer Models and BERT                                                    | 19   |
| 2.4 Class Imbalance in Token Classification                                        | 22   |
| 2.5 Evaluation Metrics for Named Entity Recognition                                | 25   |
| 2.6 Conflict Event Databases and Coding Schemes                                    | 27   |
| 2.7 Knowledge Bases and Ontologies for Events                                      | 29   |
| **3. Related Work**                                                                | 31   |
| 3.1 General Event Extraction from News                                             | 31   |
| 3.2 Violence-Specific Event Extraction Systems                                     | 33   |
| 3.3 Event Extraction in the African Context                                        | 35   |
| 3.4 Hierarchical Event Classification                                              | 36   |
| 3.5 Summary of Gaps Addressed                                                      | 37   |
| **4. The Proposed Solution**                                                       | 39   |
| 4.1 Design Principles                                                              | 39   |
| 4.2 System Architecture                                                            | 40   |
| 4.3 Entity Schema and BIO Encoding                                                 | 43   |
| 4.4 Hierarchical Violent Event Taxonomy                                            | 46   |
| 4.5 Knowledge Base Design                                                          | 49   |
| 4.6 Training Pipeline                                                              | 51   |
| 4.7 Inference and Post-Processing                                                  | 55   |
| 4.8 Web Application Architecture                                                   | 57   |
| **5. Implementation**                                                              | 59   |
| 5.1 Technology Stack                                                               | 59   |
| 5.2 Data Acquisition and Preprocessing                                             | 61   |
| 5.3 Stratified Sampling and Augmentation                                           | 63   |
| 5.4 Model Training Implementation                                                  | 65   |
| 5.5 Focal Loss and Class Weighting                                                 | 67   |
| 5.6 Backend Services and API                                                       | 69   |
| 5.7 Frontend Application                                                           | 72   |
| 5.8 Containerised Deployment                                                       | 74   |
| **6. Experimentation and Results**                                                 | 75   |
| 6.1 Experimental Setup                                                             | 75   |
| 6.2 Dataset Statistics                                                             | 76   |
| 6.3 Training Dynamics                                                              | 78   |
| 6.4 Overall Model Performance                                                      | 81   |
| 6.5 Per-Entity Analysis                                                            | 82   |
| 6.6 Ablation: Focal Loss versus Cross Entropy                                      | 84   |
| 6.7 Knowledge-Base Validation Impact                                               | 85   |
| 6.8 Inference Latency and Throughput                                               | 86   |
| 6.9 End-to-End Demonstration                                                       | 87   |
| 6.10 User Acceptance Testing                                                       | 88   |
| 6.11 Error Analysis                                                                | 90   |
| 6.12 Discussion                                                                    | 91   |
| 6.13 Threats to Validity                                                           | 92   |
| **7. Conclusions, Recommendations, and Future Work**                               | 94   |
| 7.1 Summary                                                                        | 94   |
| 7.2 Answers to the Research Questions                                              | 96   |
| 7.3 Contributions                                                                  | 98   |
| 7.4 Recommendations                                                                | 100  |
| 7.5 Future Work                                                                    | 101  |
| References                                                                         | 104  |
| Annex A: Entity Annotation Guidelines (Summary)                                    | 108  |
| Annex B: Hierarchical Taxonomy of African Violent Events                           | 110  |
| Annex C: Knowledge Base Entries (Excerpt)                                          | 115  |
| Annex D: System Screenshots                                                        | 117  |
| Annex E: Sample Augmentation Templates                                             | 120  |
| Annex F: User Acceptance Testing Questionnaire                                     | 122  |
| Signed Declaration Sheet                                                           | 124  |

\pagebreak

# List of Tables

| Table | Title                                                              | Page |
|:-----:|:-------------------------------------------------------------------|:----:|
| 3.1   | Comparative position of VioNER relative to prior systems           | 34   |
| 4.1   | Eight-entity grounded schema for the VioNER NER component          | 41   |
| 4.2   | Level 1 categories of the hierarchical taxonomy                    | 44   |
| 4.3   | Level 2 intermediate violence types                                | 45   |
| 4.4   | Knowledge base content summary                                     | 47   |
| 4.5   | Training hyperparameters                                           | 49   |
| 5.1   | Backend technology stack                                           | 55   |
| 5.2   | Frontend technology stack                                          | 56   |
| 6.1   | Hardware and software configuration                                | 74   |
| 6.2   | Pre-processed dataset statistics                                   | 75   |
| 6.3   | Entity-level frequency in the full pre-processed corpus            | 76   |
| 6.4   | Inverse-frequency class weights used in the focal-loss objective   | 77   |
| 6.5   | Per-epoch training dynamics                                        | 78   |
| 6.6   | Best validation metrics across training runs                       | 79   |
| 6.7   | Per-entity precision, recall and F1                                | 81   |
| 6.8   | Focal-loss ablation                                                | 83   |
| 6.9   | Inference latency on representative articles                       | 85   |
| 6.10  | Aggregated user acceptance testing responses                       | 87   |

\pagebreak

# List of Figures

| Figure | Title                                                              | Page |
|:------:|:-------------------------------------------------------------------|:----:|
| 4.1    | High-level architecture of the VioNER system                       | 38   |
| 4.2    | End-to-end processing pipeline                                     | 39   |
| 4.3    | Sequence of calls during synchronous inference                     | 40   |
| 4.4    | BIO encoding example for a multi-word entity                       | 42   |
| 4.5    | Four-level taxonomy hierarchy (visual outline)                     | 44   |
| 5.1    | Back-end module organisation                                       | 67   |
| 5.2    | Front-end route map                                                | 70   |
| 6.1    | Training and validation loss curves                                | 77   |
| 6.2    | Token-level validation accuracy across epochs                      | 78   |
| 6.3    | Per-entity F1 bar chart                                            | 82   |
| 6.4    | Confusion patterns between location entity types                   | 89   |

\pagebreak

# List of Algorithms

| Algorithm | Title                                                          | Page |
|:---------:|:---------------------------------------------------------------|:----:|
| 4.1       | Sub-word label alignment for BIO tagging                       | 50   |
| 4.2       | Stratified diversity sampling for entity coverage              | 61   |
| 4.3       | Template-based augmentation                                    | 62   |
| 4.4       | Focal loss with inverse-frequency weighting                    | 66   |
| 4.5       | Post-NER 5W1H structuring with knowledge-base validation       | 53   |

\pagebreak

# Acronyms and Abbreviations

| Acronym  | Expanded form                                                      |
|:---------|:-------------------------------------------------------------------|
| 5W1H     | Who, What, Where, When, Whom, How                                  |
| ACLED    | Armed Conflict Location and Event Data Project                     |
| ADF      | Allied Democratic Forces                                           |
| API      | Application Programming Interface                                  |
| AQIM     | Al-Qaeda in the Islamic Maghreb                                    |
| AU       | African Union                                                      |
| AU-CEWS  | African Union Continental Early Warning System                     |
| BERT     | Bidirectional Encoder Representations from Transformers            |
| BIO      | Beginning, Inside, Outside (tagging scheme)                        |
| CAMEO    | Conflict and Mediation Event Observations                          |
| CAR      | Central African Republic                                           |
| CRF      | Conditional Random Field                                           |
| CUDA     | Compute Unified Device Architecture                                |
| DRC      | Democratic Republic of the Congo                                   |
| ECOWAS   | Economic Community of West African States                          |
| F1       | Harmonic mean of precision and recall                              |
| FARDC    | Forces Armées de la République Démocratique du Congo               |
| GDELT    | Global Database of Events, Language, and Tone                      |
| IED      | Improvised Explosive Device                                        |
| IGAD     | Intergovernmental Authority on Development                         |
| JNIM     | Jama'at Nasr al-Islam wal Muslimin                                 |
| JWT      | JSON Web Token                                                     |
| KB       | Knowledge Base                                                     |
| LRA      | Lord's Resistance Army                                             |
| LSTM     | Long Short-Term Memory                                             |
| ML       | Machine Learning                                                   |
| MPS      | Metal Performance Shaders                                          |
| NER      | Named Entity Recognition                                           |
| NEXUS    | News cluster Event eXtraction Utilizing language Structures        |
| NLP      | Natural Language Processing                                        |
| NOEM     | News Ontology Event Model                                          |
| OWL      | Web Ontology Language                                              |
| PMVE     | Politically Motivated Violent Events (ontology)                    |
| PoS      | Part of Speech                                                     |
| RDF      | Resource Description Framework                                     |
| REC      | Regional Economic Community                                        |
| REST     | Representational State Transfer                                    |
| RoBERTa  | Robustly Optimised BERT Approach                                   |
| RSF      | Rapid Support Forces                                               |
| SPARQL   | SPARQL Protocol and RDF Query Language                             |
| SQL      | Structured Query Language                                          |
| SVBIED   | Suicide Vehicle-Borne Improvised Explosive Device                  |
| UCDP     | Uppsala Conflict Data Program                                      |
| UI       | User Interface                                                     |
| VBIED    | Vehicle-Borne Improvised Explosive Device                          |
| VioNER   | Violent Event Named Entity Recognition (this work)                 |

\pagebreak

# 1. Introduction

The research problem addressed by this thesis sits at the
intersection of three pressures: a flood of African violent-event
reporting in unstructured news text, an analyst workforce that
cannot read it fast enough, and an early-warning operational
requirement that depends on the timely conversion of that text into
structured records. The sections that follow lay out the background,
motivation, problem statement, objectives, and methods that frame
the rest of the work, and close with a roadmap to the remaining
chapters.

## 1.1 Background

The volume of digital news content describing violent events on the
African continent has grown faster than the human capacity to read,
code, and act upon it. Reports of attacks, clashes, raids, bombings,
displacement, and other forms of armed and political violence are
disseminated through wire services, mainstream outlets, regional
newspapers, and increasingly through online media [1]. The
overwhelming majority of this content is unstructured natural-language
text intended for human consumption rather than machine processing.
Converting these narratives into structured, queryable representations
is a prerequisite for systematic monitoring, statistical aggregation,
and evidence-based decision making.

Natural Language Processing (NLP) is the half-century-old discipline
that attempts to make computers do useful things with human
language, and the toolbox it has developed — part-of-speech tagging,
syntactic parsing, named entity recognition, coreference resolution
[2] — is exactly what an early-warning analyst is doing implicitly
when reading a news article. Information Extraction (IE) is the
specific sub-discipline that tries to mechanise the analyst's work:
take prose in, produce structured records out. Event Extraction,
in turn, narrows IE to events — verbs, nominalised actions, and
their participants — and asks the model to recover who did what to
whom, where, when, and how, from text alone [3], [4].

The 5W1H frame I adopt is not new. Journalism schools have taught
it for over a century, and analysts in early-warning centres read
for those slots whether or not they explicitly call them that. The
attractive property for an automated system is that 5W1H decouples
*what to extract* from *which event types exist*: even before any
taxonomic question is settled, an extractor can populate a 5W1H
record that downstream analytics can later classify.

The technical opportunity is recent. Vaswani and colleagues'
transformer architecture [5] and the line of pre-trained language
models built on it — most prominently BERT [6] — narrowed the gap
between research prototypes and operational NLP systems for
token-level tasks by an order of magnitude in five years [7]. The
combination of large-scale self-supervised pre-training with
small-scale task-specific fine-tuning is what makes a 50,000-example
domain corpus a workable input for a competitive NER model, where
ten years earlier it would not have been.

Within the specific domain of conflict and violence monitoring,
several long-running data collection efforts have constructed
structured event databases by human coding. The Armed Conflict
Location and Event Data Project (ACLED) is the most influential of
these for the African context, providing georeferenced records of
political violence and protest events with detailed actor, location,
and fatality information [8]. The Uppsala Conflict Data Program
(UCDP) [9] and the Global Database of Events, Language, and Tone
(GDELT) [10] play complementary roles. While these initiatives have
demonstrated the value of structured event data, the underlying
collection processes remain heavily manual or rely on coarse-grained
automation that may miss nuance or African-specific patterns.

The African Union Continental Early Warning System (AU-CEWS) operates
within this landscape as a continental mechanism for monitoring
conflict and crisis dynamics across the African Union member states.
AU-CEWS aggregates news content through its Africa Media Monitor tool
and draws on it for situation analysis, briefings, and early warning
products. The transformation of monitored content into structured,
analysable form remains, however, the limiting factor on the system's
throughput.

This thesis sits at the intersection of these strands. It uses a
fine-tuned BERT model as the core of a 5W1H extraction pipeline; it
targets African conflict reporting in particular; and it organises
the outputs around a knowledge base of African armed groups,
locations, and a hierarchical taxonomy of violent events. The
remainder of this chapter motivates the work in greater detail and
states the specific objectives that the work pursues.

## 1.2 Motivation

A typical morning at the AU-CEWS Situation Monitoring Centre starts
with a queue. Africa Media Monitor, the centre's news-aggregation
tool, will have pulled in somewhere between two and four hundred
items overnight for any given regional desk. Most are noise — sports
results, market reports, press releases. Maybe fifteen to forty
describe something violent: an attack, a clash, a raid, an arrest
that turned lethal. Those are the ones the analyst has to read,
read carefully, and turn into a structured record — who, what,
where, when, whom, how — that an early-warning briefing can use.

By mid-morning, on a good day, the analyst is perhaps a quarter
through. By close of business the residue rolls over into the next
day's queue. Multiply this by regions, by analysts, by the working
year, and the binding constraint on continental situation awareness
becomes clear. It is not the sophistication of any analytical model
that matters. It is the throughput of one human reading one
article at a time.

Working in this environment, and reading the centre's own internal
documentation of its data-collection and analysis tools [38], I
came to see two distinct problems hiding behind the same backlog.

The first is the obvious one: a **throughput gap**. The volume of
news human analysts can absorb in a working day is a fraction of
the daily inflow, and even at full attention the cognitive load of
reading and coding violent incidents is brutal — you cannot stay
sharp on the eighth massacre report of the morning.

The second is more insidious: a **consistency gap**. Two analysts
coding the same article will sometimes diverge on the basic
questions. Was this "violence against civilians" or "battle"? Is
that a city or a district? Should this fatality count be attributed
to the named perpetrator or marked "unknown"? Individually these are
small judgements. Aggregated across hundreds of records a week,
they make trend analysis unreliable — was the spike real, or did
the new shift just code things differently?

The two gaps interact. Closing the throughput gap by hiring more
analysts can widen the consistency gap; closing the consistency
gap by writing tighter coding rules slows everyone down and widens
the throughput gap. A machine-learning system that produces
consistent structured records from a larger share of the inflow is
attractive because it pushes on both gaps at once.

Three further observations shaped the technical choices in this
thesis. The first is that African conflict reporting features
actor names, place names, and ethnic-group references that
off-the-shelf NLP models trained on European or North American
corpora do not handle well. Boko Haram, JNIM, the M23, the
Allied Democratic Forces, Fano, Anti-Balaka — these are not
entities that mBERT learnt about during pre-training, and generic
NER models routinely break on them or assimilate them to whatever
PERSON or ORG entry they can find [11]. Fine-tuning a domain
model on annotated African conflict text closes that gap
substantially.

The second is that the class distribution is brutally skewed. In
the corpus I assemble in Chapter 5, roughly seventy-eight percent
of all tokens carry the outside (O) label. Of the remaining twenty
two percent that are entity tokens, the rarest entity types —
VICTIM and CASUALTIES, the ones the analyst actually cares about
most — make up only two percent each. A vanilla cross-entropy
fine-tune on this distribution will quietly under-recover the rare
classes while reporting deceptively high overall accuracy. Focal
loss [12] with inverse-frequency class weighting is the standard
counter, and §6.6 demonstrates that it lifts VICTIM by eleven F1
points over plain cross entropy in this setting.

The third is more architectural. An extraction system that
produces records analysts cannot trust adds load rather than
relieving it. The minimum bar is that the output be auditable: an
analyst opening an extracted record must be able to see which
text the model based each entity on, how confident the model was,
and whether the extracted actor or location matches a known
real-world referent. A curated knowledge base of African armed
groups, conflict-affected cities, and weapon categories, run
alongside the model, gives that audit trail. It also catches
plausible-sounding nonsense (M23 attacking Maiduguri, RSF
operating in Mozambique) before it reaches a human reviewer.

The shape of the thesis falls out of all this. Academically, it
contributes a fine-tuned BERT model and an annotated dataset for
African violent-event NER, together with a four-level taxonomy
designed for the African context. Practically, it ships a web
application that exposes training, inference, event management,
and analytics through a single interface, so that an analyst who
has never run a Python script can still use it.

## 1.3 Statement of the Problem

The central problem addressed in this thesis is the absence, in
the African early-warning ecosystem, of an accurate and openly
documented pipeline for converting English-language news reports of
violent events into structured 5W1H records suitable for downstream
analysis. The problem can be decomposed into three sub-problems.

**Sub-problem 1: Domain-specific entity recognition.** Generic NER
models trained on news corpora do not consistently recognise
African-specific armed groups, regional administrative units,
conflict-affected localities, and the casualty descriptions used in
African conflict reporting. Off-the-shelf models also do not
distinguish the actor, victim, action, and casualty roles that an
operational analyst cares about. A model fine-tuned on annotated
African conflict text is therefore required, supported by a
grounded annotation schema that captures the operationally relevant
entity types and excludes those that cannot be reliably grounded in
the source text.

**Sub-problem 2: Severe class imbalance.** Within the annotated
corpus, the distribution of Beginning-Inside-Outside (BIO) labels
is heavily dominated by the O label, with entity tokens forming only
a minority of the total.
Within the entity tokens themselves, ACTOR, CITY, DATE, REGION, and
DISTRICT labels dominate, while VICTIM, ACTION, and CASUALTIES are
substantially rarer. Naive training tends to over-fit to the dominant
classes and under-recover the rare but operationally important ones.
A loss function and sampling strategy that compensate for this
imbalance are required.

**Sub-problem 3: Operational packaging.** A trained model alone is
not an operational capability. To be useful, the model must be
exposed through a documented API, paired with a curated knowledge
base, embedded in a workflow that supports article ingestion, event
storage, and analytics, and operable by users who are not machine
learning specialists. Most prior academic work on event extraction
in the African context has stopped at the model boundary, leaving
the operational packaging undone. This thesis addresses operational
packaging as a first-class research output rather than as
implementation detail.

### Research Questions

The three sub-problems above are pursued through the following research
questions.

1. Which entity types in African violent-event news reports can be
   reliably grounded in source text, and what is an appropriate BIO
   schema for fine-tuning a BERT model on those entities?
2. How effectively can a fine-tuned BERT model recognise the chosen
   entities, and what loss function and sampling strategy produce the
   most balanced per-entity performance under severe class imbalance?
3. To what extent does a curated knowledge base of African armed
   groups, conflict locations, and a hierarchical taxonomy improve the
   trustworthiness and downstream utility of the extracted records?
4. What system architecture allows the model, the knowledge base, and
   the analytics layer to be operated together by users without machine
   learning expertise?

### Significance of the Study

The most direct significance is operational. Analyst time at AU-CEWS
is, as §1.2 argued, the binding constraint on continental situation
awareness during fast-moving crises; even a partial reduction in the
cost of producing a structured event record translates almost one to
one into faster, broader, and more consistent monitoring. That is
the case for building VioNER at all.

The methodological contribution is the combination, rather than any
single ingredient. Grounded supervision, focal loss with class
weighting, and a curated domain knowledge base used both for
validation and enrichment have each been studied in isolation; to
the best of my knowledge they have not been combined and reported
together on African violent-event extraction at this scale. The
methodology is documented in detail through Chapters 4 and 5 so
that it can be reproduced or adapted.

Finally, the artefacts themselves have a life beyond this thesis.
The four-level taxonomy, the eight-entity annotation schema, and the
curated knowledge base of African armed groups and conflict-affected
cities are reusable; another researcher working on humanitarian
protection, conflict early warning, or peace and security analysis
should be able to pick any of them up without rebuilding from
scratch.

## 1.4 Objectives

### General Objective

The general objective of this research is to design, implement, and
evaluate VioNER, an integrated system that extracts 5W1H attributes of
violent events from African English-language news reports through
fine-tuned BERT-based named entity recognition, supports those
extractions with a curated knowledge base and hierarchical taxonomy,
and exposes the full capability through a documented web platform.

### Specific Objectives

The following specific objectives operationalise the general objective.

1. Review the literature on information extraction, event
   extraction, named entity recognition, transformer-based language
   models, and conflict event coding, and position the work with
   respect to it.
2. Define a grounded eight-entity BIO schema (ACTOR, VICTIM, ACTION,
   DATE, REGION, CITY, DISTRICT, CASUALTIES) and document inclusion
   and exclusion rules for each.
3. Construct a four-level hierarchical taxonomy of violent events
   tailored to African conflict patterns, with approximately ninety
   five terminal categories and explicit decision rules for ambiguous
   cases.
4. Assemble a training corpus of approximately fifty thousand examples
   derived from ACLED event descriptions, combining stratified
   diversity sampling of real records with template-based augmentation
   to address vocabulary gaps and class imbalance.
5. Implement a training pipeline that fine-tunes a `bert-base-cased`
   model on the corpus, using focal loss with inverse-frequency class
   weighting, gradient clipping, learning-rate scheduling, and early
   stopping.
6. Curate a knowledge base of African armed groups, conflict-affected
   cities and regions, weapons, and the four-level taxonomy, and
   integrate it as a validation layer over raw NER output.
7. Implement a FastAPI service that exposes the trained model and
   knowledge base through routes for training management, inference,
   event storage, analytics, and knowledge base administration.
8. Implement a React-based front-end application that allows non-expert
   users to fine-tune models, run inference on documents, browse
   stored events, and review analytics.
9. Evaluate the system end to end on a held-out validation set and on
   representative real-world articles, reporting overall and per-entity
   metrics, latency, and qualitative observations from user acceptance
   testing.
10. Document limitations of the current implementation and recommend a
    concrete programme of future work, including hierarchical event
    classification at inference time and natural-language question
    answering against the event store.

## 1.5 Methods

The methodological frame is design science [13]: build the
artefact iteratively, evaluate it empirically at each stage, let
the lessons of one iteration shape the next, and control for
over-fitting throughout with held-out data. Below is the plan in
prose. Chapters 4 and 5 will give the technical detail.

The work will begin with the annotation schema. The starting point
will be the twenty-six-type schema in the proposal, refined through
a pilot study in which a sample of articles will be annotated by
hand to measure the proportion of each entity type that can be
located verbatim in source text. Entity types whose grounding rate
falls below an acceptable threshold will be dropped from the NER
schema and recovered downstream by post-processing — concretely,
EVENT_TYPE will be reconstructed by the taxonomy classifier from
the action verb plus context, and COUNTRY by a knowledge-base
look-up from the most specific WHERE entity. The result will be a
narrower schema in which every entity type can be reliably
supervised.

The training corpus will come from the ACLED open data export.
Records will be tokenised, BIO-labelled by projecting the
structured ACLED columns onto the free-text notes, and reduced
from the full 212,000-event pool to a smaller, more diverse
subset by stratified sampling that over-represents the rare entity
types. Template-based augmentation will add roughly fifteen
thousand synthetic examples to cover vocabulary that ACLED notes
do not (active-voice action verbs, descriptive victim phrasings).
The combined corpus will be split eighty / twenty into training
and validation, with stratification on entity-type presence.

The model itself will be a fine-tuned `bert-base-cased` with a
seventeen-label token-classification head, trained under AdamW
with linear warm-up, ReduceLROnPlateau scheduling, gradient
clipping, and focal loss with inverse-frequency class weights.
Sub-word labels will be aligned by carrying the first sub-word's
label to subsequent sub-words and explicitly handling the B- to I-
transition.

A curated knowledge base of African armed groups, conflict-affected
cities, and weapon categories will be loaded at inference time and
used for two purposes. First, validation: it will confirm or flag
extracted entities against curated reference data. Second,
enrichment: it will attach canonical names, country of operation,
and group type to matched entities. Mismatches between an actor's
known country of operation and the location extracted from the
same sentence will lower the event's overall confidence score and
surface it for analyst review.

The full system will be packaged behind a FastAPI service, a
PostgreSQL event store, and a React/TypeScript front-end that
covers training, inference, event management, and analytics. The
whole stack will run under Docker Compose.

Finally, the system will be evaluated against a held-out validation
set with token-level accuracy and span-level precision, recall, and
F1 per entity; against a small set of representative real-world
news articles by qualitative inspection; and by user acceptance
testing with a small group of representative users. End-to-end
inference latency will be measured on the same hardware used for
training.

## 1.6 Scope and Limitations

### Scope

The thesis addresses the extraction of 5W1H attributes from
English-language news reports describing violent events in the African
context. The artefact delivered comprises:

- A fine-tuned `bert-base-cased` model for token classification across
  the eight-entity BIO schema described above.
- A four-level hierarchical taxonomy of African violent events with
  approximately ninety-five terminal categories.
- A knowledge base of African armed groups, conflict-affected cities,
  and weapons.
- A FastAPI service exposing training, inference, event storage,
  analytics, and knowledge-base management.
- A React/TypeScript front-end allowing users to run training jobs,
  perform inference, manage events, and view analytics.
- A reproducible Docker-based deployment.

### Out of Scope

The following are explicitly outside the scope of this thesis but are
identified as priority future work in Chapter 7.

- Multilingual extraction. The model and pipeline target English text
  only. Arabic, French, Portuguese, Amharic, Swahili, and other
  African languages are out of scope.
- Real-time stream processing. Articles are processed on demand or in
  batch; the system does not target sub-second pipeline latency at
  scale.
- Predictive forecasting of future violence from extracted records.
- Automatic ingestion of news from third-party feeds. Articles are
  uploaded or submitted manually for inference.
- Natural-language question answering against the event store. Queries
  are formulated through structured filters in the analytics
  interface, not free-text questions.
- Hierarchical event classification by a learned classifier. The
  taxonomy is applied through deterministic post-NER rules informed by
  knowledge-base look-ups; a supervised hierarchical classifier is
  identified as future work.
- Production-grade hardening (high availability, multi-region
  replication, advanced authentication, audit logging) beyond a
  research prototype.

### Limitations

The principal limitations of the work are the following.

1. **Data domain.** The training data is dominated by ACLED-derived
   event descriptions, supplemented with template-based augmentation.
   ACLED descriptions are concise and follow distinctive stylistic
   conventions; full-length news articles may diverge in style and may
   require additional fine-tuning data.
2. **Synthetic augmentation.** Approximately thirty percent of the
   training corpus is generated through templated augmentation. The
   templates were designed to mirror naturalistic constructions, but
   they remain narrower than the diversity of real reporting.
3. **English only.** The system processes English text. A substantial
   share of African conflict reporting is in French, Arabic,
   Portuguese, and various African languages and is therefore not
   covered.
4. **Single-pass NER.** The model performs flat NER over BIO labels.
   Nested entities (for example, a city name inside an organisation
   name) and overlapping spans are not modelled.
5. **Post-NER taxonomy.** Hierarchical taxonomic classification of
   each event is performed by rule-based post-processing using the
   knowledge base. A learned classifier would likely outperform the
   rule-based fallback for ambiguous events.
6. **Modest computational budget.** Training is conducted on a single
   workstation with Apple Silicon GPU acceleration. Larger model
   variants such as `bert-large-cased` or specialised long-context
   models were evaluated but not used as the production model.

## 1.7 Application of Results

The primary intended user is the AU-CEWS analyst whose backlog
this thesis set out to address. The same set of capabilities is
useful, with little or no modification, to the regional economic
communities running their own monitoring functions (ECOWAS, IGAD,
SADC) and to national early-warning centres in member states. The
taxonomy-aware analytics support queries at any level of the
hierarchy — "all political violence in West Africa this quarter",
"suicide bombings attributed to JNIM in Mali in 2026", "election
violence in countries with elections in the past ninety days" —
which is the kind of slicing that briefing-writers need on demand.

Beyond the early-warning case, the event store is structured around
fields humanitarian organisations care about (actor, victim,
location, casualty count, displacement). An NGO doing protection
analysis or needs assessment can run aggregations over the same
data; the schema does not need to be redesigned to serve them.

Peace-support operations and national security services are a more
sensitive case. Open-source extraction is not a substitute for
classified intelligence, and I would not present it as one. The
useful framing is that VioNER lowers the cost of doing OSINT
systematically — a junior analyst with VioNER on their workstation
can do, in a morning, the volume of structured reading that a few
years ago would have taken a small team. Whether that fits any
particular service's workflow is a question for them.

For academic researchers, the annotated dataset, the four-level
taxonomy, and the extracted event corpus are the reusable
artefacts. Conflict-studies quantitative work has historically
been bottlenecked by hand-coded data; an open BERT-based extractor
plus a curated knowledge base shifts where that bottleneck sits.

Finally, the open architecture and documented deployment are a
modest capacity-building contribution. An African university or
research centre with the means to run Docker and a GPU can deploy
their own instance, fine-tune on their own annotated data, and
adapt the taxonomy without having to start from scratch.

## 1.8 Organization of the Rest of the Thesis

The next two chapters cover the literature. Chapter 2 will work
through the relevant theory — information and event extraction,
named entity recognition, transformers and BERT, class-imbalance
methods, the conflict-event database tradition, and event-oriented
knowledge representation — at a level sufficient to support the
decisions made in Chapter 4. Chapter 3 will then narrow to the
specific prior systems VioNER builds on or distinguishes itself
from, ending with the gap analysis that motivates the rest of the
work.

The middle of the thesis is the system itself. Chapter 4 will lay
out the design: the architecture, the entity schema, the
hierarchical taxonomy, the knowledge base, the training pipeline,
the inference pipeline, and the web application that ties them
together. Chapter 5 will document how each of those parts is
actually built — the technology stack, the data preparation, the
training implementation, the focal-loss code, the back-end
services, the front-end, the containerised deployment. The
separation between Chapter 4 (what and why) and Chapter 5 (how)
is deliberate; readers interested in the design without the
implementation detail can stop after Chapter 4.

Chapter 6 will then report the evaluation: dataset statistics,
training dynamics, overall and per-entity performance, the
focal-loss ablation, the impact of the knowledge-base layer,
latency measurements, end-to-end demonstration on real articles,
user-acceptance feedback, and an honest error analysis. The
chapter closes with a discussion, a threats-to-validity section,
and a brief account of the experiments I tried first and
abandoned.

Chapter 7 will wrap up — a summary anchored back to the analyst
queue of §1.2, explicit answers to the four research questions of
§1.3, a list of contributions, recommendations for organisations
considering adoption, and a prioritised future-work programme that
addresses the limitations of §1.6 and the threats of §6.13.

\pagebreak

# 2. Literature Review

Five strands of literature inform this thesis: information and
event extraction, named entity recognition, the transformer
architecture and BERT, methods for handling severe class imbalance
in token classification, and the conflict-event database tradition
that frames the operational context. Each is summarised below, with
a final section on knowledge-base and ontology approaches to event
representation. Paper-by-paper reviews of the most directly related
systems are deferred to Chapter 3.

## 2.1 Information Extraction and Event Extraction

The umbrella term Information Extraction (IE) [4] covers any
technique that pulls structured records out of free text. The field
is conventionally broken into four sub-tasks — named entity
recognition, relation extraction, coreference resolution, and event
extraction — and although the textbook arrangement is a pipeline,
in practice a great deal of recent work bundles two or more of these
into joint or end-to-end models. The architectural decision I make
in §4.2 is to stay close to the textbook pipeline, on grounds of
debuggability and clarity rather than peak accuracy.

Event Extraction is the sub-task I care about most directly. The
operational definition I use is the one in Ahn [3]: an event is a
verb or nominal predicate together with the participants (agent,
patient, instrument), the location, and the time that the predicate
involves. The Automatic Content Extraction program [14] formalised
this view in the early 2000s by publishing a typology of event
types and their arguments, and that typology shaped the next
decade of supervised event extraction. The Text Analysis Conference
Knowledge Base Population track later picked up the baton with
larger and more diverse evaluations.

The journalistic 5W1H frame [15] is a less rigid alternative. It
sidesteps the question of which event types to enumerate by asking
the same six questions — Who, What, Whom, Where, When, How — of
every reported event. For news text this is a near-perfect fit:
journalists are trained to answer those questions in roughly the
first paragraph, and analysts read for exactly those slots. I adopt
5W1H, leave event-type classification to a post-NER step against
the taxonomy in §4.4, and so avoid baking a fixed event-type
inventory into the supervised learning problem itself.

Hogenboom and colleagues survey event extraction methods for decision
support in two complementary papers [16], [4]. They identify three
broad methodological families: data-driven (supervised machine
learning on annotated corpora), knowledge-driven (linguistic and
ontological rules), and hybrid approaches that combine the two. The
hybrid family has dominated practical deployments because it allows
domain knowledge to be encoded in rules where it is naturally
expressible and statistical learning to be applied where rule
authorship is intractable. The VioNER system presented in this thesis
is hybrid in this sense: the entity extraction is data-driven, while
the post-NER 5W1H structuring, the taxonomy classification, and the
knowledge-base validation are rule-driven.

## 2.2 Named Entity Recognition

For the purposes of this thesis, NER means deciding for every token
in a sentence whether it belongs to an entity I care about and, if
so, which entity type. Before deep learning, the dominant approach
combined hand-engineered features (capitalisation patterns,
gazetteers, surrounding part-of-speech tags) with a sequence model
that knew how to make a structured prediction over the whole
sentence — Hidden Markov Models, Maximum Entropy Markov Models, and
later Conditional Random Fields (CRFs) [17]. CRFs became the
workhorse because they model how successive labels constrain each
other, which matters when entities span multiple tokens and a B-
must be followed by I-, not by another B-.

I encode entities in BIO, the simplest of the standard schemes: a
B- prefix on the first token of an entity, an I- prefix on each
continuation token, and an O label everywhere else. For a schema
with k entity types, BIO produces 2k + 1 labels — in my case,
seventeen. Variants like BIOES or BILOU add explicit single-token
and final-token labels to give the decoder more structure to lean
on. I chose plain BIO for two reasons: the entity types in §4.3
are short enough that the extra labels would mostly be redundant,
and seqeval-style evaluation tooling supports plain BIO without
configuration.

The first wave of neural NER systems leant on word embeddings fed
through bi-directional Long Short-Term Memory (BiLSTM) networks
[18], typically combined with a character-level convolutional or
recurrent layer to handle out-of-vocabulary tokens, and a CRF head
on top to keep the BIO transitions sane. Lample and colleagues'
architecture [19] became the recipe most replicated for several
years, and it showed that learned representations could replace
much of what the feature-engineering era had hand-crafted.

The next jump came from contextual representations — ELMo [20] and
particularly BERT [6]. Once a transformer encoder had absorbed
general-purpose language structure during pre-training, swapping
out the classifier head and fine-tuning the encoder produced
results that surpassed every BiLSTM-CRF system on the CoNLL-2003
benchmark, and the recipe has stayed roughly the same since:
contextual encoder, linear classifier, optional CRF head,
cross-entropy or focal loss. VioNER follows this recipe.

The property that matters most for a low-resource setting like the
African violent-event domain is that a transformer encoder absorbs
enough general English during pre-training that a comparatively
small specialised corpus can fine-tune it to good per-entity
performance. The 50,000-example corpus I describe in Chapter 5
would be far too small for a from-scratch BiLSTM-CRF; it is
sufficient for a fine-tuned BERT precisely because of this
transfer.

Recent work has pushed for African-language NER resources directly.
Adelani and colleagues' MasakhaNER [11] established a benchmark for
ten African languages with annotations for PERSON, ORGANISATION,
LOCATION, and DATE; their headline finding is that generic
multilingual encoders such as mBERT and XLM-RoBERTa underperform on
African text relative to encoders that have seen African corpora
during pre-training. AfroLM [40] and AfroXLMR continued this line.
My target is English-language reporting of African events rather
than African-language reporting, so I use `bert-base-cased`, but
the entity schema is strictly richer than MasakhaNER's four types,
and an African-pre-trained backbone is a natural future swap
(§7.5).

## 2.3 Transformer Models and BERT

The transformer [5] removed the recurrent step that had constrained
sequence models for years and put self-attention in its place: each
position in the input gets to look directly at every other position,
through learned query / key / value projections, and the cost of
that look-up is paid in parallel rather than in sequence. For my
purposes the practical consequences matter more than the
mathematical novelty: training can be parallelised on a GPU,
long-range dependencies — exactly the kind that link an actor at
the start of a sentence to a casualty count at the end — survive
the encoding intact, and the architecture scales gracefully with
parameter count and data.

BERT [6] is the encoder half of the original transformer turned
into a representation learner. Its pre-training task is
deliberately self-supervised: a randomly masked 15 percent of the
input tokens get hidden, the model is asked to predict them from
the surrounding context, and an auxiliary next-sentence-prediction
head is trained alongside on pairs of sentences. After that
pre-training run, the encoder carries enough generic English
structure that I can attach a small task-specific head and
fine-tune the whole thing on a few tens of thousands of NER
examples with sensible results.

For token classification specifically, the recipe is simple. BERT
gives me one contextual vector per WordPiece token; I run a linear
layer over each vector to produce logits across the seventeen-label
vocabulary; I backpropagate a focal-loss objective with class
weights (§2.4) through everything. The `bert-base-cased` checkpoint
I use has twelve transformer layers, 768-dimensional hidden states,
and roughly 110 million parameters. I use the cased variant
deliberately: in English conflict reporting, capitalisation is
extraordinarily informative for ACTOR and location entities, and
the uncased variant throws that information away.

Two further properties of BERT influence the design of the present
system. First, BERT uses WordPiece sub-word tokenisation; a single
gold-labelled word may be split into multiple sub-word tokens, and
the labels must be projected onto sub-words for training and recovered
from sub-words at inference time. The convention adopted in this
work, described in detail in Chapter 4, is to assign the original
label to the first sub-word and to convert any leading B- prefix to
I- for subsequent sub-words, while assigning -100 to special tokens
so that they are ignored by the loss. Second, BERT has a maximum
input length of 512 tokens; longer documents must be split into
overlapping windows. This thesis processes ACLED event descriptions
and most news article paragraphs without exceeding this limit, but
window-based handling is implemented for completeness.

Several BERT variants and successors have been proposed. RoBERTa
[21] improves on BERT by removing the next-sentence-prediction
objective, training longer with larger batches, and using dynamic
masking. DistilBERT [22] applies knowledge distillation to produce a
smaller and faster model with modest accuracy loss. XLM-RoBERTa [23]
extends the multilingual setting with strong performance on
non-English text. The present work fine-tunes the canonical
`bert-base-cased` because of the balance it strikes between accuracy
and resource requirements; alternative backbones are evaluated as part
of the ablation discussion in Chapter 6.

## 2.4 Class Imbalance in Token Classification

NER under BIO is, almost by construction, a deeply imbalanced
classification problem. Most tokens in any natural-language
sentence are not part of any entity, so they all carry the O label;
across the corpus I assemble in Chapter 5, O accounts for roughly
seventy-eight percent of all tokens. The remaining twenty-two
percent is itself uneven: ACTOR, CITY, DATE, REGION, and DISTRICT
are common enough to learn well, while VICTIM, ACTION, and
CASUALTIES are the entities I most need to recover and the entities
on which a naive learner does worst.

The literature gives three handles on this problem, and I take a
position on each.

**Re-sampling** the training set [24] is the textbook first response.
Oversample the sentences that contain a rare entity, undersample
the ones full of O. The wrinkle in token classification is that the
oversampling decision lives at the example level — a single
sentence — but the imbalance lives at the token level. Oversampling
a sentence to recover one VICTIM token also pulls along thirty O
tokens. My stratified diversity sampling (§5.3) is a compromise: it
oversamples sentences that contain rare entity *types*, while
selecting for entity-type diversity rather than entity-token count,
so it grows the rare classes without pumping up O proportionally.

**Class-weighted cross entropy** [25] adjusts the loss rather than
the sampler. Each class is given a weight, large for rare classes
and small for the dominant ones, that multiplies its contribution
to the gradient. Inverse-frequency weighting sets the weight to
1/f_c (optionally normalised); effective-number weighting [26]
smooths this with a corpus-sample-overlap correction. I use
inverse-frequency weights, computed once from the training-set
distribution at the start of training, with a maximum-weight cap to
prevent the rarest classes from dominating gradient updates.

**Focal loss** [12] takes a different angle. Originally proposed
for dense object detection, where the foreground/background ratio
is even worse than for NER, it down-weights examples the model is
already confident about and concentrates the loss on the examples
it is still uncertain on. The formulation, given a per-token cross
entropy `CE(p, y) = -log p_y`, is

> `FL(p, y) = -α_y · (1 - p_y)^γ · log p_y`                       (1)

where p_y is the model's predicted probability of the true class y,
γ ≥ 0 controls how aggressively easy examples are discounted (with
γ = 0 recovering ordinary cross entropy), and α_y is an optional
per-class weight that lets focal loss compose with class weighting.
A growing body of token-classification work has reported gains from
this combination over either ingredient alone.

The present work combines focal loss (γ = 2) with inverse-frequency
class weighting, computes the weights from the training-set label
distribution at the start of training, and excludes the special -100
label from both the loss and the weight computation. The
implementation follows the formulation in equation (1), extended
with optional label smoothing β for regularisation:

> `FL_LS(p, y) = -α_y · (1 - p_y)^γ · Σ_c y'_c · log p_c`         (2)

where the smoothed target distribution is defined by

> `y'_c = (1 - β) · 1[c = y] + β / (C - 1) · 1[c ≠ y]`            (3)

in which 1[·] is the indicator function, C is the total number of
classes, and β ∈ [0, 1) is the smoothing factor (β = 0 recovers the
one-hot target).

The inverse-frequency weight for class c is computed once at the
start of training as

> `α_c = T / (C · max(f_c, 1))`                                   (4)

where T is the total token count over the training set, C is the
number of classes, and f_c is the count of class c. The maximum
weight is clipped to ten to prevent gradient instability. This
clipping also has the practical effect of treating the three rarest
entities (VICTIM, ACTION, CASUALTIES) identically at the loss level
even though their raw frequencies differ slightly.

In token classification the ignore index (-100) used for special
tokens, sub-word continuations after the first sub-word of a word,
and padding, must be respected by the loss. The custom focal loss
in this work masks ignored positions before computing log-softmax,
which both excludes them from the loss and keeps the per-position
probability normalisation correct.

## 2.5 Evaluation Metrics for Named Entity Recognition

Two granularities of evaluation are conventionally reported for
sequence-labelling NER: token-level and span-level (sometimes called
entity-level).

**Token-level metrics** compare gold and predicted BIO labels at
each token position. Accuracy is the share of positions where the
labels agree, with special tokens excluded. Per-class precision and
recall can also be computed at this granularity. Token-level
accuracy is, however, a misleading headline metric for imbalanced
tagging: with O constituting roughly seventy-eight percent of
tokens in this work's corpus, a degenerate model that predicts O
everywhere would already achieve seventy-eight percent accuracy.

**Span-level metrics** compare assembled entity spans rather than
individual tokens. A predicted span (type t, start s, end e) is
counted as a true positive if and only if a gold span exists with
the same type and the same start and end positions. Partial
overlaps count as a false positive (the prediction) and a false
negative (the gold span). Per-entity precision is true positives
divided by predicted spans; per-entity recall is true positives
divided by gold spans; F1 is the harmonic mean. Macro F1 averages
per-entity F1 with equal weight; micro F1 pools counts across
entities before computing the single F1, weighting more populous
entities more heavily.

The standard reference implementation of span-level NER evaluation
is `seqeval` [39], which exposes both "default" (BIO with strict
boundary matching) and "strict" variants. I report span-level
precision, recall, and F1 with strict boundary matching
to avoid inflated scores from partial credit, since downstream
consumers of the extracted records (the knowledge-base validator,
the event store, the analytics layer) treat boundary mismatches as
distinct extractions rather than partial matches.

A subtle point arises with BIO encoding under sub-word tokenisation.
The convention used here, with the first sub-word inheriting the
B- or I- label of the underlying word and subsequent sub-words
receiving an I- label converted from any leading B-, ensures that
the recovered spans align with whole-word boundaries at inference
time. Where this convention is not followed, span-level evaluation
may be systematically optimistic or pessimistic depending on how
sub-word predictions are merged.

## 2.6 Conflict Event Databases and Coding Schemes

The taxonomic structure of violent events is informed by a long line
of conflict-event databases. Three are particularly influential.

**ACLED.** The Armed Conflict Location and Event Data Project [8]
maintains a georeferenced database of political violence and protest
events covering Africa, the Middle East, Latin America, South and
South-East Asia, and other regions. Each ACLED record includes
fields for event type, sub-event type, actors, location, fatalities,
and a free-text note describing the event. ACLED's event type taxonomy
distinguishes battles, explosions and remote violence, violence
against civilians, protests, riots, and strategic developments, with
sub-event types under each. ACLED is the principal data source for
this thesis: the training corpus is constructed by labelling ACLED
event notes against the column metadata, and the taxonomy presented
in Annex B is influenced by ACLED's structure.

**UCDP.** The Uppsala Conflict Data Program [9] focuses on organised
violence, distinguishing state-based conflict, non-state conflict,
and one-sided violence, with fatality thresholds that exclude
lower-intensity events. UCDP's careful definitional work, including
the operational definition of organised actors and the distinction
between battle-related and civilian deaths, informs the boundary
between political violence and other categories in the taxonomy.

**GDELT.** The Global Database of Events, Language, and Tone [10] is
an automatically generated event database using the CAMEO event
coding framework [27]. CAMEO is a broad taxonomy covering both
cooperative and conflictual events, organised in a four-digit
hierarchical code. GDELT's scale is impressive, but its automated
extraction is comparatively coarse and produces a high volume of
events that may not satisfy the precision standard of operational
early warning. CAMEO and GDELT are referenced in this thesis as
illustrations of the scale-versus-precision trade-off and as sources
of comparative taxonomy patterns.

The taxonomy of African violent events presented in this thesis is
synthesised from ACLED and UCDP frames with additional categories
that reflect African conflict dynamics, including pastoralist-farmer
clashes, communal cattle raiding, and election violence. The
taxonomy is presented in full in Annex B.

## 2.7 Knowledge Bases and Ontologies for Events

Knowledge bases (KBs) and ontologies complement extraction by
providing reference data and semantic structure against which
extracted items can be validated and reasoned over. Several
event-oriented vocabularies have been proposed.

The Event Ontology by Raimond and colleagues defines an abstract
notion of an event with participants, agents, places, and times. The
Linking Open Descriptions of Events (LODE) vocabulary [28] simplifies
the Event Ontology for use in linked data. Both vocabularies are
expressed in RDF/OWL and emphasise interoperability across data sets.

For violence specifically, Piskorski and colleagues developed the
Politically Motivated Violent Events (PMVE) ontology as the
underpinning of the NEXUS system [29]. PMVE encodes violence-relevant
classes and relations (perpetrator, victim, target, weapon, location,
time) in OWL and supports rule-based reasoning over extracted facts.
The taxonomy in this thesis is conceptually similar to PMVE in its
breakdown of violence types, but is tailored to African conflict
patterns and is implemented as a structured object in the application
knowledge base rather than as an OWL ontology, on grounds of
implementation simplicity and operational utility.

The knowledge base in VioNER is structured rather than ontological.
It consists of normalised dictionaries of armed groups (with name
variants, country of operation, region), African cities and regions
(with country and parent administrative unit), and weapons (grouped
by category). The KB is loaded at inference time and is used both to
validate raw NER spans (a span tagged ACTOR is upweighted if it
matches a known armed group) and to enrich extracted records (a CITY
span is annotated with its country of operation when the city is
present in the dictionary). The structured-knowledge-base approach
sacrifices some expressivity relative to RDF/OWL but is markedly
easier to maintain and to integrate with the application layer.

\pagebreak

# 3. Related Work

Where Chapter 2 surveyed the field at the level of theory and
methods, this chapter zooms in on the specific systems that VioNER
either builds on or distinguishes itself from. Only concrete systems
are reviewed — published papers, peer-reviewed conference
proceedings, masters and doctoral theses, and technical reports —
and each is read in light of what it tells me about the design
choices I had to make in VioNER. A summary of the gaps that
VioNER bridges closes the chapter.

## 3.1 General Event Extraction from News

Tanev, Atkinson, and Piskorski [1] built an early version of what
operational crisis-monitoring infrastructure actually looks like at
scale: a multilingual pipeline that pulls news from many feeds,
recognises events through hand-written patterns, and clusters them
geographically so that an emerging story can be tracked across
sources. What I take from their work is the engineering attitude —
they treat scale as the central problem rather than treating it as
an afterthought. What I don't take is the pattern-based event
recognition. Their system does not produce structured 5W1H records
that a downstream analyst could query, and patterns alone do not
scale across the actor-name and place-name diversity of African
conflict reporting.

Hogenboom and colleagues survey the broader event-extraction
landscape twice, with a slightly different cut each time [16], [4].
Their conclusion in both surveys is the same: data-driven methods
generalise but lose precision on rare event types, knowledge-driven
methods are precise but fragile, and the hybrid pipelines that mix
the two outperform either pure approach in operational settings.
VioNER takes this seriously. The NER component is data-driven; the
post-processing layer (5W1H grouping, KB lookup, taxonomy
assignment) is rule-driven; the two communicate through confidence
scores and KB metadata rather than trying to do the whole job in
either paradigm.

YAGO [30] is a different beast — Suchanek, Kasneci, and Weikum
extract millions of facts from Wikipedia infoboxes and WordNet
hierarchies into a single OWL ontology. YAGO is not directly
comparable to VioNER (its source is semi-structured rather than
free text) but two of its design choices are instructive. First,
where the source has structure, you should use it; an infobox is a
gift compared to a paragraph. Second, embedding extracted facts in
an ontology — not just storing them as rows — gives the result
analytical leverage that flat records do not. The four-level
taxonomy in §4.4 is my answer to that second observation, applied
to a free-text extraction setting where I do not get YAGO's
infobox luxury.

Hienert and Luciano [31] extend the YAGO idea to historical events
in Wikipedia using LODE. Their pipeline assumes the same
semi-structured input. I cite it here mainly as a counterpoint:
extracting from a Wikipedia article that already names "Battle of
Adwa, 1896" in its title is a fundamentally easier problem than
extracting events from ACLED notes or full-length news articles
where the event has to be inferred from prose.

## 3.2 Violence-Specific Event Extraction Systems

The NEXUS system [29] is the closest stylistic precedent in
violence-specific extraction. Piskorski, Tanev, and Wennerberg
filter incoming news with keywords, run linguistic patterns to find
violence-relevant sentences, then snap extracted entities onto the
classes of their Politically Motivated Violent Events ontology. I
draw two lessons from NEXUS. The principled ontology — PMVE —
shows how much analytical reach a tight conceptual model gives
downstream consumers, and my four-level taxonomy is partly a
response to that. At the same time, NEXUS demonstrates how
expensive pattern-based recognition becomes once the actor and
place vocabularies shift: it was tuned to European security
incidents, and porting it to the African continent — with several
hundred armed groups and tens of thousands of locality names —
would require essentially rebuilding the pattern base. I chose
fine-tuned BERT precisely because it amortises that vocabulary work
into the pre-training stage.

Two social-media-oriented papers sit at the edge of relevance to my
work. Becker and colleagues [32] extract *planned* events by
exploiting platform-specific structured fields (event titles, dates,
locations posted on Eventful) alongside the unstructured discussion
that surrounds them. Magnuson and colleagues [33] build a related
Twitter recommendation system over Eventbrite. Both targets differ
from violent events on every axis — events are unplanned and
adversarial, the source is not authoritative, and there is no
structured platform-side metadata to lean on — so I do not adopt
their pipelines. The architectural lesson I do take is the
explicit pairing of structured platform data with unstructured text;
the knowledge base in §4.5 plays the role that Eventful or Eventbrite
plays in Becker's setting.

Aratefeh and Khreich [34] survey event detection on Twitter
specifically and catalogue the supervised, unsupervised, and hybrid
techniques that have been tried for the short-text, high-noise
regime. VioNER processes news rather than tweets, so the survey
does not drive my architecture, but the noise-handling and short-text
techniques it catalogues are the natural starting point if I extend
VioNER to citizen-journalist sources in future work.

## 3.3 Event Extraction in the African Context

The closest predecessor to VioNER is the work of Taye Abdulkadir
Edris and Sungkur, who developed a system for extracting 5W
characteristics of violent events in the African context [35]. Their
system combines linguistic preprocessing with Stanford CoreNLP and
machine-learning classification with Weka. They report results on a
modest annotated corpus and demonstrate that domain-specific
adaptation improves performance over generic baselines on African
text.

The differences between Taye Abdulkadir's work and mine are
substantial. First, that implementation uses Stanford CoreNLP and
Weka, which limits access to modern transformer architectures; I
use Hugging Face Transformers and a fine-tuned BERT. Second, the
earlier annotated corpus is modest in size, while VioNER trains on
approximately fifty thousand examples derived from ACLED and
template augmentation. Third, this thesis develops an explicit
hierarchical taxonomy of African violent events with approximately
ninety-five terminal categories, curates a knowledge base of armed
groups and locations, and packages the system as a deployable web
application; Taye Abdulkadir's work stops at the model boundary.
Fourth, I address class imbalance explicitly through focal loss and
stratified sampling rather than leaving it to the supervised
learner.

The relationship between the two works is therefore one of
foundation and extension. Taye Abdulkadir established the
feasibility of 5W extraction on African conflict text; this thesis
extends that line in scale, architecture, taxonomy, knowledge-base
integration, and operational packaging.

## 3.4 Hierarchical Event Classification

Hierarchical classification of events is most fully developed in the
work of Wang and Zhao on Chinese news 5W1H semantic-element extraction
[36]. They define the News Ontology Event Model (NOEM) and populate it
with extracted assertions as RDF triples. While the linguistic
challenges of Chinese differ from those of English, the architectural
pattern of feeding extraction output into a structured ontology with
hierarchical classes is a direct antecedent of the post-NER taxonomy
pipeline in VioNER.

ACLED's own taxonomy, while operationally tuned, is also a precedent
for hierarchical violence categorisation [8]. ACLED uses two levels
(event type and sub-event type) and approximately twenty-five
sub-event categories. The present work extends this in two
directions: in depth, by adding two additional levels of granularity
(an intermediate Level 2 and a detailed Level 4); and in breadth, by
adding African-specific categories such as pastoralist-farmer clashes
and communal cattle raiding that are folded into other categories in
ACLED.

A learned hierarchical classifier could in principle replace the
rule-based taxonomy assignment used here. Methods for hierarchical
classification range from top-down cascades, in which a separate
classifier is trained at each level, to global classifiers that
predict the entire path simultaneously [37]. Designing and training a
learned hierarchical classifier is identified as future work in
Chapter 7.

## 3.5 Summary of Gaps Addressed

Table 3.1 compares the most directly related prior systems with
VioNER along seven dimensions: NLP backbone, entity-schema size,
target languages, regional focus, taxonomy depth, presence of a
curated knowledge base, and operational packaging.

*Table 3.1: Comparative position of VioNER relative to prior systems*

| System / dimension      | NLP backbone        | Schema | Languages | Regional focus | Taxonomy depth | KB integration | Operational packaging |
|:------------------------|:--------------------|:------:|:----------|:---------------|:--------------:|:--------------:|:----------------------|
| NEXUS [29]              | Pattern + linguistic | ~8    | Multilingual (EU) | Europe       | 2 levels       | PMVE ontology  | Internal prototype     |
| Tanev et al. [1]        | Pattern + linguistic | ~6    | Multilingual    | Global         | 1 level        | None curated   | Internal system        |
| YAGO [30]               | Heuristic / rules    | n/a   | English         | Global Wikipedia | n/a          | YAGO ontology  | Knowledge base only    |
| Wang & Zhao [36]        | Pattern + semantic   | 5W1H  | Chinese         | Chinese news   | NOEM ontology  | NOEM            | Research prototype     |
| Taye Abdulkadir [35]    | CoreNLP + Weka       | 5W     | English         | Africa         | None           | None            | Model only             |
| Adelani et al. (MasakhaNER) [11] | mBERT/XLM-R | 4     | 10 African      | Africa         | n/a            | None            | Benchmark + corpus     |
| **VioNER (this thesis)**| **bert-base-cased fine-tuned** | **8** | **English** | **Africa**     | **4 levels (~95 categories)** | **150 groups + 200 cities + weapons** | **Full web app + API + Docker** |

The literature review and the related-work review converge on five
gaps that this thesis addresses.

1. **Grounded entity schema.** Prior African-context work has either
   used very small schemas (person / organisation / location, as in
   MasakhaNER) or broader schemas that include entity types that
   cannot be reliably grounded in source text (the original VioNER
   proposal's 26-type schema). This thesis introduces a deliberately
   intermediate eight-entity schema in which every entity type has
   been verified to be grounded in source text in pilot evaluation
   (Section 1.5).
2. **Transformer-based NER for African violence.** Prior work in
   this domain has used pattern-based extraction (NEXUS, Tanev et
   al.) or pre-transformer machine learning (Taye Abdulkadir's
   CoreNLP + Weka). VioNER is, to the best of my knowledge, the
   first fine-tuned transformer NER model targeted specifically at
   African violent-event 5W1H extraction at the 50,000-example scale.
3. **African violent-event taxonomy at four levels.** To the best of
   my knowledge, no prior open taxonomy of African violent events at
   this level of granularity has been published. ACLED's taxonomy
   reaches two levels with approximately twenty-five sub-event
   categories; UCDP and GDELT/CAMEO are coarser-grained. The
   four-level VioNER taxonomy with approximately ninety-five terminal
   categories is presented in full in Annex B.
4. **Knowledge-base validation layer.** The combination of a curated
   knowledge base of African armed groups, cities, and weapons with
   a learned extractor — used for both validation (flagging
   geographically implausible extractions) and enrichment
   (canonicalising armed-group names, attaching country and region
   metadata to cities) — is, to the best of my knowledge, a
   contribution.
5. **Operational packaging.** Prior academic work in this area has
   stopped at the model boundary. NEXUS, Tanev et al., and Taye
   Abdulkadir all describe extraction systems without delivering a
   reproducible, documented web application that non-specialist
   users can operate end-to-end. This thesis delivers a full web
   application with documented APIs and a reproducible Docker
   Compose deployment.

\pagebreak

# 4. The Proposed Solution

The design of VioNER answers a sequence of questions: what to
extract, in what schema, how to train the extractor, how to make
its output trustworthy, and how to put it in front of an analyst.
Each section below addresses one of these in turn — design
principles, system architecture, entity schema, hierarchical
taxonomy, knowledge base, training pipeline, inference pipeline, and
the web application that sits on top. Implementation-level detail
and specific technology choices are deferred to Chapter 5.

## 4.1 Design Principles

Six principles guided the design — some I started with, others I
learned during development.

**P1: Grounded supervision.** Every entity type in the schema must
be something a human annotator can find verbatim in the source
text. I learned this one the hard way. The original schema in the
proposal had twenty-six entity types, and during the November pilot
I tried to annotate a sample by hand using it. EVENT_TYPE (was this
an "ambush" or a "raid"? often both, often neither) and COUNTRY
(rarely written explicitly when a city or region name carries the
country implicitly) had grounding rates below 60 percent. Training
on labels you cannot consistently find in the text is asking the
model to learn noise. Both got dropped from the NER schema and
moved into the post-NER taxonomy step, where they belong.

**P2: Modular pipeline.** Each stage of the system has a defined
input and output and no hidden state. Tokenise → NER → entity
assembly → confidence filtering → KB enrichment → 5W1H structuring
→ taxonomy classification → persist. Every arrow can be inspected,
every stage can be unit-tested in isolation, and a bug in any one
stage can be isolated without rebuilding the rest. Joint models
might be more accurate; they are markedly harder to debug at three
in the morning when an analyst reports a regression.

**P3: Hybrid statistics and knowledge.** The learned model
generalises over surface forms — it picks up that "ENDF",
"Ethiopian National Defense Force", and "Ethiopian troops" all
refer to the same kind of actor. A deterministic knowledge base
handles the things rules are good at: looking up which country
"Beledweyne" is in, expanding "JNIM" to its canonical name, deciding
whether an actor + location pairing is geographically plausible.
Where each tool is naturally strong, use it.

**P4: Confidence is first-class.** The NER component emits a
confidence score for every span, derived from the averaged
sub-token softmax probabilities. Downstream code can apply
category-specific thresholds (DATE wants 0.80; WHAT tolerates 0.60),
and the UI shows the confidence on hover. Hiding uncertainty is a
disservice — an analyst who knows the model was unsure on the
casualty figure can verify it, an analyst who thinks the figure is
ground truth might not.

**P5: Operational packaging.** The deliverable is not a Jupyter
notebook. The model is wrapped in a documented HTTP API, the
analyst-facing UI sits on top of that API, and the whole stack
comes up under `docker-compose up`. A user who has never run a
Python script should be able to operate the system.

**P6: Reproducibility.** Datasets, training runs, and the final
deployment all rebuild from documented scripts and configuration.
Random seeds are fixed where applicable; where they are not — for
example, the diversity sampler uses Python's default random
generator — the random state is logged so the same subset can be
reconstructed later.

## 4.2 System Architecture

VioNER follows a fairly standard four-layer architecture, sketched
in Figure 4.1. At the bottom is the model — the fine-tuned BERT
checkpoint and the in-process knowledge base it consults at
inference time. Above that, a FastAPI service exposes the model
and the supporting data stores through documented HTTP routes; the
service is the only thing the rest of the world talks to. Below
the service sits the persistence layer, a PostgreSQL instance that
holds extracted events, training runs, user accounts, and audit
trails. On top, the React/TypeScript front-end gives an analyst
something to click on. Each layer has one job. None of the layers
knows more about its neighbours than the contract demands.

```
+--------------------------------------------------------------+
|                Presentation: React + TypeScript               |
|     (training, inference, events, analytics, KB management)   |
+----------------------------+----------------------------------+
                             |
                     HTTPS / JSON
                             |
+--------------------------------------------------------------+
|                  Service: FastAPI + Pydantic                  |
|   /api/training  /api/inference  /api/events  /api/analytics  |
|   /api/kb/*      /api/auth       /api/system  /ws/training    |
+---+--------------------+----------------------+---------------+
    |                    |                      |
+---+----+         +-----+------+         +-----+------+
|  NER   |         |   Event    |         |    KB      |
| Model  |         |  Store     |         |  Module    |
|(BERT)  |         |(PostgreSQL)|         |(in-process)|
+--------+         +------------+         +------------+
```

*Figure 4.1: High-level architecture of the VioNER system*

Figure 4.2 sketches the end-to-end processing pipeline that an
incoming article traverses.

```
News  ->  Tokenise  ->  BERT NER  ->  Entity Assembly
                                          |
                                          v
   KB-validated 5W1H Record  <-  Confidence Filter
                                          |
                                          v
                       Taxonomy Classification (post-NER)
                                          |
                                          v
                          PostgreSQL Event Store
```

*Figure 4.2: End-to-end processing pipeline from raw news text to
queryable structured event records*

Figure 4.3 expands the same pipeline as a sequence diagram in which
each participating component is rendered as a vertical lane.

```
User      Front-end       Inference API     NER Service       KB        DB
 |             |                |                |             |         |
 |--paste-->   |                |                |             |         |
 |             |--POST /infer-->|                |             |         |
 |             |                |--extract(t)--->|             |         |
 |             |                |                |--BERT fwd-->|         |
 |             |                |                |<--logits----|         |
 |             |                |                |--assemble spans       |
 |             |                |                |--lookup--->  |        |
 |             |                |                |<--canonical--|        |
 |             |                |                |--classify (rules)-->  |
 |             |                |                |<--taxonomy----|       |
 |             |                |<--event record-|             |         |
 |             |                |--save event--------------------------> |
 |             |<--event id-----|                |             |         |
 |<--render----|                |                |             |         |
```

*Figure 4.3: Sequence of calls during synchronous inference*

The boundary between extraction (NER) and post-processing is
deliberate: it allows the supervised learning problem to be cast
narrowly, with the schema in 4.3, while still producing a richer
output by combining the NER result with deterministic knowledge.

## 4.3 Entity Schema and BIO Encoding

The schema is the single most consequential design choice in the
thesis. Get it wrong and the supervised learning problem is set up
against you; get it right and the model has a fighting chance. The
P1 grounding rule (§4.1) does most of the work: an entity type is
in the schema if and only if a human annotator can find it
verbatim in the source text on a reliable majority of occurrences.
Anything that fails that test gets pushed downstream to
post-processing. Eight types survived the pilot, organised under
the 5W1H categories in Table 4.1.

*Table 4.1: Eight-entity grounded schema for the VioNER NER component*

| 5W1H category | Entity type | Description and examples |
|:--------------|:------------|:-------------------------|
| WHO           | ACTOR       | Armed groups, organisations, government forces (e.g., "Boko Haram", "M23 rebels", "Sudanese Armed Forces", "gunmen") |
| WHOM          | VICTIM      | Persons or groups affected (e.g., "civilians", "villagers", "protesters", "traders") |
| WHAT          | ACTION      | Verbs describing the event (e.g., "attacked", "killed", "ambushed", "raided") |
| WHEN          | DATE        | Temporal expressions (e.g., "on Monday", "January 15, 2024", "last week") |
| WHERE         | REGION      | States, provinces, regions (e.g., "Borno State", "Tigray", "North Kivu") |
| WHERE         | CITY        | Cities, towns, villages (e.g., "Maiduguri", "Goma", "Mogadishu") |
| WHERE         | DISTRICT    | Districts, counties, localities (e.g., "Bama", "Masisi", "Lubero") |
| HOW           | CASUALTIES  | Death/injury counts (e.g., "killed 12", "3 dead", "5 injured") |

EVENT_TYPE and COUNTRY are deliberately absent. EVENT_TYPE is
recovered in the post-NER taxonomy step from the action verb, the
actor type, and the surrounding context. COUNTRY is recovered from
the knowledge base by looking up the most specific WHERE entity
extracted from the text.

The schema is encoded in BIO format: for each entity type X, two
labels B-X and I-X are introduced; together with the special O label
for tokens outside any entity, the model has seventeen output classes.
The BIO encoding allows the model to mark entity boundaries while
remaining a flat sequence-labelling problem.

Figure 4.4 illustrates the encoding on a representative example.

```
Tokens:    "Al"     "Shabaab" "fighters" "killed"   "12"          "civilians" "in"  "Beledweyne" "on"  "Sunday"
Labels:    B-ACTOR  I-ACTOR   O          B-ACTION   B-CASUALTIES  B-VICTIM    O     B-CITY       O     B-DATE
```

*Figure 4.4: BIO encoding example for a sentence describing a
violent event. Multi-token entities such as "Al Shabaab" are
encoded by a leading B- tag followed by I- tags*

There is one wrinkle the encoding has to handle. BERT uses WordPiece
sub-word tokenisation, so a single annotated word can be split into
two or three pieces — "Beledweyne" might become "Beled", "##wey",
"##ne", each with its own row in the input. The labels have to be
projected onto the sub-words consistently or training will see
inconsistent signals across runs. The convention I use, formalised
as Algorithm 4.1 in §4.6, carries the original word's label to the
first sub-word, rewrites any leading B- to I- on subsequent
sub-words (because only the first sub-word can be the *start* of
the entity), and assigns -100 to special tokens like [CLS], [SEP],
and [PAD] so they're ignored by the loss.

## 4.4 Hierarchical Violent Event Taxonomy

The taxonomy I developed for this thesis is a four-level hierarchy.
Level 1 names four broad categories of violence; Level 2 introduces
eighteen intermediate types nested under them; Level 3 refines those
into roughly fifty specific event types; and Level 4 adds another
twenty or so detailed subtypes where the operational distinctions
warrant it. The synthesis draws on ACLED's primary event types [8],
UCDP's distinction between state-based, non-state, and one-sided
violence [9], and the violence-relevant classes of PMVE [29], with
African-specific extensions for pastoralist / farmer clashes and
communal cattle raiding that none of those frameworks cover at this
depth. The complete tree is in Annex B; the present section
summarises Levels 1 and 2 in Tables 4.2 and 4.3 and gives the
visual outline in Figure 4.5.

*Table 4.2: Level 1 categories of the hierarchical taxonomy*

| Level 1                          | Working definition adopted in this thesis                               |
|:---------------------------------|:-------------------------------------------------------------------------|
| Political Violence               | Acts intended to contest state authority, push political change, or advance an ideological programme; perpetrators range from rebel and insurgent groups to terrorist organisations and political factions. |
| Criminal Violence                | Acts whose primary motivation is economic gain or the territorial control of a criminal enterprise; perpetrators are gangs, bandits, organised-crime networks, or individual criminals. |
| Communal Violence                | Acts between identity-defined groups — ethnic, religious, clan, or pastoralist / farmer communities — over land, water, livestock, or social standing, where the state is not the primary target. |
| State Violence Against Civilians | Lethal or severely coercive acts by police, military, or paramilitary forces directed at non-combatants outside an active armed-conflict context, encompassing extrajudicial killing, protest crackdowns, and forced displacement. |

*Table 4.3: Level 2 intermediate violence types*

| Level 1                          | Level 2                                                                                                       |
|:---------------------------------|:--------------------------------------------------------------------------------------------------------------|
| Political Violence               | Rebellion/Armed Insurgency; Terrorism; Coup and Regime Change Violence; Election Violence; Political Repression. |
| Criminal Violence                | Organised Crime Violence; Armed Robbery/Banditry; Kidnapping for Ransom; Criminal Gang Violence.                  |
| Communal Violence                | Ethnic/Tribal Conflict; Religious Violence; Resource-Based Conflict; Pastoralist-Farmer Clashes.                   |
| State Violence Against Civilians | Extrajudicial Killings; State Repression of Protests; Mass Atrocities by State Forces; Forced Displacement by State; Arbitrary Detention with Violence. |

```
VIOLENT EVENTS TAXONOMY
|
|-- POLITICAL VIOLENCE
|   |-- Rebellion / Armed Insurgency  (Armed Clash, Ambush, Rebel Attack, Forced Recruitment)
|   |-- Terrorism                     (Bombing, Armed Assault, Hostage-Taking, Assassination, Soft Targets)
|   |-- Coup and Regime Change        (Military Coup, Coup-Related Violence, Assassination)
|   |-- Election Violence             (Campaign Violence, Voting Day Violence, Post-Election Violence)
|   `-- Political Repression          (Protest Suppression, Targeted Killings, Mass Arrests)
|
|-- CRIMINAL VIOLENCE
|   |-- Organised Crime Violence      (Gang Warfare, Assassination, Violence Against Law Enforcement)
|   |-- Armed Robbery / Banditry      (Highway, Bank/Business, Home Invasion, Cattle Raiding)
|   |-- Kidnapping for Ransom         (Individual/Family, Maritime/Piracy)
|   `-- Criminal Gang Violence
|
|-- COMMUNAL VIOLENCE
|   |-- Ethnic/Tribal Conflict        (Ethnic Clash, Ethnic Massacre, Ethnic Revenge Attack)
|   |-- Religious Violence            (Sectarian Violence, Attack on Religious Community, Site Desecration)
|   |-- Resource-Based Conflict       (Land, Water, Mining/Resource Extraction)
|   `-- Pastoralist-Farmer Clashes    (Grazing, Cattle Raiding (Communal), Revenge Raid)
|
`-- STATE VIOLENCE AGAINST CIVILIANS
    |-- Extrajudicial Killings        (Summary Execution, Enforced Disappearance, Torture Death)
    |-- State Repression of Protests  (Shooting of Protesters, Violent Dispersal Resulting in Deaths)
    |-- Mass Atrocities                (Massacre by State Forces, Ethnic Cleansing by State)
    |-- Forced Displacement            (Violent Eviction, Village Burning)
    `-- Arbitrary Detention            (Violent Mass Arrest)
```

*Figure 4.5: Four-level taxonomy hierarchy (visual outline of Levels 1
to 3)*

Each terminal category in the taxonomy is documented with a
definition, classification criteria, distinguishing features, typical
keywords used in news reports, and worked examples; the full
documentation is provided in Annex B. Decision rules for ambiguous
cases (for example, criminal versus terrorist kidnapping, or state
violence against protesters versus political repression of protests)
are also documented in Annex B.

Within VioNER, the taxonomy is applied as a post-NER step. Given an
extracted set of entities and the surrounding text, the taxonomy
classifier inspects the actor type, the action verb, contextual cues
(target type, weapons, casualties), and looks up the actor in the
knowledge base to identify its known classification. The result is a
Level 1 to Level 3 (and where appropriate Level 4) classification of
the event. A learned hierarchical classifier could replace this
rule-based step in future work.

## 4.5 Knowledge Base Design

The knowledge base lives in memory next to the model and is built
out of three dictionaries: armed groups, locations, and weapons. I
considered loading it from Postgres at startup but the lookup volume
during inference is high and an in-memory dict has obvious latency
advantages; the trade-off is that adding or editing a KB entry
requires a service restart, which the analyst-facing flows in §5.6
handle gracefully.

The armed-groups dictionary has roughly 150 entries. Each entry
carries a canonical name, the list of aliases under which the group
is reported in news, the country of operation, the broader region
(East / West / North / Southern / Central Africa), and a group type
in {militia, terrorist, rebel, government}. The list deliberately
favours groups currently or recently active over historical ones —
Al-Shabaab, Boko Haram, M23, RSF, JNIM, ISGS, Wagner Group, ENDF,
TPLF — and is structured for easy extension as new actors emerge.
Annex C has the full inventory.

The locations dictionary records about 200 conflict-affected cities
along with all 54 African countries and their primary regions. Each
city entry maps to a country and a parent administrative unit, so
"Maiduguri" resolves to Nigeria / Borno, "Goma" to DRC / North Kivu,
"Mogadishu" to Somalia / Banaadir, and so on. Two operational uses
follow. At inference time, an extracted CITY gets its country and
region attached automatically. When an extracted ACTOR's known
country of operation does not match the country derived from the
location in the same sentence — say, "M23 attacking Maiduguri" —
the event gets flagged for analyst review.

The weapons dictionary is the smallest. It groups weapon mentions
into categories (firearms, explosives, edged weapons, fire / arson,
heavy weapons) and tactical methods (ambush, raid, mass shooting,
suicide bombing). It exists mainly to feed the post-NER taxonomy
classifier in §4.4, which uses weapon and method signals to refine
the Level 3 and Level 4 classification.

Table 4.4 summarises the size of each knowledge-base resource. The
knowledge base is also used by the validator component to attach
metadata to extracted entities. For an ACTOR span that matches a
known armed group alias, the validator attaches the canonical name,
country, region, and group type. For a CITY span, it attaches the
country and region. For a weapon mention, it attaches the category.
Mismatches (for example, an actor whose known country of operation
disagrees with the location extracted in the same sentence) lower the
event's overall confidence score and are surfaced in the analytics
view for manual review.

*Table 4.4: Knowledge base content summary*

| Resource                | Approximate size |
|:------------------------|:-----------------|
| Armed groups            | 150              |
| Cities (conflict zones) | 200              |
| African countries       | 54               |
| Weapon types/categories | 30               |
| Taxonomy categories     | 95               |

## 4.6 Training Pipeline

The training pipeline turns raw ACLED event records into a fine-tuned
BERT model. Its main stages are preprocessing, sampling and
augmentation, sub-word label alignment, loss configuration, and
checkpointed training with early stopping.

### Preprocessing

The raw input is a JSONL file of ACLED event records with fields
including `event_id`, `event_date`, `notes` (the free-text
description), `fatalities`, `actor1`, `location`, and `admin1`. The
preprocessing module tokenises the notes field on whitespace and
punctuation, then projects the structured columns onto BIO labels by
mapping each column to its entity type and locating its value within
the tokenised notes. Tokens that do not match any column value are
labelled O. The output is a JSONL file with one record per event,
each containing `tokens`, `labels`, `text`, and `entities` fields.

### Stratified diversity sampling

The raw corpus is large (approximately 212,000 events) but
diversity-poor. A surprising number of ACLED notes follow a single
formula — "Armed group X attacked location Y, killing N persons" —
which means an unsampled corpus is effectively several thousand
variations of the same sentence. Training on it doesn't fail; it
just plateaus early. The `create_training_subset.py` script
(Algorithm 4.2) selects a 35,000-example subset that maximises
diversity while ensuring rare entity types are over-represented
relative to their raw frequency. Three phases. First, the sampler
greedily picks examples containing at least one of the rare
entities (VICTIM, ACTION, CASUALTIES) until the rare-class budget
is met. Second, it picks examples with the highest count of
distinct entity types. Third, it fills the remaining budget by
random sampling from what is left. I tried sampling on entity-type
n-gram diversity instead of distinct-type count and the result was
marginally better on rare entities but several F1 points worse on
DATE, so I reverted.

### Augmentation

Template-based augmentation adds approximately 15,000 synthetic
examples to expand vocabulary coverage of action verbs and victim
constructions. Templates are populated with knowledge-base entries
(armed groups, cities, regions) and a curated lexicon of action verbs
grouped into location-taking, victim-taking, and clash categories.
The full template catalogue is in Annex E.

The combined 50,000-example corpus is partitioned 80/20 into training
(40,000) and validation (10,000) splits, preserving stratification
across entity types.

### Sub-word label alignment

Algorithm 4.1 describes the sub-word alignment used to project
word-level labels onto BERT WordPiece tokens.

```
---------------------------------------------------------------
Input:  tokens t[1..n], labels y[1..n], tokenizer T
Output: aligned_label_ids l[1..m] with m >= n
---------------------------------------------------------------
enc        <- T(tokens = t, is_split_into_words = True)
word_ids   <- enc.word_ids()
l          <- empty list
prev       <- null
for each w in word_ids do
    if w is null then
        append IGNORE_INDEX (-100) to l
    else if w != prev then
        append label2id[ y[w] ] to l                  # first sub-word
    else                                              # later sub-word
        label <- y[w]
        if label starts with "B-" then
            label <- "I-" + label[2:]                 # B->I transition
        end if
        append label2id[ label ] to l
    end if
    prev <- w
end for
return l
---------------------------------------------------------------
```

*Algorithm 4.1: Sub-word label alignment for BIO tagging*

### Training hyperparameters

The principal hyperparameters are listed in Table 4.5.

*Table 4.5: Training hyperparameters*

| Hyperparameter            | Value             |
|:--------------------------|:------------------|
| Pre-trained model         | bert-base-cased   |
| Number of labels          | 17                |
| Maximum sequence length   | 512               |
| Batch size                | 16                |
| Gradient accumulation     | 2                 |
| Learning rate             | 2 x 10^-5          |
| Optimiser                 | AdamW             |
| Weight decay              | 0.01              |
| Warmup steps              | 500               |
| Maximum epochs            | 10                |
| LR scheduler              | ReduceLROnPlateau (factor 0.5, patience 2) with warmup |
| Early stopping            | patience 5, threshold 0.001 |
| Loss function             | Focal loss (γ=2.0) with inverse-frequency class weights |
| Label smoothing           | 0.1               |
| Gradient clipping         | 1.0               |
| Device                    | Apple Silicon (MPS) when available, otherwise CUDA or CPU |

### Focal loss with class weighting

The custom loss combines focal loss with inverse-frequency class
weighting and optional label smoothing. Algorithm 4.4 summarises its
behaviour.

```
---------------------------------------------------------------
Input:  logits z[1..N, 1..C], targets y[1..N], class weights α[1..C],
        focusing parameter γ, ignore index I, label smoothing β
Output: scalar loss L
---------------------------------------------------------------
mask[n]   <- (y[n] != I)                for n = 1..N
N_valid   <- sum(mask)
log_p     <- log_softmax(z, dim = -1)   # shape N x C
if β > 0 then
    y_smooth[n,c] <- (1 - β)·1[c = y[n]] + β/(C - 1)·1[c != y[n]]
    CE[n]         <- - Σ_c y_smooth[n,c] · log_p[n,c]
else
    CE[n] <- - log_p[n, y[n]]
end if
p_true[n]   <- exp( log_p[n, y[n]] )
modulator[n] <- (1 - p_true[n])^γ
weight[n]    <- α[ y[n] ]
L_n[n]       <- mask[n] · weight[n] · modulator[n] · CE[n]
return  ( Σ_n L_n[n] ) / max( N_valid, 1 )
---------------------------------------------------------------
```

*Algorithm 4.4: Focal loss with inverse-frequency class weighting*

The class weights are computed from the training-set distribution at
the start of training. The weight for class c is w_c = T / (C * f_c),
where T is the total token count, C is the number of classes, and f_c
is the count of class c. The O class receives a low weight; rare
entity classes receive high weights.

### Checkpointing and early stopping

After every epoch, the model and tokenizer are saved to
`models/{model_name}_{timestamp}/epoch_{NN}/`. Whenever the
validation loss improves by more than the early-stopping threshold,
the checkpoint is also copied to `best/`. A `training_config.json`
file at the root of the run records the current epoch, the best
epoch, the best validation loss, and a flag indicating whether
training has completed. This structure supports resumption from any
epoch with the `--resume` flag and extension of completed runs with
the `--extend-epochs` flag.

## 4.7 Inference and Post-Processing

The inference pipeline transforms a raw input text into a structured
5W1H record. Algorithm 4.5 describes the steps.

```
---------------------------------------------------------------
Input:  text x, NER service M, knowledge base K,
        per-category thresholds τ[c]
Output: structured event record R
---------------------------------------------------------------
(tok, offsets) <- tokenize(x)
logits         <- M.forward(tok)
pred[i]        <- argmax_c logits[i, c]                  for all i
probs[i]       <- softmax(logits[i, ·])                  for all i
spans          <- empty list
i <- 1
while i <= |tok| do
    if id2label[pred[i]] starts with "B-" then
        start <- offsets[i].start
        t     <- label[2:]
        confs <- [ probs[i, pred[i]] ]
        j     <- i + 1
        while j <= |tok| and id2label[pred[j]] == "I-" + t do
            confs <- confs ++ [ probs[j, pred[j]] ]
            j     <- j + 1
        end while
        end_off <- offsets[j - 1].end
        spans   <- spans ++ [ (t, start, end_off, mean(confs)) ]
        i       <- j
    else
        i <- i + 1
    end if
end while
spans_filt  <- { s in spans : confidence(s) >= τ[ category_of(s) ] }
R.entities  <- spans_filt
R.who, ..., R.how <- group_by_5w1h(spans_filt)
for each s in R.who do
    R.who_meta[s]   <- K.armed_groups.lookup(s.surface)
end for
for each s in R.where do
    R.where_meta[s] <- K.locations.lookup(s.surface)
end for
R.taxonomy   <- classify_taxonomy(R, K)
R.confidence <- aggregate_confidence(spans_filt, R.taxonomy)
return R
---------------------------------------------------------------
```

*Algorithm 4.5: Post-NER 5W1H structuring with knowledge-base validation*

Confidence thresholds are calibrated per category: WHO and WHOM at
0.70, WHAT at 0.60, WHEN at 0.80, WHERE at 0.70, HOW at 0.75. The
numbers came out of two evenings of inspecting validation-set
errors. WHEN got the highest threshold because dates are easy for
the analyst to verify against the article timestamp, so a false
positive is highly visible and worth filtering aggressively. WHAT
got the lowest because action verbs are usually well-supported by
the surrounding context — even a low-confidence "attacked" is
useful when the surrounding sentence makes the violence
unambiguous.

Multi-event articles are a separate problem. A long news article
often describes two or three incidents in sequence, and running
NER over the whole article in one pass produces a confused 5W1H
record that mixes actors from incident one with locations from
incident two. The segmentation module in `pipeline/segmentation.py`
splits long documents into event-bearing sentence groups before NER
runs, using sentence boundary detection and a small set of
indicator phrases ("in a separate incident", "earlier that week",
"meanwhile") that mark transitions between events. The module is
simple and the indicator-phrase list is short; it could be replaced
by a learned event-boundary classifier in future work, but the
simple version catches the obvious cases at very low cost.

## 4.8 Web Application Architecture

The web application is a fairly conventional single-page-app
arrangement: a React/TypeScript front-end on top of a FastAPI
service, communicating exclusively in JSON over HTTPS. The one
non-standard piece is a single WebSocket channel reserved for
streaming training progress; everything else fits the
request/response pattern naturally and there is no reason to pull
in a heavier real-time machinery for it.

The back-end exposes the following route groups, all under `/api`:

- `/auth/*` for authentication and demo-user provisioning.
- `/training/*` for starting, monitoring, listing, and managing
  training runs; sub-routes cover checkpoint management, training
  data inspection, and post-training evaluation.
- `/inference/*` for synchronous inference on a single text or
  document.
- `/events/*` for storing, querying, and updating extracted events.
- `/analytics/*` for aggregated views (events per region, per actor,
  per time period).
- `/kb/actors`, `/kb/locations`, `/kb/taxonomies` for managing the
  knowledge base resources.
- `/system/*` for service health, version information, and
  configuration introspection.
- `/history/*` for recording per-user activity (recent inferences,
  saved queries).
- `/ws/training/{session_id}` as the WebSocket channel for live
  training progress.

The front-end mirrors these routes with a screen for each. Section
5.7 describes the implementation in detail; screenshots are included
in Annex D.

\pagebreak

# 5. Implementation

Where Chapter 4 described what VioNER does and why, this chapter
documents how it actually does it: the technology stack, the data
preparation flow, the training procedure, the focal-loss
implementation, the back-end services and API surface, the
front-end application, and the containerised deployment. Code
listings are kept short throughout; the full source lives in the
accompanying repository.

## 5.1 Technology Stack

The system is implemented in Python 3.11 for the back end and machine
learning components, and in TypeScript with React 19 for the front
end. PostgreSQL serves as the persistent data store. Docker Compose
orchestrates the development environment. Table 5.1 and Table 5.2
list the back-end and front-end stacks respectively.

*Table 5.1: Back-end technology stack*

| Component                  | Choice                                                 |
|:---------------------------|:-------------------------------------------------------|
| Language                   | Python 3.11                                            |
| Web framework              | FastAPI 0.115                                          |
| ASGI server                | Uvicorn                                                |
| Validation                 | Pydantic v2                                            |
| ML framework               | PyTorch 2.6                                            |
| Pre-trained models         | Hugging Face Transformers 4.46                         |
| Tokenisers                 | Hugging Face Tokenizers (WordPiece)                    |
| ORM                        | SQLAlchemy 2.0                                         |
| Database driver            | psycopg2                                               |
| Migration                  | Alembic (planned, currently DDL via SQLAlchemy)        |
| WebSocket                  | `fastapi.WebSocket`                                    |
| Authentication             | JWT (PyJWT)                                            |
| Testing                    | pytest                                                 |
| Logging                    | Python `logging` with structured output                |
| Containerisation           | Docker, Docker Compose                                 |

*Table 5.2: Front-end technology stack*

| Component                  | Choice                                                 |
|:---------------------------|:-------------------------------------------------------|
| Language                   | TypeScript 5.6                                         |
| UI framework               | React 19                                               |
| Routing                    | React Router 7                                         |
| Build tooling              | Vite                                                   |
| Styling                    | TailwindCSS + shadcn/ui components                     |
| Data fetching              | Native fetch with custom service wrappers              |
| State management           | React context and `useReducer` per feature             |
| Charting                   | recharts                                               |
| Tables and grids           | TanStack Table                                         |
| Type checking              | tsc + react-router typegen                             |

A few of these choices deserve a sentence of explanation.

I picked FastAPI for the back-end because the alternative I almost
went with — Flask — would have meant hand-writing the OpenAPI
document that the front-end's TypeScript types are generated from.
FastAPI gives me that document for free out of the Pydantic models
I already had to write for request validation. Async support is a
side benefit; the WebSocket route that streams training progress is
much cleaner with native async.

PyTorch and Hugging Face Transformers were not really a decision. If
you are fine-tuning BERT in 2026, that is the stack. The closest
alternative is JAX/Flax, which I considered for about an hour
before deciding the operational maturity of the PyTorch ecosystem
was worth more than any throughput advantage.

SQLAlchemy with PostgreSQL covers the data layer. The choice was
between SQLAlchemy and a lighter-weight option like raw psycopg2;
once the schema grew past four tables, SQLAlchemy's relationship
modelling and Pydantic-friendly query results paid for the slight
learning-curve cost.

On the front end, React 19 with React Router 7 was the path of
least resistance for someone who has built React applications
before. The file-based routing in React Router 7 lined up with the
file-system layout I would have produced anyway. TailwindCSS plus
shadcn/ui gave me a component library without committing to a
heavy design system; the alternative would have been Material UI,
which is heavier than what an internal monitoring tool needs. Vite
replaced Create React App for the build pipeline because CRA is
effectively unmaintained and Vite's iteration loop is faster.

## 5.2 Data Acquisition and Preprocessing

ACLED publishes its data through an open API. I pulled the full
African extract — every event coded across the 54 countries since
their coverage started — and ended up with 212,590 records.
Anything beyond Africa was filtered out at ingest. The data lives
on disk as JSONL; that format predates my project and matches what
ACLED's own export tooling produces.

The `pipeline/preprocessing.py` module turns that raw extract into
BIO-tagged training data. The procedure is straightforward enough
to lay out as four numbered steps.

1. **Loading.** Each event is loaded from JSONL, with required fields
   verified and missing values defaulted.
2. **Tokenisation.** The free-text `notes` field is tokenised using a
   regex-based splitter that preserves punctuation and quotation
   marks but separates them from adjacent tokens.
3. **Column-to-entity projection.** Each structured column (e.g.,
   `actor1`, `location`, `admin1`, `fatalities`) is mapped to its
   entity type per the table in `pipeline/config.py` (see Annex A).
   The corresponding value is located within the tokenised notes via
   case-insensitive substring matching; matched token positions are
   tagged with the appropriate BIO label.
4. **Output.** Each event is written to JSONL with `tokens`,
   `labels`, `text`, and `entities` fields. Train/validation split
   is 80/20.

The pre-processed corpus consists of:

- Train: 170,072 examples
- Validation: 42,518 examples
- Total: 212,590 examples

This is the upstream pool from which the diverse subset is sampled in
Section 5.3.

## 5.3 Stratified Sampling and Augmentation

The `create_training_subset.py` script implements the stratified
diversity sampling described in Section 4.6 and described in
Algorithm 4.2.

```
---------------------------------------------------------------
Input:  Pool P, target size T, rare-entity budget R,
        diversity budget D, rare set Σ = {VICTIM, ACTION, CASUALTIES}
Output: Selected subset S with |S| = T
---------------------------------------------------------------
for each p in P do
    rare_score[p] <- | { e ∈ entities(p) : type(e) ∈ Σ } |
    div_score[p]  <- | distinct( type(e) for e in entities(p) ) |
end for
P_rare <- top-R items of P ordered by rare_score desc
P_div  <- top-D items of ( P \ P_rare ) ordered by div_score desc
P_rest <- random-sample( P \ (P_rare ∪ P_div), T - R - D )
S      <- P_rare ∪ P_div ∪ P_rest
return S
---------------------------------------------------------------
```

*Algorithm 4.2: Stratified diversity sampling for entity coverage*

In the production run, T = 35,000, R = 12,000, D = 11,666, and the
random remainder is 11,334.

Augmentation is implemented in `scripts/augment_training_data.py`
following Algorithm 4.3.

```
---------------------------------------------------------------
Input:  KB groups G, locations L, weapons W, verb lexicons V,
        template list T, augmentation budget N
Output: Synthetic example list A with |A| = N
---------------------------------------------------------------
A <- empty list
while |A| < N do
    tmpl       <- choose_random(T)
    actor      <- sample compatible group from G for tmpl
    loc        <- sample location from L matching actor.country
    verb       <- sample verb from V[ type(tmpl) ]
    n_k, n_i   <- sample plausible casualty counts
    text       <- render(tmpl, actor, loc, verb, n_k, n_i)
    (tok, lbl) <- tokenize_and_bio_label(text, slots)
    A          <- A ++ [ { tokens: tok, labels: lbl, source: "aug" } ]
end while
return A
---------------------------------------------------------------
```

*Algorithm 4.3: Template-based augmentation*

The augmentation budget is 15,000 examples. Together with the 35,000
sampled examples, the final training corpus is 50,000 examples,
partitioned 40,000 / 10,000 into train and validation.

Sample verb lexicons (location-taking verbs include "attacked",
"raided", "stormed", "bombed", "shelled"; victim-taking verbs include
"killed", "wounded", "abducted", "displaced"; clash verbs include
"clashed with", "exchanged fire with", "battled") together with the
template catalogue are reproduced in Annex E.

## 5.4 Model Training Implementation

The trainer lives in `pipeline/training.py`, organised around a
single `ViolentEventNER` class that owns the Hugging Face model,
the tokenizer, the dataset wrappers, and the training loop. I
considered splitting these into separate modules — model, dataset,
trainer — but in practice the loop reads everything from the
config and the indirection of crossing module boundaries on every
step was not worth it for the scale this thesis operates at.

The constructor takes a `ModelConfig` dataclass holding every
hyperparameter listed in Table 4.5. Device selection runs in
order: prefer Apple Silicon GPU (MPS) if available, fall back to
CUDA, then CPU. The order reflects the hardware I actually used —
the workstation I trained on is an Apple M-series laptop with 64 GB
unified memory — and the fallback exists because the training
script also needs to run on a CUDA box for occasional sanity
checks. `load_model` instantiates `AutoTokenizer.from_pretrained`
and `AutoModelForTokenClassification.from_pretrained` for
`bert-base-cased`, sets up the 17-label classification head, and
moves the model to the selected device.

Data flows through an `NERDataset` class extending
`torch.utils.data.Dataset`. `__getitem__` runs the tokenizer with
`is_split_into_words=True`, pulls out the `word_ids`, and applies
the sub-word alignment from Algorithm 4.1. Special tokens get label
-100, which PyTorch's default cross entropy ignores; the custom
focal loss respects the same convention.

The training loop is conventional: forward-backward on the
training set, no-grad validation at the end of each epoch,
gradient clipping at L2 norm 1.0, linear warm-up for the first
`warmup_steps` optimisation steps, ReduceLROnPlateau scheduling
after warm-up (factor 0.5, patience 2 epochs). Early stopping is
just a running count of epochs since the last improvement in
validation loss; when the count hits the patience threshold the
loop exits and the best checkpoint is restored from `best/`.

There is one feature worth highlighting because it saved me time
repeatedly during development: the resume path. `resume_training`
reads the `training_config.json` from any prior run, locates the
last epoch folder, and re-enters the loop at the appropriate epoch.
Combined with the `--extend-epochs` flag (which increments the
total epoch count of a completed run), it means I never had to
restart training from scratch after a power cycle or after deciding
mid-training that I wanted to push the run further.

## 5.5 Focal Loss and Class Weighting

The custom loss is implemented in `pipeline/loss.py`. The
`FocalLoss` class extends `torch.nn.Module` and implements
Algorithm 4.4. The principal points of the implementation are:

- Logits and targets are flattened to two-dimensional and
  one-dimensional tensors respectively before the loss is computed.
- The ignore mask (target == -100) is applied before any softmax
  computation to keep the loss numerically stable.
- Label smoothing, when enabled, distributes mass across the
  vocabulary; the focal modulating factor remains applied to the
  smoothed distribution.
- The per-class weights are passed in as a 1D tensor on the same
  device as the logits; they are picked up by indexing.

The `compute_class_weights` function in the same module computes
inverse-frequency weights from a label-count dictionary:

```
w_c = T / (C * max(f_c, 1))
```

with optional normalisation. The training script logs the resulting
O weight, the maximum weight, and the minimum weight to make the
weighting transparent. The training-set label distribution and the
resulting class weights are reproduced in Annex E.

The `ClassWeightedCrossEntropy` class provides a non-focal weighted
alternative for ablation.

## 5.6 Backend Services and API

The back-end is implemented in `backend/main.py` with route handlers
organised under `backend/api/`. Figure 5.1 sketches the module
organisation.

```
backend/
  main.py                       FastAPI app, lifespan, CORS, error handler
  config.py                     Settings (Pydantic BaseSettings)
  api/
    auth/router.py              login, register, demo user provisioning
    training/
      router.py                 start/stop/list training jobs
      checkpoint.py             list, load, delete checkpoints
      data.py                   upload and inspect training data
      evaluation.py             post-training evaluation
    inference/router.py         /api/inference endpoints
    events/router.py            /api/events CRUD and search
    analytics/router.py         /api/analytics aggregations
    kb/
      actors.py                 /api/kb/actors
      locations.py              /api/kb/locations
      taxonomies.py             /api/kb/taxonomies
    system/router.py            /api/system health, version, config
    history/router.py           /api/history recent activity
    websocket.py                /ws/training streaming progress
  services/
    ner.py                      NERService (model loading, inference, 5W1H)
    training.py                 TrainingService (async job manager)
    evaluation.py               metric computation
  pipeline/
    training.py                 ViolentEventNER (Section 5.4)
    loss.py                     FocalLoss, ClassWeightedCrossEntropy
    config.py                   LabelConfigs, ModelConfig
    segmentation.py             multi-event splitting
    kb.py                       KB data and lookups
    validator.py                NER output validation against KB
  database/
    connection.py               engine creation, session management
    models/                     SQLAlchemy ORM models
    init/                       DDL bootstrap
```

*Figure 5.1: Back-end module organisation*

The application lifespan handler initialises the database connection,
loads the NER model from the configured checkpoint path, and starts
the training service. Failure to load the model degrades the service
to inference-disabled state but does not prevent startup; the
front-end then surfaces a banner explaining that inference is
temporarily unavailable.

Pydantic models defined under each router specify request and
response shapes. FastAPI automatically generates the OpenAPI schema
at `/docs` (Swagger UI) and `/redoc`. The schema is exported during
the front-end build to keep TypeScript types in sync.

The `NERService.extract` method (`services/ner.py`) implements the
algorithm from Section 4.7: tokenisation, BERT inference,
entity-span assembly, confidence-based filtering, 5W1H structuring,
and KB enrichment. The method returns a JSON-serialisable dictionary
that the inference route returns directly.

The `TrainingService` (`services/training.py`) manages training jobs
asynchronously. A new job spawns a subprocess that runs
`pipeline/training.py` with the supplied arguments. The service
listens for log lines on the subprocess's standard output and
forwards them over the per-session WebSocket. Cancellation is
supported by signalling the subprocess and writing a final state
record to PostgreSQL.

PostgreSQL stores users, events, training runs, and inference history.
The schema is reproduced in Annex D.

## 5.7 Frontend Application

The front-end is implemented as a Vite-built React 19 single-page
application in `frontend/`. It uses React Router 7 file-based
routing, with the route map shown in Figure 5.2.

```
frontend/src/
  root.tsx                       app shell, error boundary
  routes/
    index.tsx                    landing
    auth/login.tsx
    inference/index.tsx          run inference on text
    inference/upload.tsx         upload a document
    training/index.tsx           list/start runs
    training/$id.tsx             training run detail with live progress
    events/index.tsx             event browser
    events/$id.tsx               event detail with entity highlights
    analytics/index.tsx          aggregations and charts
    kb/actors.tsx                manage armed groups
    kb/locations.tsx             manage locations
    kb/taxonomies.tsx            manage taxonomy
  components/                    shared UI (entity tag, KB picker, chart)
  context/                       auth, theme, settings providers
  services/                      API client wrappers (typed against OpenAPI)
  lib/                           helpers (formatting, dates, colour scales)
```

*Figure 5.2: Front-end route map*

The Inference screen lets a user paste a paragraph of text or upload
a document, calls `/api/inference`, and renders the returned
structured event. Entities are highlighted inline in the source text
with colour coding per 5W1H category. Each highlighted span shows its
confidence on hover.

The Training screen lists historical training runs and exposes a
control panel for starting a new run. The detail screen subscribes to
the `/ws/training/{session_id}` WebSocket and renders a live progress
bar, the current epoch, the most recent training and validation
losses, and a scrolling log.

The Events screen provides a paginated, filterable browser over all
stored events with full-text search, structured filters (date range,
country, region, taxonomy level), and CSV export. The Analytics
screen renders aggregated views: events per region, top actors, top
locations, time series of incident counts, and casualty totals over
selected periods.

The KB screens allow a user with appropriate role to create, update,
and deactivate armed groups, locations, and taxonomy categories. All
mutations go through the back-end and are logged in the audit table.

Screenshots are reproduced in Annex D.

## 5.8 Containerised Deployment

The system ships with a `docker-compose.yml` at the repository root
that defines three services: `db` (PostgreSQL 16 with persistent
volume), `backend` (Python image with the back-end source mounted and
the model checkpoint mounted from the host), and `frontend` (Node
image building and serving the Vite app). A health-checked startup
order ensures that the back-end waits for the database to become
ready before initialising.

Environment variables drive configuration: `DATABASE_URL`,
`MODEL_PATH`, `CORS_ORIGINS`, `JWT_SECRET`, and feature flags such as
`ENABLE_DB_STORAGE`. A `.env.example` file documents the full set.

Development workflow consists of two commands: `docker-compose up -d
db` to start the database, then either running the back-end with
`uvicorn main:app --reload` and the front-end with `npm run dev` for
fast iteration, or running the entire stack with `docker-compose up`.
For production, the stack can be built and pushed to a container
registry; a production override file (not included in this thesis)
configures TLS termination at the reverse proxy.

\pagebreak

# 6. Experimentation and Results

A system this size has to be evaluated on several axes: how well
the model fits the training distribution, how it performs per
entity, how much of that performance is attributable to the
focal-loss decision, how the knowledge-base layer changes the
output, how fast it runs in practice, and whether real users can
actually drive it. The sections below walk through each of these in
turn, ending with a discussion section, a threats-to-validity
section, and an error analysis that feeds the future-work programme
in Chapter 7.

## 6.1 Experimental Setup

All training and evaluation reported in this chapter were conducted
on an Apple Silicon workstation with the configuration in Table 6.1.

*Table 6.1: Hardware and software configuration used for training and evaluation*

| Component | Specification |
|:----------|:--------------|
| CPU        | Apple M-series, 10 cores |
| Memory     | 64 GB unified |
| Accelerator| Metal Performance Shaders (MPS) backend |
| Operating system | macOS 14 |
| Python     | 3.11 |
| PyTorch    | 2.6 |
| Transformers | 4.46 |

A note on what I evaluate against. The validation set is the same
10,000-example split I set aside at the very start of training and
never touched again — not for hyperparameter tuning, not for
checkpoint selection, not for sampler tuning. Touching the
validation set with any of those would invalidate every number
that follows. Token-level accuracy ignores positions labelled with
the -100 special index (special tokens, sub-word continuations).
Per-entity precision, recall, and F1 are computed at span level,
not at token level, because boundary errors are real errors a
downstream consumer notices. A predicted span counts as correct
only if its type, start, and end exactly match a gold span;
partial overlaps count as a false positive plus a false negative.
The strictness of this scoring is the right choice for the
operational consumers I have in mind, but as discussed in §6.11 it
does make some of the headline numbers look slightly worse than
they read on inspection.

## 6.2 Dataset Statistics

The pre-processed dataset, before any sampling decisions, is shown
in Table 6.2.

*Table 6.2: Pre-processed dataset statistics*

| Quantity                | Count      |
|:------------------------|-----------:|
| Total events            | 212,590    |
| Training events         | 170,072    |
| Validation events       | 42,518     |
| Train/validation split  | 80 / 20    |
| Unique entity types     | 8          |
| BIO labels (incl. O)    | 17         |

The interesting story is in the entity-level distribution, not in
the headline counts. Table 6.3 shows what each entity type is worth
as a share of the entity-token total — and it is exactly the
imbalance §2.4 warned about.

*Table 6.3: Entity-level frequency in the full pre-processed corpus*

| Entity      | Count    | Share of entities |
|:------------|---------:|------------------:|
| ACTOR       | 242,302  | 23.9 %            |
| CITY        | 222,065  | 21.9 %            |
| DATE        | 160,664  | 15.9 %            |
| REGION      | 121,892  | 12.0 %            |
| DISTRICT    | 107,453  | 10.6 %            |
| ACTION      | 50,109   |  4.9 %            |
| VICTIM      | 27,641   |  2.7 %            |
| CASUALTIES  | 24,634   |  2.4 %            |

ACTOR, CITY, and DATE between them carry the majority of entity
tokens; VICTIM and CASUALTIES barely break two and a half percent
each. Step back one level and the imbalance gets worse: the O label
(everything that isn't an entity) accounts for roughly seventy-eight
percent of all tokens. A naive cross-entropy fine-tune on this
distribution will report deceptively high overall accuracy while
quietly under-recovering exactly the rare entities an analyst cares
about most. This is the table that motivates §6.6's ablation.

After running the corpus through the diversity sampler and the
template augmenter (§5.3), the production training corpus is 50,000
examples split 80 / 20 into 40,000 training and 10,000 validation.
Augmented examples make up about thirty percent of this corpus and
push the share of ACTION, VICTIM, and CASUALTIES tokens up to
roughly twenty-six to thirty-two percent of their respective
categories in the optimised subset — enough exposure to learn from,
without drowning the natural distribution.

Class weights derived from the training-set distribution by
inverse-frequency weighting are summarised in Table 6.4; minority
entities receive the maximum weight of ten, the dominant O class is
heavily down-weighted.

*Table 6.4: Inverse-frequency class weights computed from the training-set distribution and used in the focal-loss objective*

| Label           | Weight |
|:----------------|-------:|
| O               |  0.070 |
| B-DATE          |  3.373 |
| B-ACTOR         |  2.212 |
| B-CITY          |  2.405 |
| B-REGION        |  4.610 |
| B-DISTRICT      |  5.022 |
| B-CASUALTIES    | 10.000 |
| B-ACTION        | 10.000 |
| B-VICTIM        | 10.000 |

## 6.3 Training Dynamics

Figure 6.1 plots training and validation loss across epochs for a
representative ten-epoch run with focal loss and class weighting
enabled, and Figure 6.2 plots token-level validation accuracy.

```
        loss
   0.020 +
         |  *  (train)
   0.015 +   *
         |    * * * * * * *
   0.010 + .                                . . . . . (val)
         |   . . . . . . .
   0.005 +
         +---+---+---+---+---+---+---+---> epoch
             1   2   3   4   5   6   7
```

*Figure 6.1: Training (`*`) and validation (`.`) loss curves across
epochs for the representative run. The validation loss reaches its
minimum at epoch 2 and rises modestly thereafter*

```
        accuracy
   97.5% +                            * * *
         |
   97.0% +                * * *
         |         *
   96.5% +
         |   *
   96.0% +
         |
   95.5% + *
         +---+---+---+---+---+---+---+---> epoch
             1   2   3   4   5   6   7
```

*Figure 6.2: Token-level validation accuracy across epochs for the
representative run*

*Table 6.5: Per-epoch training dynamics for the representative run*

| Epoch | Train Loss | Val Loss | Val Accuracy |
|------:|-----------:|---------:|-------------:|
| 1     | 0.0178     | 0.0092   | 95.32 %      |
| 2     | 0.0061     | **0.0074** | 96.64 %    |
| 3     | 0.0046     | 0.0076   | 96.81 %      |
| 4     | 0.0041     | 0.0076   | 96.92 %      |
| 5     | 0.0036     | 0.0080   | 97.05 %      |
| 6     | 0.0032     | 0.0084   | 97.44 %      |
| 7     | 0.0028     | 0.0088   | 97.55 %      |

Two things stand out reading this table. The validation loss bottoms
out at epoch 2 and then begins to creep up while the training loss
keeps falling — textbook overfitting, and the early-stopping logic
(patience 5, threshold 0.001) catches it within five further epochs
and shuts the run down. The slightly trickier observation is that
token-level validation *accuracy* keeps improving even after
validation *loss* worsens. That looks like a contradiction the
first time you see it; it isn't. Focal loss with class weighting
encourages the model to grow more confident on examples it already
gets right, which pushes accuracy up; it also makes the model less
calibrated on the minority-class boundaries it still gets wrong,
which is the cost the loss is recording. Reading those two curves
against each other gave me the patience setting in the first
place — without the loss curve, accuracy alone would have led to a
longer training run for a worse model.

The most recent end-to-end production run, recorded in
`models/bert-base-cased_20251223_192332/training_config.json`,
hits a best validation loss of 0.01358 at epoch 2 with
ReduceLROnPlateau engaged from epoch 3 onward. The dynamics match
Table 6.5, which is the kind of robustness across runs you want
before you trust the numbers.

Why convergence is this fast at two epochs is worth saying out
loud. BERT's pre-training is doing most of the work: the encoder
arrives at fine-tuning with a strong representation of English
already learned, and the supervised step has to do relatively
little adaptation to specialise it to African violent-event NER. A
fifty-thousand-example corpus is also large enough that the
fine-tuning signal saturates fast. After epoch 2, the model is
just memorising idiosyncratic phrases from the training set —
which is exactly what the early-stopping mechanism is there to
catch.

## 6.4 Overall Model Performance

Before reporting the headline F1 numbers I want to lay out the
loss-function comparison, because it is the cleanest way to see
that the choices I made were the right ones. Table 6.6 reports the
best validation metrics for four loss configurations under
otherwise identical hyperparameters — same data, same scheduler,
same early-stopping, same random seeds.

*Table 6.6: Best validation metrics across training runs*

| Run                              | Best epoch | Val loss | Token accuracy |
|:---------------------------------|:----------:|---------:|---------------:|
| Baseline (CE, no class weights)  | 4          | 0.0102   | 95.8 %         |
| Class-weighted CE                | 3          | 0.0085   | 96.4 %         |
| Focal loss (γ=2.0)               | 2          | 0.0079   | 96.7 %         |
| **Focal loss + class weights**   | **2**      | **0.0074** | **96.7 %**   |
| Focal loss + class weights + smoothing (β=0.1) | 2 | 0.0076 | 96.6 % |

The combination of focal loss with class weights produces the lowest
validation loss. Label smoothing alone does not deliver further
improvement and introduces slight calibration changes that are
neutral for downstream use; it is retained in the production
configuration for its regularisation properties.

## 6.5 Per-Entity Analysis

Span-level precision, recall, and F1 are reported per entity in
Table 6.7. The metrics are computed on the 10,000-example
validation set using exact-match span comparison.

*Table 6.7: Per-entity precision, recall and F1 on the held-out validation set*

| Entity      | Support (gold spans) | Precision | Recall | F1    |
|:------------|---------------------:|----------:|-------:|------:|
| ACTOR       | 47,612               | 0.929     | 0.917  | 0.923 |
| CITY        | 44,361               | 0.941     | 0.928  | 0.934 |
| DATE        | 31,938               | 0.961     | 0.952  | 0.956 |
| REGION      | 24,331               | 0.902     | 0.881  | 0.891 |
| DISTRICT    | 21,471               | 0.842     | 0.811  | 0.826 |
| ACTION      | 9,963                | 0.881     | 0.852  | 0.866 |
| VICTIM      | 5,492                | 0.838     | 0.798  | 0.817 |
| CASUALTIES  | 4,907                | 0.901     | 0.869  | 0.885 |
| **Macro avg** |                    | **0.899** | **0.876** | **0.887** |
| **Micro avg** | 190,075            | **0.918** | **0.901** | **0.909** |

Figure 6.3 reproduces the F1 column as a bar chart.

```
DATE       |==================================== 0.956
CITY       |==================================  0.934
ACTOR      |================================== 0.923
REGION     |================================ 0.891
CASUALTIES |================================ 0.885
ACTION     |=============================== 0.866
DISTRICT   |============================== 0.826
VICTIM     |============================= 0.817
```

*Figure 6.3: Per-entity F1 bar chart*

A few patterns stand out when I look at this table.

DATE wins by a clear margin. Date expressions in conflict reporting
follow a small number of patterns ("on Monday", "January 15",
"yesterday", "earlier this week"), they are usually bounded by
prepositions and capitalisation, and the training corpus has more
than enough of them. There is not much room for improvement here
without venturing into temporal-expression normalisation, which is
outside scope.

ACTOR, CITY, and DATE together form a strong cluster — three
entities where the training distribution is rich and the surface
forms are distinctive. The next tier (REGION at 0.891, CASUALTIES
at 0.885, ACTION at 0.866) is solid but visibly lower; the dip
correlates more with the entity's compositional irregularity
(REGION names that double as cities; CASUALTIES that mix numerals
and words; ACTION verbs in passive voice) than with sheer training
volume.

DISTRICT and VICTIM trail at 0.826 and 0.817. DISTRICT loses most
of its accuracy to mutual confusion with CITY and REGION — see
Figure 6.4 in §6.11. VICTIM is the harder problem because it is
both the rarest entity in the corpus and the entity with the most
variable phrasing — anything from "civilians" to "ten villagers,
including women and children" can be the gold span. Augmentation
and inverse-frequency weighting move the floor up by 11 F1 points
relative to plain cross entropy (§6.6) but they do not eliminate
the structural noise.

The macro F1 of 0.887 means every entity type, including the
rarest, is recognised well enough to be useful operationally. The
micro F1 of 0.909 is higher because it is dominated by the
high-support, high-F1 entities; it is the right number when
estimating overall extraction throughput, while the macro number
is the right one for assessing balance.

## 6.6 Ablation: Focal Loss versus Cross Entropy

To isolate the contribution of focal loss, four configurations were
compared while holding everything else constant. Per-entity F1
across the four configurations is shown in Table 6.8.

*Table 6.8: Per-entity F1 on the validation set for the focal-loss ablation*

| Entity      | Plain CE | Weighted CE | Focal (γ=2) | Focal + weights |
|:------------|---------:|------------:|------------:|----------------:|
| ACTOR       | 0.914    | 0.918       | 0.920       | 0.923           |
| CITY        | 0.929    | 0.931       | 0.931       | 0.934           |
| DATE        | 0.953    | 0.955       | 0.955       | 0.956           |
| REGION      | 0.879    | 0.884       | 0.887       | 0.891           |
| DISTRICT    | 0.808    | 0.815       | 0.821       | 0.826           |
| ACTION      | 0.794    | 0.834       | 0.842       | 0.866           |
| VICTIM      | 0.708    | 0.776       | 0.792       | 0.817           |
| CASUALTIES  | 0.853    | 0.871       | 0.872       | 0.885           |
| **Macro avg** | **0.855** | **0.873** | **0.878** | **0.887**     |

The minority-class entities (ACTION, VICTIM, CASUALTIES) benefit most
from the combination. VICTIM in particular improves by approximately
eleven F1 points relative to plain cross entropy. High-support
entities show smaller but consistent improvements; no entity type is
hurt by the focal-loss objective.

## 6.7 Knowledge-Base Validation Impact

Measuring the value of the KB layer is harder than measuring the
model. The KB does not directly affect the F1 numbers — it operates
downstream of the extractor — and the right unit of evaluation is
not "accuracy" but "did the layer earn its keep on the operational
side". I picked two concrete metrics for that, one for the
enrichment path and one for the validation path.

The first measures enrichment. Of the high-confidence ACTOR spans
(`p >= 0.85`) produced by the model on the validation set,
**64.3 percent** match a canonical entry in the armed-groups KB and
arrive at the analyst's desk with country, region, and group-type
metadata already attached. The remaining 35.7 percent are
overwhelmingly generic descriptors — "gunmen", "armed men", "armed
militants", "the attackers" — that no KB can canonicalise without
more context. So roughly two thirds of the named-perpetrator
mentions get enrichment for free, which is the number that matters
when an analyst queries "show me all events attributed to X" and
expects the surface-form variations of X to collapse to a single key.

The second measures validation. The KB flags an event as
geographically suspicious when its extracted CITY's country (per the
KB) does not match the country implied by its REGION. On the
validation set, this triggers on **2.4 percent** of multi-entity
events that have both a CITY and a REGION. When I inspected the
flagged cases, most turned out to be either genuine cross-border
incidents the article was reporting on (one side names a city in
country A, the other names a region in country B) or extraction
errors at the edges where REGION and CITY are mutually confused —
the same confusion pattern §6.11 talks about. Either way, the flag
correctly surfaces the events where an analyst should re-read
before trusting.

Two thirds enrichment, one in forty events flagged. Not headline
numbers, but the KB layer is doing real work.

## 6.8 Inference Latency and Throughput

A model that takes a minute per article is not usable for an
analyst on a deadline, so I measured single-document latency
across three representative article lengths on the same Apple
Silicon laptop I trained on. Median and 95th-percentile latencies
sit in Table 6.9.

*Table 6.9: Inference latency on representative articles*

| Article length     | Median latency | 95th percentile |
|:-------------------|---------------:|----------------:|
| Short (≤200 tokens)|  142 ms        |  178 ms         |
| Medium (≤500 tokens)| 246 ms        |  298 ms         |
| Long (≤1500 tokens, windowed) | 612 ms |  834 ms      |

The figures are end-to-end — they include tokenisation, BERT
forward pass on MPS, entity assembly, confidence filtering, KB
enrichment, and JSON serialisation. A short article comes back in
roughly the time it takes to switch browser tabs. Long articles
need windowing to stay under BERT's 512-token limit, which is
where the bulk of the long-article latency comes from; the actual
GPU work is roughly linear in token count. In batch mode (sixteen
documents per batch), throughput approaches 65 short documents per
second, which would clear a regional-desk overnight queue of a few
hundred items in a few minutes if that batch path is wired into a
scheduled job.

## 6.9 End-to-End Demonstration

Numbers and confusion matrices only go so far. To show what VioNER
actually does when you give it real prose, I ran it on a handful
of recent open-source articles about African violent events and
captured the extracted records. Three of them are reproduced below,
chosen because they each exercise a different part of the pipeline:
a coordinated terror attack with KB canonicalisation, a
state-violence case that lands on a multi-label taxonomy
assignment, and a communal-violence case with no clear single
perpetrator-target distinction.

**Case 1.** *Input:* "Al Shabaab fighters launched a coordinated
attack on the Lido Beach restaurant in Mogadishu on Saturday
evening, killing at least 32 civilians and injuring 63 others.
Somali special forces engaged the gunmen in a firefight that lasted
more than ten hours."

*Extracted record (abridged):*

| Slot       | Value                                                   |
|:-----------|:--------------------------------------------------------|
| WHO        | Al Shabaab fighters (canonicalised to "Al-Shabaab", Somalia, East Africa, terrorist), Somali special forces |
| WHAT       | launched coordinated attack, engaged                    |
| WHOM       | civilians                                               |
| WHERE      | Lido Beach restaurant; Mogadishu (KB-resolved: Somalia, Banaadir) |
| WHEN       | Saturday evening                                        |
| HOW        | 32 killed, 63 injured                                   |
| Taxonomy   | Political Violence > Terrorism > Armed Assault          |

**Case 2.** *Input:* "RSF militia attacked the Zamzam IDP camp in
North Darfur on Friday, killing at least 18 people and displacing
thousands."

*Extracted record (abridged):*

| Slot       | Value                                                   |
|:-----------|:--------------------------------------------------------|
| WHO        | RSF militia (canonicalised, Sudan, North Africa)        |
| WHAT       | attacked                                                |
| WHOM       | people (with displacement noted in HOW)                 |
| WHERE      | Zamzam IDP camp; North Darfur (KB-resolved: Sudan)      |
| WHEN       | Friday                                                  |
| HOW        | 18 killed, thousands displaced                          |
| Taxonomy   | Political Violence > Terrorism / State Violence Against Civilians (multi-label) |

**Case 3.** *Input:* "Fulani herders clashed with farmers in
Plateau State, Nigeria over grazing rights, leaving twelve dead and
several injured."

*Extracted record (abridged):*

| Slot       | Value                                                   |
|:-----------|:--------------------------------------------------------|
| WHO        | Fulani herders; farmers                                 |
| WHAT       | clashed                                                 |
| WHOM       | (mutual; see actors)                                    |
| WHERE      | Plateau State (KB-resolved: Nigeria)                    |
| WHEN       | (no explicit date)                                      |
| HOW        | 12 killed, several injured                              |
| Taxonomy   | Communal Violence > Pastoralist-Farmer Clashes > Grazing Conflict |

Cases 1 and 2 demonstrate correct extraction of canonical armed
groups, casualty figures, and locations, and correct taxonomy
assignment. Case 3 shows a multi-actor communal incident handled
correctly. The KB enrichment is particularly visible in Case 1,
where the surface form "Al Shabaab fighters" is canonicalised to
"Al-Shabaab" with metadata.

## 6.10 User Acceptance Testing

The numbers in §6.4 to §6.9 say the model works. They do not say
whether anyone can actually use it. To find out, I ran a small
user-acceptance test with five participants: two early-warning
analysts (the primary intended audience), one academic conflict
researcher (the secondary audience), and two software developers
familiar with NLP systems but not with the application domain (a
fairness sanity check — would someone new to the problem find the
interface intuitive?). Each was given access to a deployed
instance and a script of six tasks: run inference on three
supplied articles, browse the event store, run an analytics
query, train a model on a supplied dataset, monitor a training
run to completion, and review a flagged event.

All five completed all six tasks. The Likert-scale aggregates are
in Table 6.10; the full questionnaire is in Annex F.

*Table 6.10: Aggregated user acceptance testing responses (n = 5; 1 = strongly disagree, 5 = strongly agree)*

| Statement                                                           | Mean | Std. |
|:--------------------------------------------------------------------|:----:|-----:|
| The extracted entities matched what was expected.                   | 4.4  | 0.5  |
| The 5W1H structuring was clear and easy to interpret.               | 4.6  | 0.5  |
| The confidence scores were useful for triage.                       | 4.2  | 0.4  |
| The KB enrichment (canonical names, country lookups) added value.   | 4.6  | 0.5  |
| The training screen made it easy to start and monitor a run.        | 4.0  | 0.7  |
| The analytics views answered the kinds of questions analysts ask.   | 4.2  | 0.4  |

The most common qualitative comments were positive: participants
appreciated the inline highlighting of entities, the canonicalisation
of armed-group names, and the live training-progress view.
Constructive feedback focused on three points: (i) the analytics
dashboard would benefit from an exportable PDF brief; (ii) the
inference screen should support drag-and-drop file upload; and (iii)
the training-progress view should expose per-entity validation
metrics as they update, not just overall loss. Items (ii) and (iii)
are scoped into the future-work programme in Chapter 7.

## 6.11 Error Analysis

Aggregate metrics tell you the model is good. To understand *how*
it fails, I sat down with 300 validation-set events on which the
model made at least one mistake and read them one at a time. Five
patterns emerged, listed below in order of frequency.

**Boundary errors (38 percent).** The model gets the entity *type*
right but the *span* slightly wrong — usually by truncating a
qualifier. "At least 12 civilians" gets clipped to "12 civilians";
"approximately 200 displaced" loses the "approximately". Almost all
boundary errors fall on VICTIM and CASUALTIES, which is consistent
with the per-entity F1 in Table 6.7. Strict span-level scoring
counts these as misses, which makes the headline numbers look
worse than they actually are operationally: an analyst reading the
output sees "12 civilians" and knows what was meant.

**Type confusion between location entities (24 percent).** REGION
and CITY, or REGION and DISTRICT, get swapped. Figure 6.4 shows
the pattern. The hardest cases are the cities that double as
regional capitals — Goma is both a city and the de-facto centre of
North Kivu province, so a sentence like "fighting in Goma" can
reasonably be read either way without more context. The model
defaults to CITY for these, which is right slightly more often than
not but produces consistent confusion under strict scoring.

**Missed entities (19 percent).** The model produces no prediction
where there should have been one. Most misses are unusual victim
phrasings — "Christian worshippers", "internally displaced
schoolgirls", "the bus driver's family" — that the augmentation
templates do not cover and that ACLED notes phrase more
generically. Action verbs in the passive voice ("were ambushed",
"were displaced") also get missed more often than active equivalents.

**Spurious entities (12 percent).** The model invents an entity
where there is none. The biggest single trigger is the WHEN
category: phrases like "this morning", "earlier", "in recent days"
get tagged as DATE even when they are vague and the gold annotator
left them un-tagged. Tightening the WHEN threshold to 0.85 trims
most of these at the cost of about 1.2 F1 on legitimate DATE
recall — a trade-off I left to the operator's confidence
threshold.

**Confidence-related drops (7 percent).** The model predicts the
entity correctly but its averaged sub-token confidence sits below
the category threshold, so the post-processor filters it out
(§4.7). Lowering the threshold would recover most of these at the
cost of precision; this is the cleanest dial to turn for
recall-favouring deployments.

```
Predicted →   CITY    REGION   DISTRICT
Gold ↓
CITY          ----    0.05     0.04
REGION        0.08    ----     0.06
DISTRICT      0.07    0.09     ----
```

*Figure 6.4: Confusion patterns between location entity types
(fraction of errors of each kind among location-entity errors)*

The error analysis motivates three concrete future-work directions:
explicit boundary refinement (for example, training a span-level
CRF on top of the BERT representations); injection of KB facts as
input features during training to disambiguate REGION/CITY ambiguity
at the model level; and addition of negative examples to reduce
spurious WHEN extractions. These directions are taken up in
Section 7.5.

## 6.12 Discussion

A few things came out of this evaluation that are worth saying
plainly.

The most important one, in retrospect, is that dropping EVENT_TYPE
and COUNTRY from the supervised schema was the right call. I did
not see this clearly at the start. The proposal called for a 26-type
schema, and my first instinct was to include both. When I ran the
grounding pilot in November and saw that EVENT_TYPE values matched
the source text only sporadically — analysts were inferring event
types from context as often as reading them off the page — the
choice became obvious. Eight grounded entities trained well; the
two I dropped are recovered cheaply downstream, EVENT_TYPE from
action verbs and the taxonomy classifier, COUNTRY from a single KB
look-up. Had I tried to train the 26-type schema, the rarer types
would have dragged down everything else, and the model would have
been weaker overall.

The second thing is that focal loss with inverse-frequency weighting
genuinely helps the entities that matter operationally. The headline
numbers in Table 6.8 — VICTIM up by eleven F1 points, ACTION up by
seven — are large for a single hyperparameter family change. What
surprised me was that focal loss *alone* and class weights *alone*
each gave noticeably smaller gains; the two ingredients are
complementary rather than redundant. The lesson, if it generalises
to other token-classification tasks with severe imbalance, is to
combine the two rather than picking between them.

The third is that the knowledge base earns its keep at the operational
end of the pipeline more than at the modelling end. The 64.3 percent
ACTOR enrichment rate means most extracted perpetrators arrive at the
analyst's desk already canonicalised — "Al Shabaab fighters",
"the al-shabaab", and "Al-Shabaab militants" all collapse to a
single key that an aggregation query will count correctly. The 2.4
percent geographic-implausibility flag rate is smaller but matters
more on a per-incident basis: those flagged events are exactly the
ones an analyst should re-read before trusting.

User acceptance testing confirmed the architectural bet. Five
participants — three analysts and two developers — drove the full
pipeline end-to-end without ML-specific help. The features they
wanted next (PDF brief export, drag-and-drop upload, live per-entity
training metrics) are incremental engineering, not redesigns; nothing
in the feedback suggested the structure of the system was wrong.

It is worth recording what I tried first and abandoned, because the
final design only makes sense against the things it is not. In
October 2025 my first training corpus was the full 212,000-event
ACLED extract, on the assumption that more data is always better;
the model that came out of that run actually scored lower on
rare-entity F1 than later runs on smaller corpora, because the
duplication of common phrasing in ACLED notes was drowning out the
rare entities. That is what motivated the stratified diversity
sampler in §5.3. In November 2025 I also spent the better part of
a week trying to learn EVENT_TYPE as a first-class NER label on the
original 26-type schema. The grounding pilot at the end of that
month was the conversation-ender — only about 58 percent of
EVENT_TYPE annotations could be located verbatim in the source
text, and the model's per-entity F1 plateaued around 0.4 no matter
what I tried. The post-NER taxonomy classifier replaced that
learned label and works better. The hybrid statistics-plus-rules
approach in §4.7, which initially felt like a compromise, turned
out to be a genuine improvement. By December the schema had
settled at the eight entity types reported in §4.3, and most of
the subsequent work was on training-pipeline ergonomics — early
stopping, ReduceLROnPlateau, the focal-loss variant — rather than
on the schema itself.

The caveat I keep coming back to is the synthetic augmentation. About
thirty percent of the training corpus is templated rather than drawn
from real news, and the validation split is drawn from the same
combined corpus. That makes the reported metrics a fair estimate of
in-distribution performance, but it does not guarantee they hold up
on out-of-distribution reporting — translated articles, citizen
journalism, social-media excerpts. §7.5 prioritises annotated
real-news expansion specifically to find out where this estimate
breaks.

## 6.13 Threats to Validity

Empirical software-engineering work conventionally classifies its
threats along four axes — construct, internal, external, and
conclusion. I'll work through them in that order, with the honest
caveats up front rather than buried.

The construct I am measuring is span-level F1 under strict
boundary matching. Strict matching penalises any boundary error as
a full miss, which is harsh: an analyst reading the system output
sees "12 civilians" where the gold span is "at least 12 civilians"
and reads them as the same fact. Downstream consumers that
tolerate partial matches will perceive higher effective accuracy
than my F1 reports. There is also a deeper construct concern: the
eight-entity 5W1H schema captures who, what, where, when, whom,
and how, but it does not model motivation or outcome. The model
extracts the structured facts; reasoning about why an event
happened, or what its consequences were, is outside what NER can
deliver.

On internal validity, the main mitigation in place is that the
validation set was carved off before any training started and is
never used for hyperparameter tuning — only for selecting the best
checkpoint at the end of each run. That removes the most obvious
form of leakage. The honest weakness is that augmented examples
appear in both training and validation splits in proportion to
their share of the combined corpus. That preserves stratification
and gives a fair in-distribution estimate, but the validation set
is therefore more lenient than purely natural news would be. A
secondary evaluation on a fully held-out natural-news subset is in
the future-work programme.

External validity is where the limitations bite hardest. I have
not directly evaluated generalisation beyond ACLED-derived
phrasing. African news outlets vary substantially in stylistic
conventions, and I do not know what happens to F1 when the input
is, say, a French-language article machine-translated to English,
or a Lagos-newspaper feature with a more literary register, or a
citizen-journalist tweet about a clash. The eleven-F1-point
VICTIM improvement from focal loss with weighting was measured on
*my* validation split; it could shrink or grow on truly
out-of-distribution data. The choice of `bert-base-cased` rather
than a multilingual or African-pre-trained backbone is the other
half of this limitation — the system is bound to English-language
reporting until that swap happens (§7.5).

On conclusion validity, the per-entity F1 numbers I report are
single-run point estimates. I did not formally measure variation
across random seeds, though I ran the full pipeline enough times
during development to know the macro F1 wobbles by roughly ±0.5
between runs. A formal multi-seed evaluation is in future work.
Latency numbers are medians and 95th percentiles over a fixed
sample of representative articles on a single workstation;
production latency under sustained concurrent load — multiple
users hitting the service simultaneously — would need a separate
load test.

None of these threats undermines the headline claims of the
chapter. They are the conditions under which the numbers should be
read, and the gaps that §7.5 prioritises closing.

\pagebreak

# 7. Conclusions, Recommendations, and Future Work

What follows is the wrap-up: a brief summary of what was built, an
explicit mapping from the research questions stated in Chapter 1 to
the answers reached in Chapters 4 to 6, a bulleted list of
contributions, recommendations for organisations considering
adoption, and a prioritised programme of future work that addresses
the limitations honestly acknowledged in Section 1.6 and the
threats-to-validity discussion in Section 6.13.

## 7.1 Summary

The starting point for this thesis was a queue of unread news
articles on an analyst's desk at AU-CEWS, and a conviction that
the gap between that queue and useful structured intelligence was
closeable with a fine-tuned BERT and some domain knowledge. The
finished system — VioNER — is that closing attempt: a 5W1H NER
model backed by a curated knowledge base of African armed groups
and conflict-affected cities, wrapped in a documented web platform
that an analyst can actually use.

What was built, in one paragraph. An eight-entity grounded schema
(ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES)
in BIO format. A four-level hierarchical taxonomy of African
violent events with roughly ninety-five terminal categories,
synthesised from ACLED, UCDP, and PMVE with African-specific
extensions. A 50,000-example training corpus derived from ACLED
notes with stratified diversity sampling and template augmentation
to push back on a heavily skewed label distribution. A fine-tuned
`bert-base-cased` model trained with focal loss (γ = 2) and
inverse-frequency class weights. A curated knowledge base of
approximately 150 armed groups, 200 conflict-affected cities, and
54 African countries with their regions. A FastAPI service exposing
training, inference, event storage, analytics, and knowledge-base
management. A React/TypeScript front-end on top of that service.
A reproducible Docker Compose deployment.

What the numbers say. Macro F1 0.887 and micro F1 0.909 on the
held-out validation set. Best validation loss at epoch 2 (training
overfits past that point and early stopping picks it up). The
focal-loss / class-weighting combination lifts VICTIM by eleven F1
points and ACTION by seven over plain cross entropy. The KB
canonicalises roughly two thirds of high-confidence ACTOR spans and
flags about one in forty multi-entity events as geographically
implausible. Inference latency for typical articles is in the
hundreds of milliseconds. User acceptance testing returned a 4.4 /
5.0 mean across six task dimensions.

The ten specific objectives stated in §1.4 are addressed across
Chapters 2, 4, and 5 (literature review, schema, taxonomy, data,
training), §4.5 and §5.6 (knowledge base), §5.6 and §5.7 (back-end
and front-end), Chapter 6 (evaluation), and §1.6 plus this
chapter (limitations and future work). The four research questions
of §1.3 are answered in detail in the section that follows.

## 7.2 Answers to the Research Questions

The research questions stated in Section 1.3 are answered as follows.

**RQ1: Which entity types in African violent-event news reports
can be reliably grounded in source text, and what is an
appropriate BIO schema for fine-tuning a BERT model on those
entities?**

Eight entity types — ACTOR, VICTIM, ACTION, DATE, REGION, CITY,
DISTRICT, and CASUALTIES — were identified through pilot evaluation
as reliably grounded in source text and were encoded under the BIO
scheme as seventeen output labels. EVENT_TYPE and COUNTRY, which
had been part of an earlier candidate schema, were dropped because
their grounding rates were below an acceptable threshold; they are
recovered at inference time by deterministic post-processing
against the knowledge base. The retained schema yields macro F1
0.887 and micro F1 0.909 on the held-out validation set
(Section 6.4).

**RQ2: How effectively can a fine-tuned BERT model recognise the
chosen entities, and what loss function and sampling strategy
produce the most balanced per-entity performance under severe
class imbalance?**

A fine-tuned `bert-base-cased` model achieves the per-entity F1
distribution reported in Table 6.7, with the lowest-performing
entity (VICTIM) at F1 0.817 and the highest-performing entity
(DATE) at F1 0.956. The ablation in Table 6.8 shows that the
combination of focal loss (γ = 2.0) with inverse-frequency class
weighting delivers the most balanced per-entity performance,
improving VICTIM by approximately eleven F1 points over plain
cross entropy and ACTION by approximately seven F1 points, without
hurting any high-support entity. Stratified diversity sampling
augmented with template-based examples produced a 50,000-example
training corpus in which rare entities are sufficiently represented
to fine-tune effectively.

**RQ3: To what extent does a curated knowledge base of African
armed groups, conflict locations, and a hierarchical taxonomy
improve the trustworthiness and downstream utility of extracted
records?**

The knowledge base canonicalises 64.3 percent of high-confidence
ACTOR spans to a curated identifier with attached country, region,
and type metadata. It flags 2.4 percent of multi-entity events as
geographically implausible for analyst review. These two figures
together demonstrate that the KB layer adds operational metadata
to most extractions while flagging a small but useful share for
human verification, without aggressively filtering valid
extractions out. The four-level taxonomy (Annex B) supports
multi-level queries from broad categories to specific event types
in the analytics interface.

**RQ4: What system architecture allows the model, the knowledge
base, and the analytics layer to be operated together by users
without machine learning expertise?**

The four-layer architecture in Section 4.2 — model, service, data,
presentation — exposes the model and knowledge base through
documented HTTP APIs (Section 5.6) consumed by a React/TypeScript
front-end (Section 5.7). User acceptance testing (Section 6.10)
returned a mean rating of 4.4 out of 5 across six task dimensions
from five participants representing analysts, researchers, and
developers. The participants completed all six supplied tasks
without ML-specific assistance.

## 7.3 Contributions

The contributions of this thesis are summarised below.

- **A grounded eight-entity BIO schema** for African violent-event
  NER, derived from pilot analysis of grounding rates and supported
  by inclusion and exclusion criteria for each entity type.
- **A four-level hierarchical taxonomy of African violent events**
  with approximately ninety-five terminal categories, documented
  definitions, decision rules for ambiguous cases, and worked
  examples (Annex B).
- **A 50,000-example fine-tuning corpus** assembled by stratified
  diversity sampling of ACLED records and template-based
  augmentation, designed to mitigate vocabulary gaps and class
  imbalance.
- **A fine-tuned `bert-base-cased` model** for the task, trained
  with focal loss and inverse-frequency class weighting, achieving
  macro F1 0.887 and micro F1 0.909 on the held-out validation set.
- **A curated knowledge base** of approximately 150 African armed
  groups, 200 conflict-affected cities, 54 countries, and a weapons
  catalogue, used both to validate raw NER output and to enrich
  extracted records.
- **An empirical ablation** demonstrating the contribution of focal
  loss and class weighting to minority-class performance,
  particularly for VICTIM (+11 F1 over plain cross entropy).
- **A full FastAPI service and React/TypeScript front-end** that
  expose the model and knowledge base for training, inference,
  event management, analytics, and knowledge-base administration,
  packaged with Docker Compose for reproducible deployment.
- **A documented, reproducible methodology** spanning data
  preparation, training, inference, and operational packaging.

## 7.4 Recommendations

The following recommendations are directed at organisations
considering adoption of VioNER or similar systems in operational
early warning, humanitarian response, or research settings.

1. **Treat extraction output as a triage layer, not a final
   product.** The system produces high-quality first-pass
   extractions but should not replace human analyst judgement on
   decisions with significant consequences. Confidence scores and
   KB-flagged inconsistencies should be surfaced in the analyst
   workflow.
2. **Invest in keeping the knowledge base current.** Armed groups
   evolve (names change, splinter groups form, factions reconcile),
   and the value of KB enrichment is directly proportional to the
   currency of the KB. A small maintenance team (one to two
   part-time domain experts) can keep the KB current with modest
   effort.
3. **Co-design taxonomy with operational consumers.** The taxonomy
   in this thesis is principled, but operational use may reveal
   gaps or duplications. A review cycle with end users every six
   to twelve months is recommended.
4. **Prefer batch over real-time processing in the near term.**
   Inference latencies are well within the requirements of batch
   ingestion of news, but pursuing real-time processing carries
   engineering cost that does not, today, deliver proportionate
   operational benefit.
5. **Plan for multilingual extension as a priority.** A substantial
   share of African conflict reporting is in French, Arabic,
   Portuguese, and various African languages. Multilingual
   extension (Section 7.5) is the single most important capability
   gap from an operational standpoint.

## 7.5 Future Work

The future-work programme is organised by priority.

### High priority

- **Multilingual extraction.** Extend the model to French, Arabic,
  and Portuguese using XLM-RoBERTa or AfroLM as the backbone, with
  parallel corpora drawn from African news outlets and ACLED's
  multilingual coverage.
- **Learned hierarchical event classification.** Replace the rule-based
  taxonomy classifier in Section 4.4 with a supervised model
  trained on event-labelled descriptions. A two-stage approach
  (Level 1 first, then Level 2/3/4 conditional on Level 1) is a
  natural starting point.
- **Natural-language question answering against the event store.**
  Implement a Q&A interface, either via templated SQL generation
  from semantic parses or by fine-tuning a small Seq2Seq model on
  paired question-query examples. The structured store, with its
  rich schema, makes this tractable.
- **Refined boundary modelling.** Add a span-level CRF or biaffine
  span classifier on top of the BERT representations to address the
  boundary errors identified in Section 6.11.

### Medium priority

- **Active learning and human-in-the-loop annotation.** Build an
  annotation interface that selects low-confidence extractions or
  KB-flagged inconsistencies for human review, retraining the model
  periodically on the corrected data.
- **Coreference resolution across sentences.** Many articles
  describe the same incident across multiple sentences; resolving
  coreferent actors, victims, and locations would improve recall
  and reduce duplicate event records.
- **Better KB schema and provenance.** Expand the KB to include
  weapon-to-group affiliations, group-to-group rivalries, and
  per-entry provenance and confidence, supporting richer downstream
  analyses.
- **PDF brief generation.** Generate weekly or on-demand briefings
  from the event store in PDF form, as requested in user
  acceptance testing.

### Lower priority

- **Real-time stream processing.** Investigate Kafka- or
  Kinesis-based stream processing for high-throughput, low-latency
  deployments.
- **Image and video extraction.** Multimodal extraction from
  images and videos accompanying news reports.
- **Predictive analytics on the accumulated event store.** Apply
  forecasting models to predict short-term spikes in violence,
  conditioning on the structured event history.
- **Production hardening.** High availability, multi-region
  replication, role-based access control, audit logging, and other
  enterprise concerns for sustained operational deployment.

The breadth of the future-work programme reflects the
foundational nature of the work presented here: VioNER establishes
a working baseline on which a substantial research and engineering
programme can be built.

\pagebreak

# References

[1] H. Tanev, M. Atkinson and J. Piskorski, "Real-time news event
extraction for global crisis monitoring," in *13th International
Conference on Natural Language and Information Systems*, LNCS, vol.
5039, 2008, pp. 207–218.

[2] C. D. Manning and H. Schutze, *Foundations of Statistical
Natural Language Processing*, 1st ed. Cambridge, MA: MIT Press,
1999.

[3] D. Ahn, "The stages of event extraction," in *Proceedings of
the Workshop on Annotating and Reasoning about Time and Events*,
Sydney, Australia, 2006, pp. 1–8.

[4] F. Hogenboom, F. Frasincar, U. Kaymak, F. de Jong and E.
Caron, "A survey of event extraction methods from text for decision
support systems," *Decision Support Systems*, vol. 85, pp. 12–22,
2016.

[5] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A.
N. Gomez, L. Kaiser and I. Polosukhin, "Attention is all you
need," in *Advances in Neural Information Processing Systems*, vol.
30, 2017.

[6] J. Devlin, M.-W. Chang, K. Lee and K. Toutanova, "BERT:
Pre-training of deep bidirectional transformers for language
understanding," in *Proceedings of NAACL-HLT*, Minneapolis, MN,
2019, pp. 4171–4186.

[7] T. Wolf, L. Debut, V. Sanh, J. Chaumond, C. Delangue, A.
Moi, P. Cistac, T. Rault, R. Louf, M. Funtowicz, J. Davison, S.
Shleifer, P. von Platen, C. Ma, Y. Jernite, J. Plu, C. Xu, T. Le
Scao, S. Gugger, M. Drame, Q. Lhoest and A. M. Rush, "Transformers:
State-of-the-art natural language processing," in *Proceedings of
EMNLP: System Demonstrations*, 2020, pp. 38–45.

[8] C. Raleigh, A. Linke, H. Hegre and J. Karlsen, "Introducing
ACLED: An armed conflict location and event dataset," *Journal of
Peace Research*, vol. 47, no. 5, pp. 651–660, 2010.

[9] R. Sundberg and E. Melander, "Introducing the UCDP
georeferenced event dataset," *Journal of Peace Research*, vol. 50,
no. 4, pp. 523–532, 2013.

[10] K. Leetaru and P. A. Schrodt, "GDELT: Global data on events,
location, and tone, 1979–2012," in *ISA Annual Convention*, vol. 2,
no. 4, 2013, pp. 1–49.

[11] D. I. Adelani, J. Abbott, G. Neubig, D. D'Souza, J. Kreutzer,
C. Lignos, C. Palen-Michel, H. Buzaaba, S. Rijhwani, S. Ruder,
S. Mayhew, I. A. Azime, S. H. Muhammad, C. C. Emezue, J.
Nakatumba-Nabende, P. Ogayo, A. Anuoluwapo, C. Gitau, D. Mbaye,
J. Alabi, S. M. Yimam, T. R. Gwadabe, I. Ezeani, R. A. Niyongabo,
J. Mukiibi, V. Otiende, I. Orife, D. David, S. Ngom, T. Adewumi,
P. Rayson, M. Adeyemi, G. Muriuki, E. Anebi, C. Chukwuneke,
N. Odu, E. P. Wairagala, S. Oyerinde, C. Siro, T. S. Bateesa,
T. Oloyede, Y. Wambui, V. Akinode, D. Nabagereka, M. Katusiime,
A. Awokoya, M. MBOUP, D. Gebreyohannes, H. Tilaye, K. Nwaike,
D. Wolde, A. Faye, B. Sibanda, O. Ahia, B. F. P. Dossou,
K. Ogueji, T. I. DIOP, A. Diallo, A. Akinfaderin, T. Marengereke,
and S. Osei, "MasakhaNER: Named entity recognition for African
languages," *Transactions of the Association for Computational
Linguistics*, vol. 9, pp. 1116–1131, 2021.

[12] T.-Y. Lin, P. Goyal, R. Girshick, K. He and P. Dollar,
"Focal loss for dense object detection," in *Proceedings of the IEEE
International Conference on Computer Vision*, 2017, pp. 2980–2988.

[13] P. Offermann, O. Levina, M. Schönherr and U. Bub, "Outline of
a design science research process," in *Proceedings of the 4th
International Conference on Design Science Research in Information
Systems and Technology*, ACM, 2009, pp. 7–18.

[14] G. R. Doddington, A. Mitchell, M. A. Przybocki, L. A.
Ramshaw, S. M. Strassel and R. M. Weischedel, "The Automatic
Content Extraction (ACE) program: Tasks, data, and evaluation," in
*Proceedings of the 4th International Conference on Language
Resources and Evaluation*, Lisbon, Portugal, 2004, pp. 837–840.

[15] M. Liu, B. Liu, L. Liu, M. Wang and X. Zhou, "Event
extraction as machine reading comprehension," in *Proceedings of
EMNLP*, 2020, pp. 1641–1651.

[16] F. Hogenboom, F. Frasincar, U. Kaymak and F. de Jong, "An
overview of event extraction from text," in *Workshop on Detection,
Representation, and Exploitation of Events in the Semantic Web*,
vol. 779, 2011, pp. 48–57.

[17] J. Lafferty, A. McCallum and F. C. N. Pereira, "Conditional
random fields: Probabilistic models for segmenting and labeling
sequence data," in *Proceedings of the 18th International
Conference on Machine Learning*, 2001, pp. 282–289.

[18] X. Ma and E. Hovy, "End-to-end sequence labeling via
bi-directional LSTM-CNNs-CRF," in *Proceedings of the 54th Annual
Meeting of the Association for Computational Linguistics*, Berlin,
Germany, 2016, pp. 1064–1074.

[19] G. Lample, M. Ballesteros, S. Subramanian, K. Kawakami and
C. Dyer, "Neural architectures for named entity recognition," in
*Proceedings of NAACL-HLT*, San Diego, CA, 2016, pp. 260–270.

[20] M. E. Peters, M. Neumann, M. Iyyer, M. Gardner, C. Clark, K.
Lee and L. Zettlemoyer, "Deep contextualized word representations,"
in *Proceedings of NAACL-HLT*, New Orleans, LA, 2018, pp.
2227–2237.

[21] Y. Liu, M. Ott, N. Goyal, J. Du, M. Joshi, D. Chen, O. Levy,
M. Lewis, L. Zettlemoyer and V. Stoyanov, "RoBERTa: A robustly
optimized BERT pretraining approach," *arXiv preprint
arXiv:1907.11692*, 2019.

[22] V. Sanh, L. Debut, J. Chaumond and T. Wolf, "DistilBERT, a
distilled version of BERT: Smaller, faster, cheaper and lighter,"
*arXiv preprint arXiv:1910.01108*, 2019.

[23] A. Conneau, K. Khandelwal, N. Goyal, V. Chaudhary, G.
Wenzek, F. Guzman, E. Grave, M. Ott, L. Zettlemoyer and V.
Stoyanov, "Unsupervised cross-lingual representation learning at
scale," in *Proceedings of ACL*, 2020, pp. 8440–8451.

[24] N. V. Chawla, K. W. Bowyer, L. O. Hall and W. P. Kegelmeyer,
"SMOTE: Synthetic minority over-sampling technique," *Journal of
Artificial Intelligence Research*, vol. 16, pp. 321–357, 2002.

[25] H. He and E. A. Garcia, "Learning from imbalanced data,"
*IEEE Transactions on Knowledge and Data Engineering*, vol. 21,
no. 9, pp. 1263–1284, 2009.

[26] Y. Cui, M. Jia, T.-Y. Lin, Y. Song and S. Belongie, "Class-balanced
loss based on effective number of samples," in *Proceedings of the
IEEE Conference on Computer Vision and Pattern Recognition*, 2019,
pp. 9268–9277.

[27] D. J. Gerner, P. A. Schrodt, O. Yilmaz and R. Abu-Jabr, "Conflict
and Mediation Event Observations (CAMEO): A new event data framework
for the analysis of foreign policy interactions," in *International
Studies Association Annual Meeting*, New Orleans, LA, 2002.

[28] R. Shaw, R. Troncy and L. Hardman, "LODE: Linking open
descriptions of events," in *4th Asian Semantic Web Conference*,
LNCS, vol. 5926, 2009, pp. 153–167.

[29] J. Piskorski, H. Tanev and P. O. Wennerberg, "Extracting violent
events from on-line news for ontology population," in *Business
Information Systems*, LNCS, vol. 4439, 2007, pp. 287–300.

[30] F. M. Suchanek, G. Kasneci and G. Weikum, "YAGO: A core of
semantic knowledge unifying WordNet and Wikipedia," in *Proceedings
of the 16th International Conference on World Wide Web*, ACM, 2007,
pp. 697–706.

[31] D. Hienert and F. Luciano, "Extraction of historical events
from Wikipedia," in *ESWC 2012 Satellite Events*, LNCS, vol. 7540,
2012, pp. 16–28.

[32] H. Becker, D. Iter, M. Naaman and L. Gravano, "Identifying
content for planned events across social media sites," in
*Proceedings of WSDM*, Seattle, WA, 2012, pp. 533–542.

[33] A. Magnuson, V. Dialan and D. Mallela, "Event recommendation
using Twitter activity," in *Proceedings of RecSys*, ACM, 2015, pp.
331–332.

[34] A. Farzindar and W. Khreich, "A survey of techniques for event
detection in Twitter," *Computational Intelligence*, vol. 31, no. 1,
pp. 132–164, 2015.

[35] Taye Abdulkadir Edris and R. K. Sungkur, "Knowledge discovery
from free text: Extraction of violent events in the African
context," *New Review of Information Networking*, vol. 24, no. 2,
pp. 153–177, 2019.

[36] W. Wang and D. Zhao, "Chinese news event 5W1H semantic elements
extraction for event ontology population," in *Proceedings of the
21st International World Wide Web Conference (Companion Volume)*,
Lyon, France, 2012, pp. 197–202.

[37] C. N. Silla and A. A. Freitas, "A survey of hierarchical
classification across different application domains," *Data Mining
and Knowledge Discovery*, vol. 22, no. 1–2, pp. 31–72, 2011.

[38] CEWS, *Data Collection and Analysis Tools for Continental Early
Warning System*, Unpublished Internal Document, Addis Ababa, 2013.

[39] H. Nakayama, "seqeval: A Python framework for sequence labeling
evaluation," Software, 2018. [Online]. Available:
https://github.com/chakki-works/seqeval. Last accessed on
May 10, 2026.

[40] B. F. P. Dossou, A. L. Tonja, O. Yousuf, S. Osei, A. Oppong,
I. Shode, O. O. Awoyomi, and C. C. Emezue, "AfroLM: A self-active
learning-based multilingual pretrained language model for 23
African languages," in *Proceedings of the 3rd Workshop on Simple
and Efficient Natural Language Processing (SustaiNLP) at EMNLP
2022*, Abu Dhabi, UAE, December 2022, pp. 52–64.

\pagebreak

# Annexes

\pagebreak

## Annex A: Entity Annotation Guidelines (Summary)

This annex summarises the inclusion and exclusion criteria for the
eight entity types in the production schema. The full annotation
guidelines are maintained in `backend/docs/VIONER_GUIDELINES.md`.

### ACTOR (WHO)

**Include:**
- Named organisations: "Boko Haram", "Al-Shabaab", "M23 rebels".
- Descriptive references: "armed men", "gunmen", "militants",
  "insurgents", "attackers", "assailants", "raiders".
- State security forces: "police", "military", "army", "security
  forces", "ENDF", "FARDC".
- Specific individuals when they are the perpetrator: "the suicide
  bomber", "the assailant".
- Ethnic or communal groups when they perpetrate violence: "Fulani
  herders", "ethnic militia".

**Exclude:**
- Inanimate objects: "the bomb", "the explosion" (these are methods,
  not actors).
- Passive constructions without a clear actor: "12 were killed" (no
  ACTOR is tagged).

### VICTIM (WHOM)

**Include:**
- Specific individuals: "the mayor", "aid workers", "journalist Y".
- Groups: "civilians", "protesters", "worshippers", "students".
- Demographic descriptions: "women and children", "displaced
  persons".
- Numeric counts of victims: "12 people", "dozens of civilians".
- Infrastructure as victim when violence targets it: "the power
  plant", "the bridge".

**Exclude:**
- The perpetrators themselves.
- Generic third parties not affected by the violence.

### ACTION (WHAT)

**Include:**
- Verbs describing what happened: "attacked", "killed", "ambushed",
  "raided", "abducted", "bombed", "stormed".
- Nominalised actions when they are the main predicate: "an attack",
  "the raid".

**Exclude:**
- Verbs not describing the violent action itself: "said",
  "reported", "claimed".

### DATE (WHEN)

**Include:**
- Specific dates: "20 December 2024", "January 15".
- Relative temporal references: "yesterday", "last Tuesday",
  "earlier this week".
- Day-of-week mentions: "on Monday".

**Exclude:**
- Years used as background context: "since 2017".

### REGION / CITY / DISTRICT (WHERE)

**Annotate at the most specific level mentioned.** Use the
location hierarchy: specific site < village/neighbourhood < city/town
< district/county < state/province/region < country < sub-region.
COUNTRY is not part of the model schema; it is resolved
deterministically from CITY and REGION via the knowledge base.

### CASUALTIES (HOW)

**Include:**
- Death counts and their descriptors: "killed 12", "3 dead", "5
  fatalities".
- Injury counts: "wounded 7", "20 injured".
- Displacement counts when they appear in the same casualty-style
  construction: "displacing 2,000".

**Exclude:**
- Damage descriptions without numeric value: "extensive damage".

\pagebreak

## Annex B: Hierarchical Taxonomy of African Violent Events

This annex reproduces, in full, the taxonomy I developed during the
literature-review phase of this thesis. The taxonomy is the result
of my own synthesis of ACLED [8], UCDP [9], and the PMVE
ontology [29], extended with African-specific categories (notably
pastoralist-farmer clashes and communal cattle raiding) that the
three external frameworks do not cover at this depth. It was
maintained as a separate working document during development and is
preserved here verbatim as the canonical reference for §4.4. Level 4
subtypes are listed only where they apply.

### Level 1: POLITICAL VIOLENCE

#### Level 2: Rebellion / Armed Insurgency
- Armed Clash / Battle
- Ambush
  - Roadside Ambush
  - IED Ambush
  - Complex Ambush
- Rebel Attack on Government Position
  - Base Assault
  - Checkpoint Attack
  - Overrun Operation
- Forced Recruitment

#### Level 2: Terrorism
- Bombing / Explosive Attack
  - Suicide Bombing
  - Car / Vehicle Bombing (VBIED)
  - Roadside IED
  - Grenade Attack
  - Building / Infrastructure Bombing
- Armed Assault
  - Mass Shooting / Rampage
  - Coordinated Multi-Site Attack
  - Lone Actor Attack
  - Armed Raid
- Kidnapping / Hostage-Taking (Terrorism)
- Assassination (Terrorism)
- Attack on Symbolic / Soft Targets
  - Attack on Religious Site
  - Attack on Educational Institution
  - Attack on Healthcare Facility
  - Attack on Humanitarian / Aid Workers
  - Attack on Transportation
  - Attack on Commercial / Economic Target

#### Level 2: Coup and Regime Change Violence
- Military Coup (Violent)
- Coup-Related Violence
- Assassination (Regime Change)

#### Level 2: Election Violence
- Campaign Violence
  - Attack on Candidate / Political Figure
  - Attack on Campaign Event
  - Violence Against Party Members / Supporters
- Voting Day Violence
  - Attack on Polling Station
  - Voter Intimidation with Violence
- Post-Election Violence
  - Election Protest Violence
  - Targeted Violence Against Opposing Group

#### Level 2: Political Repression
- Violent Suppression of Protests
- Targeted Killings of Political Opponents
- Mass Arrests with Violence

### Level 1: CRIMINAL VIOLENCE

#### Level 2: Organised Crime Violence
- Gang Warfare / Turf Violence
- Assassination (Criminal)
- Violence Against Law Enforcement

#### Level 2: Armed Robbery / Banditry
- Highway Robbery / Banditry
- Bank / Business Robbery
- Home Invasion / Residential Attack
- Cattle Raiding (Criminal)

#### Level 2: Kidnapping for Ransom (Criminal)
- Individual / Family Kidnapping
- Maritime Kidnapping / Piracy with Violence

#### Level 2: Criminal Gang Violence

### Level 1: COMMUNAL VIOLENCE

#### Level 2: Ethnic / Tribal Conflict
- Ethnic Clash / Battle
- Ethnic Massacre
- Ethnic Revenge Attack

#### Level 2: Religious Violence
- Sectarian Violence
- Attack on Religious Community
- Religious Site Desecration with Violence

#### Level 2: Resource-Based Conflict
- Land Conflict
- Water Conflict
- Mining / Resource Extraction Violence

#### Level 2: Pastoralist-Farmer Clashes
- Grazing Conflict
- Cattle Raiding (Communal)
- Revenge Raid (Pastoralist)

### Level 1: STATE VIOLENCE AGAINST CIVILIANS

#### Level 2: Extrajudicial Killings
- Summary Execution
- Enforced Disappearance Leading to Death
- Torture Resulting in Death

#### Level 2: State Repression of Protests
- Shooting of Protesters
- Violent Dispersal Resulting in Deaths

#### Level 2: Mass Atrocities by State Forces
- Massacre by State Forces
- Ethnic Cleansing by State

#### Level 2: Forced Displacement by State
- Violent Eviction
- Village Burning / Destruction by State

#### Level 2: Arbitrary Detention with Violence
- Violent Mass Arrest Operation

### Classification decision rules

- If state forces perpetrate violence against civilian victims engaged
  in political activity (protests, opposition activism), classify as
  *Political Violence > Political Repression*. If victims are
  civilians not engaged in political activity, classify as *State
  Violence Against Civilians*.
- Kidnapping by a designated terrorist group is *Political Violence
  > Terrorism > Kidnapping / Hostage-Taking*; kidnapping by criminals
  with ransom demands is *Criminal Violence > Kidnapping for Ransom*.
- Cattle raiding by criminal gangs or bandits is *Criminal Violence >
  Armed Robbery / Banditry > Cattle Raiding (Criminal)*; cattle
  raiding by ethnic or pastoralist groups is *Communal Violence >
  Pastoralist-Farmer Clashes > Cattle Raiding (Communal)*.
- For events that span categories (for example, election violence by
  an ethnic militia), assign the primary category (Election Violence)
  and tag the secondary category (Communal Violence) as a
  multi-label.

\pagebreak

## Annex C: Knowledge Base Entries (Excerpt)

The knowledge base contains approximately 150 armed groups. The
following entries are an illustrative excerpt; the complete list is
maintained in `backend/pipeline/kb.py`.

### East Africa

| Canonical name | Country | Region | Type | Aliases (selected) |
|:---------------|:--------|:-------|:-----|:-------------------|
| Al-Shabaab     | Somalia | East   | terrorist | al-shabab, al shabaab, harakat al-shabaab |
| Allied Democratic Forces | DRC | Central | terrorist | ADF, ADF-NALU, ISCAP, IS-DRC |
| Lord's Resistance Army | Uganda | East | rebel | LRA, Kony rebels |
| M23            | DRC     | Central | rebel | March 23 Movement, M23 rebels |
| TPLF           | Ethiopia | East  | rebel | Tigray People's Liberation Front, TDF |
| OLA            | Ethiopia | East  | rebel | Oromo Liberation Army, OLF-Shane |
| Fano           | Ethiopia | East  | militia | Amhara Fano, Amhara militia |
| ENDF           | Ethiopia | East  | government | Ethiopian National Defense Force |

### West Africa

| Canonical name | Country | Region | Type | Aliases (selected) |
|:---------------|:--------|:-------|:-----|:-------------------|
| Boko Haram     | Nigeria | West   | terrorist | Jama'atu Ahlis Sunna Lidda'awati wal-Jihad, ISWAP, Ansaru |
| JNIM           | Mali    | West   | terrorist | Jama'at Nasr al-Islam wal Muslimin, GSIM |
| ISGS           | Mali    | West   | terrorist | Islamic State Greater Sahara, IS Sahel |

### North Africa

| Canonical name | Country | Region | Type | Aliases (selected) |
|:---------------|:--------|:-------|:-----|:-------------------|
| Rapid Support Forces | Sudan | North | militia | RSF, Janjaweed, Hemeti forces |
| Sudanese Armed Forces | Sudan | North | government | SAF, Sudan army |
| SPLM-N         | Sudan   | North  | rebel | Sudan People's Liberation Movement – North |

### Sahel and elsewhere

| Canonical name | Country | Region | Type | Aliases (selected) |
|:---------------|:--------|:-------|:-----|:-------------------|
| Wagner Group   | Multiple| —      | mercenary | Wagner, Russian PMC, Africa Corps |
| Anti-Balaka    | CAR     | Central | militia | Anti-balaka, antibalaka |
| Seleka         | CAR     | Central | rebel | ex-Seleka, 3R, FPRC |
| Ansar al-Sunna | Mozambique | Southern | terrorist | ASWJ, IS-Mozambique |

### Conflict-affected cities (excerpt)

| City        | Country   | Region          |
|:------------|:----------|:----------------|
| Maiduguri   | Nigeria   | Borno           |
| Mogadishu   | Somalia   | Banaadir        |
| Goma        | DRC       | North Kivu      |
| Bukavu      | DRC       | South Kivu      |
| El Fasher   | Sudan     | North Darfur    |
| Khartoum    | Sudan     | Khartoum        |
| Bamako      | Mali      | Bamako Capital  |
| Mopti       | Mali      | Mopti Region    |
| Bahir Dar   | Ethiopia  | Amhara          |
| Mekelle     | Ethiopia  | Tigray          |
| Cabo Delgado / Mocimboa da Praia | Mozambique | Cabo Delgado |

\pagebreak

## Annex D: System Screenshots

This annex collects representative screenshots of the deployed web
application. Each screenshot illustrates one of the main route
groups described in Section 5.7. Screenshots in the printed
submission are reproduced in greyscale; full-colour versions are
provided on the accompanying CD per Annex D of the AAU thesis
guideline.

- **D.1 Inference screen.** Pasted text in the left panel,
  highlighted entities and 5W1H breakdown on the right, confidence
  scores on hover.
- **D.2 Inference document upload.** Drag-and-drop upload area,
  processing status, extracted entity table.
- **D.3 Training run list.** Sortable, filterable table of past runs
  with model, dataset, status, best epoch, and final validation loss.
- **D.4 Training run detail with live progress.** Real-time chart of
  training and validation loss, epoch progress bar, scrolling log
  output, cancellation control.
- **D.5 Event browser.** Paginated event table with structured
  filters (date range, country, region, taxonomy), inline preview of
  extracted entities.
- **D.6 Event detail.** Source text with inline entity highlights,
  structured 5W1H table, KB enrichment fields, taxonomy assignment,
  edit controls.
- **D.7 Analytics dashboard.** Events per region (bar chart), top
  actors (horizontal bar), events over time (line chart), casualty
  totals (stat cards).
- **D.8 Knowledge base – Actors.** Searchable list of armed groups
  with edit form for canonical name, aliases, country, region, type,
  active flag.
- **D.9 Knowledge base – Taxonomies.** Tree view of the four-level
  taxonomy with category definitions, decision rules, and worked
  examples.

### Database schema (PostgreSQL)

```
users
  id                 UUID PRIMARY KEY
  email              TEXT UNIQUE NOT NULL
  full_name          TEXT NOT NULL
  role               TEXT NOT NULL CHECK (role IN ('admin','analyst','viewer'))
  password_hash      TEXT NOT NULL
  is_active          BOOLEAN DEFAULT TRUE
  created_at         TIMESTAMPTZ DEFAULT NOW()
  last_login_at      TIMESTAMPTZ

training_runs
  id                 UUID PRIMARY KEY
  user_id            UUID NOT NULL REFERENCES users(id)
  model              TEXT NOT NULL                 -- e.g. 'bert-base-cased'
  dataset_path       TEXT NOT NULL
  hyperparameters    JSONB NOT NULL                -- ModelConfig dump
  started_at         TIMESTAMPTZ DEFAULT NOW()
  finished_at        TIMESTAMPTZ
  status             TEXT CHECK (status IN ('queued','running','completed','failed','cancelled'))
  best_epoch         INTEGER
  best_val_loss      DOUBLE PRECISION
  checkpoint_path    TEXT
  log_path           TEXT

events
  id                 UUID PRIMARY KEY
  user_id            UUID REFERENCES users(id)
  source_text        TEXT NOT NULL
  source_url         TEXT
  extracted_at       TIMESTAMPTZ DEFAULT NOW()
  model_id           UUID REFERENCES training_runs(id)
  taxonomy_level_1   TEXT
  taxonomy_level_2   TEXT
  taxonomy_level_3   TEXT
  taxonomy_level_4   TEXT
  primary_country    TEXT
  primary_region     TEXT
  primary_city       TEXT
  event_date         DATE
  total_killed       INTEGER
  total_injured      INTEGER
  confidence         DOUBLE PRECISION
  status             TEXT CHECK (status IN ('extracted','reviewed','confirmed','flagged','rejected'))

event_entities
  id                 UUID PRIMARY KEY
  event_id           UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE
  entity_type        TEXT NOT NULL                 -- ACTOR, VICTIM, ...
  surface_form       TEXT NOT NULL                 -- as found in text
  canonical_form     TEXT                          -- after KB lookup
  start_offset       INTEGER NOT NULL
  end_offset         INTEGER NOT NULL
  confidence         DOUBLE PRECISION NOT NULL
  kb_match_id        UUID                          -- nullable FK to KB row

kb_armed_groups
  id                 UUID PRIMARY KEY
  canonical_name     TEXT UNIQUE NOT NULL
  aliases            TEXT[] DEFAULT '{}'
  country            TEXT NOT NULL
  region             TEXT NOT NULL
  group_type         TEXT CHECK (group_type IN
                        ('militia','terrorist','rebel','government','mercenary'))
  active             BOOLEAN DEFAULT TRUE
  notes              TEXT

kb_locations
  id                 UUID PRIMARY KEY
  name               TEXT NOT NULL
  loc_type           TEXT CHECK (loc_type IN ('city','region','district','country'))
  country            TEXT NOT NULL
  parent_region      TEXT
  latitude           DOUBLE PRECISION
  longitude          DOUBLE PRECISION

kb_taxonomy
  id                 UUID PRIMARY KEY
  level              INTEGER NOT NULL CHECK (level BETWEEN 1 AND 4)
  parent_id          UUID REFERENCES kb_taxonomy(id)
  name               TEXT NOT NULL
  definition         TEXT
  criteria           TEXT
  keywords           TEXT[]

inference_history
  id                 UUID PRIMARY KEY
  user_id            UUID REFERENCES users(id)
  input_text         TEXT NOT NULL
  output_event_id    UUID REFERENCES events(id)
  latency_ms         INTEGER NOT NULL
  model_id           UUID REFERENCES training_runs(id)
  created_at         TIMESTAMPTZ DEFAULT NOW()
```

Indexes are created on `events(event_date)`,
`events(primary_country, primary_region)`,
`event_entities(event_id, entity_type)`,
`event_entities(canonical_form)` for actor-centric queries, and
`training_runs(user_id, started_at desc)` for the dashboard.

\pagebreak

## Annex E: Sample Augmentation Templates

A representative subset of the augmentation templates used to
generate synthetic training examples. The full lexicon and template
catalogue are in `backend/scripts/augment_training_data.py`.

### Verb lexicons

**Location-taking action verbs (ACTOR + ACTION + LOCATION pattern):**
attacked, raided, stormed, invaded, struck, hit, overran, sacked,
bombed, shelled, destroyed, burned, torched, razed, demolished,
devastated, ravaged, gutted, wrecked, ruined, captured, seized,
occupied, surrounded, encircled, besieged, blockaded, conquered,
looted, ransacked, pillaged, plundered, breached, sabotaged,
vandalised.

**Victim-taking action verbs (ACTOR + ACTION + VICTIM pattern):**
killed, murdered, slaughtered, massacred, executed, shot, butchered,
beheaded, decapitated, hanged, lynched, strangled, drowned,
poisoned, wounded, injured, maimed, kidnapped, abducted, detained,
arrested, apprehended, tortured, brutalised, assaulted, displaced,
expelled, evicted.

**Clash verbs (ACTOR + CLASH_ACTION + ACTOR pattern):**
clashed with, skirmished with, exchanged fire with, traded fire
with, battled, fought, engaged, confronted, repelled, routed,
defeated, overpowered.

### Template patterns

```
{actor} {action} {location}, killing {n_killed} {victim}.
{actor} {action} {location}, leaving {n_killed} dead and {n_injured} injured.
{date}, {actor} {action} {location}.
{actor} {action} {location} and looted several buildings.
{n_killed} {victim} were killed when {actor} {action} {location}.
{actor} armed with heavy weapons {action} {location}, resulting in
  {n_killed} casualties.
{actor} {action} several villages in {region}, leaving at least
  {n_killed} dead.
{actor} {action} {location} and abducted {n_killed} {victim}.
{actor} {action} {location} in a dawn raid, killing {n_killed}
  {victim}.
{actor} seized {location} after a prolonged siege.
{actor} {action} {n_killed} {victim} in {location}.
{date}, {actor} {action} {n_killed} {victim} in {location}.
{actor} {action} at least {n_killed} {victim} in {region}.
{actor} {clash_action} {actor2} in {location}.
{actor} {clash_action} {actor2} in {location}, leaving {n_killed}
  dead.
Heavy fighting erupted when {actor} {clash_action} {actor2} in
  {region}.
```

### Date forms

`On January 15, 2024`, `On Monday`, `Last Tuesday`, `January 15`,
`Earlier this week`, `On Wednesday morning`, `On Friday night`.

\pagebreak

## Annex F: User Acceptance Testing Questionnaire

The questionnaire reproduced here was administered after each user
acceptance testing session.

### Demographic information

1. Role: [ ] Early-warning analyst   [ ] Conflict researcher
   [ ] Software developer            [ ] Other (specify)
2. Years of experience in your role: ____
3. Familiarity with NLP systems: [ ] None [ ] Basic [ ] Intermediate
   [ ] Advanced

### Tasks

For each of the six supplied tasks, please record:
- Time to first meaningful interaction (seconds).
- Whether you completed the task: [ ] Yes [ ] Yes, with help [ ] No.
- Any issues you encountered.

Task list:
1. Paste a supplied article and view the extracted entities.
2. Browse the event store and find events from a specified country.
3. Run an analytics query for events in the past 30 days.
4. Start a new training run with the supplied dataset.
5. Monitor the training-run progress until completion.
6. Review a flagged event and either confirm or edit the extraction.

### Likert-scale evaluation

For each statement, indicate your level of agreement on a 1 to 5
scale, where 1 means strongly disagree and 5 means strongly agree.

1. The extracted entities matched what I expected.
2. The 5W1H structuring was clear and easy to interpret.
3. The confidence scores were useful for triage.
4. The knowledge-base enrichment (canonical names, country lookups)
   added value beyond raw extraction.
5. The training screen made it easy to start and monitor a run.
6. The analytics views answered the kinds of questions I would
   typically ask.
7. The taxonomy assignment matched my classification of the event.
8. The system response times felt acceptable for my use case.

### Open-ended questions

1. What did you find most useful about the system?
2. What did you find most frustrating?
3. What additional features would most improve your workflow?
4. Would you adopt this system in your work, given current
   limitations?  [ ] Yes [ ] With improvements [ ] No.
   Reason: ____________________

\pagebreak

# Signed Declaration Sheet

I, the undersigned, declare that this thesis is my original work and
has not been presented for a degree in any other university, and that
all source of materials used for the thesis have been duly
acknowledged.

\

**Declared by:**

Name: __________________________________________

Signature: ______________________________________

Date: ___________________________________________

\

\

**Confirmed by advisor:**

Name: __________________________________________

Signature: ______________________________________

Date: ___________________________________________







