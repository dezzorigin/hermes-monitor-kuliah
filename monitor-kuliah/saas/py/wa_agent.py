#!/usr/bin/env python3
"""WA agent (Baileys via n8n): perintah natural -> aksi setting -> fallback link web."""
import re
WEB = "https://appkamu.id"
def handle(pesan: str, user: dict) -> dict:
    p = pesan.lower()
    if re.search(r"geser|ubah|pindah.*jadwal", p):
        return {"aksi": "update_jadwal", "balas": f"Siap, jadwal diupdate. Cek {WEB}/jadwal"}
    if re.search(r"berhenti|stop|matiin.*reminder", p):
        return {"aksi": "stop_reminder", "balas": f"Reminder dimatikan. Atur lagi di {WEB}/reminder"}
    if re.search(r"tugas.*apa|cek.*tugas", p):
        return {"aksi": "list_tugas", "balas": "Tugas minggu ini: cek {link}".format(link=f"{WEB}/tugas")}
    if "captcha" in p or re.fullmatch(r"\d{4,6}", p.strip()):
        return {"aksi": "jawab_captcha", "balas": "Captcha diterima, lanjut login..."}
    return {"aksi": "bantuan", "balas": f"Gue bisa: ubah jadwal, stop reminder, cek tugas. Atau buka {WEB}"}
if __name__ == "__main__":
    for m in ["geser jadwal logika ke jam 3", "cek tugas apa aja", "48213", "halo"]:
        print(m, "->", handle(m, {})["balas"])
