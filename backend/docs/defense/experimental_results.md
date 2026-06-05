# VioNER Defense — Experimental Results Explained

The final piece of the study trilogy. This document takes **every number, every table, and every chart** in Chapter 6 of the thesis and explains:

- **What it shows** — in plain English, no jargon
- **How to read it** — column by column, row by row
- **What it means** — for the analyst, for the contribution claim, for the panel
- **A worked example** — concrete numbers you can hold in your head
- **What a panellist might ask** — with prepared answers

If you've felt foggy when looking at F1 tables, ablation grids, or Likert scores — this is the document that fixes that. Read it top to bottom once, then keep it open during slide 27-29 rehearsal.

---

## How to use this document

| Pass | Purpose |
|:--|:--|
| **Read 1** — full pass | Understand what every table in Chapter 6 is showing |
| **Read 2** — Parts 4, 5, 6, 7 | The headline metrics and the ablation — these are what slides 27-29 are based on |
| **Read 3** — Part 11 | How each result supports each contribution claim |
| **Defence eve** — Part 12 only | Q&A scripts for results questions |

---

# Part 1 · The experimentation philosophy — why we measure what we measure

Before we look at any numbers, we need to know **what kind of evidence the thesis is producing and what it's evidence *for*.**

## What does "evaluation" mean for a machine-learning system?

A trained model is a black box. We poured 50,000 examples of training data into it, ran the optimiser for a few hours, and out came a checkpoint with 110 million weights. The natural question is *"how good is this thing?"* Evaluation is the structured way of answering that question.

The catch: you can't evaluate the model on the same data it trained on. The model has *seen* that data — it may have memorised parts of it. Evaluating on training data is like grading a student on a take-home test where they wrote the answer key themselves. The number you get back is flatteringly high but tells you nothing about how the student will do on a fresh exam.

This is why VioNER **holds out a validation set**. 80% of the 50,000 examples become training data; the remaining 10,000 are set aside and the model **never sees them during training**. After training is done, we run the model on the 10,000 held-out examples and measure what comes out. *Those* numbers are honest — they tell us how the model performs on data it didn't memorise.

> **The held-out validation set is the source of every number you'll see in this document.** When the thesis reports "macro F1 = 0.887", that's the macro F1 on the 10,000 held-out examples. When the ablation table compares loss functions, all four are evaluated on the same 10,000 held-out examples.

## The four kinds of evaluation in this thesis

| Evaluation kind | What it measures | Where in Chapter 6 |
|:--|:--|:--|
| **Quantitative model evaluation** | How well the trained model extracts entities — precision, recall, F1 per entity, overall | §6.4, §6.5 |
| **Ablation** | Which design choices actually contributed — train 4 models with different loss functions and compare | §6.6 |
| **Operational impact metrics** | What the KB layer actually does on real extraction — flag rate, enrichment rate | §6.7 |
| **User Acceptance Testing (UAT)** | Whether a non-ML analyst can use the system end-to-end | §6.10 |

Each kind of evaluation supports a different claim. The model metrics support RQ2 (modelling quality). The ablation supports the contribution claim about loss-function choice. The operational metrics support RQ3 (KB value). The UAT supports RQ4 (system usability).

When a panellist asks *"what evidence supports your claim?"* — the answer depends on which claim. This document walks through each.

## What each number is "made of"

Most metrics in this document come from comparing the model's predictions to gold-standard human labels. The basic units are:

- **TP (true positive)** — the model predicted an entity, and it was correct
- **FP (false positive)** — the model predicted an entity that wasn't actually there
- **FN (false negative)** — there was an entity the model missed

These three numbers determine **precision**, **recall**, and **F1** — the three metrics that appear on every slide and in every table. The next few Parts walk through them.

---

# Part 2 · The training corpus — by the numbers

Before looking at how well the trained model performs, you need to know *what it was trained on*.

## The 50,000-example corpus

| Source | Examples |
|:--|--:|
| ACLED open-data export (stratified diversity sample) | 35,000 |
| Template-based augmentation (rare-class coverage) | 15,000 |
| **Total fine-tuning corpus** | **50,000** |

These 50,000 are *examples* — each one a tokenised sentence (or short passage) with BIO labels for every token.

### What "stratified diversity sampling" means in practice

ACLED's full African events file is roughly 212,000 records. Naïve random sampling would pull mostly *common* events (single armed-clash incidents, repeated IED patterns) because those dominate the file. Stratified diversity sampling instead **oversamples** rare entity types — events involving distinctive victim phrasings, unusual casualty descriptions, action verbs in passive voice.

The effect: the 35,000-example sample has roughly the same operational coverage as the full 212,000-example file, but with more representational variety on the entities the analyst cares about most.

### What "template-based augmentation" means in practice

A template is a fill-in-the-blank pattern with slots for entity types:

```
Template: "[ACTOR_PHRASE] attacked [VICTIM_PHRASE] in [CITY] on [DATE], killing [CASUALTIES_PHRASE]."

Filled:   "Boko Haram militants attacked Christian worshippers in Maiduguri on Friday,
           killing at least 17."
```

Templates let you generate synthetic training examples with controlled coverage of rare entity types. The 15,000 augmented examples specifically pad the under-represented entity types (VICTIM, ACTION, CASUALTIES) so the model has enough samples to learn from.

## Class imbalance — the key fact about the corpus

Across all the tokens in the training set, the BIO-label distribution is roughly:

| Label group | Token share |
|:--|--:|
| O (outside any entity) | **~78%** |
| ACTOR entities (B-ACTOR + I-ACTOR) | ~6% |
| CITY entities | ~5% |
| DATE entities | ~3% |
| REGION + DISTRICT entities | ~5% |
| **VICTIM, ACTION, CASUALTIES** combined | **~3%** |

**That bottom row is the operational pain point.** The entities the analyst needs most (victims, casualty counts, action verbs) are the rarest. The model has fewer examples to learn from, the optimiser gives them less gradient signal, and the resulting per-entity F1 is lower without explicit imbalance handling.

This is the empirical reason for the focal-loss + class-weights training recipe (Contribution 3). The whole training methodology exists because of this distribution.

## The 80/20 train/validation split

- **80%** of 50,000 = **40,000 examples** used for training
- **20%** of 50,000 = **10,000 examples** held out for validation

The split is **stratified on entity-type presence** — meaning the validation set has the same proportional mix of entity types as the training set. If 12% of articles in the corpus contain a VICTIM mention, the validation set also has ~12% with VICTIM mentions.

Additional integrity controls (covered in §6.13 of the thesis):

- **Article-level split**, not sentence-level — no article appears in both halves
- **Hash-based deduplication** before splitting — copy-pasted duplicates can't sneak across
- **Augmentation template pools partitioned** — train templates and validation templates don't overlap

These controls eliminate the main ways "validation leakage" sneaks into NER experiments. When the thesis reports a validation F1, it's a fair estimate of how the model would perform on truly new data.

---

# Part 3 · Training dynamics — watching the model learn

## What a training run looks like

Training proceeds in **epochs**. One epoch = one full pass through the 40,000 training examples. After each epoch, the model is briefly evaluated on the 10,000-example validation set to see how it's doing on data it hasn't seen.

The thesis reports per-epoch numbers in Table 6.5 (and a more detailed version in backup B2 of the defense slides):

| Epoch | Train loss | Val loss | Token accuracy | Macro F1 |
|:--:|--:|--:|--:|--:|
| 1 | 0.0231 | 0.0118 | 95.2 % | 0.823 |
| **2** | **0.0094** | **0.0074** | **96.7 %** | **0.887** |
| 3 | 0.0061 | 0.0079 | 96.6 % | 0.885 |
| 4 | 0.0044 | 0.0089 | 96.5 % | 0.881 |
| 5 | 0.0033 | 0.0102 | 96.3 % | 0.875 |

### Before reading the table — what "loss" actually is, step by step

The two loss columns are the most important — and the easiest to mis-read — so let's build them up carefully.

