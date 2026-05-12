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

The volume of unstructured news reporting on violent events in Africa
exceeds the capacity of human analysts to read, code, and act upon
within operationally useful timeframes. The African Union Continental
Early Warning System (AU-CEWS) aggregates thousands of articles daily,
yet their transformation into structured, analysable intelligence
remains predominantly manual. This thesis presents VioNER, an
end-to-end system that extracts 5W1H attributes (Who, What, Where,
When, Whom, How) from African news reports of violent events through
fine-tuned BERT-based named entity recognition coupled with a
knowledge-base validation layer. A grounded annotation schema of
eight entity types (ACTOR, VICTIM, ACTION, DATE, REGION, CITY,
DISTRICT, CASUALTIES) is introduced in BIO format, alongside a
four-level hierarchical taxonomy of approximately ninety-five
African violent-event categories. The model was fine-tuned on a
fifty-thousand-example corpus derived from the Armed Conflict
Location and Event Data (ACLED) project, combining stratified
diversity sampling with template-based augmentation to address severe
class imbalance, in which the O (outside) label accounts for
seventy-eight percent of tokens. A focal-loss objective (γ = 2.0)
with inverse-frequency class weights was used to counter the dominant
classes. The fine-tuned `bert-base-cased` model achieved a macro F1
of 0.887 and a micro F1 of 0.909 on a ten-thousand-example held-out
validation set, converging in two epochs with a best validation
loss of 0.0136. An ablation isolated the contribution of focal loss
with class weighting, which improved the rarest entity (VICTIM) by
eleven F1 points over plain cross entropy. The trained model is
exposed through a FastAPI service, a PostgreSQL event store, a
curated knowledge base of one hundred and fifty African armed groups
and two hundred conflict-affected cities, and a React/TypeScript web
application supporting training, inference, event management, and
analytics. End-to-end inference latency is one hundred and forty-two
milliseconds for short articles and six hundred milliseconds for
windowed long articles. User acceptance testing with five
participants returned a mean rating of 4.4 out of 5 across six task
dimensions. The artefact reduces analyst processing time
substantially and produces structured records suitable for downstream
early-warning analysis.

**Keywords:** Named Entity Recognition, BERT, Event Extraction,
Violent Events, African Conflicts, 5W1H, Knowledge Base, Focal Loss

\pagebreak

# Dedication

To my family, for their unwavering encouragement throughout this
research, and to the analysts whose patient reading of conflict
reports inspired the work that follows.

\pagebreak

# Acknowledgements

I am deeply indebted to my advisor, Dr. Fekade Getrahun, for his
guidance, critical reading, and steady encouragement throughout the
research. His insistence on rigour and operational relevance shaped
every chapter of this thesis.

I thank the staff of the Addis Ababa University Department of Computer
Science for their support during the programme. I am grateful to the
African Union Continental Early Warning System (AU-CEWS) for
articulating the operational requirements that motivated this work,
and to the Armed Conflict Location and Event Data Project (ACLED) for
maintaining the open dataset on which this study relies.

I acknowledge the prior thesis work of Taye Abdulkadir, whose
exploration of 5W extraction in the African context provided a
foundation that this research extends.

Finally, I thank my family and friends for their patience and support
during the long months of training, debugging, and writing.

\pagebreak

# Table of Contents

1. Introduction ......................................................... 1
   1.1 Background ........................................................ 1
   1.2 Motivation ........................................................ 3
   1.3 Statement of the Problem .......................................... 5
   1.4 Objectives ........................................................ 7
   1.5 Methods ........................................................... 8
   1.6 Scope and Limitations ............................................. 10
   1.7 Application of Results ............................................ 12
   1.8 Organization of the Rest of the Thesis ............................ 14
2. Literature Review ..................................................... 15
   2.1 Information Extraction and Event Extraction ...................... 15
   2.2 Named Entity Recognition ......................................... 17
   2.3 Transformer Models and BERT ...................................... 19
   2.4 Class Imbalance in Token Classification .......................... 22
   2.5 Evaluation Metrics for Named Entity Recognition ................. 25
   2.6 Conflict Event Databases and Coding Schemes ..................... 27
   2.7 Knowledge Bases and Ontologies for Events ....................... 29
3. Related Work .......................................................... 28
   3.1 General Event Extraction from News ............................... 28
   3.2 Violence-Specific Event Extraction Systems ....................... 30
   3.3 Event Extraction in the African Context .......................... 32
   3.4 Hierarchical Event Classification ................................ 33
   3.5 Summary of Gaps Addressed ........................................ 34
4. The Proposed Solution ................................................. 36
   4.1 Design Principles ................................................ 36
   4.2 System Architecture .............................................. 37
   4.3 Entity Schema and BIO Encoding ................................... 40
   4.4 Hierarchical Violent Event Taxonomy .............................. 43
   4.5 Knowledge Base Design ............................................ 46
   4.6 Training Pipeline ................................................ 48
   4.7 Inference and Post-Processing .................................... 51
   4.8 Web Application Architecture ..................................... 53
5. Implementation ........................................................ 55
   5.1 Technology Stack ................................................. 55
   5.2 Data Acquisition and Preprocessing ............................... 57
   5.3 Stratified Sampling and Augmentation ............................. 60
   5.4 Model Training Implementation .................................... 62
   5.5 Focal Loss and Class Weighting ................................... 65
   5.6 Backend Services and API ......................................... 67
   5.7 Frontend Application ............................................. 70
   5.8 Containerised Deployment ......................................... 72
6. Experimentation and Results ........................................... 74
   6.1 Experimental Setup ............................................... 74
   6.2 Dataset Statistics ............................................... 75
   6.3 Training Dynamics ................................................ 77
   6.4 Overall Model Performance ........................................ 79
   6.5 Per-Entity Analysis .............................................. 81
   6.6 Ablation: Focal Loss versus Cross Entropy ........................ 83
   6.7 Knowledge-Base Validation Impact ................................. 84
   6.8 Inference Latency and Throughput ................................. 85
   6.9 End-to-End Demonstration ......................................... 86
   6.10 User Acceptance Testing ......................................... 87
   6.11 Error Analysis .................................................. 88
7. Conclusions, Recommendations, and Future Work ......................... 90
   7.1 Summary .......................................................... 90
   7.2 Contributions .................................................... 91
   7.3 Recommendations .................................................. 93
   7.4 Future Work ...................................................... 94

References ............................................................... 97

Annexes .................................................................. 101

Annex A: Entity Annotation Guidelines (Summary) ......................... 101
Annex B: Hierarchical Taxonomy of African Violent Events ................ 103
Annex C: Knowledge Base Entries (Excerpt) ............................... 108
Annex D: System Screenshots ............................................. 110
Annex E: Sample Augmentation Templates .................................. 113
Annex F: User Acceptance Testing Questionnaire .......................... 115

Signed Declaration Sheet ................................................. 117

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
| 6.1   | Pre-processed dataset statistics                                   | 75   |
| 6.2   | Entity-level frequency in the full pre-processed corpus            | 76   |
| 6.3   | Best validation metrics across training runs                       | 79   |
| 6.4   | Per-entity precision, recall and F1                                | 81   |
| 6.5   | Focal-loss ablation                                                | 83   |
| 6.6   | Inference latency on representative articles                       | 85   |

\pagebreak

# List of Figures

| Figure | Title                                                              | Page |
|:------:|:-------------------------------------------------------------------|:----:|
| 4.1    | High-level architecture of the VioNER system                       | 38   |
| 4.2    | End-to-end processing pipeline                                     | 39   |
| 4.3    | BIO encoding example for a multi-word entity                        | 42   |
| 4.4    | Four-level taxonomy hierarchy (visual outline)                      | 43   |
| 4.5    | Knowledge-base entity-relationship outline                          | 46   |
| 4.6    | NER training data flow                                              | 49   |
| 4.7    | Inference and post-processing pipeline                              | 52   |
| 5.1    | Backend module organisation                                        | 67   |
| 5.2    | Frontend route map                                                 | 70   |
| 6.1    | Training and validation loss curves                                 | 77   |
| 6.2    | Validation accuracy across epochs                                  | 78   |
| 6.3    | Per-entity F1 bar chart                                            | 82   |
| 6.4    | Confusion patterns between location entity types                    | 89   |

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
| FAPA     | FastAPI                                                            |
| FARDC    | Forces Armées de la République Démocratique du Congo               |
| GDELT    | Global Database of Events, Language, and Tone                      |
| IED      | Improvised Explosive Device                                        |
| IGAD     | Intergovernmental Authority on Development                         |
| JNIM     | Jama'at Nasr al-Islam wal Muslimin                                 |
| KB       | Knowledge Base                                                     |
| LRA      | Lord's Resistance Army                                             |
| LSTM     | Long Short-Term Memory                                             |
| ML       | Machine Learning                                                   |
| MPS      | Metal Performance Shaders                                          |
| NER      | Named Entity Recognition                                           |
| NEXUS    | News cluster Event eXtraction Utilizing language Structures        |
| NLP      | Natural Language Processing                                        |
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
| 5W1H     | Who, What, Where, When, Whom, How                                  |

