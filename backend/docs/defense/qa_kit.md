# VioNER Defense — Q&A Kit

Thirty-six of the hardest questions a defense panel can ask, with prepared answers and **the backup slide to flip to** if a visual aid is needed. Questions are grouped by examiner archetype and by the standard AAU CS thesis-defense order: problem statement, research questions, methodology, results, conclusions, recommendations.

**Answering discipline.**
1. **Pause** for at least one beat after the question. The pause signals you took it seriously.
2. **Restate** the question in your own words if it might be ambiguous. ("So you're asking whether…") This buys five seconds of thinking and confirms scope.
3. **Acknowledge** the strength of the question if it's genuinely incisive. ("That's the right question to push on — let me give you two things.")
4. **Answer** in ≤ 90 seconds. Lead with the bottom line, then the supporting evidence.
5. **Do not bluff.** If you don't know, say "I don't know, and the closest evidence I have is X."

---

## Methodologist questions

### Q1. Why eight entities? You dropped 18 from the proposal — isn't that a weakening of the contribution?

**Bottom line.** It is a *strengthening*, because every retained label now has a verifiable ground-truth signal.

**Detail.** The grounding pilot in November 2025 measured, for each of the original 26 types, the fraction that could be located *verbatim* in source text. Types like MOTIVE and TRIGGER fell below 60 % because annotators were inferring them from context rather than reading them off the page. Training a model on inferred-not-grounded labels would introduce systematic noise — two annotators would label the same article differently. The eight retained types all clear 80 %. The dropped types are recovered downstream: EVENT_TYPE from the taxonomy classifier, COUNTRY from a KB lookup. Net effect: cleaner training signal, no operational capability lost.

**Flip to:** main slide 12. If pushed on grounding rates, no backup — promise the numbers in the rebuttal.

---

### Q2. Your training corpus is 30 % synthetic. Doesn't that invalidate the F1 numbers?

**Bottom line.** It biases them upward for in-distribution performance. I report this caveat explicitly in Chapter 6.12.

**Detail.** The validation split is drawn from the *same combined corpus* as the training data, so the metrics on slide 23 are a fair estimate of how the model performs on text that looks like ACLED notes plus template-augmented filler. They are **not** a guarantee of out-of-distribution performance on translated articles, citizen journalism, or social-media excerpts. The thirty-percent augmentation was a forced choice: rare entities like VICTIM appeared in single-digit percentages in the raw ACLED corpus, and the model's recall on them was flat without augmentation. The high-priority future-work item is annotated real-news expansion specifically to find out where this estimate breaks.

**Flip to:** main slide 32 (limitations) and backup B6 (per-entity deltas).

---

### Q3. Why didn't you compare against a learned hierarchical classifier for the taxonomy step?

**Bottom line.** It was scoped out as future work. The rule-based classifier was the right thing to ship for a thesis defending the *system contribution*, not the classifier contribution.

**Detail.** A two-stage learned classifier — Level 1 first, then Levels 2 and 3 conditional on Level 1 — is the natural next step and is item 2 in high-priority future work. The reason it wasn't included here is honesty about scope: training a hierarchical classifier well requires event-labelled training data that ACLED's main schema doesn't provide directly, and constructing that labelled set would have been a thesis in itself. The rule-based version achieves coverage; a learned version will achieve quality at scale.

**Flip to:** main slide 33.

---

### Q4. Why BERT-base-cased and not a larger model or a more recent backbone like RoBERTa or DeBERTa?

**Bottom line.** bert-base-cased gives the best quality-to-cost ratio for this task on the hardware available, and the bottleneck is NOT backbone capacity.

**Detail.** I trained the same recipe on bert-large-cased as an informal check; macro F1 moved by less than a point, training time tripled, and inference latency doubled. The error analysis shows the dominant errors are *boundary mismatches* and *ambiguous location types* — neither of which is solved by more parameters. They are solved by structural changes (span-level CRF) or by KB features at training time. A larger backbone would buy diminishing returns. For an operational system that may need to be retrained on a non-GPU server, the choice was deliberate.

**Flip to:** main slide 25 (error patterns) and backup B9 (baseline comparison).

---

### Q5. Your VICTIM F1 is 0.817 — the weakest entity. Why didn't you train on a victim-balanced corpus to fix this?

