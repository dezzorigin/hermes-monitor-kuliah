# Cara Pakai — Hermes Monitor Kuliah

## Yang bisa jalan tanpa kredensial (mode aman)

Semua perintah di bawah ini tidak menyentuh jaringan kampus dan tidak
butuh password. Cocok untuk verifikasi setelah clone.

```bash
# 1. Cek jadwal hari ini (JSON: now, hari, absen_aktif)
#    Skrip memakai path /opt/data/... — untuk mode aman, patch path-nya:
python3 - <<'EOF'
import importlib.util, io, contextlib
spec = importlib.util.spec_from_file_location(
    "cs", "monitor-kuliah/scripts/check_schedule.py")
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)
cs.JADWAL_PATH = "monitor-kuliah/jadwal.json"
cs.STATE_PATH = "/tmp/hmk-state.json"
open("/tmp/hmk-state.json", "w").write('{"tanggal":"2000-01-01","done":[]}')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    cs.main()
print(buf.getvalue())
EOF
```

Output asli (Kamis 19 Nov 2026, 16:18 WIB — 2 menit sebelum jendela
Sistem Operasi dibuka):

```json
{"now": "2026-11-19T16:18:26.940211+07:00", "hari": "Kamis", "absen_aktif": []}
```

Benar kosong: jendela `check_schedule` untuk SINF2023 baru buka
16:20 (mulai 16:35 − 15 mnt).

```bash
# 2. Demo pipeline SaaS (tanpa login, tanpa WA)
python3 monitor-kuliah/saas/runner.py --demo
# -> "OK runner searah pipeline_v2.json"

# 3. Jadwal cron SaaS
python3 monitor-kuliah/saas/py/scheduler.py
# -> absen tiap 10 menit, reminder tiap 60 menit

# 4. Tes lengkap (11 tes, tanpa jaringan/kredensial)
pip install pytest
python3 -m pytest tests/ -q

# 5. Lint + secret-scan + advisory sweep
pip install ruff
ruff check .
python3 scripts/advisory-sweep.py
```

## Yang butuh server Hermes (tidak bisa dari clone biasa)

Skrip absen memakai path absolut `/opt/data/monitor-kuliah/` dan
vault Hermes di `/opt/data/vault/`. Di server, tata letaknya:

```
/opt/data/monitor-kuliah/
├── jadwal.json            # disalin dari repo
├── scripts/               # check_schedule.py, absen_gate.py,
│                          # absen_run.py, simkuliah_login.py, krs_login.py
├── state.json             # dedupe tugas (dibuat cron)
├── absen_state.json       # done per akun per tanggal (dibuat cron)
├── evidence/              # screenshot bukti absen
├── drafts/                # draft tugas
└── .venv-captcha/         # venv ddddocr + requests + pillow
/opt/data/vault/
├── vault.key              # kunci Fernet (JANGAN di-copy ke mana pun)
└── vault.json.enc         # vault terenkripsi
```

Setup awal di server (sekali saja):

```bash
bash install_dependencies.sh   # buat direktori + venv captcha (uv + ddddocr)
```

Lalu cron Hermes memuat `cron/cron_jobs.json` (2 job — lihat
[ARCHITECTURE.md](ARCHITECTURE.md)). Password diambil dari vault
langsung di memori; tidak pernah ditulis ke file atau log.

## Mengubah jadwal

Edit `monitor-kuliah/jadwal.json` (satu MK = satu objek: `kode`,
`nama`, `sks`, `kelas`, `hari`, `mulai`, `selesai`, `ruang`,
`jenis` teori/praktikum). Setelah edit, jalankan tes — tes akan
menangkap bentrok jam yang tidak didokumentasikan:

```bash
python3 -m pytest tests/test_schedule.py -q
```

Catatan: Sabtu 08:00 memang bentrok (Praktikum PBO + Pendidikan
Agama) — keduanya dicek, dan tes mengunci fakta itu.

## Landing etalase

`index.html` + `styles.css` + `app.js` adalah etalase statis untuk
Cloudflare Pages, bukan produknya. Tidak butuh build:

```bash
python3 -m http.server 8461 --bind 127.0.0.1   # lalu buka :8461
```

Jam "sekarang" di strip atas dihitung live di browser (zona
Asia/Jakarta); kelas yang sedang berlangsung disorot Stabilo.