#### What is "loss" for a single token?

Recall from the formulas doc: for every token, the BERT model produces a probability for each of the 17 BIO labels. The **loss** for that one token is the formula's answer to *"how wrong was the model on this token?"* — a single non-negative number.

For plain cross-entropy (the simplest form), the per-token loss is just $-\log p_y$ where $p_y$ is the probability the model assigned to the *correct* label. A few illustrative values:

| Model's probability on the true label ($p_y$) | Per-token loss ($-\log p_y$) | What this means |
|--:|--:|:--|
| 0.99 | **0.010** | Confident-and-correct → tiny loss |
| 0.80 | **0.223** | Mostly right → small loss |
| 0.50 | **0.693** | Uncertain → noticeable loss |
| 0.20 | **1.609** | Wrong with some confidence → big loss |
| 0.05 | **2.996** | Confidently wrong → huge loss |

VioNER's production loss is more elaborate (focal loss + class weights + smoothing) — see `formulas_explained.md` Part A for the full math — but the shape is the same: small probability on the true label = big loss.

#### What is "loss" for a single training example (one sentence)?

A training example is a tokenised sentence. The per-example loss is the **average** of the per-token losses across all tokens in that sentence.

**Worked example.** A 5-token training sentence with gold labels:

| Token | Gold label | Model's $p_y$ at this moment | Per-token loss |
|:--|:--|--:|--:|
| Boko | B-ACTOR | 0.85 | $-\log(0.85)$ = 0.163 |
| Haram | I-ACTOR | 0.90 | $-\log(0.90)$ = 0.105 |
| killed | B-ACTION | 0.45 | $-\log(0.45)$ = 0.799 |
| civilians | B-VICTIM | 0.40 | $-\log(0.40)$ = 0.916 |
| today | B-DATE | 0.95 | $-\log(0.95)$ = 0.051 |

Per-example loss for this sentence = (0.163 + 0.105 + 0.799 + 0.916 + 0.051) ÷ 5 = **0.407**

Notice: the model is doing well on ACTOR and DATE but struggling on ACTION and VICTIM. The per-example loss is dominated by the two hard tokens (0.799 and 0.916) — exactly the operationally-critical rare entities focal loss is designed to suppress.

#### What is "loss" for one epoch?

An **epoch** is one full pass through the training data (or the validation data). The per-epoch loss is the **average** of the per-example losses across all examples in that epoch.

For VioNER:
- Train epoch loss = average across all **40,000 training examples**
- Val epoch loss = average across all **10,000 validation examples**

These two numbers are what Table 6.5 reports per epoch.

---

### Train loss vs val loss — what's different about how they're calculated

The two losses use the same per-token formula and the same averaging procedure. The difference is **what the model is doing while the loss is being computed.**

#### How **train loss** is computed

During training, the pipeline processes the 40,000 training examples in batches (16 examples per batch). For each batch:

1. The current model produces predictions on the batch
2. Per-token losses are computed (using gold labels)
3. The batch's loss is averaged
4. **The gradient is computed and the weights are updated** — the model has just become slightly different
5. The batch's loss is also recorded for the epoch average

After the entire epoch, the per-epoch train loss reported is the average across all the batch losses during that epoch.

**Important subtlety:** the model that produced the loss on batch 1 is NOT the same as the model that produced the loss on batch 2,500 (the last batch). The weights have been updated 2,500 times during that epoch. So **train loss for an epoch is a *rolling* average across a changing model** — the earlier batches were evaluated with worse weights, the later batches with better weights. The reported number is the mean.

Additionally, during training **dropout is ON** — a regularisation technique that randomly zeros out a fraction of the model's internal activations on each batch. Dropout makes the model harder to evaluate (effectively running with random sub-networks). This artificially inflates train loss.

#### How **val loss** is computed

After the epoch finishes — *and after all 40,000 training updates are done* — the pipeline switches to **evaluation mode**:

1. The model's weights are frozen (no more updates)
2. **Dropout is turned OFF** — the full network is used
3. All 10,000 validation examples are processed in a single sweep
4. Per-token losses are computed (using gold labels), averaged per example
5. The epoch's val loss = average across all 10,000 examples

Two big differences from train loss: (a) the model is at its end-of-epoch state, not rolling, and (b) dropout is off so the full network is in play. **Val loss is therefore computed against a "better" version of the model than most batches saw during training.**

#### Why val loss can be *lower* than train loss

Look at the table again:

| Epoch | Train loss | Val loss |
|:--:|--:|--:|
| 1 | 0.0231 | 0.0118 |
| 2 | 0.0094 | 0.0074 |

Val loss is **lower** than train loss at both epochs 1 and 2. That looks paradoxical — shouldn't the model do better on data it's seen than on data it hasn't?

The answer is the two effects above:

1. **Train loss is rolling.** Epoch 1's train loss averages batches from across the entire epoch, including the very early batches when the model had barely started learning. The first few hundred batches contribute high losses that drag the epoch average up.

2. **Dropout is off during validation.** The full BERT model running on validation is effectively a stronger model than the dropout-sub-sampled model that saw training batches.

This is a normal pattern when fine-tuning a pretrained transformer. Once training stabilises (epoch 2 onward), train and val loss become directly comparable.

#### What the gap between train loss and val loss tells you

The gap is called the **generalisation gap**. Read it across the rows:

| Epoch | Train loss | Val loss | Val − Train | What this signals |
|:--:|--:|--:|--:|:--|
| 1 | 0.0231 | 0.0118 | **−0.0113** | Val cheaper than train (dropout + rolling) |
| 2 | 0.0094 | 0.0074 | **−0.0020** | Still slightly negative; model fits both halves comparably |
| 3 | 0.0061 | 0.0079 | **+0.0018** | Train is now cheaper than val — **overfitting begins** |
| 4 | 0.0044 | 0.0089 | **+0.0045** | Gap widens — clear overfitting |
| 5 | 0.0033 | 0.0102 | **+0.0069** | Gap continues widening |

Once the gap flips positive and starts growing, the model is **memorising training-specific patterns** that don't generalise. Training-set performance keeps improving (the model "knows" the training set better) but held-out performance gets worse (the model has been over-specialised).

That flip happens between epoch 2 and epoch 3. That's why early stopping selects epoch 2 as the best checkpoint — it's the last epoch where the model's improvement on training data corresponded to genuine learning, not memorisation.

#### Summary — what each loss tells you

- **Train loss** answers: *"How well is the model fitting the data it sees during training?"* It drops monotonically as long as training continues — the model is always able to fit training data better with more updates.
- **Val loss** answers: *"How well is the model generalising to data it hasn't seen?"* It drops while the model is learning genuine patterns and rises once the model starts memorising training-specific noise.
- **The gap (val − train)** answers: *"Is the model learning or memorising?"* When the gap widens, memorisation is winning.

Train loss alone is not enough — you could drive it to zero by memorising the training set perfectly, and it would tell you nothing about the model's real quality. Val loss is what we actually optimise for (via early stopping). Train loss is the *companion signal* that tells us whether the val-loss improvement is real or coincidental.

---

### How to read this table — column by column

