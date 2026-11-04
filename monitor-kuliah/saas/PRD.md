# PRD — BantuKuliah (Agreement Contract & Acuan QA)

**Produk:** SaaS asisten kuliah — auto-absen, monitor tugas, reminder jadwal
**Domain:** bantukuliah.biz.id
**Versi:** 1.0 · 9 Okt 2026
**Status dokumen:** CONTRACT — dokumen ini adalah acuan tunggal

---

## 0. Ketentuan Dokumen (Agreement)

1. **Dokumen ini adalah kontrak.** Jika ada konflik antara implementasi, ucapan/chat, atau dokumen lain — **isi PRD ini yang menang**.
2. Perubahan requirement hanya sah lewat **amendemen tertulis** (versi naik + catatan perubahan di §10). Klaim "katanya boleh" tanpa amendemen = tidak berlaku.
3. **QA tester menguji terhadap dokumen ini**, bukan terhadap pendapat developer. Kriteria PASS/FAIL tiap fitur tertulis eksplisit di §6 — tidak boleh ditafsirkan lain.
4. Fitur yang tidak tertulis di PRD ini = **di luar scope**. Bug/permintaan di luar scope masuk backlog, bukan blocker rilis.
5. Definisi "selesai" sebuah fitur = semua kriteria PASS di §6 terpenuhi + evidence tersimpan.
6. Status tiap fitur dilacak di tabel sign-off §9. Label yang sah: `PASS`, `FAIL`, `BLOCKED`, `NOT-TESTED`.

---

## 1. Gambaran Produk

Mahasiswa lupa absen karena dosen membuka presensi kapan saja dalam jam kuliah (window ~10–30 menit), dan lupa deadline karena info tersebar di beberapa portal. BantuKuliah menghubungkan akun portal kampus user, lalu:

1. **Absen otomatis** saat presensi dibuka dosen
2. **Memantau tugas & deadline** dari LMS kampus
3. **Mengirim reminder & hasil** ke WhatsApp user

Prinsip mengikat: user setup sekali, sistem jalan sendiri. **Gagal pun wajib lapor — tidak ada silent failure.**

---

## 2. User Story (dengan ID untuk referensi QA)

### Onboarding
- **US-1** Sebagai mahasiswa baru, aku bisa daftar, pilih kampus, dan hubungkan akun portal (NPM + password) dalam < 5 menit tanpa bantuan admin.
- **US-2** Sebagai user, kalau kredensialku salah aku mendapat pesan "NPM/password salah", bukan error teknis.
- **US-3** Sebagai user, aku bisa hubungkan nomor WhatsApp-ku sebagai kanal notifikasi.

### Auto-Absen
- **US-4** Sistem absen otomatis begitu dosen membuka presensi, tanpa aku membuka portal.
- **US-5** Aku selalu menerima notifikasi hasil absen — sukses MAUPUN gagal beserta alasannya.
- **US-6** Aku bisa memilih waktu absen: "saat kelas mulai" atau "menjelang selesai".
- **US-7** Aku bisa melihat riwayat absen + bukti per mata kuliah.

### Monitor Tugas
- **US-8** Aku dinotifikasi saat ada tugas baru atau deadline/instruksi berubah — tidak ada notif duplikat untuk tugas yang sama.
- **US-9** Aku diingatkan H-1 sebelum deadline.
- **US-10** Aku bisa lihat daftar semua tugas aktif (judul, MK, deadline, status) di satu tempat.

### Reminder & Kontrol
- **US-11** Aku menerima pengingat 30 menit sebelum kelas (nama MK + jam + ruang) via WhatsApp.
- **US-12** Aku bisa matikan reminder dan putus koneksi portal kapan saja; putus koneksi = kredensial dihapus dan semua job berhenti.

### Dashboard & Admin
- **US-13** Aku bisa lihat % kehadiranku terhadap batas minimum kampus.
- **US-14** Aku bisa koreksi jadwal kuliah manual jika hasil fetch dari portal salah.
- **US-15** Sebagai admin, aku bisa lihat status koneksi portal tiap user dan success rate absen.

---

## 3. List Fitur & Scope

