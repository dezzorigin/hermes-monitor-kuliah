# Arsitektur — Hermes Monitor Kuliah

Monitor kuliah otomatis untuk satu mahasiswa Informatika USK, dijalankan
sebagai **cron Hermes** (bukan server web). Ada dua pekerjaan yang
berjalan berdampingan: **absensi SIMKULIAH** (time-critical, tiap
10 menit) dan **monitor tugas** (Moodle + Google Classroom, 4 kali
sehari). Keduanya dikoordinasi satu skill (`monitor-kuliah-soul`) dan
satu file jadwal (`jadwal.json`).

Diagram visual: [diagrams/architecture.html](diagrams/architecture.html).

## Komponen

| Komponen | File | Tugas |
|---|---|---|
| Jadwal | `monitor-kuliah/jadwal.json` | 13 MK, 21 SKS, Senin–Sabtu, WIB. Satu-satunya sumber kebenaran jadwal. |
| Cek jadwal | `monitor-kuliah/scripts/check_schedule.py` | MK aktif sekarang? Jendela mulai−15 mnt s/d mulai+30 mnt. Output JSON. |
| Gerbang absen | `monitor-kuliah/scripts/absen_gate.py` + `scripts/absen_gate.sh` | Dipicu tiap 10 mnt. Di luar jendela output konstan `idle` → agent tidak bangun. Di dalam jendela output berubah tiap tick → agent jalan. Jendela: mulai−10 mnt s/d selesai+10 mnt. |
| Pelaksana absen | `monitor-kuliah/scripts/absen_run.py` | Login → GET `/index.php/absensi` → parse tombol → POST konfirmasi → verifikasi ulang → tulis `absen_state.json`. |
| Login SIMKULIAH | `monitor-kuliah/scripts/simkuliah_login.py` | `requests.Session` + captcha 5 digit dipecahkan lokal (ddddocr), retry sampai 6 kali. |
| Login KRS | `monitor-kuliah/scripts/krs_login.py` | Login KRS USK (Laravel): CSRF `_token` + captcha, pola sama. |
| Cron | `cron/cron_jobs.json` | 2 job: `monitor-tugas-dezz` (4×/hari) dan `absen-watcher-dezz` (tiap 10 mnt, via gate). |
| Soul/skill | `skills/productivity/monitor-kuliah-soul/SKILL.md` | Persona + aturan mengikat + pitfall terbukti (captcha, SweetAlert, re-login Moodle). |
| State tugas | `monitor-kuliah/state.json` | Dedupe tugas: `tugas_id → {deadline, hash_instruksi, last_reported}`. |
| State absen | `monitor-kuliah/absen_state.json` | MK yang sudah absen hari ini, per akun, per tanggal. |
| SaaS (tahap awal) | `monitor-kuliah/saas/` | Arah multi-kampus: pipeline JSON, runner demo, scheduler, adapter per kampus, solver captcha berlapis, agen WA. Bukan produk live. |
| Draft tugas | `monitor-kuliah/drafts/` + `generate_pdfs.py` | Draft jawaban (Markdown) + PDF-nya. |

## Alur absen (satu tick)

```
cron tiap 10 mnt
  └─ absen_gate.sh → absen_gate.py
       ├─ di luar jendela  → "idle" (agent diam)
       └─ di dalam jendela → "SINF2023(pending:dezz) @ 16:35"
            └─ absen_run.py
                 ├─ decrypt password dari vault Hermes (Fernet;
                 │  password tidak pernah di-print / ditulis file)
                 ├─ simkuliah_login.login() — session + ddddocr
                 ├─ GET /index.php/absensi
                 ├─ parse_absensi(): tombol konfirmasi-kehadiran-*
                 │  (Pola A var-style 2026 + Pola B legacy + onclick)
                 ├─ POST /index.php/absensi/konfirmasi_kehadiran
                 │  (langsung, tanpa klik dialog SweetAlert)
                 ├─ verifikasi: GET ulang, tombol hilang / "success"
                 └─ absen_state.json: MK masuk daftar done hari ini
```

Kenapa POST langsung, bukan klik tombol? Dialog konfirmasi SweetAlert
di SIMKULIAH tidak andal diklik — server bisa membalas "sudah presensi"
padahal belum. POST langsung dengan parameter yang diekstrak dari
inline script tombol adalah jalur yang terbukti (lihat SKILL.md).

## Alur monitor tugas (4× sehari)

```
cron 06.00 / 12.00 / 18.00 / 00.00 WIB
  ├─ Moodle elearning.usk.ac.id — assignment, kuis, forum, timeline
  ├─ Google Classroom (2 akun) — stream + classwork
  ├─ dedupe vs state.json (hash instruksi sama → skip)
  └─ laporan: SUMBER | MK | item | deadline | status | aksi
```

Aturan keras: **tugas tidak pernah di-submit** sebelum konfirmasi.
Kuis/ujian hanya dilaporkan. Absen boleh otomatis karena
time-critical.

## Jendela waktu (ringkas)

| Pemeriksa | Jendela |
|---|---|
| `check_schedule.py` | mulai −15 mnt s/d mulai +30 mnt |
| `absen_gate.py` | mulai −10 mnt s/d selesai +10 mnt |

Dua jendela ini sengaja berbeda: `check_schedule` untuk pertanyaan
"ada MK aktif?", gate untuk "apakah agent perlu bangun tiap 10 menit?"
(dosen bisa membuka presensi kapan pun selama jam kuliah).

## Kredensial & keamanan

- Password **hanya dari vault Hermes** (terenkripsi Fernet). Tidak ada
  password di repo, di log, atau di laporan.
- Gitleaks memindai seluruh riwayat di CI (`fetch-depth: 0`).
  Scan lokal 19 Nov 2026: **6 commit, no leaks found**.
- `.env` + `.env.*` di-`.gitignore`. Jangan pernah commit file vault,
  kunci, atau screenshot berisi captcha/password.
- Catatan: `absen_run.py` dan skrip lain memakai path absolut
  `/opt/data/monitor-kuliah/...` — itu path di server Hermes, bukan
  di repo. Menjalankan skrip dari repo butuh path tersebut tersedia
  (lihat [USAGE.md](USAGE.md)).

## SaaS multi-kampus (`monitor-kuliah/saas/`)

Arah yang sedang dirintis, bukan produk live: pipeline yang sama
(absen + reminder) untuk banyak kampus dan banyak pengguna, dengan
paket (`plans.json`), adapter per kampus (`py/adapters.py`), solver
captcha berlapis (`py/captcha_solver.py`: reuse sesi → empty bypass →
ddddocr lokal → CapSolver → WA interaktif), dan agen WA
(`py/wa_agent.py`). Jalankan demonya tanpa kredensial:
`python3 monitor-kuliah/saas/runner.py --demo`.
