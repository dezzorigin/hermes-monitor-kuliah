# Deploy — Hermes Monitor Kuliah

Ada dua "deploy" yang berbeda — jangan dicampur:

## 1. Landing etalase → Cloudflare Pages (publik)

Yang di-deploy hanya file statis di root repo: `index.html`,
`styles.css`, `app.js`, `favicon.svg`, `og-image.png`. Deploy lewat
`~/workspace/github-actions/cf_pages.py` (API token via vault, tanpa
kredensial di chat):

```bash
python3 ~/workspace/github-actions/cf_pages.py create-project hermes-monitor-kuliah
python3 ~/workspace/github-actions/cf_pages.py deploy hermes-monitor-kuliah .
```

- Nama pilihan pertama: `hermes-monitor-kuliah`
  (fallback: `monitor-kuliah-hermes`, `hermes-kuliah-monitor`).
  Nama dengan sufiks di hasil create = sudah dipakai akun lain —
  pindah ke fallback berikutnya.
- URL: `https://hermes-monitor-kuliah.pages.dev/` (sesuaikan nama akhir).
- Verifikasi live SEBELUM merge: root 200 + marker landing + semua
  tag `og:`/`twitter:` ada + `og-image.png` 200 dengan
  `Content-Type: image/*` (Pages fallback bisa menipu dengan
  `text/html`).
- Set homepage repo ke URL Pages (PATCH homepage) setelah deploy.

## 2. Automation → server Hermes (privat, bukan Pages)

Skrip Python + cron + vault TIDAK di-deploy ke Pages. Jalurnya:

1. Salin `monitor-kuliah/` ke `/opt/data/monitor-kuliah/` di server.
2. `bash install_dependencies.sh` (venv captcha).
3. Muat `cron/cron_jobs.json` ke Hermes (2 job).
4. Pastikan vault berisi kredensial yang dirujuk cron (password
   diambil dari vault, tidak pernah ditulis ke file).

Perubahan jadwal cukup edit `monitor-kuliah/jadwal.json` di repo,
lalu salin ulang file itu ke server — tidak perlu restart apa pun
(skrin membaca file tiap tick).

## CI

`.github/workflows/ci.yml` jalan di tiap push/PR ke `main`:
python-test (py_compile + pytest) → lint-ruff → gitleaks (riwayat
penuh) → advisory-sweep (OSV) → static-checks (html-validate + gate
P0 + OG) → playwright-e2e (landing, hanya CI) → smoke (file deploy).

PR hanya di-merge kalau SEMUA job hijau, termasuk gitleaks.
