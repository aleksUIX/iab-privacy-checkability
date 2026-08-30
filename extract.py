#!/usr/bin/env python3
"""Extract normative statements from pinned IAB privacy specs.

Corpus (wire artifacts only; CMP JS APIs are excluded from the count):
  gpp-string, gpp-guidelines, tcf-v2-string, us-privacy, openrtb-privacy

Outputs data/statements.csv and data/extract_summary.json.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
PINNED = ROOT / "specs" / "pinned"
ORTB = Path.home() / "Documents/workspace/vast-master/rtblint/.openrtb-specs/2.x/openrtb-2.6-202606.md"
OUT = ROOT / "data"

NORMATIVE = re.compile(
    r"\b(must not|must|shall not|shall|should not|should|may not|may|"
    r"required|recommended|optional|cannot|prohibited|not permitted|not allowed|"
    r"expected to|is expected)\b",
    re.IGNORECASE,
)
ABBREV = re.compile(r"\b(e\.g|i\.e|etc|vs|cf|no|v|approx)\.$", re.IGNORECASE)

SKIP_SECTIONS = re.compile(
    r"(license|disclaimer|about iab|contributors|version history|"
    r"table of contents|additional reading|about the iab)",
    re.IGNORECASE,
)


def obligation_type(sentence: str) -> str:
    s = sentence.lower()
    if re.search(
        r"\b(must|shall|required|cannot|prohibited|not permitted|not allowed|expected to)\b",
        s,
    ):
        return "obligation"
    if re.search(r"\b(should|recommended|advised)\b", s):
        return "recommendation"
    return "permission"


def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9`\"])", text)
    buf = ""
    for p in parts:
        buf = (buf + " " + p).strip() if buf else p
        if ABBREV.search(buf.rstrip(".")):
            continue
        yield buf
        buf = ""
    if buf:
        yield buf


def strip_md(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    return text


def html_tables_to_md(text: str) -> str:
    def convert(m):
        rows_out = []
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), re.S):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
            cells = [
                re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).replace("&nbsp;", " ").strip()
                for c in cells
            ]
            if cells:
                rows_out.append("| " + " | ".join(cells) + " |")
        if len(rows_out) > 1:
            sep = "| " + " | ".join(["---"] * (rows_out[0].count("|") - 1)) + " |"
            rows_out.insert(1, sep)
        return "\n".join(rows_out)

    return re.sub(r"<table[^>]*>.*?</table>", convert, text, flags=re.S)


def parse_markdown(spec: str, path: Path, start_pat: str | None = None):
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = html_tables_to_md(raw).split("\n")
    start = 0
    if start_pat:
        for i, ln in enumerate(lines):
            if re.search(start_pat, ln, re.I):
                start = i
                break

    statements = []
    section = ""
    in_code = False
    i = start
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        # Setext underlines leftover in some IAB markdown dumps (`=======`).
        # They are not prose and must not be concatenated into the previous sentence.
        if re.match(r"^[=-]{3,}$", ln.strip()):
            i += 1
            continue
        h = re.match(r"^#{1,4}\s+(.*)", ln)
        if h:
            section = strip_md(h.group(1)).strip()
            i += 1
            continue
        if SKIP_SECTIONS.search(section):
            i += 1
            continue
        if ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 2 and not re.match(r"^[-: ]+$", cells[0]):
                desc = strip_md(" ".join(cells[1:])).replace("<br>", " ")
                field = strip_md(cells[0]).strip("` ")
                for sent in split_sentences(desc):
                    if NORMATIVE.search(sent) and len(sent) > 20:
                        statements.append(
                            {
                                "spec": spec,
                                "stratum": "field-desc",
                                "section": section,
                                "field": field,
                                "text": sent,
                                "obligation": obligation_type(sent),
                            }
                        )
            i += 1
            continue
        para = ln.strip()
        while (
            para
            and i + 1 < len(lines)
            and lines[i + 1].strip()
            and not re.match(r"^[=-]{3,}$", lines[i + 1].strip())
            and not lines[i + 1].strip().startswith(("|", "#", "```", "- ", "* "))
        ):
            i += 1
            para += " " + lines[i].strip()
        para = strip_md(para)
        for sent in split_sentences(para):
            if NORMATIVE.search(sent) and len(sent) > 25:
                statements.append(
                    {
                        "spec": spec,
                        "stratum": "prose",
                        "section": section,
                        "field": "",
                        "text": sent,
                        "obligation": obligation_type(sent),
                    }
                )
        i += 1
    return statements


def parse_openrtb_privacy():
    """Regs object, privacy section, device dnt/lmt/ifa, user consent, cookie-sync privacy close."""
    text = ORTB.read_text(encoding="utf-8")
    chunks = []
    # 2.7 Privacy
    m = re.search(r"## 2\.7 - Privacy.*?(?=## 2\.8)", text, re.S)
    if m:
        chunks.append(("2.7 Privacy", m.group(0)))
    m = re.search(r"### 3\.2\.3 - Object: Regs.*?(?=### 3\.2\.4)", text, re.S)
    if m:
        chunks.append(("3.2.3 Regs", m.group(0)))
    m = re.search(r"### 3\.2\.18 - Object: Device.*?(?=### 3\.2\.19)", text, re.S)
    if m:
        chunks.append(("3.2.18 Device", m.group(0)))
    m = re.search(r"### 3\.2\.20 - Object: User.*?(?=### 3\.2\.21)", text, re.S)
    if m:
        chunks.append(("3.2.20 User", m.group(0)))
    m = re.search(r"### 3\.2\.27 - Object: EID.*?(?=### 3\.2\.28)", text, re.S)
    if m:
        chunks.append(("3.2.27 EID", m.group(0)))
    m = re.search(r"### 3\.2\.28 - Object: UID.*?(?=### 3\.2\.29)", text, re.S)
    if m:
        chunks.append(("3.2.28 UID", m.group(0)))
    m = re.search(
        r"Other Considerations and Best Practices.*",
        text,
        re.S,
    )
    if m:
        chunks.append(("Appendix C privacy", m.group(0)[:2500]))

    tmp = ROOT / "specs" / "pinned" / "openrtb-privacy-excerpt.md"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(
        "\n\n".join(f"# {title}\n\n{body}" for title, body in chunks),
        encoding="utf-8",
    )
    statements = parse_markdown("openrtb-privacy", tmp)
    keep_fields = {
        "coppa",
        "gdpr",
        "us_privacy",
        "gpp",
        "gpp_sid",
        "dnt",
        "lmt",
        "ifa",
        "consent",
        "eids",
        "source",
        "uids",
        "atype",
        "inserter",
        "matcher",
        "mm",
        "id",
    }
    keep_section_prefixes = (
        "2.7",
        "3.2.3",
        "Appendix C",
    )
    privacy_re = re.compile(
        r"\b(privacy|consent|gdpr|gpp|coppa|track|ifa|cookie|opt-?out|eid)\b",
        re.I,
    )
    kept = []
    for row in statements:
        if any(row["section"].startswith(p) for p in keep_section_prefixes):
            kept.append(row)
            continue
        field = (row.get("field") or "").strip("` ").lower()
        if field in keep_fields and row["section"].startswith(
            ("3.2.18", "3.2.20", "3.2.27", "3.2.28")
        ):
            kept.append(row)
            continue
        if privacy_re.search(row["text"]) and row["section"].startswith(
            ("3.2.18", "3.2.20", "3.2.27", "3.2.28")
        ):
            kept.append(row)
    return kept


def main():
    OUT.mkdir(exist_ok=True)
    PINNED.mkdir(parents=True, exist_ok=True)

    sources = [
        (
            "gpp-string",
            PINNED / "gpp-consent-string.md",
            r"^## About the Global Privacy Protocol String",
        ),
        (
            "gpp-guidelines",
            PINNED / "gpp-implementation.md",
            r"^## 1\. Introduction",
        ),
        (
            "tcf-v2-string",
            PINNED / "tcf-v2-string.md",
            r"^## Introduction",
        ),
        (
            "us-privacy",
            PINNED / "us-privacy-string.md",
            r"^## Introduction",
        ),
    ]

    all_st = []
    for spec, path, start in sources:
        if not path.exists():
            raise SystemExit(f"missing {path}")
        st = parse_markdown(spec, path, start)
        all_st.extend(st)
        print(f"{spec}: {len(st)}")

    ortb = parse_openrtb_privacy()
    all_st.extend(ortb)
    print(f"openrtb-privacy: {len(ortb)}")

    # Dedup identical (spec, text)
    seen = set()
    uniq = []
    for row in all_st:
        key = (row["spec"], row["text"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(row)

    for i, row in enumerate(uniq):
        row["id"] = i

    glued = [r for r in uniq if "=======" in r["text"] or "-------" in r["text"]]
    if glued:
        raise SystemExit(f"setext underline leaked into {len(glued)} statements")

    with open(OUT / "statements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["id", "spec", "stratum", "section", "field", "text", "obligation"],
        )
        w.writeheader()
        w.writerows(uniq)

    summary = {
        "n": len(uniq),
        "by_spec": {
            k: len([s for s in uniq if s["spec"] == k])
            for k in sorted({s["spec"] for s in uniq})
        },
        "by_obligation": {
            k: len([s for s in uniq if s["obligation"] == k])
            for k in ("obligation", "recommendation", "permission")
        },
    }
    (OUT / "extract_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
