# VioNER Defense — Formulas Explained

This document walks through **every formula** that appears in the thesis and the defense slides. Each section follows the same shape:

1. **The formula** — written cleanly in LaTeX.
2. **Plain English** — what it computes, in everyday language.
3. **Symbol breakdown** — what each letter means.
4. **Worked numeric example** — concrete numbers so the math is visible.
5. **Where in the thesis / where in the slides** — exact cross-references.
6. **Why it was required** — the problem it solves.
7. **Likely panel questions** — with one-line answers.

Read top to bottom once. Then keep this document next to `qa_kit.md` for defense day — if a panellist asks "what does that formula mean", flip here.

---

# Prerequisite: BIO tags — what the model actually predicts

Before any formula makes sense, you need to remember what the model's *output* is. BERT's classification head produces a label for every token in the input. The labels come from a fixed set of **17 BIO tags** defined by this thesis. The "$C = 17$ classes" you'll see in every formula refers to these 17 labels — not to anything else.

## What B, I, O each stand for

| Tag prefix | Meaning |
|:-:|:--|
| **B-** | **Beginning** of an entity. The first token of an entity span. |
| **I-** | **Inside** an entity. A continuation token within the same span as the preceding B- or I-. |
| **O** | **Outside** any entity. A token that is not part of any entity at all. |

This is the standard sequence-labelling encoding from CoNLL-2000 / 2003: every token gets exactly one tag, and a multi-token entity is encoded as B-Type followed by one or more I-Type tags of the same Type.

> **Why this scheme rather than alternatives?** BIO uses $2k + 1$ labels for $k$ entity types — minimum needed to express both span starts and continuations. BIOES (Begin / Inside / Outside / End / Single) would use $4k + 1$ but adds redundant End and Single tags. The thesis chose BIO because African news rarely has adjacent same-type entities with no intervening token; the extra BIOES labels wouldn't earn their place. *(See defense slide 18.)*

## The 8 entity types VioNER tags

The thesis settled on 8 grounded entity types after the November 2025 schema-pruning pilot (§4.3 of the thesis). Each entity contributes a B- and an I- form, plus the shared O label — $8 \times 2 + 1 = \mathbf{17}$ BIO labels in total.

| 5W1H slot | Entity type | What it tags | Example span |
|:--|:--|:--|:--|
| **WHO** | **ACTOR** | The perpetrator — group or individual responsible for the action | "Al-Shabaab fighters" |
| **WHO** | **VICTIM** | Those harmed or targeted — civilians, soldiers, communities | "twelve civilians" |
| **WHAT** | **ACTION** | The act of violence itself | "attacked", "ambushed" |
| **WHEN** | **DATE** | Time expressions | "on Tuesday", "January 15" |
| **WHERE** | **REGION** | Administrative region or province | "North Kivu province" |
| **WHERE** | **CITY** | Named city or town | "Mogadishu", "Goma" |
| **WHERE** | **DISTRICT** | Administrative subdivision below region | "Beni territory" |
| **HOW** | **CASUALTIES** | Killed-or-injured counts and their qualifiers | "at least 12 killed" |

The **WHY** slot — motive, trigger — is intentionally **not** in this list. Those types were dropped from the supervised schema because their grounding rate fell below 80 % in the November pilot: annotators were *inferring* motive from context rather than reading it off the page, which would have introduced systematic label noise. *(See defense slide 16.)*

## The 17 BIO labels in full

This is the complete label set the model picks from at every token position:

| # | Label | What it marks |
|:-:|:--|:--|
| 1 | **O** | Outside any entity — punctuation, prepositions, generic NPs, etc. |
| 2 | B-ACTOR | First token of a perpetrator mention |
| 3 | I-ACTOR | Continuation of a perpetrator mention |
| 4 | B-VICTIM | First token of a victim mention |
| 5 | I-VICTIM | Continuation of a victim mention |
| 6 | B-ACTION | First token of an action verb phrase |
| 7 | I-ACTION | Continuation of an action verb phrase |
| 8 | B-DATE | First token of a date expression |
| 9 | I-DATE | Continuation of a date expression |
| 10 | B-REGION | First token of a region name |
| 11 | I-REGION | Continuation of a region name |
| 12 | B-CITY | First token of a city name |
| 13 | I-CITY | Continuation of a city name |
| 14 | B-DISTRICT | First token of a district name |
| 15 | I-DISTRICT | Continuation of a district name |
| 16 | B-CASUALTIES | First token of a casualty count |
| 17 | I-CASUALTIES | Continuation of a casualty count |

When you read **"17 classes"**, **"$C = 17$"**, or **"class $c$"** in any formula below, this is the list. Every per-token softmax distribution is over these 17 outcomes.

## Worked example: one sentence, tagged

Take the canonical sentence from slide 7:

> *"On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least 12 soldiers."*

Token-by-token BIO labels (gold annotation):

| # | Token | Label | Why this label |
|:-:|:--|:--|:--|
| 1 | On | O | Preposition, outside any entity |
| 2 | Tuesday | B-DATE | First and only token of the DATE span |
| 3 | , | O | Punctuation |
| 4 | fighters | O | Generic noun — does not name an actor |
| 5 | from | O | Preposition |
| 6 | Al | B-ACTOR | First token of the ACTOR span "Al-Shabaab" |
| 7 | - | I-ACTOR | Continuation across the hyphen |
| 8 | Shabaab | I-ACTOR | Continuation of the ACTOR span |
| 9 | attacked | B-ACTION | First and only token of the ACTION span |
| 10 | a | O | Article |
| 11 | military | B-VICTIM | First token of the VICTIM span "military convoy" |
| 12 | convoy | I-VICTIM | Continuation of the VICTIM span |
| 13 | near | O | Preposition |
| 14 | Mogadishu | B-CITY | First and only token of the CITY span |
| 15 | , | O | Punctuation |
| 16 | killing | O | Secondary action verb — primary ACTION already tagged |
| 17 | at | B-CASUALTIES | First token of the CASUALTIES span "at least 12 soldiers" |
| 18 | least | I-CASUALTIES | Continuation |
| 19 | 12 | I-CASUALTIES | Continuation |
| 20 | soldiers | I-CASUALTIES | Continuation |
| 21 | . | O | Final punctuation |

Out of 21 tokens, **11 are O** (≈ 52 %) and 10 carry one of the 16 B/I entity labels. In the **full** training corpus the O fraction is higher — about **78 %** — because most sentences mix one or two short entities with many connective and stop words. That 78 % O figure is exactly the class-imbalance problem the focal-loss formulas address.

## How BIO encoding plumbs into the formulas below

This is the bridge between the BIO primer and the rest of the document:

- Every formula that mentions **"class $c$"** iterates over these 17 labels.
- The model's softmax output (**§1** below) is a probability distribution over these 17 labels per token.
- The inverse-frequency class weight $\alpha_c$ (**§3** below) is one weight per label — so **17 weights in total**, computed once at the start of training.
- Span-level precision / recall / F1 (**§7** below) first regroups adjacent B-Type / I-Type runs back into spans before scoring. So the underlying granularity is the BIO label, but the *reported* numbers are per-entity-type — 8 per-entity F1 scores plus a macro average, not 17.
- The "O dominates" claim throughout the formulas refers to label #1 in the table above.
- The "rare classes" the focal loss is designed to protect — VICTIM, ACTION, CASUALTIES — are labels #4–5, #6–7, and #16–17 respectively.

With those 17 labels and their B/I/O semantics fresh, the formulas in the rest of this document should read cleanly.

---

## At-a-glance map

| # | Formula | One-line purpose | Thesis | Slides |
|:-:|:--|:--|:--|:--|
| 1 | **Softmax** | Turns model outputs into class probabilities | §2.3 (background) | Slide 20 step 3 |
| 2 | **Cross-entropy loss** $\mathcal{L}_{\text{CE}}$ | Standard loss for classification — the *baseline* this thesis improves on | §2.4, §6.6 ablation | Slide 21, 29 |
| 3 | **Inverse-frequency class weights** $\alpha_c$ — **Eq. (4)** | Bigger weight on rare classes so they aren't drowned out | §2.4 (Eq. 4) | Slide 21 |
| 4 | **Focal loss** $\text{FL}$ — **Eq. (1)** | Down-weights easy correct examples; focuses on hard ones | §2.4 (Eq. 1), §5.5 | Slide 21 (headline equation) |
| 5 | **Label-smoothing target** $y'_c$ — **Eq. (3)** | Replaces one-hot labels with softened targets for regularisation | §2.4 (Eq. 3) | Backup B1 |
| 6 | **Focal loss + smoothing** $\text{FL}_{\text{LS}}$ — **Eq. (2)** | The production loss: focal + class weights + smoothing | §2.4 (Eq. 2), §5.5 | Slide 21 |
| 7 | **Precision, Recall, F1** | The three NER evaluation numbers per entity | §2.5 | Slides 27, 28 |
| 8 | **Macro F1 vs Micro F1** | Two ways to average F1 across entity types | §2.5 | Slides 27, 28 |
| 9 | **Token accuracy** | The simple metric; reported but warned against | §2.5 | Slide 27 caption |
| 10 | **Cohen's κ** | Inter-annotator agreement, corrected for chance | §5.2 (annotation) | Slide 24 (data quality) |

Below, in the order most useful for defense: model output → loss family → metrics → agreement.

---

# Part A · The loss family (training-time math)

Before any formula in this part makes sense, you need a mental picture of what *"training a model"* even means. Let's build it from scratch — assume nothing.

## What is a neural network, in one sentence?

A neural network is **a mathematical function with millions of adjustable dials**. You give it an input — a sentence, an image, a number — and it produces an output. The dials are called **weights** (or **parameters**). The BERT model used in this thesis (`bert-base-cased`) has **110 million** of them. Initially they're set to random values, so the model's output is also random. The whole job of "training" is to turn those dials so the output starts to be useful.

## What is "training" a model? — A student-studying analogy

Imagine you're a student preparing for a math exam.

1. You pick a **practice problem** from a textbook.
2. You write down **your answer**.
3. You **look up the correct answer** in the back of the book.
4. If you got it wrong, you **study** the relevant chapter and try to adjust *how you'd think about that kind of problem* next time.
5. You take the next practice problem. **Repeat hundreds of times.**

That's exactly how a neural network learns. Substituting the technical terms:

| Student step | What happens in BERT training |
|:--|:--|
| 1. Pick a practice problem | The pipeline draws one **training example** — for VioNER, that's one tokenised sentence. |
| 2. Write down your answer | BERT does a **forward pass** and predicts a BIO label for every token. |
| 3. Look up the correct answer | The pipeline compares predictions to the **gold labels** (the human-annotated truth). |
| 4. Study and adjust | The pipeline **nudges the weights** in the direction that would have made the prediction less wrong. |
| 5. Repeat | The pipeline iterates across **50,000 examples**, **2 epochs** (passes through the data). |

After enough nudges, the weights converge to a configuration where the model's predictions are close to the gold labels on the training data — and, hopefully, on data the model has never seen.

## What is a loss function?

The **loss function** is the formula that turns *"how wrong was that prediction"* into a single number. The bigger the number, the more wrong the prediction.

Carry on with the student analogy. When you grade your practice test, you write a score at the top — say "7 out of 10". A higher exam score means you did better; the loss is essentially the inverse — *higher loss means worse*. Specifically:

- **High loss** on a token = "the model was very wrong here → nudge the weights *hard*."
- **Low loss** on a token = "the model was about right → nudge a little."
- **Zero loss** = "perfect prediction → don't change anything."

The loss is computed for **every token in every training example**. The training pipeline averages losses across the batch, then uses that average to decide *how much* to nudge each weight.

> **Every formula in Part A is some variant of this loss function.** The story of this thesis, in one sentence, is *which loss function — out of plain cross-entropy, class-weighted cross-entropy, focal loss, or focal-loss-plus-class-weights — makes the model get the rare-entity classes right.*

## What does "minimising the loss" mean? — A hiker-on-a-mountain analogy

Think of the loss as the **altitude of a hiker** on a vast mountainous landscape. Each point on that landscape corresponds to one possible configuration of all 110 million model weights. The hiker's job is to **walk to the lowest valley** — the configuration where the loss is smallest.

The hiker can only see one step in each direction at a time. To know which way is "downhill", the pipeline computes a **gradient** — a vector that says *"for each weight, twisting it slightly this way decreases the loss by this much."* The hiker then takes a small step in the downhill direction, recomputes, and repeats.

That algorithm is called **gradient descent**. The specific optimiser used in this thesis — **AdamW** — is a refined version that adapts the step size per weight based on the history of gradients. The key point for understanding the formulas below: every formula in Part A produces a single number whose **gradient** is what nudges the weights.

## How the formulas in this part fit together

To compute the loss for one token, the pipeline runs through this chain:

```
1.  BERT forward pass          →  17 raw scores (one per BIO label) per token
2.  Softmax (§1)               →  17 probabilities per token (sum to 1)
3.  Loss function (§2 onward)  →  a single non-negative number per token
4.  Backpropagation            →  gradient computed automatically (PyTorch handles this)
5.  Optimiser step             →  weights nudged in the gradient direction
```

Each section below explains one piece of this chain. **Read them in order** — softmax produces what the loss eats, and each subsequent loss variant builds on the previous one. By the end of §6 you'll be able to read the focal-loss formula on slide 21 and know exactly what every symbol does.

---

## 1. Softmax — turning model outputs into probabilities

### Why we need this at all

At the end of its forward pass, BERT produces **17 raw numbers per token** — one per BIO label. These raw numbers are called **logits**. They can be anything: positive, negative, large, small. A logit of $+4$ for the O label means *"I lean strongly towards O"*. A logit of $-3$ for B-VICTIM means *"I lean away from B-VICTIM"*. A logit of $0$ is neutral.

#### What "17 numbers per token" means concretely

Take the canonical sentence from the BIO primer:

> *"On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least 12 soldiers."*

After tokenisation that's 21 tokens. The crucial fact: **for each one of those 21 tokens, BERT outputs a vector of 17 numbers — not 17 numbers total for the sentence, but 17 numbers per token.** So BERT's full output for this sentence is a grid of $21 \times 17 = 357$ raw numbers.

Why 17? Because there are 17 BIO labels (the list from the primer). **For every token, the model has to rank all 17 possible labels** — assigning each one a numeric score that says *"how strongly do I lean toward this being the right label here"*.

#### A worked example for one token

Pick a single token from the sentence: **"Mogadishu"**. The gold label is B-CITY. BERT produces a 17-number vector for it. Imagine the numbers come out as follows (illustrative — the actual numbers depend on the trained weights, but they look qualitatively like this):

| Position | Label | Logit |
|:--:|:--|--:|
| 1 | O | -2.1 |
| 2 | B-ACTOR | -1.5 |
| 3 | I-ACTOR | -3.2 |
| 4 | B-VICTIM | -1.8 |
| 5 | I-VICTIM | -3.5 |
| 6 | B-ACTION | -2.7 |
| 7 | I-ACTION | -3.8 |
| 8 | B-DATE | -1.2 |
| 9 | I-DATE | -3.0 |
| 10 | B-REGION | **+1.4** |
| 11 | I-REGION | -2.5 |
| 12 | **B-CITY** | **+4.2** ← highest |
| 13 | I-CITY | +0.3 |
| 14 | B-DISTRICT | +0.8 |
| 15 | I-DISTRICT | -2.0 |
| 16 | B-CASUALTIES | -3.4 |
| 17 | I-CASUALTIES | -4.1 |

Read each line as the model's "vote strength" for one label:

- **B-CITY scored +4.2** → *"I lean strongly toward this token being B-CITY."*
- **B-REGION scored +1.4** → *"I also see some signal that it could be B-REGION — regions and cities share name patterns."*
- **B-DISTRICT scored +0.8** → *"Mild lean toward B-DISTRICT."*
- **O scored −2.1** → *"I lean against this being a non-entity."*
- **I-CASUALTIES scored −4.1** → *"Strongly against this being a casualty continuation."*

The model's *prediction* is the label with the highest score: **B-CITY** here. But it didn't just pick one — it produced all 17 because we need the *graded* view for the next steps.

#### Why output all 17 and not just the winner?

Three reasons:

1. **Softmax needs all 17.** To convert these logits into probabilities, the softmax formula (below) needs the full distribution. You cannot compute "probability of B-CITY" without knowing how strong every alternative looked.
2. **Loss needs all 17.** Cross-entropy loss (§2) uses the probability of the *true* class. To get that probability you have to normalise across all 17 alternatives — so all 17 are required upstream.
3. **Confidence matters operationally.** The dominance of the winning logit (here 4.2 vs the runner-up 1.4) becomes the **confidence score** the analyst sees next to each entity in the UI. If B-CITY had only narrowly beaten B-REGION, the model would be genuinely uncertain — and the analyst should re-read the article. (This is how the per-category confidence threshold in §4.7 of the thesis works.)

#### The full structure for the whole sentence

For our 21-token example, BERT's complete classification output is a **21 × 17 grid** of raw numbers. Each row is one token; each column is one BIO label. Position $(i, j)$ holds the logit for "token $i$ is label $j$".

In PyTorch code this is literally a tensor of shape `[sequence_length, num_labels]` = `[21, 17]` for this sentence. Larger sentences get bigger first dimensions; the 17 never changes.

After softmax (next step), every row becomes a probability distribution that sums to 1, and the highest-probability label in each row is the model's prediction for that token.

#### So what's the actual problem softmax solves?

The 17 raw numbers don't look like a probability distribution. We can't say *"the model is 84 % sure this token is O"* by reading a logit of $+4$ directly — $+4$ could be high or low depending on what the other 16 logits are. We need to convert the 17 logits into **17 percentages that sum to 100 %**, accounting for the relative strengths. That conversion is what softmax does, described next.

### The intuitive recipe

Softmax does three things in order:

1. **Exponentiate** each logit. The function $e^x$ turns any real number into a positive number. Positive logits become large positives ($e^4 = 54.6$); negative logits become small positives ($e^{-3} = 0.05$). This step also amplifies differences: a logit of 5 becomes 148 while a logit of 2 becomes 7, so a clearly-winning logit ends up overwhelmingly larger than its competitors.
2. **Sum** all 17 exponentials to get a total.
3. **Divide** each exponentiated logit by that total. Each result lands between 0 and 1, and the 17 results sum to exactly 1.

That's it. The "soft" in *softmax* is the contrast with *argmax* — argmax just picks the largest logit and gives it 100 %, ignoring the others. Softmax keeps a **graded distribution**: even the runners-up get some probability mass.

### Analogy: 17 judges scoring a contestant

Imagine a panel of 17 judges each writing a score from $-10$ to $+10$ for a single contestant. The raw scores aren't directly comparable (some judges are tougher). Softmax is the normalisation procedure that converts the 17 raw scores into 17 percentages that sum to 100 % — a **share of belief** in each judge's opinion. The highest-scoring judge gets the biggest share but the others still contribute something.

### The formula

For one token, BERT produces a vector of $C = 17$ raw scores (one per BIO label) called **logits**, written $z_1, z_2, \dots, z_C$. Softmax converts them into probabilities that sum to 1:

$$\hat{y}_c \;=\; \text{softmax}(z_c) \;=\; \frac{e^{z_c}}{\displaystyle\sum_{k=1}^{C} e^{z_k}}$$

### Plain English

> *"For each token, the model has 17 raw scores — one for each possible label. Softmax converts them into a probability distribution. The class with the largest score becomes the most probable, but all 17 still get a positive probability that sums to 1."*

### Symbol breakdown

| Symbol | Meaning |
|:-:|:--|
| $z_c$ | Raw model output (logit) for class $c$. Can be any real number — positive, negative, large, small. |
| $e^{z_c}$ | The exponential function — turns logits into positive numbers. |
| $\sum_k e^{z_k}$ | Sum of all exponentiated logits — used as a normaliser so the result sums to 1. |
| $\hat{y}_c$ | Predicted probability of class $c$ — between 0 and 1. |
| $C$ | Total number of classes. Here $C = 17$ (B-ACTOR, I-ACTOR, B-VICTIM, …, O). |

### Worked numeric example