- **Epoch**: which pass through the data this row reports
- **Train loss**: average per-token loss across all 40,000 training examples during this epoch. Calculated *while* the model is being updated (so it's a rolling average over a changing model); dropout is on.
- **Val loss**: average per-token loss across all 10,000 held-out validation examples, evaluated *after* the epoch finishes with the model frozen and dropout off. Lower = better generalisation.
- **Token accuracy**: fraction of validation tokens where the predicted label (argmax over the 17-class distribution) matches the gold label.
- **Macro F1**: the operational metric we actually care about — average per-entity F1, evaluated on the same held-out validation set.

### What this table tells you

Read the **train loss** column top to bottom. It keeps falling: 0.0231 → 0.0094 → 0.0061 → 0.0044 → 0.0033. That's expected — every epoch the model fits the training data better.

Now read the **val loss** column. It falls for epoch 1 → epoch 2 (0.0118 → 0.0074), and then it starts *rising*: 0.0074 → 0.0079 → 0.0089 → 0.0102. This is **overfitting** — the model is getting better at training data but worse at held-out data because it's started memorising specific examples instead of learning generalisable patterns.

**Epoch 2 is the sweet spot.** Validation loss is lowest there (0.0074). Macro F1 is highest there (0.887). Token accuracy is highest there (96.7%). The thesis saves the epoch-2 checkpoint as the final model and discards everything after.

### How "early stopping" works

The training loop is told to stop training once validation loss stops improving for two consecutive epochs. So:
- Epoch 1 — val loss 0.0118
- Epoch 2 — val loss 0.0074 ← improved
- Epoch 3 — val loss 0.0079 ← worse (patience = 1)
- Epoch 4 — val loss 0.0089 ← worse (patience = 2) → STOP

The trained system reverts to the epoch-2 checkpoint and reports those numbers. This is why the thesis says *"convergence at epoch 2"* — that's where the best-performing model lives.

### What a panellist might ask

**Q: "Why does the best model converge so quickly — only 2 epochs?"**

> *"Because BERT was already pre-trained on Wikipedia and BookCorpus before fine-tuning, the model arrives at the NER task with strong general language representations. Fine-tuning is then a relatively short adjustment of the existing representations to the new entity schema. Two epochs of fine-tuning is enough for the model to specialise; more epochs cause it to start memorising training-specific patterns at the cost of generalisation. The validation loss curve in Table 6.5 confirms this — epoch 3 onward, validation loss rises."*

**Q: "Is 2 epochs too short? Could you have under-trained?"**

> *"No — early stopping correctly identifies epoch 2 as the best checkpoint by validation loss. Training longer didn't fail because of capacity; it failed because of overfitting. The model has the capacity to memorise the 50,000 training examples if allowed to. Early stopping prevents that. Backup slide B2 shows the per-epoch dynamics."*

---

# Part 4 · Overall model performance — the headline numbers

This is what slide 27 of the deck shows. Two numbers.

| Metric | Value | What it means |
|:--|--:|:--|
| **Micro F1** | **0.909** | Overall extraction quality, weighted by entity frequency |
| **Macro F1** | **0.887** | Overall extraction quality, with every entity type equally weighted |
| **Token accuracy** | 96.7% | Fraction of tokens with the correct label |

These are all measured on the 10,000-example held-out validation set, containing **190,075 gold entity spans**.

## What "F1" is, very simply

When the model produces output, each prediction falls into one of three buckets:

| Bucket | What happened |
|:--|:--|
| **True Positive (TP)** | Model said "this is an entity" and was right |
| **False Positive (FP)** | Model said "this is an entity" and was wrong |
| **False Negative (FN)** | Model missed an entity that was actually there |

From these three counts we compute two quality numbers:

- **Precision** = TP / (TP + FP) = *"of the entities I predicted, what fraction were correct?"*
- **Recall** = TP / (TP + FN) = *"of the entities that actually existed, what fraction did I find?"*

**F1** combines precision and recall into a single number:

$$F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}$$

F1 is high *only when both precision and recall are high*. A model with 100% precision but 10% recall scores only ~18% F1, not 55%. The harmonic mean punishes one-sided performance.

## A concrete worked example

Suppose the validation set has 100 VICTIM gold spans (the real victims that should be extracted). The model predicts 90 spans as VICTIM. Of those 90:

- 82 match an actual gold VICTIM (TP = 82)
- 8 don't match anything (FP = 8 — false alarms)
- 18 gold VICTIMs the model didn't find (FN = 18 — missed)

Compute:
- Precision = 82 / (82 + 8) = 82 / 90 = **0.911** → "When the model said VICTIM, it was right 91% of the time"
- Recall = 82 / (82 + 18) = 82 / 100 = **0.820** → "Of the actual victims, the model found 82%"
- F1 = 2 × 0.911 × 0.820 / (0.911 + 0.820) = 1.494 / 1.731 = **0.863**

So an F1 of 0.863 on VICTIM means: out of 100 actual victims, you'll find about 82, with about 8 false alarms.

## Micro F1 vs Macro F1 — the difference

Imagine the model achieves these F1 scores per entity:

| Entity | Support (gold spans) | F1 |
|:--|--:|--:|
| DATE | 31,938 | 0.956 |
| CITY | 44,361 | 0.934 |
| ACTOR | 47,612 | 0.923 |
| REGION | 24,331 | 0.891 |
| CASUALTIES | 4,907 | 0.885 |
| ACTION | 9,963 | 0.866 |
| DISTRICT | 21,471 | 0.826 |
| VICTIM | 5,492 | 0.817 |

**Macro F1** is the simple average of the 8 per-entity F1 values:

$$Macro F1 = (0.956 + 0.934 + 0.923 + 0.891 + 0.885 + 0.866 + 0.826 + 0.817) / 8 = 0.887$$

Every entity counts the same. VICTIM's 0.817 affects macro F1 just as much as DATE's 0.956 does, even though there are 6× more DATE spans than VICTIM spans in the validation set.

**Micro F1** is computed differently. Pool all the TP, FP, FN counts across all entities and compute F1 from those pooled totals:

$$Micro F1 = 2 \times \frac{\sum TP}{2\sum TP + \sum FP + \sum FN} = 0.909$$

Here the high-support entities (DATE, CITY, ACTOR) dominate because they contribute more TPs, FPs, and FNs to the pool. Micro F1 is therefore higher than macro F1 (0.909 > 0.887) because the entities with the most spans also have the highest F1.

## When to use which

- **Macro F1** = the right number for assessing **balance** across entity types. A bad rare-entity F1 drags it down sharply. This is the number that tells you *"does the model treat all entities fairly?"*
- **Micro F1** = the right number for estimating **overall throughput**. It tells you *"on average, what fraction of the entities in a batch of articles will I get right?"*

The thesis reports both because both are operationally meaningful. The relationship — micro > macro by about 2 points — confirms that the high-support entities (which the analyst sees most often) are performing best.

## What a panellist might ask

**Q: "Why is your headline metric F1 instead of accuracy?"**

> *"Because 78% of tokens are O (non-entity). A degenerate 'predict O everywhere' model would already score 78% token accuracy without learning anything. F1 ignores correct O predictions entirely and measures only how well the model recovers actual entities. That's the right metric for an extraction task — what matters is the entities you found, not the non-entities you correctly ignored."*

**Q: "Strict or relaxed span matching?"**

> *"Strict — both type and exact boundaries must match. CoNLL-2003 convention. A predicted span like '12 civilians' that overlaps a gold span of 'at least 12 civilians' counts as a false positive against the prediction AND a false negative against the gold. A relaxed-match score with 50% overlap tolerance would be 1.5-2 F1 points higher; we report strict for honesty."*

---

# Part 5 · Per-entity F1 — the rich detail

This is Table 6.7 of the thesis, and it's the table on slide 28. It tells you which entities the model does well on and which are hardest.

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
| **Macro avg** | — | **0.899** | **0.876** | **0.887** |
| **Micro avg** | 190,075 | **0.918** | **0.901** | **0.909** |

## How to read this table

### The Support column

This tells you **how many gold-standard spans of each entity type are in the validation set**. Add the eight numbers and you get 190,075 — the total number of gold spans across all entities. This is the "denominator" for everything else.

The Support column also tells you which entities are common (DATE 31,938, CITY 44,361, ACTOR 47,612) and which are rare (CASUALTIES 4,907, VICTIM 5,492). Rare entities have less training data to learn from and less validation data to evaluate against. Higher variance is expected on the rare rows.

### The Precision and Recall columns

For each entity, these tell you the two halves of the F1 story:

- **Precision** column for VICTIM = 0.838 → "When the model predicted VICTIM, it was correct 83.8% of the time"
- **Recall** column for VICTIM = 0.798 → "Of the actual VICTIMs in the validation set, the model found 79.8%"

