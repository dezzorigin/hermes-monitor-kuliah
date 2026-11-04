# Hermes Monitor Kuliah & Asisten Tugas Clone Bundle

Paket kloning mandiri (*all-in-one clone bundle*) untuk mereplikasi soul, skill, arsitektur otomatisasi, skrip absensi, modul pengerjaan kuis/UTS, dan pipeline asisten tugas akademik Dezz ke instance Hermes Agent lainnya (khususnya Telegram).

---

## 📦 Isi Paket Bundle

```
hermes-monitor-kuliah/
├── INJEKSI_CEPAT.md                 -> Panduan step-by-step injeksi cepat ke instance target
├── setup_vault_guide.md             -> Petunjuk konfigurasi enkripsi kredensial vault
├── install_dependencies.sh          -> Script setup environment venv & OCR captcha (ddddocr)
├── config/
│   └── config_telegram_snippet.yaml -> Contoh konfigurasi binding soul & skill di config.yaml
├── cron/
│   └── cron_jobs.json               -> Definisi cron job: monitor tugas & watcher absensi
├── scripts/
│   └── absen_gate.sh                -> Wrapper cron gate pengecek window kuliah aktif
├── skills/
│   └── productivity/
│       └── monitor-kuliah-soul/
│           └── SKILL.md             -> Skill kanonik, aturan main, dan pitfall terbukti
└── monitor-kuliah/
    ├── jadwal.json                  -> Jadwal kuliah lengkap Dezz (12 MK: teori & praktikum)
    ├── state.json                   -> State dedupe tugas/kuis & tracking progres
    ├── absen_state.json             -> State harian rekaman absensi SIMKULIAH
    ├── generate_pdfs.py             -> Generator otomatis laporan PDF tugas (ReportLab)
    ├── scripts/
    │   ├── absen_run.py             -> Engine otomatisasi absen multi-akun (Dezz + Rizki)
    │   ├── absen_gate.py            -> Deteksi window aktif (10 menit sebelum/sesudah jam kelas)
    │   ├── check_schedule.py        -> Parser jadwal kuliah
    │   ├── simkuliah_login.py       -> Engine login SIMKULIAH + OCR captcha otomatis
    │   └── krs_login.py             -> Engine login KRS USK + OCR captcha
    ├── drafts/                      -> Draft tugas yang sudah dikerjakan (Komnum Interpolasi, PBO)
    ├── resources/                   -> Modul materi kuliah asli (PDF & referensi)
    ├── evidence/                    -> Bukti tangkapan layar pengerjaan kuis, UTS, dan absensi
    └── saas/                        -> Arsitektur & spesifikasi PRD pipeline monitoring
```

---

## ⚡ Fitur Utama

1. **Auto-Absen SIMKULIAH dengan Bypass Captcha:**
   - Menyelesaikan CAPTCHA gambar 5 digit lokal secara instan menggunakan `ddddocr` tanpa ketergantungan API pihak ketiga.
   - Deteksi otomatis sesi presensi dibuka oleh dosen dan mengirim payload presensi via POST internal yang andal.
2. **Monitoring Moodle e-learning USK:**
   - Scan otomatis tugas baru, kuis, forum pengumuman, dan upcoming events.
   - Auto re-login aman dengan dekripsi kredensial langsung dari vault Hermes.
3. **Pengerjaan & Draft Tugas Mandiri:**
   - Menganalisis instruksi tugas dosen, menghitung solusi numerik / kode program, dan menyusun laporan terstruktur format Markdown & PDF.
   - Menjalankan kuis/UTS dengan analisis cepat dan konfirmasi sebelum submit.
4. **Dedupe Cerdas:**
   - Tidak ada pengulangan laporan; hanya melaporkan tugas baru atau perubahan instruksi/deadline.