Suppose for a single token BERT produces three logits (we'll pretend only 3 classes exist for clarity):

| Class | Logit $z_c$ | $e^{z_c}$ |
|:--|--:|--:|
| O | 4.0 | 54.6 |
| B-VICTIM | 2.0 | 7.4 |
| B-ACTOR | 1.0 | 2.7 |
| **Sum** |  | **64.7** |

Softmax:

- $\hat{y}_{\text{O}} = 54.6 / 64.7 = 0.844$
- $\hat{y}_{\text{B-VICTIM}} = 7.4 / 64.7 = 0.114$
- $\hat{y}_{\text{B-ACTOR}} = 2.7 / 64.7 = 0.042$

These three sum to 1.000. The model is 84.4 % confident the token is O.

### Where in the thesis / slides

- Thesis §2.3 (background on transformer models)
- Defense slide 20, step 3 ("forward pass returns per-token softmax distributions over 17 labels")

### Why it was required

Every subsequent formula — cross-entropy, focal loss, confidence filtering — needs probabilities, not raw scores. Softmax is the bridge between the model's internal representation and the rest of the pipeline.

### Likely panel questions

- **"Why softmax and not sigmoid?"** — *"Softmax gives a single distribution over mutually exclusive classes; sigmoid would let each class be true independently. BIO labels are mutually exclusive — a token is exactly one label."*
- **"What is the temperature here?"** — *"Temperature = 1.0; standard softmax. Lower temperature would sharpen the distribution; higher would flatten it. We use the unmodified version."*

---

## 2. Cross-entropy loss — the baseline

### Why we need a loss at all

After softmax (§1), the model gives us 17 probabilities for one token. The gold label says exactly one of those 17 labels is the right one. We need to convert *"how close were the predicted probabilities to the truth"* into a single number — the loss. **Cross-entropy** is the standard answer to that question for classification problems.

### A 30-second refresher on logarithms

The **logarithm** of a number $x$ (natural log, written $\log x$ or $\ln x$) is the answer to *"what power do I have to raise $e \approx 2.718$ to, to get $x$?"*. You don't need to compute logs by hand — just remember the qualitative behaviour:

| $x$ | $\log x$ | Reading |
|--:|--:|:--|
| 1.0 | 0.000 | $\log$ of 1 is zero |
| 0.5 | -0.693 | $\log$ of "half" is moderately negative |
| 0.1 | -2.302 | $\log$ of "one-tenth" is quite negative |
| 0.01 | -4.605 | $\log$ of "one in a hundred" is very negative |
| 0.001 | -6.907 | And it keeps getting worse as $x$ shrinks |

Two facts to remember:

1. $\log(1) = 0$ — perfect score means zero on the log scale.
2. $\log$ of small numbers is very negative, and gets unboundedly more negative as the number approaches zero.

That second property is exactly what we want for loss: assigning a tiny probability to the true class should produce a *huge* penalty.

### Why "minus log" specifically?

Take the model's predicted probability for the **true** class, $p_y$. (For the example token whose gold label is O, $p_y$ is the model's probability for O.)

- If $p_y = 1.0$, the model was perfect. $-\log(1.0) = 0$. **Zero loss.** Good.
- If $p_y = 0.5$, the model was uncertain. $-\log(0.5) = 0.693$. **Modest loss.**
- If $p_y = 0.01$, the model was confidently wrong. $-\log(0.01) = 4.605$. **Big loss.**
- If $p_y = 0.001$, the model was catastrophically wrong. $-\log(0.001) = 6.907$. **Huge loss.**

The "minus log" formula is **the standard loss for classification** because it has exactly the property we want: zero penalty for confident-correct, growing penalty for confident-wrong, and the penalty grows asymptotically without bound as the model's confidence in the wrong direction gets worse.

### Analogy: "surprise"

Cross-entropy is sometimes called the **surprise** of the model. The intuition:

- If the model predicted O with probability 0.99 and the gold says O, the model is *"barely surprised"* — it called it. Loss is small (0.01).
- If the model predicted O with probability 0.01 and the gold says O, the model is *"extremely surprised"* — it didn't see this coming at all. Loss is large (4.6).

The loss literally measures how unprepared the model was for the true answer. The optimiser then nudges the weights to reduce future surprise on similar tokens.

### The formula

For a single token whose true class is $y$, cross-entropy loss is:

$$\mathcal{L}_{\text{CE}}(p, y) \;=\; -\log p_y$$

where $p_y = \hat{y}_y$ is the model's predicted probability for the true class.

### Plain English

> *"If the model gave high probability to the right answer, the loss is small. If it gave low probability, the loss is large. The minus-log function rewards confidence and punishes uncertainty."*

### Symbol breakdown

| Symbol | Meaning |
|:-:|:--|
| $p_y$ | Probability the model assigned to the **true** class (the one the gold label says). |
| $\log p_y$ | Natural logarithm of that probability. Always ≤ 0 because $p_y \in [0, 1]$. |
| $-\log p_y$ | The minus sign flips it to non-negative, so loss = 0 when $p_y = 1$ (perfect) and loss → ∞ when $p_y \to 0$. |

### Worked numeric example

| True label | Model's $p_y$ | $\mathcal{L}_{\text{CE}} = -\log p_y$ |
|:--|--:|--:|
| O (correct, confident) | 0.99 | 0.010 |
| O (correct, uncertain) | 0.60 | 0.511 |
| B-VICTIM (wrong, model said O) | 0.05 | 2.996 |

Notice how a wrong-answer token (last row) contributes ~300× more loss than a confidently-correct one (first row).

### Where in the thesis / slides

- Thesis §2.4 (defined inline near Eq. (1))
- Thesis §6.6 (the ablation that compares cross-entropy against focal loss)
- Defense slide 21 (mentioned as the "plain CE" baseline)
- Defense slide 29 (the ablation table — first column)

### Why it was required (and then dropped as the production loss)

Cross-entropy is the default classification loss. It works fine when classes are balanced. **But on VioNER's data 78 % of tokens are class O.** Almost all of those O tokens are *easy* for the model — it gets them right with high confidence. Each easy correct O contributes a tiny loss (≈ 0.01), but there are so many of them that they collectively dominate the total. The gradient signal for the rare entities — VICTIM, ACTION, CASUALTIES — gets drowned out.

The thesis reports the cross-entropy baseline because the contribution claim is that **focal loss + class weights beats cross-entropy by 11 F1 on VICTIM**. The baseline number — VICTIM F1 = 0.708 under plain cross-entropy — is what makes the +11 F1 gain quantifiable.

### Likely panel questions

- **"Why not just use cross-entropy?"** — *"Because 78 % of tokens are O. Plain cross-entropy gives equal per-token weight to O tokens and rare-class tokens, and the rare classes (VICTIM, ACTION, CASUALTIES) get drowned out. Section 6.6 of the thesis quantifies this — under plain CE, VICTIM F1 is 0.708; under focal loss with class weights it's 0.817, a gain of 11 F1 points."*

---

## 3. Inverse-frequency class weights — Equation (4)

### Why we need this on top of cross-entropy

Cross-entropy treats every token's loss equally. That sounds fair, but it has a hidden problem on imbalanced data. Recall the BIO tag distribution from the primer at the top of this document:

- 78 % of all training tokens are **O** (outside any entity)
- 22 % are entity tokens, and within those:
  - ACTOR, CITY, DATE are common (single-percentage-point shares each)
  - VICTIM, ACTION, CASUALTIES are rare (well under 1 % each)

Now imagine a training batch with 10,000 tokens. About 7,800 are O. Most of those O tokens are easy — the model figured out long ago that punctuation, articles, and prepositions are usually O. So each easy-O token contributes a small cross-entropy loss, say 0.01. But there are 7,800 of them, so they collectively contribute $7{,}800 \times 0.01 = 78$ units of loss.

In contrast, the batch might contain only **5 VICTIM tokens**, each contributing maybe 1.0 in loss (because the model is still struggling with them). Their total: $5 \times 1.0 = 5$ units of loss.

When the pipeline averages losses across the batch and computes the gradient, the **gradient signal is dominated by O tokens by a factor of 15**, even though VICTIM tokens are the ones the model most needs to learn from. **The rare classes are being drowned out.**

**Class weights fix this** by multiplying each token's loss by a per-class number — a big multiplier for rare classes, a tiny multiplier for common ones. The result is that the per-batch contribution of all 17 classes becomes more balanced, and the gradient pays proper attention to the rare classes.

### Analogy: an unfair voting system

Imagine an election where you have 7,800 voters from one big city and 5 voters from a tiny rural community. If each vote counts equally, the city decides everything and the rural voters are effectively ignored. To balance the system, you could give each rural voter 1,560 votes (so their voice equals 7,800 city votes ÷ 5 rural voters). The election would then represent both groups proportionally.

Inverse-frequency class weights are exactly that re-weighting. A class with fewer tokens gets a bigger per-token weight, so it isn't drowned out by the common classes.

### The formula

For each class $c$, compute a weight once at the start of training:

$$\alpha_c \;=\; \frac{T}{C \,\cdot\, \max(f_c,\, 1)}$$

with a clip: $\alpha_c \leftarrow \min(\alpha_c,\, 10)$ to prevent extreme weights from blowing up the gradient.

### Plain English

> *"Rare classes get a bigger multiplier on their loss; common classes get a smaller one. The multiplier is proportional to one divided by the class frequency, normalised so balanced classes would all get a weight of 1."*

### Symbol breakdown

| Symbol | Meaning |
|:-:|:--|
| $T$ | Total number of (non-ignored) tokens in the training set. |
| $C$ | Number of classes — 17 here. |
| $f_c$ | Count of class $c$ tokens in the training set. |
| $\max(f_c, 1)$ | Prevents division by zero when a class has no tokens. |
| $\alpha_c$ | The weight assigned to class $c$ for the loss. |

### Sanity check on the formula

If classes were perfectly balanced, every class would have $f_c = T/C$ tokens, so

$$\alpha_c = \frac{T}{C \cdot (T/C)} = 1$$

— every class gets weight 1 (no re-weighting). If class $c$ is *rarer* than balanced, $f_c < T/C$, so $\alpha_c > 1$ — that class gets boosted. The formula is exactly "expected count under balance ÷ actual count".

### Worked numeric example

Assume realistic VioNER training numbers:

| Quantity | Value |
|:--|--:|
| Total training tokens $T$ | 2,000,000 |
| Number of classes $C$ | 17 |
| Balanced expectation $T / C$ | 117,647 |

Counting tokens per class (approximate):

| Class $c$ | Count $f_c$ | $\alpha_c = T / (C \cdot f_c)$ | After clip |
|:--|--:|--:|--:|
| O | 1,560,000 | **0.075** | 0.075 |
| B-DATE | 32,000 | 3.68 | 3.68 |
| B-ACTOR | 48,000 | 2.45 | 2.45 |
| B-ACTION | 10,000 | 11.76 | **10.0** (clipped) |
| B-VICTIM | 5,500 | 21.39 | **10.0** (clipped) |

The clip at 10 is doing real work — without it, VICTIM and CASUALTIES would have weights above 20, which destabilises early training.

**Effect:** a VICTIM token contributes about $10 / 0.075 \approx 130 \times$ more loss-weight than an O token. That is what counter-balances the 78 % O dominance.

