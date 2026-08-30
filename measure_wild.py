#!/usr/bin/env python3
"""Privacy-field presence and shape across paper 3 captures.

Reads private jsonl. Writes only aggregates: no consent strings, IFAs,
user ids, page URLs, or GPP payloads. Site-clustered rates.

Prevalence (Section 6 headline) stays Sample A wave 3. Other waves are
stability. Sample B is confirmatory, not a prevalence sample.

GPP section IDs are decoded from the header (type 3 version 1 Fibonacci
range), matching RTBlint's decoder. The string itself is not stored.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).parent
CAP = (
    Path.home()
    / "Documents/workspace/vast-master/vast-media/paper/openrtb-wild/captures"
)
OUT = HERE / "data" / "wild_privacy.json"

GPP_HEADER_OK = re.compile(r"^DB[A-Za-z0-9+/_-]*")
USP_SHAPE = re.compile(r"^1[YN-]{3}$")

WAVES = [
    ("sampleA-wave1", "wave-wave1-sampleA.jsonl", "A"),
    ("sampleA-wave3", "wave-wave3-sampleA.jsonl", "A"),
    ("sampleA-tranco-deep", "tranco-deep.jsonl", "A"),
    ("sampleB-full1", "full1.jsonl", "B"),
    ("sampleB-wave2", "wave-wave2-sampleB.jsonl", "B"),
    ("sampleB-wave4", "wave-wave4-sampleB.jsonl", "B"),
]

PREVALENCE = "sampleA-wave3"

SID_NAME = {
    1: "tcfeuv1",
    2: "tcfeuv2",
    5: "tcfca",
    6: "uspv1",
    7: "usnat",
}

ENDPOINT_NAMES = {
    "htlb.casalemedia.com": "Index",
    "rtb.openx.net": "OpenX",
    "ssb-global.smartadserver.com": "Smart",
    "direct.adsrvr.org": "The Trade Desk",
    "prebid-server.rubiconproject.com": "Magnite PBS",
    "btlr.sharethrough.com": "Sharethrough",
    "c2shb.pubgw.yahoo.com": "Yahoo",
    "hbopenbid.pubmatic.com": "PubMatic",
    "prebid.media.net": "Media.net",
    "fastlane.rubiconproject.com": "Magnite Fastlane",
    "grid-bidder.criteo.com": "Criteo",
    "adx.adform.net": "Adform",
    "ib.adnxs.com": "Xandr",
    "ap.lijit.com": "Lijit",
    "web.ads.aps.amazon-adsystem.com": "Amazon",
}

FLAG_KEYS = [
    "any_privacy_signal",
    "gpp",
    "gpp_sid",
    "gpp_first_class",
    "gpp_ext",
    "gpp_both_placements",
    "gdpr_first_class",
    "gdpr_ext",
    "us_privacy_first_class",
    "us_privacy_ext",
    "coppa",
    "coppa_0",
    "coppa_1",
    "consent_first_class",
    "consent_ext",
    "dnt",
    "lmt",
    "ifa",
    "gpp_header_shape",
    "gpp_has_tilde",
    "gpp_header_decoded",
    "usp_shape",
    "gpp_sid_pair",
    "gpp_without_sid",
    "sid_without_gpp",
    "header_sid_mismatch",
    "gpp_and_usp",
    "gpp_and_gdpr_ext",
    "usp_and_gdpr_ext",
    "sec_tcfeuv2",
    "sec_usnat",
    "sec_uspv1",
    "sec_tcfca",
    "sec_us_state",
    "sec_other",
]


def six_bit_value(ch: str) -> int | None:
    o = ord(ch)
    if 65 <= o <= 90:
        return o - 65
    if 97 <= o <= 122:
        return 26 + (o - 97)
    if 48 <= o <= 57:
        return 52 + (o - 48)
    if ch in "+-":
        return 62
    if ch in "/_":
        return 63
    return None


class BitReader:
    def __init__(self, encoded: str):
        bits: list[bool] = []
        for ch in encoded:
            v = six_bit_value(ch)
            if v is None:
                self.bits = []
                self.pos = 0
                self.ok = False
                return
            for shift in range(5, -1, -1):
                bits.append((v >> shift) & 1 == 1)
        self.bits = bits
        self.pos = 0
        self.ok = True

    def read_bits(self, n: int) -> int | None:
        if n == 0 or self.pos + n > len(self.bits):
            return None
        value = 0
        for _ in range(n):
            value = (value << 1) | int(self.bits[self.pos])
            self.pos += 1
        return value

    def read_fibonacci(self) -> int | None:
        prev = False
        weight, nxt, total = 1, 2, 0
        while True:
            if self.pos >= len(self.bits):
                return None
            bit = self.bits[self.pos]
            self.pos += 1
            if prev and bit:
                return total
            if bit:
                total += weight
            prev = bit
            following = weight + nxt
            weight, nxt = nxt, following
            if weight > 1_000_000:
                return None


def decode_gpp_header(header: str) -> list[int] | None:
    reader = BitReader(header)
    if not reader.ok:
        return None
    header_type = reader.read_bits(6)
    version = reader.read_bits(6)
    if header_type != 3 or version != 1:
        return None
    count = reader.read_bits(12)
    if count is None or count == 0 or count > 64:
        return None
    ids: list[int] = []
    last = 0
    for _ in range(count):
        is_group = reader.read_bits(1)
        delta = reader.read_fibonacci()
        if is_group is None or delta is None:
            return None
        last += delta
        if is_group == 1:
            offset = reader.read_fibonacci()
            if offset is None:
                return None
            end = last + offset
            ids.extend(range(last, end + 1))
            last = end
        else:
            ids.append(last)
    return ids


def _self_check():
    assert decode_gpp_header("DBABM") == [2]
    assert decode_gpp_header("DBACNY") == [2, 6]
    assert decode_gpp_header("DBABjw") == [5, 6]
    assert decode_gpp_header("DBABLA") == [7]


def present(obj, key) -> bool:
    if not isinstance(obj, dict) or key not in obj:
        return False
    v = obj[key]
    return v is not None and v != "" and v != []


def as_int(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and v.strip().lstrip("+-").isdigit():
        return int(v.strip())
    return None


def parse_sids(raw) -> list[int]:
    if raw is None:
        return []
    if isinstance(raw, list):
        out = []
        for item in raw:
            n = as_int(item)
            if n is not None:
                out.append(n)
        return out
    if isinstance(raw, str):
        parts = re.split(r"[,\s]+", raw.strip())
        out = []
        for p in parts:
            n = as_int(p)
            if n is not None:
                out.append(n)
        return out
    n = as_int(raw)
    return [n] if n is not None else []


def host_of(url: str) -> str:
    if not url:
        return ""
    if "://" not in url:
        return url.split("/")[0].lower()
    return (urlparse(url).netloc or "").lower()


def sid_bucket(sid: int) -> str:
    if sid in SID_NAME:
        return SID_NAME[sid]
    if 8 <= sid <= 32:
        return "us_state"
    return "other"


def walk(body: dict) -> dict:
    regs = body.get("regs") if isinstance(body.get("regs"), dict) else {}
    regs_ext = regs.get("ext") if isinstance(regs.get("ext"), dict) else {}
    user = body.get("user") if isinstance(body.get("user"), dict) else {}
    user_ext = user.get("ext") if isinstance(user.get("ext"), dict) else {}
    device = body.get("device") if isinstance(body.get("device"), dict) else {}

    gpp_fc = present(regs, "gpp")
    gpp_ext = present(regs_ext, "gpp")
    gpp = gpp_fc or gpp_ext
    sid_fc = present(regs, "gpp_sid")
    sid_ext = present(regs_ext, "gpp_sid")
    gpp_sid = sid_fc or sid_ext
    gdpr_fc = present(regs, "gdpr")
    gdpr_ext = present(regs_ext, "gdpr")
    usp_fc = present(regs, "us_privacy")
    usp_ext = present(regs_ext, "us_privacy")
    coppa_present = present(regs, "coppa")
    consent_fc = present(user, "consent")
    consent_ext = present(user_ext, "consent")

    gpp_val = regs.get("gpp") if gpp_fc else regs_ext.get("gpp") if gpp_ext else None
    header = ""
    sections_after = 0
    decoded: list[int] | None = None
    gpp_shape = False
    gpp_tilde = False
    if isinstance(gpp_val, str) and gpp_val:
        gpp_tilde = "~" in gpp_val
        header = gpp_val.split("~", 1)[0]
        gpp_shape = bool(GPP_HEADER_OK.match(header))
        if gpp_tilde:
            sections_after = gpp_val.count("~")
        decoded = decode_gpp_header(header)

    declared = parse_sids(regs.get("gpp_sid") if sid_fc else regs_ext.get("gpp_sid"))
    header_ids = decoded or []
    mismatch = bool(gpp and decoded is not None and declared and declared != header_ids)

    usp_val = regs.get("us_privacy") if usp_fc else regs_ext.get("us_privacy") if usp_ext else None
    usp_str = usp_val if isinstance(usp_val, str) else None
    usp_shape = bool(usp_str and USP_SHAPE.match(usp_str))

    coppa_n = as_int(regs.get("coppa")) if coppa_present else None
    gdpr_n = as_int(regs.get("gdpr") if gdpr_fc else regs_ext.get("gdpr") if gdpr_ext else None)

    buckets = {sid_bucket(s) for s in (declared or header_ids)}

    flags = {
        "gpp": gpp,
        "gpp_sid": gpp_sid,
        "gpp_first_class": gpp_fc,
        "gpp_ext": gpp_ext,
        "gpp_both_placements": gpp_fc and gpp_ext,
        "gdpr_first_class": gdpr_fc,
        "gdpr_ext": gdpr_ext,
        "us_privacy_first_class": usp_fc,
        "us_privacy_ext": usp_ext,
        "coppa": coppa_present,
        "coppa_0": coppa_n == 0,
        "coppa_1": coppa_n == 1,
        "consent_first_class": consent_fc,
        "consent_ext": consent_ext,
        "dnt": present(device, "dnt"),
        "lmt": present(device, "lmt"),
        "ifa": present(device, "ifa"),
        "gpp_header_shape": gpp and gpp_shape,
        "gpp_has_tilde": gpp and gpp_tilde,
        "gpp_header_decoded": decoded is not None,
        "usp_shape": (usp_fc or usp_ext) and usp_shape,
        "gpp_sid_pair": bool(gpp and gpp_sid),
        "gpp_without_sid": bool(gpp and not gpp_sid),
        "sid_without_gpp": bool(gpp_sid and not gpp),
        "header_sid_mismatch": mismatch,
        "gpp_and_usp": gpp and (usp_fc or usp_ext),
        "gpp_and_gdpr_ext": gpp and gdpr_ext,
        "usp_and_gdpr_ext": (usp_fc or usp_ext) and gdpr_ext,
        "sec_tcfeuv2": "tcfeuv2" in buckets,
        "sec_usnat": "usnat" in buckets,
        "sec_uspv1": "uspv1" in buckets,
        "sec_tcfca": "tcfca" in buckets,
        "sec_us_state": "us_state" in buckets,
        "sec_other": "other" in buckets or "tcfeuv1" in buckets,
        "any_privacy_signal": any(
            [gpp, gpp_sid, gdpr_fc, gdpr_ext, usp_fc, usp_ext, coppa_present, consent_fc, consent_ext]
        ),
    }
    extra = {
        "declared_sids": declared,
        "header_sids": header_ids,
        "usp_pattern": usp_str if usp_shape else None,
        "coppa_n": coppa_n,
        "gdpr_n": gdpr_n,
        "n_header_sections": len(header_ids),
        "n_payload_sections": sections_after,
    }
    return flags, extra


def site_rate(site_flags: dict[str, set[str]], n_sites: int, key: str) -> dict:
    hits = sum(1 for flags in site_flags.values() if key in flags)
    return {"sites": hits, "n_sites": n_sites, "share": round(hits / n_sites, 4) if n_sites else 0}


def summarize(path: Path, sample: str) -> dict:
    n_req = 0
    payload_hits: dict[str, int] = defaultdict(int)
    site_flags: dict[str, set[str]] = defaultdict(set)
    sites: set[str] = set()
    usp_patterns: dict[str, int] = defaultdict(int)
    sid_payloads: dict[str, int] = defaultdict(int)
    sid_sites: dict[str, set[str]] = defaultdict(set)
    ep_stats: dict[str, dict] = defaultdict(
        lambda: {"n": 0, "sites": set(), "gpp_sites": set(), "gdpr_ext_sites": set(), "usp_ext_sites": set()}
    )
    coppa_vals: dict[str, int] = defaultdict(int)
    gdpr_vals: dict[str, int] = defaultdict(int)
    mismatch_payloads = 0

    with path.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("kind") != "ortb-request":
                continue
            body = rec.get("body")
            if not isinstance(body, dict):
                continue
            site = rec.get("site") or ""
            host = host_of(rec.get("endpoint") or "")
            sites.add(site)
            n_req += 1
            flags, extra = walk(body)
            for k, v in flags.items():
                if v:
                    payload_hits[k] += 1
                    site_flags[site].add(k)
            if extra["usp_pattern"]:
                usp_patterns[extra["usp_pattern"]] += 1
            if extra["coppa_n"] is not None:
                coppa_vals[str(extra["coppa_n"])] += 1
            if extra["gdpr_n"] is not None:
                gdpr_vals[str(extra["gdpr_n"])] += 1
            if flags["header_sid_mismatch"]:
                mismatch_payloads += 1
            id_source = extra["declared_sids"] or extra["header_sids"]
            for sid in id_source:
                b = sid_bucket(sid)
                sid_payloads[b] += 1
                sid_sites[b].add(site)
                sid_payloads[f"id:{sid}"] += 1
                sid_sites[f"id:{sid}"].add(site)
            if host:
                e = ep_stats[host]
                e["n"] += 1
                e["sites"].add(site)
                if flags["gpp"]:
                    e["gpp_sites"].add(site)
                if flags["gdpr_ext"]:
                    e["gdpr_ext_sites"].add(site)
                if flags["us_privacy_ext"]:
                    e["usp_ext_sites"].add(site)

    n_sites = len(sites)
    keys = list(FLAG_KEYS)
    for k in sorted(payload_hits):
        if k not in keys:
            keys.append(k)

    endpoints = []
    for host, d in ep_stats.items():
        ns = len(d["sites"])
        if ns < 10:
            continue
        endpoints.append(
            {
                "host": host,
                "name": ENDPOINT_NAMES.get(host, host),
                "sites": ns,
                "requests": d["n"],
                "gpp_sites": len(d["gpp_sites"]),
                "gdpr_ext_sites": len(d["gdpr_ext_sites"]),
                "usp_ext_sites": len(d["usp_ext_sites"]),
            }
        )
    endpoints.sort(key=lambda r: (-r["sites"], -r["requests"]))

    sid_out = {}
    for k, pays in sorted(sid_payloads.items(), key=lambda kv: (-kv[1], kv[0])):
        sid_out[k] = {
            "payloads": pays,
            "sites": len(sid_sites[k]),
            "n_sites": n_sites,
        }

    return {
        "capture": path.name,
        "sample": sample,
        "n_request_payloads": n_req,
        "n_sites": n_sites,
        "payload_share": {
            k: {
                "payloads": payload_hits.get(k, 0),
                "share": round(payload_hits.get(k, 0) / n_req, 4) if n_req else 0,
            }
            for k in keys
        },
        "site_share": {k: site_rate(site_flags, n_sites, k) for k in keys},
        "usp_patterns": dict(sorted(usp_patterns.items(), key=lambda kv: -kv[1])),
        "coppa_values": dict(coppa_vals),
        "gdpr_values": dict(gdpr_vals),
        "gpp_sections": sid_out,
        "header_sid_mismatch_payloads": mismatch_payloads,
        "endpoints_ge10_sites": endpoints,
    }


STABILITY_KEYS = [
    "gpp",
    "gpp_first_class",
    "gpp_ext",
    "gdpr_ext",
    "us_privacy_ext",
    "us_privacy_first_class",
    "coppa",
    "coppa_1",
    "consent_first_class",
    "gpp_without_sid",
    "sec_usnat",
    "sec_tcfeuv2",
    "sec_uspv1",
    "gpp_and_usp",
    "ifa",
    "lmt",
]


def main():
    _self_check()
    waves = {}
    for key, fname, sample in WAVES:
        path = CAP / fname
        if not path.exists():
            raise SystemExit(f"missing {path}")
        waves[key] = summarize(path, sample)
        print(
            key,
            "req",
            waves[key]["n_request_payloads"],
            "sites",
            waves[key]["n_sites"],
            "gpp",
            waves[key]["site_share"]["gpp"]["sites"],
            "usnat",
            waves[key]["site_share"]["sec_usnat"]["sites"],
        )

    prev = waves[PREVALENCE]
    union_a = set()
    # cannot recover raw site sets from summarize; recompute union counts cheaply
    union_sites_a: set[str] = set()
    union_sites_b: set[str] = set()
    union_sites: set[str] = set()
    for key, fname, sample in WAVES:
        with (CAP / fname).open(encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("kind") != "ortb-request":
                    continue
                s = rec.get("site") or ""
                union_sites.add(s)
                if sample == "A":
                    union_sites_a.add(s)
                else:
                    union_sites_b.add(s)

    stability = {}
    for sample in ("A", "B"):
        rows = []
        for key, _fname, samp in WAVES:
            if samp != sample:
                continue
            w = waves[key]
            row = {
                "wave": key,
                "n_request_payloads": w["n_request_payloads"],
                "n_sites": w["n_sites"],
            }
            for k in STABILITY_KEYS:
                row[k] = w["site_share"][k]
            rows.append(row)
        stability[sample] = rows

    out = {
        "prevalence_wave": PREVALENCE,
        "capture": prev["capture"],
        "n_request_payloads": prev["n_request_payloads"],
        "n_sites": prev["n_sites"],
        "payload_share": prev["payload_share"],
        "site_share": prev["site_share"],
        "usp_patterns": prev["usp_patterns"],
        "coppa_values": prev["coppa_values"],
        "gdpr_values": prev["gdpr_values"],
        "gpp_sections": prev["gpp_sections"],
        "header_sid_mismatch_payloads": prev["header_sid_mismatch_payloads"],
        "endpoints_ge10_sites": prev["endpoints_ge10_sites"],
        "waves": {
            k: {
                "capture": v["capture"],
                "sample": v["sample"],
                "n_request_payloads": v["n_request_payloads"],
                "n_sites": v["n_sites"],
                "site_share": {kk: v["site_share"][kk] for kk in STABILITY_KEYS},
                "payload_share": {
                    kk: v["payload_share"][kk]
                    for kk in ("gpp", "gdpr_ext", "us_privacy_ext", "coppa", "gpp_without_sid")
                },
                "gpp_sections_named": {
                    name: v["gpp_sections"].get(name, {"payloads": 0, "sites": 0, "n_sites": v["n_sites"]})
                    for name in ("tcfeuv2", "usnat", "uspv1", "tcfca", "us_state", "other")
                },
                "coppa_values": v["coppa_values"],
                "usp_patterns": v["usp_patterns"],
            }
            for k, v in waves.items()
        },
        "stability": stability,
        "union_sites": {
            "sampleA": len(union_sites_a),
            "sampleB": len(union_sites_b),
            "either": len(union_sites),
        },
        "note": (
            "US residential vantage. Harness accepts a CMP grant where a known button exists. "
            "Not an EEA TCF-prevalence study. No payload values stored. "
            "Prevalence claims use Sample A wave 3. Sample B is confirmatory. "
            "GPP section IDs decoded from headers; strings discarded."
        ),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    ss = prev["site_share"]
    print(
        json.dumps(
            {
                "prevalence": PREVALENCE,
                "n_req": prev["n_request_payloads"],
                "n_sites": prev["n_sites"],
                "union": out["union_sites"],
                "gpp": ss["gpp"],
                "usnat": ss["sec_usnat"],
                "tcfeuv2": ss["sec_tcfeuv2"],
                "uspv1": ss["sec_uspv1"],
                "coppa_0": ss["coppa_0"],
                "coppa_1": ss["coppa_1"],
                "gpp_and_usp": ss["gpp_and_usp"],
                "mismatch_payloads": prev["header_sid_mismatch_payloads"],
                "usp_patterns": prev["usp_patterns"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
