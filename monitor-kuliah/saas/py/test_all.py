#!/usr/bin/env python3
"""Verifikasi semua JSON load + solver + adapter + agent jalan (real run)."""
import json, glob, sys
sys.path.insert(0, "/opt/data/monitor-kuliah/saas")
for f in sorted(glob.glob("/opt/data/monitor-kuliah/saas/json/*.json")):
    d = json.load(open(f)); print("OK json:", f.split("/")[-1], type(d).__name__)
from py.captcha_solver import solve
print("solver reuse:", solve("", "none", {"session": "x"})["via"])
print("solver captcha file:", solve("/opt/data/monitor-kuliah/evidence/captcha_test.png", "simple_image", {})["via"])
from py.adapters import get_adapter
print("adapter usk:", get_adapter("usk").login({})["via"])
from py.wa_agent import handle
print("agent:", handle("geser jadwal logika ke jam 3", {})["aksi"])
print("ALL OK")