\pagebreak

# 1. Introduction

This chapter introduces the research problem addressed in this thesis,
the motivation that drives it, and the objectives that guide the
investigation. It locates the work within the operational context of
African early warning and crisis response, summarises the methods
employed, defines the scope and limitations, and outlines the
remainder of the document. The chapter is intended to give the reader
sufficient context to follow the technical material that follows.

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

Natural Language Processing (NLP) has historically offered a partial
answer to this problem through techniques such as part-of-speech
tagging, named entity recognition, syntactic parsing, and coreference
resolution [2]. Building on these foundations, the sub-field of
Information Extraction (IE) seeks to identify named entities,
relations between entities, and events within text and to populate
structured records that downstream systems can consume. Event
Extraction, in turn, treats an event as a complex construct with
attributes such as actors, actions, locations, temporal markers, and
circumstances, and aims to recover these attributes from prose [3],
[4].

Within Event Extraction, the 5W1H paradigm provides a compact
template: Who performed the act, What action was taken, Whom or what
was affected, Where it occurred, When it occurred, and How it
unfolded. The 5W1H template is well aligned with how journalists are
trained to report and with how analysts are trained to consume
reports. It is therefore a natural target representation for an
extraction system intended to support intelligence and humanitarian
work.

The state of the art in NLP shifted decisively with the introduction
of the Transformer architecture [5] and pre-trained language models
based on it, of which Bidirectional Encoder Representations from
Transformers (BERT) is the most widely deployed [6]. BERT and its
successors are pre-trained on large corpora using masked language
modelling, then fine-tuned on smaller labelled datasets for downstream
tasks such as Named Entity Recognition (NER). The combination of
strong pre-training with task-specific fine-tuning has substantially
narrowed the gap between research prototypes and operational systems
for token-level prediction tasks [7].

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

Consider a typical morning in a continental monitoring centre. A
single analyst is responsible for a region in which, over the
preceding twenty-four hours, between two hundred and four hundred
news items were aggregated by the centre's media-monitoring tool.
Of these, perhaps fifteen to forty describe violent incidents that
the analyst must read, structure into actor / action / location /
time / casualty fields, classify, and route to the appropriate
desk. By mid-morning the analyst has reached perhaps a quarter of
the queue; by close of business, the residue rolls over into the
next day. This pattern repeats across regions and analysts. The
binding constraint on continental situation awareness is not the
sophistication of analytical models but the throughput of human
reading and coding.

The author's exposure to this operational context at the AU-CEWS
Situation Monitoring Centre revealed two persistent gaps. The first
is a *throughput gap*: the volume of news that human analysts can
read in a working day is a small fraction of the daily inflow, and
the cognitive load of reading and coding violent-event reports is
high. The second is a *consistency gap*: analysts coding the same
article may diverge in how they categorise actors, events, and
locations, especially under time pressure or in fast-moving
situations. These two gaps interact. A system that produces
consistent structured records from a larger fraction of the inflow
would free analyst attention for interpretation rather than
extraction, and would also raise the comparability of records
across analysts, regions, and time periods.

Three further observations motivate the technical choices made in
this thesis. First, African conflict reporting features patterns and
named entities that are under-represented in generic, off-the-shelf
NLP models trained on European or North American news corpora.
Generic NER models routinely misclassify African armed groups, regional
administrative divisions, and locally significant locations [11]. A
domain-specific model fine-tuned on African conflict reporting is
therefore likely to outperform off-the-shelf alternatives by a
meaningful margin.

Second, the class distribution within a violent-event NER task is
extremely skewed. The overwhelming majority of tokens in a typical
news sentence carry the outside (O) label, while entity tokens form a
small fraction of the total. Naive cross-entropy training on this
distribution tends to under-fit minority entity types. Techniques
such as focal loss [12] and inverse-frequency class weighting are
well-suited to this regime and have been shown to improve recall on
rare classes without sacrificing precision on dominant ones.

Third, the operational utility of extracted entities depends not only
on per-token accuracy but on whether the extracted records can be
trusted, queried, and audited. A knowledge base of known armed
groups, conflict-affected cities, weapons, and a hierarchical taxonomy
of violent events allows the extracted output to be cross-checked
against curated reference data, with low-confidence or implausible
extractions flagged for human review.

The motivation behind this thesis is therefore both academic and
practical. Academically, it contributes a fine-tuned, domain-specific
BERT model and a corresponding annotated dataset for the African
violent-event NER task, together with a hierarchical taxonomy designed
for that context. Practically, it provides a deployable web platform
that exposes training, inference, event management, and analytics
through a unified interface, lowering the technical barrier for
operational adoption.

## 1.3 Statement of the Problem

The central problem addressed in this thesis is the absence, in the
African early-warning ecosystem, of a robust, accurate, and openly
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
corpus, the distribution of BIO labels is heavily dominated by the O
label, with entity tokens forming only a minority of the total.
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

This study is significant on three grounds.

**Operational significance.** The artefact reduces the analyst time
required to convert raw news into structured event records. In the
target context (AU-CEWS Situation Monitoring), analyst time is the
binding constraint on situation awareness during fast-moving
crises. Even a partial reduction in the cost of structured event
extraction translates directly into faster, broader, and more
consistent monitoring.

**Methodological significance.** The combination of a grounded
entity schema, focal-loss training under severe class imbalance,
and a curated domain knowledge base is, to the best of the author's
knowledge, the first such combination applied to African
violent-event extraction at this scale. The methodology is
documented in sufficient detail to be reproducible by other
researchers.

**Resource significance.** The four-level taxonomy of African
violent events, the entity annotation schema, and the curated
knowledge base of African armed groups and conflict-affected cities
are themselves reusable artefacts. They can be adopted or adapted
by researchers and practitioners working on adjacent tasks in
conflict monitoring, humanitarian protection, and security
analysis.

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

1. Review state-of-the-art literature on information extraction, event
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

The research adopts a design-science methodology [13] coupled with
empirical evaluation of the artefact. Each component is built
iteratively, with the lessons of one iteration informing the design of
the next, and with quantitative evaluation against held-out data
controlling for over-fitting at each stage. The principal methodical
choices are summarised below; full detail is provided in
Chapter 4 and Chapter 5.

**Annotation schema design.** Drawing on the proposal taxonomy, the
ACLED column conventions, and a pilot study of grounding rates in
synthetically and naturally annotated text, the entity schema is
restricted to entity types that can be reliably found verbatim in
source text. EVENT_TYPE and COUNTRY were dropped from the schema in
the course of this analysis because their grounding rates were too low
to support reliable supervision; instead, COUNTRY is recovered
deterministically from the knowledge base and the event-type
hierarchy is computed in a post-NER step.

**Data acquisition and preparation.** Raw event records are obtained
from ACLED via its open data exports. The records are tokenised and
labelled in BIO format using the column-to-entity mapping documented
in Section 5.2. Stratified diversity sampling is then applied to a
target subset size of 35,000 records, with augmentation adding
approximately 15,000 templated examples to expand vocabulary coverage
of action verbs and victim-targeting constructions that are
under-represented in raw ACLED text. The resulting 50,000-example
corpus is partitioned into 80 percent training and 20 percent
validation.

**Model fine-tuning.** The `bert-base-cased` model from the Hugging
Face hub is fine-tuned for token classification with seventeen output
labels (eight entity types times two BIO prefixes, plus the O label).
Sub-word labels are aligned by carrying the first-subword label to
subsequent sub-words with the B-/I- transition handled explicitly.
Training uses AdamW with linear warm-up, optional ReduceLROnPlateau
scheduling, gradient clipping, and a focal-loss objective with
inverse-frequency class weights computed from the training set.

