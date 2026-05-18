#!/usr/bin/env python3
"""
Local AI-text detector. Implements the same surface signals that
commercial AI-detection tools (GPTZero, Originality.ai, Turnitin AI)
rely on. Does not match their accuracy but produces actionable
section-level scores.

Signals checked:
1. Sentence-length variance (burstiness) — humans high, AI low.
2. Sentence-length predictability — AI tends toward medium uniform.
3. AI-tell phrases — explicit list of common AI phrasings.
4. Bold-stub paragraph density (**Word.**).
5. Sentence-opener variance — AI starts sentences with "The" / "This"
   more uniformly than humans.
6. Lexical diversity (type-token ratio) per paragraph.
7. Repeated phrase bigrams (>4 occurrences = template).

Output: per-section scores and a top-flagged-passages report.
"""
import re
import sys
import statistics
from collections import Counter
from pathlib import Path

PATH = Path(sys.argv[1] if len(sys.argv) > 1 else "backend/docs/thesis/thesis.md")

# Known AI-tell phrases (broad coverage)
AI_PHRASES = [
    r"\bdelve into\b",
    r"\bdive deep\b",
    r"\bharnessing the power of\b",
    r"\bleverage\b",
    r"\bunlock\b",
    r"\bunleash\b",
    r"\bstreamline\b",
    r"\brobust\b",
    r"\bseamless(ly)?\b",
    r"\bcutting[- ]edge\b",
    r"\bstate[- ]of[- ]the[- ]art\b",
    r"\bgame[- ]changer\b",
    r"\bnavigate\b",
    r"\bin today's\b",
    r"\bin the ever[- ]evolving\b",
    r"\bin the realm of\b",
    r"\bit is important to note that\b",
    r"\bit is worth noting that\b",
    r"\bit should be noted that\b",
    r"\bit is essential to\b",
    r"\bplays a crucial role\b",
    r"\bcrucial\b",
    r"\bpivotal\b",
    r"\bparamount\b",
    r"\bmultifaceted\b",
    r"\bcomprehensive (approach|solution|framework|system)\b",
    r"\bholistic\b",
    r"\bsynergy\b",
    r"\boverarching\b",
    r"\baligned with\b",
    r"\bin conclusion,?\s",
    r"\bin summary,?\s",
    r"\bto summarise,?\s",
    r"\bto wrap up,?\s",
    r"\bMoreover,?\s",
    r"\bFurthermore,?\s",
    r"\bAdditionally,?\s",
    r"\bIn addition,?\s",
    r"\bNotably,?\s",
    r"\bSignificantly,?\s",
    r"\bIndeed,?\s",
    r"\bIn essence,?\s",
    r"\bThe present (work|thesis|research|study)\b",
    r"\bthe author('s)?\b",
    r"\bThis (paper|thesis|study|work) presents\b",
    r"\bThis (chapter|section) (introduces|reviews|presents|describes|discusses)\b",
    r"\bThe results support\b",
    r"\bThe findings suggest\b",
    r"\bThe data shows that\b",
    r"\btestament to\b",
    r"\bunderpin(ned|ning|s)?\b",
]

def normalise(text):
    return re.sub(r"\s+", " ", text).strip()

def split_into_sections(text):
    """Split markdown body into sections by ^## headings."""
    sections = []
    current = {"title": "FRONT_MATTER", "body": []}
    in_body = False
    for line in text.splitlines():
        if line.startswith("# 1. Introduction"):
            in_body = True
            sections.append(current)
            current = {"title": line.lstrip("# ").strip(), "body": []}
            continue
        if line.startswith("# References"):
            sections.append(current)
            return sections
        if line.startswith("## "):
            sections.append(current)
            current = {"title": line.lstrip("# ").strip(), "body": []}
            continue
        if in_body:
            current["body"].append(line)
    sections.append(current)
    return sections

def strip_code_and_tables(text):
    """Remove markdown code blocks and tables to score prose only."""
    out = []
    in_code = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("|") or line.startswith(":"):
            continue
        out.append(line)
    return "\n".join(out)

def sentences(text):
    text = strip_code_and_tables(text)
    text = re.sub(r"\n+", " ", text)
    # Simple sentence splitter
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    parts = [normalise(p) for p in parts if normalise(p)]
    # Drop captions and very short fragments
    parts = [p for p in parts if len(p.split()) >= 4]
    return parts

