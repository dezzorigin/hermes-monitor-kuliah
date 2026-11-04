#!/usr/bin/env python3
"""Monitor gate untuk cron absen-watcher-dezz.
Output konstan ('idle') di luar window kuliah -> agent skip.
Di dalam window: output berubah tiap tick (timestamp) -> agent jalan tiap interval.
MK yang sudah 'done' di absen_state.json dikeluarkan -> setelah absen, output balik 'idle'.
"""
import json
import sys
sys.path.insert(0, "/opt/data/monitor-kuliah/scripts")
from check_schedule import load_jadwal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Jakarta")
STATE_PATH = "/opt/data/monitor-kuliah/absen_state.json"
WINDOW_PRE_MIN = 10
WINDOW_POST_MIN = 10  # setelah jam selesai kuliah

now = datetime.now(TZ)
hari_map = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
            "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
hari_ini = hari_map[now.strftime("%A")]

# baca done per akun (format baru 'akun' atau lama 'done' list flat)
def load_done():
    try:
        d = json.load(open(STATE_PATH))
        if d.get("tanggal") != now.strftime("%Y-%m-%d"):
            return {"dezz": set(), "rizki": set()}
        if "akun" in d:
            return {k: set(v.get("done", [])) for k, v in d["akun"].items()}
        return {"dezz": set(d.get("done", [])), "rizki": set()}
    except Exception:
        return {"dezz": set(), "rizki": set()}

done_map = load_done()
# gate aktif kalau ada MK yang belum done di SALAH SATU akun
done = done_map.get("dezz", set()) | done_map.get("rizki", set())
# tapi MK yang sudah done di KEDUA akun tidak usah dipantau
done_both = done_map.get("dezz", set()) & done_map.get("rizki", set())

aktif = []
for mk in load_jadwal():
    if mk["hari"] != hari_ini or mk["kode"] in done_both:
        continue
    mulai = datetime.strptime(mk["mulai"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=TZ)
    selesai = datetime.strptime(mk["selesai"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=TZ)
    # window: 10 mnt sebelum kelas s/d 10 mnt setelah jam selesai
    # (dosen bisa buka presensi kapan pun selama jam kuliah)
    if mulai - timedelta(minutes=WINDOW_PRE_MIN) <= now <= selesai + timedelta(minutes=WINDOW_POST_MIN):
        aktif.append(mk["kode"])

if not aktif:
    print("idle")
else:
    # detail akun yg masih pending per MK + timestamp -> output beda tiap tick -> agent bangun tiap interval
    parts = []
    for k in aktif:
        pend = [a for a in ("dezz", "rizki") if k not in done_map.get(a, set())]
        parts.append(f"{k}(pending:{','.join(pend) or '-'})")
    print(" ".join(parts) + " @" + now.strftime("%H:%M"))
