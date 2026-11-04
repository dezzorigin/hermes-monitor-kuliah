# Panduan Injeksi Cepat Clone Monitor Kuliah ke Hermes Telegram (5 Menit)

Panduan ini untuk langsung menyuntikkan seluruh otak, skill, skrip, dan memori **Monitor Kuliah & Asisten Tugas Dezz** ke instance Hermes Telegram kamu.

---

## Langkah 1: Ekstrak Bundle di Server Target

Salin file `hermes-monitor-kuliah-clone.zip` ke server target (`/opt/data/`), lalu ekstrak:

```bash
cd /opt/data
unzip -o hermes-monitor-kuliah-clone.zip
cd hermes-monitor-kuliah
```

---

## Langkah 2: Pindahkan File ke Struktur Sistem Hermes

Jalankan perintah copy berikut agar file berada di path kanonik Hermes:

```bash
# 1. Pasang Skill monitor-kuliah-soul
mkdir -p /opt/data/skills/productivity
cp -r skills/productivity/monitor-kuliah-soul /opt/data/skills/productivity/

# 2. Pasang Core Folder & Skrip
cp -r monitor-kuliah /opt/data/
mkdir -p /opt/data/scripts
cp scripts/absen_gate.sh /opt/data/scripts/
chmod +x /opt/data/scripts/absen_gate.sh /opt/data/monitor-kuliah/scripts/*.py

# 3. Buat direktori logs & evidence jika belum ada
mkdir -p /opt/data/monitor-kuliah/evidence /opt/data/monitor-kuliah/drafts /opt/data/monitor-kuliah/tmp
```

---

## Langkah 3: Setup Environment Captcha Solver (ddddocr)

Jalankan skrip instalasi dependency lokal:

```bash
bash /opt/data/hermes-monitor-kuliah/install_dependencies.sh
```

Ini akan membuat venv `/opt/data/monitor-kuliah/.venv-captcha` dan menginstal `ddddocr`, `pillow`, dan `requests` untuk bypass otomatis captcha SIMKULIAH & KRS.

---

## Langkah 4: Setup Kredensial Vault

Ikuti panduan di `setup_vault_guide.md`.
**Cara tercepat:** Salin file `/opt/data/vault/vault.key` dan `/opt/data/vault/vault.json.enc` dari server ini ke `/opt/data/vault/` di server baru.

---

## Langkah 5: Pasang Cron Job Otomatis

Kamu bisa meminta Hermes Telegram kamu langsung lewat chat:
> *"Tolong baca file `/opt/data/hermes-monitor-kuliah/cron/cron_jobs.json` dan tambahkan kedua cron job tersebut (monitor-tugas-dezz dan absen-watcher-dezz) ke sistem cron kamu dengan delivery ke chat ini."*

Atau jika ingin manual via terminal Hermes:
Import definisi dari `cron/cron_jobs.json` ke `/opt/data/cron/jobs.json`.

---

## Langkah 6: Hubungkan Soul ke Bot Telegram di `config.yaml`

Buka file `/opt/data/config.yaml` di server baru, lalu tambahkan/sesuaikan platform Telegram:

```yaml
platforms:
  telegram:
    enabled: true
    bot_token: "TOKEN_BOT_TELEGRAM_KAMU"
    allowed_users:
      - ID_TELEGRAM_KAMU
    channel_overrides:
      "ID_CHAT_TELEGRAM_KAMU":
        system_prompt: |
          # Soul: Monitor Kuliah & Asisten Tugas — Dezz
          ... (Salin dari config/config_telegram_snippet.yaml) ...
    channel_skill_bindings:
      - id: "ID_CHAT_TELEGRAM_KAMU"
        skills:
          - monitor-kuliah-soul
```

Setelah config disimpan, restart gateway Hermes:
```bash
# Jika pakai s6 overlay (Dokploy/Docker):
s6-svc -t /run/service/gateway-default
# Atau restart container Hermes di Dokploy
```

---

## Selesai! 🎉
Bot Telegram kamu sekarang punya kapabilitas identik 100%:
1. Bisa memantau Moodle, kuis, UTS, dan assignment secara proaktif.
2. Otomatis mengisi absensi di SIMKULIAH dalam window ~10 menit via solver OCR.
3. Menulis draft tugas laporan, makalah, perhitungan interpolasi, PBO, dll.