Notice that **across every row, precision is slightly higher than recall**. That's a recurring NER pattern — when the model is unsure, it predicts O (the easy default) rather than risking a wrong entity prediction. The result is fewer false positives, more false negatives — high precision, lower recall.

For the analyst, this means: *"VioNER produces output you can mostly trust (precision is high), but you'll occasionally need to add an entity the model missed (recall is a bit lower)."*

### The F1 column

The harmonic mean of precision and recall. This is the single-number summary for each entity.

## How to read each row in plain English

**DATE (F1 = 0.956)** — the strongest. Date expressions in conflict reporting follow a small set of recognisable patterns ("on Monday", "January 15", "earlier this week"). The model finds them very reliably. *Analyst experience: "I never have to add a missing date."*

**CITY (F1 = 0.934)** — second strongest. Named cities like "Mogadishu", "Goma", "Kismayo" have distinctive surface forms that the model recognises consistently. *Analyst experience: "Cities are usually right; rare misses I can spot immediately."*

**ACTOR (F1 = 0.923)** — third strongest. African armed groups are well-supported in the training corpus and the model handles their variants ("Al-Shabaab", "Al Shabaab", "al-shabaab") well thanks to the case-sensitive backbone plus KB enrichment. *Analyst experience: "Perpetrators are usually correctly identified."*

**REGION (F1 = 0.891)** — strong middle tier. Region names have more compositional irregularity than cities (some regions double as cities, others are described relative to a country). *Analyst experience: "Mostly right; occasional region/country confusion I have to correct."*

**CASUALTIES (F1 = 0.885)** — strong middle tier despite being a rare entity. Casualty phrasings have a small set of patterns ("X killed", "Y dead", "Z wounded") that the model learns well. *Analyst experience: "Casualty counts mostly correct; the qualifier 'at least' sometimes dropped."*

**ACTION (F1 = 0.866)** — middle tier. Action verbs in passive voice ("were ambushed", "were displaced") are harder than active ones ("ambushed", "displaced"). The model misses about 14% of actions, especially in passive constructions. *Analyst experience: "Active-voice attacks are caught; passive ones I sometimes need to add."*

**DISTRICT (F1 = 0.826)** — weakest of the location types. Districts in Africa often share names with their main city ("Beni" the district vs "Beni" the town) or with their region. The model defaults to CITY for ambiguous cases. *Analyst experience: "District tagging is the location field I most often correct."*

**VICTIM (F1 = 0.817)** — the weakest. Victim phrasings are extremely variable ("civilians", "Christian worshippers", "the bus driver's family", "internally displaced schoolgirls"). The model recovers 80% of them; the missing 20% are the unusual phrasings. *Analyst experience: "Victims are the field I most often have to add or correct, especially for non-standard phrasings."*

## What this table tells you operationally

The table is a per-field guide to where the model's output is most/least reliable. An analyst using VioNER knows:

- Dates and locations are essentially solved — trust the output
- Actors are mostly solved — spot-check for new groups
- Casualty counts are mostly solved — verify the qualifier
- Actions need occasional addition for passive-voice constructions
- Districts and victims need the most analyst correction

That per-field reliability map is what makes the review-vs-rewrite workflow finally save time. The analyst knows what to skim and what to read carefully.

## What a panellist might ask

**Q: "Why is VICTIM the worst?"**

> *"Combination of low support (5,492 gold spans vs 47,612 for ACTOR) and high phrasing variability — anything from 'civilians' to 'Christian worshippers' to 'the bus driver's family' can be a VICTIM. The model has fewer examples to learn from and a wider variety to recognise. The ablation in section 6.6 shows the focal-loss recipe lifted VICTIM by 11 F1 points over plain cross-entropy; the remaining gap is structural noise that needs either real-news expansion (limitation 2) or boundary refinement via a span-level CRF (future work item 4)."*

**Q: "Why is precision higher than recall on every row?"**

> *"Standard NER behaviour. When the model is uncertain about whether a token is an entity, it defaults to O — the safe choice. The cost is missing some real entities (lower recall); the benefit is fewer false alarms (higher precision). For an analyst reviewing extracted records, higher precision is preferable to higher recall — fewer false alarms means less time spent rejecting model predictions. The per-category confidence thresholds in section 4.7 can be tuned per use case to trade precision for recall."*

---

# Part 6 · The ablation table — the most important table in the thesis

This is Table 6.8 of the thesis. It's the table on slide 29. It's the **single most important table in Chapter 6** because it's the evidence for the contribution claim about loss-function choice (Contribution 3, Gap 2).

| Entity | Plain CE | Weighted CE | Focal (γ=2) | **Focal + weights** |
|:--|--:|--:|--:|--:|
| ACTOR | 0.914 | 0.918 | 0.920 | **0.923** |
| ACTION | 0.794 | 0.834 | 0.842 | **0.866** *(+0.072)* |
| VICTIM | **0.708** | 0.776 | 0.792 | **0.817** *(+0.109)* |
| CASUALTIES | 0.853 | 0.871 | 0.872 | **0.885** |
| **Macro avg** | 0.855 | 0.873 | 0.878 | **0.887** |

## What the table shows

Four training configurations were tested **under identical conditions** — same data, same scheduler, same random seeds, same number of epochs. The **only** thing different between the four runs was the loss function.

The thesis evaluated each trained model on the same 10,000-example held-out validation set and reported the per-entity F1 for the rare entities (the ones the loss change is most meant to help) plus the macro average.

## How to read this table — column by column

### Column 1: Entity

Lists four operationally-important entities. The full per-entity table for the production configuration is Table 6.7 (shown in Part 5 above); this ablation focuses on the rare/medium entities where the loss change should have the biggest effect.

### Column 2: Plain CE — the baseline

"Plain CE" = plain cross-entropy. This is what generic BERT NER models use by default. No imbalance handling at all. Train on whatever distribution is there.

These are the F1 scores the model achieves with this baseline loss. They tell you what the analyst would get from a generic-trained NER system.

### Column 3: Weighted CE

Cross-entropy with inverse-frequency class weights. Each token's loss is multiplied by a per-class weight; rare classes get larger weights. This is **one of two ingredients** in the production loss.

### Column 4: Focal (γ=2)

Focal loss alone, with the focusing parameter γ = 2.0. This adds a per-example multiplier that suppresses easy-correct tokens so the model focuses on hard ones. This is **the other ingredient**.

### Column 5: Focal + weights (the production choice)

Both ingredients combined. This is the loss function actually deployed in VioNER's production model.

## How to read each row in plain English

### Reading the VICTIM row

> Plain CE: 0.708 — *"With a baseline generic-NER loss, VioNER finds 71% of victims with similar precision."*
>
> Weighted CE: 0.776 — *"Adding class weights alone lifts that to 78% — gain of ~7 F1 points."*
>
> Focal alone: 0.792 — *"Focal loss alone lifts it to 79% — gain of ~8 F1 points."*
>
> **Focal + weights: 0.817** — *"Combining both ingredients lifts it to 82% — gain of ~11 F1 points over baseline."*

The combination beats either ingredient alone. This is the **complementarity** claim — the two ingredients attack different parts of the imbalance problem and stack with each other.

### Reading the ACTION row

Plain CE: 0.794 → Focal + weights: 0.866. Gain of +7.2 F1 points. Same pattern as VICTIM — the combination beats each ingredient alone.

### Reading the ACTOR row

Plain CE: 0.914 → Focal + weights: 0.923. Gain of only +0.9 F1 points. ACTOR is a common entity (47,612 spans) that the baseline already handles well. Imbalance-handling tweaks don't help much here because there isn't an imbalance problem to solve for ACTOR.

### Reading the Macro row

Plain CE macro: 0.855 → Focal + weights macro: 0.887. Gain of +3.2 F1 points overall. Macro F1 is dominated by the rare-class gains because rare classes count equally in the macro average.

## What this table proves

Three claims, each backed by a specific comparison in the table:

### Claim 1: The combination of focal loss + class weights beats plain cross-entropy

Compare column 2 (plain CE) with column 5 (focal + weights). Every entity improves. Macro F1 improves by 3.2 points. The combination is **measurably better** than what generic NER training would produce.

### Claim 2: Each ingredient alone is insufficient

Compare column 2 (plain CE) → column 3 (weighted CE) → column 5 (focal + weights). Class weights alone give partial credit (+7 on VICTIM). The combination gives more (+11 on VICTIM). Similarly, focal alone gives +8 on VICTIM; the combination gives +11. **Neither ingredient alone reaches what the combination achieves.** That's the complementarity claim — the two ingredients are non-redundant.

### Claim 3: No entity is hurt by the production configuration

Look at every row. Column 5 (focal + weights) is ≥ column 2 (plain CE) for **every entity**, not just the rare ones. The combination doesn't trade common-class accuracy for rare-class accuracy — that would be operationally unacceptable for analyst workflows that depend on DATE and ACTOR. The thesis explicitly verifies this and reports it as a property of the loss choice.

## How to use this table in the defense

When a panellist asks *"how do you know your loss function actually helps?"* — point at this table. Walk them through the comparison from left to right on the VICTIM row, then on the ACTION row. The +11 and +7 deltas are the empirical answer.

When a panellist asks *"why not just use class weights?"* — point at columns 3 vs 5. Weighted CE alone gives VICTIM 0.776; the combination gives 0.817. The +4 point delta is the evidence that focal loss adds something class weights don't.

When a panellist asks *"why not just focal loss?"* — point at columns 4 vs 5. Focal alone gives VICTIM 0.792; the combination gives 0.817. The +2.5 point delta is the evidence that class weights add something focal loss doesn't.

## A worked example: what does +11 F1 actually mean for the analyst?

Imagine the analyst processes 100 articles per day. Each article averages ~5 VICTIM mentions = 500 victims per day.

Under plain cross-entropy (VICTIM F1 = 0.708):
- Recall ≈ 0.700 → model finds **350** of the 500 victims per day
- The analyst has to manually add the **150** missed victims to records

Under focal + weights (VICTIM F1 = 0.817):
- Recall ≈ 0.798 → model finds **400** of the 500 victims per day
- The analyst has to manually add the **100** missed victims

**That's 50 fewer victims per day the analyst has to add manually.** Across a 250-day working year, that's ~12,500 fewer analyst additions per year for the same coverage. At 30 seconds per addition, that's about **100 analyst-hours saved annually** just on victim-entity recovery.

That's what +11 F1 on VICTIM means operationally. It's not an abstract metric improvement; it's measurable time recovery for the consumer.

## What a panellist might ask

**Q: "Is the +11 F1 gain on VICTIM statistically significant?"**

> *"Yes. The thesis ran each configuration with three random seeds (42, 17, 91). Run-to-run macro F1 variance is about ±0.4 percentage points. The +10.9 VICTIM gain exceeds this variance by 25×. Paired bootstrap at the article level confirms p < 0.01 for the VICTIM and ACTION gains. Section 6.4 discusses the variance and section 6.6 reports the significance."*

**Q: "Why isn't there an entry for label smoothing in the ablation?"**

> *"Label smoothing is a third ingredient in equation 2 of the thesis (the production loss). It was tested separately in section 6.4 — turned out to have a marginal effect on validation loss but improves calibration of confidence scores. We kept it in production but didn't structure a separate ablation row because the effect was too small to be visible in the F1 table. Section 6.4 reports the comparison: val loss 0.0074 without smoothing, 0.0076 with smoothing."*

---

# Part 7 · KB validation impact — the operational metrics

This is the evidence for Contribution 4 (curated knowledge base) and Gap 3 (trust and aggregation). Reported in §6.7 of the thesis.

## The two numbers

| Metric | Value | What it measures |
|:--|--:|:--|
| Geographic-implausibility flag rate | **2.4%** | Fraction of extracted events where the KB flags an actor/location mismatch |
| ACTOR enrichment rate | **64.3%** | Fraction of extracted ACTOR mentions that successfully match a canonical KB entry |

Both are measured on the held-out validation set.

## What the 2.4% flag rate means in practice

Out of every 100 events the system extracts, the KB flags ~2 of them for analyst re-read because the actor and location don't match plausibly. The other 98 events have no flag (either the actor-location pair is plausible, or the KB doesn't have enough info to judge).

### A concrete walk-through

Imagine an analyst processes 1,000 articles in a week, producing ~1,000 extracted event records. The KB flag rate of 2.4% means:

- **~24 records** get a `geo_implausible` flag → these should be re-read by the analyst before being used downstream
- **~976 records** have no flag → these proceed to the event store with normal confidence

The analyst's workflow becomes:
1. **Review the 24 flagged records first** (priority queue)
2. Approve / correct / reject each one
3. **Browse the 976 unflagged records as routine**

This is the operational value of the validation layer: it directs analyst attention to the records most likely to need review. Without the KB, every record looks equally trustworthy; the analyst would have to spot-check randomly. With the KB, the spot-check is targeted.

### Why 2.4% and not higher

The flag rate is the *intersection* of:
- The KB having coverage of both the actor and the location
- The actor and location having genuinely different country mappings
- The model having actually misextracted one of them OR the article reporting something unusual

It's a conservative signal. Most extractions pass plausibility because most articles correctly pair an actor with their actual theatre of operation. The 2.4% are exactly the cases where something is genuinely off.

## What the 64.3% enrichment rate means in practice

Out of every 100 ACTOR mentions the model extracts, ~64 of them get matched to a canonical KB entry. The other ~36 either don't match the KB (unknown actor, new group, generic phrase like "armed men") or match below the 0.85 fuzzy-match threshold.

### A concrete walk-through

Same 1,000 articles, ~3,000 ACTOR mentions across them (each article averages ~3 perpetrator references).

- **~1,929 ACTOR mentions** (64.3%) match a canonical KB entry → these get enriched with canonical name, country code, group type
- **~1,071 ACTOR mentions** (35.7%) don't match → these carry only the raw surface form

Downstream analytics query like *"all Al-Shabaab attacks this month"*:
- Without enrichment, the query matches only records with the exact string "Al-Shabaab" — counts maybe 18 events
- **With enrichment**, the query matches by `kb_id`, recovering "Al Shabaab" / "al-shabaab" / "Al-Shabaab militants" / "Al-Shabaab fighters" too — counts the true ~34 events

The enrichment rate determines how much of the analytics layer benefits. 64.3% is enough to make most actor-aggregation queries substantially more accurate, even when some mentions remain unenriched.

### Why 64.3% and not higher

The remaining 35.7% break down roughly as:
- **Unknown / new armed groups** (~15%) — not yet in the KB; need curation
- **Generic phrasings** (~10%) — "unknown gunmen", "armed men", "unidentified attackers" — no canonical match possible
- **Below-threshold matches** (~10%) — close enough to plausibly be a known group but below the 0.85 confidence cut-off to avoid false matches

The thesis sets the threshold conservatively. Lowering it would increase enrichment rate but introduce false canonicalisations (collapsing distinct groups under one entry). Conservative threshold = higher precision on enrichment = analyst trusts the canonical match when it happens.

## What a panellist might ask

**Q: "Is 2.4% flag rate enough to be useful?"**

> *"Yes — and small flag rates are operationally appropriate. The flag identifies the records that most benefit from analyst re-read. If the flag rate were 30%, analysts would treat it as noise; if it were 0.2%, it would miss too many genuine cases. 2.4% lands in the sweet spot — small enough to feel manageable as a priority queue, large enough to catch the systematic errors that matter. Section 6.7 reports the breakdown of what gets flagged: the majority are extraction errors the model genuinely got wrong, with a minority being articles describing unusual events that warrant verification."*

**Q: "What happens to the 35.7% of actors that don't enrich?"**