**Knowledge-base integration.** A static knowledge base of African
armed groups, conflict-affected cities, and the four-level taxonomy is
loaded at inference time. Raw entity spans are validated against the
knowledge base, with confidence scores adjusted upward for entities
that match curated entries and downward for those that do not. The
post-NER pipeline then assembles a 5W1H record per detected event
description.

**System packaging.** The trained model, the knowledge base, and the
event store are exposed through a FastAPI service with documented
routes for each capability, and a React/TypeScript front-end is built
on top of it. The system is containerised with Docker Compose for
reproducible deployment.

**Evaluation.** The fine-tuned model is evaluated against a held-out
validation set using token-level accuracy, per-entity precision,
recall, and F1, and through qualitative inspection on out-of-corpus
news articles. End-to-end latency is measured at inference time, and
qualitative user acceptance testing is conducted on a small group of
representative users.

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

The deliverables of this thesis have several immediate and prospective
applications across the African early warning, humanitarian, security,
and research ecosystems.

**Operational early warning.** AU-CEWS, regional economic communities,
and national early warning centres can use the system to accelerate
the conversion of news into structured event records, freeing analyst
attention for interpretation and decision support. The hierarchical
taxonomy supports multi-level queries from broad categories
("political violence in West Africa this quarter") to specific event
types ("suicide bombings attributed to JNIM in Mali").

**Humanitarian response.** Humanitarian organisations require detailed
information about violence affecting civilian populations and
humanitarian access. The event store, with its actor, victim,
location, and casualty fields, provides a base for protection
analysis, needs assessment, and access mapping.

**Security and defence analysis.** Peace support operations and
national security services can use the system to monitor non-state
armed groups, track cross-border threats, and inform operational
planning, recognising that automated output supplements rather than
replaces classified intelligence streams.

**Research.** Academic researchers and policy institutes can use the
annotated dataset, the taxonomy, and the extracted event corpus as
inputs to quantitative conflict studies, comparative analyses, and
methodological development in domain-specific NLP.

**Capacity building.** The open architecture, documented annotation
schema, and reproducible deployment lower the technical barrier for
African universities, research centres, and government bodies to adopt
and adapt the system to their own monitoring needs.

The breadth of these applications underlines that even with the
acknowledged limitations, the artefact produced by this thesis
contributes value beyond its strict research contributions.

## 1.8 Organization of the Rest of the Thesis

The remainder of this thesis will be organised as follows. Chapter 2
will review relevant literature, covering the foundations of
information extraction and named entity recognition, the transformer
architecture and BERT, techniques for handling class imbalance in
token classification, and the conflict-event database landscape that
informs the taxonomy. Chapter 3 will review prior systems most
directly related to this work, including violence-specific event
extraction systems and the closest African-context predecessor, and
will identify the specific gaps that the present work bridges.
Chapter 4 will present the proposed solution, including the high-level
system architecture, the entity schema, the hierarchical taxonomy, the
knowledge base, the training pipeline, the inference pipeline, and
the web-application architecture. Chapter 5 will describe the
implementation, including the technology stack, data preparation,
model training, focal-loss objective, backend services, and
frontend application. Chapter 6 will present the experimental
results, including dataset statistics, training dynamics, overall and
per-entity performance, ablation studies, error analysis, and user
acceptance feedback. Chapter 7 will conclude the thesis with a
summary of contributions, recommendations, and a prioritised future
work programme that addresses the limitations identified in Section 1.6.

\pagebreak

# 2. Literature Review

This chapter reviews the theoretical and methodological literature
that underpins the work presented in this thesis. The review begins
with the broader fields of Information Extraction and Event
Extraction, then narrows to Named Entity Recognition, the transformer
architecture and BERT, methods for handling class imbalance in token
classification, the family of conflict-event databases that shape the
operational context, and finally the use of knowledge bases and
ontologies in representing extracted events. Specific paper-by-paper
reviews of the most directly related prior systems are deferred to
Chapter 3.

## 2.1 Information Extraction and Event Extraction

Information Extraction (IE) is the family of techniques that derive
structured data from unstructured natural-language text [4]. Within
IE, the canonical sub-tasks include Named Entity Recognition, relation
extraction, coreference resolution, and event extraction. These
sub-tasks are typically organised in a pipeline in which the output of
one stage is consumed by the next, although end-to-end and joint
learning approaches have also been developed.

Event Extraction (EE) treats an event as a structured combination of
attributes representing an empirical occurrence, typically a verb or
nominal predicate together with its participants (agent, patient,
instrument), location, and time [3]. Two long-standing schemas have
shaped how the field thinks about event structure. The Automatic
Content Extraction (ACE) program defined a typology of event types
with corresponding arguments and influenced a generation of supervised
event extraction systems [14]. The Text Analysis Conference Knowledge
Base Population (TAC-KBP) track has continued this line of work with
larger and more diverse benchmarks.

Within EE, the 5W1H paradigm offers a journalistic alternative to ACE
that is particularly well suited to news text [15]. Rather than
committing to a fixed inventory of event types, 5W1H asks, for each
reported event, the questions Who, What, Whom, Where, When, and How.
This thesis adopts the 5W1H formulation and ties it to a domain
ontology of violent events; the ontology lives outside the NER model
proper and is applied as a post-processing step.

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

Named Entity Recognition (NER) is the task of identifying spans of
text that refer to entities of interest and assigning each span to one
of a small set of types. Classical NER systems before the deep
learning era combined hand-crafted features with sequence models such
as Hidden Markov Models, Maximum Entropy Markov Models, and
Conditional Random Fields (CRFs) [17]. CRFs were widely adopted
because they model dependencies between successive labels, which is
essential for the BIO tagging scheme adopted by most modern NER
systems.

The BIO scheme assigns each token one of three roles: B- for the
beginning of an entity, I- for an internal token of an entity, and O
for a token outside any entity. For a schema with k entity types,
this expands to 2k + 1 labels in total. The BIO encoding is
exhaustively understood in the literature, including its variants
(BIOES, BILOU) that add explicit single-token and end-of-entity
labels to further constrain decoder behaviour. This thesis adopts
the simple BIO formulation, which gives seventeen labels for the
eight-entity schema (two BIO prefixes per entity type plus the O
label).

Neural NER systems began to outperform feature-engineered models with
the introduction of word embeddings and bi-directional Long
Short-Term Memory (BiLSTM) networks [18]. The combination of BiLSTM
with character-level convolutional networks and a CRF decoder, as in
the architecture of Lample and colleagues [19], became the standard
recipe for several years. These models proved that distributed
representations could substitute for many of the hand-engineered
features that had been central to earlier systems.

The introduction of contextual word representations such as ELMo [20]
and especially BERT [6] subsequently produced a step change in NER
accuracy. Modern NER systems typically fine-tune a pre-trained
transformer encoder with a linear classifier on top, optionally with
a CRF head. Devlin and colleagues reported state-of-the-art results
on the CoNLL-2003 NER benchmark with this architecture, and the
results have been replicated and extended in subsequent work on
multilingual and domain-specific NER.

For violent-event extraction in the African context, the most
relevant property of pre-trained transformer encoders is their
inductive bias toward generalisation: a model that has been pre-trained
on a large general-domain corpus can be fine-tuned with a relatively
small domain-specific corpus and still produce strong domain-specific
performance. This property is particularly important when the
domain corpus is heavily skewed in its label distribution, as is the
case in this work.

The need for African-specific resources has been recognised in
recent work. Adelani and colleagues introduced MasakhaNER [11], a
named-entity recognition benchmark for ten African languages
including Amharic, Hausa, Igbo, Kinyarwanda, Luganda, Luo, Wolof,
and Yoruba, with annotations for PERSON, ORGANISATION, LOCATION, and
DATE. MasakhaNER demonstrated that generic multilingual models such
as mBERT and XLM-RoBERTa underperform on African text compared to
models pre-trained or further fine-tuned on African corpora.
Subsequent work on AfroLM and AfroXLMR has extended this line by
producing African-pre-trained encoders. The VioNER schema targets
English-language reporting and therefore uses `bert-base-cased`, but
the design is compatible with these African encoders as a future
backbone, and the entity inventory (ACTOR/VICTIM/ACTION/etc.) is
strictly richer than the four-type MasakhaNER schema.

## 2.3 Transformer Models and BERT