### Where in the thesis / slides

- Thesis §2.4, Equation (4) — defined and motivated
- Thesis §5.5 — implementation: weights computed once at training start, clipped at 10, ignore-index (-100) excluded from both the loss and the weight computation
- Defense slide 21 — appears as $w_c \propto 1/\text{freq}(c)$ in the focal-loss equation (where the thesis writes $\alpha_c$, the slide writes $w_c$ — same thing)

### Why it was required

Without per-class weighting, the model optimises overall accuracy, which on imbalanced data means "get O right almost always". The model converges to a state where it is very good at the easy class and mediocre at the operationally important rare classes. Class weights give the optimiser an explicit instruction: *one VICTIM mistake hurts much more than one O mistake.*

### Likely panel questions

- **"Why $T / (C \cdot f_c)$ and not just $1/f_c$?"** — *"Both are inverse-frequency, but the normalised form has the property that a perfectly balanced class gets weight 1. That makes the clip threshold (10) interpretable as 'no class can dominate by more than 10× the balanced-class weight'."*
- **"Why clip at 10?"** — *"Empirical — unclipped weights of 20-plus produced gradient instability in the first few hundred training steps. 10 keeps the rare classes elevated without destabilising early training."*
- **"Did you try effective-number weighting (Cui et al. 2019)?"** — *"Tried; it gave essentially the same per-entity F1 as plain inverse-frequency. The thesis kept the simpler scheme because it is reproducible without the corpus-overlap correction."*

---

## 4. Focal loss — Equation (1) — THE HEADLINE

### Why we need YET ANOTHER loss after class weights

Take stock of what we have so far:

- **Plain cross-entropy** (§2) treats all tokens equally — fails because 78 % are O.
- **Class weights** (§3) give rare classes a bigger per-token multiplier — helps, but **still treats all tokens within a class equally**.

Here's the remaining problem: many tokens are *easy*. For example, an O token between two punctuation marks is almost trivially O, and the model figures it out within the first epoch. Plain cross-entropy still spends loss-budget on those easy-correct tokens — the loss is small per token (say 0.01), but there are so many easy-correct tokens that they collectively eat up gradient. The optimiser ends up *polishing* tokens it already gets right instead of *focusing* on the tokens it still gets wrong.

**Focal loss is the surgical instrument** that fixes this. It tells the optimiser: *"don't bother polishing tokens you're already right about. Spend the gradient on the tokens you're still struggling with."*

### Analogy: a spotlight in a dim classroom

Imagine you're a teacher with 100 students. 95 of them already understand the topic; 5 are struggling. With **uniform attention** (= cross-entropy), you give equal time to each of the 100 students — wasting most of your energy on students who don't need it.

**Focal loss is like installing a spotlight that automatically brightens when a student looks confused, and dims when a student looks confident.** The harder it is for a student, the more attention they get. Students who already understand fade into the background; struggling students get nearly all of your focus.

The parameter $\gamma$ controls *how aggressive* the spotlight is:

- $\gamma = 0$ — the spotlight is uniform. Focal loss reduces to plain cross-entropy.
- $\gamma = 2$ — the spotlight is **sharp**. Confident-correct students get almost zero attention; struggling students get nearly all of it. This is the value used in this thesis (and the value recommended in the original focal-loss paper by Lin et al. 2017).
- $\gamma = 5$ — the spotlight is *too* sharp. Even moderately-confident students fade out and the optimiser only ever sees the catastrophic cases, which destabilises early training.

### The formula

For a single token with true class $y$ and predicted probability $p_y$:

$$\boxed{\text{FL}(p, y) \;=\; -\alpha_y \cdot (1 - p_y)^{\gamma} \cdot \log p_y}$$

Three factors multiplied together. Compare with cross-entropy ($\mathcal{L}_{\text{CE}} = -\log p_y$): focal loss adds two things — the class weight $\alpha_y$ and the **focusing modulator** $(1 - p_y)^\gamma$.

### Plain English

> *"Focal loss is cross-entropy with two extras. First, every class gets a weight (rare classes bigger, common classes smaller). Second, every token gets a modulator that becomes tiny when the model is already correct-and-confident, and becomes large when the model is uncertain. The net effect is that the loss focuses learning on the hard examples and the rare classes."*

### Symbol breakdown

| Symbol | Meaning | Range |
|:-:|:--|:-:|
| $p_y$ | Model's predicted probability for the **true** class. | $[0, 1]$ |
| $\alpha_y$ | Class weight for the true class — from Equation (4) above. | $[0.075,\, 10]$ here |
| $\gamma$ | The **focusing parameter**. Larger $\gamma$ = more aggressive down-weighting of easy examples. | $\gamma = 2.0$ in this thesis |
| $(1 - p_y)^\gamma$ | The focusing modulator. Small when $p_y \to 1$; close to 1 when $p_y \to 0$. | $[0, 1]$ |
| $-\log p_y$ | The original cross-entropy term. | $[0, \infty)$ |

### The focusing modulator in pictures

With $\gamma = 2$:

| $p_y$ | $(1 - p_y)^2$ | Reading |
|:--|--:|:--|
| 0.99 | 0.0001 | Model is very confident and correct → focal loss virtually ignores this token. |
| 0.90 | 0.01 | Confident-correct → 100× less weight than a hard token. |
| 0.50 | 0.25 | Uncertain → still substantial loss. |
| 0.10 | 0.81 | Wrong with high confidence → almost full loss applied. |
| 0.01 | 0.98 | Catastrophically wrong → effectively full loss. |

The take-home: **as the model gets better on a token, that token contributes less and less to the gradient.** The optimiser is forced to spend capacity on tokens it still gets wrong.

### Worked numeric example (combining class weights AND focal modulator)

Two contrasting tokens. Class weights from §3 above: $\alpha_{\text{O}} = 0.075$, $\alpha_{\text{VICTIM}} = 10$. $\gamma = 2$.

| Token | $p_y$ | Term-by-term | Focal loss |
|:--|--:|:--|--:|
| Easy O | 0.99 | $-\, 0.075 \cdot (0.01)^2 \cdot \log(0.99)$ | $7.5 \times 10^{-8}$ |
| Hard VICTIM | 0.50 | $-\, 10 \cdot (0.50)^2 \cdot \log(0.50)$ | $\mathbf{1.733}$ |

**Ratio:** the hard-VICTIM token contributes about **23 million times** more loss than the easy-O token. With plain cross-entropy and uniform weights, the same comparison gives:

| Token | $p_y$ | Plain CE | Ratio vs O |
|:--|--:|--:|--:|
| Easy O | 0.99 | 0.0101 | 1× |
| Hard VICTIM | 0.50 | 0.693 | 69× |

So focal loss with class weights amplifies the VICTIM-vs-O signal by another factor of about **330,000**. *That is the design intent.*

### Where in the thesis / slides

- Thesis §2.4, **Equation (1)** — definition
- Thesis §5.5 — implementation details (ignore-index masking, log-softmax stability)
- Thesis §6.6 — ablation table comparing plain CE, weighted CE, focal alone, focal + weights
- Defense slide 21 — **this is the headline equation** of the talk
- Defense slide 29 — the ablation table that quantifies the gain

### Why it was required

The motivating problem: 78 % of training tokens are O, and almost all of them are easy. Plain cross-entropy gives each easy-O token a small but non-zero loss; multiply by hundreds of thousands of easy-O tokens per batch and the gradient signal from rare-class examples gets washed out. Focal loss with $\gamma = 2$ suppresses the easy-O contribution by 100× or more, so the gradient becomes dominated by the harder examples — which is where the rare entities live.

The thesis's contribution claim is that **focal loss + inverse-frequency weights is complementary, not redundant**. The ablation in §6.6 / slide 29 shows:

- Class weights alone: VICTIM F1 = 0.776 (+7 over plain CE)
- Focal loss alone: VICTIM F1 = 0.792 (+8)
- Focal loss + class weights: VICTIM F1 = **0.817 (+11)**

The combined gain (+11) exceeds the sum of the individual gains (+7, +8 → would predict ≈ +15 if additive, but the gains overlap somewhat). Empirically the combination is the winner.

### Likely panel questions

- **"Why $\gamma = 2$?"** — *"Lin et al. 2017 — the focal-loss paper — reports $\gamma = 2$ as the value that works across object-detection benchmarks. We tried $\gamma = 1$ (smaller gain on VICTIM) and $\gamma = 3$ (marginally larger gain but unstable in early epochs). $\gamma = 2$ is the literature default and operationally stable."*
- **"Is focal loss just class weighting in disguise?"** — *"No. Class weighting changes the weight by class only. Focal loss changes the weight by individual example — even within one class, easy and hard examples get different weights. The two ingredients are orthogonal; the ablation confirms they are complementary."*
- **"What's the gradient look like?"** — *"$\partial \text{FL} / \partial z = (1 - p_y)^{\gamma} \cdot (p_y - y)$ approximately. The modulator scales the standard cross-entropy gradient. When the model is already correct-confident, the gradient is near zero — no learning happens on that token."*

---

## 5. Label smoothing target — Equation (3)

### The formula

For a token with true class $y$, the label-smoothing target distribution is:

$$y'_c \;=\; (1 - \beta) \cdot \mathbb{1}[c = y] \;+\; \frac{\beta}{C - 1} \cdot \mathbb{1}[c \neq y]$$

where $\beta \in [0, 1)$ is the smoothing factor, and $\mathbb{1}[\cdot]$ is 1 if the condition holds, 0 otherwise.

### Plain English

> *"Instead of saying 'the true class has probability 1 and every other class has probability 0', label smoothing says 'the true class has probability ~0.9 and every other class shares the remaining 0.1 equally'. The model is trained against a softer target, which prevents it from becoming overconfident."*

### Symbol breakdown

| Symbol | Meaning |
|:-:|:--|
| $y'_c$ | Smoothed target probability for class $c$. |
| $y$ | The true class label for this token. |
| $\beta$ | Smoothing strength. $\beta = 0$ gives the original hard one-hot label. $\beta = 0.1$ is the conventional choice. |
| $C$ | Number of classes (17). |
| $\mathbb{1}[c = y]$ | Indicator: 1 if $c$ is the true class, else 0. |

### Worked numeric example

With $\beta = 0.1$, $C = 17$, and true class $y$ = B-VICTIM:

- Target for the true class B-VICTIM: $(1 - 0.1) = \mathbf{0.9}$
- Target for each of the other 16 classes: $0.1 / 16 = \mathbf{0.00625}$

