# VioNER Defense — Concepts and Jargon Explained for a Beginner

**This document assumes zero ML background.** If a term in the thesis or in the other study docs feels opaque, look it up here. Every concept gets:

1. **In one sentence** — the simplest possible definition
2. **The analogy** — a concrete real-world parallel you can hold in your head
3. **Worked example** — with actual numbers
4. **In the thesis** — where it appears
5. **What a panellist means** — when they use this word during your defense

Read top to bottom once. Then keep it open next to `formulas_explained.md` — if the math doc gets opaque, drop back here for the analogy first.

---

## How to use this document

| Pass | Purpose |
|:--|:--|
| **Read 1** — full pass | Get every term into your head with its analogy |
| **Read 2** — Section A and Section C | The most important concepts: training (A) and evaluation (C) |
| **Defence eve** — the cheat sheet at the very end | One-line versions for last-minute recall |

The document is organised by what you encounter as the model runs end-to-end:

- **Section A** — The big picture (what is NER, what goes in, what comes out)
- **Section B** — How the model thinks (BERT, transformer, attention, softmax)
- **Section C** — How the model learns (loss, gradient, training)
- **Section D** — The loss functions (CE, focal, class weights, label smoothing)
- **Section E** — How we measure quality (F1, precision, recall, TP/FP/FN)
- **Section F** — Training procedure terms (epoch, batch, val loss, overfitting)
- **Section G** — Other thesis terms (Cohen's κ, Likert, hyperparameters, …)
- **Section H** — One-line cheat sheet at the very end

---

# Section A · The big picture — what is this thesis even doing?

## A1. NER — Named Entity Recognition

**In one sentence.** NER is the task of looking at a sentence and labelling each piece of text with what *kind of thing* it refers to — a person, a date, a location, etc.

**The analogy.** Imagine reading a newspaper article with a yellow highlighter, a pink highlighter, and a green highlighter. You highlight every person's name in yellow, every location in pink, every date in green. At the end of the article you have a structured set of *who, where, when* — that's NER. The model just does it automatically and with categories you've defined ahead of time.

**Worked example.** Input sentence:

> *"Al-Shabaab attacked a convoy near Mogadishu on Tuesday, killing 12 soldiers."*

NER output:

| Span | Label |
|:--|:--|
| Al-Shabaab | ACTOR |
| convoy | VICTIM |
| Mogadishu | CITY |
| Tuesday | DATE |
| attacked | ACTION |
| 12 soldiers | CASUALTIES |

**In the thesis.** Chapter 1 introduces NER as the central technical task. The whole system is built around it.

**What a panellist means.** When they say "the NER component" they mean the trained BERT model that produces these per-token entity labels.

---

## A2. Entity / Entity type / Entity span

**In one sentence.** An entity is a meaningful chunk of text (a person's name, a place, etc.); the entity *type* is what category it falls into; the entity *span* is the exact start-and-end position of that chunk.

**The analogy.** In the highlighted article above, *"Al-Shabaab"* is an **entity**. **ACTOR** is its **entity type**. The **span** is the positions of its first and last characters in the article.

**Worked example.** In the sentence above:

| Entity | Type | Span (token positions) |
|:--|:--|:--|
| "Al-Shabaab" | ACTOR | tokens 1-3 |
| "convoy" | VICTIM | token 6 |
| "12 soldiers" | CASUALTIES | tokens 10-11 |

**In the thesis.** §4.3 defines the 8 entity types (ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES).

**What a panellist means.** When they say "span" they mean the exact text region (start and end), not just the label. "Span-level F1" means scoring counts only when both the span boundaries AND the type are correct.

---

## A3. BIO encoding (B-, I-, O)

**In one sentence.** BIO encoding is how we mark each token with a label: **B-** for the *beginning* of an entity span, **I-** for an *inside* (continuation) token of the same span, and **O** for *outside* any entity.

**The analogy.** Imagine writing in the margin of a book. Next to the first word of every entity name, you write "B-ENTITY_TYPE". Next to every continuation word of the same entity, you write "I-ENTITY_TYPE". Next to every word that's not part of any entity, you write "O". That's BIO encoding.

**Worked example.** "Al-Shabaab attacked a convoy" with sub-word tokenisation:

| Token | Label |
|:--|:--|
| Al | B-ACTOR |
| - | I-ACTOR |
| Shabaab | I-ACTOR |
| attacked | B-ACTION |
| a | O |
| convoy | B-VICTIM |

Reading the labels back: B-ACTOR followed by two I-ACTORs = a single ACTOR span spanning three tokens. B-ACTION (alone) = a one-token ACTION span. O = not an entity. B-VICTIM = a one-token VICTIM span.

**In the thesis.** §4.3 explains BIO encoding and why it was chosen over BIOES (which has extra E- and S- tags).

**What a panellist means.** When they say "BIO labels" they mean the 17 possible tags (O plus B-/I- for each of the 8 entity types).

---

## A4. Token / Tokenisation / WordPiece

**In one sentence.** A token is the smallest unit the model processes; tokenisation is the act of splitting text into tokens; WordPiece is BERT's specific tokenisation algorithm that breaks words into sub-word pieces.

**The analogy.** Imagine you're feeding text into a paper shredder. The paper shredder doesn't shred letter by letter (too fine-grained) and not whole-sentence-at-a-time (too coarse). It shreds at a specific granularity. BERT's WordPiece shredder produces "tokens" — usually whole words, but unusual or long words get broken into sub-word pieces.

**Worked example.**

| Input text | WordPiece tokens |
|:--|:--|
| "attacked" | ["attacked"] *(one token — common word)* |
| "Al-Shabaab" | ["Al", "-", "Sha", "##baab"] *(four tokens — uncommon name)* |
| "Mogadishu" | ["Mo", "##gad", "##ishu"] *(three sub-word tokens)* |

The `##` prefix marks "this is a continuation of the previous token, not a new word." So "Sha" + "##baab" reassembles into "Shabaab".

**In the thesis.** §5.4 discusses tokenisation; §4.3 covers BIO encoding under sub-word tokenisation (the subtle case where labels have to propagate from the first sub-word to its continuations).

**What a panellist means.** When they say "token" they almost always mean a sub-word piece, not a whole word. When they say "sequence length 128" they mean 128 sub-word tokens, which is roughly 80-90 words.

---

# Section B · How the model thinks

## B1. BERT (Bidirectional Encoder Representations from Transformers)

**In one sentence.** BERT is a neural network that has already been "pre-trained" on billions of words of English text, so it knows English in a general way; we then "fine-tune" it on our specific NER task.

**The analogy.** Imagine you hire someone who has already read the entire English Wikipedia and BookCorpus. They have a general understanding of language — grammar, vocabulary, how sentences are structured. You then give them a one-week training course on your specific task (extracting violent-event entities from African news). They become specialised much faster than someone hired off the street who'd have to learn English first.

That generalist who already knows English is **BERT**. The one-week specialised training is **fine-tuning**.

**Worked example.** BERT-base-cased has **110 million parameters** (knobs the model can adjust). Initially these knobs are set to values that capture general English. Fine-tuning makes small adjustments to those knobs over 2 epochs of training, specialising the model for the African violent-event NER task while preserving the general English knowledge.

**In the thesis.** §5.4 documents the choice of `bert-base-cased` as the backbone. The case-sensitive variant matters because African armed-group names ("JNIM", "RSF") use capitalisation that the uncased variant would lose.

**What a panellist means.** "BERT" is sometimes the specific model, sometimes the family of models. "BERT-NER" usually refers to BERT + a classification head fine-tuned for entity recognition.

---

## B2. Transformer / Attention

**In one sentence.** A transformer is a type of neural network architecture; "attention" is the specific mechanism transformers use that lets each word look at every other word in the sentence simultaneously.

**The analogy.** Imagine you're reading the sentence *"The bank was robbed near the river."* When you read "bank", you need to decide whether it means *financial institution* or *side of a river*. You glance at "river" later in the sentence and that helps you understand "bank" means the side-of-the-river one.

That cross-reference — looking at other words to understand the current word — is **attention**. A transformer does this for every word simultaneously, in parallel, using mathematical operations.

**Worked example.** When processing the word "Goma" in *"fighting in Goma between rebels and the army"*, the model's attention mechanism lets the representation of "Goma" be informed by:
- "fighting" (tells the model it's an event location)
- "rebels" and "army" (tells the model this is a conflict context)
- "in" (tells the model "Goma" is a location, not an actor)

All these contextual pulls happen at once, in parallel, inside the transformer.

**In the thesis.** §2.3 covers transformer architecture as background. Most of the time the thesis treats BERT as a black box; the transformer details aren't central to the contribution.

**What a panellist means.** "Self-attention", "multi-head attention", "transformer block" — all refer to the internal machinery of BERT. You don't need to derive the math; you need to know that attention is what lets BERT understand each word in context.

---

## B3. Logits

**In one sentence.** Logits are the raw, unnormalised scores that BERT produces — one per possible BIO label per token — before softmax converts them into probabilities.

**The analogy.** Imagine a panel of 17 judges (one per BIO label) each scoring a contestant from -10 to +10. The raw scores are positive or negative, large or small, and they don't sum to anything specific. Those raw judge scores are **logits**.

**Worked example.** For the token "Mogadishu", BERT might produce these 17 logits (illustrative):

| BIO label | Logit |
|:--|--:|
| O | -2.1 |
| B-ACTOR | -1.5 |
| I-ACTOR | -3.2 |
| B-VICTIM | -1.8 |
| ... | ... |
| **B-CITY** | **+4.2** ← highest |
| I-CITY | +0.3 |
| ... | ... |

B-CITY has the highest raw score (+4.2). The model is leaning strongly toward "this token is the beginning of a city name".

**In the thesis.** Discussed in §2.3 (background) and §5.4 (model architecture).

**What a panellist means.** "Logits" = raw scores before softmax. "Logit-space" = working with these raw scores directly without converting to probabilities.

---

## B4. Softmax

**In one sentence.** Softmax is a mathematical operation that converts the 17 raw logits into 17 probabilities that sum to 1 (i.e. 100%).

**The analogy.** Take those 17 judge scores from B3. Soft-max says *"OK, let me convert these raw scores into a percentage share of belief in each label."* It uses an exponential function to make positive scores dominant and negative scores tiny, then normalises so the 17 percentages sum to 100%.

The result for our "Mogadishu" example might be:

| BIO label | Softmax probability |
|:--|--:|
| O | 0.001 |
| B-ACTOR | 0.001 |
| ... | ... |
| **B-CITY** | **0.94** ← 94% probability |
| B-REGION | 0.04 |
| ... | ... |

These all sum to 1. The model is "94% sure this is B-CITY".

**In the thesis.** Implicit throughout — softmax is the standard final layer for classification. `formulas_explained.md` §1 walks through the math.

**What a panellist means.** "Softmax output" = the probability distribution. "Argmax over softmax" = pick the highest-probability label.

---

## B5. Confidence score

**In one sentence.** The confidence score is just the highest softmax probability — how sure the model is about its top prediction.

**The analogy.** When a weather forecaster says "70% chance of rain tomorrow", that 70% is their confidence. Higher = more sure. Lower = more uncertain.

**Worked example.** From the Mogadishu example, the confidence on the B-CITY prediction is 0.94 = 94% confident.

If a different token's softmax came out spread more evenly (top label at 0.40, second at 0.35, third at 0.15), the confidence would be 0.40 — the model is uncertain. Low-confidence predictions get filtered out by the per-category threshold in §4.7.

**In the thesis.** Used in §4.7 for confidence-based filtering; reported per entity in the UI for the analyst.

**What a panellist means.** "Confidence" almost always refers to this softmax-max probability. It's the model's self-assessment of certainty.

---

# Section C · How the model learns

## C1. Loss / Loss function

**In one sentence.** Loss is a single non-negative number that says "how wrong was the model on this example"; the loss function is the formula used to compute it.

**The analogy.** Imagine a student taking a multiple-choice test. After each question, the teacher tells them whether they were right and how confident they should have been in the correct answer. A confident-wrong answer is a big mistake. A correct-and-confident answer is a small mistake (almost zero). An uncertain answer in either direction is a medium mistake.

The number the teacher writes next to each question — measuring "how off was the student" — is the **loss**. Smaller loss = better performance. Zero loss = perfect.

**Worked example.** For one token where the gold label is B-VICTIM:

- If the model gave 0.95 probability to B-VICTIM → loss is **0.05** (small — almost right)
- If the model gave 0.50 probability to B-VICTIM → loss is **0.69** (medium — uncertain)
- If the model gave 0.10 probability to B-VICTIM → loss is **2.30** (large — confidently wrong)

**In the thesis.** §2.4 introduces loss functions; §5.5 documents which loss VioNER actually uses. `formulas_explained.md` Part A walks through the math.

**What a panellist means.** "Loss" = the optimisation target. The whole point of training is to minimise loss across the training set.

---

## C2. Cross-entropy (CE) loss

**In one sentence.** Cross-entropy is the standard classification loss, defined as *minus the log of the probability the model gave to the true class*.

**The analogy.** Cross-entropy is sometimes called "surprise". Think of it this way:

- If the model expected the right answer (high probability), it isn't surprised → small loss.
- If the model didn't expect the right answer (low probability), it's very surprised → big loss.

The bigger the surprise, the bigger the loss. The model is being trained to be less and less surprised by the gold labels over time.

**Worked example.** Using the natural logarithm (the math doesn't matter — just intuition):

| Model's probability on the true label | $-\log$ of that probability = CE loss |
|--:|--:|
| 1.00 (perfect) | 0.00 |
| 0.90 | 0.11 |
| 0.50 | 0.69 |
| 0.10 | 2.30 |
| 0.01 | 4.61 |

Notice: as the probability gets closer to zero, the loss grows without bound. The model is punished severely for being confident in the wrong answer.

**In the thesis.** §2.4 defines it; §6.6 ablation shows it's the **baseline** that focal loss + class weights improve on.

**What a panellist means.** "CE", "cross-entropy", "log loss" — all the same thing. The standard, unmodified classification loss that most NER models train with by default.

---

## C3. Gradient

**In one sentence.** The gradient is a list of numbers — one per weight in the model — telling you, **for each weight individually**, *"changing this weight slightly would change the loss by this much, in this direction."* The gradient is the bridge between *"we know the loss"* and *"we know how to reduce it."*

**The analogy.** Imagine you have a control panel with **110 million dials** — one dial per weight in BERT. After each training batch, a single number lights up on the panel: the **wrongness score** = the loss. You want to lower that number.

The gradient is a printout that appears next to the panel saying, for each of the 110 million dials:
> *"Turning this dial slightly UP would change the wrongness score by **X** (in some direction)."*

- If X is **positive** → turning UP makes things WORSE → so we should turn DOWN to reduce the loss
- If X is **negative** → turning UP makes things BETTER → so we should turn UP to reduce the loss
- The bigger the magnitude of X, the more impactful that dial is on the loss

The gradient turns *"the loss is 5.0"* (vague — you know you're wrong but not how to fix it) into *"to reduce the loss, turn dial #1 down by 2 units, dial #2 up by 1.5, dial #3 down by 0.5, ..."* repeated for every weight. That's a 110-million-entry recipe for reducing the loss.

**Worked example with 3 weights.** Forget 110 million for a moment. Imagine a tiny model with only **3 weights**: w₁, w₂, w₃. After one training batch:

- The model produces predictions
- Compared to gold labels, the **loss = 5.0**
- Backpropagation (next concept) computes the gradient:

| Weight | Gradient value | What it means |
|:--|--:|:--|
| w₁ | **+2.0** | "If you increase w₁ by 1 unit, the loss goes UP by 2." → DECREASE w₁ to reduce loss |
| w₂ | **−1.5** | "If you increase w₂ by 1 unit, the loss goes DOWN by 1.5." → INCREASE w₂ to reduce loss |
| w₃ | **+0.5** | "Increasing w₃ raises the loss slightly." → decrease w₃ a little |

The gradient by itself doesn't change anything — it just produces this list of *"which way each weight should move, and how strongly"*. Gradient descent (next concept) is what actually uses this list to update the weights.

**Connection to loss.** *The gradient is the answer to: given that we know the loss, what should we do about each weight to reduce it?* Without the gradient, we'd know we're wrong but have no idea how to fix it. With the gradient, we have a 110-million-dimensional recipe for nudging the loss downward.

**In the thesis.** Conceptually throughout Chapter 5 (training); never written out by hand because PyTorch handles it automatically.

**What a panellist means.** "Gradient signal" = the magnitude of the gradient on a particular set of weights. "Gradient drowned out" = rare-class tokens produce small gradients that get washed out by common-class tokens' larger gradients — this is the imbalance problem focal loss and class weights address.

---

## C4. Gradient descent and Backpropagation

These are **two distinct things that always work together**:

- **Backpropagation** = how you **compute** the gradient.
- **Gradient descent** = how you **use** the gradient to actually update the weights.

> Think of it as: **backpropagation is the GPS that calculates the route; gradient descent is the act of driving along that route.**

### C4a. Backpropagation

**In one sentence.** Backpropagation is the calculus trick that computes the gradient by working **backward** from the loss through every layer of the network — figuring out, for each weight, how much it contributed to the final loss.

**The analogy.** Imagine a factory assembly line that produces a product. At the end of the line, a quality inspector gives the product a **defect score** — the loss. You want to figure out which factory worker contributed how much to the defect, so you can give each worker corrective instructions.

You can't see each worker's contribution directly. But you can trace BACKWARD from the defective product:

- Look at the final station: *"how much of the defect came from this station?"*
- Then the previous station: *"how much of THAT came from this station's input?"*
- Walk all the way back to the raw materials (the weights).

At the end you have a list saying *"worker #1 contributed +2.0 to the defect; worker #2 contributed -1.5; ..."*. That's the gradient. The walking-backward procedure is **backpropagation**.

In a neural network: the forward pass goes **input → layer 1 → layer 2 → ... → output → loss**. The backward pass goes **loss → ... → layer 2 → layer 1 → weights**. Hence *back-propagation*.

**Worked example.** PyTorch handles backprop automatically. In code:

```python
loss = compute_loss(model_output, gold_labels)   # forward pass
loss.backward()                                   # BACKPROP — fills in the gradient
                                                   # for every weight automatically
```

After `loss.backward()` runs, every one of the 110 million weights has its gradient sitting next to it (PyTorch stores it in `weight.grad`). You never write the backprop math yourself; PyTorch generates it from the forward-pass structure.

### C4b. Gradient descent

**In one sentence.** Gradient descent is the algorithm of taking a small step in the direction **opposite** to the gradient — because moving opposite the gradient is what reduces the loss.

**The analogy.** Carry the mountain analogy: the gradient tells you which direction is UPHILL on the loss landscape (positive = uphill). To go DOWNHILL (toward lower loss), you walk **opposite** the gradient. The size of your step is controlled by the **learning rate** — small enough that you don't overshoot the valley, large enough that you make progress.

The full update rule:
$$w_{\text{new}} = w_{\text{old}} \;-\; \text{learning rate} \;\times\; \text{gradient}$$

The minus sign is the "go opposite" part. The learning rate is the step size.

**Worked example.** Continuing the 3-weight model from C3. We computed the gradients = [+2.0, −1.5, +0.5]. With learning rate 0.1:

| Weight | Old value | Gradient | Update = LR × gradient | New value |
|:--|--:|--:|--:|--:|
| w₁ | (say) 0.50 | +2.0 | 0.1 × 2.0 = +0.20 | 0.50 − 0.20 = **0.30** |
| w₂ | (say) 0.30 | −1.5 | 0.1 × (−1.5) = −0.15 | 0.30 − (−0.15) = **0.45** |
| w₃ | (say) 0.40 | +0.5 | 0.1 × 0.5 = +0.05 | 0.40 − 0.05 = **0.35** |

After these updates, when we run the next batch through the (slightly modified) model and compute the loss, it should be slightly lower than 5.0 — say 4.8. Then we backprop again, compute a new gradient, take another descent step. Repeat across 5,000 batches (2 epochs × 2,500 batches/epoch) and the loss settles to 0.0074 (the val-loss minimum from Table 6.5).

For 110 million weights the procedure is **exactly the same** — just much more dimensional. PyTorch handles both backprop and the gradient-descent step automatically.

### Putting it all together — the full training loop

This is what happens on every single batch of training. **Notice how the four concepts — loss, gradient, backprop, gradient descent — chain together:**

| Step | What happens | Concept | Connection to loss |
|:-:|:--|:--|:--|
| 1 | Batch flows through the model → predictions | Forward pass | (produces inputs for loss) |
| 2 | Predictions compared to gold labels → one number | **Loss** (C1, C2) | *"How wrong was the model?"* |
| 3 | Walk backward through the network, computing how each weight contributed | **Backpropagation** | *"How do I reduce the loss?"* — gives the gradient |
| 4 | Each weight moves slightly opposite to its gradient | **Gradient descent** | *"Take one step toward lower loss"* |
| 5 | Loss for the NEXT batch is slightly lower | (back to step 1) | The loop continues |

After ~5,000 repetitions of steps 1-4 (two epochs), the weights have settled to values that produce low loss. **That's what "training" actually is — repeated execution of this loop.**

A way to read the loss/gradient/backprop/descent chain in one sentence:

> *"The **loss** says how wrong we are. **Backpropagation** uses the loss to compute the **gradient** — a per-weight recipe for reducing the loss. **Gradient descent** applies that recipe by nudging each weight slightly opposite its gradient. Repeat ~5,000 times across two epochs and the model converges."*

**In the thesis.** Discussed in standard training-loop context throughout Chapter 5.

**What a panellist means.** "Backprop" = the gradient computation step. "Gradient descent step" = one weight-update (one batch's worth). "End-to-end training" = the gradient flows all the way from the loss back through every layer of BERT, including the pretrained ones, so all 110M weights are updatable. "Frozen layers" = some layers' gradients are zeroed out so those layers don't update (VioNER does NOT freeze any layers — it fine-tunes end-to-end).

---

## C5. Optimiser / AdamW

**In one sentence.** The optimiser is the algorithm that actually adjusts the weights using the gradient; AdamW is the specific optimiser VioNER uses — an improved version of plain gradient descent with adaptive step sizes.

**The analogy.** Plain gradient descent takes a step of the same size in every direction. AdamW is smarter — it keeps track of past gradients and adjusts each weight's step size based on history (weights with consistent gradients get bigger steps; weights with noisy gradients get smaller steps).

**Worked example.** Plain gradient descent with learning rate 5×10⁻⁵: every weight gets nudged by *gradient × 5×10⁻⁵*.

AdamW with learning rate 5×10⁻⁵: every weight gets nudged by *gradient × adapted-step-size × 5×10⁻⁵*. The adapted-step-size varies per weight based on history. Result: faster, more stable convergence.

**In the thesis.** §5.5 documents the optimiser; backup B1 of the slides shows the configuration.

**What a panellist means.** "AdamW" = the specific optimiser; "Adam" is the older version; "weight decay 0.01" is the AdamW-specific regularisation parameter.

---

# Section D · The loss functions — the ones that actually appear in the thesis

## D1. Focal loss

**In one sentence.** Focal loss is cross-entropy with a "focusing factor" that automatically pays less attention to tokens the model already gets right, so the optimiser concentrates on the hard ones.

**The analogy.** Imagine a teacher in a class of 100 students. Two are struggling; 98 already understand. Normal teaching (= cross-entropy) gives equal time to all 100 → the strugglers fall further behind. Focal teaching gives near-zero attention to the 98 who get it and almost all attention to the 2 strugglers → the strugglers catch up.

The mathematical "focusing factor" $(1 - p_y)^\gamma$ does exactly that automatically:

- For a token the model is already 99% correct on, the factor is $(1 - 0.99)^2 = 0.0001$. The loss is multiplied by 0.0001 → essentially zero attention.
- For a token the model is only 50% correct on, the factor is $(1 - 0.50)^2 = 0.25$. The loss is multiplied by 0.25 → still substantial attention.

The optimiser ends up spending its time on the harder tokens — which is where the rare entities live.

**Worked example.** Same five-token sentence "Boko Haram killed civilians today" used earlier:

| Token | True label | $p_y$ | CE loss | Focal factor $(1-p_y)^2$ | Focal loss |
|:--|:--|--:|--:|--:|--:|
| Boko | B-ACTOR | 0.85 | 0.163 | 0.023 | **0.004** |
| Haram | I-ACTOR | 0.90 | 0.105 | 0.010 | **0.001** |
| killed | B-ACTION | 0.45 | 0.799 | 0.303 | **0.242** |
| civilians | B-VICTIM | 0.40 | 0.916 | 0.360 | **0.330** |
| today | B-DATE | 0.95 | 0.051 | 0.003 | **0.000** |

#### How the table was calculated — focal loss is just multiplication

The rightmost column **is the product of the two columns to its left**. In formula form:

$$\text{Focal Loss} \;=\; \underbrace{(1 - p_y)^\gamma}_{\text{focal factor}} \;\times\; \underbrace{(-\log p_y)}_{\text{CE loss}}$$

Focal loss is cross-entropy with one extra multiplier in front. With $\gamma = 2$ that multiplier is $(1 - p_y)^2$. Walk through one row to see the arithmetic:

**Hard token — "killed" (B-ACTION, $p_y = 0.45$):**

1. CE loss = $-\log(0.45) = 0.799$ → moderate, because the model is uncertain
2. Focal factor = $(1 - 0.45)^2 = 0.55^2 = 0.303$
3. Focal loss = $0.799 \times 0.303 = \mathbf{0.242}$

**Easy token — "today" (B-DATE, $p_y = 0.95$):**

1. CE loss = $-\log(0.95) = 0.051$ → tiny, because the model is already 95% right
2. Focal factor = $(1 - 0.95)^2 = 0.05^2 = 0.003$
3. Focal loss = $0.051 \times 0.003 = \mathbf{0.000153} \approx 0.000$

Notice what happened in the easy case: the CE was already small (0.051), and the focal factor *then multiplied it by 0.003*, making it essentially zero. That's the focusing effect — confident-correct tokens get suppressed almost entirely. The hard tokens (killed, civilians) keep most of their CE loss because their focal factors are close to 1.

**The dimmer-switch intuition.** Think of the focal factor as a dimmer switch sitting between cross-entropy and the optimiser. When $p_y$ is high, the dimmer is nearly closed → that token barely affects training. When $p_y$ is low, the dimmer is nearly open → that token contributes fully. Cross-entropy alone treats easy and hard tokens equally; focal loss dims the easy ones via the multiplier and lets the hard ones through at full volume.

**With class weights, it's just one more multiplication.** The full production loss adds the per-class weight $\alpha_y$ as a third multiplicand:

$$\text{Production Focal Loss} \;=\; \alpha_y \;\times\; (1 - p_y)^\gamma \;\times\; (-\log p_y)$$

So "civilians" (B-VICTIM) with class weight $\alpha_{\text{VICTIM}} = 10$ would have a production loss of $10 \times 0.330 = 3.30$ — ten times more impactful on the gradient than the focal-loss-only version. Rare-class tokens dominate training under the production loss because their $\alpha_y$ is much larger than the common classes'.

#### What the table shows operationally

Under plain cross-entropy, the easy tokens (Boko, Haram, today) contributed 0.163 + 0.105 + 0.051 = 0.319 to the loss. Under focal loss, those same tokens contribute almost nothing (0.004 + 0.001 + 0.000 ≈ 0.005). The optimiser is now spending almost all its capacity on the hard tokens (killed, civilians).

**In the thesis.** §2.4 introduces focal loss; §5.5 documents the production configuration; §6.6 shows the ablation.

**What a panellist means.** "Focal loss with γ=2" — γ is the focusing parameter (2 is the literature default). "Focal loss helps with class imbalance" — yes, because the rare-class tokens are usually the hard ones, so focal loss directs attention to them.

---

## D2. Class weights / Inverse-frequency class weights

**In one sentence.** Class weights are per-category multipliers on the loss — rare classes get a big multiplier so they aren't drowned out by common ones; "inverse-frequency" just means the weight is proportional to 1 divided by how often the class appears.

**The analogy.** Imagine an election with 7,800 voters from one city and 5 voters from a tiny village. One-person-one-vote gives the city overwhelming control. To balance the system, you could give each villager 1,560 votes (so their voice equals 7,800 city votes ÷ 5 villagers).

Class weights are exactly that re-weighting. A class with fewer tokens gets a bigger per-token weight, so the optimiser pays attention to it proportionally.

**Worked example.** Inverse-frequency formula: $\alpha_c = T / (C \cdot f_c)$ where T = total tokens, C = number of classes, $f_c$ = how many tokens of class c.

With T = 2,000,000, C = 17, and:

| Class | Token count $f_c$ | Weight $\alpha_c$ | After clip at 10 |
|:--|--:|--:|--:|
| O | 1,560,000 | 0.075 | 0.075 |
| B-DATE | 32,000 | 3.68 | 3.68 |
| B-ACTOR | 48,000 | 2.45 | 2.45 |
| B-ACTION | 10,000 | 11.76 | **10.0** (clipped) |
| B-VICTIM | 5,500 | 21.39 | **10.0** (clipped) |

Result: VICTIM tokens contribute about $10 / 0.075 ≈ 130×$ more loss-weight than O tokens. Rare classes are no longer drowned out.

**In the thesis.** §2.4 (Eq. 4), §5.5 (implementation), §6.6 (ablation).

**What a panellist means.** "Class weights", "inverse-frequency weighting", "α_c" — same thing. The cap-at-10 detail prevents the rarest classes from destabilising training.

---

## D3. Label smoothing

**In one sentence.** Label smoothing replaces the hard one-hot label (1.0 on the right class, 0.0 on every other) with a soft version (0.9 on the right class, 0.1 spread across the others) — a regularisation trick that prevents the model from becoming overconfident.

**The analogy.** Instead of telling a student *"the answer is C and every other option is 100% wrong"*, you tell them *"the answer is C with 90% confidence, but A, B, D each have a 3.3% chance of being defensible too."* The student becomes less dogmatic and produces better-calibrated confidence later.

**Worked example.** For a token with true label B-VICTIM and 17 classes total:

- One-hot target: B-VICTIM = 1.0, every other class = 0.0
- Smoothed target with β=0.1: B-VICTIM = 0.9, each of the other 16 classes = 0.1/16 = **0.00625**

The model is trained against the smoothed target, which prevents the logits from growing arbitrarily large.

**In the thesis.** §2.4 (Eq. 3), §5.5 (implementation), §6.4 (tested separately — marginal effect).

**What a panellist means.** "Label smoothing β=0.1" — β is the smoothing strength; 0.1 is the conventional choice from Szegedy et al. 2016 (the Inception paper).

---

## D4. Cross-entropy vs Focal Loss vs Focal+Weights — what's the difference?

This is the comparison Table 6.8 makes. Each loss is a variation on the same theme.

| Loss | What it does | Used in VioNER? |
|:--|:--|:--|
| **Plain cross-entropy** | Computes $-\log p_y$ for each token; sums equally across all tokens | **No** — used only as the ablation baseline |
| **Weighted cross-entropy** | Plain CE multiplied by per-class weights so rare classes count more | **No** — also an ablation comparison |
| **Focal loss alone** | Plain CE multiplied by $(1-p_y)^\gamma$ so easy tokens count less | **No** — also an ablation comparison |
| **Focal loss + class weights + label smoothing** | All three modifications applied together | **YES** — this is the production loss |

The §6.6 ablation runs the same training pipeline four times, swapping only the loss function. The combination wins on every rare-entity F1.

**Defense-day version.** *"The production loss is focal loss with inverse-frequency class weights and label smoothing. The ablation in section 6.6 compares this against three alternatives — plain cross-entropy, weighted cross-entropy, focal alone — and shows the combination beats every alternative on the rare entities by 7-11 F1 points without hurting any common entity."*

---

# Section E · How we measure quality

## E1. True Positive (TP) / False Positive (FP) / False Negative (FN)

**In one sentence.** When you compare predictions to gold labels: **TP** = the model predicted an entity and was right; **FP** = the model predicted an entity that wasn't really there; **FN** = a real entity the model missed entirely.

**The analogy.** Imagine an email spam filter:

- **TP** — the filter flags an email as spam, and it really was spam ✓
- **FP** — the filter flags an email as spam, but it was a legitimate email (false alarm) ✗
- **FN** — the filter doesn't flag an email, but it really was spam (missed spam) ✗
- **TN** (true negative) — the filter doesn't flag it, and it really wasn't spam ✓

For NER, the four buckets are the same. TN doesn't matter for entity metrics because almost all tokens are TN (correctly identified as O).

**Worked example.** Validation set has 100 VICTIM gold spans. The model predicts 90 spans as VICTIM. Of those 90:

- 82 match an actual gold VICTIM → **TP = 82**
- 8 don't match anything → **FP = 8** (false alarms — model predicted VICTIM where there wasn't one)
- The 18 gold VICTIMs the model didn't find → **FN = 18** (missed)

**In the thesis.** §2.5 defines them; every results table is built from these three counts.

**What a panellist means.** "TPs", "false positives", "missed entities (FN)" — all the same vocabulary across NER, medical testing, spam filtering. Same concepts, same names.

---

## E2. Precision

**In one sentence.** Of all the entities the model predicted, what fraction were correct.

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$

**The analogy.** Of all the emails your spam filter flagged, what fraction were really spam? If most flagged emails were real spam, your filter has high precision. If half your flagged emails were legitimate (false alarms), your filter has poor precision — you have to keep checking your spam folder.

**Worked example.** With TP=82 and FP=8 from above:

$$\text{Precision} = \frac{82}{82 + 8} = \frac{82}{90} = \mathbf{0.911}$$

Read: *"When the model said VICTIM, it was correct 91% of the time."*

**In the thesis.** Every per-entity table has a Precision column.

**What a panellist means.** "Precision-favourable" = the model trades fewer false alarms for more missed entities. "Per-entity precision" = computed separately for each entity type.

---

## E3. Recall

**In one sentence.** Of all the entities that actually exist (in the gold labels), what fraction did the model recover.

$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

**The analogy.** Of all the real spam emails arriving in your inbox, what fraction did your filter catch? If most spam got flagged, your filter has high recall. If half the spam slipped through to your inbox, your filter has poor recall.

**Worked example.** With TP=82 and FN=18 from above:

$$\text{Recall} = \frac{82}{82 + 18} = \frac{82}{100} = \mathbf{0.820}$$

Read: *"Of the 100 actual victims in the validation set, the model found 82."*

**In the thesis.** Every per-entity table has a Recall column.

**What a panellist means.** "Recall-favourable" = trade fewer missed entities for more false alarms. "Recall on VICTIM" = how thoroughly the model finds VICTIM entities.

---

## E4. F1 score

**In one sentence.** F1 is a single number that combines precision and recall by taking their harmonic mean — punishing weakness on either side.

$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

**The analogy.** F1 is like a movie review score that drops if either the acting OR the plot is bad. A movie with great acting (precision=1.0) but terrible plot (recall=0.1) doesn't get a 55/100; it gets an 18/100 (the F1 of 1.0 and 0.1). The harmonic mean is the harsh judge that says "weakness anywhere hurts the score badly".

**Why the harsh judge is the right judge for NER.** A model with perfect precision but terrible recall would miss almost everything (useless for an analyst). A model with perfect recall but terrible precision would drown the analyst in false alarms (also useless). You need both. F1 ensures you don't game one at the cost of the other.

**Worked example.** With precision=0.911 and recall=0.820:

$$\text{F1} = 2 \times \frac{0.911 \times 0.820}{0.911 + 0.820} = \frac{1.494}{1.731} = \mathbf{0.864}$$

Read: *"Combined precision-recall quality for VICTIM = 0.864."*

**In the thesis.** Every per-entity table has an F1 column. The headline metrics on every slide (macro F1 0.887, micro F1 0.909) are aggregated F1s.

**What a panellist means.** "F1 of 0.85+" is strong for NER. "Harmonic mean" = the specific way F1 combines precision and recall.

---

## E5. Macro F1 vs Micro F1

**In one sentence.** Macro F1 averages the per-entity F1s as equals; Micro F1 pools all the TP/FP/FN counts across entities and computes one F1 from the pool — which weights common entities more.

**The analogy.** Imagine you're grading a multi-subject exam with Maths (100 questions), History (50 questions), and Art (10 questions).

- **Macro grading** — Average the three subject percentages. Maths counts as much as Art even though Art is much smaller.
- **Micro grading** — Pool all the questions across subjects, then compute one overall percentage. Maths dominates because it has the most questions.

Same idea for F1:

- **Macro F1** treats each entity type as equally important.
- **Micro F1** treats each individual gold span as equally important — so high-support entities (DATE, CITY, ACTOR) dominate.

**Worked example.** From thesis Table 6.7:

| Entity | F1 |
|:--|--:|
| DATE | 0.956 |
| CITY | 0.934 |
| ACTOR | 0.923 |
| REGION | 0.891 |
| CASUALTIES | 0.885 |
| ACTION | 0.866 |
| DISTRICT | 0.826 |
| VICTIM | 0.817 |

**Macro F1** = simple average = $(0.956 + 0.934 + ... + 0.817) / 8 = \mathbf{0.887}$

**Micro F1** = computed from pooled counts = $\mathbf{0.909}$ (higher, because DATE, CITY, ACTOR — the high-support entities — also have the highest F1)

**In the thesis.** §2.5 defines both; §6.4 reports both.

**What a panellist means.** "Macro F1 is the right balance number" — yes, it punishes weak rare-entity performance. "Micro F1 estimates throughput" — yes, it estimates overall extraction quality across a batch.

---

## E6. Confusion matrix

**In one sentence.** A confusion matrix is a grid showing, for each pair (gold class, predicted class), how often that confusion happened — useful for diagnosing *what kind of errors* the model makes.

**The analogy.** Imagine a teacher tallying student errors on a multiple-choice exam. For each question with correct answer X, the teacher counts how many students answered A, B, C, D. The result is a grid showing "students who should have answered X often confused it with Y". That grid is the confusion matrix.

**Worked example.** Thesis Table 6.11 (location-type confusion):

| Gold \\ Predicted | CITY | REGION | DISTRICT |
|:--|--:|--:|--:|
| CITY | (correct) | 0.05 | 0.04 |
| REGION | 0.08 | (correct) | 0.06 |
| DISTRICT | 0.07 | 0.09 | (correct) |

Read row 3: when the true label was DISTRICT, the model mistakenly predicted CITY 7% of the time and REGION 9% of the time. The DISTRICT row has the most confusion — DISTRICT is the hardest entity for the model.

**In the thesis.** Table 6.11 in §6.11.

**What a panellist means.** "Confusion matrix off-diagonals" = the error counts. "Diagonal omitted because it's the correct predictions, not errors" — exactly what Table 6.11 does.

---

# Section F · Training procedure terms

## F1. Epoch

**In one sentence.** An epoch is one full pass through the training data — the model sees every training example exactly once during one epoch.

**The analogy.** Reading the entire textbook from cover to cover. One epoch = one read of the whole book. Multiple epochs = re-reading the book multiple times so the model's understanding deepens.

**Worked example.** VioNER has 40,000 training examples. With batch size 16, each epoch processes 40,000 / 16 = **2,500 batches**. The optimiser updates the weights 2,500 times during one epoch.

VioNER converges at **epoch 2** — the model only needs two passes through the data because BERT was already pretrained on Wikipedia.

**In the thesis.** §5.4, §6.3. Table 6.5 reports per-epoch metrics.

**What a panellist means.** "2 epochs" = the model saw the training data twice. "Per-epoch loss" = the average loss across one full pass.

---

## F2. Batch / Mini-batch / Batch size

**In one sentence.** A batch is a small group of training examples processed together; "batch size" is how many examples are in one group; VioNER uses batch size 16.

**The analogy.** Instead of reading the textbook one word at a time (impossibly slow) or all at once (memory overload), you read it one chapter at a time. The chapter is the batch. Batch size 16 means 16 sentences per chapter.

Why batches? Because GPUs and modern hardware process many examples in parallel efficiently. Batch size 16 means BERT does its 110-million-parameter computation on 16 sentences simultaneously, then averages the gradients across those 16 to update the weights.

**Worked example.** With 40,000 training examples and batch size 16:
- 1 batch = 16 examples
- 1 epoch = 2,500 batches
- 2 epochs = 5,000 batches = 5,000 weight updates

**In the thesis.** §5.4 (training config); batch size 16 chosen because of memory constraints on the M2 Max hardware.

**What a panellist means.** "Mini-batch" = standard usage; just means "batch". "Batch normalisation" = a different concept (a layer-normalisation technique). Don't confuse them.

---

## F3. Train loss vs Validation loss

Already covered extensively in `experimental_results.md` Part 3. Recap:

**In one sentence.** Train loss = loss computed on data the model sees during training (drops monotonically). Val loss = loss computed on held-out data the model never sees during training (drops while learning, rises when overfitting).

**The analogy.** Train loss = how well a student does on their practice tests (always improves with practice). Val loss = how well that student does on a fresh exam they haven't seen (improves while learning, then plateaus or worsens if they memorise practice questions).

**Worked example.** From Table 6.5:

| Epoch | Train loss | Val loss | Reading |
|:--:|--:|--:|:--|
| 1 | 0.0231 | 0.0118 | Both dropping fast — learning |
| 2 | 0.0094 | 0.0074 | Val at minimum — best checkpoint |
| 3 | 0.0061 | 0.0079 | Val rising — overfitting starts |

**In the thesis.** Table 6.5 in §6.3.

**What a panellist means.** "The train/val curves diverge" = overfitting is happening. "Val loss plateaus" = the model has learned what it can.

---

## F4. Overfitting / Underfitting

**In one sentence.** Overfitting = the model has memorised training-specific patterns that don't generalise to new data; underfitting = the model hasn't learned enough yet to do well on anything.

**The analogy.**

- **Underfitting** — a student who hasn't studied enough. They do poorly on practice tests AND on the real exam.
- **Good fit** — a student who has studied just enough. They do well on practice tests AND on the real exam.
- **Overfitting** — a student who memorised the practice tests so well they ace those, but bomb the real exam because the questions are different.

**Worked example.** VioNER at epoch 1 = underfitting (val loss 0.0118 is still relatively high). At epoch 2 = good fit (val loss 0.0074, the minimum). At epoch 5 = overfitting (val loss 0.0102, rising while train loss continues to fall).

**In the thesis.** §6.3, §6.13.

**What a panellist means.** "Overfit to the training data" = the model memorised, didn't generalise. "Generalisation gap" = train loss minus val loss; bigger gap = more overfitting.

---

## F5. Early stopping

**In one sentence.** Early stopping = automatically halting training when validation loss stops improving, so the model doesn't continue into the overfitting regime.

**The analogy.** A study coach who watches the student's mock-exam scores and stops them from studying further the moment scores stop improving — because beyond that point, more study would only cause memorisation, not learning.

**Worked example.** VioNER's early-stopping rule: "stop training if validation loss hasn't improved in 2 consecutive epochs." Applied to Table 6.5:

- Epoch 1 → val loss 0.0118
- Epoch 2 → val loss 0.0074 (improved — best so far)
- Epoch 3 → val loss 0.0079 (worse — patience used: 1)
- Epoch 4 → val loss 0.0089 (worse — patience used: 2) → **STOP**

The training run reverts to the epoch-2 checkpoint as the final model.

**In the thesis.** §5.4 (config), Table 6.5 (dynamics).

**What a panellist means.** "Patience 2" = wait 2 epochs of no improvement before stopping. "Best checkpoint" = the epoch where val loss was lowest.

---

## F6. Hyperparameters

**In one sentence.** Hyperparameters are the configuration choices you make about how to train the model — learning rate, batch size, number of epochs, loss function parameters — as opposed to the model weights, which are learned during training.

**The analogy.** When baking a cake, the *ingredients* are like the training data (raw input). The *cake* is like the trained model (the output). The *recipe* — oven temperature, baking time, how long to mix the batter — is like the hyperparameters. You choose those before baking. The cake learns to be a cake during baking, but you didn't choose what the cake's molecules become; you chose the recipe.

**Worked example.** VioNER's hyperparameters include:

| Hyperparameter | Value | What it controls |
|:--|:--|:--|
| Learning rate | 5×10⁻⁵ | How big each gradient-descent step is |
| Batch size | 16 | How many examples per batch |
| Max epochs | 10 | Upper limit on how long to train |
| Focal loss γ | 2.0 | How aggressively to suppress easy tokens |
| Class weight cap | 10 | Prevents the rarest classes from destabilising training |
| Warmup ratio | 0.1 | Fraction of training where learning rate ramps up |

The model has 110 million **parameters** (the weights). It has roughly a dozen **hyperparameters**. The parameters are learned; the hyperparameters are chosen.

**In the thesis.** §5.4, backup B1.

**What a panellist means.** "Hyperparameter tuning" = trying different values to find the best. "Grid search" = systematically trying combinations. "Default from the literature" = the value other papers have used.

---

# Section G · Other thesis terms

## G1. Cohen's Kappa (κ)

**In one sentence.** Cohen's κ measures how often two annotators agreed on the same labels, corrected for the agreement you'd expect by chance.

**The analogy.** Two doctors looking at the same X-ray. If both say "pneumonia" you have agreement — but they might agree just by random luck. κ asks: "would they agree this much by accident? No? Then their agreement is real."

κ = 0 means agreement no better than chance. κ = 1 means perfect agreement. κ = 0.78 (VioNER's number) means substantial agreement on the Landis-Koch scale.

**Worked example.** Two annotators labelling 200 documents. They agree on 92% of tokens (observed agreement). The chance agreement (what they'd agree on by random labelling, given the class distribution) is around 64%. Then:

$$\kappa = \frac{0.92 - 0.64}{1 - 0.64} = \frac{0.28}{0.36} = \mathbf{0.78}$$

**In the thesis.** §5.2 (annotation), slide 24 (data quality).

**What a panellist means.** "Substantial agreement" = κ between 0.61 and 0.80 on the Landis-Koch scale. "Almost-perfect agreement" = κ above 0.80.

---

## G2. Validation set / Held-out data

**In one sentence.** The validation set is a slice of the data the model never sees during training, so we can honestly measure how well it performs on unseen examples.

**The analogy.** When studying for a test, you don't grade yourself on the practice problems you already solved (you'd cheat). You grade yourself on a fresh mock exam. The mock exam is the validation set — held aside specifically so the measurement is honest.

**Worked example.** VioNER's 50,000 examples → 80/20 split → 40,000 train + **10,000 validation**. The model only ever sees the 40,000 during training. Every F1 number reported is on the 10,000 validation set.

**In the thesis.** §5.3, §6.13.

**What a panellist means.** "Held-out", "validation split", "out-of-sample evaluation" — all the same thing.

---

## G3. Fine-tuning / Transfer learning / Pretraining

**In one sentence.** Pretraining is when BERT was originally trained on Wikipedia by Google; fine-tuning is when this thesis took that pretrained BERT and trained it further on the specific NER task; transfer learning is the general name for this two-stage approach.

**The analogy.** A medical generalist (= pretrained BERT) who has already studied general medicine extensively. Then you give them additional specialist training in cardiology (= fine-tuning on VioNER's task). They become a cardiologist much faster than a fresh student would, because they already know anatomy, physiology, and general clinical patterns.

**Worked example.** Pretraining of bert-base-cased: months of GPU time at Google on billions of tokens. Fine-tuning by this thesis: 2 epochs over 40,000 sentences on an M2 Max box (~40 minutes). The fine-tuning is cheap because the pretrained model already knows English.

**In the thesis.** §2.3, §5.4.

**What a panellist means.** "Off-the-shelf pretrained model" = use BERT's pretrained weights as the starting point. "Frozen vs unfrozen layers" = whether all 110M weights get updated during fine-tuning or only some. VioNER uses end-to-end fine-tuning (all weights update).

---

## G4. Likert scale

**In one sentence.** A Likert scale is a survey response option from "strongly disagree" (1) to "strongly agree" (5), used in user-acceptance testing to capture how participants felt about specific statements.

**The analogy.** When you fill out a survey at a restaurant — "On a scale of 1 to 5, how was your food?" — that's a Likert scale.

**Worked example.** UAT statement: *"The 5W1H structuring was clear."*

- 1 = strongly disagree
- 2 = disagree
- 3 = neutral
- 4 = agree
- 5 = strongly agree

VioNER's UAT: mean score on this statement = **4.6**. That's "agree to strongly agree" on average — the participants found the 5W1H structure clear.

**In the thesis.** §6.10, Table 6.10.

**What a panellist means.** "Likert mean 4.6 with std 0.5" = average response of 4.6 with low spread (most participants agreed). "Likert response is ordinal, not interval" = the spaces between 1, 2, 3, 4, 5 aren't necessarily equal — but for practical comparison purposes, means are still informative.

---

## G5. Checkpoint / Model weights / Parameters

**In one sentence.** A checkpoint is a saved snapshot of the model's weights (parameters) at a specific point during training, so you can reload the model later.

**The analogy.** Saving a video game. You can come back to that exact game state any time. The "save file" is the checkpoint.

**Worked example.** VioNER saves a checkpoint at the end of every epoch:

- `models/run_20260204/epoch_01/` — 4 GB of weights from after epoch 1
- `models/run_20260204/epoch_02/` — 4 GB of weights from after epoch 2 (the best checkpoint)
- `models/run_20260204/epoch_03/` — 4 GB of weights from after epoch 3

At inference time, the system loads the best checkpoint (`epoch_02/`) — those are the 110 million weight values the model uses to predict labels.

**In the thesis.** §5.4.

**What a panellist means.** "Trained checkpoint" = the saved weights. "Model parameters" = same as model weights. "110M parameters" = the model has 110 million adjustable numbers.

---

## G6. Inference / Forward pass

**In one sentence.** Inference = running the trained model on a new article to produce predictions; forward pass = one specific computation of "input → output" through the network.

**The analogy.** Once the student has graduated, asking them an exam question (= inference). The mental computation they do to come up with the answer (= forward pass). No more learning happens at inference time; the student just applies what they already know.

**Worked example.** Analyst pastes one article. The system:

1. Tokenises it (~3 ms)
2. Runs the forward pass through BERT (~110 ms — most of the time)
3. Decodes the spans (~2 ms)
4. KB lookup + taxonomy (~25 ms)
5. Persists to DB (~10 ms)

Total ~150 ms. That's one inference. No gradient computation, no weight updates — just the forward pass plus post-processing.

**In the thesis.** §4.7, §5.6, §6.8.

**What a panellist means.** "Inference time" = how long it takes to predict on one input. "Inference latency" = same thing. "Forward pass" = the specific computation through the layers.

---

## G7. Span-level vs Token-level evaluation

**In one sentence.** Token-level scoring counts every token; span-level scoring counts only complete entities — and span-level is the harsher and operationally-meaningful one.

**The analogy.** Imagine grading a fill-in-the-blank exercise where the answer is "New York City":

- **Token-level** — gives partial credit for getting "New" right, "York" right, "City" right (3 out of 3 = 100%)
- **Span-level** — requires getting "New York City" exactly correct as a unit (1 right or 0 right)

If the student writes "York City" (missed "New"), token-level scoring gives 67% credit. Span-level scoring gives 0%.

**Worked example.** Gold span = "at least 12 civilians". Model predicts "12 civilians":

- Token-level — model got 2 of 4 tokens right (50% token-level accuracy)
- Span-level — model produced a different span; both type and exact boundaries are needed for a match. Strict span-level scoring counts this as: FP on "12 civilians" + FN on "at least 12 civilians". **Span-level F1 contribution: zero.**

VioNER reports span-level F1 because that's what the analyst experiences — a partially-correct span doesn't save them much time, since they still have to edit.

**In the thesis.** §2.5 (definitions); span-level used throughout Chapter 6.

**What a panellist means.** "Strict span-level" = exact-match scoring. "Relaxed span" = partial-credit scoring (1.5-2 F1 points higher than strict). VioNER reports strict for honesty.

---

# Section H · Cheat sheet — one line per concept

For last-minute recall the night before. If you can fluently produce the right-hand column for each term, you're ready.

## The big picture

| Term | One-line definition |
|:--|:--|
| **NER** | The task of labelling each token with what kind of entity it represents |
| **Entity span** | A specific text region (start, end) plus its entity type |
| **BIO** | Labelling scheme: B-X = first token of an X entity, I-X = continuation, O = outside any entity |
| **Token** | The smallest unit the model processes (a sub-word piece) |
| **WordPiece** | BERT's specific tokenisation algorithm |

## How the model thinks

| Term | One-line definition |
|:--|:--|
| **BERT** | A pretrained transformer; the backbone model VioNER fine-tunes |
| **Transformer** | The neural-network architecture BERT is built on; "attention" is its key trick |
| **Attention** | The mechanism that lets each token's representation be informed by every other token |
| **Logits** | Raw model scores before softmax |
| **Softmax** | Converts logits into probabilities that sum to 1 |
| **Confidence** | The highest softmax probability — how sure the model is of its top prediction |

## How the model learns

| Term | One-line definition |
|:--|:--|
| **Loss** | A single number measuring how wrong the model is on one example |
| **Loss function** | The formula that computes the loss |
| **Cross-entropy (CE)** | Standard classification loss: $-\log p_y$ — the surprise metric |
| **Gradient** | A per-weight list: "how would the loss change if I nudged this weight?" — one entry per weight |
| **Gradient descent** | Read the gradient → move every weight slightly *opposite* to it (= toward lower loss) → repeat |
| **Backpropagation** | The calculus trick that computes the gradient by walking *backward* from the loss through every layer |
| **Optimiser** | Algorithm that uses the gradient to update weights; VioNER uses AdamW |
| **Learning rate** | The step size of gradient descent; 5×10⁻⁵ here |

## The loss functions

| Term | One-line definition |
|:--|:--|
| **Plain cross-entropy** | $-\log p_y$ — the baseline loss; what generic NER uses |
| **Class weights** | Per-class multipliers on the loss; rare classes get bigger multipliers |
| **Inverse-frequency weights** | Class weights proportional to 1/class-frequency; clipped at 10 |
| **Focal loss** | Cross-entropy with a $(1-p_y)^\gamma$ focusing factor that suppresses easy tokens |
| **γ (gamma)** | Focal loss's focusing parameter; VioNER uses γ=2 |
| **Label smoothing** | Replace one-hot targets with soft ones (0.9 on true class, 0.1 spread); β=0.1 |

## Quality metrics

| Term | One-line definition |
|:--|:--|
| **TP** | True positive — model predicted entity correctly |
| **FP** | False positive — model predicted an entity that wasn't there |
| **FN** | False negative — real entity the model missed |
| **Precision** | TP / (TP + FP) — fraction of predictions that were correct |
| **Recall** | TP / (TP + FN) — fraction of real entities recovered |
| **F1** | Harmonic mean of precision and recall — punishes one-sided performance |
| **Macro F1** | Average per-entity F1; weights every entity type equally |
| **Micro F1** | F1 from pooled TP/FP/FN counts; weights by entity frequency |
| **Token accuracy** | Fraction of correctly-labelled tokens; misleading because 78% are O |
| **Confusion matrix** | Grid showing gold-vs-predicted error counts |
| **Span-level scoring** | Strict-match scoring requiring exact span boundaries AND type |

## Training procedure

| Term | One-line definition |
|:--|:--|
| **Epoch** | One full pass through the training data |
| **Batch** | A small group of examples processed together; VioNER batch size = 16 |
| **Train loss** | Loss on training examples; rolling average over a changing model; dropout on |
| **Val loss** | Loss on held-out validation examples; computed with model frozen + dropout off |
| **Generalisation gap** | Val loss minus train loss; positive and growing = overfitting |
| **Overfitting** | Model memorises training-specific patterns; val loss rises while train falls |
| **Underfitting** | Model hasn't learned enough; both losses still high |
| **Early stopping** | Halt training when val loss stops improving (patience = 2) |
| **Checkpoint** | A saved snapshot of model weights at a specific epoch |
| **Hyperparameters** | Configuration choices for training (lr, batch size, etc.) — not learned by training |
| **Fine-tuning** | Taking a pretrained model and training it further on a specific task |
| **Pretraining** | The original Wikipedia/BookCorpus training of BERT (done by Google) |
| **Transfer learning** | The general two-stage approach: pretrain + fine-tune |

## Other thesis terms

| Term | One-line definition |
|:--|:--|
| **Cohen's κ** | Inter-annotator agreement corrected for chance; VioNER = 0.78 (substantial) |
| **Validation set** | The held-out 10,000 examples the model never sees during training |
| **Held-out** | Data set aside from training; used only for evaluation |
| **Inference** | Running the trained model on new data to produce predictions |
| **Forward pass** | One computation from input through the layers to output |
| **Likert scale** | 1-5 survey response from strongly disagree to strongly agree |
| **Model parameters** | The 110 million weights inside BERT — learned during training |
| **Span** | A specific text region from token i to token j |
| **Augmentation** | Synthetic training examples generated from templates |
| **Stratified sampling** | Sampling that preserves or rebalances class proportions |
| **Ablation** | An experiment that turns one ingredient off to measure its individual contribution |

---

# One last calibration note

You don't need to derive any of this on a whiteboard during the defense. You need to be able to **state the term, give the analogy, and connect it to the contribution claim**. That's the level the panel is testing — fluency, not derivation.

When in doubt, fall back on the analogy:

- F1 = movie review score that drops for bad acting OR bad plot
- Cross-entropy = surprise
- Focal loss = spotlight on struggling students
- Class weights = giving small towns more votes
- Gradient = downhill direction in fog
- Epoch = one read of the textbook
- Validation set = the mock exam
- BERT = a generalist who already knows English
- Overfitting = memorising practice answers
- Cohen's κ = two doctors agreeing on the X-ray, beyond chance

Speak with the calm authority of someone who has used these words to explain the thesis to a non-specialist friend over coffee. That's the energy level the defense wants. The math is there in the formulas doc when they push deeper; the analogies are here when they want clarity.
