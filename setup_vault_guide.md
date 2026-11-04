# Panduan Setup Vault Kredensial Kampus

Agar Hermes di instance Telegram bisa login otomatis ke **Moodle e-learning USK** dan **SIMKULIAH**, sistem membutuhkan kredensial yang tersimpan terenkripsi di vault Hermes.

---

## Opsi 1: Salin Vault yang Sudah Ada (Paling Cepat & Rekomendasi ⚡)

Karena kedua instance Hermes milik kamu sendiri, cara paling praktis adalah langsung menyalin file vault terenkripsi dari server saat ini ke server target.

Di server baru:
```bash
mkdir -p /opt/data/vault
```

Salin dua file ini dari instance lama ke direktori `/opt/data/vault/`:
1. `/opt/data/vault/vault.key` (Kunci enkripsi Fernet)
2. `/opt/data/vault/vault.json.enc` (Data vault terenkripsi)

Pastikan permission-nya aman:
```bash
chmod 600 /opt/data/vault/vault.key /opt/data/vault/vault.json.enc
```

**Kelebihan Opsi 1:**
- Handle vault (`vault_e07e226cbdae`, `vault_3f284af2e789`, `vault_b37c19ed6f0b`) akan **identik 100%**.
- Skrip `absen_run.py`, cron prompt, dan fungsi login Moodle langsung jalan tanpa perlu ubah kode apa pun!

---

## Opsi 2: Buat Item Vault Baru via CLI Hermes

Jika instance baru belum memiliki vault atau ingin diatur dari awal:

1. **Jalankan perintah vault add:**
   ```bash
   hermes vault add
   ```
2. **Pilih tipe:** `login`
3. **Masukkan detail akun:**
   - **Label:** `Moodle + SIMKULIAH USK`
   - **Identifier (NPM):** `250810701100090`
   - **Password:** Masukkan password portal kampus kamu
4. Catat **ID Vault** yang dihasilkan (misal `vault_xxxxxxxxxxxx`).
5. Jika ID berbeda dari `vault_3f284af2e789` atau `vault_e07e226cbdae`:
   - Buka `/opt/data/monitor-kuliah/scripts/absen_run.py` baris 33-34, ganti ID-nya:
     ```python
     AKUN = {
         "dezz":  {"npm": "250810701100090", "vault": "vault_ID_BARU_KAMU"},
         "rizki": {"npm": "250810701100049", "vault": "vault_ID_BARU_RIZKI"},
     }
     ```
   - Update juga prompt cron job di `cron/cron_jobs.json`.