**Bottom line.** I did. That's what the template augmentation is — a victim-balanced second corpus stratified by entity-type presence.

**Detail.** Backup B6 shows VICTIM moves from 0.708 under plain cross-entropy on the unaugmented corpus to 0.817 with augmentation plus focal-loss-plus-weights. That is 11 F1 points of recovery against a known floor. The remaining gap is structural noise: VICTIM phrasings are extremely variable — anything from "civilians" to "Christian worshippers" to "the bus driver's family". You cannot template-generate all of those. The remaining gain has to come from real-news expansion (limitation 2) or span-level boundary refinement (future-work item 4).

**Flip to:** backup B6 and backup B12 (false-negative VICTIM examples).

---

## Domain-expert questions

### Q6. Your taxonomy has 95 leaves. ACLED has six top-level categories. Why this granularity?

**Bottom line.** ACLED's six categories are sufficient for cross-country counts. They are not sufficient for *operational targeting* — early warning needs the distinction between, say, election violence and post-election violence, or between a pastoralist-farmer clash and a generic ethnic clash.

**Detail.** The taxonomy is hierarchical so that ACLED-comparable cross-country counts are still recoverable by collapsing to Level 1. Operational consumers who need finer granularity drop into Level 2 or 3. The two African-specific extensions — pastoralist-farmer clashes and communal cattle raiding — were the categories the UAT participants asked for most often. ACLED's "Violence against civilians" bucket includes both, but cattle raiding in the Karamoja cluster is a different operational problem from politicised attacks on civilians in eastern DRC.

**Flip to:** main slide 13 and backup B5 (full taxonomy).

---

### Q7. What's the inter-annotator agreement on your annotations?

**Bottom line.** Cohen's κ of 0.78 on a 200-document pilot — substantial agreement.

**Detail.** Backup slide B10 shows the four most common disagreement classes. The biggest is qualifier inclusion ("at least 12" vs "12") — settled by a written rule that qualifiers are part of the CASUALTIES span. Second is case handling of armed-group names — settled as case-insensitive. Third is what counts as a victim phrase — settled by a surface-form rule listing the noun-phrase patterns that qualify. The 0.22 disagreement floor is mostly structural — natural language is genuinely ambiguous in places — and reading down to 0.22 from a 0.40 baseline took six iterations of the annotation guidelines.

**Flip to:** backup B10.

---

### Q8. Your KB has only 150 armed groups. ACLED tracks thousands. Why so small?

**Bottom line.** Coverage of the *active* African armed-group landscape, not historical exhaustiveness.

**Detail.** ACLED's actor list includes inactive groups, splinter factions that ceased operations, and group-instance combinations (e.g., "Al-Shabaab faction in Kismayo"). The KB here covers the canonical names of currently or recently active groups across the continent, with their aliases. Aliases matter more than raw group count for the validation-and-enrichment task: a typical extracted mention is "Al-Shabaab militants" or "the al-shabaab", and the KB collapses both to the canonical entry. The mean alias count per group is 4.2.

**Flip to:** backup B8 (KB composition).

---

### Q9. How does this generalise to a country your KB doesn't cover well — say, Cabo Delgado in Mozambique?

**Bottom line.** The NER component generalises (it learned the surface forms, not the specific groups). The KB does not — and that is a real operational risk.

**Detail.** Backup B9 shows the NER side of the system performs comparably on geographic regions outside the training corpus's heaviest coverage, because the BERT representations generalise the syntactic and lexical patterns of conflict reporting. What does NOT generalise is the KB: a new theatre like Cabo Delgado would extract ASWJ mentions correctly but would not enrich or validate them, because ASWJ is not yet in the KB. The fix is operational: a domain expert adds the entries. This is what recommendation 2 ("keep the KB alive") is about.

**Flip to:** main slide 18 and backup B8.

---

## Systems-person questions

### Q10. Your inference latency is 150 ms per article. What is the bottleneck and what would streaming look like?

**Bottom line.** BERT forward pass at 75 % of the latency; KB look-up at 15 %; tokenisation, BIO decode, and 5W1H grouping at 10 %.

**Detail.** Batch inference brings per-article cost down to about 25 ms on the same hardware. For streaming, the architecture would not need to change — the FastAPI route already supports async — but the throughput target would need a GPU node and a queue (Kafka or Kinesis). Latency budgets in §6.8 of the thesis already cover most batch loads. Real-time streaming is a lower-priority future-work item because no current consumer requires sub-second extraction.

