#!/usr/bin/env python3
"""simkuliah_login.py — full-Python login SIMKULIAH USK + bypass captcha.

Alur:
  1. requests.Session -> GET / -> ambil cookie (ci_session) + URL captcha_image
  2. GET captcha_image (session SAMA — captcha di-bind ke session tsb)
  3. OCR lokal ddddocr -> 5 digit
  4. POST /index.php/login/auth {username,password,captcha_answer}
  5. Kalau captcha salah -> gambar baru -> ulangi (max N kali)
  6. Verdict login dari redirect/isi halaman dashboard

Trik kunci: session harus konsisten (captcha di-bind ke PHP session),
dan kirim 't' cache-buster sama kayak browser.

Butuh: requests + ddddocr (venv /opt/data/monitor-kuliah/.venv-captcha)
       -> install requests: uv pip install --python .venv-captcha/bin/python requests
"""
import re, sys, time, urllib.parse

BASE = "https://simkuliah.usk.ac.id"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import ddddocr
OCR = ddddocr.DdddOcr(show_ad=False)


def fetch_login(sess):
    """GET halaman login, kembalikan (html, captcha_url)."""
    r = sess.get(BASE + "/", headers={"User-Agent": UA}, verify=False, timeout=20)
    r.raise_for_status()
    m = re.search(r'src="([^"]*captcha_image[^"]*)"', r.text)
    cap_url = m.group(1) if m else BASE + "/index.php/login/captcha_image"
    return r.text, cap_url


def solve_captcha(sess, cap_url, save_path=None):
    """Download captcha di session yang sama -> OCR -> (jawaban, png_path)."""
    # cache-buster baru tiap request, kayak JS-nya
    sep = "&" if "?" in cap_url else "?"
    url = f"{cap_url}{sep}t={int(time.time())}"
    r = sess.get(url, headers={"User-Agent": UA, "Referer": BASE + "/"},
               verify=False, timeout=20)
    r.raise_for_status()
    png = r.content
    if save_path:
        open(save_path, "wb").write(png)
    return OCR.classification(png), png


def post_login(sess, username, password, captcha):
    """POST /index.php/login/auth. Return (response, verdict)."""
    r = sess.post(
        BASE + "/index.php/login/auth",
        data={"username": username, "password": password, "captcha_answer": captcha},
        headers={"User-Agent": UA, "Referer": BASE + "/"},
        verify=False, timeout=20, allow_redirects=True,
    )
    url_now = r.url.lower()
    body = r.text
    # SIMKULIAH redirect ke dashboard kalau sukses; tetap di /login kalau gagal
    if "/login" in url_now or "login/auth" in url_now:
        if "captcha" in body.lower() and ("salah" in body.lower() or "verifikasi" in body.lower()):
            return r, "captcha_salah"
        return r, "gagal"          # masih halaman login (password salah / captcha salah)
    return r, "ok"                 # dashboard/absensi page


def login(username, password, max_retry=6, workdir="/opt/data/monitor-kuliah/tmp"):
    """Loop login sampe masuk / retry habis. Return (session_terotentikasi|None, log)."""
    sess = requests.Session()
    log = []
    for attempt in range(1, max_retry + 1):
        _, cap_url = fetch_login(sess)          # captcha baru tiap gagal
        save = f"{workdir}/cap_{int(time.time())}_{attempt}.png"
        jawaban, png = solve_captcha(sess, cap_url, save_path=save)
        jawaban = re.sub(r"\D", "", jawaban)[:5]     # pastikan 5 digit angka
        log.append(f"try{attempt}: ocr='{jawaban}' file={save}")
        r, verdict = post_login(sess, username, password, jawaban)
        log.append(f"  -> {verdict} @ {r.url}")
        if verdict == "ok":
            return sess, log
        # 'captcha_salah'/'gagal' -> loop: fetch_login lagi (captcha auto-refresh)
    return None, log


def absen_terbuka(sess):
    """GET halaman absensi -> list tombol konfirmasi-kehadiran + parameter inline-nya."""
    r = sess.get(BASE + "/index.php/absensi", headers={"User-Agent": UA},
                 verify=False, timeout=20)
    # tiap tombol: konfirmasi-kehadiran-<id> dengan inline onclick berisi
    # kelas, kd_mt_kul8, jadwal_mulai, jadwal_berakhir, pertemuan, sks_mengajar, id
    out = []
    for m in re.finditer(
            r"konfirmasi-kehadiran-(\d+)[^>]*onclick=\"([^\"]+)\"", r.text):
        out.append({"id_tombol": m.group(1), "onclick": m.group(2)})
    return r.text, out


def konfirmasi(sess, params: dict):
    """POST langsung ke konfirmasi_kehadiran (jangan klik SweetAlert)."""
    r = sess.post(BASE + "/index.php/absensi/konfirmasi_kehadiran",
                  data=params, headers={"User-Agent": UA,
                                        "Referer": BASE + "/index.php/absensi",
                                        "X-Requested-With": "XMLHttpRequest"},
                  verify=False, timeout=20)
    return r.text.strip()  # 'success' = absen masuk


if __name__ == "__main__":
    import json, getpass
    user = sys.argv[1] if len(sys.argv) > 1 else input("NPM: ")
    pw = sys.argv[2] if len(sys.argv) > 2 else getpass.getpass("Password: ")
    sess, log = login(user, pw)
    print("\n".join(log))
    if not sess:
        print("LOGIN GAGAL setelah semua retry"); sys.exit(1)
    html, tombol = absen_terbuka(sess)
    print(f"login OK; tombol presensi terdeteksi: {len(tombol)}")
    for t in tombol:
        print(" ", t["id_tombol"], "->", t["onclick"][:120])