These 17 numbers sum to $0.9 + 16 \times 0.00625 = 1.000$. The model is now told "B-VICTIM is right but the other 16 are not totally wrong either".

### Where in the thesis / slides

- Thesis §2.4, **Equation (3)** — definition
- Thesis §5.5 — implementation: kept in production but with mild effect (described in §6.4)
- Defense backup B1 (hyperparameter table mentions $\beta$ implicitly)

### Why it was required

Label smoothing is a **regularisation** technique. The intuition is that one-hot targets push the model towards extremely large logits for the true class (so its softmax probability approaches 1), and that extreme behaviour can hurt calibration and generalisation. Smoothing keeps logits bounded.

In this thesis, label smoothing was **tested but turned out to give only a marginal gain**. The thesis kept it in production because the cost (slightly worse validation loss) is small and the calibration benefit is real, but it is *not* the reason the system works. The headline gains come from focal loss + class weights.

### Likely panel questions

- **"Why $\beta = 0.1$?"** — *"Inception paper default (Szegedy et al. 2016); the de-facto standard. Larger $\beta$ began to hurt validation F1."*
- **"Did smoothing actually help?"** — *"Marginally. Section 6.4 reports val loss 0.0074 without smoothing, 0.0076 with — slightly worse on the loss number, but smoother confidence distributions for downstream filtering. Kept in production for the calibration benefit."*

---

## 6. Focal loss with label smoothing — Equation (2) — THE PRODUCTION LOSS

### The formula

Combining focal loss (Eq. 1), inverse-frequency weights (Eq. 4), and label smoothing (Eq. 3):

$$\text{FL}_{\text{LS}}(p, y) \;=\; -\alpha_y \cdot (1 - p_y)^{\gamma} \cdot \sum_{c=1}^{C} y'_c \cdot \log p_c$$

This is the **actual loss function used in production training**. The sum runs over all classes (not just the true one) because every class gets a non-zero smoothed target.

### Plain English

> *"Same as focal loss, but instead of computing the loss against a one-hot label (which makes the sum collapse to a single term), we compute it against the smoothed target distribution. The result is one number per token that combines all three innovations: per-class weighting, per-example focusing, and target smoothing."*

### Symbol breakdown

Already defined above. New piece: the $\sum_c$ outer sum runs over all 17 classes because the smoothed target $y'_c$ is non-zero everywhere.

### Worked numeric example

True class = B-VICTIM. Suppose the model's softmax distribution puts $p_{\text{VICTIM}} = 0.50$, $p_{\text{O}} = 0.30$, and the remaining 0.20 spread across the other 15 classes. Use $\beta = 0.1$, $\gamma = 2$, $\alpha_{\text{VICTIM}} = 10$.

| Class $c$ | $y'_c$ | $\log p_c$ (using rough probs) | $y'_c \cdot \log p_c$ |
|:--|--:|--:|--:|
| B-VICTIM (true) | 0.9 | $\log 0.50 = -0.693$ | $-0.624$ |
| O | 0.00625 | $\log 0.30 = -1.204$ | $-0.0075$ |
| Each of 15 other | 0.00625 | $\log(0.20/15) \approx -4.32$ | $-0.027$ each |

Sum of inner term: $-0.624 - 0.0075 - 15 \times 0.027 \approx -1.03$

Then:

$$\text{FL}_{\text{LS}} = -10 \cdot (1 - 0.50)^2 \cdot (-1.03) = 10 \cdot 0.25 \cdot 1.03 = \mathbf{2.58}$$

Compare with the same token under plain Eq. (1) focal loss (no smoothing): we computed 1.733 earlier. Smoothing made the loss slightly larger (2.58 vs 1.73) because the model is now also penalised for putting too little probability mass on the "smoothed-as-non-zero" non-true classes.

### Where in the thesis / slides

- Thesis §2.4, **Equation (2)** — definition
- Thesis §5.5 — implementation
- Defense slide 21 — the equation shown is Equation (1) (without smoothing) because $\beta = 0$ recovers it; the production code uses Eq. (2)

### Why it was required

This is just the integrated form. Equations (1), (3), and (4) are the ingredients; Equation (2) is the recipe that combines them. The thesis presents them separately so that the contribution of each ingredient can be ablated independently in §6.6.

### Likely panel questions

- **"If the slide shows Eq. (1), why is the production code Eq. (2)?"** — *"Equation (2) reduces to (1) when $\beta = 0$. With $\beta = 0.1$ the smoothing term is small in effect but non-zero. The slide shows the simpler form for clarity; the codebase uses (2) for the calibration benefit."*

---

# Part B · The metric family (evaluation-time math)

Now we leave training behind. The model's weights are frozen. We need to **answer one question**: *how good is the trained model at extracting entities from text it has never seen?* That's evaluation, and the next four formulas are how every results table in the thesis was computed.

## Why we hold data out

During training (Part A), the model adjusts its weights to fit the training examples. The danger is that the model could **memorise** the training data without learning anything generalisable — like a student who memorises practice-exam answers without understanding the material. Such a student would ace the practice exam and bomb the real one.

To detect this and to estimate real-world performance honestly, we **set aside** a portion of the data — the **validation split** — that the model **never sees during training**. After training is complete, we run the model on the validation split and measure performance there. The metrics on the validation split are a fair estimate of what would happen on truly new, unseen data.

This thesis uses an **80 / 20 split**:

- **80 %** of the 50,000 examples → training (the model sees these and adjusts weights)
- **20 %** = **10,000 examples** → validation (the model never trains on these)

Every F1 number on slides 27, 28, 29 — including the headline 0.909 micro F1 — was computed on that held-out 10,000-example validation split.

> **The split is at the article level, not the sentence level.** No article appears in both halves. The thesis goes one step further: articles are hashed and deduplicated *before* the split, so even copy-pasted duplicates can't sneak across. This is what "held-out integrity" on slide 24 means.

## What are TP, FP, FN? — A spam-filter analogy

To compute any NER metric, we first bucketise every prediction into one of four boxes. Think of an email spam filter:

| Bucket | What happened in spam filtering | What it means for NER |
|:--|:--|:--|
| **True Positive (TP)** | Filter said "spam" → email was spam ✓ | Model predicted an entity → gold says yes, same type and same boundaries ✓ |
| **False Positive (FP)** | Filter said "spam" → email was real ✗ | Model predicted an entity → gold says no (or different type/boundaries) ✗ |
| **False Negative (FN)** | Filter said "not spam" → email was spam ✗ | Model missed an entity that was actually there ✗ |
| **True Negative (TN)** | Filter said "not spam" → email was real ✓ | Model correctly said "no entity here" ✓ |

For NER we **don't report TN** because there are too many of them — every O token is technically a TN, and counting them would dilute the metric. The three numbers that drive every NER report are:

- **TP**: useful entities found
- **FP**: false alarms (extra work for the analyst)
- **FN**: missed entities (gap in coverage)

### Why both FP and FN matter

A model that achieves **high precision** but **low recall** is the equivalent of a spam filter that only flags emails it is 100 % sure about. Almost nothing flagged is wrong (low FP), but tons of actual spam slips through (high FN). For VioNER that would mean: every extracted record is correct, but most of the violent events in the article queue never get extracted. The analyst still has to do everything by hand.

A model that achieves **high recall** but **low precision** is the equivalent of a spam filter that flags everything that looks even vaguely suspicious. Almost no real spam slips through (low FN), but the user has to wade through tons of false alarms (high FP). For VioNER that would mean: nothing is missed, but every entity list has so much noise that the analyst spends as much time filtering false alarms as they would have on the original article.

Both modes are failure modes. The thesis reports **F1**, which is high only when both precision and recall are high simultaneously.

---

## 7. Precision, Recall, F1 — span-level

### The formulas

For each entity type, count over the validation set:

- **TP** (true positives): predicted spans that exactly match a gold span (same type AND same boundaries)
- **FP** (false positives): predicted spans that don't match any gold span
- **FN** (false negatives): gold spans that no prediction matches

Then:

$$\text{Precision} \;=\; \frac{\text{TP}}{\text{TP} + \text{FP}}$$

$$\text{Recall} \;=\; \frac{\text{TP}}{\text{TP} + \text{FN}}$$

$$\text{F1} \;=\; 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

### Plain English

> *"Precision: of the entities the model predicted, what fraction were right? Recall: of the entities that really existed, what fraction did the model find? F1 is the harmonic mean — a single number that rewards being good at both."*

### Symbol breakdown

| Symbol | Meaning |
|:-:|:--|
| TP | Number of predicted spans that exactly match gold (correct, useful predictions). |
| FP | Predicted spans with no matching gold (wrong predictions — noise the analyst would have to filter). |
| FN | Gold spans with no matching prediction (missed extractions — work the analyst still has to do manually). |
| F1 | Harmonic mean of P and R — closer to whichever is lower. |

### Worked numeric example — VICTIM from the thesis

From Table 6.7 (slide 28): VICTIM precision = 0.838, recall = 0.798, gold support (total gold VICTIM spans) = 5,492.

Reverse-engineer the counts:

- True positives: TP = 5,492 × recall = 5,492 × 0.798 = **4,383** VICTIM spans correctly recovered
- False negatives: FN = 5,492 − 4,383 = **1,109** VICTIM spans missed
- From precision: TP / (TP + FP) = 0.838, so FP = TP × (1 − 0.838) / 0.838 = 4,383 × 0.1934 = **848**

So the model recovered 4,383 of 5,492 gold VICTIMs (recall 0.798), produced 848 false alarms (so precision 0.838).

F1 check:

$$\text{F1} = \frac{2 \cdot 0.838 \cdot 0.798}{0.838 + 0.798} = \frac{1.337}{1.636} = \mathbf{0.817}$$

Matches the thesis table. ✓

### Why harmonic mean?

The harmonic mean is **closer to the smaller of the two values** than the arithmetic mean. If precision = 1.0 and recall = 0.1:

- Arithmetic mean: (1.0 + 0.1) / 2 = 0.55 — flattering.
- Harmonic mean (F1): 2 × 1.0 × 0.1 / 1.1 = 0.182 — honest.

F1 punishes a model that wins on one metric by sacrificing the other. That is exactly what we want for NER: high precision with terrible recall is useless (we missed everything), and high recall with terrible precision is useless (we drowned the analyst in false alarms).

### Where in the thesis / slides

- Thesis §2.5 — definitions
- Thesis §6.4–6.7 — every results table
- Defense slide 27 — the headline F1
- Defense slide 28 — per-entity precision/recall/F1
- Defense slide 29 — ablation in F1 terms