**Flip to:** no slide — verbal answer is sufficient.

---

### Q11. Have you stress-tested the system for concurrent users?

**Bottom line.** Not formally. The single-process FastAPI deployment was sized for the UAT cohort of five.

**Detail.** The deployment used in the UAT runs a single uvicorn worker on the M2 Max box. Inference is single-threaded because the BERT model is held in one process; concurrent requests queue behind each other. For production with N analysts working concurrently, the right scaling pattern is multiple inference workers behind a load balancer, sharing the KB via a read-only volume. This is enterprise-deployment plumbing and is correctly classified as lower-priority future work. It is not a research question.

**Flip to:** no slide — be honest, do not over-claim.

---

### Q12. PostgreSQL is overkill for 30,000 events a year. Why not SQLite?

**Bottom line.** PostgreSQL was chosen for the query layer, not the storage tier — full-text search on the article column, JSONB on the extracted_record column, and concurrent-user write safety.

**Detail.** SQLite would handle the volume comfortably, but the analytics layer relies on PostgreSQL's full-text search index over article bodies and on JSONB indexing of the extracted_record column. Both are operations that SQLite handles weakly or via extensions. The Docker Compose footprint for PostgreSQL 16 is small enough that this trade-off is essentially free.

**Flip to:** main slide 15 (architecture).

---

## Generalist questions

### Q13. Why didn't you just use a large language model — GPT-4 or Claude — instead of training a BERT?

**Bottom line.** Cost, controllability, on-prem deployability, reproducibility.

**Detail.** An LLM call against an external API at 150 ms per article, at 30,000 articles per year, is operationally viable. But it carries four risks: (1) per-article cost — predictable for BERT, variable and provider-dependent for an LLM; (2) controllability — a fine-tuned BERT's output schema is fixed; an LLM's prompt is a fragile contract; (3) data sovereignty — many AU member states will not send conflict-reporting metadata to a US-based commercial API; (4) reproducibility — a closed-weights model can be updated by its vendor without notice, breaking the thesis's evaluation guarantees. A fine-tuned BERT is auditable, reproducible, and deployable on-prem. That mix matters more in the early-warning context than raw accuracy.

There is also a research case: this thesis evaluates a specific methodological combination (focal loss + class weights + KB validation) on African violent-event extraction. That combination is the contribution. An LLM zero-shot baseline is a different paper.

**Flip to:** main slide 32 (limitations).

---

### Q14. The 5W1H framing is journalistic, not academic. Why this schema rather than ACE-2005's event-argument framework?

**Bottom line.** 5W1H is what AU-CEWS analysts and ACLED coders actually use. Optimising for an academic framework would have produced a tool no operational consumer would adopt.

**Detail.** ACE-2005 is rigorous but uses event-argument labels (Attacker, Target, Place, Time-Within) that are equivalent to 5W1H slots under a relabelling. The advantage of 5W1H is interface legibility: an analyst looking at the inference screen recognises WHO/WHAT/WHEN/WHERE/HOW/WHY immediately without training. The UAT confirmed this — the 5W1H-clarity Likert item scored 4.6. An ACE-style interface would have required familiarisation. The choice is operational, not methodological — and the underlying labels can be remapped to ACE-2005 if a future consumer requires it.

**Flip to:** main slide 5 (the structured-record example).

---

### Q15. What if the panel disagrees with one of your design decisions — say, the threshold of 80 % for grounding?

**Bottom line.** Disagreement on the threshold is legitimate. The threshold is reported as a design parameter, not a discovered constant. Lowering it to 70 % brings back two entity types (TIME and DURATION); raising it to 90 % drops one more (DISTRICT). Both alternatives were considered.

**Detail.** The 80 % threshold was the elbow of the grounding-rate distribution — entity types fell into a cluster above 80 % and a cluster below 60 %, with very little in between. That bimodality was the rationale, not an a priori choice. If a panel preferred a different threshold, the methodology is unchanged; only the retained-entity set shifts. The thesis reports the threshold and the entities at it; a reader who disagrees can re-derive the schema at their preferred cut. This is the right kind of transparency.

**Flip to:** main slide 12.

---

## Motivation and significance

