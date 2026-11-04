#!/usr/bin/env python3
"""Cek apakah sekarang dalam window absen. Output: JSON list MK yang aktif."""
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

JADWAL_PATH = "/opt/data/monitor-kuliah/jadwal.json"
STATE_PATH = "/opt/data/monitor-kuliah/absen_state.json"
TZ = ZoneInfo("Asia/Jakarta")
WINDOW_PRE_MIN = 15   # mulai cek 15 menit sebelum kelas
WINDOW_POST_MIN = 30  # stop cek 30 menit setelah kelas mulai

def load_absen_done():
    """Return set of kode MK yang sudah absen hari ini."""
    try:
        with open(STATE_PATH) as f:
            data = json.load(f)
        if data.get("tanggal") != datetime.now(TZ).strftime("%Y-%m-%d"):
            return set()
        return set(data.get("done", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def load_jadwal():
    with open(JADWAL_PATH) as f:
        return json.load(f)["mata_kuliah"]

def main():
    now = datetime.now(TZ)
    hari_map = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    hari_ini = hari_map[now.strftime("%A")]
    done_today = load_absen_done()
    aktif = []

    for mk in load_jadwal():
        if mk["hari"] != hari_ini:
            continue
        if mk["kode"] in done_today:
            continue  # sudah absen hari ini
        mulai = datetime.strptime(mk["mulai"], "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=TZ
        )
        win_start = mulai - timedelta(minutes=WINDOW_PRE_MIN)
        win_end = mulai + timedelta(minutes=WINDOW_POST_MIN)
        if win_start <= now <= win_end:
            aktif.append({
                "kode": mk["kode"],
                "nama": mk["nama"],
                "kelas": mk["kelas"],
                "jam": f'{mk["mulai"]}-{mk["selesai"]}',
                "ruang": mk["ruang"],
                "window_start": win_start.isoformat(),
                "window_end": win_end.isoformat(),
            })

    print(json.dumps({"now": now.isoformat(), "hari": hari_ini, "absen_aktif": aktif}, ensure_ascii=False))

if __name__ == "__main__":
    main()