> *"They carry the raw surface form. The downstream record stores the extracted text but no kb_id. Analytics queries that aggregate by kb_id won't include them; queries that aggregate by raw text might find them if the surface form happens to match. The unenriched records aren't lost — they just don't benefit from canonicalisation. New armed groups that emerge after KB curation are exactly this case, which is why §7.4 recommends ongoing KB maintenance — recommendation 2."*

---

# Part 8 · Inference latency — how fast is fast enough

This is §6.8 of the thesis. The number is **~150 ms per article on a single CPU core**.

## What 150 ms means in practice

That's about a sixth of a second. Per article. On commodity hardware.

### What 150 ms enables

- An analyst pasting an article into the UI gets entity chips back **before they can blink twice**
- Batch processing 30,000 articles per year takes ~75 minutes of compute time total
- A single CPU box handles every African violent event article published in a year, with thousands of percent of headroom

### Comparison with the manual baseline

| Process | Time per article |
|:--|:--|
| Manual coding by an analyst | **15–25 minutes** |
| VioNER inference + analyst review | **150 ms + review time** |

If review time averages even 5 minutes per article (down from 15-25 minutes of from-scratch coding), VioNER reduces per-article cost by **3-5×**. That's the speed half of Gap 1 (Part 6 of this document).

### Where the 150 ms is spent

Detailed breakdown from §6.8 of the thesis:

| Step | Latency contribution |
|:--|--:|
| BERT forward pass (the model itself) | ~75% |
| KB validation + enrichment | ~15% |
| Tokenisation, BIO decode, 5W1H grouping | ~10% |

The BERT forward pass is the dominant cost. This is expected — a 110M-parameter neural network is the most computationally expensive component. The KB lookup is fast because the KB is in-memory (preloaded at server startup, not re-queried from a database).

### Throughput

On the M2 Max with MPS acceleration, throughput is roughly:
- **Single-article inference**: ~150 ms (the latency number)
- **Batch-mode inference** (32 articles at once): ~25 ms per article
- **Sustained throughput**: ~40 articles/sec on the production hardware

Batch inference is faster per article because the GPU/MPS overhead is amortised across the batch. For VioNER's use case (analyst pastes one article at a time), the single-article number is what matters.

## What a panellist might ask

**Q: "Is 150 ms fast enough for production?"**

> *"For VioNER's use case — analyst-driven article submission — yes. The analyst pastes an article, gets results back in less time than it takes them to look up from the keyboard. For real-time streaming use cases (Kafka or Kinesis ingestion at high throughput), the architecture would need to change to support batched inference and possibly GPU deployment. That's lower-priority future work because no current consumer requires sub-second extraction at high stream rates."*

**Q: "Could you make it faster?"**

> *"Yes, three ways. Batch inference (already supported) brings per-article cost to ~25 ms. A smaller model (DistilBERT or TinyBERT) would cut that further at some F1 cost. GPU deployment would reduce by another 5-10× on appropriate hardware. None of these are needed for the current consumer base; they remain available paths if a future deployment requires higher throughput."*

---

# Part 9 · UAT results — does the system actually work for analysts?

This is §6.10 of the thesis, the table on slide 34. It's the evidence for Contribution 5 and Gap 4.

## What was tested

Five participants used the deployed VioNER system to complete six end-to-end tasks:

| Task | What the participant did |
|:--|:--|
| 1 | Run inference on three supplied articles |
| 2 | Browse the event store with filters |
| 3 | Run an analytics query |
| 4 | Train a new model on a supplied dataset |
| 5 | Monitor a training run to completion |
| 6 | Review a flagged event |

After each task, participants rated their experience on a 5-point Likert scale (1 = strongly disagree, 5 = strongly agree) on six statements.

## Who the participants were

| Participant type | Count | Role in UAT |
|:--|:-:|:--|
| Early-warning analysts | 2 | Primary intended audience |
| Academic conflict researcher | 1 | Secondary audience |
| NLP developers unfamiliar with conflict domain | 2 | Fairness sanity check — would someone with technical literacy but no domain knowledge find it intuitive? |
| **Total** | **5** | |

## The completion result

**All 5 participants completed all 6 tasks.** This is the foundational UAT claim — the system is usable by the intended audience. If anyone had failed to complete a task, that would have been a usability red flag worth reporting.

## The Likert scores

Table 6.10 in the thesis:

| Statement | Mean | Std |
|:--|:--:|:--:|
| Extracted entities matched expectations | **4.4** | 0.5 |
| 5W1H structuring was clear | **4.6** | 0.5 |
| Confidence scores were useful for triage | 4.2 | 0.4 |
| KB enrichment added value | **4.6** | 0.5 |
| Training screen was easy to use | 4.0 | 0.7 |
| Analytics answered analyst-style questions | 4.2 | 0.4 |

### How to read Likert scores

- 5 = strongly agree
- 4 = agree
- 3 = neutral
- 2 = disagree
- 1 = strongly disagree

A mean of **4.0+** means *"on average, participants agreed or strongly agreed with the statement."* All six statements cleared 4.0.

The standard deviation column tells you how *consistent* the participants were. A small std (0.4-0.5) means participants mostly agreed with each other on the statement. A larger std (0.7+) means there was more spread. The "Training screen was easy" item had the largest spread (std = 0.7), suggesting one or two participants found it harder than others — which fed directly into future-work item *training UX improvements*.

### What this table proves

**The two highest items** — 5W1H structuring clarity (4.6) and KB enrichment value (4.6) — are exactly the two things this thesis claims as differentiating contributions. The fact that the analyst-facing scores are highest on the differentiating items means *the things the thesis says are valuable are the things the participants found valuable.* That's coherent evidence that the contribution claims match the operational experience.

**The lowest item** — "Training screen was easy" at 4.0 — became future work. The participants liked the live loss-curve update but wanted clearer hyperparameter explanations and dataset previews. These improvements are scoped into medium-priority future work in §7.5.

## A concrete walk-through

Participant 3 (an early-warning analyst with 6 years experience):

1. **Inference task**: pasted article into UI; got 5W1H chips back; spot-checked them against the article; identified one missing VICTIM entity (a passive-voice phrasing the model missed) and added it manually.
2. **Browsing task**: filtered events by country = SOM, date range = last 30 days; sorted by casualty count; exported CSV.
3. **Analytics task**: opened analytics dashboard; identified the actor responsible for the most attacks in the date range.
4. **Training task**: kicked off a training run with default hyperparameters; watched the loss curve update; observed the model converge at epoch 2.
5. **Monitoring task**: continued watching the training run while filling out the UAT survey for tasks 1-3.
6. **Review task**: filtered events by `geo_implausible` flag; re-read three flagged events; corrected one (mismatched actor extraction) and approved two as genuinely unusual events.

Total time to complete all 6 tasks: 47 minutes. Their Likert scores averaged 4.5. Their qualitative feedback: *"The inference screen is the obvious win. I'd want a PDF export from analytics before I'd recommend this to my team."* (PDF export is in future work.)

## What a panellist might ask

**Q: "n=5 is too small for statistical significance."**

> *"Correct — UAT scores at n=5 are descriptive, not inferential. The thesis doesn't claim statistical significance on the Likert means. What n=5 provides is qualitative usability validation. Nielsen's industry rule of thumb — five users find about 85% of usability issues — supports n=5 for the qualitative claim. The constructive feedback was internally consistent across participants: three of five asked for drag-and-drop file upload; three asked for per-entity training metrics. Internal consistency at this sample size is stronger evidence than mean Likert scores would be. A larger UAT with n=15-20 is appropriate before production deployment but was out of thesis scope."*

**Q: "What if all 5 participants had been domain experts? Wouldn't that bias the results?"**

> *"Yes — and that's why the composition was deliberately mixed. Two early-warning analysts (primary audience), one academic researcher (secondary), and two NLP developers who didn't know the conflict domain. The NLP developers serve as a fairness sanity check: would someone with technical literacy but no domain background find the interface intuitive? Their participation alongside domain experts is what makes the UAT useful — it validates both 'the system fits the workflow' and 'the system doesn't assume too much domain expertise'."*