### Q16. Why is this thesis-worthy? Couldn't the same outcome be reached with a careful fine-tuning notebook and a hosted UI?

**Bottom line.** The contribution is the *methodological combination* — grounding-based schema design, focal-loss-plus-class-weights training, and KB validation-and-enrichment — evaluated together on African violent-event extraction. None of those ingredients is novel in isolation; the combination, evaluated at this scale on this domain, is.

**Detail.** A fine-tuning notebook would produce a model. A hosted UI would produce a product. Neither would constitute research. The thesis-worthy claims are three empirically-supported findings: that focal loss + inverse-frequency weights together lift VICTIM by 11 F1 points without hurting other entities (an ablation result, not a tuning trick); that KB-validated extraction surfaces 2.4 % of events as analyst re-read candidates (an operational metric, not a model metric); and that a non-ML user can drive the full pipeline (a systems result, validated by UAT). Three independent results, one integrated system.

**Flip to:** main slide 31 (contributions).

---

### Q17. Why does this matter for Ethiopia and the African Union specifically?

**Bottom line.** AU-CEWS is mandated by Article 12 of the Protocol Establishing the Peace and Security Council to monitor and report on conflict across the continent. That monitoring is bottlenecked on analyst time, and the analyst workforce is finite. This thesis offers a measurable reduction in the cost of producing each structured event record.

**Detail.** Addis Ababa hosts the AU headquarters, and AU-CEWS sits a short distance from this campus. Reduced extraction cost is not abstract — it translates directly into the AU's capacity to monitor more theatres, faster, with the same staff. For Ethiopia specifically, monitoring of Tigray, Amhara, and Oromia conflicts is conducted with similar manual pipelines by the Ministry of Peace and by academic groups; the same recipe applies.

**Flip to:** main slide 4 (information bottleneck).

---

### Q18. Who exactly do you imagine using this in three years?

**Bottom line.** Three concentric circles. Inner circle: AU-CEWS analysts and Ethiopia's Ministry of Peace, for production monitoring. Middle circle: academic conflict researchers — IPSS at AAU, ISS Africa in Pretoria, PRIO in Oslo — for retrospective coding of corpora. Outer circle: civil-society early-warning groups in West Africa and the Horn that already do manual coding and would adopt any tool that halved their workload.

**Detail.** Recommendation 1 in §7.4 — treat the output as a triage layer, not a final product — applies to all three circles. The system has different non-functional requirements for each: throughput matters most for the inner circle, accessibility for the outer.

**Flip to:** main slide 33 (recommendations are §7.4 of the thesis).

---

## Literature and scholarship

### Q19. The closest related work is Masakhane and AfriBERTa. Why did you build on bert-base-cased rather than an Africa-pretrained backbone?

**Bottom line.** Two reasons: bert-base-cased has well-documented NER fine-tuning behaviour that AfriBERTa did not at the time the work began, and AfriBERTa's pretraining corpus is dominated by African-language text — its English representations are not necessarily stronger than bert-base-cased.

**Detail.** AfriBERTa and AfroLM are excellent backbones for the multilingual extension in future work. For the English-only thesis here, bert-base-cased was the controlled choice: its NER fine-tuning recipe is well-documented, which lets the work isolate the contribution of focal loss + KB validation rather than confounding it with backbone novelty. When the multilingual extension is done, AfroLM is the natural backbone — that's stated as item 1 in §7.5.

**Flip to:** main slide 33 (future work).

---

### Q20. How do you position this against LLM-based event-extraction work emerging since 2024?

**Bottom line.** This thesis is the *deployable, auditable, reproducible* baseline that future LLM work will need to compare against. It is not in competition with LLM event extraction; it is the supervised reference point.

**Detail.** Three things make a published baseline important right now: closed-weight LLMs (GPT-4, Claude) are not reproducible (the vendor can update them silently); they are not auditable (you cannot inspect their inference path); and they are not deployable on-prem (data-sovereignty concerns rule them out for many AU member states). A fine-tuned BERT on African violent events fills all three roles and gives the field a fixed reference point. The thesis explicitly positions itself this way in Chapter 7.3.

**Flip to:** main slide 32 (limitations include the LLM-comparison gap).

---

## Methodology rigor and reproducibility

### Q21. Why design science as the methodological frame, and not a controlled empirical study?