### Why it was required

F1 is the universal NER reporting metric. CoNLL-2003 set the convention; every NER paper since reports F1 in the same form. Reporting precision and recall separately exposes the trade-off (some entities are precision-bound, some recall-bound).

### Likely panel questions

- **"Why not just accuracy?"** — *"With 78 % O tokens, a degenerate predict-O-everywhere model would score 78 % token accuracy. F1 on entity spans is the right metric because it ignores correct O predictions entirely."*
- **"Strict or relaxed span matching?"** — *"Strict — both type and exact boundaries must match. CoNLL-2003 convention. A relaxed-match score (50 % overlap) would be 1.5-2 points higher."*

---

## 8. Macro F1 vs Micro F1

### The formulas

After computing per-entity F1 ($\text{F1}_c$ for class $c$):

$$\text{Macro F1} \;=\; \frac{1}{K} \sum_{c=1}^{K} \text{F1}_c$$

(average of per-class F1; each class weighted equally — $K$ here is the number of entity types, **not** the number of BIO labels)

$$\text{Micro F1} \;=\; \text{F1}\Bigl(\sum_c \text{TP}_c, \, \sum_c \text{FP}_c, \, \sum_c \text{FN}_c\Bigr)$$

(F1 recomputed from pooled counts; high-support classes dominate)

### Plain English

> *"Macro F1 averages the per-entity F1 scores, treating every entity type as equally important. Micro F1 pools the raw counts across all entity types and computes one F1 from those — so populous classes like DATE and CITY drive the number more than VICTIM does."*

### When to use which

- **Macro F1** — the right number when you want to know whether the model is balanced across entity types. A bad rare-entity F1 brings macro down sharply.
- **Micro F1** — the right number when you want to estimate overall extraction throughput. Dominated by the high-support entities. Treats every gold span as equally important.

### Worked numeric example using thesis numbers

From Table 6.7:

| Entity | Support | F1 |
|:--|--:|--:|
| DATE | 31,938 | 0.956 |
| CITY | 44,361 | 0.934 |
| ACTOR | 47,612 | 0.923 |
| REGION | 24,331 | 0.891 |
| CASUALTIES | 4,907 | 0.885 |
| ACTION | 9,963 | 0.866 |
| DISTRICT | 21,471 | 0.826 |
| VICTIM | 5,492 | 0.817 |

**Macro F1:**

$$(0.956 + 0.934 + 0.923 + 0.891 + 0.885 + 0.866 + 0.826 + 0.817) / 8 = 7.098 / 8 = \mathbf{0.887}$$

Matches the thesis. ✓

**Micro F1:** computed from pooled TP/FP/FN across all 8 entities. The thesis reports 0.909 — about 2 points higher than macro because the high-support entities (DATE, CITY, ACTOR) have higher F1 and dominate the pool.

### Where in the thesis / slides

- Thesis §2.5 — definitions
- Defense slide 27 — both reported in the caption
- Defense slide 28 — macro reported as the bottom row

### Why it was required

Reporting one of these in isolation is misleading. Macro alone hides the fact that the model performs well overall; micro alone hides the fact that VICTIM is weaker. Reporting both is standard NER practice and the thesis's defence depends on both: macro shows balance, micro shows operational throughput.

### Likely panel questions

- **"Which is more important?"** — *"Depends on the use case. For analyst triage on rare events, macro matters more — we need every entity type to be usable. For estimating annual throughput across all events, micro matters more."*
- **"Why is micro higher than macro here?"** — *"Because the highest-support entities (DATE, CITY, ACTOR) also have the highest F1. Micro is weighted by support, so it inherits their numbers more strongly than the rare-entity numbers."*

---

## 9. Token accuracy

### The formula

$$\text{Token accuracy} \;=\; \frac{\text{number of correctly classified tokens}}{\text{total tokens (excluding special tokens)}}$$

### Plain English

> *"The fraction of token positions where the model's predicted label matches the gold label."*

### Worked numeric example

Imagine a 100-token validation set where the model gets 95 tokens right (78 O tokens correctly tagged as O, plus 17 entity tokens correctly tagged with their entity).

$$\text{Token acc} = 95/100 = \mathbf{0.95}$$

### Where in the thesis / slides

- Thesis §2.5 — defined, with a warning
- Defense slide 27 — reported as 96.7 % in the caption

### Why it was required (and why it should not be the headline)

The thesis reports token accuracy for completeness — it is the simplest available metric and easy for non-specialists to interpret. **But §2.5 explicitly warns against using it as the headline metric.** With 78 % O tokens, a "predict O everywhere" model already achieves 78 % accuracy without learning anything useful. The 96.7 % accuracy reported in this thesis sounds good, but the meaningful gain over the naïve baseline is only 96.7 − 78 = **18.7 percentage points** of useful learning. F1 — which ignores correct O predictions — is the metric that captures actual entity-extraction quality.

### Likely panel questions

- **"96.7 % accuracy sounds great — why isn't that your headline?"** — *"Because 78 % of tokens are O, so the trivial 'predict O everywhere' baseline already gives 78 %. The headline metric is span-level F1, which ignores correct O predictions and measures actual entity recovery."*

---

# Part C · The agreement metric

The first two parts measured the **model**. This last part measures the **data the model learned from** — specifically, how trustworthy the gold labels are. Without this, every F1 number in Part B is suspect.

## What is "annotation" in the first place?

A neural network can only learn from **labelled** data. For VioNER that means: for every sentence in the training corpus, every token has a BIO label written next to it that says what it is. Where do those labels come from? From human **annotators** reading the source text and assigning labels by hand, guided by a written annotation guideline.

The process for one sentence:

1. A human reads a news article — say, the canonical *"On Tuesday, fighters from Al-Shabaab attacked a military convoy near Mogadishu, killing at least 12 soldiers."*
2. They identify the entity spans: *"Tuesday"* is a DATE, *"Al-Shabaab"* is an ACTOR, *"attacked"* is an ACTION, *"military convoy"* is a VICTIM, *"Mogadishu"* is a CITY, *"at least 12 soldiers"* is a CASUALTIES span.
3. They write down the BIO tag for each token (the full token-by-token table in the BIO primer at the top of this document).

Multiplied across 50,000 examples, that's a lot of human time. In this thesis, the gold labels were produced by **projecting ACLED's structured columns onto the free-text notes** (a semi-automated process that gives a first-pass labelling), followed by **manual review and spot-checking** to catch errors. The guideline that tells annotators *exactly* how to draw each kind of span grew from 9 pages to 31 pages over six iterations (§5.2 of the thesis).

## Why measure agreement?

Here's the threat: **human annotators disagree**. Two careful annotators looking at the same sentence can draw the same span differently. For example, *"twelve civilians"* vs *"at least twelve civilians"* — does the qualifier belong inside the CASUALTIES span? Without an explicit rule, two annotators will choose differently, and the corpus ends up with inconsistent labels.

If those disagreements are common, **the gold labels themselves are noisy**, and any F1 number we compute against them inherits that noise. We'd be reporting how well the model matches a moving target.

We measure inter-annotator agreement to **estimate how clean the gold labels are**. If two annotators agree on 92 % of tokens after a sensible disagreement-correction protocol, the labels are clean enough that the trained model's failures probably reflect *model* error, not *label* error. If they disagree on, say, 40 % of tokens, the labels are too noisy to draw any model-quality conclusion at all.

## Analogy: two doctors reading the same X-ray

Imagine two radiologists looking at the same chest X-ray:

- If they **both** say *"pneumonia in the lower right lobe"*, that's strong evidence — the finding is real and the procedure is reliable.
- If one says *"pneumonia"* and the other says *"no abnormality at all"*, you can't trust either reading. Either the X-ray itself is unclear, or one of the radiologists is wrong, or the diagnostic criteria are ambiguous.

You'd want a single number that summarises how reliable the *procedure* is — independently of what the right answer turns out to be. **Cohen's κ is that number.** And it has a subtlety the raw agreement doesn't: it corrects for chance agreement. If 78 % of tokens are O, two annotators will agree about 60 % of the time just by random labelling. κ subtracts out that chance baseline so the number reflects *actual annotator skill at the edge cases*.

---

## 10. Cohen's κ — annotator agreement

### The formula

For two annotators classifying the same items:

$$\kappa \;=\; \frac{p_o - p_e}{1 - p_e}$$

### Plain English

> *"Of the cases where two annotators agreed, what fraction of that agreement was beyond what you'd expect by random chance? κ = 1 means they always agree; κ = 0 means they agree no more than chance; κ < 0 means they agree less than chance."*

### Symbol breakdown

| Symbol | Meaning |
|:-:|:--|
| $p_o$ | **Observed agreement** — the fraction of items both annotators gave the same label to. |
| $p_e$ | **Chance agreement** — the probability they would agree purely by random labelling, computed from the marginal frequencies. |
| $\kappa$ | Agreement corrected for chance. |

### Computing $p_e$

If annotator A labels with class frequencies $p_A(c)$ and annotator B with $p_B(c)$, the chance agreement is

$$p_e = \sum_c p_A(c) \cdot p_B(c)$$

— the sum over all classes of the joint probability of both choosing that class independently.

### Landis-Koch interpretation scale

| κ range | Interpretation |
|:--|:--|
| < 0.00 | Worse than chance (rare) |
| 0.00 – 0.20 | Slight agreement |
| 0.21 – 0.40 | Fair |
| 0.41 – 0.60 | Moderate |
| 0.61 – 0.80 | **Substantial** ← this thesis lives here at 0.78 |
| 0.81 – 1.00 | Almost perfect |

### Worked numeric example

Suppose two annotators each label 200 tokens. Their distributions are:

| Class | Annotator A | Annotator B |
|:--|--:|--:|
| O | 78 % | 76 % |
| Any entity | 22 % | 24 % |

Imagine they agree on 92 % of tokens overall ($p_o = 0.92$).

Chance agreement:

$$p_e = 0.78 \cdot 0.76 + 0.22 \cdot 0.24 = 0.593 + 0.053 = 0.646$$

Cohen's κ:

$$\kappa = \frac{0.92 - 0.646}{1 - 0.646} = \frac{0.274}{0.354} = \mathbf{0.774}$$

≈ 0.78. The 0.78 reported in the thesis is in the substantial-agreement band.

### Where in the thesis / slides

- Thesis §5.2 — annotation process and IAA reporting
- Defense slide 24 (data: enough and good enough) — Cohen's κ = 0.78 in the quality column
- Q&A kit Q7, Q26, Q41 — answers depending on this number