---

# Part 10 · Error analysis — what does the model get wrong, and why

This is §6.11 of the thesis. Two important pieces: a confusion matrix and a list of error categories.

## The location confusion matrix (Table 6.11)

This table is on slide 30 of the deck.

| Gold \\ Predicted | CITY | REGION | DISTRICT |
|:--|--:|--:|--:|
| CITY | — | 0.05 | 0.04 |
| REGION | 0.08 | — | 0.06 |
| DISTRICT | 0.07 | 0.09 | — |

### How to read this matrix

The **rows** are what the gold label actually was. The **columns** are what the model predicted. The cells show what fraction of errors in each row went to each predicted column.

The **diagonal is omitted** because it represents correct predictions (gold = predicted = correct), not errors. We're studying only the errors here.

### Reading each row in plain English

**Row 1 — Gold = CITY**: When the true label was CITY, the model mistakenly predicted REGION 5% of the time and DISTRICT 4% of the time. That's a total of 9% confusion — 91% of CITY mentions were correctly predicted as CITY.

**Row 2 — Gold = REGION**: When the true label was REGION, the model mistakenly predicted CITY 8% and DISTRICT 6%. Total confusion 14% — 86% of REGION mentions were correctly identified.

**Row 3 — Gold = DISTRICT** *(the worst row)*: When the true label was DISTRICT, the model mistakenly predicted CITY 7% and REGION 9%. Total confusion 16% — only 84% of DISTRICT mentions were correctly identified. DISTRICT loses to both other location types simultaneously.

### What this table tells you operationally

**DISTRICT is the most confused location type.** When a place is named in an article, the model defaults to CITY for ambiguous cases (because CITY is more often right). DISTRICT-specific labels are harder to assign because many African districts share names with their main city or with their containing region.

The canonical example: **Goma**. Goma is a city in eastern DRC. It's also the de facto seat of North Kivu province (so people sometimes mean the region when they say "Goma"). It's also the centre of Goma territory (the district). The phrase *"fighting in Goma"* doesn't disambiguate which level.

The model defaults to CITY. The thesis acknowledges this and proposes a span-level CRF (Conditional Random Field) on top of the BERT representations as a future-work fix — the CRF can use sequence-level constraints to disambiguate similarly-named entities. This is high-priority future work item 4.

## The five error categories

Beyond the confusion matrix, the thesis analyses 300 validation events where the model made at least one mistake and categorises the errors:

| Category | % of all errors | What it looks like |
|:--|--:|:--|
| **Boundary mismatch** | **38%** | Right entity type, wrong span. "at least 12 civilians" tagged as "12 civilians" (qualifier dropped) |
| **Location type confusion** | **24%** | Wrong location type. DISTRICT predicted as CITY (the matrix above) |
| **Missed entities** | **19%** | Model didn't tag something that should have been tagged. Often passive-voice ACTION verbs ("were ambushed") |
| **Spurious entities** | **12%** | Model tagged something that shouldn't have been tagged. Most are DATE-class — "this morning", "earlier" tagged as DATE when they shouldn't be |
| **Confidence drops** | **7%** | Model predicted correctly but below the per-category confidence threshold, so the post-processor filtered it out |

## What each error category means for the analyst

**Boundary mismatch (38% — the biggest category)**: The model gets the entity type right but clips a word or two off the span. From the analyst's perspective, this is the **least costly** error — they see "12 civilians" tagged as CASUALTIES and immediately understand what was meant. They might need to edit the span to recover the qualifier ("at least") but the content is essentially there.

**Location confusion (24%)**: Already discussed above. The analyst sees a CITY tag where DISTRICT was correct. They correct the type but the location is right.

**Missed entities (19%)**: The model didn't tag something. From the analyst's perspective, this is **most costly per error** because they have to add the entity from scratch. Augmenting training data for passive-voice action verbs is the targeted fix.

**Spurious entities (12%)**: The model tagged something it shouldn't have. The analyst removes the tag. Vague temporal phrases ("this morning") are the most common case. The thesis discusses raising the WHEN confidence threshold to 0.85 to filter most of these at the cost of ~1.2 F1 on legitimate DATE recall — a tunable trade-off left to the operator.

**Confidence drops (7%)**: The model got it right but was less confident than the threshold required. The analyst sees a missed entity that the model "knew" about. Lowering the threshold would recover these at some precision cost.

## What the error analysis tells you about future improvements

Each error category points at a specific intervention:

- **Boundary mismatch (38%)** → high-priority future work item 4: span-level CRF for boundary refinement
- **Location confusion (24%)** → same item (CRF can disambiguate location types using sequence context)
- **Missed entities (19%)** → expand templates and real-news coverage of passive-voice and rare phrasings
- **Spurious entities (12%)** → tune per-category confidence thresholds (already configurable in the inference pipeline)
- **Confidence drops (7%)** → tune thresholds in the recall-favouring direction for use cases that prefer it

This is what makes error analysis useful: it's not just "the model fails sometimes". It's a structured diagnosis that maps each failure mode to a specific fix.

## What a panellist might ask

**Q: "Why is boundary mismatch your biggest error category? Can't you just train better?"**

> *"Boundary mismatch is the biggest single category but not the most damaging — the analyst sees the right entity type with a slightly clipped span, which is operationally close to correct. The structural cause is that NER models trained with token-level loss don't have sequence-level boundary constraints. A span-level CRF or biaffine head on top of the BERT representations would address this by introducing sequence-level decoding. This is high-priority future work item 4 in section 7.5. Doing it well requires a separate training-time change, which is why it's deferred."*

**Q: "Why doesn't the model just learn to handle passive voice?"**

> *"Two reasons. First, passive-voice action verbs are systematically under-represented in ACLED notes — the source corpus skews to active-voice reporting. Second, even with augmentation, passive-voice phrasings are highly variable. The augmentation templates cover some but not all. Real-news expansion (limitation 2) would help here because real news has more passive-voice variety than ACLED notes do. The thesis is honest about this trade-off in section 6.13."*

---

# Part 11 · How each experimental result supports each contribution claim

This is the bridge between Chapter 6 and the thesis's contribution claims (Chapter 7). The format: contribution claim ← supporting evidence ← source.

| Contribution claim | Evidence in Chapter 6 | Specific source |
|:--|:--|:--|
| **C1** — The 8-entity grounding-validated schema produces consistent supervision | Cohen's κ = 0.78 on the 200-doc pilot | §5.2 / §6 dataset discussion |
| **C2** — The 4-level taxonomy is operationally usable | UAT participants successfully completed taxonomy-related tasks; analytics dashboard uses Level-1 aggregation | §6.10 + the analytics walk-through |
| **C3** — Focal loss + class weights lifts rare-entity F1 | Ablation table 6.8: VICTIM +11 F1, ACTION +7 F1, no entity hurt | §6.6, slide 29 |
| **C4** — Curated KB delivers measurable operational value | 2.4% flag rate + 64.3% enrichment rate + UAT Likert 4.6 on "KB enrichment added value" | §6.7 + §6.10 |
| **C5** — Deployable platform is operable by non-ML users | All 5 UAT participants completed all 6 end-to-end tasks; Likert ≥ 4.0 on every item | §6.10 |

## Using this table on defense day

When a panellist asks *"what's your evidence for contribution X?"* — point at the row for X. Each row has both *what the evidence is* and *where in the thesis it lives*.

When a panellist asks *"how do the experimental results justify the contributions?"* — read them this table top to bottom. Five contributions, five distinct sources of evidence, all empirical.

---

# Part 12 · Defending the experimental results in Q&A

Likely panel questions about Chapter 6's numbers — with prepared answers.

### Q · "Walk me through your most important result."

**Bottom line.** Table 6.8 — the focal-loss ablation. VICTIM F1 moves from 0.708 under plain cross-entropy to 0.817 under focal + class weights, a gain of 11 F1 points, on the held-out validation set.

