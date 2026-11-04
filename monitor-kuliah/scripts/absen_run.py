#!/usr/bin/env python3
"""absen_run.py — watcher absensi SIMKULIAH untuk satu run cron.

Alur per akun (dezz -> rizki):
  1. Ambil password dari vault Hermes (decrypt langsung; tidak diprint/ditulis file).
  2. Login via simkuliah_login.login() (requests session + ddddocr).
  3. GET /index.php/absensi -> parse status per MK:
       - tombol konfirmasi-kehadiran-*  -> absen via POST konfirmasi_kehadiran
       - 'sudah absen' / 'belum waktu' / 'dosen belum absen' -> catat status
  4. Update absen_state.json + laporan JSON ke stdout.

Pemakaian: python3 absen_run.py            -> proses semua akun pending
           python3 absen_run.py dezz       -> hanya dezz
"""
import json, os, re, sys, time
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, "/opt/data/monitor-kuliah/scripts")
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import simkuliah_login as sk

TZ = ZoneInfo("Asia/Jakarta")
BASE = "https://simkuliah.usk.ac.id"
STATE = "/opt/data/monitor-kuliah/absen_state.json"
EVID = "/opt/data/monitor-kuliah/evidence"
VAULT_KEY = "/opt/data/vault/vault.key"
VAULT_ENC = "/opt/data/vault/vault.json.enc"

AKUN = {
    "dezz":  {"npm": "250810701100090", "vault": "vault_3f284af2e789"},
    "rizki": {"npm": "250810701100049", "vault": "vault_b37c19ed6f0b"},
}

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def vault_password(item_id):
    from cryptography.fernet import Fernet
    key = open(VAULT_KEY, "rb").read().strip()
    data = json.loads(Fernet(key).decrypt(
        open(VAULT_ENC, "rb").read()).decode())
    for it in data["items"]:
        if it["id"] == item_id:
            return it["secret"]["password"]
    raise KeyError(item_id)


def load_state():
    try:
        d = json.load(open(STATE))
    except Exception:
        d = {}
    if d.get("tanggal") != datetime.now(TZ).strftime("%Y-%m-%d"):
        d = {"tanggal": datetime.now(TZ).strftime("%Y-%m-%d"),
             "akun": {"dezz": {"npm": AKUN["dezz"]["npm"], "done": [],
                               "pending": []},
                      "rizki": {"npm": AKUN["rizki"]["npm"], "done": [],
                                "pending": []}}}
    d.setdefault("akun", {})
    for a, meta in AKUN.items():
        d["akun"].setdefault(a, {"npm": meta["npm"], "done": [], "pending": []})
    return d


def parse_absensi(html):
    """Ringkas halaman absensi: status global + tombol + parameter POST-nya."""
    info = {"tombol": [], "status_teks": None, "rows": []}
    low = html.lower()
    for kw in ("belum masuk waktu absen", "anda sudah absen",
               "dosen belum absen", "sudah presensi"):
        if kw in low:
            info["status_teks"] = kw
            break

    # tombol konfirmasi — inline script berisi semua parameter
    keys = ["kelas", "kd_mt_kul8", "jadwal_mulai", "jadwal_berakhir",
            "pertemuan", "sks_mengajar", "id"]

    # Pola A (format 2026): tombol + blok JS 'var kelas = ...; var kd_mt_kul_8...'
    for m in re.finditer(
            r"konfirmasi-kehadiran-(\d+)[\"']?\)\.on\(\"click\""
            r"[\s\S]{0,3000}?var kelas = \\?'([^']*)\\?';"
            r"[\s\S]*?var kd_mt_kul_8 = \\?'([^']*)\\?';"
            r"[\s\S]*?var jadwal_mulai = \\?'([^']*)\\?';"
            r"[\s\S]*?var jadwal_berakhir = \\?'([^']*)\\?';"
            r"[\s\S]*?var pertemuan = \\?'([^']*)\\?';"
            r"[\s\S]*?var sks_mengajar = \\?'([^']*)\\?';"
            r"[\s\S]*?var id = \\?'([^']*)\\?';",
            html):
        tid = m.group(1)
        vals = list(m.groups()[1:])
        info["tombol"].append({"id_tombol": tid,
                               "params": dict(zip(keys, vals))})

    # Pola B (lama): konfirmasiKehadiran('arg1','arg2',...)
    for m in re.finditer(
            r"konfirmasi-kehadiran-(\d+)[\s\S]{0,4000}?konfirmasiKehadiran\(([^)]*)\)",
            html):
        tid, args = m.group(1), m.group(2)
        vals = [a.strip().strip("'\"") for a in args.split(",")]
        params = dict(zip(keys, vals))
        info["tombol"].append({"id_tombol": tid, "params": params})

    # fallback: pola onclick langsung di tag button
    if not info["tombol"]:
        for m in re.finditer(
                r"id=\"konfirmasi-kehadiran-(\d+)\"[^>]*onclick=\"([^\"]+)\"",
                html):
            tid, oc = m.group(1), m.group(2)
            am = re.search(r"\((.*)\)", oc)
            if am:
                vals = [a.strip().strip("'\"") for a in am.group(1).split(",")]
                keys = ["kelas", "kd_mt_kul8", "jadwal_mulai", "jadwal_berakhir",
                        "pertemuan", "sks_mengajar", "id"]
                info["tombol"].append(
                    {"id_tombol": tid, "params": dict(zip(keys, vals))})

    # rows: ambil kode MK dari tabel untuk map tombol->MK
    for m in re.finditer(r"(SINF\d{4}|MKWU\d{4})", html):
        info["rows"].append(m.group(1))
    info["rows"] = sorted(set(info["rows"]))
    return info


