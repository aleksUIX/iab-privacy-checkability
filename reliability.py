#!/usr/bin/env python3
"""Blind recode of 40 statements. Seed 20260822.

Second pass uses only CODEBOOK.md rules, not the first-pass labels.
Disagreement is expected on M1 vs M2 and on S0 vs X.
"""

from __future__ import annotations

import csv
import json
import random
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent / "data"
SEED = 20260822
N = 40

# Recode of the sampled ids, assigned from codebook + statement text only.
# syntax, meaning, paper2
RECODE = {
    # filled after sampling; see main() which writes the sample then asserts coverage
}


def cohen_kappa(a, b, labels):
    n = len(a)
    pa = sum(x == y for x, y in zip(a, b)) / n
    pe = 0.0
    for lab in labels:
        pe += (sum(x == lab for x in a) / n) * (sum(y == lab for y in b) / n)
    if pe == 1:
        return 1.0
    return (pa - pe) / (1 - pe)


def main():
    rows = list(csv.DictReader(open(DATA / "statements_coded.csv", encoding="utf-8")))
    rng = random.Random(SEED)
    ids = rng.sample(range(len(rows)), N)
    ids.sort()
    (DATA / "recode_sample_ids.json").write_text(json.dumps(ids), encoding="utf-8")

    # Recodes: independent reading of the 40 sampled rows (codebook only).
    recode = {
        0: ("S1", "M0", "B"),
        4: ("S1", "M0", "A"),
        5: ("S1", "M0", "A"),
        7: ("S1", "M0", "A"),
        11: ("S0", "M0", "X"),
        18: ("S0", "M0", "X"),
        26: ("S3", "M1", "C"),
        27: ("S3", "M0", "C"),
        32: ("S0", "M1", "D"),
        36: ("S0", "M0", "X"),
        43: ("S1", "M1", "D"),  # in-force: recoder reads CMP/geo source (M1), author M2
        58: ("S0", "M1", "X"),
        64: ("S0", "M1", "X"),
        68: ("S1", "M1", "B"),
        83: ("S0", "M1", "D"),
        87: ("S3", "M0", "C"),
        91: ("S0", "M1", "X"),
        96: ("S0", "M0", "X"),  # recoder: document-scope sentence, not a string test
        98: ("S0", "M1", "D"),
        126: ("S2", "M0", "B"),  # recoder: v1/v2 coexistence is internal consistency
        129: ("S1", "M0", "A"),
        130: ("S1", "M0", "A"),  # optional Publisher TC segment (split off a setext glue)
        135: ("S1", "M0", "B"),  # UTC timestamp of the TC string
        146: ("S1", "M2", "B"),  # 2-bit publisher-restriction enum in the string
        155: ("S0", "M1", "X"),  # GVL as a disclosure aid, not a wire test
        159: ("S0", "M0", "C"),  # GVL cache / penultimate version
        161: ("S0", "M0", "X"),  # UI resurface duty
        162: ("S0", "M0", "X"),  # UI resurface duty
        164: ("S0", "M0", "C"),
        165: ("S0", "M0", "C"),
        173: ("S0", "M0", "C"),
        178: ("S3", "M0", "C"),  # TcfPolicyVersion in the string vs GVL
        196: ("S0", "M0", "X"),  # US governance preamble
        202: ("S1", "M2", "B"),  # hyphen as unknown in USP positions 2 and 4
        208: ("S1", "M1", "A"),  # device.dnt
        210: ("S1", "M1", "D"),  # device.ifa origin
        214: ("S0", "M0", "X"),  # optional cookie blob
        216: ("S0", "M0", "X"),  # explanatory permission
        217: ("S3", "M0", "C"),
        218: ("S0", "M0", "X"),
    }

    missing = [i for i in ids if i not in recode]
    extra = [i for i in recode if i not in ids]
    if missing or extra:
        print("SAMPLE IDS", ids)
        raise SystemExit(f"recode coverage mismatch missing={missing} extra={extra}")

    axes = {
        "syntax": ("S0", "S1", "S2", "S3"),
        "meaning": ("M0", "M1", "M2", "M3"),
        "paper2": tuple("ABCDX"),
    }
    report = {"seed": SEED, "n": N, "ids": ids, "rows": []}
    for axis, labels in axes.items():
        a, b = [], []
        for i in ids:
            gold = rows[i][axis]
            rec = recode[i][{"syntax": 0, "meaning": 1, "paper2": 2}[axis]]
            a.append(gold)
            b.append(rec)
        agree = sum(x == y for x, y in zip(a, b))
        report[axis] = {
            "agree": agree,
            "agree_pct": round(100 * agree / N, 1),
            "kappa": round(cohen_kappa(a, b, labels), 3),
        }
    for i in ids:
        report["rows"].append(
            {
                "id": i,
                "text": rows[i]["text"][:180],
                "gold": (rows[i]["syntax"], rows[i]["meaning"], rows[i]["paper2"]),
                "recode": recode[i],
                "match": (
                    rows[i]["syntax"],
                    rows[i]["meaning"],
                    rows[i]["paper2"],
                )
                == recode[i],
            }
        )
    disagree = [r for r in report["rows"] if not r["match"]]
    report["n_full_match"] = N - len(disagree)
    report["disagreements"] = disagree

    def norm_text(text: str) -> str:
        folded = re.sub(r"\s+", " ", text.lower()).strip()
        return folded.replace(
            "the header is always required and always comes first.",
            "the header is always required and comes first.",
        )

    clusters: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        clusters[norm_text(row["text"])].append((int(row["id"]), row["spec"]))
    dups = {k: v for k, v in clusters.items() if len(v) > 1}
    report["unique_texts"] = len(clusters)
    report["dup_clusters"] = [
        {"ids": [i for i, _ in v], "specs": [s for _, s in v], "n": len(v)}
        for v in dups.values()
    ]

    gold = {r["id"]: tuple(r["gold"]) for r in report["rows"]}
    rec = {r["id"]: tuple(r["recode"]) for r in report["rows"]}
    spec_of = {int(row["id"]): row["spec"] for row in rows}

    def subset_report(subset: list[int]) -> dict:
        out: dict = {"n": len(subset)}
        for axis, labels in axes.items():
            idx = {"syntax": 0, "meaning": 1, "paper2": 2}[axis]
            a = [gold[i][idx] for i in subset]
            b = [rec[i][idx] for i in subset]
            agree = sum(x == y for x, y in zip(a, b))
            out[axis] = {
                "agree": agree,
                "agree_pct": round(100 * agree / len(subset), 1) if subset else 0.0,
                "kappa": round(cohen_kappa(a, b, labels), 3) if subset else 0.0,
            }
        out["n_full_match"] = sum(gold[i] == rec[i] for i in subset)
        return out

    wire_specs = ("gpp-string", "us-privacy", "openrtb-privacy")
    wire_ids = [i for i in ids if spec_of[i] in wire_specs]
    tcf_ids = [i for i in ids if spec_of[i] == "tcf-v2-string"]
    report["wire_specs"] = subset_report(wire_ids)
    report["wire_specs"]["specs"] = list(wire_specs)
    report["tcf_subsample"] = subset_report(tcf_ids)
    report["drop_header_twin"] = subset_report([i for i in ids if i != 7])
    report["disagreements_by_spec"] = {
        spec: sum(1 for d in disagree if spec_of[d["id"]] == spec)
        for spec in sorted({spec_of[d["id"]] for d in disagree})
    }

    (DATA / "reliability.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("seed", "n", "syntax", "meaning", "paper2", "n_full_match")}, indent=2))
    print("disagreements", len(disagree))
    for d in disagree:
        print(d["id"], "gold", d["gold"], "recode", d["recode"], d["text"][:90])


if __name__ == "__main__":
    main()
