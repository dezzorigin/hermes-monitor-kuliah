#!/usr/bin/env bash
set -e

echo "=== [1/3] Menyiapkan Direktori & Environment Monitor Kuliah ==="
mkdir -p /opt/data/monitor-kuliah/evidence
mkdir -p /opt/data/monitor-kuliah/drafts
mkdir -p /opt/data/monitor-kuliah/tmp
mkdir -p /opt/data/scripts

echo "=== [2/3] Membuat Virtualenv untuk CAPTCHA OCR (ddddocr) ==="
cd /opt/data/monitor-kuliah
if ! command -v uv &> /dev/null; then
    echo "uv tidak ditemukan, menginstal uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

uv venv .venv-captcha --python 3.12 || uv venv .venv-captcha
uv pip install --python .venv-captcha/bin/python ddddocr pillow requests urllib3

echo "=== [3/3] Menyiapkan Dependency PDF & Laporan (opsional) ==="
uv pip install --python .venv-captcha/bin/python reportlab || true

echo "=== [SELESAI] Environment Monitor Kuliah Siap! ==="