### Why it was required

Without an inter-annotator-agreement metric, the panel cannot tell whether the gold labels are reliable. A trained model can only be as good as the labels it learned from; if annotators disagreed about half the time, the gold standard itself is noise, and any F1 number means little. κ = 0.78 says the annotation is internally consistent enough that **the F1 numbers reflect model quality, not label noise**.

The thesis uses κ rather than raw agreement because raw agreement is inflated by the dominance of the O class — annotators would agree on most tokens just by both labelling them O. κ corrects for that chance agreement and gives a number that reflects actual annotator skill at the harder edge-case decisions.

### Likely panel questions

- **"Why κ = 0.78 and not higher?"** — *"0.78 is in the 'substantial' band on the Landis-Koch scale. Reading down to 0.85 (almost-perfect) would require constraining annotators with more mechanical rules at the cost of edge-case quality. The natural floor in NER is around 0.80-0.85 for any non-trivial schema; we live close to that floor."*
- **"What's the consequence for F1?"** — *"Q41 answers this — Monte-Carlo simulation of the κ disagreement as label noise gives an F1 uncertainty band of ±2.7 percentage points. The +11 F1 VICTIM gain exceeds that by 4×, so the conclusion is robust to annotation noise at this κ level."*

---

# How the formulas fit together

## Training-time math (the path from data to model)

```
gold BIO labels ───►  one-hot target y
                        │
                        ▼
                    smoothed target  y'   ◄── Eq. (3)
                        │
                        ▼
BERT(input) ─► logits z ─► softmax ─► probabilities p   ◄── §1 above
                        │
                        ▼
                  -α_y · (1-p_y)^γ · Σ y'_c · log p_c   ◄── Eq. (2) production loss
                        │
                        ▼
                    gradient  ─►  backprop  ─►  updated BERT
```

Class weights $\alpha_c$ (Eq. 4) are computed once before training begins and held fixed.

## Evaluation-time math (the path from model to F1)

```
BERT(input) ─► logits z ─► softmax ─► probabilities p
                        │
                        ▼
              argmax over 17 classes  ─►  predicted BIO labels
                        │
                        ▼
              BIO decode  ─►  predicted spans (type, start, end)
                        │
                        ▼
              compare with gold spans
                        │
                        ▼
                TP, FP, FN per entity type   ◄── §7
                        │
                        ▼
        Precision, Recall, F1 per entity     ◄── §7
                        │
                        ▼
            Macro F1, Micro F1               ◄── §8
```

## Quality-control math (separately, on the gold labels themselves)

```
two annotators ─► two labellings of the same 200-doc pilot
                        │
                        ▼
              observed agreement p_o
              expected agreement p_e         ◄── §10
                        │
                        ▼
                Cohen's κ = (p_o - p_e) / (1 - p_e)  =  0.78
```

---

# One-page cheat sheet

If you only memorise five things from this document, memorise these:

1. **Softmax** turns raw model outputs into probabilities. $p_y$ is the probability the model assigned to the true class.
2. **Cross-entropy loss** $= -\log p_y$. The baseline. Drowns rare classes when 78 % of tokens are O.
3. **Focal loss** $= -\alpha_y \cdot (1 - p_y)^{\gamma} \cdot \log p_y$ with $\gamma = 2$. Suppresses easy-correct tokens by a factor of $(1-p_y)^2$; for $p_y = 0.99$ that is $0.0001$ — 10,000× suppression.
4. **Class weights** $\alpha_c = T / (C \cdot f_c)$ clipped at 10. VICTIM gets weight ≈ 10; O gets weight ≈ 0.075. Ratio ≈ 130×.
5. **Span-level F1** $= 2 \cdot P \cdot R / (P + R)$ on exactly-matched entity spans. **Macro** averages across entity types; **micro** pools all counts.

And the headline result derives from these:

> *Plain cross-entropy gives VICTIM F1 = 0.708. Focal loss + class weights gives VICTIM F1 = 0.817. The gain is **+10.9 F1**, computed exactly as $\text{F1}(\text{TP}, \text{FP}, \text{FN})$ on the held-out validation split of 5,492 VICTIM gold spans.*

That sentence is the empirical answer to RQ2 and the single most quotable result of this thesis. Every formula in this document is in service of that sentence.

---

## Where to flip if asked

| Panel question type | Section here |
|:--|:-:|
| "What is focal loss?" | §4 |
| "Why $\gamma = 2$?" | §4 |
| "How do you compute class weights?" | §3 |
| "Why not just cross-entropy?" | §2 + §4 |
| "What is precision / recall / F1?" | §7 |
| "Macro or micro — which matters?" | §8 |
| "What does 96.7 % accuracy mean?" | §9 |
| "What is Cohen's κ?" | §10 |
| "How does the loss fit together?" | "How the formulas fit together" |

---

# Part D · How to talk about these formulas during the defense

Two scenarios where formulas come up in your defense:

- **Proactive** — you are presenting slide 21 (the training recipe with the focal-loss equation) or slide 24 (data quality with Cohen's κ). You speak to the formula as part of the talk.
- **Reactive** — an examiner stops you to ask "what does that mean", "why this not that", or "walk me through this equation".

This part gives you a script for both, plus the answering discipline that keeps you calm when a formula is on screen and three pairs of eyes are watching.

---

## The universal answering pattern

When a formula question lands, follow this sequence — every time, no exceptions:

1. **Pause one beat.** A two-second silence makes you sound considered. It also gives you time to choose the right level of depth.
2. **Plain English first.** Lead with what the formula *does* in everyday language. Never lead with symbols.
3. **Then walk the symbols.** Point at the equation. Name each symbol. Connect it back to the plain English you just said.
4. **End with the empirical hook.** Tie the formula to the result it produced — *"and that's why VICTIM F1 moved from 0.708 to 0.817."*
5. **Stop.** Don't keep talking. Wait for the examiner to indicate "go deeper" or "next question".

The discipline of this pattern matters more than the words. If you panic and start with symbols, the panel hears uncertainty.

---

## Proactive — when YOU bring the formula up

### Slide 21 — Focal loss with class weights (the headline equation)

You will reach this slide around minute 17 of the talk. The equation is on screen. Here is what to say, in plain conversational English. **Time budget: 90 seconds.**

> *"The loss function is the technical heart of this work. Let me walk through it term by term — it is built up from three ingredients."*

> *"The backbone is plain cross-entropy — the minus-log-of-the-true-class-probability term you can see in the equation. That's the standard classification loss; it tells the model 'you were wrong by this much on this token'."*

> *"On top of cross-entropy I add two modifications. The first is the class weight $\alpha_y$ — the per-class multiplier. Rare classes like VICTIM and CASUALTIES get a larger weight; common classes like O and DATE get a smaller one. The weights are computed once at the start of training from the inverse of each class's frequency. Without these weights, the 78-percent O class would dominate the gradient and the rare classes would never learn."*

> *"The second modification is the focal-loss focusing factor — the $(1 - \hat{y}_y)$ raised to the power $\gamma$ term. When the model is already confident and correct on a token, that factor goes nearly to zero, so the loss on that token is essentially ignored. When the model is uncertain or wrong, the factor stays close to one, so the full loss is applied. The effect is that the optimiser spends its capacity on hard tokens, not on easy ones."*

> *"Why combine both? Because they attack different aspects of the imbalance problem. Class weights re-balance across classes; focal loss re-balances across examples within a class. Section 6.6 of the thesis is the ablation that shows the two are complementary, not redundant — they each help individually, and the combination helps more than either alone. The empirical headline: this configuration lifts VICTIM by 11 F1 points and ACTION by 7, with no entity hurt."*

**Then pivot to the next slide.**

> *"The full hyperparameter table is in backup B1 if you want to drill into specific values."*

#### Pointing strategy

Stand at an angle so the panel can see both you and the screen. Point at the equation **once** per ingredient — once at the cross-entropy term, once at the $\alpha_y$ term, once at the $(1 - \hat{y}_y)^\gamma$ term. Don't trace the formula left-to-right with your finger while talking; that looks anxious.

### Slide 24 — Cohen's κ (data quality)

You will reach this slide around minute 14, after the dataset slide. The κ figure (0.78) sits in the right-hand column. **Time budget: 30 seconds.**

> *"Quality defence on the right. Cohen's kappa is the standard inter-annotator agreement metric — it measures how often two annotators agreed on the same label, corrected for the agreement you'd expect by chance. Range is minus-one to plus-one; this thesis comes in at zero-point-seven-eight on a two-hundred-document pilot. On the Landis-Koch interpretation scale that's substantial agreement — meaning the gold labels are internally consistent enough that the F1 numbers we report reflect model quality, not label noise."*

You do **not** need to write the formula on the board. The number and its interpretation are enough.

---

## Reactive — when the examiner asks

The following scripts are calibrated to **30, 60, or 90 seconds**. Pick the depth based on how the question was phrased:

- *"What is cross-entropy?"* → 30 seconds. Beginner-level question. Don't over-deliver.
- *"Why focal loss and not cross-entropy?"* → 60 seconds. They want the comparison logic.
- *"Walk me through equation 2 in detail."* → 90 seconds. They want the term-by-term breakdown.

If you can't read the question's depth, default to 60 seconds and stop. They will ask for more if they want it.

### Q · "What is cross-entropy loss?" — 30 seconds

> *"Cross-entropy is the standard classification loss. For each token, it takes the model's predicted probability for the true class and computes minus the natural logarithm of that probability. The intuition is 'surprise' — if the model gave high probability to the right answer, the loss is small; if it gave low probability, the loss is large. The minus-log function has the right shape for this: zero when the model is perfect, growing unboundedly as the model's confidence in the wrong direction increases. It's the baseline this thesis improves on."*

### Q · "Why focal loss and not cross-entropy?" — 60 seconds

> *"Three reasons that build on each other. First, plain cross-entropy treats every token equally, which fails on imbalanced data — 78 percent of tokens in this corpus are O, and the gradient signal from the rare entity classes gets drowned out. Second, even with class weights added to cross-entropy, the loss still spends gradient on easy tokens — tokens the model already gets right with high confidence. Those easy tokens are numerous, and they collectively waste capacity that should be spent on hard cases. Focal loss fixes the second problem by adding a focusing factor that goes nearly to zero whenever the model is already confident-and-correct. The empirical result: with focal loss and class weights together, VICTIM F1 moves from 0.708 under plain cross-entropy to 0.817 — a gain of about 11 F1 points, no other entity hurt. That ablation is in section 6.6 of the thesis."*

### Q · "What does $\gamma$ control?" — 30 seconds

> *"Gamma controls how aggressively focal loss down-weights easy examples. With gamma equal to zero, focal loss reduces to plain cross-entropy. With gamma equal to two — the value used here, also the literature default from the Lin et al. 2017 paper — the focusing factor at probability 0.9 is 0.01, meaning a confident-correct token contributes 100 times less to the loss than a maximally hard token. We tried gamma equal to one and gamma equal to three; one gave smaller gains, three caused instability in early training. Two was operationally stable."*

### Q · "How are class weights computed?" — 45 seconds

> *"At the start of training, before any gradient is computed, the pipeline counts how many tokens of each of the 17 BIO labels appear in the training set. The weight for each class is then computed as the total token count divided by the product of the number of classes and that class's count. The formula is in equation 4 of the thesis. The intuition is that if classes were balanced, every weight would come out to one; classes that are rarer than balanced get weights above one. We cap the weights at ten to prevent the rarest classes — VICTIM and CASUALTIES — from producing unstable gradients in early training. The cap is mentioned in section 5.5."*

### Q · "What is F1?" — 30 seconds

> *"F1 is the harmonic mean of precision and recall. Precision is the fraction of predicted entities that were correct; recall is the fraction of gold entities the model recovered. F1 punishes you when either one is low — a model with 100 percent precision but 10 percent recall scores about 18 percent F1, not 55 percent. That's why it's the standard NER metric: you can't game it by tuning only one side."*

### Q · "Macro versus micro — which matters?" — 45 seconds

> *"Both, for different purposes. Macro F1 averages the per-entity F1 scores treating every entity equally — so a poor rare-entity F1 drags it down sharply. Micro F1 pools the raw true-positive, false-positive, and false-negative counts across all entities before computing one F1 — so the high-support entities like DATE and CITY dominate it. For this thesis, macro is the right number for assessing balance across entity types — it's how we know VICTIM hasn't been sacrificed for ACTOR. Micro is the right number for estimating overall extraction throughput. The thesis reports both: macro 0.887, micro 0.909."*

### Q · "What does Cohen's κ = 0.78 mean?" — 30 seconds

> *"Cohen's kappa measures inter-annotator agreement corrected for chance. The raw agreement number alone is misleading because two annotators would agree on most tokens just by both labelling them O. Kappa subtracts out that chance baseline. Zero-point-seven-eight on the Landis-Koch scale is substantial agreement — one band below almost-perfect. It tells us the gold labels are internally consistent enough that the F1 numbers reflect model error, not label noise."*

### Q · "Walk me through equation 2 in detail." — 90 seconds

This is the deepest version. Use it when the examiner explicitly asks for term-by-term.

> *"Equation 2 is the production loss — focal loss with class weights and label smoothing combined. Three ingredients."*

> *"First ingredient — the class weight, alpha-sub-y. This is the per-class multiplier from equation 4 — it scales the whole loss up for rare classes and down for common ones. Computed once at training start, held fixed."*

> *"Second ingredient — the focal-loss focusing factor, $(1 - \hat{y}_y)$ raised to the power gamma. This is the per-example modulator. When the model's predicted probability on the true class is near 1, the factor is near 0; when the probability is near 0, the factor is near 1. With gamma equal to 2, a probability of 0.9 gives a factor of 0.01 — 100-times suppression."*

> *"Third ingredient — the inner sum across all 17 classes of the smoothed target times the log-probability. The smoothed target comes from equation 3 — instead of a one-hot label where the true class is 1 and all others are 0, the smoothed version uses 0.9 for the true class and distributes the remaining 0.1 evenly across the other 16 classes. This regularises against overconfident predictions."*

> *"Multiply all three together and put a minus sign in front so we're minimising rather than maximising. That's the loss the gradient is computed against on every batch of training."*

> *"When the smoothing factor beta is zero, equation 2 reduces to equation 1. In production we use beta equal to 0.1 — small but non-zero."*

### Q · "Can you derive the gradient of focal loss?" — graceful answer

This is the kind of question that can blindside you. The honest answer:

> *"The gradient is computed automatically by PyTorch through backpropagation, so I never derived it by hand. The qualitative shape, which is what matters for the design choice, is that the gradient is the standard cross-entropy gradient — predicted probability minus the target — multiplied by the focal modulator $(1 - p_y)^\gamma$. When the model is confident-correct, the modulator goes to zero and so does the gradient. That's why focal loss makes the optimiser skip easy tokens. If you'd like the exact derivation, it's in section 3.2 of the Lin et al. 2017 paper."*

That's a 30-second answer that demonstrates understanding without pretending you can do calculus on the board.

---

## What level of depth to go to

Master's defenses are not classroom whiteboard sessions. **You are not expected to derive gradients, prove convergence properties, or compute by hand.** You ARE expected to:

- Know what each formula computes intuitively
- Know which formula is used where in the pipeline
- Know the empirical evidence each formula's contribution rests on
- Be able to point at any term and say what it does

Aim for **graduate-engineer fluency**, not **theoretical-mathematician fluency**. The examiners want to see that you understand your own thesis, not that you could teach a numerical-optimisation course.

A useful rule of thumb: **answer for 30 to 90 seconds, then stop**. The examiner will ask for more if they want it. Over-delivering is a worse failure mode than under-delivering, because it signals you are nervous and trying to prove yourself.

---

## What NOT to say

| Don't say | Why it hurts |
|:--|:--|
| *"I'm not really sure what gamma does exactly..."* | Hedging on a defined hyperparameter signals lack of preparation. If you don't know, say "gamma is 2 — let me explain why" rather than admit ignorance of the value. |
| *"It's complicated..."* | A defensible thesis is not "complicated"; it is precise. Say what is true. |
| *"This is just from the paper..."* | The thesis cites Lin et al. for focal loss, but you own the choice to use it. Defend the choice, not just the citation. |
| *"I trusted what my advisor said..."* | Even if true, this passes ownership away from you. Reframe as "after discussion with my advisor, the choice was..." |
| *"I think it works because..."* | If you don't know, say "the evidence in section 6.6 shows..." — point at the empirical record, not your guess. |
| Long pauses without indicating you are thinking | Silence reads as lost. If you need a beat, say *"let me organise the answer for a second"* — the panel will wait. |
| Writing on a whiteboard unprompted | Defence Q&A is usually verbal. Writing while talking is hard. If you need to point at something, point at the slide. |

---

## When you genuinely don't know

This will happen at least once during a 30-minute defense. Don't panic. Use this template:

> *"That's a question I don't have direct evidence on. The closest related evidence I have is [name what you do have — a section, a related result, an analogy]. If I had to speculate, my best guess would be [bounded conjecture]. But I'd want to verify that before saying it confidently."*

Examples of legitimate "I don't know" moments for the formula material:

- *"What's the exact gradient expression for focal loss?"* → *"I haven't derived it by hand. PyTorch handles backpropagation. The qualitative behaviour is what drove the design choice."*
- *"What's the relationship between focal loss and the dice loss used in segmentation?"* → *"I haven't compared focal loss to dice loss directly. The thesis chose focal loss because it has direct prior work in token classification under imbalance, which is the closer analogue."*
- *"What if you used a different smoothing distribution — like uniform plus knowledge-base priors?"* → *"That's a direction I didn't explore. The thesis stayed with the standard uniform smoothing from Szegedy et al. 2016. Knowledge-base-informed smoothing is an interesting future-work idea."*

The pattern: name what you know, name what you don't, stop there. Honest scope-bounding is respected; bluffing is the single most damaging behaviour in a defense.

---

## Pocket reference — 5 things to memorise cold

If you only memorise five things from this entire document, memorise these. They will get you through 90 percent of formula questions.

1. **Plain cross-entropy** $= -\log p_y$. The baseline. *"Surprise" if the model gave low probability to the right answer.*
2. **Class weight** $\alpha_c = T / (C \cdot f_c)$, clipped at 10. *"Total tokens divided by classes times this class's count — rare classes get bigger weight."*
3. **Focal loss** $= -\alpha_y \cdot (1 - p_y)^\gamma \cdot \log p_y$ with $\gamma = 2$. *"Cross-entropy with two extras — class weights and a focusing factor that suppresses easy tokens."*
4. **F1** $= 2PR/(P+R)$. *"Harmonic mean of precision and recall — punishes weakness on either side."*
5. **The headline result.** *"Plain cross-entropy gives VICTIM F1 = 0.708; focal loss + class weights gives 0.817; gain is +11 F1 points; ablation in section 6.6."*

That sentence is the single most quotable result of the thesis. Memorise it word for word.

---

## Practice plan

You won't internalise this by reading once. The plan:

| Pass | Goal | How |
|:--|:--|:--|
| 1 | Read top to bottom | Get the structure into your head; don't worry about memorising |
| 2 | Cover the formula, read only the plain-English | Test whether you can recall the *meaning* without the symbols |
| 3 | Cover the plain-English, read only the formula | Test whether you can reconstruct the meaning from the symbols |
| 4 | Stand and deliver the 90-second slide-21 script out loud | Time yourself; aim for 80-100 seconds |
| 5 | Have a friend pick three Q&A questions at random and ask them | Practice the answering pattern under mild pressure |
| 6 | Final pass: read only Part D (this section) and the cheat sheet | Defence-eve calibration |

**Don't try to memorise verbatim except for the pocket reference and the headline sentence.** You want the *shape* of the answers in your head, not the words — verbatim memorisation produces robotic delivery that examiners can detect immediately.

---

## Worst-case fallback — when you blank

You forget what gamma is. You forget what micro F1 is. Your mind is empty. Here is the universal fallback line, delivered with calm:

> *"Let me come back to that — could you ask the next question and I'll return to this one?"*

This is **completely acceptable**. Examiners would rather you say this than watch you stumble. Then, on the *next* answer, your brain will usually reset and you can return to the first question with composure.

If you can't even produce the fallback line, the second-tier fallback is to **point at the formula** and say:

> *"Let me walk through what this term does first..."*

— and then describe the formula term by term in plain English using the BIO primer table and the universal answering pattern. You don't need to remember the specific Q to give a useful A — the structure of the answer is the same regardless of which detail they asked about.

---

## One last thing

The examiners chose your thesis to defend. They have read it. They are not trying to catch you out — they are trying to **assess whether you understand your own work**. Every formula in this document is *your* work, even the ones taken from prior literature, because you made the choices that combined them. Speak with the calm authority of someone who built the thing. The math is hard; you understood it well enough to ship a system that works. Trust that, and answer accordingly.
