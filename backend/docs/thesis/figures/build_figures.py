#!/usr/bin/env python3
"""Render the formal thesis figures requested by the advisor (C418,
C438, C453, C747) using Graphviz. Outputs are PNG files placed next
to this script.

Usage:
    cd backend/docs/thesis/figures
    python build_figures.py
"""

from __future__ import annotations

from pathlib import Path

from graphviz import Digraph


HERE = Path(__file__).resolve().parent


def _render(dot: Digraph, stem: str, dpi: str = "120") -> None:
    out = HERE / stem
    dot.attr(dpi=dpi)
    dot.render(filename=stem, directory=HERE, format="png", cleanup=True)
    print(f"  wrote {out.with_suffix('.png').name}")


def build_architecture() -> None:
    """Figure 4.1: High-level architecture (C418)."""
    g = Digraph("architecture", format="png")
    g.attr(rankdir="TB", splines="ortho", nodesep="0.5", ranksep="0.55",
           fontname="Helvetica", fontsize="11")
    g.attr("node", shape="box", style="rounded,filled",
           fillcolor="#F4F6FA", color="#3D4F7C", fontname="Helvetica",
           fontsize="11")
    g.attr("edge", color="#3D4F7C", fontname="Helvetica", fontsize="10")

    g.node("ui", "Presentation layer\nReact + TypeScript\n(training, inference,\n"
                  "events, analytics, KB)")
    g.node("api", "Service layer\nFastAPI + Pydantic\n"
                   "/api/training  /api/inference  /api/events\n"
                   "/api/analytics  /api/kb  /api/auth  /api/system",
           fillcolor="#EAF2E3", color="#3D6A2E")
    g.node("ner", "NER component\nFine-tuned BERT\n(in-process)",
           fillcolor="#FDF2E0", color="#A66A1A")
    g.node("kb", "Knowledge base\nArmed groups, locations,\nweapons (in-process)",
           fillcolor="#FDF2E0", color="#A66A1A")
    g.node("db", "Persistence layer\nPostgreSQL 16\n(events, runs, accounts)",
           fillcolor="#F2E6F2", color="#6B2A6B")

    g.edge("ui", "api", label="  HTTPS / JSON  ")
    g.edge("api", "ner", label="  predict  ")
    g.edge("api", "kb",  label="  validate  ")
    g.edge("api", "db",  label="  store / query  ")

    _render(g, "architecture")


def build_process_flow() -> None:
    """Figure 4.2: End-to-end processing pipeline + Figure 4.3 process
    flow replacement for the sequence diagram (C438). Top-to-bottom
    flow with two-column wrapping so it fits an A4 portrait page."""
    g = Digraph("process_flow", format="png")
    g.attr(rankdir="TB", splines="ortho", nodesep="0.35", ranksep="0.4",
           fontname="Helvetica", fontsize="11")
    g.attr("node", shape="box", style="rounded,filled", fillcolor="#F4F6FA",
           color="#3D4F7C", fontname="Helvetica", fontsize="11",
           width="2.4", height="0.55", fixedsize="true")
    g.attr("edge", color="#3D4F7C", fontname="Helvetica", fontsize="10")

    steps = [
        ("s1",  "1. Analyst submits article text"),
        ("s2",  "2. Tokenise (WordPiece)"),
        ("s3",  "3. BERT NER forward pass"),
        ("s4",  "4. BIO decode to spans"),
        ("s5",  "5. Confidence filtering"),
        ("s6",  "6. 5W1H grouping"),
        ("s7",  "7. KB validation (actor, location)"),
        ("s8",  "8. Taxonomy classification"),
        ("s9",  "9. Persist event (PostgreSQL)"),
        ("s10", "10. Render record in UI"),
    ]
    for sid, label in steps:
        g.node(sid, label)
    for (a, _), (b, _) in zip(steps, steps[1:]):
        g.edge(a, b)

    _render(g, "process_flow")


# Taxonomy nodes shared between the §4.4 summary figure and the Annex B
# full figure. The (label, [children]) tuples form a tree.
TAXONOMY = {
    "Political Violence": [
        "Rebellion / Armed Insurgency",
        "Terrorism",
        "Coup and Regime Change",
        "Election Violence",
        "Political Repression",
    ],
    "Criminal Violence": [
        "Organised Crime Violence",
        "Armed Robbery / Banditry",
        "Kidnapping for Ransom",
        "Criminal Gang Violence",
    ],
    "Communal Violence": [
        "Ethnic / Tribal Conflict",
        "Religious Violence",
        "Resource-Based Conflict",
        "Pastoralist-Farmer Clashes",
    ],
    "State Violence against Civilians": [
        "Extrajudicial Killings",
        "State Repression of Protests",
        "Mass Atrocities by State Forces",
        "Forced Displacement by State",
        "Arbitrary Detention",
    ],
}

