#!/usr/bin/env python3
"""Hand-reviewed syntax/meaning and paper-2 class labels.

Heuristic seeds the pass. Every row is confirmed or overridden below.
n=221 (see extract_summary.json). Recode sample: reliability.py, n=40, seed 20260822.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

DATA = Path(__file__).parent / "data"

# id -> (syntax, meaning, paper2)
# syntax: S0 S1 S2 S3
# meaning: M0 M1 M2 M3
# paper2: A B C D X
OVERRIDES: dict[int, tuple[str, str, str]] = {}


def heuristic(row: dict) -> tuple[str, str, str]:
    spec = row["spec"]
    sec = (row["section"] or "").lower()
    field = (row["field"] or "").lower()
    t = row["text"].lower()

    # --- obvious non-conformance ---
    if re.search(
        r"^(this document specifies|as the concern for|prescribed use of the tcf may support|"
        r"in particular, first parties|the information stored in the gvl is used for determining|"
        r"please note the difference|the ruling should therefore|"
        r"before adopting and implementing|"
        r"this section details the overall|"
        r"as the gpp aims|the gpp provides vendors with a technical mechanism to understand)",
        t,
    ):
        return "S0", "M0", "X"
    if re.search(
        r"\b(for example, if tcf needs|example when|example global|planet49 judgment|"
        r"81\)\.|this includes the requirement to provide information about the duration|"
        r"examples of non-cookie|regional governance in the us may increase|"
        r"resources required for ongoing|"
        r"this is required to make real-time|"
        r"there are already existing vendor lists|"
        r"when a creative is rendered, it may contain|"
        r"the user `id` is an exchange artifact)",
        t,
    ):
        return "S0", "M0", "X"
    if "version history" in sec or "about iab" in sec or "disclaimer" in sec:
        return "S0", "M0", "X"
    if "getting started" in sec and spec == "gpp-guidelines":
        return "S0", "M0", "X"
    if spec == "gpp-guidelines" and any(
        k in sec
        for k in (
            "2. publisher",
            "2.1 about consent",
            "2.2 deciding",
            "3. cmp guidelines",
            "3.2 presentation",
            "what's the difference between a gpp id",
        )
    ):
        return "S0", "M1", "X" if "must" not in t else ("S0", "M1", "D")
    if spec == "gpp-string" and "how do i get" in sec:
        if "pixel is in" in t or "cmp api cannot" in t:
            return "S3", "M1", "C"
        if "must add a pair of macros" in t or "must insert it within a url" in t:
            return "S3", "M0", "C"
        if "gpp_string" in t or "gpp_sid" in t or "macro" in t:
            if "example" in t and "must include two key-value" in t:
                return "S0", "M0", "X"
            if "propagated as is" in t:
                return "S3", "M0", "C"
            if "replace the macros" in t or "valid gpp id" in t:
                return "S3", "M0", "C"
            if "should match the value returned by the cmp api" in t:
                return "S3", "M1", "C"
            if "single section id" in t or "up to 2 values" in t:
                return "S1", "M0", "B"
            if "considered “in force”" in t or 'considered "in force"' in t or "in force" in t:
                return "S1", "M2", "D"
            return "S3", "M0", "C"
        if "must neither create" in t:
            return "S0", "M1", "D"
        return "S0", "M1", "X"

    # vendor registration / GVL / CMP list (not the privacy string)
    if re.search(
        r"\b(tools portal|registration portal|sign the mspa|gvl id|"
        r"must retrieve their ids|vendors should decide which framework|"
        r"must register for each specific framework|"
        r"public attestation of compliance|"
        r"follow technical standards provided|"
        r"cmp api specified in this document|"
        r"must operate in a service-specific|"
        r"legal counsel|business and legal teams|"
        r"consult their cmps|vendor partners to understand|"
        r"iab certification|cmp ids|"
        r"you should always provide your id|"
        r"you should set the field to 1|"
        r"not required to implement all supported sections)\b",
        t,
    ):
        if "header" in t and "required" in t:
            pass
        else:
            return "S0", "M1", "D"

    # encoding / string shape
    if re.search(
        r"\b(must contain a header|header is always required|header section is always required|"
        r"must be formatted|core string is always required|must contain a core tc string|"
        r"base64-like|modified version of it|fibonacci|int\(12\)|bit representation|"
        r"ids must be represented in the order|"
        r"must be in sorted order|"
        r"israngeencoding|is always required and comes first|"
        r"third character position|hyphen character may also|"
        r"1---|base85 cookie safe|"
        r"0 = no, 1 = yes|0 = tracking is unrestricted|"
        r"this field must always have the value of 1|"
        r"bits 2 to 5 are required|"
        r"value is required even if it is 0|"
        r"us privacy section is deprecated)\b",
        t,
    ):
        meaning = "M0"
        syntax = "S1"
        p2 = "B"
        if re.search(r"\b(order the related sections|section count|sorted order|header declares)\b", t):
            syntax = "S2"
        if re.search(r"\b(0 = |1 = |base85|1---|hyphen|always have the value of 1|bits 2 to 5)\b", t):
            p2 = "A"
        if "deprecated" in t:
            p2 = "B"
        if "coppa" in t:
            meaning = "M2"
        return syntax, meaning, p2

    # macros / URL / OpenRTB placement: S3
    if re.search(
        r"\b(url-based|url parameter|macro|openrtb regs|regs object|"
        r"transaction headers|tcf api must be implemented|"
        r"gdpr_consent|gpp_string|us_privacy` parameter|"
        r"pass the gpp string in the ad call|"
        r"consent payload should be sent according to the openrtb)\b",
        t,
    ):
        if "example" in t and len(t) < 80:
            return "S0", "M0", "X"
        return "S3", "M0", "C"

    # CMP as author / user choice / LAT / DNT / IFA OS
    if re.search(
        r"\b(must neither create nor alter|may only be created by an iab europe tcf registered cmp|"
        r"clear affirmative action|cmp wrote|consent management platform|"
        r"do not track|limit ad tracking|operating system|"
        r"must afford the user a means to opt in|"
        r"right to object|"
        r"vendors that are not included in the gpp string are required to respect|"
        r"parties receiving the data are expected to act)\b",
        t,
    ):
        if field in ("dnt", "lmt"):
            return "S1", "M1", "A"
        if field == "ifa":
            return "S1", "M1", "D"
        return "S0", "M1", "D"

    # sender deems / coppa / in force / gdpr flag
    if re.search(
        r"\b(sender deems|subject to the coppa|opt-out sale|"
        r"digital property has determined|"
        r"expected to provide consumer privacy signals|"
        r"expected to send the us privacy string|"
        r"when a sale of data may occur)\b",
        t,
    ):
        if "hyphen" in t or "1---" in t or "character position" in t:
            return "S1", "M2", "B"
        return "S0", "M2", "D"

    # GVL / GCL fetch
    if re.search(
        r"\b(global vendor list|global cmp list|vendor-list\.consensu|"
        r"must now be server-side|cache-control|max-age|"
        r"compressed version of the gvl|compressed version of the gcl|"
        r"deleteddate|tcfpolicyversion)\b",
        t,
    ):
        if "planet49" in sec or "cookie" in field:
            return "S0", "M1", "D"
        return "S0", "M0", "C"

    # publisher restrictions / legal basis: meaning in the string bits, truth is policy
    if re.search(
        r"\b(publisher restrictions|legal basis|legitimate interest|"
        r"must always respect a restriction|must not apply the legitimate|"
        r"purpose 1 is always required|"
        r"vendors should not rely on the _publisher tc_|"
        r"must not be created before clear affirmative)\b",
        t,
    ):
        if re.search(r"\b(2 bits enum|restrictiontype|numpubrestrictions)\b", t + " " + field):
            return "S1", "M1", "A"
        return "S0", "M1", "D"

    # header/section consistency
    if re.search(
        r"\b(only one section should be sent|multiple sections identified|"
        r"header sections list should contain only|"
        r"applicable to this request|"
        r"signalstatus|pingreturn)\b",
        t,
    ):
        if "geolocation" in t or "discretion" in t:
            return "S0", "M2", "D"
        if "header" in t and "present" in t:
            return "S2", "M0", "B"
        return "S1", "M0", "B"

    # OpenRTB field rows
    if spec == "openrtb-privacy":
        if field in ("dnt", "lmt"):
            return "S1", "M1", "A"
        if field == "ifa":
            return "S1", "M1", "D"
        if field == "gpp_sid":
            return "S1", "M2", "B"
        if field in ("id", "buyeruid"):
            return "S0", "M1", "D"
        if field == "customdata" and "base85" in t:
            return "S1", "M0", "A"
        if field == "customdata":
            return "S0", "M0", "X"
        if field == "inserter" and "ads.txt" in t:
            return "S3", "M0", "C"
        if field in ("inserter", "matcher", "atype"):
            if "may be omitted" in t or "mm=0" in t:
                return "S1", "M0", "B"
            if "highly recommended" in t:
                return "S1", "M0", "B"
            return "S0", "M0", "D"
        return "S1", "M0", "B"

    if spec == "us-privacy":
        if "character" in t or "hyphen" in t or "1---" in t:
            return "S1", "M2", "B"
        if "url" in t or "parameter" in t:
            return "S3", "M0", "C"
        if "expected to act" in t:
            return "S0", "M1", "D"
        if "expected to" in t:
            return "S0", "M2", "D"
        return "S0", "M0", "X"

    # TCF string format leftover
    if spec == "tcf-v2-string":
        if "tc string format" in sec or field:
            if "optional except" in t or "may appear in any order" in t:
                return "S1", "M0", "A"
            if "must" in t or "required" in t:
                return "S1", "M0", "B"
        if "url-based" in sec or "full tc string passing" in sec:
            return "S3", "M0", "C"
        if "who should create" in sec or "when should a tc string" in sec:
            return "S0", "M1", "D"
        if "conflicting string versions" in sec:
            return "S2", "M0", "B"
        if "disclosed vendor" in sec:
            return "S1", "M1", "B"
        return "S0", "M1", "D"

    if spec == "gpp-guidelines":
        if "header section is always required" in t or "at least one section" in t:
            return "S1", "M0", "A"
        if "us privacy section is deprecated" in t:
            return "S1", "M0", "B"
        if "finding a gpp string" in sec or "sending a gpp string" in sec:
            return "S3", "M0", "C"
        if "encoding the gpp string" in sec:
            return "S1", "M0", "B"
        if "applicable section" in sec:
            return "S1", "M2", "D"
        return "S0", "M1", "D"

    if spec == "gpp-string":
        if "who should create" in sec:
            return "S0", "M1", "D"
        if "creating a gpp string" in sec or "section encoding" in sec or "header" in sec:
            if "policy writers" in t or "field names" in t or "camelcase" in t:
                return "S0", "M0", "X"
            return "S1", "M0", "B"
        return "S1", "M0", "B"

    return "S0", "M0", "D"


# Manual confirmations that beat the heuristic. Built by reading every row.
# Format: inclusive id ranges as (start, end, syntax, meaning, paper2) plus singles.
SPANS = [
    # gpp-string
    (0, 0, "S1", "M0", "B"),
    (1, 1, "S0", "M1", "D"),
    (2, 2, "S1", "M0", "B"),
    (3, 3, "S0", "M0", "X"),
    (4, 5, "S1", "M0", "A"),
    (6, 6, "S0", "M0", "X"),
    (7, 7, "S1", "M0", "A"),
    (8, 8, "S2", "M0", "B"),
    (9, 11, "S0", "M0", "X"),
    (12, 13, "S1", "M0", "B"),
    (14, 18, "S0", "M0", "X"),
    (19, 24, "S0", "M1", "X"),
    (25, 25, "S0", "M0", "X"),
    (26, 26, "S3", "M1", "C"),
    (27, 29, "S3", "M0", "C"),
    (30, 30, "S1", "M0", "B"),
    (31, 31, "S1", "M1", "C"),
    (32, 32, "S0", "M1", "D"),
    (33, 33, "S0", "M0", "X"),
    (34, 35, "S1", "M0", "B"),
    (36, 36, "S0", "M0", "X"),
    (37, 39, "S3", "M0", "C"),
    (40, 40, "S1", "M0", "B"),
    (41, 42, "S1", "M0", "B"),
    (43, 43, "S1", "M2", "D"),
    (44, 44, "S3", "M1", "C"),
    # gpp-guidelines
    (45, 47, "S0", "M0", "X"),
    (48, 48, "S0", "M1", "X"),
    (49, 49, "S0", "M0", "X"),
    (50, 50, "S1", "M0", "A"),
    (51, 51, "S1", "M0", "B"),
    (52, 52, "S1", "M0", "A"),
    (53, 53, "S3", "M1", "C"),
    (54, 54, "S1", "M0", "B"),
    (55, 55, "S0", "M1", "D"),
    (56, 56, "S1", "M0", "A"),
    (57, 57, "S0", "M1", "X"),
    (58, 66, "S0", "M1", "X"),
    (67, 68, "S1", "M1", "B"),
    (69, 70, "S0", "M1", "X"),
    (71, 71, "S0", "M1", "D"),
    (72, 72, "S2", "M0", "B"),
    (73, 73, "S1", "M2", "B"),
    (74, 76, "S0", "M2", "D"),
    (77, 77, "S1", "M0", "B"),
    (78, 80, "S0", "M1", "D"),
    (81, 82, "S0", "M1", "X"),
    (83, 83, "S0", "M1", "D"),
    (84, 88, "S3", "M0", "C"),
    (89, 89, "S0", "M1", "D"),
    # tcf-v2-string
    (90, 92, "S0", "M1", "X"),
    (93, 94, "S0", "M1", "D"),
    (95, 95, "S0", "M0", "X"),
    (96, 96, "S1", "M0", "B"),
    (97, 97, "S0", "M1", "X"),
    (98, 99, "S0", "M1", "D"),
    (100, 101, "S0", "M1", "D"),
    (102, 104, "S0", "M1", "D"),
    (105, 110, "S0", "M1", "D"),
    (111, 111, "S0", "M0", "X"),
    (112, 118, "S3", "M0", "C"),
    (119, 119, "S1", "M0", "B"),
    (120, 120, "S3", "M1", "C"),
    (121, 122, "S0", "M1", "D"),
    (123, 123, "S0", "M1", "X"),
    (124, 124, "S1", "M1", "B"),
    (125, 128, "S0", "M1", "D"),
    (129, 133, "S1", "M0", "A"),
    (134, 136, "S1", "M0", "B"),
    (137, 137, "S1", "M1", "B"),
    (138, 138, "S1", "M0", "A"),
    (139, 139, "S1", "M1", "D"),
    (140, 140, "S1", "M0", "A"),
    (141, 142, "S1", "M0", "B"),
    (143, 143, "S1", "M1", "D"),
    (144, 145, "S1", "M0", "A"),
    (146, 151, "S0", "M1", "D"),
    (152, 154, "S0", "M1", "D"),
    (155, 155, "S0", "M1", "X"),
    (156, 173, "S0", "M0", "C"),
    (174, 175, "S0", "M0", "C"),
    (176, 178, "S0", "M1", "C"),
    (179, 185, "S0", "M1", "X"),
    (186, 186, "S0", "M1", "C"),
    (187, 187, "S1", "M1", "C"),
    (188, 193, "S0", "M0", "C"),
    (194, 195, "S0", "M0", "X"),
    # us-privacy
    (196, 196, "S0", "M0", "X"),
    (197, 197, "S0", "M2", "D"),
    (198, 198, "S0", "M1", "D"),
    (199, 200, "S0", "M2", "D"),
    (201, 203, "S1", "M2", "B"),
    (204, 205, "S3", "M0", "C"),
    # openrtb-privacy
    (206, 207, "S1", "M2", "B"),
    (208, 209, "S1", "M1", "A"),
    (210, 210, "S1", "M1", "D"),
    (211, 211, "S0", "M0", "X"),
    (212, 213, "S0", "M1", "D"),
    (214, 214, "S0", "M0", "X"),
    (215, 215, "S1", "M0", "A"),
    (216, 216, "S0", "M0", "D"),
    (217, 217, "S3", "M0", "C"),
    (218, 218, "S0", "M0", "X"),
    (219, 219, "S1", "M0", "B"),
    (220, 220, "S1", "M0", "B"),
]


def labels_for_n(n: int) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str] | None] = [None] * n
    for a, b, s, m, p in SPANS:
        for i in range(a, b + 1):
            if out[i] is not None:
                raise SystemExit(f"duplicate span id {i}")
            out[i] = (s, m, p)
    missing = [i for i, v in enumerate(out) if v is None]
    if missing:
        raise SystemExit(f"unlabeled ids: {missing[:20]} (n={len(missing)})")
    return out  # type: ignore[return-value]


def main():
    rows = list(csv.DictReader(open(DATA / "statements.csv", encoding="utf-8")))
    labs = labels_for_n(len(rows))
    for r, (s, m, p) in zip(rows, labs):
        r["syntax"] = s
        r["meaning"] = m
        r["paper2"] = p
        hs, hm, hp = heuristic(r)
        r["heuristic_syntax"] = hs
        r["heuristic_meaning"] = hm
        r["heuristic_paper2"] = hp
        r["heuristic_agree"] = int((hs, hm, hp) == (s, m, p))

    outp = DATA / "statements_coded.csv"
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    conf = [r for r in rows if r["paper2"] != "X"]
    stats = {
        "n_keyword": len(rows),
        "n_excluded_x": len(rows) - len(conf),
        "n_conformance": len(conf),
        "heuristic_full_agree": sum(int(r["heuristic_agree"]) for r in rows),
        "by_spec": {},
        "syntax": {k: 0 for k in ("S0", "S1", "S2", "S3")},
        "meaning": {k: 0 for k in ("M0", "M1", "M2", "M3")},
        "paper2": {k: 0 for k in "ABCD"},
        "syntax_x_meaning": {},
    }
    for spec in sorted({r["spec"] for r in rows}):
        sub = [r for r in rows if r["spec"] == spec]
        csub = [r for r in sub if r["paper2"] != "X"]
        stats["by_spec"][spec] = {
            "keyword": len(sub),
            "conformance": len(csub),
            "x": len(sub) - len(csub),
            "syntax": {k: len([r for r in csub if r["syntax"] == k]) for k in ("S0", "S1", "S2", "S3")},
            "meaning": {k: len([r for r in csub if r["meaning"] == k]) for k in ("M0", "M1", "M2", "M3")},
            "paper2": {k: len([r for r in csub if r["paper2"] == k]) for k in "ABCD"},
        }
    for r in conf:
        stats["syntax"][r["syntax"]] += 1
        stats["meaning"][r["meaning"]] += 1
        stats["paper2"][r["paper2"]] += 1
        key = f"{r['syntax']}+{r['meaning']}"
        stats["syntax_x_meaning"][key] = stats["syntax_x_meaning"].get(key, 0) + 1

    n = len(conf)
    stats["syntax_pct"] = {k: round(100 * v / n, 1) for k, v in stats["syntax"].items()}
    stats["meaning_pct"] = {k: round(100 * v / n, 1) for k, v in stats["meaning"].items()}
    stats["paper2_pct"] = {k: round(100 * v / n, 1) for k, v in stats["paper2"].items()}
    s12 = stats["syntax"]["S1"] + stats["syntax"]["S2"]
    stats["syntax_shape_or_internal_pct"] = round(100 * s12 / n, 1)
    stats["meaning_person_fact_in_message_pct"] = round(100 * stats["meaning"]["M0"] / n, 1)
    stats["static_checkable_pct"] = round(
        100 * (stats["paper2"]["A"] + stats["paper2"]["B"]) / n, 1
    )
    (DATA / "code_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps({k: stats[k] for k in (
        "n_keyword", "n_excluded_x", "n_conformance",
        "syntax_pct", "meaning_pct", "paper2_pct",
        "syntax_shape_or_internal_pct", "static_checkable_pct",
        "heuristic_full_agree",
    )}, indent=2))
    print("cross", json.dumps(stats["syntax_x_meaning"], indent=2))


if __name__ == "__main__":
    main()
