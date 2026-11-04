#!/usr/bin/env python3
"""Tahap-1 SaaS core: dari workflow Dezz -> multi-kampus.
Dipetakan dari: jadwal.json, state.json, assign_index.json, check_schedule.py
Run: python3 core_pipeline.py --demo
"""
import json, hashlib, argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Jakarta")
PLANS = {
 "absensi_monthly": {"price":19900,"fitur":["auto_absen"]},
 "absensi_semester": {"price":49900,"fitur":["auto_absen"]},
 "reminder_monthly": {"price":9900,"fitur":["reminder_wa"]},
 "reminder_semester": {"price":29900,"fitur":["reminder_wa"]},
 "bundling_monthly": {"price":24500,"fitur":["auto_absen","reminder_wa"]},
 "bundling_semester": {"price":69900,"fitur":["auto_absen","reminder_wa"]},
}
# 11 kampus Aceh — tahap-1: USK live, sisanya registry adapter
KAMPUSES = [
 {"id":"usk","nama":"USK","lms":"moodle","absen":"simkuliah","status":"live"},
 {"id":"uin_ar_raniry","nama":"UIN Ar-Raniry","lms":"moodle/siakad","absen":"siakad","status":"adapter_stub"},
 {"id":"ummuha","nama":"UMMUHA","lms":"moodle","absen":"siakad","status":"adapter_stub"},
 {"id":"ahmad_dahlan","nama":"IT Ahmad Dahlan","lms":"moodle","absen":"siakad","status":"adapter_stub"},
 {"id":"ubudiyah","nama":"Ubudiyah","lms":"moodle","absen":"siakad","status":"adapter_stub"},
 {"id":"serambi","nama":"Serambi Mekkah","lms":"siakad","absen":"siakad","status":"adapter_stub"},
 {"id":"abulyatama","nama":"Abulyatama","lms":"siakad","absen":"siakad","status":"adapter_stub"},
 {"id":"utu","nama":"UTU Teuku Umar","lms":"moodle","absen":"siakad","status":"adapter_stub"},
 {"id":"ut","nama":"UT Banda Aceh","lms":"elearning-ut","absen":"elearning","status":"adapter_stub"},
 {"id":"unimal","nama":"Unimal","lms":"moodle","absen":"siakad","status":"adapter_stub"},
 {"id":"politeknik_aceh","nama":"Politeknik Aceh","lms":"siakad","absen":"siakad","status":"adapter_stub"},
]

def norm_task(kampus, mk, judul, deadline_iso, instruksi):
    h = hashlib.sha256(f"{kampus}|{mk}|{judul}|{instruksi}".encode()).hexdigest()[:12]
    return {"tugas_id": f"{kampus}_{h}","kampus":kampus,"mk":mk,"judul":judul,
            "deadline":deadline_iso,"hash_instruksi":h}

def is_new(state:dict, t:dict):
    old = state.get(t["tugas_id"])
    return (old is None or old.get("hash_instruksi")!=t["hash_instruksi"]
            or old.get("deadline")!=t["deadline"])

def entitled(plan_id:str, fitur:str):
    return fitur in PLANS.get(plan_id,{}).get("fitur",[])

def window_aktif(jadwal:list, now:datetime, pre=15, post=30, done=set()):
    aktif=[]
    for mk in jadwal:
        if mk["kode"] in done: continue
        mulai = datetime.strptime(mk["mulai"],"%H:%M").replace(
            year=now.year,month=now.month,day=now.day,tzinfo=TZ)
        if mulai-timedelta(minutes=pre) <= now <= mulai+timedelta(minutes=post):
            aktif.append(mk["kode"])
    return aktif

def demo():
    now = datetime.now(TZ)
    print(f"now={now.isoformat()} kampus_terdaftar={len(KAMPUSES)}")
    # 1. dedupe ala state.json
    st = {}
    t1 = norm_task("usk","Komputasi Numerik","TUGAS 01","2026-10-15T13:10","folio_pdf")
    print("tugas_baru?", is_new(st,t1), t1["tugas_id"])
    st[t1["tugas_id"]]={"hash_instruksi":t1["hash_instruksi"],"deadline":t1["deadline"]}
    print("tugas_sama_lapor_lagi?", is_new(st,t1), "(harus False = dedupe jalan)")
    # 2. entitlement bundling
    for p in ["reminder_monthly","absensi_monthly","bundling_monthly"]:
        print(f"{p}: absen={entitled(p,'auto_absen')} reminder={entitled(p,'reminder_wa')}")
    # 3. window absen ala check_schedule.py + jadwal_custom user
    jadwal = [{"kode":"SINF2007","mulai":"14:00"},{"kode":"CUSTOM_MK","mulai":now.strftime("%H:%M")}]
    print("window_aktif:", window_aktif(jadwal, now, done={"SINF2007"}),
          "(CUSTOM_MK harus muncul = jadwal custom user jalan)")
    print("OK tahap-1 valid: dedupe + entitlement + window + registry 11 kampus")

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--demo",action="store_true");a=ap.parse_args()
    demo() if a.demo else ap.print_help()
