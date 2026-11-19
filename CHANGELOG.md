# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelot.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-11-19

### Added
- Landing etalase statis (`index.html`, `styles.css`, `app.js`): papan
  jadwal mingguan dari `jadwal.json` (13 MK, 21 SKS) + papan status
  monitor; live di Cloudflare Pages.
- `docs/` lengkap: `DESIGN.md` (kontrak arah desain), `ARCHITECTURE.md`,
  `USAGE.md`, `TESTING.md`, `DEPLOY.md`, diagram SVG
  `docs/diagrams/architecture.html`.
- `tests/test_schedule.py` — 11 tes nyata (jadwal, jendela absen,
  parser halaman absensi, demo runner, scheduler), tanpa
  jaringan/kredensial.
- CI (`.github/workflows/ci.yml`): py_compile + pytest, ruff, gitleaks
  (riwayat penuh), advisory-sweep OSV, html-validate + gate P0 + OG,
  Playwright E2E (hanya CI), smoke file deploy.
- `scripts/advisory-sweep.py` (OSV PyPI) + `requirements.txt` dengan
  6 dependensi produksi dipin.
- `og-image.png` (1200×630, dibuat dengan PIL mengikuti palet landing).
- `scripts/check-static.mjs` (gate P0 anti-slop + tag OG/Twitter +
  data jadwal) dan `scripts/make-og-image.py`.

### Fixed
- Hapus import tak terpakai (ruff F401) di `check_schedule.py`,
  `absen_run.py`, `simkuliah_login.py`, `core_pipeline.py`,
  `runner.py`; hapus variabel lokal tak terpakai (F841) di
  `captcha_solver.py`, `krs_login.py`, `simkuliah_login.py`.
- README lama menyebut `npm install` / `npm run dev` untuk repo
  Python — diganti README standar yang menjelaskan monitor ini.

### Security
- Gitleaks 8.24.3 atas seluruh riwayat (6 commit): no leaks found.
- Job CI gitleaks (`fetch-depth: 0`) wajib hijau sebelum merge.

## [Unreleased]

### Added
- Initial Python project setup for Hermes Monitor Kuliah
- Course tracking components
- Dashboard visualization
- Data persistence with Supabase
- Notification system setup

### Changed
- Updated Python dependencies to latest stable versions
- Improved dashboard visualization with Charts.js
- Enhanced data persistence with Supabase
- Refactored notification system for reliability

### Fixed
- Fixed course tracking bug
- Fixed dashboard refresh issues
- Fixed notification delivery problems

### Security
- Updated dependency versions to patch vulnerabilities
- Fixed potential data exposure issues
- Fixed Supabase RLS policy vulnerabilities

## [1.0.0] - 2024-08-03

### Added
- Initial Hermes Monitor Kuliah setup
- Course tracking system
- Dashboard visualization
- Supabase integration
- Notification system
