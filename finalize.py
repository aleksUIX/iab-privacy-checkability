#!/usr/bin/env python3
"""Merge coded statements, wild aggregates, and field table into paper numbers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"
ISSUES = (
    Path.home()
    / "Documents/workspace/vast-master/vast-media/paper/openrtb-wild/dataset_sampleA/issues.csv"
)
PAYLOADS = (
    Path.home()
    / "Documents/workspace/vast-master/vast-media/paper/openrtb-wild/dataset_sampleA/payloads.csv"
)


def pct(n, d):
    return round(100.0 * n / d, 1) if d else 0.0


def wilson(x, n, z=1.96):
    if n <= 0:
        return {"x": x, "n": n, "pct": 0.0, "lo": 0.0, "hi": 0.0}
    p = x / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    margin = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5 / den
    return {
        "x": x,
        "n": n,
        "pct": pct(x, n),
        "lo": round(100.0 * (centre - margin), 1),
        "hi": round(100.0 * (centre + margin), 1),
    }


def rule_of_three(n):
    return {"n": n, "events": 0, "upper_pct": round(300.0 / n, 1) if n else 0.0}


def spec_profile(rows):
    conf = [r for r in rows if r["paper2"] != "X"]
    n = len(conf)
    s12 = sum(1 for r in conf if r["syntax"] in ("S1", "S2"))
    m0 = sum(1 for r in conf if r["meaning"] == "M0")
    green = sum(
        1
        for r in conf
        if r["syntax"] in ("S1", "S2") and r["meaning"] == "M0"
    )
    return {
        "n": n,
        "s1_plus_s2": s12,
        "s1_plus_s2_pct": pct(s12, n),
        "m0": m0,
        "m0_pct": pct(m0, n),
        "green": green,
        "green_pct": pct(green, n),
    }


def paper3_leftover():
    issues = list(csv.DictReader(open(ISSUES, encoding="utf-8")))
    payloads = list(csv.DictReader(open(PAYLOADS, encoding="utf-8")))
    sites = {p["site"] for p in payloads if p.get("side") == "request"}
    by = {}
    for path in (
        "regs.ext.gdpr",
        "user.ext.consent",
        "regs.gpp",
        "regs.gpp_sid",
        "regs.gdpr",
    ):
        hit = {i["site"] for i in issues if i.get("path") == path}
        by[path] = {"sites": len(hit), "n_sites": len(sites)}
    return {"n_sites": len(sites), "n_issues": len(issues), "by_path": by}


def main():
    code = json.loads((DATA / "code_stats.json").read_text())
    wild = json.loads((DATA / "wild_privacy.json").read_text())
    fields = json.loads((DATA / "fields.json").read_text())
    extract = json.loads((DATA / "extract_summary.json").read_text())
    leftover = paper3_leftover()
    reliability = json.loads((DATA / "reliability.json").read_text())

    coded = list(csv.DictReader(open(DATA / "statements_coded.csv", encoding="utf-8")))

    def is_wire(r):
        if r["paper2"] == "X":
            return False
        if r["spec"] in ("gpp-string", "us-privacy", "openrtb-privacy"):
            return True
        if r["spec"] == "gpp-guidelines":
            return r["syntax"] in ("S1", "S2", "S3")
        sec = (r["section"] or "").lower()
        if any(
            k in sec
            for k in (
                "global vendor",
                "global cmp",
                "planet49",
                "caching",
                "gvl",
                "gcl",
                "vendor fields relating",
            )
        ):
            return False
        return True

    wire = [r for r in coded if is_wire(r)]
    nw = len(wire)

    def counts(rows, key, labels):
        return {lab: len([r for r in rows if r[key] == lab]) for lab in labels}

    sx = counts(wire, "syntax", ("S0", "S1", "S2", "S3"))
    mx = counts(wire, "meaning", ("M0", "M1", "M2", "M3"))
    px = counts(wire, "paper2", tuple("ABCD"))
    wire_stats = {
        "n": nw,
        "syntax": sx,
        "syntax_pct": {k: pct(v, nw) for k, v in sx.items()},
        "meaning": mx,
        "meaning_pct": {k: pct(v, nw) for k, v in mx.items()},
        "paper2": px,
        "paper2_pct": {k: pct(v, nw) for k, v in px.items()},
        "s1_plus_s2_pct": pct(sx["S1"] + sx["S2"], nw),
        "static_checkable_pct": pct(px["A"] + px["B"], nw),
        "rule": "String and placement artifacts only. Drops GVL/GCL caching, Planet49 storage disclosures, and GPP-guidelines process prose that is not S1/S2/S3.",
    }

    conf = [r for r in coded if r["paper2"] != "X"]
    specs = sorted({r["spec"] for r in conf})
    leave_one_out = {"full": spec_profile(coded)}
    for sp in specs:
        leave_one_out[f"drop:{sp}"] = spec_profile(
            [r for r in coded if r["spec"] != sp]
        )
    leave_one_out["gpp-string-only"] = spec_profile(
        [r for r in coded if r["spec"] == "gpp-string"]
    )

    recode_alt = [dict(r) for r in coded]
    by_id = {int(r["id"]): r for r in recode_alt}
    for d in reliability["disagreements"]:
        row = by_id[d["id"]]
        row["syntax"], row["meaning"], row["paper2"] = d["recode"]
    leave_one_out["recode-adopt-all"] = spec_profile(recode_alt)

    heur = {
        "n_conformance": len(conf),
        "syntax_agree": sum(
            1 for r in conf if r["syntax"] == r["heuristic_syntax"]
        ),
        "meaning_agree": sum(
            1 for r in conf if r["meaning"] == r["heuristic_meaning"]
        ),
        "paper2_agree": sum(
            1 for r in conf if r["paper2"] == r["heuristic_paper2"]
        ),
        "triple_agree": sum(int(r["heuristic_agree"]) for r in conf),
        "note": "Keyword seed in code.py, not a second coder. Author labels are Table 1.",
    }
    heur["syntax_agree_pct"] = pct(heur["syntax_agree"], heur["n_conformance"])
    heur["meaning_agree_pct"] = pct(heur["meaning_agree"], heur["n_conformance"])
    heur["triple_agree_pct"] = pct(heur["triple_agree"], heur["n_conformance"])

    n = code["n_conformance"]
    table1 = []
    for spec, d in code["by_spec"].items():
        row = {"spec": spec, "keyword": d["keyword"], "conformance": d["conformance"], "x": d["x"]}
        row.update({f"S_{k}": d["syntax"][k] for k in ("S0", "S1", "S2", "S3")})
        row.update({f"M_{k}": d["meaning"][k] for k in ("M0", "M1", "M2", "M3")})
        table1.append(row)

    wsite = wild["site_share"]
    wpay = wild["payload_share"]

    def site(k):
        d = wsite.get(k) or {"sites": 0, "n_sites": wild["n_sites"], "share": 0}
        return d

    out = {
        "extract": extract,
        "n_keyword": code["n_keyword"],
        "n_excluded_x": code["n_excluded_x"],
        "n_conformance": n,
        "syntax": code["syntax"],
        "syntax_pct": code["syntax_pct"],
        "meaning": code["meaning"],
        "meaning_pct": code["meaning_pct"],
        "paper2": code["paper2"],
        "paper2_pct": code["paper2_pct"],
        "syntax_x_meaning": code["syntax_x_meaning"],
        "syntax_shape_or_internal_pct": code["syntax_shape_or_internal_pct"],
        "static_checkable_pct": code["static_checkable_pct"],
        "s1_plus_s2_n": code["syntax"]["S1"] + code["syntax"]["S2"],
        "m0_n": code["meaning"]["M0"],
        "m1_n": code["meaning"]["M1"],
        "m2_n": code["meaning"]["M2"],
        "wire_subset": wire_stats,
        "leave_one_spec_out": leave_one_out,
        "heuristic_vs_author": heur,
        "table1": table1,
        "table2_fields": fields["openrtb_2_6"],
        "wild": {
            "capture": wild["capture"],
            "n_request_payloads": wild["n_request_payloads"],
            "n_sites": wild["n_sites"],
            "sites_any_privacy": site("any_privacy_signal"),
            "sites_gpp": site("gpp"),
            "sites_gpp_first_class": site("gpp_first_class"),
            "sites_gpp_ext": site("gpp_ext"),
            "sites_gdpr_ext": site("gdpr_ext"),
            "sites_gdpr_first_class": site("gdpr_first_class"),
            "sites_usp_ext": site("us_privacy_ext"),
            "sites_usp_first_class": site("us_privacy_first_class"),
            "sites_coppa": site("coppa"),
            "sites_consent_ext": site("consent_ext"),
            "sites_consent_first_class": site("consent_first_class"),
            "sites_dnt": site("dnt"),
            "sites_lmt": site("lmt"),
            "sites_ifa": site("ifa"),
            "sites_gpp_header_shape": site("gpp_header_shape"),
            "sites_gpp_header_decoded": site("gpp_header_decoded"),
            "sites_gpp_without_sid": site("gpp_without_sid"),
            "sites_header_sid_mismatch": site("header_sid_mismatch"),
            "sites_gpp_and_usp": site("gpp_and_usp"),
            "gpp_sites_without_codec": {
                "sites": site("gpp")["sites"] - site("gpp_header_decoded")["sites"],
                "n_gpp_sites": site("gpp")["sites"],
            },
            "payloads_usp_shape": wpay.get("usp_shape"),
            "payloads_gpp_and_usp": wpay.get("gpp_and_usp"),
            "usp_patterns": wild.get("usp_patterns"),
            "usp_pattern_n": sum(wild.get("usp_patterns", {}).values()),
            "intervals": {
                "gpp": wilson(site("gpp")["sites"], wild["n_sites"]),
                "us_privacy_ext": wilson(
                    site("us_privacy_ext")["sites"], wild["n_sites"]
                ),
                "gdpr_ext": wilson(site("gdpr_ext")["sites"], wild["n_sites"]),
                "gpp_without_sid": wilson(
                    site("gpp_without_sid")["sites"], wild["n_sites"]
                ),
                "tcf_eu_rule_of_three_union_sites": rule_of_three(
                    wild["union_sites"]["either"]
                ),
            },
            "payloads_gpp_without_sid": wpay.get("gpp_without_sid"),
            "payloads_gpp": wpay.get("gpp"),
            "payloads_usp_ext": wpay.get("us_privacy_ext"),
            "note": wild["note"],
        },
        "paper3_frozen_issues": leftover,
        "paper3_ext_gdpr_sites": leftover["by_path"]["regs.ext.gdpr"]["sites"],
        "paper3_n_sites": leftover["n_sites"],
        "wild_expanded": {
            "n_request_all_waves": sum(w["n_request_payloads"] for w in wild["waves"].values()),
                "union_sites": wild["union_sites"],
                "stability": wild["stability"],
                "gpp_sections": wild["gpp_sections"],
                "coppa_values": wild["coppa_values"],
                "gdpr_values": wild["gdpr_values"],
                "usp_patterns": wild["usp_patterns"],
                "header_sid_mismatch_payloads": wild["header_sid_mismatch_payloads"],
                "endpoints_ge10_sites": wild["endpoints_ge10_sites"],
                "sampleB_full1": {
                "n_sites": wild["waves"]["sampleB-full1"]["n_sites"],
                "n_request_payloads": wild["waves"]["sampleB-full1"]["n_request_payloads"],
                "site_share": wild["waves"]["sampleB-full1"]["site_share"],
                "gpp_sections_named": wild["waves"]["sampleB-full1"]["gpp_sections_named"],
                "coppa_values": wild["waves"]["sampleB-full1"]["coppa_values"],
            },
        },
        "pins": json.loads(
            (Path(__file__).parent / "PINS.json").read_text(encoding="utf-8")
        ),
    }
    (DATA / "final_stats.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_conformance": n,
                "S1+S2_pct": out["syntax_shape_or_internal_pct"],
                "M0_pct": out["meaning_pct"]["M0"],
                "M1_pct": out["meaning_pct"]["M1"],
                "M2_pct": out["meaning_pct"]["M2"],
                "wire_n": out["wire_subset"]["n"],
                "wire_S1S2": out["wire_subset"]["s1_plus_s2_pct"],
                "wire_M0": out["wire_subset"]["meaning_pct"]["M0"],
                "paper3_ext_gdpr": f"{out['paper3_ext_gdpr_sites']} of {out['paper3_n_sites']}",
                "wild_gpp_sites": site("gpp"),
                "wild_gdpr_ext": site("gdpr_ext"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