| ID | Fitur | Prioritas | Scope MVP |
|----|-------|-----------|-----------|
| F1 | Onboarding + connect portal (verifikasi login nyata) | P0 | ✅ |
| F2 | Auto-absen SIMKULIAH | P0 | ✅ |
| F3 | Monitor tugas Moodle + dedupe | P0 | ✅ |
| F4 | CAPTCHA solver berlapis | P0 | ✅ (internal, diuji via F1/F2) |
| F5 | Notifikasi & reminder WhatsApp | P0 | ✅ |
| F6 | Dashboard web | P0 | ✅ |
| F7 | Plan & entitlement | P1 | ✅ (entitlement only; billing fase 2) |
| F8 | Google Classroom sebagai sumber tugas | P2 | ❌ fase 2 |
| F9 | Multi-kampus adapter | P2 | ❌ fase 3 |
| F10 | % kehadiran & peringatan batas minimum | P1 | ✅ (tampilan di F6) |

**Di luar scope MVP (tidak boleh diuji sebagai bug):** pembayaran otomatis, kampus selain USK, Google Classroom, submit tugas, aksi nilai/kuis/ujian apa pun.

---

## 4. Flow Fitur Core

### F1 — Onboarding & Connect Portal
```
Daftar → pilih kampus (USK) → input NPM + password
→ sistem LOGIN NYATA ke SIMKULIAH sebagai verifikasi
   ├─ sukses → kredensial ke vault → status "connected" → input no WA → selesai
   └─ gagal  → kredensial TIDAK disimpan → pesan "NPM/password salah" → boleh retry
```
Aturan kontrak:
- Verifikasi = login beneran. Kredensial yang belum terverifikasi tidak boleh berstatus `connected`.
- Nama akun pasca-login bisa beda dari ekspektasi — BUKAN error; simpan nama hasil scrape ke profil.
- Password hanya lewat vault/secret store — zero plaintext di DB, log, dan prompt AI.

### F2 — Auto-Absen
```
Gate cek jadwal user hari ini tiap interval:
  Di luar window (mulai-10m s/d selesai+10m) → idle, tidak ada aksi
  Di dalam window & MK belum absen:
    → login (reuse sesi dulu kalau valid)
    → buka halaman presensi → deteksi sesi yang dibuka dosen
    ├─ presensi terbuka → POST konfirmasi kehadiran
    │     ├─ "success" → catat + evidence → notif "Absen SUKSES <jam>"
    │     └─ gagal → retry → notif "Absen GAGAL: <alasan>"
    └─ presensi belum dibuka → cek lagi interval berikutnya
```
Aturan kontrak:
- Konfirmasi absen dilakukan via request langsung ke endpoint konfirmasi, bukan klik dialog UI.
- Window pemantauan mencakup seluruh jam kuliah (dosen bisa buka presensi kapan pun).
- Idempoten: (user, MK, tanggal) maksimal 1 absen sukses.
- Setiap run menyimpan evidence (response/screenshot) yang bisa dilihat user.

### F3 — Monitor Tugas
```
Cron 4x/hari (06, 12, 18, 00 WIB):
  → login Moodle (auto re-login kalau session expired)
  → fetch assignment aktif → normalisasi {mk, judul, deadline, hash_instruksi}
  → bandingkan state:
      ├─ hash & deadline sama → skip
      ├─ baru → simpan + notif "Tugas baru"
      └─ berubah → update + notif "Deadline/instruksi berubah"
  → H-1 deadline → notif pengingat
```

### F4 — CAPTCHA Solver (internal)
```
Butuh captcha → coba berurutan termurah dulu:
  1. Reuse sesi valid → skip
  2. Solver lokal (gambar sederhana)
  3. Solver berbayar (reCAPTCHA/Turnstile)
  4. Fallback: kirim gambar ke WA user → tunggu jawaban ≤ 2 menit
```
Aturan kontrak: captcha yang berubah setelah gagal login WAJIB di-solve ulang dari gambar terbaru; hasil tiap strategi dicatat.