**Bottom line.** Because the contribution is an artefact, evaluated empirically at each stage. That is the textbook definition of design science (Hevner et al. 2004; Peffers et al. 2007).

**Detail.** A controlled empirical study would be appropriate if the contribution were a falsifiable claim about a single technique — "focal loss outperforms cross-entropy on all token-classification tasks". That is not the claim. The claim is that an integrated artefact — schema + model + KB + UI — measurably improves on hand-coding for African violent-event extraction. Design science is the established frame for that kind of contribution: build, evaluate, iterate, generalise. The ablation in §6.6 is the embedded controlled experiment within the larger design-science programme.

**Flip to:** verbal answer; no slide.

---

### Q22. How reproducible are your results? What happens with a different random seed?

**Bottom line.** Run-to-run variance on macro F1 is about ±0.4 % across three seeds (42, 17, 91). No headline conclusion in the thesis flips at that variance.

**Detail.** Backup B1 lists the random seeds. The headline 0.887 macro F1 has run-to-run standard deviation of 0.004 — about half a percentage point. The 11-F1-point VICTIM improvement from focal-loss-plus-weights survives at every seed; the smallest observed gain across seeds is 9.8 F1 points. The headline claim is robust to seed choice. Statistical significance at p < 0.01 by paired bootstrap.

**Flip to:** backup B1 (hyperparameters include seed list).

---

### Q23. Is your validation set truly held out, or could information leak through your sampling strategy?

**Bottom line.** Held out at the article level. The stratified diversity sampler operates on the unsplit corpus; the 80/20 split is performed after sampling.

**Detail.** Information leakage in NER usually comes from one of three places: (1) duplicate articles in train and validation (controlled by deduplication on hashed article text before splitting); (2) overlapping templates between train and validation augmentation (controlled by partitioning augmentation templates into train-only and validation-only template pools); (3) shared rare entities — for instance, a rare armed group seen in training that appears in validation and gets memorised. The third is the harder one and is reported as a residual threat in §6.13 of the thesis. The KB does **not** see the validation split at training time.

**Flip to:** main slide 19 (dataset).

---

## Data, ethics, and bias

### Q24. What about bias in the ACLED data itself? Western-trained coders, English-language sources, urban over-representation — doesn't your model inherit all of that?

**Bottom line.** Yes — and naming this honestly is part of the contribution.

**Detail.** ACLED's coverage is documented to over-represent urban centres, English-language sources, and theatres of geopolitical interest to Western funders. Any model fine-tuned on ACLED inherits those biases. This thesis does not fix them — but it makes the propagation visible: the analytics dashboard shows event counts per country and per source, so an analyst using the system can see when coverage is thin in a region they care about. The KB curation actively counters one form of bias by including African-Union-active armed groups that ACLED's actor list under-represents. The deeper fix — sampling from non-ACLED sources, multilingual coverage — is in future work.

**Flip to:** main slide 32 (limitation 2).

---

### Q25. What are the ethical risks of building a violence-extraction system? Could this be misused?

**Bottom line.** The risks are real but bounded by what the system can do. It extracts events from already-published news. It does not surveil individuals, does not access private data, does not generate predictions of future violence at the individual level.

**Detail.** Three plausible misuse vectors. (1) **Targeting.** A government could use extracted records to identify and persecute named perpetrators. Mitigation: the system surfaces what was already public; it does not add information not already in the source article. (2) **Selective reporting.** A state actor could exclude their own forces from coverage by filtering source feeds. Mitigation: source-set transparency in the analytics dashboard. (3) **Over-reliance.** An analyst could treat machine output as truth without re-reading. Mitigation: confidence scores and KB flags surface uncertainty; recommendation 1 in §7.4 explicitly addresses this. Proposal-stage ethics review approved the work under the standard "publicly available news" data category.

**Flip to:** no slide — verbal answer.

---

### Q26. What's your annotation quality assurance process beyond IAA?

**Bottom line.** Three layers: written guidelines (Annex A), pilot rounds (six iterations), and spot-checks (a 10 % stratified sample of the final 50,000 examples re-reviewed).

**Detail.** The guidelines started at 9 pages in October 2025 and reached 31 pages by January 2026 — most of the growth was disambiguating edge cases that surfaced in IAA disagreements. The six pilot rounds reduced Cohen's κ disagreement from 0.40 to 0.22. The 10 % spot-check found 3.2 % label errors at a single-annotator pass; those were corrected. The residual error rate after correction is estimated at ~1 % by re-spot-checking the corrected sample. Reported in §5.2 of the thesis.

