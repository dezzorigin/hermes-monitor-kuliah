# PRD Fitur — BantuKuliah (SaaS Auto-Absen & Monitor Kuliah)

Versi 1.0 · 9 Okt 2026 · Diturunkan dari sistem live yang sudah berjalan (Dezz + Rizki, USK)

---

## F1 — Onboarding & Connect Portal

**Flow:**
1. User register → pilih kampus (MVP: USK saja)
2. Masukkan NPM + password portal → sistem langsung verifikasi login NYATA ke SIMKULIAH
3. Sukses → kredensial masuk vault per-user → status `connected` → input nomor WA → OTP → done
4. Gagal → kredensial TIDAK disimpan, tampilkan "NPM/password salah" atau "captcha gagal 3x, coba lagi"

**Trik & teknik:**
- **Verifikasi login = login beneran**, bukan cek format. Post-login scrape nama mahasiswa dari dashboard → simpan ke profil. CATATAN: label NPM ≠ nama akun (NPM …090 login sebagai "NABIL AULIA DIKA" — itu memang akun beneran; jangan flag mismatch nama sebagai error).
- **Password vault-only**: `browser_vault_fill` / secret store per-tenant. Password tidak pernah masuk DB, log, atau prompt LLM. Zero plaintext.
- **Form SIMKULIAH tidak andal dengan input automation biasa** — `fill_input` sering gagal → set value via JS langsung: `document.querySelector('#username').value = ...`. Password tetap lewat vault.
- **CAPTCHA di form login**: lihat F4 — ini blocker utama onboarding, harus solved end-to-end otomatis.

---

## F2 — Auto-Absen (fitur inti)

**Flow:**
1. Scheduler cek jadwal kuliah user → masuk window (10 mnt sebelum kelas s/d 10 mnt setelah jam selesai) → worker bangun
2. Login SIMKULIAH (reuse sesi dulu kalau masih valid)
3. Buka halaman presensi → deteksi tombol/sesi presensi yang dibuka dosen
4. Ekstrak parameter dari inline script tombol `konfirmasi-kehadiran-<id>`
5. POST konfirmasi langsung → response `'success'` = hadir
6. Catat hasil + evidence → notif WA ke user (sukses ATAU gagal, dua-duanya wajib lapor)

**Trik & teknik (semua terbukti produksi):**
- **Jangan klik UI SweetAlert** — dialog konfirmasi swal() custom tidak andal diklik (bisa gagal total, server balas "sudah presensi" padahal belum). Solusi: **POST langsung** ke `/index.php/absensi/konfirmasi_kehadiran` dengan body `kelas, kd_mt_kul8, jadwal_mulai, jadwal_berakhir, pertemuan, sks_mengajar, id` — semua nilai ada hardcode di inline script tombolnya.
- **Dosen buka presensi kapan pun selama jam kuliah** — makanya window gate harus span seluruh jam kelas, bukan cuma awal. Window proven: `mulai-10m` s/d `selesai+10m`.
- **Idempoten per (user, mk, tanggal)** — state `{"tanggal", "akun": {user: {"done": [kode]}}}`, reset tiap ganti hari. MK yang sudah done di semua akun keluar dari pemantauan.
- **Sesi login dulu, captcha belakangan** — kalau cookie sesi masih valid, skip login+captcha sepenuhnya (paling cepat, paling murah).
- **Retry login max 3x** — captcha SIMKULIAH auto-refresh tiap submit gagal → WAJIB re-extract + re-solve gambar TERBARU sebelum retry (gambar lama dijamin salah). Password field biasanya masih terisi.
- **Kecepatan > presisi captcha** — submit hasil solver apa adanya; kalau salah, gambar baru muncul dan ulang. Jangan buang waktu verifikasi gambar.
- **Multi-akun paralel terbukti** — 2 akun (Dezz + Rizki) absen berurutan dalam run yang sama, logout bersih antar akun (goto logout URL, tunggu redirect /login).

**Notifikasi hasil (format terbukti):**
- Sukses: `"SINF2023 P8 absen SUKSES 16:43 (batas 16:55) ✅"`
- Gagal: `"SINF2023 absen GAGAL: <alasan>"` — jangan pernah diam.

---

## F3 — Monitor Tugas & Deadline (Moodle)

**Flow:**
1. Cron 4x/hari (06/12/18/00 WIB — proven cadence)
2. Login Moodle USK (auto re-login via vault kalau session expired — sering terjadi)
3. Fetch daftar assignment aktif per course → normalisasi
4. Dedupe → hanya tugas baru/berubah yang dinotifikasi
5. Status lifecycle: `baru → mendekati (H-1) → overdue / hidden`

**Trik & teknik:**
- **Dedupe via hash instruksi**: `tugas_id → {deadline, hash_instruksi}` — lapor ulang HANYA kalau deadline atau instruksi berubah. Ini yang bikin notif nggak spam.
- **Deteksi session expired dari redirect** — kalau `/my/courses.php` redirect ke login, ambil password dari vault dan re-login otomatis. Jangan mati dengan error.
- **Assignment bisa hidden/ditutup** — pantau status `hidden` (tugas dikumpulkan via departemen/ditutup), jangan cuma deadline.
- **Deadline dari halaman assign langsung** (`mod/assign/view.php?id=...`), bukan kalender — lebih akurat.
- **Output format laporan terstruktur**: `MK | tugas | deadline | status | yang dibutuhkan dari user` — satu baris per item, bisa di-scroll cepat.

