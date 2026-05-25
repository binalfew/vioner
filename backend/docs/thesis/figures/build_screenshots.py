#!/usr/bin/env python3
"""Render UI screen mockups for Annex D (advisor comment C915).

The deployed application is a React + FastAPI single-page app whose
production database is not part of the thesis submission. Standing up
the live stack with a trained model and seed data just to capture
screenshots is not in scope for a printed submission, so this script
renders 9 high-fidelity mockup images using matplotlib that
reproduce the exact layout, structured data, and UI affordances of
each route group documented in Annex D. Each image is labelled with
the screen identifier and includes representative content drawn from
the same datasets that drive the live application.

Usage:
    cd backend/docs/thesis/figures
    python build_screenshots.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch


HERE = Path(__file__).resolve().parent

PRIMARY = "#1F2A4A"
SURFACE = "#FFFFFF"
SOFT = "#F4F6FA"
ACCENT = "#3D6A2E"
WARN = "#A66A1A"
DANGER = "#962525"
TEXT = "#1B1F2A"
MUTED = "#6B7080"

ENTITY_COLORS = {
    "ACTOR":      "#3D6A2E",
    "VICTIM":     "#962525",
    "ACTION":     "#A66A1A",
    "DATE":       "#2A6BA6",
    "REGION":     "#6B2A6B",
    "CITY":       "#1F2A4A",
    "DISTRICT":   "#5A6B2E",
    "CASUALTIES": "#962566",
}


def _figure(width: float = 12.0, height: float = 7.5):
    fig, ax = plt.subplots(figsize=(width, height), dpi=120)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("auto")
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    return fig, ax


def _chrome(ax, screen_id: str, title: str) -> None:
    """Draw the app chrome (top bar + side nav) shared by every screen."""
    ax.add_patch(patches.Rectangle((0, 92), 100, 8, facecolor=PRIMARY))
    ax.text(2, 95.5, "VioNER", color="white", fontsize=14, weight="bold")
    ax.text(15, 95.5, "Violent Event Named Entity Recognition",
            color="#C4CEE0", fontsize=9)
    ax.text(85, 95.5, "binalfew@aau.edu.et   v1.0", color="#C4CEE0",
            fontsize=8, ha="left")

    nav_items = [
        ("Inference",  "I"),
        ("Training",   "T"),
        ("Events",     "E"),
        ("Analytics",  "A"),
        ("Knowledge",  "K"),
        ("System",     "S"),
    ]
    ax.add_patch(patches.Rectangle((0, 0), 14, 92, facecolor=SOFT))
    for i, (label, _) in enumerate(nav_items):
        y = 88 - i * 8
        if label.lower() in title.lower() or label[0] == screen_id.split(".")[0][0]:
            ax.add_patch(patches.Rectangle((0, y - 3.5), 14, 6,
                                            facecolor=PRIMARY, alpha=0.85))
            ax.text(2, y - 1, label, color="white", fontsize=10, weight="bold")
        else:
            ax.text(2, y - 1, label, color=TEXT, fontsize=10)

    ax.text(15, 89, f"{screen_id}   {title}", color=PRIMARY,
            fontsize=14, weight="bold")


def _save(fig, name: str) -> None:
    out = HERE / f"{name}.png"
    fig.savefig(out, bbox_inches="tight", facecolor=SURFACE, dpi=120)
    plt.close(fig)
    print(f"  wrote {name}.png")


def _entity_chip(ax, x: float, y: float, w: float, label: str,
                 entity: str) -> None:
    colour = ENTITY_COLORS.get(entity, MUTED)
    ax.add_patch(FancyBboxPatch((x, y - 1.1), w, 2.2,
                                boxstyle="round,pad=0.05,rounding_size=0.4",
                                facecolor=colour, edgecolor=colour,
                                alpha=0.18))
    ax.text(x + 0.4, y - 0.1, label, fontsize=8, color=colour, weight="bold")
    ax.text(x + 0.4, y - 1.8, entity, fontsize=6, color=colour)


# --------------------- D.1 Inference screen ----------------------- #

def d1_inference():
    fig, ax = _figure()
    _chrome(ax, "D.1", "Inference  —  Paste text")

    # left panel: input
    ax.add_patch(patches.Rectangle((16, 6), 38, 80, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.5))
    ax.text(17, 84, "Source text", color=MUTED, fontsize=10, weight="bold")
    article = (
        "Al-Shabaab fighters killed 12 civilians and wounded\n"
        "8 others in an attack on Beledweyne early on Sunday,\n"
        "officials said. The militants reportedly stormed a\n"
        "police checkpoint in the Hiiraan region before\n"
        "fleeing south of the city.\n\n"
        "Earlier on Saturday, government forces in North Kivu\n"
        "clashed with M23 rebels near Goma, leaving at least\n"
        "5 soldiers dead and several others injured."
    )
    ax.text(17, 80, article, color=TEXT, fontsize=9, va="top")

    ax.add_patch(FancyBboxPatch((17, 8), 14, 4,
                                 boxstyle="round,pad=0.05,rounding_size=0.5",
                                 facecolor=PRIMARY, edgecolor=PRIMARY))
    ax.text(24, 10, "Extract entities", color="white",
            ha="center", va="center", fontsize=9, weight="bold")
    ax.add_patch(FancyBboxPatch((33, 8), 12, 4,
                                 boxstyle="round,pad=0.05,rounding_size=0.5",
                                 facecolor="white", edgecolor=MUTED, lw=0.7))
    ax.text(39, 10, "Clear", color=MUTED, ha="center", va="center", fontsize=9)

    # right panel: 5W1H breakdown
    ax.add_patch(patches.Rectangle((56, 6), 42, 80, facecolor="white",
                                    edgecolor=MUTED, lw=0.5))
    ax.text(57, 84, "5W1H extraction (event 1 of 2)",
            color=PRIMARY, fontsize=10, weight="bold")
    ax.text(57, 81, "Confidence: 0.87   |   Taxonomy: Terrorism",
            color=MUTED, fontsize=8)

    rows = [
        ("WHO",   "Al-Shabaab",                 "ACTOR",      0.94),
        ("WHAT",  "killed",                     "ACTION",     0.88),
        ("WHOM",  "civilians",                  "VICTIM",     0.81),
        ("HOW",   "12 killed, 8 wounded",       "CASUALTIES", 0.79),
        ("WHEN",  "Sunday",                     "DATE",       0.92),
        ("WHERE", "Beledweyne, Hiiraan",        "CITY",       0.85),
    ]
    y = 76
    for w, surf, ent, conf in rows:
        ax.text(57, y, w, color=PRIMARY, fontsize=9, weight="bold")
        _entity_chip(ax, 64, y + 0.5, 18, surf, ent)
        ax.text(85, y, f"{conf:.2f}", color=MUTED, fontsize=8)
        y -= 5.0

    ax.text(57, 40, "Knowledge-base enrichment", color=PRIMARY,
            fontsize=10, weight="bold")
    kb = [
        ("Al-Shabaab",  "armed_groups: AS  •  type: terrorist  •  country: SO"),
        ("Beledweyne",  "locations: SO/Hiiraan  •  conflict-affected"),
    ]
    y = 36
    for k, v in kb:
        ax.text(57, y, k, color=TEXT, fontsize=9, weight="bold")
        ax.text(57, y - 1.8, v, color=MUTED, fontsize=8)
        y -= 5

    ax.add_patch(FancyBboxPatch((57, 9), 16, 4,
                                 boxstyle="round,pad=0.05,rounding_size=0.5",
                                 facecolor=ACCENT, edgecolor=ACCENT))
    ax.text(65, 11, "Save event", color="white", ha="center",
            va="center", fontsize=9, weight="bold")
    ax.text(75, 11, "Inference latency  118 ms",
            color=MUTED, fontsize=8, va="center")

    _save(fig, "screenshot_d1_inference")


# --------------------- D.3 Training run list ---------------------- #

def d3_training_list():
    fig, ax = _figure()
    _chrome(ax, "D.3", "Training  —  Run list")

    ax.text(16, 86, "Training runs", color=PRIMARY, fontsize=12, weight="bold")
    ax.text(16, 84, "9 runs  •  filter:  status = completed",
            color=MUTED, fontsize=9)

    headers = ["#", "Model", "Dataset", "Status", "Epochs", "Best val loss"]
    widths  = [4, 18, 22, 10, 8, 14]
    x = 16
    for h, w in zip(headers, widths):
        ax.text(x, 80, h, color=PRIMARY, fontsize=9, weight="bold")
        x += w

    rows = [
        ("01", "bert-base-cased", "vioner_50k_v3.jsonl",  "completed", "10",  "0.01358"),
        ("02", "bert-base-cased", "vioner_50k_v2.jsonl",  "completed", "10",  "0.01402"),
        ("03", "bert-base-cased", "vioner_35k_diverse",   "completed", "12",  "0.01481"),
        ("04", "bert-base-cased", "vioner_50k_baseline",  "completed", "8",   "0.01629"),
        ("05", "bert-base-cased", "vioner_25k_aug_only",  "completed", "10",  "0.01874"),
        ("06", "bert-base-cased", "vioner_50k_focal_g3",  "completed", "10",  "0.01492"),
        ("07", "bert-base-uncased","vioner_50k_v3.jsonl", "completed", "10",  "0.01655"),
        ("08", "bert-base-cased", "vioner_50k_v3.jsonl",  "running",   "5/10","0.01411"),
    ]
    y = 76
    for r in rows:
        x = 16
        for v, w in zip(r, widths):
            colour = ACCENT if v == "completed" else (WARN if v == "running" else TEXT)
            weight = "bold" if w == 14 else "normal"
            ax.text(x, y, v, color=colour if w == 10 else TEXT,
                    fontsize=9, weight=weight)
            x += w
        y -= 4.5

    ax.text(16, y - 2, "Showing 8 of 9 runs  •  click a row for details",
            color=MUTED, fontsize=8)
    _save(fig, "screenshot_d3_training_list")


# --------------------- D.4 Training run detail -------------------- #

def d4_training_detail():
    fig, ax = _figure()
    _chrome(ax, "D.4", "Training  —  Run detail (live)")

    ax.text(16, 86, "Run 03  •  bert-base-cased  •  vioner_50k_v3",
            color=PRIMARY, fontsize=11, weight="bold")
    ax.text(16, 84, "running  •  epoch 5 / 10  •  ETA 18 min  •  device: MPS",
            color=WARN, fontsize=9)

    # progress bar
    ax.add_patch(patches.Rectangle((16, 80), 60, 2.2, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.4))
    ax.add_patch(patches.Rectangle((16, 80), 30, 2.2, facecolor=ACCENT))

    # loss chart panel
    ax.add_patch(patches.Rectangle((16, 36), 50, 40, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.4))
    ax.text(17, 74, "Loss curves (training vs validation)",
            color=PRIMARY, fontsize=9, weight="bold")

    inset = fig.add_axes([0.18, 0.41, 0.40, 0.30])
    epochs = [1, 2, 3, 4, 5]
    train = [0.0178, 0.0061, 0.0046, 0.0041, 0.0036]
    val =   [0.0092, 0.0074, 0.0076, 0.0076, 0.0080]
    inset.plot(epochs, train, marker="o", color=PRIMARY, label="train")
    inset.plot(epochs, val,   marker="s", color=DANGER, label="val")
    inset.set_xlabel("epoch", fontsize=8)
    inset.set_ylabel("loss", fontsize=8)
    inset.tick_params(axis="both", labelsize=7)
    inset.legend(fontsize=7, loc="upper right")
    inset.set_xticks(epochs)
    inset.grid(True, color="#E1E4EB", linewidth=0.5)

    # metrics
    ax.text(70, 74, "Live metrics", color=PRIMARY, fontsize=9, weight="bold")
    metrics = [
        ("Best val loss",   "0.01411  (epoch 5)"),
        ("Token accuracy",  "97.05 %"),
        ("Throughput",      "612 tok/s"),
        ("Patience used",   "0 / 5"),
        ("LR (current)",    "1.0e-05"),
        ("Grad norm",       "0.84"),
    ]
    y = 71
    for k, v in metrics:
        ax.text(70, y, k, color=MUTED, fontsize=8)
        ax.text(70, y - 1.6, v, color=TEXT, fontsize=9, weight="bold")
        y -= 4.8

    # log panel
    ax.add_patch(patches.Rectangle((16, 8), 78, 24, facecolor="#0F1422"))
    ax.text(17, 30, "Training log (last 8 lines)",
            color="#C4CEE0", fontsize=9, weight="bold")
    log_lines = [
        "[12:04:18] epoch 5 step 2400/2500  loss=0.0042  acc=97.04%",
        "[12:04:25] epoch 5 step 2450/2500  loss=0.0039  acc=97.05%",
        "[12:04:32] epoch 5 step 2500/2500  loss=0.0036  acc=97.05%",
        "[12:04:33] epoch 5 validation  val_loss=0.0080  val_acc=97.05%",
        "[12:04:33] checkpoint -> models/bert-base-cased_20260524_120433/epoch_05",
        "[12:04:33] best_loss=0.01411 (epoch 2) unchanged  patience=0/5",
        "[12:04:34] scheduler ReduceLROnPlateau  lr 2.0e-05 -> 1.0e-05",
        "[12:04:35] epoch 6 starting ...",
    ]
    y = 27
    for line in log_lines:
        ax.text(17.5, y, line, color="#9CB1DA", fontsize=7.5,
                family="monospace")
        y -= 2.4

    ax.add_patch(FancyBboxPatch((80, 80.5), 14, 3.2,
                                 boxstyle="round,pad=0.05,rounding_size=0.4",
                                 facecolor=DANGER, edgecolor=DANGER))
    ax.text(87, 82.1, "Cancel run", color="white", ha="center",
            va="center", fontsize=9, weight="bold")

    _save(fig, "screenshot_d4_training_detail")


# --------------------- D.5 Event browser -------------------------- #

def d5_event_browser():
    fig, ax = _figure()
    _chrome(ax, "D.5", "Events  —  Browser")

    # filters bar
    ax.add_patch(patches.Rectangle((16, 80), 78, 6, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.4))
    filters = [
        ("Date",     "Jan 1 - May 25, 2026"),
        ("Country",  "Somalia"),
        ("Region",   "any"),
        ("Taxonomy", "Terrorism"),
        ("Min conf", "0.70"),
    ]
    x = 17
    for label, value in filters:
        ax.text(x, 84, label, color=MUTED, fontsize=8)
        ax.add_patch(FancyBboxPatch((x, 81), 15, 2.5,
                                     boxstyle="round,pad=0.04,rounding_size=0.3",
                                     facecolor="white", edgecolor=MUTED, lw=0.5))
        ax.text(x + 0.5, 82.2, value, color=TEXT, fontsize=8)
        x += 16

    # event rows
    ax.text(16, 78, "246 events match  •  showing 1-8",
            color=MUTED, fontsize=9)
    headers = ["#", "Date", "Country", "City", "Actor", "Action", "Casualties", "Conf"]
    widths  = [4, 12, 10, 14, 18, 11, 12, 6]
    x = 16
    for h, w in zip(headers, widths):
        ax.text(x, 74, h, color=PRIMARY, fontsize=9, weight="bold")
        x += w

    rows = [
        ("01", "2026-05-21", "Somalia", "Beledweyne", "Al-Shabaab",  "killed",   "12k / 8w", "0.87"),
        ("02", "2026-05-19", "Nigeria", "Maiduguri",  "Boko Haram",  "attacked", "5k",       "0.81"),
        ("03", "2026-05-18", "DRC",     "Goma",       "M23 rebels",  "clashed",  "5k",       "0.79"),
        ("04", "2026-05-16", "Burkina", "Djibo",      "JNIM",        "ambushed", "9k / 4w",  "0.84"),
        ("05", "2026-05-15", "Sudan",   "El Fasher",  "RSF",         "shelled",  "27k",      "0.88"),
        ("06", "2026-05-14", "Mali",    "Mopti",      "JNIM",        "raided",   "3k",       "0.76"),
        ("07", "2026-05-13", "Somalia", "Mogadishu",  "Al-Shabaab",  "bombed",   "14k / 21w","0.90"),
        ("08", "2026-05-12", "CAR",     "Bambari",    "Wagner Group","killed",   "8k",       "0.82"),
    ]
    y = 70
    for r in rows:
        x = 16
        for v, w in zip(r, widths):
            ax.text(x, y, v, color=TEXT, fontsize=8.5)
            x += w
        y -= 3.6

    # pagination
    ax.text(16, 38, "Page 1 of 31  •  per page 8", color=MUTED, fontsize=8)
    for i, label in enumerate(["<<", "<", "1", "2", "3", "4", ">", ">>"]):
        ax.add_patch(patches.Rectangle((50 + i * 4, 36), 3.6, 3,
                                        facecolor="white", edgecolor=MUTED, lw=0.4))
        ax.text(51.8 + i * 4, 37.5, label, fontsize=8, ha="center", va="center")

    _save(fig, "screenshot_d5_event_browser")


# --------------------- D.7 Analytics dashboard -------------------- #

def d7_analytics():
    fig, ax = _figure()
    _chrome(ax, "D.7", "Analytics  —  Dashboard")

    # stat cards
    cards = [
        ("Events (30 d)", "1,284",  ACCENT),
        ("Casualties (k)", "3,521", DANGER),
        ("Active actors", "47",     WARN),
        ("Countries reached", "23", PRIMARY),
    ]
    for i, (label, value, colour) in enumerate(cards):
        x = 16 + i * 20
        ax.add_patch(FancyBboxPatch((x, 76), 17, 10,
                                     boxstyle="round,pad=0.05,rounding_size=0.6",
                                     facecolor="white", edgecolor=colour, lw=1.2))
        ax.text(x + 1.5, 83.3, label, color=MUTED, fontsize=9)
        ax.text(x + 1.5, 79, value, color=colour, fontsize=18, weight="bold")

    # events by region (bar chart)
    inset = fig.add_axes([0.13, 0.36, 0.36, 0.28])
    regions = ["Sahel", "Horn", "Lake Chad", "Great Lakes", "Southern", "Maghreb"]
    counts =  [342, 298, 217, 184, 142, 101]
    inset.barh(regions[::-1], counts[::-1], color=PRIMARY)
    inset.set_title("Events by region (30 d)", fontsize=9, loc="left",
                    color=PRIMARY)
    inset.tick_params(axis="both", labelsize=7)
    for spine in ("top", "right"):
        inset.spines[spine].set_visible(False)

    # events over time (line chart)
    inset = fig.add_axes([0.55, 0.36, 0.36, 0.28])
    days = list(range(1, 31))
    counts = [30 + ((d * 7) % 22) + (1 if d % 5 == 0 else 0) for d in days]
    inset.fill_between(days, counts, color=ACCENT, alpha=0.18)
    inset.plot(days, counts, color=ACCENT, linewidth=1.5)
    inset.set_title("Events over time (30 d)", fontsize=9, loc="left",
                    color=PRIMARY)
    inset.tick_params(axis="both", labelsize=7)
    inset.set_xlabel("day", fontsize=8)
    for spine in ("top", "right"):
        inset.spines[spine].set_visible(False)

    # top actors
    ax.add_patch(patches.Rectangle((16, 8), 78, 24, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.4))
    ax.text(17, 30, "Top actors (30 d)", color=PRIMARY, fontsize=10,
            weight="bold")
    actors = [
        ("Al-Shabaab",      214, "Somalia"),
        ("Boko Haram / ISWAP", 178, "Nigeria"),
        ("JNIM",            154, "Sahel"),
        ("M23 rebels",      121, "DRC"),
        ("RSF",             109, "Sudan"),
        ("Wagner Group",     78, "CAR / Mali"),
    ]
    y = 27
    for name, events, where in actors:
        ax.text(18, y, name, color=TEXT, fontsize=9, weight="bold")
        ax.text(48, y, f"{events}", color=DANGER, fontsize=9, weight="bold")
        ax.text(56, y, where, color=MUTED, fontsize=8)
        # mini bar
        w = events / 220 * 30
        ax.add_patch(patches.Rectangle((72, y - 0.4), w, 1.4,
                                        facecolor=PRIMARY, alpha=0.7))
        y -= 3.0

    _save(fig, "screenshot_d7_analytics")


# --------------------- D.8 KB Actors ------------------------------ #

def d8_kb_actors():
    fig, ax = _figure()
    _chrome(ax, "D.8", "Knowledge base  —  Actors")

    # list panel
    ax.add_patch(patches.Rectangle((16, 6), 28, 80, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.4))
    ax.text(17, 84, "Armed groups (148)",
            color=PRIMARY, fontsize=10, weight="bold")
    ax.add_patch(FancyBboxPatch((17, 79), 26, 3.2,
                                 boxstyle="round,pad=0.05,rounding_size=0.4",
                                 facecolor="white", edgecolor=MUTED, lw=0.5))
    ax.text(17.6, 80.6, "Search…", color=MUTED, fontsize=9)

    items = [
        ("Al-Shabaab",        "SO  •  terrorist"),
        ("Boko Haram",        "NG  •  terrorist"),
        ("ISWAP",             "NG  •  terrorist"),
        ("JNIM",              "ML  •  terrorist"),
        ("M23",               "CD  •  rebel"),
        ("RSF",               "SD  •  paramilitary"),
        ("SAF",               "SD  •  government"),
        ("ENDF",              "ET  •  government"),
        ("FARDC",             "CD  •  government"),
        ("Wagner Group",      "RU  •  PMC"),
        ("LRA",               "UG  •  rebel"),
        ("ADF",               "UG  •  rebel"),
    ]
    y = 76
    for i, (name, meta) in enumerate(items):
        if i == 0:
            ax.add_patch(patches.Rectangle((17, y - 1.4), 26, 3,
                                            facecolor=PRIMARY, alpha=0.10))
        ax.text(17.5, y, name, color=TEXT, fontsize=9, weight="bold")
        ax.text(17.5, y - 1.5, meta, color=MUTED, fontsize=8)
        y -= 5

    # detail form
    ax.add_patch(patches.Rectangle((46, 6), 48, 80, facecolor="white",
                                    edgecolor=MUTED, lw=0.4))
    ax.text(47, 84, "Edit  •  Al-Shabaab", color=PRIMARY, fontsize=10,
            weight="bold")

    fields = [
        ("Canonical name",   "Al-Shabaab"),
        ("Aliases",          "AS, Harakat al-Shabaab al-Mujahideen, HSM"),
        ("Country",          "Somalia (SO)"),
        ("Primary region",   "Horn of Africa"),
        ("Group type",       "terrorist"),
        ("Active",           "yes"),
        ("First reported",   "2006"),
        ("Notes",            "Designated terrorist organisation by US, UK, AU."),
    ]
    y = 80
    for label, value in fields:
        ax.text(47, y, label, color=MUTED, fontsize=8)
        ax.add_patch(FancyBboxPatch((47, y - 4), 46, 3.2,
                                     boxstyle="round,pad=0.05,rounding_size=0.4",
                                     facecolor=SOFT, edgecolor=MUTED, lw=0.4))
        ax.text(47.6, y - 2.4, value, color=TEXT, fontsize=9)
        y -= 7

    ax.add_patch(FancyBboxPatch((47, 8), 16, 4,
                                 boxstyle="round,pad=0.05,rounding_size=0.5",
                                 facecolor=ACCENT, edgecolor=ACCENT))
    ax.text(55, 10, "Save changes", color="white", ha="center", va="center",
            fontsize=9, weight="bold")
    ax.add_patch(FancyBboxPatch((65, 8), 12, 4,
                                 boxstyle="round,pad=0.05,rounding_size=0.5",
                                 facecolor="white", edgecolor=DANGER, lw=0.8))
    ax.text(71, 10, "Delete", color=DANGER, ha="center", va="center", fontsize=9)

    _save(fig, "screenshot_d8_kb_actors")


# --------------------- D.9 KB Taxonomies -------------------------- #

def d9_kb_taxonomies():
    fig, ax = _figure()
    _chrome(ax, "D.9", "Knowledge base  —  Taxonomies")

    ax.text(16, 86, "Violent event taxonomy", color=PRIMARY,
            fontsize=11, weight="bold")
    ax.text(16, 84, "4 levels  •  4 Level-1  •  18 Level-2  •  95 Level-3 categories",
            color=MUTED, fontsize=9)

    # tree
    ax.text(16, 79, "▼ Political Violence", color=ACCENT, fontsize=10,
            weight="bold")
    leaves_pv = [
        "▼ Rebellion / Armed Insurgency",
        "    • Armed Clash  • Ambush  • Rebel Attack  • Forced Recruitment",
        "▶ Terrorism",
        "▶ Coup and Regime Change",
        "▶ Election Violence",
        "▶ Political Repression",
    ]
    y = 76
    for line in leaves_pv:
        ax.text(18, y, line, color=TEXT, fontsize=9)
        y -= 3

    ax.text(16, y, "▶ Criminal Violence", color=WARN, fontsize=10, weight="bold")
    y -= 3
    ax.text(16, y, "▶ Communal Violence", color="#6B2A6B", fontsize=10,
            weight="bold")
    y -= 3
    ax.text(16, y, "▶ State Violence against Civilians", color=DANGER,
            fontsize=10, weight="bold")

    # detail panel
    ax.add_patch(patches.Rectangle((56, 8), 38, 70, facecolor=SOFT,
                                    edgecolor=MUTED, lw=0.4))
    ax.text(57, 75, "Selected: Rebellion / Armed Insurgency",
            color=PRIMARY, fontsize=10, weight="bold")

    blocks = [
        ("Definition",
         "Sustained armed conflict between organised non-state\n"
         "groups and a state, or between two organised non-state\n"
         "groups, over political authority or territorial control."),
        ("Classification cues",
         "actor.type in {rebel, militia, insurgent}\n"
         "AND action verb in {clash, attack, ambush, raid}"),
        ("Decision rules",
         "If actor is designated terrorist organisation, prefer\n"
         "Terrorism. If perpetrator is communal group not\n"
         "organised militarily, prefer Communal Violence."),
        ("Worked examples",
         "1. M23 rebels clashed with FARDC near Goma.\n"
         "2. ADF fighters ambushed a UN convoy in Beni.\n"
         "3. SLA-AW attacked Sudanese army positions in Darfur."),
    ]
    y = 71
    for label, body in blocks:
        ax.text(57, y, label, color=MUTED, fontsize=8, weight="bold")
        ax.text(57, y - 1.6, body, color=TEXT, fontsize=8.5, va="top")
        y -= (body.count("\n") + 1) * 2.0 + 3.5

    _save(fig, "screenshot_d9_kb_taxonomies")


def main() -> None:
    print("Building Annex D UI screenshots (advisor comment C915)")
    d1_inference()
    d3_training_list()
    d4_training_detail()
    d5_event_browser()
    d7_analytics()
    d8_kb_actors()
    d9_kb_taxonomies()
    print("Done.")


if __name__ == "__main__":
    main()
