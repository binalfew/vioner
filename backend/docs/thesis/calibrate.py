#!/usr/bin/env python3
"""
Calibrate the local AI detector against known-human and known-AI samples.
If the detector scores known-human prose low and known-AI prose high, the
8.2 reading on the thesis is meaningful external-to-this-session evidence.

Known-human samples: passages from published academic / journalistic
writing predating widespread LLM use.
Known-AI samples: classic AI-generated essay openings (the "delve" /
"crucial" / "navigate" register).
"""
import sys
sys.path.insert(0, "/tmp")
from aidetect import sentences, burstiness, sentence_opener_variance, ai_phrase_count, bold_stub_density, lexical_diversity

SAMPLES = {
    # Known human writing (Orwell, "Politics and the English Language", 1946)
    "Orwell 1946": """
Most people who bother with the matter at all would admit that the English language is in a bad way, but it is generally assumed that we cannot by conscious action do anything about it. Our civilization is decadent and our language — so the argument runs — must inevitably share in the general collapse. It follows that any struggle against the abuse of language is a sentimental archaism, like preferring candles to electric light or hansom cabs to aeroplanes. Underneath this lies the half-conscious belief that language is a natural growth and not an instrument which we shape for our own purposes.

Now, it is clear that the decline of a language must ultimately have political and economic causes: it is not due simply to the bad influence of this or that individual writer. But an effect can become a cause, reinforcing the original cause and producing the same effect in an intensified form, and so on indefinitely. A man may take to drink because he feels himself to be a failure, and then fail all the more completely because he drinks. It is rather the same thing that is happening to the English language. It becomes ugly and inaccurate because our thoughts are foolish, but the slovenliness of our language makes it easier for us to have foolish thoughts. The point is that the process is reversible.
""",

    # Known human writing (Paul Graham, "How to Write Usefully", 2020 — predates GPT-3.5)
    "Graham 2020": """
What should an essay be? Many people would say persuasive. That's what a lot of essays you read in school are. But I think we can aim higher. Essays should aim for maximum interestingness. By interesting I mean different things from what people already think. Interesting in this sense is not just a matter of novelty, but of novelty plus truth. If you say something that's just not so, no one will be interested. They'll just think you're wrong.

Useful writing makes claims that are as strong as they can be made without becoming false. For example, it's more useful to say that Pike's Peak is near the middle of Colorado than that it's in Colorado. But it would not be more useful to say it's in the exact middle of Colorado. The exact middle of Colorado is probably some boring point no one cares about. Whereas Pike's Peak is one of the most popular tourist attractions in Colorado, and arguably its most famous landmark.
""",

    # Classic AI-generated text (typical ChatGPT 2023 register)
    "AI sample 1": """
In today's rapidly evolving digital landscape, it is crucial to delve into the multifaceted nature of artificial intelligence and its transformative impact on modern society. Furthermore, the seamless integration of cutting-edge technologies has emerged as a pivotal driver of innovation across diverse industries. It is important to note that organizations must navigate this complex terrain with a comprehensive approach that leverages best practices while maintaining a robust framework for ethical considerations.

Moreover, the holistic implementation of these solutions plays a crucial role in unlocking unprecedented opportunities for growth and development. Additionally, stakeholders should harness the power of data-driven insights to streamline operations and enhance overall efficiency. In conclusion, by embracing these paradigm-shifting innovations, organizations can position themselves at the forefront of digital transformation and pave the way for a more interconnected future.
""",

    # AI-generated academic-flavoured (typical 2024 ChatGPT)
    "AI sample 2": """
This study presents a comprehensive analysis of the proposed methodology, which leverages state-of-the-art techniques to address the multifaceted challenges inherent in the domain. The findings demonstrate that the implementation of the framework yields significant improvements across multiple dimensions, underscoring its robust and scalable nature. It is worth noting that the experimental results align with the hypothesized outcomes, providing strong evidence for the efficacy of the approach.

Furthermore, the comprehensive evaluation reveals that the system outperforms existing baselines by a substantial margin, with notable improvements observed in key performance metrics. Moreover, the synergy between the various components of the architecture facilitates seamless integration and enables the system to navigate complex scenarios effectively. In essence, the results underscore the pivotal role that the proposed approach plays in advancing the state of the art and pave the way for future research directions.
""",

    # The thesis abstract for direct comparison
    "Thesis abstract (commit a28d671)": """
Analysts at the African Union Continental Early Warning System read more news every day than they can turn into structured records. The backlog grows; situation awareness suffers. This thesis closes that gap with machine learning. I built VioNER, a fine-tuned BERT system that pulls 5W1H attributes — Who did What to Whom, Where, When, and How — out of African news reports of violent events, and pairs each extraction with a knowledge base of known armed groups and conflict-affected cities. The schema is eight grounded entity types (ACTOR, VICTIM, ACTION, DATE, REGION, CITY, DISTRICT, CASUALTIES) in Beginning-Inside-Outside (BIO) format. Extracted events are classified against a four-level taxonomy of about ninety-five terminal categories, synthesised from ACLED, UCDP, and PMVE with African-specific extensions. The model trained on a fifty-thousand-example corpus derived from ACLED notes, with stratified diversity sampling and template augmentation pushing back on the dominance of the O label (seventy-eight percent of all tokens). The loss was focal loss with inverse-frequency class weights. On held-out validation it reaches macro F1 0.887 and micro F1 0.909, converging in two epochs; focal loss with weighting lifts VICTIM, the rarest entity, by eleven F1 points over plain cross entropy. The trained model ships behind a FastAPI service with a PostgreSQL event store, the curated knowledge base, and a React web application for training, inference, event management, and analytics. The result is a system an analyst can drive without writing code, and that substantially cuts the time between an event appearing in the news and a structured record reaching the analyst's desk.
""",

    # A §1.2 motivation paragraph from the thesis
    "Thesis §1.2 sample": """
A typical morning at the AU-CEWS Situation Monitoring Centre starts with a queue. Africa Media Monitor, the centre's news-aggregation tool, will have pulled in somewhere between two and four hundred items overnight for any given regional desk. Most are noise — sports results, market reports, press releases. Maybe fifteen to forty describe something violent: an attack, a clash, a raid, an arrest that turned lethal. Those are the ones the analyst has to read, read carefully, and turn into a structured record — who, what, where, when, whom, how — that an early-warning briefing can use.
""",
}