**Detail.** Four training configurations under identical conditions. The combination of focal loss with inverse-frequency class weights beats every alternative on the rare entities — VICTIM, ACTION, CASUALTIES — without hurting common entities. Each ingredient alone gives partial credit (+7, +8 respectively on VICTIM); the combination gives +11. This is the empirical answer to RQ2 (modelling under severe class imbalance) and the basis for Contribution 3.

### Q · "How do you know the F1 numbers aren't inflated by overfitting?"

**Bottom line.** All F1 numbers reported are on a held-out 10,000-example validation set the model never sees during training.

**Detail.** The 80/20 split is at the article level with hash-based deduplication before splitting. Augmentation template pools are partitioned between train and validation. The validation loss curve in Table 6.5 also confirms no overfitting at the reported checkpoint — val loss is at its minimum at epoch 2 (the chosen checkpoint) and rises in epochs 3+. If the model were overfit, val loss would already be rising before the chosen epoch. Section 6.13 discusses residual leakage risks honestly.

### Q · "Is your headline F1 number (0.909 micro) good or just average?"

**Bottom line.** Strong for a domain-specific NER task with severe class imbalance.

**Detail.** Comparable English-language NER tasks: CoNLL-2003 reports around 0.92 micro F1 on a 4-entity general-news task with mild imbalance. VioNER reports 0.91 micro on an 8-entity violent-event task with severe imbalance — competitive with the established benchmark and on a harder distribution. Backup B9 of the slides shows VioNER outperforming generic BERT NER models on the entity-tag overlap (0.94 vs 0.82 macro F1 for the four shared entity types).

### Q · "Why didn't you compare against ACLED quality directly?"

**Bottom line.** ACLED is hand-coded — there's no comparable F1 metric to compute against it.

**Detail.** ACLED's records are the gold standard for African violent-event data. You can't compute F1 of ACLED's coders against themselves — they ARE the ground truth in the broader literature. The defensible comparison is against other automated extraction systems on the same task. Backup B9 reports this comparison.

### Q · "The UAT only had 5 participants. Can you draw conclusions from that?"

**Bottom line.** Qualitatively yes; inferentially no. The thesis is explicit about this in §6.10.

**Detail.** Nielsen's industry rule of thumb is that 5 users find about 85% of usability issues. That supports the qualitative validation. For inferential statistics on the Likert means, n=5 is too small — and the thesis doesn't claim that level of inference. What the thesis does claim is that the system is operable by non-ML users (foundational claim, supported by all 5 completing all 6 tasks) and that participants find the differentiating features valuable (supported by Likert scores of 4.6 on the two key items). A larger UAT before production is appropriate but was out of thesis scope.

### Q · "Why does precision exceed recall on every row of Table 6.7?"

**Bottom line.** Standard NER behaviour. When the model is uncertain, it defaults to O — the safe choice. Fewer false positives, more false negatives.

**Detail.** This pattern is operationally desirable for an analyst-review workflow. Higher precision means fewer false alarms — less time spent rejecting bad model predictions. Higher recall would mean fewer missed entities but more false alarms. The trade-off is configurable per category via confidence thresholds in section 4.7; for the production thresholds reported in the thesis, the model leans precision-favourable.

### Q · "What about reproducibility — can someone else recompute these numbers?"

**Bottom line.** Yes. The thesis reports hyperparameters (backup B1), random seeds (42, 17, 91), and training data construction (§5.3) in enough detail for reproduction.

**Detail.** Run-to-run variance across the three seeds is approximately ±0.4 percentage points on macro F1. All reported gains in the ablation exceed this variance by an order of magnitude. The repository contains the training code, the inference pipeline, and the Docker Compose configuration. Anyone with the repo and the ACLED open-data export should be able to reproduce the headline numbers to within ±0.4 F1.

### Q · "What if your validation set is too easy?"

**Bottom line.** It's drawn from the same combined corpus as the training data, which makes it an estimate of in-distribution performance, not out-of-distribution.

**Detail.** This is honest scope-limitation 2 of the thesis. 30% of the corpus is template-augmented; the validation set draws from the same combined distribution. So the F1 numbers are a fair estimate of how the model performs on data that looks like ACLED notes plus template augmentation, but they don't guarantee out-of-distribution performance on, say, citizen-journalism reporting or translated articles. Future-work item 3 — annotated real-news expansion — exists specifically to measure where this estimate breaks. Section 6.13 discusses this as a construct-validity threat.

### Q · "What's the single most important table in Chapter 6?"

**Bottom line.** Table 6.8, the focal-loss ablation. Without it, the loss-function contribution would be assertion rather than evidence.

**Detail.** Table 6.7 (per-entity F1) tells you what the production system delivers. Table 6.8 tells you why the design choice was correct. Section 6.6 contains both the ablation and the discussion of complementarity (focal loss + class weights are not redundant). If only one table from Chapter 6 had to make it into a paper, it would be Table 6.8.

---

# Appendix · Quick reference — what every number on every slide means

When you're rehearsing and a number flashes by, here's the cheat sheet.

| Number | Where it appears | What it means |
|:--|:--|:--|
| **0.909** | Slide 27, headline | Micro F1 on validation set across 190,075 spans |
| **0.887** | Slide 27, caption | Macro F1 — average per-entity F1 |
| **96.7%** | Slide 27, caption | Token accuracy — least informative because 78% is O |
| **190,075** | Slide 27, caption | Total gold spans in validation set across all 8 entities |
| **0.956** | Slide 28, DATE row | DATE F1 — strongest entity |
| **0.817** | Slide 28, VICTIM row | VICTIM F1 — weakest entity |
| **0.708** | Slide 29, plain CE column | VICTIM F1 with the baseline loss |
| **+0.109** | Slide 29 highlight | VICTIM gain from focal + weights vs plain CE |
| **+0.072** | Slide 29 highlight | ACTION gain from focal + weights vs plain CE |
| **0.08** | Slide 30 confusion matrix | Fraction of REGION errors that get tagged as CITY |
| **0.09** | Slide 30 confusion matrix | Fraction of DISTRICT errors that get tagged as REGION (the worst confusion) |
| **2.4%** | Slide 22 KB row | KB geographic-implausibility flag rate |
| **64.3%** | Slide 22 KB row | KB ACTOR enrichment rate |
| **150 ms** | Slide 20 process flow | End-to-end inference latency on CPU |
| **n=5** | Slide 34 UAT | Number of UAT participants |
| **6** | Slide 34 UAT | Number of tasks completed |
| **4.6** | Slide 34 highest items | Likert mean on "5W1H structuring was clear" and "KB enrichment added value" |
| **4.0** | Slide 34 lowest item | Likert mean on "Training screen was easy" — drove future-work |
| **2** | Backup B2 | Epoch at which the best checkpoint converges |
| **0.0074** | Backup B2 | Validation loss at epoch 2 (the minimum) |
| **κ = 0.78** | Slide 24 quality column | Cohen's kappa inter-annotator agreement on the 200-doc pilot |
| **0.78 → 0.22** | Slide 24 quality column | Disagreement reduction across 6 pilot iterations |
| **3.2% → ~1%** | Slide 24 quality column | Spot-check error rate before/after correction |
| **22 k / 12 k / 50 k** | Slide 24 volume table | CoNLL-2003 / MIT Movie NER / VioNER corpus sizes |

---

# One last calibration note

Every number in this document is on the validation set. Every comparison in this document is between configurations that differ in exactly one variable. Every operational metric (flag rate, enrichment rate) is measured on real extracted output. The UAT was conducted on a deployed system with real participants completing real tasks.

In other words: **the experimental results are honest, controlled, measured, and reproducible**. When you defend them in the room, you're defending evidence, not assertion. The numbers were what they were — and the contribution claims align with what the numbers show.

Speak with the calm authority of someone who measured the thing and reports honestly. The data supports the claims. Trust that, and answer accordingly.