def proses_akun(nama, target_mk):
    meta = AKUN[nama]
    res = {"akun": nama, "npm": meta["npm"], "hasil": [], "error": None}
    try:
        pw = vault_password(meta["vault"])
    except Exception as e:
        res["error"] = f"vault: {e}"
        return res

    sess, log = sk.login(meta["npm"], pw, max_retry=6,
                         workdir="/opt/data/monitor-kuliah/tmp")
    res["login_log"] = log[-3:]  # 3 attempt terakhir saja
    if not sess:
        res["error"] = "login gagal setelah retry"
        return res

    # siapa yang login
    try:
        r = sess.get(BASE + "/index.php/absensi",
                     headers={"User-Agent": UA}, verify=False, timeout=20)
        html = r.text
    except Exception as e:
        res["error"] = f"GET absensi: {e}"
        return res
    m = re.search(r"(NABIL AULIA DIKA|MUHAMMAD RIZKI)", html)
    if m:
        res["login_as"] = m.group(1)

    info = parse_absensi(html)
    res["status_teks"] = info["status_teks"]
    res["mk_terlihat"] = info["rows"]

    # simpan snapshot html buat bukti/debug
    ts = datetime.now(TZ).strftime("%Y%m%d_%H%M")
    open(f"{EVID}/absensi_page_{ts}_{nama}.html", "w").write(html)

    # match tombol -> MK lewat kd_mt_kul8? kd_mt_kul8 bukan kode MK langsung.
    # Strategi: kalau cuma 1 MK target & ada tombol, pakai tombol pertama.
    # Kalau beberapa, cocokkan urutan tombol dgn kemunculan kode di html sekitar.
    tombol = info["tombol"]
    if not tombol:
        return res

    # posisi kode MK di html vs posisi tombol id -> mapping terdekat
    def map_mk(tid):
        pos = html.find(f"konfirmasi-kehadiran-{tid}")
        best, bdist = None, 1 << 30
        for m2 in re.finditer(r"(SINF\d{4}|MKWU\d{4})", html):
            d = abs(m2.start() - pos)
            if d < bdist:
                bdist, best = d, m2.group(1)
        return best

    for t in tombol:
        mk = map_mk(t["id_tombol"]) or "?"
        entry = {"mk": mk, "id_tombol": t["id_tombol"]}
        if target_mk and mk not in target_mk and "?" not in target_mk:
            # tombol utk MK lain — tetap absen juga (aman, absen = presensi)
            pass
        out = sk.konfirmasi(sess, t["params"])
        entry["response"] = out[:120]
        # verifikasi ulang
        try:
            r2 = sess.get(BASE + "/index.php/absensi",
                          headers={"User-Agent": UA}, verify=False, timeout=20)
            i2 = parse_absensi(r2.text)
            masih = [b["id_tombol"] for b in i2["tombol"]]
            sudah = "sudah" in out.lower()  # 'Anda sudah melakukan presensi'
            entry["sukses"] = (t["id_tombol"] not in masih
                               or out.strip() == "success" or sudah
                               or "anda sudah absen" in r2.text.lower())
        except Exception:
            entry["sukses"] = (out.strip() == "success"
                               or "sudah" in out.lower())
        res["hasil"].append(entry)
        time.sleep(1)
    return res


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    target = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
    state = load_state()
    laporan = []

    for nama in ("dezz", "rizki"):
        if only and nama != only:
            continue
        r = proses_akun(nama, target)
        laporan.append(r)
        st = state["akun"][nama]
        for h in r.get("hasil", []):
            if h.get("sukses") and h["mk"] != "?":
                if h["mk"] not in st["done"]:
                    st["done"].append(h["mk"])
                if h["mk"] in st.get("pending", []):
                    st["pending"].remove(h["mk"])
            elif h.get("sukses") and h["mk"] == "?":
                pass
        # kalau halaman bilang 'anda sudah absen' dan tidak ada tombol
        if r.get("status_teks") == "anda sudah absen" and not r.get("hasil"):
            for mk in target:
                if mk not in st["done"]:
                    st["done"].append(mk)
                if mk in st.get("pending", []):
                    st["pending"].remove(mk)
        if r.get("login_as"):
            st["login_as"] = r["login_as"]
        st["note"] = f"cek {datetime.now(TZ).strftime('%H:%M')} WIB: {r.get('status_teks') or '-'}; tombol={len(r.get('hasil', []))}"
        time.sleep(2)

    state["last_check"] = datetime.now(TZ).strftime("%Y-%m-%dT%H:%MWIB")
    state["captcha_solver"] = "ddddocr venv .venv-captcha (requests-session login)"
    json.dump(state, open(STATE, "w"), indent=1, ensure_ascii=False)

    print(json.dumps({"ts": datetime.now(TZ).isoformat(timespec="seconds"),
                      "laporan": laporan}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