def burstiness(sent_lengths):
    """Higher = more human. Computed as stdev / mean of sentence lengths."""
    if len(sent_lengths) < 3:
        return 0
    return statistics.stdev(sent_lengths) / max(statistics.mean(sent_lengths), 1)

def sentence_opener_variance(sents):
    """How many distinct opening words / total. Higher = more human."""
    if not sents:
        return 0
    openers = [s.split()[0].lower() if s.split() else "" for s in sents]
    return len(set(openers)) / len(openers)

def ai_phrase_count(text):
    n = 0
    hits = []
    for pat in AI_PHRASES:
        for m in re.finditer(pat, text, re.IGNORECASE):
            n += 1
            hits.append((pat, m.group(0)))
    return n, hits

def bold_stub_density(text):
    stubs = re.findall(r"^\*\*[A-Z][^*]+\.\*\*", text, re.MULTILINE)
    paras = max(len([p for p in text.split("\n\n") if p.strip()]), 1)
    return len(stubs) / paras, len(stubs)

def lexical_diversity(text):
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if not words:
        return 0
    return len(set(words)) / len(words)

def score_section(sec):
    text = "\n".join(sec["body"])
    sents = sentences(text)
    sent_lengths = [len(s.split()) for s in sents]
    n_sents = len(sents)
    if n_sents < 3:
        return None
    b = burstiness(sent_lengths)
    o = sentence_opener_variance(sents)
    ai_n, ai_hits = ai_phrase_count(text)
    stub_density, stub_count = bold_stub_density(text)
    diversity = lexical_diversity(text)

    # Heuristic AI-likeness score (higher = more AI-like)
    # Calibrated so 0 = clearly human, 100 = clearly AI
    ai_score = (
        max(0, 30 - 30 * (b / 0.7))     # low burstiness penalty
      + max(0, 25 - 25 * (o / 0.55))     # low opener variance penalty
      + min(25, 4 * ai_n / max(n_sents/10, 1))  # AI phrase density
      + min(15, 30 * stub_density)       # bold-stub density
      + max(0, 5 - 25 * (diversity - 0.45))      # low lexical diversity
    )
    ai_score = max(0, min(100, ai_score))

    return {
        "title": sec["title"],
        "n_sents": n_sents,
        "burstiness": round(b, 3),
        "opener_variance": round(o, 3),
        "ai_phrases": ai_n,
        "ai_hits": ai_hits[:5],
        "bold_stub_count": stub_count,
        "lexical_diversity": round(diversity, 3),
        "ai_score": round(ai_score, 1),
    }

def main():
    text = PATH.read_text()
    sections = split_into_sections(text)
    results = []
    for sec in sections:
        s = score_section(sec)
        if s:
            results.append(s)

    results.sort(key=lambda r: -r["ai_score"])

    print(f"{'Section':<50} {'sents':>6} {'burst':>7} {'opener':>7} {'AI-ph':>6} {'stub':>5} {'div':>5} {'score':>6}")
    print("-" * 100)
    for r in results:
        title = r["title"][:48]
        print(f"{title:<50} {r['n_sents']:>6} {r['burstiness']:>7.3f} {r['opener_variance']:>7.3f} {r['ai_phrases']:>6} {r['bold_stub_count']:>5} {r['lexical_diversity']:>5.3f} {r['ai_score']:>6.1f}")

    print()
    print("=== Top 5 sections most flagged ===")
    for r in results[:5]:
        print(f"\n  [{r['ai_score']:.1f}] {r['title']}")
        print(f"      burstiness {r['burstiness']:.3f} (>0.5 healthy)")
        print(f"      opener variance {r['opener_variance']:.3f} (>0.4 healthy)")
        if r["ai_hits"]:
            print(f"      AI phrases:")
            for pat, hit in r["ai_hits"][:5]:
                print(f"        '{hit}' (matched /{pat}/)")
        if r["bold_stub_count"] > 0:
            print(f"      {r['bold_stub_count']} bold-stub paragraphs")

    print()
    overall = statistics.mean(r["ai_score"] for r in results)
    print(f"=== Overall document AI-likeness score: {overall:.1f}/100 ===")
    print("  <20:  reads as human")
    print("  20-40: reads as edited human / hybrid")
    print("  40-60: leans AI; rewrite flagged sections")
    print("  >60: clearly AI; substantial rewrite required")

if __name__ == "__main__":
    main()