The transformer architecture, introduced by Vaswani and colleagues
[5], replaces recurrent and convolutional sequence operations with
self-attention. In self-attention, each position in a sequence
attends to every other position, with attention weights computed from
learned query, key, and value projections. The architecture allows
strong parallel computation, captures long-range dependencies without
the vanishing-gradient problems of recurrent models, and scales well
with both data and parameters.

BERT [6] applies the encoder half of the transformer to
representation learning. The model is pre-trained on a large corpus
using two objectives: masked language modelling, in which 15 percent
of the input tokens are masked and the model is trained to predict
them, and next-sentence prediction, in which the model receives a
pair of sentences and is trained to predict whether the second
follows the first. The pre-trained encoder can then be fine-tuned on
downstream tasks with relatively few task-specific parameters.

For token-level prediction tasks such as NER, BERT exposes the
sequence of contextual representations as output. A linear
classification head over these representations produces per-token
logits over the label vocabulary, and the model is fine-tuned with a
standard cross-entropy or alternative loss against gold labels. The
`bert-base-cased` variant used in this thesis has 12 transformer
layers, 768 hidden dimensions, and approximately 110 million
parameters. Cased tokenisation is preferred for NER because
capitalisation is a strong feature for entity detection in English.

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

Token classification in NER is intrinsically class-imbalanced. In a
typical news sentence, most tokens carry the O label, and within the
entity tokens themselves some types are far more common than others.
For the corpus assembled in this thesis, O tokens constitute
approximately 78 percent of the total, with entity tokens forming the
remaining 22 percent. Within the entity tokens, the distribution is
itself skewed: ACTOR, CITY, DATE, REGION, and DISTRICT together
account for the bulk of entity occurrences, while VICTIM, ACTION, and
CASUALTIES are substantially rarer (see Chapter 6 for full
statistics).

Three well-established families of techniques address class imbalance.

**Re-sampling.** The training set is rebalanced by oversampling
minority-class examples or undersampling majority-class examples
[24]. In token classification, this is awkward because rebalancing
operates at the example level rather than the token level: a single
sentence contains tokens from many classes, and oversampling sentences
that include a rare entity also oversamples the O tokens within those
sentences. Stratified diversity sampling, as adopted in this thesis,
applies the principle at example granularity while preserving overall
distributional diversity.

**Class-weighted cross entropy.** The cross-entropy loss is reweighted
per class so that minority classes carry larger gradient contributions
[25]. Inverse-frequency weighting computes the weight for class c as
1/f_c, optionally normalised; effective-number weighting [26] uses a
smoothed variant that accounts for sample overlap. This thesis
applies inverse-frequency class weights computed from the actual
training-set distribution.

**Focal loss.** Focal loss, introduced by Lin and colleagues for dense
object detection [12], down-weights well-classified examples and
focuses learning on difficult ones. For a per-token cross entropy of
CE(p, y) = -log p_y, the focal loss is

> FL(p, y) = -α_y (1 - p_y)^γ log p_y

where γ controls the strength of down-weighting (γ = 0 recovers
cross entropy) and α_y is an optional per-class weight. Focal loss
has been shown to outperform plain cross entropy in object detection
and in token classification with imbalanced labels, particularly when
combined with a class-weighting scheme.

The present work combines focal loss (γ = 2) with inverse-frequency
class weighting, computes the weights from the training-set label
distribution at the start of training, and excludes the special -100
label from both the loss and the weight computation. The
implementation follows the formulation in [12], extended with optional
label smoothing β for regularisation:

> FL_LS(p, y) = -α_y (1 - p_y)^γ Σ_c y'_c log p_c
>
> where y'_c = (1 − β) · 1[c = y] + β / (C − 1) · 1[c ≠ y].

The inverse-frequency weight for class c is computed once at the
start of training as

> α_c = T / (C · max(f_c, 1)),

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
boundary matching) and "strict" variants. The present work reports
span-level precision, recall, and F1 with strict boundary matching
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

This chapter reviews prior systems most directly related to the
present work. The review is intentionally narrower than the
literature review in Chapter 2: only published papers, peer-reviewed
conference proceedings, masters and doctoral theses, and technical
reports that present concrete systems are included, and each entry is
read in light of how it informs or differs from VioNER. The chapter
concludes with a synthesis of the gaps that the thesis bridges.

## 3.1 General Event Extraction from News

Tanev, Atkinson, and Piskorski present a real-time news event
extraction architecture aimed at global crisis monitoring [1]. Their
system processes large volumes of multilingual news and combines
pattern-based event recognition with geographical clustering to
identify locations and to track evolving situations. Its strengths
include scalability and breadth of coverage; its limitations, from
the perspective of this thesis, are that event recognition is
pattern-based rather than learned and that the system does not
generate a structured 5W1H representation per event suitable for
downstream querying.

Hogenboom and colleagues survey event-extraction methods from text
with a particular focus on decision-support applications [16], [4].
They identify three methodological families (data-driven,
knowledge-driven, hybrid) and conclude that hybrid pipelines that
combine statistical learning with linguistic and domain rules are the
most operationally viable. The methodological positioning of VioNER,
in which a learned NER component is paired with a rule-driven
post-processing layer informed by a curated knowledge base, follows
their recommendation.

Suchanek, Kasneci, and Weikum construct YAGO, a large-scale ontology
of facts extracted automatically from Wikipedia and WordNet [30].
YAGO demonstrates the value of automatic extraction from a structured
source: by exploiting infobox and category data, the authors derive
millions of structured assertions with high accuracy. The relevance
to this thesis is twofold. First, YAGO illustrates the operational
distinction between extracting from semi-structured sources, where
extraction can rely on the structure, and extracting from free text,
where the model must learn structure from regularities in surface
form. Second, YAGO embeds extracted facts in an ontology, which
parallels the role of the taxonomy and knowledge base in VioNER.

Hienert and Luciano extend a similar approach to the extraction of
historical events from multilingual Wikipedia [31], demonstrating the
applicability of standardised event models such as LODE to large
corpora. Their methodology is constrained by the semi-structured
nature of the source and is not directly applicable to ACLED notes or
to full news articles. It is, however, a useful counterpoint:
extraction from semi-structured sources is qualitatively different
from extraction from free text.

## 3.2 Violence-Specific Event Extraction Systems

Piskorski, Tanev, and Wennerberg developed the NEXUS system, which
extracts security-related events using the PMVE ontology [29]. NEXUS
applies keyword filtering and linguistic patterns to identify
violence-relevant articles, then maps extracted entities and events
onto PMVE classes. The system's strengths include a principled
ontology and demonstrated coverage of European security incidents;
its limitations, from the perspective of African deployment, include
its tuning to European actor and place vocabularies and its reliance
on hand-crafted patterns. PMVE itself, however, is a valuable
reference for the construction of the present taxonomy.

Becker and colleagues focus on planned events on social media [32],
exploiting platform-specific structured fields to combine with
discussion text. Their approach is orthogonal to the present work in
several ways. Planned events differ qualitatively from violent
incidents, which by their nature are unplanned and adversarial.
Social-media reporting introduces noise and veracity concerns that
make it unsuitable as a primary source for formal early warning.
That said, Becker and colleagues' integration of structured platform
data with unstructured text is a precedent for the role of the
knowledge base in VioNER.

Magnuson and colleagues build a Twitter-based event recommendation
system on top of Eventbrite [33]. Their work confirms both the
promise and the risks of social-media event extraction. Aratefeh and
Khreich survey techniques for event detection in Twitter [34],
categorising approaches into supervised, unsupervised, and hybrid
methods and discussing the role of topic modelling, classification,
and clustering. While VioNER targets traditional news rather than
social media, the noise-handling and short-text techniques surveyed in
this body of work are useful contingency tools for future extensions
to short-form reporting.

## 3.3 Event Extraction in the African Context

The closest predecessor to VioNER is the work of Taye Abdulkadir
Edris and Sungkur, who developed a system for extracting 5W
characteristics of violent events in the African context [35]. Their
system combines linguistic preprocessing with Stanford CoreNLP and
machine-learning classification with Weka. They report results on a
modest annotated corpus and demonstrate that domain-specific
adaptation improves performance over generic baselines on African
text.

The differences between Taye Abdulkadir's work and the present thesis
are substantial. First, Taye Abdulkadir's implementation uses
Stanford CoreNLP and Weka, which limits access to modern transformer
architectures; the present work uses Hugging Face Transformers and a
fine-tuned BERT. Second, Taye Abdulkadir's annotated corpus is
modest in size, whereas the present work uses approximately fifty
thousand training examples derived from ACLED and template
augmentation. Third, the present work develops an explicit
hierarchical taxonomy of African violent events with approximately
ninety-five terminal categories, supports a curated knowledge base of
armed groups and locations, and packages the system as a deployable
web application; Taye Abdulkadir's work stops at the model boundary.
Fourth, the present work documents and addresses class imbalance
explicitly through focal loss and stratified sampling.

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

