#!/usr/bin/env python3
"""Figures for the privacy-signaling preprint. Numbers from data/final_stats.json."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

HERE = Path(__file__).parent
DATA = json.loads((HERE / "data" / "final_stats.json").read_text())
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

INK, INK2 = "#111111", "#555555"
S_COL = {"S0": "#d8dbe0", "S1": "#1f5c3a", "S2": "#8ab17d", "S3": "#4a7c9b"}
M_COL = {"M0": "#1f5c3a", "M1": "#c4a35a", "M2": "#a65d57", "M3": "#6f6d66"}

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 9,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "figure.dpi": 200,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def fig1_hops():
    """One GPP string across hops, annotated syntax vs meaning."""
    fig, ax = plt.subplots(figsize=(9.2, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis("off")

    boxes = [
        (0.15, 1.15, 1.9, 1.15, "CMP / OS / store", "M1 source of truth\nnot in the message"),
        (2.35, 1.15, 2.15, 1.15, "OpenRTB regs.gpp", "S1 shape  S2 pairing\nM1 author unknown"),
        (4.8, 1.15, 2.15, 1.15, "VAST [GPPSTRING]", "S3 vs the bid\nif both hops exist"),
        (7.25, 1.15, 2.4, 1.15, "SSAI beacon / stitcher", "Stitcher is declarer\nof record (paper 4)"),
    ]
    for x, y, w, h, title, sub in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.04,rounding_size=0.08",
                facecolor="#f4f5f3",
                edgecolor="#333333",
                linewidth=0.9,
            )
        )
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=8.5, fontweight="bold")
        ax.text(x + w / 2, y + 0.18, sub, ha="center", va="bottom", fontsize=7, color=INK2)
    for x0, x1 in ((2.05, 2.35), (4.5, 4.8), (6.95, 7.25)):
        ax.add_patch(
            FancyArrowPatch(
                (x0, 1.72),
                (x1, 1.72),
                arrowstyle="-|>",
                mutation_scale=10,
                color="#333333",
                lw=0.9,
            )
        )
    ax.add_patch(
        FancyBboxPatch(
            (0.15, 0.15),
            9.5,
            0.72,
            boxstyle="round,pad=0.03,rounding_size=0.06",
            facecolor="#eeeef0",
            edgecolor="#888888",
            linewidth=0.7,
            linestyle="--",
        )
    )
    ax.text(
        4.9,
        0.51,
        "Surface 2 (ACR / TV OS) never reads these fields. Opt-out is firmware, not regs.gpp.  (M3)",
        ha="center",
        va="center",
        fontsize=8,
    )
    ax.set_title("GPP string hops: syntax on the IAB artifacts, meaning elsewhere", loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig1-hops.png", bbox_inches="tight")
    fig.savefig(FIG / "fig1-hops.pdf", bbox_inches="tight")
    plt.close()


def fig2_classes():
    """Syntax and meaning shares by spec, conformance statements only."""
    table = DATA["table1"]
    labels = {
        "gpp-string": "GPP string",
        "gpp-guidelines": "GPP guidelines",
        "tcf-v2-string": "TCF v2 string",
        "us-privacy": "US Privacy",
        "openrtb-privacy": "OpenRTB privacy",
    }
    order = ["gpp-string", "gpp-guidelines", "tcf-v2-string", "us-privacy", "openrtb-privacy"]
    rows = [next(r for r in table if r["spec"] == s) for s in order]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.6), sharey=True)
    y = range(len(rows))[::-1]

    def stack(ax, keys, colors, title, prefix):
        for yi, r in zip(y, rows):
            left = 0.0
            n = r["conformance"] or 1
            for k in keys:
                share = 100.0 * r[f"{prefix}_{k}"] / n
                if share <= 0:
                    continue
                ax.barh(
                    yi,
                    share,
                    left=left,
                    color=colors[k],
                    edgecolor="#333333",
                    linewidth=0.5,
                    height=0.62,
                )
                if share >= 12:
                    ax.text(
                        left + share / 2,
                        yi,
                        f"{share:.0f}",
                        ha="center",
                        va="center",
                        fontsize=7.5,
                        color="#fff" if k in ("S1", "M0", "M2") else "#111",
                    )
                left += share
            ax.text(101.5, yi, f"n={r['conformance']}", va="center", fontsize=7, color=INK2)
        ax.set_xlim(0, 118)
        ax.set_xlabel("share of conformance statements (%)")
        ax.set_title(title, loc="left", fontsize=9.5)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_yticks(list(y))
    axes[0].set_yticklabels([labels[s] for s in order], fontsize=8.5)
    stack(axes[0], ["S0", "S1", "S2", "S3"], S_COL, "Syntax class", "S")
    stack(axes[1], ["M0", "M1", "M2", "M3"], M_COL, "Meaning class", "M")
    axes[0].legend(
        handles=[Patch(facecolor=S_COL[k], edgecolor="#333", label=k) for k in ("S0", "S1", "S2", "S3")],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.42),
        ncol=4,
        frameon=False,
        fontsize=8,
    )
    axes[1].legend(
        handles=[Patch(facecolor=M_COL[k], edgecolor="#333", label=k) for k in ("M0", "M1", "M2", "M3")],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.42),
        ncol=4,
        frameon=False,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig2-classes.png", bbox_inches="tight")
    fig.savefig(FIG / "fig2-classes.pdf", bbox_inches="tight")
    plt.close()


def fig3_sections():
    """GPP section mix, Sample A wave 3 vs Sample B first contact. Site share."""
    exp = DATA["wild_expanded"]
    a = DATA["wild"]["n_sites"]
    # prevalence site_share lives on DATA["wild"] after finalize copies site()
    # Use expanded stability / sampleB plus gpp_sections site counts from prevalence json via wild_expanded
    a_n = DATA["wild"]["n_sites"]
    b = exp["sampleB_full1"]
    b_n = b["n_sites"]

    def share(sites, n):
        return 100.0 * sites / n if n else 0

    # named sections from prevalence gpp_sections and sample B
    a_sec = exp["gpp_sections"]
    b_sec = b["gpp_sections_named"]
    labels = [
        ("US National (7)", a_sec.get("usnat", {}).get("sites", 0), b_sec["usnat"]["sites"]),
        ("US Privacy in GPP (6)", a_sec.get("uspv1", {}).get("sites", 0), b_sec["uspv1"]["sites"]),
        ("US state (8-32)", a_sec.get("us_state", {}).get("sites", 0), b_sec["us_state"]["sites"]),
        ("TCF EU (2)", a_sec.get("tcfeuv2", {}).get("sites", 0), b_sec["tcfeuv2"]["sites"]),
        ("TCF CA (5)", a_sec.get("tcfca", {}).get("sites", 0), b_sec["tcfca"]["sites"]),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    y = list(range(len(labels)))[::-1]
    h = 0.36
    ax.barh(
        [yi + h / 2 for yi in y],
        [share(a, a_n) for _, a, _ in labels],
        height=h,
        color="#1f5c3a",
        edgecolor="#333",
        linewidth=0.5,
        label=f"Sample A (n={a_n} sites)",
    )
    ax.barh(
        [yi - h / 2 for yi in y],
        [share(b, b_n) for _, _, b in labels],
        height=h,
        color="#8ab17d",
        edgecolor="#333",
        linewidth=0.5,
        label=f"Sample B (n={b_n} sites)",
    )
    ax.set_yticks(list(y))
    ax.set_yticklabels([lab for lab, _, _ in labels], fontsize=8.5)
    ax.set_xlabel("share of sites with that GPP section id (%)")
    ax.set_xlim(0, 55)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("GPP section mix is US National, not TCF", loc="left", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig3-gpp-sections.png", bbox_inches="tight")
    fig.savefig(FIG / "fig3-gpp-sections.pdf", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    fig1_hops()
    fig2_classes()
    fig3_sections()
    print("wrote", FIG)
