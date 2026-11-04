#!/usr/bin/env python3
"""Runner tahap-1.5: arah automation persis pipeline_v2.json. Run: python3 runner.py --demo"""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
TZ = ZoneInfo("Asia/Jakarta")

def log(step, msg): print(f"[{step}] {msg}")

def entitled(plan, fitur):
    m={"reminder_monthly":["reminder_wa"],"absensi_monthly":["auto_absen"],
       "bundling_monthly":["auto_absen","reminder_wa"]}
    return fitur in m.get(plan,[])

def solve_captcha(tipe):
    # cabang captcha_branch di JSON
    if tipe=="none": log("captcha","no_captcha -> submit langsung"); return True
    if tipe=="simple_image":
        log("captcha","simple_image (SIMAK/Moodle Aceh) -> ddddocr lokal <1s Rp0, retry max3x")
        return True
    if tipe=="recaptcha":
        log("captcha","reCAPTCHA/Turnstile -> CapSolver/2Captcha ~Rp200/15-30dt")
        return True
    log("captcha","gagal 3x -> wa_interaktif: kirim gambar ke WA, tunggu balasan 2 mnt")
    return False

def run_demo():
    log("cron_ingest","trigger absen 10m / reminder 60m")
    user={"nama":"demo-usk","kampus":"usk","plan":"bundling_monthly"}
    log("load_user",f"{user['nama']}@{user['kampus']} plan={user['plan']}")
    log("entitlement",f"absen={entitled(user['plan'],'auto_absen')} reminder={entitled(user['plan'],'reminder_wa')}")
    log("auth_session","sesi valid? tidak -> login via vault (password tak pernah plain)")
    solve_captcha("simple_image")  # ganti none/recaptcha/fail untuk coba cabang lain
    log("fetch","absen SIMKULIAH + assign Moodle + Classroom OAuth")
    log("normalize_dedupe","tugas_id=usk_a8e9b44be3f4 hash sama -> skip, hash beda -> baru")
    log("execute","auto_absen klik dalam window pre15/post30 + reminder_queue H-3/H-1/H-3jam")
    log("notify_wa","Baileys: KOMPUTASI NUMERIK | TUGAS 01 | 15 Okt | app.id/t/xxx")
    log("evidence","screenshot -> /evidence/demo-usk/2026-09-30/")
    print("OK runner searah pipeline_v2.json")

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--demo",action="store_true");a=ap.parse_args()
    run_demo() if a.demo else ap.print_help()