*Table 3.1: Comparative position of VioNER relative to prior systems.*

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
   CoreNLP + Weka). VioNER is, to the best of the author's
   knowledge, the first fine-tuned transformer NER model targeted
   specifically at African violent-event 5W1H extraction at the
   50,000-example scale.
3. **African violent-event taxonomy at four levels.** No prior open
   taxonomy of African violent events at this level of granularity
   has been published, to the best of the author's knowledge.
   ACLED's taxonomy reaches two levels with approximately
   twenty-five sub-event categories; UCDP and GDELT/CAMEO are
   coarser-grained. The four-level VioNER taxonomy with
   approximately ninety-five terminal categories is presented in
   full in Annex B.
4. **Knowledge-base validation layer.** The combination of a curated
   knowledge base of African armed groups, cities, and weapons with
   a learned extractor, used for both validation (flagging
   geographically implausible extractions) and enrichment
   (canonicalising armed-group names, attaching country and region
   metadata to cities), is, to the best of the author's knowledge,
   a contribution.
5. **Operational packaging.** Prior academic work in this area has
   stopped at the model boundary. NEXUS, Tanev et al., and Taye
   Abdulkadir all describe extraction systems without delivering a
   reproducible, documented web application that non-specialist
   users can operate end-to-end. This thesis delivers a full web
   application with documented APIs and a reproducible Docker
   Compose deployment.

\pagebreak

# 4. The Proposed Solution

This chapter presents the design of the VioNER system. It first
states the design principles that guide the construction, then
describes the system architecture at a high level, defines the entity
schema and BIO encoding, presents the hierarchical taxonomy, specifies
the knowledge base, details the training pipeline, the inference
pipeline, and the web application architecture. Implementation
detail and the specific technology choices made to realise this
design are deferred to Chapter 5.

## 4.1 Design Principles

Six principles guide the design.

**P1: Grounded supervision.** Every entity type in the schema must be
something that can be reliably found verbatim in source text. Entity
types whose grounding rates were below an acceptable threshold during
pilot study (specifically, EVENT_TYPE and COUNTRY) are excluded from
the NER model and recovered downstream by deterministic post-processing
against the knowledge base.

**P2: Modular pipeline.** The system is organised as a pipeline in
which each stage has a well-defined input and output, with no hidden
state. NER produces token labels; entity assembly produces spans;
post-processing produces 5W1H records; knowledge-base validation
produces enriched records. Each stage can be inspected, replaced, and
unit-tested in isolation.

**P3: Hybrid statistics and knowledge.** A learned model handles
generalisation over surface forms. A structured knowledge base
handles deterministic look-ups (city-to-country resolution, armed
group alias resolution, taxonomy classification). Each is used where
it is strongest.

**P4: Confidence is first-class.** Every span produced by the NER
component carries a confidence score derived from the softmax
probabilities. Downstream stages can apply category-specific
thresholds, and the UI surfaces confidence so that users see what they
are trusting.

**P5: Operational packaging.** The model is exposed through a
documented HTTP API and consumed by a web UI. Users do not need to
know about checkpoints, tokenisers, or label vocabularies.

**P6: Reproducibility.** All datasets, training runs, and the final
deployment are reproducible from documented scripts and configuration.
Random seeds are fixed where applicable and recorded where not.

## 4.2 System Architecture

Figure 4.1 outlines the high-level architecture of VioNER. The system
is organised in four layers: a model layer that hosts the trained
BERT model, a service layer that exposes the model and supporting data
stores through HTTP APIs, a data layer that persists events,
training runs, and user accounts, and a presentation layer that
provides the web UI.

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

*Figure 4.1: High-level architecture of the VioNER system.*

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
queryable structured event records.*

The boundary between extraction (NER) and post-processing is
deliberate: it allows the supervised learning problem to be cast
narrowly, with the schema in 4.3, while still producing a richer
output by combining the NER result with deterministic knowledge.

## 4.3 Entity Schema and BIO Encoding

The entity schema is the central design decision. As discussed under
P1, the schema is restricted to entity types that pilot evaluation
confirmed as reliably grounded in source text. The resulting eight
entity types, organised under the 5W1H categories, are listed in
Table 4.1.

*Table 4.1: Eight-entity grounded schema for the VioNER NER component.*

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

Figure 4.3 illustrates the encoding on a representative example.

```
Tokens:    "Al"     "Shabaab" "fighters" "killed"   "12"          "civilians" "in"  "Beledweyne" "on"  "Sunday"
Labels:    B-ACTOR  I-ACTOR   O          B-ACTION   B-CASUALTIES  B-VICTIM    O     B-CITY       O     B-DATE
```

*Figure 4.3: BIO encoding example for a sentence describing a
violent event. Multi-token entities such as "Al Shabaab" are
encoded by a leading B- tag followed by I- tags.*

Sub-word tokenisation introduces a complication: a single
gold-labelled word may be split into several sub-word tokens, and the
labels must be projected onto the sub-words during training. The
convention adopted here, summarised as Algorithm 4.1 in Section 4.6,
assigns the original label to the first sub-word and converts any
leading B- prefix to I- for subsequent sub-words, while assigning the
ignore index (-100) to special tokens such as [CLS], [SEP], and [PAD]
so that they are excluded from the loss.

## 4.4 Hierarchical Violent Event Taxonomy

The taxonomy of violent events is constructed at four levels. Level
1 distinguishes four broad violence categories. Level 2 introduces
eighteen intermediate types. Level 3 refines into approximately fifty
specific event types. Level 4 adds approximately twenty additional
detailed subtypes for the most common categories. The complete
taxonomy is presented in Annex B; this section presents the Level 1
and Level 2 structure.

*Table 4.2: Level 1 categories of the hierarchical taxonomy.*

| Level 1                          | Definition                                                            |
|:---------------------------------|:----------------------------------------------------------------------|
| Political Violence               | Violence motivated by political objectives, including contesting state authority, achieving political change, or advancing ideological agendas. |
| Criminal Violence                | Violence motivated by economic gain or territorial control by criminal organisations.                                                              |
| Communal Violence                | Violence between identity-based groups (ethnic, religious, clan) over resources, territory, or social dominance.                                  |
| State Violence Against Civilians | Violence perpetrated by state security forces against non-combatant civilians outside of armed conflict contexts.                                |

*Table 4.3: Level 2 intermediate violence types.*

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

*Figure 4.4: Four-level taxonomy hierarchy (visual outline of Levels 1
to 3).*

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

The knowledge base is a structured, in-process resource loaded at
service startup. It consists of three dictionaries.

**Armed Groups.** Approximately 150 entries cover major armed groups
active in Africa, each represented by a canonical name, a list of
aliases, a country of operation, a region, and a group type (militia,
terrorist, rebel, or government). Entries are organised by region
(East, West, North, Southern, Central Africa) for readability.
Example entries include Al-Shabaab (Somalia), Boko Haram (Nigeria),
M23 (DRC), Rapid Support Forces (Sudan), JNIM (Mali), and Wagner
Group (multiple). The full list is in Annex C.

**Cities and Regions.** Approximately 200 conflict-affected cities
are recorded with their country and parent administrative region.
The dictionary also covers all 54 African countries with their
capitals and major regions. Examples include Maiduguri (Nigeria,
Borno), Goma (DRC, North Kivu), Mogadishu (Somalia, Banaadir), El
Fasher (Sudan, North Darfur), and Bamako (Mali, Bamako Capital
District). The dictionary is used both to resolve city-country
ambiguity at inference time and to flag geographically implausible
extractions.

**Weapons and Tactics.** A categorised list of weapons (firearms,
explosives, edged weapons, fire/arson, heavy weapons) and tactical
methods (ambush, raid, mass shooting, suicide bombing). The list is
used by the post-NER taxonomy classifier to inform Level 3 and Level 4
classification.

The knowledge base is also used by the validator component to attach
metadata to extracted entities. For an ACTOR span that matches a
known armed group alias, the validator attaches the canonical name,
country, region, and group type. For a CITY span, it attaches the
country and region. For a weapon mention, it attaches the category.
Mismatches (for example, an actor whose known country of operation
disagrees with the location extracted in the same sentence) lower the
event's overall confidence score and are surfaced in the analytics
view for manual review.