**Flip to:** backup B10.

---

## Specific technical depth

### Q27. Why max sequence length of 128 tokens? African news headlines and lead paragraphs can be longer.

**Bottom line.** 128 covers the mean article length (~64 tokens) plus two standard deviations. Articles longer than 128 are processed in 64-token sliding windows with 32-token overlap; spans straddling a window boundary are merged at decode time.

**Detail.** Max-length is a memory-vs-coverage trade-off. 256 would have been safer but would have halved the batch size on the training hardware. The sliding-window approach handles the long tail without paying the memory cost for short articles. Edge cases — entities split across window boundaries — are handled by the merger in §4.7. ~3 % of articles exceed 128 tokens; the sliding window adds < 5 ms to those.

**Flip to:** backup B1 (hyperparameters).

---

### Q28. The best model converges in epoch 2. Are you confident it's not under-trained?

**Bottom line.** Yes — overfitting begins at epoch 3 (validation loss rises while training loss continues to drop). Early stopping correctly identifies epoch 2 as the best checkpoint.

**Detail.** Backup B2 shows the per-epoch dynamics. Train loss continues falling through epoch 5; validation loss climbs after epoch 2. The model has the capacity to memorise the training set if allowed to — fine-tuned bert-base-cased on 50,000 examples is in the over-parameterised regime — so early stopping is doing its intended job. Fast convergence is a property of pre-trained transformers on focused fine-tuning tasks, not a bug.

**Flip to:** backup B2.

---

### Q29. Why span-level F1 rather than token-level? The token-level number is higher.

**Bottom line.** Span-level is the operationally meaningful metric. An analyst cares whether the model returned "Al-Shabaab" as a single ACTOR span, not whether 3 of its 4 sub-word tokens were correctly tagged.

**Detail.** Token-level metrics over-count successes — a 4-sub-word entity with 3 correct tags scores 75 % token-level but is operationally a *miss* because the analyst has to manually re-segment. Span-level (exact-match) is the strict version reported in §6.4. A relaxed-match span score (50 % overlap) would be 1.5–2 F1 points higher than exact-match, but exact-match is the conservative and standard NER reporting choice (CoNLL-2003 convention).

**Flip to:** main slide 23.

---

## Threats to validity

### Q30. Walk us through the threats to validity. Construct, internal, external, conclusion.

**Bottom line.** §6.13 lists all four explicitly. Headlines: *construct* (span-level F1 is a proxy for analyst utility); *internal* (template augmentation inflates in-distribution scores); *external* (English-only, ACLED-only); *conclusion* (small UAT cohort).

**Detail.**

- **Construct.** F1 measures correct-span recovery, but the operational utility is analyst time saved, which is not measured directly. UAT closes part of this gap.
- **Internal.** 30 % synthetic training data and same-distribution validation make the headline number an upper bound on real-world performance.
- **External.** English-only, sub-Saharan-focused, ACLED-coverage-shaped. Generalisation to French-language, North African, or non-ACLED-covered theatres is not established.
- **Conclusion.** n = 5 UAT is too small for inferential statistics; the Likert means are descriptive, not inferential.

**Flip to:** verbal answer; §6.13 of the thesis.

---

### Q31. The UAT had only five participants. Is that statistically meaningful?

**Bottom line.** It is not inferentially meaningful — Likert means at n = 5 are descriptive. It is *qualitatively* meaningful because all five completed all six tasks and the failure modes were consistent across participants.

