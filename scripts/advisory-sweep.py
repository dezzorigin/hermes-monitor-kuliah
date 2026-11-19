#!/usr/bin/env python3
"""Sweep dependensi produksi terhadap OSV (Open Source Vulnerabilities).

Pola repo #24-#43: 1 POST ke api.osv.dev/v1/querybatch untuk semua paket
produksi. JANGAN ganti ke `npm audit` (melaporkan advisory dev-only
sebagai temuan produksi) atau ke GitHub Advisory DB API + GITHUB_TOKEN
(401 deterministik di CI).

Repo ini (automation monitor kuliah Python + landing statis) punya 6
dependensi produksi, dipin di requirements.txt di root repo:
requests, urllib3, cryptography (decrypt vault), ddddocr (OCR captcha),
pillow, reportlab (PDF draft tugas). Ekosistem PyPI.

Usage:
    python3 scripts/advisory-sweep.py
No token needed. Exit code 0 = production tree clean, 1 = findings,
2 = API error.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

SEVERITIES = ("HIGH", "CRITICAL")
OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"


def load_prod_packages(req_path):
    """name -> sorted list of versions, dari pin == di requirements.txt."""
    prod = {}
    if not os.path.exists(req_path):
        return prod
    with open(req_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            m = re.match(r"^([A-Za-z0-9_.-]+)==([^\s;]+)", line)
            if m:
                prod.setdefault(m.group(1).lower(), set()).add(m.group(2))
    return {name: sorted(vers) for name, vers in sorted(prod.items())}


def severity_of(vuln):
    ds = vuln.get("database_specific") or {}
    sev = (ds.get("severity") or "").upper()
    if sev in ("CRITICAL", "HIGH", "MODERATE", "LOW"):
        return sev
    for entry in vuln.get("severity", []) or []:
        try:
            score = float(entry.get("score", ""))
        except (TypeError, ValueError):
            continue
        if score >= 9.0:
            return "CRITICAL"
        if score >= 7.0:
            return "HIGH"
        if score >= 4.0:
            return "MODERATE"
        return "LOW"
    return None


def query_osv(queries):
    body = json.dumps({"queries": queries}).encode()
    req = urllib.request.Request(
        OSV_BATCH_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.build_opener().open(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read()[:500].decode("utf-8", "replace")
        print(f"ERROR: OSV API {e.code}: {detail}", file=sys.stderr)
        raise SystemExit(2)
    except urllib.error.URLError as e:
        print(f"ERROR: OSV API unreachable: {e}", file=sys.stderr)
        raise SystemExit(2)


def sweep(prod):
    pairs = [(name, ver) for name, vers in prod.items() for ver in vers]
    print(
        f"checking {len(prod)} production packages "
        f"({len(pairs)} name@version pairs)",
        flush=True,
    )
    queries = [
        {"package": {"name": name, "ecosystem": "PyPI"}, "version": ver}
        for name, ver in pairs
    ]
    if not queries:
        return [], []
    resp = query_osv(queries)
    results = resp.get("results", [])
    findings = []
    unknown = []
    seen = set()
    for (name, ver), res in zip(pairs, results):
        for vuln in res.get("vulns", []) or []:
            sev = severity_of(vuln)
            vid = vuln.get("id", "?")
            aliases = ",".join(vuln.get("aliases", []) or [])
            key = (name, ver, vid)
            if key in seen:
                continue
            seen.add(key)
            if sev in SEVERITIES:
                findings.append(f"{name}@{ver}: {vid} {sev} {aliases}")
            elif sev is None:
                unknown.append(f"{name}@{ver}: {vid} (severity unknown)")
    return findings, unknown


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prod = load_prod_packages(os.path.join(root, "requirements.txt"))
    findings, unknown = sweep(prod)
    for line in unknown:
        print("  note: " + line, flush=True)
    if findings:
        print("FAIL: high/critical advisories:", flush=True)
        for line in findings:
            print("  " + line, flush=True)
        return 1
    print(
        "OK: no high/critical advisories affect production dependencies",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