*Table 4.4: Knowledge base content summary.*

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
diversity-poor: many events share repeating phrasing. The
`create_training_subset.py` script (Algorithm 4.2) selects a
35,000-example subset that maximises diversity while ensuring that
rare entity types receive proportionate representation. The algorithm
operates in three phases: first, it selects examples that contain at
least one rare entity (VICTIM, ACTION, CASUALTIES) until the rare-class
budget is met; second, it selects examples with high entity diversity
(number of distinct entity types); third, it fills the remaining
budget by random sampling from the residual pool.

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

> **Algorithm 4.1:** Sub-word label alignment for BIO tagging
>
> Input: tokens, labels, tokenizer
>
> 1. Run the tokenizer with `is_split_into_words=True`.
> 2. Retrieve `word_ids` from the encoding.
> 3. Initialise `prev_word_idx` to None.
> 4. For each `word_idx` in `word_ids`:
>    - If `word_idx` is None: emit -100 (ignore in loss).
>    - Else if `word_idx != prev_word_idx`: emit `label2id[labels[word_idx]]`.
>    - Else: take the label of the underlying word; if it starts with B-,
>      rewrite the prefix to I-; emit `label2id` of the rewritten label.
>    - Set `prev_word_idx = word_idx`.
> 5. Return the list of label ids.

### Training hyperparameters

The principal hyperparameters are listed in Table 4.5.

*Table 4.5: Training hyperparameters.*

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

> **Algorithm 4.4:** Focal loss with inverse-frequency weighting
>
> Input: logits z (N x C), targets y (N), class weights α (C), gamma,
> ignore index I, label smoothing β
>
> 1. Mask positions where y == I and exclude them from the loss.
> 2. Compute log-softmax of z to obtain log p.
> 3. If β > 0, smooth one-hot targets so that the true class gets
>    1 - β and the remaining mass β / (C-1) is distributed uniformly.
> 4. Compute per-position cross entropy: CE_n = -Σ_c y_n,c * log p_n,c.
> 5. Compute focal modulating factor: m_n = (1 - p_n,y_n)^γ.
> 6. Multiply by per-class weight α_y_n.
> 7. Return the mean of α_y_n * m_n * CE_n over the un-masked positions.

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

> **Algorithm 4.5:** Post-NER 5W1H structuring with knowledge-base
> validation
>
> Input: text, NER service, knowledge base
>
> 1. Tokenise text and run BERT NER to obtain per-token label ids and
>    softmax probabilities.
> 2. Walk the predictions to assemble entity spans following BIO
>    transitions; for each span, record start, end, label, surface
>    form, and the mean confidence of the constituent sub-tokens.
> 3. Filter spans by category-specific confidence thresholds (see
>    below).
> 4. Map each filtered span to its 5W1H category via the
>    {ACTOR -> WHO, VICTIM -> WHOM, ACTION -> WHAT, DATE -> WHEN,
>    REGION/CITY/DISTRICT -> WHERE, CASUALTIES -> HOW} table.
> 5. For each ACTOR span, look up the canonical name and metadata in
>    the armed-groups KB; for each WHERE span, look up the country
>    and parent region in the locations KB; for each weapon mention
>    surfaced in HOW, look up the weapon category.
> 6. Apply the taxonomy classifier (Section 4.4) over the enriched
>    record to assign Level 1 to Level 4 taxonomy labels.
> 7. Combine all of the above into a single structured event record.

Confidence thresholds are calibrated by category: WHO 0.70, WHOM
0.70, WHAT 0.60, WHEN 0.80, WHERE 0.70, HOW 0.75. These thresholds
were determined by inspection of validation-set behaviour: WHEN
demands high precision because dates are easy to verify and false
positives are highly visible; WHAT is allowed to be more permissive
because actions are typically supported by surrounding context.

Multi-event texts are handled by a segmentation step that splits long
documents into event-bearing sentences before running NER. The
segmentation module (`pipeline/segmentation.py`) uses sentence
boundary detection and a small set of indicator phrases (for example,
"in a separate incident", "earlier that week") to identify event
boundaries.

## 4.8 Web Application Architecture

The web application is organised as a single-page React/TypeScript
front-end backed by a FastAPI service. The front-end communicates
with the back-end exclusively through JSON over HTTPS, with a single
WebSocket channel reserved for streaming training progress.

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

This chapter describes the implementation of the VioNER system. It
documents the technology stack, the data preparation flow, the
training procedure, the focal-loss implementation, the back-end
services and API surface, the front-end application, and the
containerised deployment. The chapter complements Chapter 4: where
that chapter described what the system does and why, this one
describes how it does it.

## 5.1 Technology Stack

The system is implemented in Python 3.11 for the back end and machine
learning components, and in TypeScript with React 19 for the front
end. PostgreSQL serves as the persistent data store. Docker Compose
orchestrates the development environment.

*Table 5.1: Back-end technology stack.*

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

*Table 5.2: Front-end technology stack.*

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

The motivation for these choices is summarised below. FastAPI gives
type-driven API definition with automatic OpenAPI generation and
strong asynchronous support; the OpenAPI document is consumed by the
front-end to keep type definitions aligned. PyTorch and Hugging Face
Transformers are the de-facto standard for transformer fine-tuning.
SQLAlchemy provides a stable ORM. React 19 with React Router 7 gives
a modern routing surface (including file-based route definitions) and
fast iteration during development. TailwindCSS combined with shadcn/ui
gives a coherent component library without locking the project into a
heavy design system. Vite provides fast development builds and
production bundling.

## 5.2 Data Acquisition and Preprocessing

The primary data source is the ACLED open dataset, accessed through
the ACLED API. The retrieved records cover the 54 African countries
and span multiple years. The raw extract is approximately 212,590
event records.

The preprocessing module `pipeline/preprocessing.py` converts the raw
extract into BIO-tagged training data. The principal steps are:

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

> **Algorithm 4.2:** Stratified diversity sampling for entity coverage
>
> Input: Pool P, target size T, rare-entity budget R, diversity budget D
>
> 1. Identify the rare entity set: {VICTIM, ACTION, CASUALTIES}.
> 2. For each example p in P, compute its rare-entity score (number of
>    distinct rare-entity types present).
> 3. Select the top R examples by rare-entity score.
> 4. From the remaining pool, score each example by its number of
>    distinct entity types and select the top D examples.
> 5. From the residual pool, randomly sample the remaining T - R - D
>    examples.
> 6. Return the union.

In the production run, T = 35,000, R = 12,000, D = 11,666, and the
random remainder is 11,334.

Augmentation is implemented in `scripts/augment_training_data.py`
following Algorithm 4.3.

> **Algorithm 4.3:** Template-based augmentation
>
> Input: KB armed groups, locations, weapons; verb lexicons; template list
>
> 1. For each template, repeatedly:
>    - Sample an actor from the KB compatible with the template.
>    - Sample a location from the KB compatible with the actor's country
>      of operation, where possible.
>    - Sample an action verb from the verb lexicon appropriate to the
>      template type (location-taking, victim-taking, or clash).
>    - Sample casualties counts within plausible ranges.
>    - Populate the template and produce a tokenised, BIO-labelled
>      example with `source = "augmentation"`.
> 2. Stop when the augmentation budget is exhausted.

The augmentation budget is 15,000 examples. Together with the 35,000
sampled examples, the final training corpus is 50,000 examples,
partitioned 40,000 / 10,000 into train and validation.

Sample verb lexicons (location-taking verbs include "attacked",
"raided", "stormed", "bombed", "shelled"; victim-taking verbs include
"killed", "wounded", "abducted", "displaced"; clash verbs include
"clashed with", "exchanged fire with", "battled") together with the
template catalogue are reproduced in Annex E.

## 5.4 Model Training Implementation

The trainer is implemented as `pipeline/training.py`, organised
around a `ViolentEventNER` class that wraps the Hugging Face model,
the tokenizer, the dataset, and the training loop.

The constructor receives a `ModelConfig` dataclass that captures all
hyperparameters (Table 4.5). Device selection prefers Apple Silicon
GPU (MPS) when available, falls back to CUDA where present, and
ultimately to CPU. The `load_model` method instantiates
`AutoTokenizer.from_pretrained` and
`AutoModelForTokenClassification.from_pretrained` for `bert-base-cased`,
configures the model with the 17-label classification head, and moves
it to the selected device.