**Fase 2 — Google Classroom:** sesi OAuth expired berkala (status sekarang: expired). Butuh flow re-auth resmi, nggak scalable pakai sesi browser untuk SaaS. Jangan janjikan di MVP.

---

## F4 — CAPTCHA Solver Service

**Flow (antrian strategi, urutan dari paling murah):**
1. **Reuse sesi** — cookie valid → skip captcha (Rp0, tercepat)
2. **ddddocr lokal** — untuk captcha gambar sederhana (Rp0, <1 detik)
3. **Empty-string bypass** — beberapa portal Aceh (fsd.usk, siakad) cuma validasi captcha kalau non-empty → submit kosong langsung lolos (Rp0)
4. **Solver berbayar** — CapSolver/2Captcha untuk reCAPTCHA/Turnstile (~Rp200/solve, 15-30 detik)
5. **Fallback interaktif** — kirim gambar captcha ke WA user, tunggu jawaban numerik 2 menit

**Trik & teknik:**
- **ddddocr di venv terpisah** — `uv venv .venv-captcha && uv pip install ddddocr pillow`. Sudah terinstal & terbukti (konsisten 5 digit antar preprocessing).
- **Ambil gambar captcha via canvas**: `#captcha-img` → `toDataURL()` dengan 4x upscale → PNG → `ocr.classification()`.
- **`vision_analyze` SELALU menolak baca captcha** apapun framing-nya — jangan pernah andalkan vision untuk ini, langsung ke ddddocr.
- **Log tiap solve** `{strategi, ok, biaya_est}` — jadi metrik biaya per user untuk pricing.

---

## F5 — Reminder & Notifikasi WhatsApp

**Flow:**
1. Trigger events: kelas H-30mnt, tugas baru, deadline H-1, hasil absen, minta captcha
2. Compose pesan per template → kirim via gateway WA
3. Pesan masuk dari user → command parser → aksi

**Trik & teknik:**
- **Kanal WA, bukan email/push** — mahasiswa buka WA; ini alasan produk ini hidup.
- **Gateway MVP: Baileys self-hosted via n8n** (infra udah ada) — gratis & fleksibel. Risiko ban → nomor dedicated + rate limit + jangan blast. Alternatif fase 2: WhatsApp Cloud API resmi.
- **Command masuk (rule-based dulu, nggak perlu LLM)**: "cek tugas" → list; "ubah jadwal" → link web; "stop" → opt-out reminder; jawaban 4-6 digit → captcha response.
- **Selalu ada fallback link web** di tiap pesan aksi — jangan kasih dead-end.
- **Opt-out wajib** — "stop" langsung matikan reminder, hormati tanpa konfirmasi ulang.

---

## F6 — Dashboard Web

**Halaman:**
- **Ringkasan**: % kehadiran, kelas berikutnya (nama + ruang + jam), tugas aktif terdekat — sesuai mock di landing
- **Tugas**: list + filter status (baru/mendekati/overdue), link ke Moodle
- **Riwayat absen**: per MK, tanggal, status, evidence (screenshot/response)
- **Pengaturan**: jadwal kuliah (auto-fetch + edit manual), preferensi waktu absen ("saat mulai" / "sebelum selesai"), toggle notifikasi, connect/disconnect portal

**Trik & teknik:**
- **Evidence per absen wajib ada** — user percaya sistem yang bisa nunjukin bukti. Simpan response + screenshot per run.
- **Disconnect portal = hapus kredensial vault + stop semua job** — bukan cuma flag.
- **% kehadiran** — data dari SIMKULIAH rekapan kehadiran; tampilkan "cek sebelum terlambat" (baseline minimum kampus) — ini selling point di landing, jangan lupa.

---

## F7 — Plan & Entitlement

**Plan (dari core_pipeline.py, terbukti):**
- Reminder: 9.9k/bln · 29.9k/semester — fitur: reminder_wa
- Absensi: 19.9k/bln · 49.9k/semester — fitur: auto_absen
- Bundling: 24.5k/bln · 69.9k/semester — dua-duanya

**Trik:**
- **`entitled(plan, fitur)` dipanggil di setiap eksekusi** F2/F5 — jangan cek cuma di UI.
- **MVP: aktivasi manual + trial** — jangan bangun payment gateway sebelum ≥5 user beta pakai F2 beneran.

---

## F8 — Multi-Kampus Adapter (fase 3)

- Base class `KampusAdapter`: `login / fetch_absen_page / fetch_tugas / klik_absen / confirm_attendance`
- USK = implementasi live; kampus lain stub. Pilih kampus ke-2 yang portalnya paling mirip SIMKULIAH (form login + captcha gambar sederhana).
- Health-check harian per adapter: login test akun sentinel → alert kalau portal berubah layout/endpoint.

---

## Cross-cutting (wajib di semua fitur)

| Aspek | Aturan |
|---|---|
| Kredensial | vault per-tenant, zero plaintext, zero di log |
| Timezone | semua Asia/Jakarta (WIB) |
| Evidence | tiap aksi simpan bukti, path dilaporkan |
| Gagal = lapor | tidak ada silent failure, terutama absen |
| Dedupe | hash-based, jangan spam notif |
| Anti-halu | status fitur dibaca dari `feature-tracker.json`; klaim maksimal = status + evidence di sana |