### F5 — Notifikasi & Reminder WhatsApp
```
Kirim WA pada: H-30m kelas | tugas baru/berubah | H-1 deadline |
               hasil absen (sukses/gagal) | permintaan captcha
Pesan masuk: "cek tugas"→daftar | "stop"→opt-out langsung | 4-6 digit→jawaban captcha
```
Aturan kontrak: opt-out "stop" berlaku seketika tanpa konfirmasi ulang.

### F6 — Dashboard
- Ringkasan: % kehadiran, kelas berikutnya, tugas terdekat
- Tugas: list + status (baru/mendekati/overdue) + link sumber
- Riwayat absen: per MK — tanggal, jam, status, bukti
- Pengaturan: jadwal (fetch + edit), preferensi waktu absen, toggle notif, disconnect portal

Aturan kontrak: **disconnect = hapus kredensial + hentikan semua job user**, bukan sekadar flag UI.

---

## 5. System Flow

```
   user daftar → [F1 Connect] → kredensial → VAULT per-user
                      │ fetch jadwal
                      ▼
   ┌────────── SCHEDULER (window gate) ──────────┐
   │  Kerja hanya saat ada MK aktif / jadwal cek │
   └──────┬──────────────────────────┬───────────┘
          ▼                          ▼
     [F2 Absen]                 [F3 Monitor tugas]
          │                          │
      butuh captcha ──► [F4 Solver] ◄┘
          │                          │
          ▼                          ▼
   ┌──────── STATE STORE ────────────────────┐
   │  absen (idempoten/hari) · tugas (hash)  │
   │  evidence per aksi                      │
   └────────────────┬─────────────────────────┘
                    ▼
             [F5 WA Notif] → USER → [F6 Dashboard]
```

Aturan sistem mengikat: vault per-user · timezone Asia/Jakarta (WIB) · idempoten · silent failure dilarang · entitlement dicek saat eksekusi.

---

## 6. Kriteria PASS/FAIL untuk QA (acuan pengujian)

QA menguji item berikut. PASS hanya jika kondisi terpenuhi persis; selain itu FAIL.

### F1 — Onboarding
- [ ] **F1-A** User baru menyelesaikan connect portal dengan kredensial VALID → status `connected` + jadwal ter-fetch.
- [ ] **F1-B** Kredensial SALAH → status tetap `disconnected`, pesan "NPM/password salah", dan kredensial tidak tersimpan di mana pun.
- [ ] **F1-C** Password tidak muncul di DB, log, atau response API mana pun (cek tabel, log file, response).
- [ ] **F1-D** Total waktu onboarding ≤ 5 menit untuk user dengan kredensial valid.

### F2 — Auto-Absen
- [ ] **F2-A** Saat dosen membuka presensi di dalam window → status kehadiran di portal berubah menjadi hadir, tercatat di riwayat, evidence tersimpan.
- [ ] **F2-B** Notifikasi hasil (sukses atau gagal+alasan) terkirim ≤ 1 menit setelah keputusan final.
- [ ] **F2-C** Menjalankan absen 2x untuk (user, MK, tanggal) yang sama → tidak menghasilkan record ganda.
- [ ] **F2-D** Di luar window jadwal → tidak ada aksi sama sekali (cek log: gate `idle`).
- [ ] **F2-E** Preferensi "saat mulai" vs "menjelang selesai" mengubah waktu eksekusi sesuai pilihan.
- [ ] **F2-F** Success rate ≥ 95% dari presensi yang benar-benar dibuka dosen (diukur min. 10 sesi beta).

### F3 — Monitor Tugas
- [ ] **F3-A** Tugas baru di Moodle → notif ≤ interval cron berikutnya, isi: MK | judul | deadline.
- [ ] **F3-B** Tugas yang sama tanpa perubahan → TIDAK ada notif ulang (dedupe).
- [ ] **F3-C** Deadline/instruksi berubah → notif "berubah" dengan data baru.
- [ ] **F3-D** Session expired → sistem re-login sendiri tanpa intervensi user.
- [ ] **F3-E** H-1 deadline → notif pengingat terkirim.

### F4 — CAPTCHA Solver
- [ ] **F4-A** Login dengan captcha gambar sederhana → lolos otomatis tanpa intervensi user ≥ 80% percobaan.
- [ ] **F4-B** Setelah login gagal, retry selalu memakai captcha TERBARU (bukan gambar cache).
- [ ] **F4-C** Tiap solve tercatat: strategi yang dipakai + berhasil/gagal.

