#!/usr/bin/env python3
"""Rewrite thesis.md to remove first-person pronouns (advisor comment
C625). Applies a curated list of context-aware regex substitutions
that cover the predictable surface forms ("I built X" -> "X was
built"). Anything not covered must be cleaned by a manual pass.

Usage:
    python depersonalize.py            # apply in place
    python depersonalize.py --dry-run  # print residual count without writing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "thesis.md"

# Each entry: (pattern, replacement). Patterns are applied in order;
# later patterns see the output of earlier ones. All patterns assume the
# default re flags. Word-boundary "\b" is used liberally so we do not
# accidentally chew the BIO label prefix "I-" or words like "we" inside
# "weight".

SUBS: list[tuple[str, str]] = [
    # --- Verbs of authorship / agency. "I X" -> impersonal. -----------
    (r"\bI built\b",        "VioNER was built as"),
    (r"\bI present\b",      "this thesis presents"),
    (r"\bI argue\b",        "this thesis argues"),
    (r"\bI adopt\b",        "the adopted"),
    (r"\bI use\b",          "the work uses"),
    (r"\bI take\b",         "the work takes"),
    (r"\bI chose\b",        "the choice was made for"),
    (r"\bI choose\b",       "the choice falls on"),
    (r"\bI describe\b",     "the work describes"),
    (r"\bI develop(ed)?\b", "the work develop\\1"),
    (r"\bI design(ed)?\b",  "the design was"),
    (r"\bI implement(ed)?\b", "the implementation"),
    (r"\bI assemble\b",     "the assembled"),
    (r"\bI defined\b",      "the definition was"),
    (r"\bI define\b",       "this thesis defines"),
    (r"\bI report\b",       "this chapter reports"),
    (r"\bI document\b",     "this chapter documents"),
    (r"\bI evaluate\b",     "the evaluation"),
    (r"\bI ran\b",          "the experiment ran"),
    (r"\bI run\b",          "the experiment runs"),
    (r"\bI measure\b",      "the measurement"),
    (r"\bI compare\b",      "the comparison"),
    (r"\bI tested\b",       "the tests"),
    (r"\bI test\b",         "the test"),
    (r"\bI applied\b",      "the application of"),
    (r"\bI apply\b",        "the work applies"),
    (r"\bI considered\b",   "consideration was given to"),
    (r"\bI consider\b",     "consideration is given to"),
    (r"\bI selected\b",     "the selection of"),
    (r"\bI select\b",       "the selection"),
    (r"\bI arrived at\b",   "the configuration arrived at was"),
    (r"\bI wanted\b",       "the work required"),
    (r"\bI need(ed)?\b",    "the work require\\1"),
    (r"\bI partition\b",    "the corpus is partitioned"),
    (r"\bI verified\b",     "verification"),
    (r"\bI saw\b",          "observation showed"),
    (r"\bI did not\b",      "this thesis did not"),
    (r"\bI do not\b",       "this thesis does not"),
    (r"\bI would\b",        "one would"),
    (r"\bI could\b",        "one could"),
    (r"\bI can\b",          "one can"),
    (r"\bI also\b",         "this thesis also"),
    (r"\bI then\b",         "the work then"),
    (r"\bI care about most\b", "of greatest interest here is"),
    (r"\bI care about\b",   "of interest"),
    (r"\bI land on\b",      "the selected set is"),
    (r"\bI try\b",          "the work tries"),
    (r"\bI tried\b",        "earlier attempts tried"),
    (r"\bI work through\b", "the work surveys"),
    (r"\bI offered\b",      "the offer was"),
    (r"\bI offer\b",        "the offering is"),
    (r"\bI ground\b",       "the grounding is"),
    (r"\bI fold\b",         "the folding"),
    (r"\bI mean\b",         "the meaning is"),
    (r"\bI know\b",         "it is known"),
    (r"\bI think\b",        "it is held"),

    # --- "I am ..." statements (acknowledgements / personal) ----------
    (r"\bI am deeply indebted to\b", "Deep gratitude is owed to"),
    (r"\bI am grateful\b",  "Gratitude is owed"),
    (r"\bI acknowledge\b",  "Acknowledgement is owed to"),
    (r"\bI thank\b",        "Thanks are owed to"),
    (r"\bFinally, I\b",     "Finally, the author"),

    # --- Possessive "my" ----------------------------------------------
    (r"\bto my knowledge\b",      "to the best of available knowledge"),
    (r"\bin my case\b",           "in this case"),
    (r"\bmy compromise\b",        "the compromise adopted"),
    (r"\bmy own\b",               "an original"),
    (r"\bmy first instinct\b",    "the initial instinct"),
    (r"\bmy approach\b",          "the approach taken"),
    (r"\bmy answer\b",            "the answer"),
    (r"\bmy decision\b",          "the decision"),
    (r"\bmy advisor\b",           "the advisor"),
    (r"\bmy family\b",            "the author's family"),

    # --- "for me" / "to me" -------------------------------------------
    (r"\bfor me\b",               "for the author"),
    (r"\bto me\b",                ""),
    (r"\bgave me\b",              "yielded"),
    (r"\bled me to\b",            "led to"),

    # --- "we" (single occurrence in thesis) ---------------------------
    (r"\bwe got\b",               "the system got"),

    # --- Second-pass patterns gathered from the residue --------------
    (r"\bI encode\b",            "this thesis encodes"),
    (r"\bI fine-tune\b",         "the fine-tuned model is"),
    (r"\bI most need\b",         "of greatest interest"),
    (r"\bI cite\b",              "the literature cites"),
    (r"\bI extend\b",            "this thesis extends"),
    (r"\bI address\b",           "this thesis addresses"),
    (r"\bI picked\b",            "the choice fell on"),
    (r"\bI pulled\b",            "the data were pulled from"),
    (r"\bI reverted\b",          "the change was reverted"),
    (r"\bI committed to\b",      "were committed to"),
    (r"\bI learned\b",           "the work surfaced"),
    (r"\bI came to\b",           "emerged"),
    (r"\bI almost\b",            "the alternative almost"),
    (r"\bI inspected\b",         "inspection of"),
    (r"\bI measured\b",          "measurements were taken of"),
    (r"\bI cared about\b",       "of greatest interest"),
    (r"\bI kept\b",              "the work retained"),
    (r"\bI sat down with\b",     "an inspection was conducted on"),
    (r"\bI set out to answer\b", "this thesis set out to answer"),
    (r"\bI set aside\b",         "set aside"),
    (r"\bI trained\b",           "training was performed"),
    (r"\bI never had to\b",      "there was never a need to"),
    (r"\bI had to\b",            "it was necessary to"),
    (r"\bI almost picked\b",     "the alternative almost selected was"),
    (r"\bI'll\b",                "this chapter will"),
    (r"\bI spoke with\b",        "consulted during user testing"),
    (r"\bI ordered\b",           "the items have been ordered"),
    (r"\bI have ordered\b",      "they have been ordered"),
    (r"\bIn October 2025 my\b",  "In October 2025 the"),
    (r"\bI have in mind\b",      "envisaged"),
    (r"\bI have\b",              "the work has"),
    (r"\bI almost\b",            "the close alternative was"),
    (r"\bif I extend\b",         "if the work were extended"),
    (r"\bif I were starting over\b", "if the work were to start over"),

    (r"\bI " + r"(?P<v>am|was|were)\b", r"the author \g<v>"),

    # --- "saved me", "led me", "matters to me", "for me" etc. --------
    (r"\bsaved me\b",       "saved the author"),
    (r"\bled me\b",         "led the author"),
    (r"\bsurprised me\b",   "was surprising"),
    (r"\bme to\b",          "necessary to"),
    (r"\bcosts me\b",       "costs the work"),
    (r"\bgive me\b",        "produce"),
    (r"\bgives me\b",       "produces"),
    (r"\btells me\b",       "tells us"),  # awkward; manual sweep may revisit
    (r"\bwhat (?:tells|told) me\b", "what was apparent"),

    # --- "my" residues -----------------------------------------------
    (r"\bmy F1\b",             "the F1"),
    (r"\bmy project\b",        "this project"),
    (r"\bmy taxonomy\b",       "the taxonomy"),
    (r"\bmy system\b",         "the system"),
    (r"\bmy four-level\b",     "the four-level"),
    (r"\bmy runs\b",           "the runs reported here"),
    (r"\bmy validation\b",     "the validation"),
    (r"\bmy use case\b",       "the use case"),
    (r"\bmy classification\b", "the classification"),

    # --- Possessive that the user-facing text should retain ----------
    # Lines in the UAT questionnaire (Annex F) intentionally use first
    # person because they are the survey instrument shown to participants.
    # They are left as-is by this script.
]

# Patterns we want to make sure we DON'T touch:
NO_TOUCH = [
    re.compile(r"\bI[-\.]"),         # BIO labels: I-ACTOR, I.e
    re.compile(r"\bI/O\b"),          # IO scheme
    re.compile(r"\bI\b(?=[A-Z]{2,})"),
]


def apply(text: str) -> str:
    for pat, repl in SUBS:
        text = re.sub(pat, repl, text)
    return text


def count_pronouns(text: str) -> dict[str, int]:
    counts = {}
    for w in ("I", "we", "my", "our", "me", "us"):
        pat = rf"(^|[^A-Za-z-]){w}(?=[^A-Za-z0-9-])"
        counts[w] = len(re.findall(pat, text))
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = TARGET.read_text(encoding="utf-8")
    before = count_pronouns(text)
    new_text = apply(text)
    after = count_pronouns(new_text)

    print("First-person pronoun counts:")
    print(f"  before: {before}")
    print(f"  after:  {after}")
    delta = sum(before.values()) - sum(after.values())
    print(f"  removed: {delta}")
    print(f"  residue: {sum(after.values())}")

    if not args.dry_run:
        TARGET.write_text(new_text, encoding="utf-8")
        print(f"  wrote: {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