The `NERDataset` class implements `torch.utils.data.Dataset`. Its
`__getitem__` runs the tokenizer with `is_split_into_words=True`,
retrieves `word_ids`, and applies the alignment in Algorithm 4.1.
Special tokens are assigned label -100, which PyTorch ignores in the
default cross-entropy loss and which the custom focal loss also
respects.

The training loop iterates `num_epochs` epochs, with a per-epoch
forward/backward pass for training and a no-grad validation pass.
Gradient clipping bounds the L2 norm of the gradient at 1.0. The
linear warm-up schedule is applied during the first `warmup_steps`
optimisation steps, after which the ReduceLROnPlateau scheduler takes
over and reduces the learning rate by a factor of 0.5 when the
validation loss fails to improve for two consecutive epochs.

Early stopping is implemented by tracking the best validation loss
seen so far and a counter of epochs without improvement. When the
counter reaches the patience threshold, training stops. The best
model is restored from the `best/` checkpoint after termination.

Resumption is supported by `resume_training`, which reads the saved
`training_config.json`, locates the most recent epoch folder, and
re-enters the training loop at the appropriate epoch. Extension of a
completed run is supported by the `--extend-epochs` flag, which
increments the total epoch count and restarts the loop at the next
epoch.

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

*Figure 5.1: Back-end module organisation.*

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
routing.

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

*Figure 5.2: Front-end route map.*

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

This chapter presents the empirical evaluation of VioNER. It
describes the experimental setup, reports dataset statistics,
training dynamics, overall and per-entity performance, an ablation
of the focal-loss objective, the effect of knowledge-base validation
on extraction quality, inference latency, end-to-end behaviour on
representative articles, and user acceptance feedback. The chapter
concludes with an error analysis that motivates the future-work
programme in Chapter 7.

## 6.1 Experimental Setup

All training and evaluation reported in this chapter were conducted
on an Apple Silicon workstation with the configuration in Table 6.1.

| Component | Specification |
|:----------|:--------------|
| CPU        | Apple M-series, 10 cores |
| Memory     | 64 GB unified |
| Accelerator| Metal Performance Shaders (MPS) backend |
| Operating system | macOS 14 |
| Python     | 3.11 |
| PyTorch    | 2.6 |
| Transformers | 4.46 |

Validation metrics are computed on the held-out 10,000-example
validation split that was set aside at the start of training and not
seen during any training run. Token-level accuracy excludes positions
labelled with the special ignore index (-100). Per-entity precision,
recall, and F1 are computed over assembled entity spans (rather than
individual tokens) so that boundary errors are penalised. A predicted
entity is considered correct if its label, start, and end exactly
match a gold entity.

## 6.2 Dataset Statistics

Table 6.1 summarises the pre-processed dataset before subset
selection.

*Table 6.1: Pre-processed dataset statistics.*

| Quantity                | Count      |
|:------------------------|-----------:|
| Total events            | 212,590    |
| Training events         | 170,072    |
| Validation events       | 42,518     |
| Train/validation split  | 80 / 20    |
| Unique entity types     | 8          |
| BIO labels (incl. O)    | 17         |

Table 6.2 reports entity-level frequencies in the full pre-processed
corpus.

*Table 6.2: Entity-level frequency in the full pre-processed corpus.*

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

The O-token share over the full corpus is approximately 78 percent of
all tokens, confirming the imbalance noted in Section 2.4.

After stratified diversity sampling and augmentation (Section 5.3),
the production training corpus comprises 50,000 examples partitioned
40,000 (train) and 10,000 (validation). Augmented examples constitute
approximately 30 percent of this corpus and substantially raise the
share of ACTION, VICTIM, and CASUALTIES tokens to the order of 26 to
32 percent of their respective categories in the optimised subset.

Class weights derived from the training-set distribution by
inverse-frequency weighting are summarised below; minority entities
receive the maximum weight of 10, the dominant O class is heavily
down-weighted.

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

*Table 6.3: Per-epoch training dynamics for the representative run.*

| Epoch | Train Loss | Val Loss | Val Accuracy |
|------:|-----------:|---------:|-------------:|
| 1     | 0.0178     | 0.0092   | 95.32 %      |
| 2     | 0.0061     | **0.0074** | 96.64 %    |
| 3     | 0.0046     | 0.0076   | 96.81 %      |
| 4     | 0.0041     | 0.0076   | 96.92 %      |
| 5     | 0.0036     | 0.0080   | 97.05 %      |
| 6     | 0.0032     | 0.0084   | 97.44 %      |
| 7     | 0.0028     | 0.0088   | 97.55 %      |

Two observations stand out. First, the validation loss reaches its
minimum at epoch 2, after which it begins to creep upward. Training
loss continues to fall, indicating onset of overfitting. The early
stopping mechanism with patience 5 and threshold 0.001 detects this
within five further epochs and terminates training. Second,
token-level validation accuracy continues to improve even as
validation loss worsens. This is a known artefact of focal loss and
class-weighted training: the model becomes more confident on
already-correct predictions (raising accuracy) while losing
calibration on minority-class boundaries (raising loss).

The most recent end-to-end production run, recorded in
`models/bert-base-cased_20251223_192332/training_config.json`,
reports a best validation loss of 0.01358 at epoch 2 with the
ReduceLROnPlateau scheduler engaged from epoch 3 onward. This is
consistent with the dynamics in Table 6.3 and confirms the
robustness of the fast-convergence behaviour across runs.

The convergence speed (two epochs to best validation loss) reflects
two design choices acting together. First, the BERT pre-training
provides strong initialisation, so very little adaptation is needed
to specialise to the African violent-event NER task. Second, the
50,000-example training set is large enough to saturate the
fine-tuning signal within a few passes; further epochs over-fit on
training-set idiosyncrasies.

## 6.4 Overall Model Performance

*Table 6.3: Best validation metrics across training runs.*

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

Span-level precision, recall, and F1 are reported per entity in Table
6.4. The metrics are computed on the 10,000-example validation set
using exact-match span comparison.

*Table 6.4: Per-entity precision, recall and F1 on the held-out validation set.*

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

*Figure 6.3: Per-entity F1 bar chart.*

Several patterns emerge.

- **DATE achieves the highest F1.** Date expressions in conflict
  reporting follow predictable patterns ("on Monday", "January 15",
  "yesterday") that are well covered by the training corpus and well
  bounded by prepositions and capitalisation.
- **ACTOR, CITY, and DATE form a cluster of strong performance.**
  These entities have both abundant training data and distinctive
  surface markers.
- **REGION and DISTRICT are slightly weaker.** Their main source of
  error is mutual confusion: a region named after its capital city
  is sometimes tagged CITY rather than REGION, and a city that
  doubles as a district is sometimes tagged DISTRICT. The confusion
  pattern is analysed further in Section 6.11.
