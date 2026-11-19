# Testing — Hermes Monitor Kuliah

## Ringkas

| Lapisan | Perintah | Keterangan |
|---|---|---|
| Unit + integrasi lokal | `python3 -m pytest tests/ -q` | 11 tes, tanpa jaringan/kredensial |
| Compile | `python3 -m py_compile <semua .py>` | Dijalankan job CI `python-test` |
| Lint | `ruff check .` | E4/E7/E9/F (lihat `pyproject.toml`) |
| Secret-scan | gitleaks (job CI, `fetch-depth: 0`) | Riwayat penuh; lokal: `gitleaks git .` |
| Advisory | `python3 scripts/advisory-sweep.py` | OSV PyPI; HIGH/CRITICAL = gagal |
| Statis landing | `npm run validate` | Gate P0 anti-slop + tag OG + data jadwal |
| HTML | `npx html-validate index.html` | — |
| E2E landing | `npm run e2e` | Playwright, **hanya di CI** |

## Tes pytest (`tests/test_schedule.py`)

11 tes, semuanya menjalankan kode ASLI repo:

1. `test_jadwal_valid_13_mk_21_sks` — jadwal.json: 13 MK, 21 SKS,
   semua field ada, jam valid, mulai < selesai.
2. `test_jadwal_bentrok_sabtu_terdokumentasi` — satu-satunya bentrok
   adalah Sabtu 08:00 (SINF2017 + MKWU2001); bentrok lain = gagal.
3. `test_jadwal_hari_tercakup` — 6 hari Senin–Sabtu, tanpa Minggu.
4. `test_check_schedule_load_jadwal` — `load_jadwal()` baca 13 MK.
5. `test_check_schedule_load_absen_done` — state hari ini vs tanggal
   basi vs file hilang.
6. `test_check_schedule_main_output_asli` — `main()` end-to-end dengan
   path di-patch: stdout JSON `{now, hari, absen_aktif}`.
7. `test_window_check_schedule_untuk_mk_hari_ini` — konstanta jendela
   15/30 mnt dan lebar jendela 45 mnt.
8. `test_parse_absensi_pola_a_dan_status` — parser halaman absensi
   (Pola A var-style) di atas fixture HTML: 7 parameter tombol
   diekstrak persis.
9. `test_parse_absensi_status_sudah_absen` — keyword "anda sudah absen".
10. `test_parse_absensi_tanpa_tombol` — "dosen belum absen", tanpa tombol.
11. `test_runner_demo_output` + `test_scheduler_cron_10_dan_60_menit` —
    demo pipeline SaaS + jadwal cron (absen 10 mnt, reminder 60 mnt).

Tes 8–10 memuat `absen_run.py` dengan stub `requests`/`urllib3`/
`simkuliah_login`, karena import aslinya butuh ddddocr + path
`/opt/data`. Parser yang diuji adalah fungsi aslinya, bukan tiruan.

## Yang TIDAK diuji di CI (dan kenapa)

- **Login SIMKULIAH/KRS sungguhan** — butuh kredensial vault + akses
  ke sistem kampus. Tidak pernah dijalankan di CI. Verifikasi login
  dilakukan manual di server Hermes, dan buktinya berupa screenshot
  di `monitor-kuliah/evidence/`.
- **POST konfirmasi kehadiran** — aksi nyata ke sistem kampus.
  Parser + verifikasi diuji di atas fixture; aksi nyatanya hanya
  lewat cron di jendela absen.
- **Screenshot/video demo landing** — Chromium tidak bisa start di
  sandbox VM ini (mmap memfd ditolak). Follow-up: ambil dari browser
  live. Bukan gate merge.

## Hasil lokal terakhir (19 Nov 2026, VM dev)

- `py_compile` semua modul: OK.
- `pytest`: tidak bisa jalan lokal (pytest belum terpasang; instalasi
  lokal dilarang aturan sandbox) — dijalankan CI.
- Dry-run `check_schedule.py` (path di-patch): Kamis 16:18 WIB →
  `{"hari": "Kamis", "absen_aktif": []}` (benar; jendela SO buka 16:20).
- `runner.py --demo`: `OK runner searah pipeline_v2.json`.
- `scripts/advisory-sweep.py`: 6 paket, OK (tanpa HIGH/CRITICAL).
- `node scripts/check-static.mjs`: semua gate lolos.
- Gitleaks 8.24.3 lokal: 6 commit, `no leaks found`.
