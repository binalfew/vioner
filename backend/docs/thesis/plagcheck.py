#!/usr/bin/env python3
"""
Local plagiarism check: detect verbatim n-gram overlap between the
thesis body and a corpus of source documents.

Approach:
- Normalise text (lowercase, drop punctuation, collapse whitespace).
- Extract n-grams (default: n=8) from both thesis and each source.
- For each thesis n-gram that appears verbatim in a source, count it
  as a "hit" and record context.
- Report overlap percentage and the longest contiguous matches.

Note: this is an n-gram approach similar to what Turnitin does at its
core. It only finds verbatim/near-verbatim lifts; it does not detect
paraphrasing or semantic reuse. For a thesis where the proposal,
taxonomy, and annotation guidelines are the student's OWN prior work,
any overlap with those is "self-plagiarism" risk — even legitimate
reuse should be cited or rephrased to avoid triggering similarity
scores.
"""
import re
import sys
from collections import Counter
from pathlib import Path

THESIS = Path("backend/docs/thesis/thesis.md")
SOURCES = {
    "proposal":          Path("/tmp/proposal.md"),
    "taxonomy":          Path("/tmp/taxonomy.md"),
    "annotation":        Path("/tmp/annotation.md"),
    "vioner_guidelines": Path("backend/docs/VIONER_GUIDELINES.md"),
    "entity_rules":      Path("backend/docs/ENTITY_CLASSIFICATION_RULES.md"),
    "data_prep":         Path("backend/docs/DATA_PREPARATION.md"),
    "training_imps":     Path("backend/docs/TRAINING_IMPROVEMENTS.md"),
    "analysis_report":   Path("backend/docs/ANALYSIS_REPORT.md"),
}

N_GRAM = 8        # 8-word phrases — what Turnitin typically uses
MIN_REPORT = 10   # report only matches of this many consecutive words

def normalise(text: str) -> str:
    # lowercase
    text = text.lower()
    # drop punctuation, replace with space
    text = re.sub(r"[^\w\s]", " ", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def words(text: str) -> list[str]:
    return normalise(text).split()

def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def thesis_body(text: str) -> str:
    """Slice the body from Chapter 1 to References (exclude annexes)."""
    start = text.find("\n# 1. Introduction")
    end = text.find("\n# References")
    return text[start:end] if start >= 0 and end >= 0 else text

def find_runs(thesis_tokens, source_tokens_set, min_run):
    """Find contiguous spans in thesis_tokens that are present as
    consecutive n-grams in source_tokens_set."""
    n = N_GRAM
    runs = []
    i = 0
    while i <= len(thesis_tokens) - n:
        gram = tuple(thesis_tokens[i:i+n])
        if gram in source_tokens_set:
            # extend the run as far as possible
            j = i + n
            while j < len(thesis_tokens):
                nxt = tuple(thesis_tokens[j-n+1:j+1])
                if nxt in source_tokens_set:
                    j += 1
                else:
                    break
            run_len = j - i
            if run_len >= min_run:
                runs.append((i, j, run_len))
            i = j + 1
        else:
            i += 1
    return runs

def main():
    thesis_text = THESIS.read_text()
    body = thesis_body(thesis_text)
    body_tokens = words(body)

    total_grams = len(body_tokens) - N_GRAM + 1

    print(f"Thesis body: {len(body_tokens):,} words, {total_grams:,} {N_GRAM}-grams")
    print()

    union_hits = set()
    per_source = {}

    for name, path in SOURCES.items():
        if not path.exists():
            print(f"  {name}: file missing, skipping")
            continue
        src_text = path.read_text()
        src_tokens = words(src_text)
        src_grams = set(ngrams(src_tokens, N_GRAM))
        # count thesis n-grams that appear in source
        thesis_grams_set = set(ngrams(body_tokens, N_GRAM))
        hits = thesis_grams_set & src_grams
        per_source[name] = (len(hits), len(src_grams))
        union_hits |= hits

        # find contiguous runs >= MIN_REPORT words
        runs = find_runs(body_tokens, src_grams, MIN_REPORT)
        pct = 100.0 * len(hits) / total_grams if total_grams else 0
        print(f"  {name:20s}: {len(hits):4d} matching {N_GRAM}-grams "
              f"({pct:5.2f}% of thesis), longest runs:")
        for start, end, length in sorted(runs, key=lambda r: -r[2])[:5]:
            phrase = " ".join(body_tokens[start:end])
            if len(phrase) > 200:
                phrase = phrase[:200] + " ..."
            print(f"      {length} words: \"{phrase}\"")
        print()

    union_pct = 100.0 * len(union_hits) / total_grams if total_grams else 0
    print(f"=== UNION OF ALL SOURCES ===")
    print(f"  matching {N_GRAM}-grams: {len(union_hits):,} of {total_grams:,}")
    print(f"  thesis body similarity to source-doc corpus: {union_pct:.2f}%")
    print()
    print("Interpretation:")
    print("  < 1%:  excellent, no concerning overlap")
    print("  1-5%:  acceptable for typical thesis")
    print("  5-15%: review the longest runs; rephrase if needed")
    print("  > 15%: significant rewrite required")

if __name__ == "__main__":
    main()