LEAVES_ANNEX = {
    "Rebellion / Armed Insurgency": ["Armed Clash", "Ambush", "Rebel Attack", "Forced Recruitment"],
    "Terrorism": ["Bombing", "Armed Assault", "Hostage-Taking", "Assassination", "Soft Target Attack"],
    "Coup and Regime Change": ["Military Coup", "Coup-Related Violence", "Assassination"],
    "Election Violence": ["Campaign Violence", "Voting Day Violence", "Post-Election Violence"],
    "Political Repression": ["Protest Suppression", "Targeted Killing", "Mass Arrest"],

    "Organised Crime Violence": ["Gang Warfare", "Assassination", "Violence against Law Enforcement"],
    "Armed Robbery / Banditry": ["Highway", "Bank / Business", "Home Invasion", "Cattle Raiding"],
    "Kidnapping for Ransom": ["Individual / Family", "Maritime / Piracy"],
    "Criminal Gang Violence": [],

    "Ethnic / Tribal Conflict": ["Ethnic Clash", "Ethnic Massacre", "Ethnic Revenge Attack"],
    "Religious Violence": ["Sectarian Violence", "Attack on Religious Community", "Site Desecration"],
    "Resource-Based Conflict": ["Land", "Water", "Mining / Resource Extraction"],
    "Pastoralist-Farmer Clashes": ["Grazing", "Cattle Raiding (Communal)", "Revenge Raid"],

    "Extrajudicial Killings": ["Summary Execution", "Enforced Disappearance", "Torture Death"],
    "State Repression of Protests": ["Shooting of Protesters", "Violent Dispersal"],
    "Mass Atrocities by State Forces": ["Massacre", "Ethnic Cleansing"],
    "Forced Displacement by State": ["Violent Eviction", "Village Burning"],
    "Arbitrary Detention": ["Mass Arrest"],
}

ROOT = "Violent Events Taxonomy"

LEVEL1_COLOURS = {
    "Political Violence":               ("#EAF2E3", "#3D6A2E"),
    "Criminal Violence":                ("#FDF2E0", "#A66A1A"),
    "Communal Violence":                ("#F2E6F2", "#6B2A6B"),
    "State Violence against Civilians": ("#FBE0E0", "#962525"),
}


def _build_taxonomy(stem: str, include_leaves: bool) -> None:
    """LR layout: root on the left, then Level 1, then Level 2,
    then (optionally) Level 3 leaves. This keeps the figure within
    portrait-page width and grows vertically as more leaves are added."""
    g = Digraph(stem, format="png")
    g.attr(rankdir="LR", splines="ortho", nodesep="0.12", ranksep="0.6",
           fontname="Helvetica", fontsize="10")
    g.attr("node", shape="box", style="rounded,filled", fillcolor="#F4F6FA",
           color="#3D4F7C", fontname="Helvetica", fontsize="10",
           margin="0.10,0.05")
    g.attr("edge", color="#3D4F7C", arrowsize="0.55")

    g.node("root", ROOT, fillcolor="#3D4F7C", fontcolor="white",
           color="#1F2A4A", fontname="Helvetica Bold", fontsize="11")

    for l1, l2_list in TAXONOMY.items():
        l1_id = f"l1_{abs(hash(l1)) % 10**8}"
        fill, border = LEVEL1_COLOURS[l1]
        g.node(l1_id, l1, fillcolor=fill, color=border,
               fontname="Helvetica Bold")
        g.edge("root", l1_id)
        for l2 in l2_list:
            l2_id = f"l2_{abs(hash(l2 + l1)) % 10**8}"
            g.node(l2_id, l2, fillcolor=fill, color=border)
            g.edge(l1_id, l2_id)
            if include_leaves:
                for leaf in LEAVES_ANNEX.get(l2, []):
                    leaf_id = f"l3_{abs(hash(leaf + l2 + l1)) % 10**8}"
                    g.node(leaf_id, leaf, fillcolor="white", color=border,
                           fontsize="9")
                    g.edge(l2_id, leaf_id)

    _render(g, stem)


def build_taxonomy_summary() -> None:
    """Figure 4.5: §4.4 summary taxonomy figure (C453). Level 1 and 2
    only."""
    _build_taxonomy("taxonomy_summary", include_leaves=False)


def build_taxonomy_annex() -> None:
    """Figure B.1: Annex B full taxonomy figure (C747). Includes
    Level-3 leaf categories."""
    _build_taxonomy("taxonomy_annex", include_leaves=True)


def build_methodology_cycle() -> None:
    """Defense-deck figure: design-science cycle with four nodes
    (Build, Evaluate, Learn, Refine) arranged in a feedback loop.
    Used on the methodology slide of the defense presentation."""
    g = Digraph("methodology", format="png", engine="circo")
    g.attr(splines="curved", normalize="true", nodesep="0.4",
           fontname="Helvetica", fontsize="13", bgcolor="white",
           pad="0.4", size="6,4!", ratio="fill")
    g.attr("node", shape="circle", style="filled",
           fontname="Helvetica Bold", fontsize="14",
           width="1.4", fixedsize="true", penwidth="2")
    g.attr("edge", color="#1F2A4A", fontname="Helvetica", fontsize="11",
           fontcolor="#5A6378", penwidth="2.2", arrowsize="0.9")

    g.node("build",  "Build",    fillcolor="#EAF2E3", color="#3D6A2E")
    g.node("eval",   "Evaluate", fillcolor="#FDF2E0", color="#A66A1A")
    g.node("learn",  "Learn",    fillcolor="#F2E6F2", color="#6B2A6B")
    g.node("refine", "Refine",   fillcolor="#FBE0E0", color="#962525")

    g.edge("build",  "eval")
    g.edge("eval",   "learn")
    g.edge("learn",  "refine")
    g.edge("refine", "build")

    _render(g, "methodology")


def main() -> None:
    print("Building thesis figures (advisor comments C418, C438, C453, C747)")
    build_architecture()
    build_process_flow()
    build_taxonomy_summary()
    build_taxonomy_annex()
    print("Building defense-deck figures")
    build_methodology_cycle()
    print("Done.")


if __name__ == "__main__":
    main()