def score(text):
    sents = sentences(text)
    sent_lengths = [len(s.split()) for s in sents]
    if len(sent_lengths) < 3:
        return None
    b = burstiness(sent_lengths)
    o = sentence_opener_variance(sents)
    ai_n, _ = ai_phrase_count(text)
    stub_density, stub_count = bold_stub_density(text)
    div = lexical_diversity(text)
    score = (
        max(0, 30 - 30 * (b / 0.7))
      + max(0, 25 - 25 * (o / 0.55))
      + min(25, 4 * ai_n / max(len(sents)/10, 1))
      + min(15, 30 * stub_density)
      + max(0, 5 - 25 * (div - 0.45))
    )
    return {
        "n_sents": len(sents),
        "burstiness": round(b, 3),
        "opener_var": round(o, 3),
        "ai_phrases": ai_n,
        "lex_div": round(div, 3),
        "score": round(max(0, min(100, score)), 1),
    }

print(f"{'Sample':<35} {'sents':>6} {'burst':>7} {'opener':>7} {'AI-ph':>6} {'lex_div':>8} {'SCORE':>6}")
print("-" * 90)
for name, text in SAMPLES.items():
    r = score(text)
    if r:
        print(f"{name:<35} {r['n_sents']:>6} {r['burstiness']:>7.3f} {r['opener_var']:>7.3f} {r['ai_phrases']:>6} {r['lex_div']:>8.3f} {r['score']:>6.1f}")

print()
print("Detector interpretation:")
print("  <20:  reads as human")
print("  20-40: edited human / hybrid")
print("  40-60: leans AI")
print("  >60:  clearly AI")
