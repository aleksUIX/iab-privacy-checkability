#!/usr/bin/env python3
"""Assert that every headline number in the manuscript matches data/final_stats.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
STATS = json.loads((HERE / "data" / "final_stats.json").read_text())
REL = json.loads((HERE / "data" / "reliability.json").read_text())
MD = (HERE / "preprint-privacy-signaling.md").read_text()
BODY = MD.split("## References", 1)[0]


def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(1)


def must(fragment: str, label: str) -> None:
    if fragment not in MD:
        fail(f"missing {label!r}: {fragment!r}")


def cited_in_body() -> set[int]:
    used: set[int] = set()
    for blob in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", BODY):
        used.update(int(x) for x in blob.split(","))
    return used


def main() -> None:
    n = STATS["n_conformance"]
    kw = STATS["n_keyword"]
    x = STATS["n_excluded_x"]
    s12 = STATS["syntax_shape_or_internal_pct"]
    s12n = STATS["syntax"]["S1"] + STATS["syntax"]["S2"]
    green = STATS["leave_one_spec_out"]["full"]["green"]
    green_pct = STATS["leave_one_spec_out"]["full"]["green_pct"]
    tcf = next(r for r in STATS["table1"] if r["spec"] == "tcf-v2-string")
    gpp = next(r for r in STATS["table1"] if r["spec"] == "gpp-string")
    gpp_s12_pct = round(100.0 * (gpp["S_S1"] + gpp["S_S2"]) / gpp["conformance"], 1)
    gpp_m0_pct = round(100.0 * gpp["M_M0"] / gpp["conformance"], 1)
    loo = STATS["leave_one_spec_out"]
    wild = STATS["wild"]
    rec = loo["recode-adopt-all"]

    must("Paper 5 of the checkability series", "series number")
    if "Paper 6 of the checkability series" in MD:
        fail("series number still says Paper 6")

    must(f"{kw} normative-keyword sentences", "keyword n")
    must(f"{x} non-conformance", "excluded X")
    must(f"{n} statements remain", "conformance n (abstract)")
    must(f"{n} conformance statements", "conformance n (body)")
    must(f"S1+S2 is {s12}%", "S1+S2 headline")
    must(f"{green} of {n} statements ({green_pct}%)", "green cell")
    must(f"{tcf['S_S0']} of {tcf['conformance']} conformance statements", "TCF S0")
    must(f"{gpp['S_S1'] + gpp['S_S2']} ({gpp_s12_pct}%)", "GPP S1+S2")
    must(f"{gpp['M_M0']} ({gpp_m0_pct}%)", "GPP M0")
    must("38 of 79", "leftover gdpr sites")
    must(f"{wild['sites_gpp']['sites']} of {wild['n_sites']}", "GPP sites")
    must(
        f"{wild['gpp_sites_without_codec']['sites']} of {wild['gpp_sites_without_codec']['n_gpp_sites']}",
        "GPP no codec",
    )
    must("1,334 payloads", "USP alphabet formatted")
    must(f"{wild['sites_any_privacy']['sites']}", "any privacy sites")
    must("83.5%", "any privacy share")
    must("kappa 0.83", "syntax kappa")
    must("kappa 0.80", "meaning kappa")
    must("kappa 0.81", "paper2 kappa")
    must(f"{REL['n_full_match']} of 40", "full triple match")
    must(f"n from {n} to {rec['n']}", "recode-adopt n")
    must(f"{rec['s1_plus_s2_pct']}%", "recode-adopt S1+S2")
    must(f"{rec['green_pct']}%", "recode-adopt green")
    must(f"wire cut (n={STATS['wire_subset']['n']})", "wire n")
    must(f"{STATS['wire_subset']['s1_plus_s2_pct']}%", "wire S1+S2")
    must(f"{STATS['static_checkable_pct']}%", "static A+B")
    must("20,226 requests", "all-wave requests")
    must("165 sites", "union sites")
    must("one document-scope sentence", "recode inventory")
    must(f"{REL['wire_specs']['syntax']['agree']} of {REL['wire_specs']['n']}", "wire recode syntax")
    must(f"{REL['wire_specs']['meaning']['agree']} of {REL['wire_specs']['n']}", "wire recode meaning")
    tcf_n_dis = REL["disagreements_by_spec"]["tcf-v2-string"]
    must(f"Six of eight disagreements", "tcf disagreement share")
    if tcf_n_dis != 6:
        fail(f"expected 6 TCF disagreements, got {tcf_n_dis}")
    must("217 unique texts", "unique texts")
    tcf_k = REL["tcf_subsample"]["syntax"]["kappa"]
    must(f"0.47", "tcf syntax kappa")
    if round(tcf_k, 2) != 0.47:
        fail(f"manuscript 0.47 != reliability {tcf_k}")
    twin_k = REL["drop_header_twin"]["syntax"]["kappa"]
    must("0.82", "drop-twin syntax kappa")
    if round(twin_k, 2) != 0.82:
        fail(f"manuscript 0.82 != reliability {twin_k}")
    must("two rejects and one warn", "monday list")
    if "three rejects from this corpus" in MD:
        fail("leftover ext.gdpr called a reject")
    iv = wild["intervals"]["gpp"]
    must(f"{iv['lo']}% to {iv['hi']}%", "GPP Wilson")
    gpp_s3_pct = round(100.0 * gpp["S_S3"] / gpp["conformance"], 1)
    must(f"Eight more ({gpp_s3_pct}%) are S3", "GPP S3")

    table1_label = {
        "gpp-string": "GPP string",
        "gpp-guidelines": "GPP guidelines",
        "tcf-v2-string": "TCF v2 string",
        "us-privacy": "US Privacy",
        "openrtb-privacy": "OpenRTB privacy",
    }
    for row in STATS["table1"]:
        label = table1_label[row["spec"]]
        must(
            (
                f"| {label} | {row['keyword']} | {row['x']} | {row['conformance']} | "
                f"{row['S_S0']} | {row['S_S1']} | {row['S_S2']} | {row['S_S3']} | "
                f"{row['M_M0']} | {row['M_M1']} | {row['M_M2']} | {row['M_M3']} |"
            ),
            f"table1 {label}",
        )

    full = loo["full"]
    must(
        f"| Full portfolio | {full['n']} | {full['s1_plus_s2_pct']}% | {full['m0_pct']}% | {full['green_pct']}% |",
        "table2 full",
    )

    wave_label = {
        "sampleA-wave1": "Sample A wave 1",
        "sampleA-wave3": "Sample A wave 3",
        "sampleA-tranco-deep": "Sample A tranco-deep",
        "sampleB-full1": "Sample B full1",
        "sampleB-wave2": "Sample B wave 2",
        "sampleB-wave4": "Sample B wave 4",
    }
    stab = STATS["wild_expanded"]["stability"]
    for w in stab["A"] + stab["B"]:
        lab = wave_label[w["wave"]]
        must(
            (
                f"| {lab} | {w['n_sites']} | {w['gpp']['sites']} | {w['gdpr_ext']['sites']} | "
                f"{w['us_privacy_ext']['sites']} | {w['sec_usnat']['sites']} | "
                f"{w['sec_tcfeuv2']['sites']} | {w['coppa_1']['sites']} | {w['ifa']['sites']} |"
            ),
            f"table5 {lab}",
        )

    usp = wild["usp_patterns"]
    must(f"| `1YNY` | {usp['1YNY']} |", "usp 1YNY")
    must(f"| `1YNN` | {usp['1YNN']} |", "usp 1YNN")
    must(f"| `1YN-` | {usp['1YN-']} |", "usp 1YN-")
    must(f"| `1---` | {usp['1---']} |", "usp 1---")
    other = usp["1NN-"] + usp["1NNY"] + usp["1NNN"] + usp["1YYN"]
    must(f"| other four patterns | {other} |", "usp other")

    must("Regs Resources", "OpenRTB 7.5 companion")
    must("221 keyword rows", "CSV row count wording")
    sidless = wild["payloads_gpp_without_sid"]
    must(
        f"{sidless['payloads']} payloads ({round(sidless['share'] * 100, 1)}%)",
        "gpp without sid payloads",
    )
    must(
        f"{STATS['wild_expanded']['header_sid_mismatch_payloads']} payloads, concentrated",
        "header/sid mismatch payloads",
    )

    css = (HERE / "build" / "print.css").read_text()
    if "preprint v1.0, August 2026" not in css:
        fail("print.css running header missing v1.0")

    if "=======" in (HERE / "data" / "statements.csv").read_text():
        fail("setext underline leaked into statements.csv")
    if STATS.get("s1_plus_s2_n") != s12n:
        fail(f"s1_plus_s2_n {STATS.get('s1_plus_s2_n')} != S1+S2 {s12n}")
    if green != STATS["syntax_x_meaning"]["S1+M0"] + STATS["syntax_x_meaning"]["S2+M0"]:
        fail("green cell != S1+M0 + S2+M0")
    if "two document-scope" in MD:
        fail("stale recode inventory still says two document-scope sentences")
    if "On a CTV app that rule has nowhere to execute" in MD:
        fail("unhedged CTV CMP claim")
    if "when there is no CMP" in MD:
        fail("unhedged CTV heading still says there is no CMP")
    if "streamlines compliance" in MD:
        fail("About-section transmission claim misstated as compliance in the guidelines")
    if "coding rule 3" in MD:
        fail("manuscript cites a numbered codebook rule the PDF does not contain")
    if "without the author GPP assumed," in MD:
        fail("unhedged conclusion on the GPP author")
    if "Yahoo is both GPP and leftover GDPR on 8 of 10" in MD:
        fail("Yahoo overlap overclaim")

    disagrees = REL["disagreements"]
    if len(disagrees) != 8:
        fail(f"expected 8 recode disagreements, got {len(disagrees)}")

    eps = STATS["wild_expanded"]["endpoints_ge10_sites"]
    if len(eps) != 18:
        fail(f"expected 18 Table 7 endpoints, got {len(eps)}")
    must("18 endpoints present on at least 10", "adapter n")
    for ep in eps:
        counts = (
            f"| {ep['sites']} | {ep['gpp_sites']} | "
            f"{ep['gdpr_ext_sites']} | {ep['usp_ext_sites']} |"
        )
        if counts not in MD:
            fail(f"adapter counts missing for {ep['name']}: {counts}")

    bib = [int(m) for m in re.findall(r"^\[(\d+)\]", MD, re.M)]
    if bib != list(range(1, max(bib) + 1)):
        fail(f"bibliography not sequential: {bib}")
    unused = [i for i in bib if i not in cited_in_body()]
    if unused:
        fail(f"unused bibliography numbers: {unused}")

    print(
        json.dumps(
            {
                "ok": True,
                "n_keyword": kw,
                "n_conformance": n,
                "s1_plus_s2_n": s12n,
                "s1_plus_s2_pct": s12,
                "green_pct": green_pct,
                "kappa": (REL["syntax"]["kappa"], REL["meaning"]["kappa"], REL["paper2"]["kappa"]),
                "bib": f"1-{max(bib)}",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