### F5 — WhatsApp
- [ ] **F5-A** Reminder kelas terkirim 30 menit (±5) sebelum jam mulai, isi: nama MK + jam + ruang.
- [ ] **F5-B** "stop" dari user → reminder berhenti seketika; tidak ada pesan berikutnya.
- [ ] **F5-C** "cek tugas" → balasan berisi daftar tugas aktif atau link dashboard.
- [ ] **F5-D** Jawaban angka 4-6 digit diteruskan sebagai jawaban captcha.

### F6 — Dashboard
- [ ] **F6-A** Ringkasan menampilkan: % kehadiran, kelas berikutnya, tugas terdekat — data sesuai state sebenarnya.
- [ ] **F6-B** Riwayat absen per MK menampilkan tanggal/jam/status/bukti.
- [ ] **F6-C** Edit jadwal manual menimpa hasil fetch dan dipakai oleh scheduler.
- [ ] **F6-D** Disconnect portal → kredensial terhapus + semua job user berhenti (verifikasi vault kosong & tidak ada run berikutnya).

### F7 — Entitlement
- [ ] **F7-A** User plan `reminder` TIDAK menjalankan absen meski jadwal aktif (cek: tidak ada run absen).
- [ ] **F7-B** User plan `absensi` TIDAK menerima reminder kelas/tugas.
- [ ] **F7-C** User `bundling` mendapat keduanya.
- [ ] **F7-D** Downgrade plan menghentikan fitur berbayar seketika pada run berikutnya.

### Aturan umum
- [ ] **G-1** Tidak ada silent failure: semua kegagalan aksi penting menghasilkan notif dengan alasan.
- [ ] **G-2** Semua timestamp memakai WIB (Asia/Jakarta).
- [ ] **G-3** Evidence tersimpan dan bisa diakses user untuk setiap aksi F2.

---

## 7. Non-Fungsional (bagian dari kontrak)

- **Keamanan:** kredensial vault-only per user; zero plaintext; disconnect menghapus kredensial.
- **Reliabilitas:** retry login max 3x dengan captcha baru; seluruh run absen selesai dalam window.
- **Observability:** tiap run → log terstruktur {user, fitur, hasil, via, durasi, evidence}.
- **Privasi:** data user per-tenant terpisah; evidence tidak bocor antar user.

---

## 8. Risiko & Batasan yang Disepakati

- Perubahan layout/endpoint portal kampus = risiko bersama; mitigasi: adapter + health-check, bukan jaminan uptime portal.
- Auto-absen bergantung dosen benar-benar membuka presensi di portal — sistem tidak menjanjikan absen untuk presensi offline/manual.
- WhatsApp bukan kanal resmi ber-SLA; keterlambatan pengiriman oleh provider di luar kontrol sistem.

---

## 9. Sign-off & Tracking Status Fitur

Diisi saat QA/regresi. Satu baris per fitur per rilis.

| Fitur | Versi diuji | Status | Tanggal | Penguji | Catatan/Evidence |
|-------|-------------|--------|---------|---------|------------------|
| F1 Onboarding | — | NOT-TESTED | — | — | — |
| F2 Auto-absen | — | NOT-TESTED | — | — | — |
| F3 Monitor tugas | — | NOT-TESTED | — | — | — |
| F4 Captcha solver | — | NOT-TESTED | — | — | — |
| F5 WhatsApp | — | NOT-TESTED | — | — | — |
| F6 Dashboard | — | NOT-TESTED | — | — | — |
| F7 Entitlement | — | NOT-TESTED | — | — | — |
| F10 % Kehadiran | — | NOT-TESTED | — | — | — |

**Release gate:** semua P0 berstatus `PASS` → MVP boleh rilis. `FAIL`/`BLOCKED` pada P0 = tidak rilis.

---

## 10. Riwayat Perubahan (Amendemen)

| Versi | Tanggal | Perubahan | Disetujui |
|-------|---------|-----------|-----------|
| 1.0 | 2026-10-09 | Versi awal kontrak — diturunkan dari sistem live (Dezz/Rizki, USK) | — |