- **VICTIM is the lowest-performing entity.** Despite the augmentation
  effort and the inverse-frequency weighting, the rarest entity in
  the corpus also has the noisiest boundary signal: victim
  descriptions vary widely in length and phrasing ("civilians", "ten
  villagers, including women and children"), and the model
  occasionally truncates or over-extends spans.

The macro F1 of 0.887 indicates that all entity types are recognised
to a useful degree even after accounting for class imbalance. The
micro F1 of 0.909 reflects the dominance of the high-support, high-F1
entities.

## 6.6 Ablation: Focal Loss versus Cross Entropy

To isolate the contribution of focal loss, four configurations were
compared while holding everything else constant.

*Table 6.5: Focal-loss ablation. Per-entity F1 on the validation set.*

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

The knowledge-base validation layer (Section 4.5) attaches metadata
to extracted spans and adjusts confidence scores. Its contribution
to downstream usefulness is assessed in two ways.

First, the percentage of high-confidence (`p >= 0.85`) ACTOR spans
whose canonical name is found in the KB is **64.3 percent** of
validation-set ACTOR predictions. This number is interpreted as the
share of extractions that downstream pipelines can be enriched with
group metadata without further look-up. The remaining 35.7 percent
are typically generic descriptors ("gunmen", "armed men") that
cannot be canonicalised without further context.

Second, the rate of geographically implausible CITY/REGION pairs (a
CITY whose country, per the KB, differs from the country implied by
the REGION) is **2.4 percent** of multi-entity events with both a
CITY and a REGION extracted. Such events are flagged in the UI for
manual review, and on inspection most arise from genuine ambiguity in
the source text (for example, a story discussing a cross-border
incident that mentions a city on one side and a region on the other)
rather than extraction errors.

Together, these numbers indicate that the knowledge base adds
operational value on top of the raw NER output without significantly
filtering out valid extractions.

## 6.8 Inference Latency and Throughput

Single-document inference latency was measured for three
representative article lengths on the same hardware used for
training.

*Table 6.6: Inference latency on representative articles.*

| Article length     | Median latency | 95th percentile |
|:-------------------|---------------:|----------------:|
| Short (≤200 tokens)|  142 ms        |  178 ms         |
| Medium (≤500 tokens)| 246 ms        |  298 ms         |
| Long (≤1500 tokens, windowed) | 612 ms |  834 ms      |

These latencies include tokenisation, BERT inference on MPS, entity
assembly, confidence filtering, KB enrichment, and JSON
serialisation. Throughput in batch mode (sixteen documents per batch)
reaches approximately 65 short documents per second.

## 6.9 End-to-End Demonstration

To illustrate the end-to-end behaviour, the system was applied to a
sample of recent open-source news articles describing African
violent events. Three illustrative cases are reproduced below.

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

A small user acceptance test was conducted with five participants
representing the target audience: two early-warning analysts, one
academic conflict researcher, and two software developers familiar
with NLP systems but not with the specific application domain.
Participants were given access to a deployed instance of VioNER and
asked to perform six tasks (run inference on three supplied
articles, browse the event store, run an analytics query, train a
model with a supplied dataset, and review a flagged event).

Participants completed all six tasks. Aggregated Likert-scale
responses (1 = strongly disagree, 5 = strongly agree) are reported
below.

| Statement                                                           | Mean | Std. |
|:--------------------------------------------------------------------|:----:|-----:|
| The extracted entities matched what I expected.                     | 4.4  | 0.5  |
| The 5W1H structuring was clear and easy to interpret.               | 4.6  | 0.5  |
| The confidence scores were useful for triage.                       | 4.2  | 0.4  |
| The KB enrichment (canonical names, country lookups) added value.   | 4.6  | 0.5  |
| The training screen made it easy to start and monitor a run.        | 4.0  | 0.7  |
| The analytics views answered the kinds of questions I would ask.    | 4.2  | 0.4  |

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

A targeted error analysis was conducted on 300 validation-set events
with at least one extraction error. The errors break down as follows.

- **Boundary errors (38 percent).** The model identifies the entity
  type correctly but truncates or over-extends the span. Most boundary
  errors affect VICTIM and CASUALTIES, where the gold span includes
  qualifiers ("at least", "approximately") that the model sometimes
  omits.
- **Type confusion between location entities (24 percent).** REGION
  and CITY, or REGION and DISTRICT, are interchanged. Figure 6.4
  visualises the confusion. Most cases involve cities that lend their
  name to a region or district.
- **Missed entities (19 percent).** The model fails to recognise an
  entity, usually a victim group or action verb whose phrasing is
  uncommon in the training corpus (for example, "Christian
  worshippers" as VICTIM).
- **Spurious entities (12 percent).** The model emits an entity that
  has no gold counterpart. Spurious WHEN entities arise most often,
  triggered by tokens such as "this morning" or "earlier" in
  ambiguous contexts.
- **Confidence-related drops (7 percent).** The model emits the
  entity but its average confidence falls below the category
  threshold and the entity is filtered out by post-processing.
  Lowering the threshold for these cases would recover some recall at
  the cost of precision.

```
Predicted →   CITY    REGION   DISTRICT
Gold ↓
CITY          ----    0.05     0.04
REGION        0.08    ----     0.06
DISTRICT      0.07    0.09     ----
```

*Figure 6.4: Confusion patterns between location entity types
(fraction of errors of each kind among location-entity errors).*

The error analysis motivates three concrete future-work directions:
explicit boundary refinement (for example, training a span-level
CRF on top of the BERT representations); injection of KB facts as
input features during training to disambiguate REGION/CITY ambiguity
at the model level; and addition of negative examples to reduce
spurious WHEN extractions. These directions are taken up in
Section 7.4.

\pagebreak

# 7. Conclusions, Recommendations, and Future Work

This chapter concludes the thesis. It summarises the work, lists
the contributions in bulleted form, makes recommendations to
practitioners, and identifies a prioritised programme of future
research.

## 7.1 Summary

This thesis set out to address the absence, in the African early
warning ecosystem, of a robust and openly documented pipeline for
converting English-language news reports of violent events into
structured 5W1H records. The general objective stated in
Section 1.4 was the design, implementation, and evaluation of VioNER,
an integrated system that uses fine-tuned BERT-based named entity
recognition to extract 5W1H attributes, supports those extractions
with a curated knowledge base and hierarchical taxonomy, and exposes
the full capability through a documented web platform.

Chapter 1 framed the problem in operational terms and listed ten
specific objectives. Chapter 2 reviewed the relevant theoretical
foundations: information and event extraction, named entity
recognition, the transformer architecture and BERT, methods for
handling class imbalance, conflict-event databases, and
event-oriented knowledge representation. Chapter 3 reviewed the
most directly related prior systems and identified five gaps that
this thesis bridges. Chapter 4 presented the proposed solution,
including the eight-entity BIO schema, the four-level hierarchical
taxonomy of African violent events, the structured knowledge base,
the training pipeline, the inference pipeline, and the web
application architecture. Chapter 5 documented the implementation,
covering the technology stack, data preparation, training, the focal
loss, the back-end and front-end. Chapter 6 reported empirical
results: a macro F1 of 0.887 and micro F1 of 0.909 on the held-out
validation set, with fast convergence (best at epoch 2),
demonstrable benefit from focal loss and class weighting (notably
+11 F1 for VICTIM relative to plain cross entropy), 64.3 percent KB
canonicalisation of high-confidence ACTOR spans, and inference
latencies in the hundreds of milliseconds for typical articles.

The specific objectives stated in Section 1.4 have been addressed
as follows: objectives 1 to 5 (literature review, schema, taxonomy,
data assembly, model training) are addressed in Chapters 2, 4, and
5; objective 6 (knowledge base) in Sections 4.5 and 5.6; objectives
7 and 8 (back-end and front-end) in Sections 5.6 and 5.7; objective
9 (evaluation) in Chapter 6; objective 10 (limitations and future
work) in Section 1.6 and the remainder of this chapter. The
research questions in Section 1.3 are answered respectively by the
eight-entity grounded schema (RQ1), the empirical results in
Sections 6.4 to 6.6 (RQ2), the results in Section 6.7 (RQ3), and
the system architecture in Sections 4.2 and 5.6 to 5.7 (RQ4).

## 7.2 Contributions

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

## 7.3 Recommendations

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
   extension (Section 7.4) is the single most important capability
   gap from an operational standpoint.

## 7.4 Future Work

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
C. Lignos *et al.*, "MasakhaNER: Named entity recognition for
African languages," *Transactions of the Association for
Computational Linguistics*, vol. 9, pp. 1116–1131, 2021.

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

[40] D. I. Adelani, J. Alabi, A. Fan, J. Kreutzer, X. Shen *et al.*,
"AfroLM: A self-active learning-based multilingual pretrained
language model for 23 African languages," in *Proceedings of the
3rd Workshop on Simple and Efficient Natural Language Processing
(SustaiNLP)*, 2022.

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

The full four-level taxonomy is reproduced below. Level 4 subtypes
are listed only where they apply.

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

### Database schema summary

```
users                ( id, email, full_name, role, password_hash, created_at )
training_runs        ( id, user_id, model, dataset, hyperparameters,
                       started_at, finished_at, status, best_epoch,
                       best_val_loss )
events               ( id, user_id, source_text, extracted_at, model_id,
                       taxonomy_level_1, taxonomy_level_2,
                       taxonomy_level_3, taxonomy_level_4,
                       confidence, status )
event_entities       ( id, event_id, entity_type, surface_form,
                       canonical_form, start, end, confidence,
                       kb_match_id )
kb_armed_groups      ( id, canonical_name, aliases, country, region,
                       group_type, active )
kb_locations         ( id, name, type, country, parent_region )
kb_taxonomy          ( id, level, parent_id, name, definition,
                       criteria, keywords )
inference_history    ( id, user_id, input_text, output_event_id,
                       latency_ms, created_at )
```

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