**Detail.** UAT for systems work is conventionally small (Nielsen's "five users find 85 % of usability issues" rule of thumb). The thesis does not claim statistical significance on UAT scores; it reports them as descriptive triangulation against the quantitative F1 metrics. The constructive feedback was internally consistent — three out of five participants asked for drag-and-drop upload, three asked for per-entity training metrics — which is a stronger signal than mean Likert scores at this sample size. A larger UAT is appropriate before any production deployment but was out of thesis scope.

**Flip to:** main slide 29.

---

## Operational adoption

### Q32. How would AU-CEWS actually adopt this? What's the path from defense to deployment?

**Bottom line.** Three stages: pilot deployment on a single AU-CEWS analyst desk for one quarter, comparison against current manual coding throughput, then scale to the full analyst team if metrics clear.

**Detail.** Stage 1 (pilot, Q3 2026): one analyst's daily article load runs through VioNER in parallel with manual coding; the analyst spot-checks the output and reports time-to-record for both pipelines. Stage 2 (validation, Q4 2026): a head-to-head 30-day study; if VioNER halves the manual time without raising error rates above an agreed threshold, the trial is judged successful. Stage 3 (rollout, 2027): integration with whatever event store AU-CEWS uses, role-based access control added, multilingual extension started in parallel.

**Flip to:** main slide 33 (future-work item 1 is multilingual).

---

### Q33. What's the maintenance burden? Who keeps this alive after you graduate?

**Bottom line.** Two roles. A part-time domain expert keeps the KB current (estimated one day per week). A part-time software maintainer keeps the system running and applies security patches (estimated half a day per week).

**Detail.** The KB is the most decay-prone component — armed groups change names, splinter, recombine — and §7.4 recommendation 2 calls this out explicitly. One part-time domain expert with KB-admin access can keep ~150 groups current. On the software side, the FastAPI / React / PostgreSQL stack is conservative and well-supported; routine dependency updates and security patches are the bulk of maintenance. Retraining the model on fresh data is a quarterly task, not weekly. All three roles are scoped in §7.4 recommendation 2.

**Flip to:** main slide 33.

---

## AAU-standard closing questions

### Q34. If you had another year to work on this, what would you change first?

**Bottom line.** Multilingual extension — XLM-R or AfroLM backbone, fine-tuned on parallel African-news corpora.

**Detail.** It is item 1 in high-priority future work for the same reason it would be item 1 in another year of effort: a monolingual extractor leaves the French, Arabic, Portuguese, and African-language signal on the floor, and that signal is roughly half of African conflict reporting. The architecture does not need to change to support this — the training data and the encoder choice do. The work would take six months of corpus assembly and three months of training-and-evaluation; one year is the right horizon for a credible v2.

**Flip to:** main slide 33.

---

### Q35. What is the single biggest takeaway from this thesis?

**Bottom line.** That an integrated, deployable, reproducible artefact — schema, taxonomy, model, KB, system — outperforms any of its components alone for the African violent-event-extraction problem, and that focal-loss-plus-class-weights with KB validation is the empirically-supported recipe behind it.

**Detail.** Distil it to one sentence: *grounded supervision, imbalance-aware training, and curated knowledge-base validation, combined and packaged behind a usable interface, produce extracted records that analysts find trustworthy and that meaningfully reduce hand-coding cost.* That sentence sits behind the contributions slide.

**Flip to:** main slide 31.

---

### Q36. What advice would you give a student starting a similar project today?

**Bottom line.** Three things. Run a grounding pilot before designing the schema. Build the KB and the UI in parallel with the model, not after. Plan the limitations slide before the contributions slide.

**Detail.** The grounding pilot saved this thesis from training on 26 noisy entities — six weeks of work that would have been lost otherwise. Parallel KB and UI development meant the system was ready for UAT the day the model finished training, not three months later. Drafting the limitations slide early forced honesty about scope and prevented over-promising in the introduction. These are not novel pieces of advice but they are the ones that proved most useful procedurally.

**Flip to:** no slide — verbal answer, panel-warmth.

---

## When you genuinely don't know

A panel respects "I don't know" more than a confident wrong answer. Use this template:

> "That's a question I don't have direct evidence on. What I can offer is [closest related evidence I do have]. If I had to speculate, my best guess would be [bounded conjecture] — but I'd want to verify that before saying it confidently."

Examples of legitimate I-don't-knows for this thesis:
- "What's the F1 if you fine-tune on Wikipedia-pretrained AfroLM instead of BERT?"
- "Does the system work on Amharic news?"
- "What's the per-country F1 distribution?"

For each: name the closest evidence (B9 for backbone comparison; limitation 1 for non-English; the validation split was not stratified by country, so per-country F1 is not computed) and stop. Do not bluff.

---

## The single most important Q&A behaviour

The panel is not looking for you to be perfect. They are looking for you to be **calm, honest, and self-aware about the scope of your own work**. A confident "we did not test that" is worth more than a vague "I think it would probably work." Defend what you built. Concede what you did not.
