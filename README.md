# Hermes Monitor Kuliah

Monitor kuliah otomatis untuk mahasiswa Informatika USK — dijalankan
sebagai **cron Hermes**, bukan server web. Dua pekerjaan: **absensi
SIMKULIAH** yang time-critical (dicek tiap 10 menit, hanya bangun di
dalam jendela kuliah) dan **monitor tugas** Moodle + Google Classroom
(4 kali sehari, dengan dedupe supaya tiap tugas hanya dilaporkan
sekali).

> **Live:** https://hermes-monitor-kuliah.pages.dev/ — landing etalase
> (papan jadwal + status monitor). Produknya adalah automation Python
> di repo ini; halaman live bukan produknya.

## Status Proyek

**Proper + live** (P1 #46, 19 Nov 2026): gitleaks bersih atas seluruh
riwayat, CI hijau (pytest + ruff + gitleaks + OSV + E2E landing),
landing live di Cloudflare Pages.

## Yang dimonitor

| Sumber | Jadwal | Aksi |
|---|---|---|
| SIMKULIAH absensi | tiap 10 mnt, di jendela kuliah | auto-absen + verifikasi |
| Moodle elearning USK | 06.00, 12.00, 18.00, 00.00 WIB | lapor tugas/pengumuman baru |
| Google Classroom (2 akun) | sama | lapor tugas/pengumuman baru |

Jadwal kuliah: **13 mata kuliah, 21 SKS, Senin–Sabtu** (lihat
`monitor-kuliah/jadwal.json`). Sabtu 08.00 ada dua MK bersamaan —
keduanya dicek.

## Cara kerja (ringkas)

1. **Gerbang** — `absen_gate.py` jalan tiap 10 menit. Di luar jendela
   kuliah output-nya konstan `idle`, agent tidak bangun. Di dalam
   jendela (mulai−10 mnt s/d selesai+10 mnt) output berubah tiap tick.
2. **Login** — `simkuliah_login.py`: session + captcha 5 digit
   dipecahkan lokal dengan ddddocr, retry sampai 6 kali.
3. **Absen** — `absen_run.py`: baca halaman absensi, parse tombol
   `konfirmasi-kehadiran-*`, POST konfirmasi langsung (tanpa
   mengandalkan klik dialog SweetAlert), verifikasi ulang, catat di
   `absen_state.json`.
4. **Dedupe tugas** — hash instruksi yang sama tidak dilaporkan ulang
   (`state.json`). Kuis/ujian hanya dilaporkan; tugas tidak pernah
   di-submit tanpa konfirmasi.

Detail lengkap: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Diagram: [docs/diagrams/architecture.html](docs/diagrams/architecture.html).

## Struktur Proyek

```
monitor-kuliah/
├── jadwal.json            # 13 MK, 21 SKS — sumber kebenaran jadwal
├── scripts/               # check_schedule, absen_gate, absen_run,
│                          # simkuliah_login, krs_login
├── saas/                  # arah multi-kampus (pipeline, runner demo)
├── state.json             # dedupe tugas
├── absen_state.json       # MK sudah absen hari ini
├── drafts/                # draft tugas + PDF
└── evidence/              # screenshot bukti absen
cron/cron_jobs.json         # 2 job Hermes
skills/productivity/monitor-kuliah-soul/   # soul + pitfall terbukti
config/                    # cuplikan config (Telegram)
docs/                      # DESIGN, ARCHITECTURE, USAGE, TESTING, DEPLOY
index.html / styles.css / app.js   # landing etalase (Pages)
tests/                     # 11 tes pytest
```

## Mode aman (tanpa kredensial)

```bash
# Cek jadwal hari ini (path di-patch ke repo lokal)
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

# Demo pipeline SaaS (tanpa login, tanpa WA)
python3 monitor-kuliah/saas/runner.py --demo

# Tes + lint + sweep
python3 -m pytest tests/ -q
ruff check .
python3 scripts/advisory-sweep.py
```

Output asli (Kamis 19 Nov 2026, 16:18 WIB):

```json
{"now": "2026-11-19T16:18:26.940211+07:00", "hari": "Kamis", "absen_aktif": []}
```

Kosong dengan benar — jendela Sistem Operasi baru dibuka 16:20.

> Login nyata + vault hanya ada di server Hermes
> (`/opt/data/monitor-kuliah/`, `/opt/data/vault/`). Lihat
> [docs/USAGE.md](docs/USAGE.md). Jangan pernah menulis password ke
> file, log, atau chat.

## Tech Stack

Python 3.12 (stdlib + `requests`, `urllib3`, `cryptography`,
`ddddocr`, `pillow`, `reportlab` — dipin di `requirements.txt`).
Landing: HTML + CSS + JS murni, tanpa build.

## Pengujian

11 tes pytest (jadwal, jendela absen, parser halaman absensi, demo
runner, scheduler) — tanpa jaringan dan tanpa kredensial. CI juga
menjalankan ruff, gitleaks atas seluruh riwayat, advisory-sweep OSV,
html-validate + gate P0 anti-slop, dan E2E Playwright atas landing
(hanya di CI). Lihat [docs/TESTING.md](docs/TESTING.md).

## Desain landing

Referensi: NEVERBLAND "School Education App — timetable V2"
(Dribbble) untuk struktur tabel jadwal; EduView (Smit M. Solanki)
untuk kartu status. Palet terang papan pengumuman kampus (kertas,
hijau papan, stabilo) dengan detail khas stempel status karet.
Kontrak lengkap: [docs/DESIGN.md](docs/DESIGN.md).

## Lisensi

MIT — lihat [LICENSE](./LICENSE).

---
_Dikembangkan oleh **dezzorigin** (Nabil Aulia Dika)._
