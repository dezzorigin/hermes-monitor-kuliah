#!/usr/bin/env python3
"""Generate og-image.png 1200x630 untuk Hermes Monitor Kuliah (PIL, lokal).

Mengikuti palet landing (docs/DESIGN.md): Kertas Papan #FFFEF9,
Tinta #1E2430, Hijau Papan #14684E, Stabilo #F7C948, Merah Absen #B3261E.
Kartu papan pengumuman: header hijau, judul serif, strip stabilo,
stempel status. Bukan screenshot asli.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
KERTAS = (255, 254, 249)   # #FFFEF9
TINTA = (30, 36, 48)       # #1E2430
HIJAU = (20, 104, 78)      # #14684E
STABILO = (247, 201, 72)   # #F7C948
MERAH = (179, 38, 30)      # #B3261E
MUTED = (86, 93, 107)      # #565D6B
GARIS = (216, 213, 204)    # #D8D5CC

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

img = Image.new("RGB", (W, H), KERTAS)
d = ImageDraw.Draw(img)

# header hijau papan + garis tinta
d.rectangle([0, 0, W, 190], fill=HIJAU)
d.rectangle([0, 190, W, 196], fill=TINTA)
# garis tepi dalam
d.rectangle([28, 28, W - 28, H - 28], outline=TINTA, width=3)

# kicker
f_kick = ImageFont.truetype(MONO_B, 28)
d.text((72, 56), "UNIVERSITAS SYIAH KUALA  ·  INFORMATIKA", font=f_kick, fill=STABILO)

# judul
f_title = ImageFont.truetype(SERIF_B, 92)
d.text((68, 96), "Hermes Monitor Kuliah", font=f_title, fill=KERTAS)

# strip stabilo: jadwal
d.rectangle([72, 228, W - 72, 292], fill=STABILO)
f_strip = ImageFont.truetype(SANS_B, 32)
d.text((96, 240), "13 mata kuliah  ·  21 SKS  ·  Senin–Sabtu  ·  WIB", font=f_strip, fill=TINTA)

# subjudul
f_sub = ImageFont.truetype(SANS, 34)
d.text((72, 322), "Papan jadwal + monitor absensi SIMKULIAH:", font=f_sub, fill=TINTA)
d.text((72, 368), "cron tiap 10 menit, gerbang jendela, dedupe tugas.", font=f_sub, fill=TINTA)

# stempel status
f_stamp = ImageFont.truetype(MONO_B, 26)
stamps = [("DI LUAR JENDELA", MUTED), ("HADIR", HIJAU), ("MENUNGGU DOSEN", MERAH)]
x = 72
y = 448
for label, color in stamps:
    tw = d.textlength(label, font=f_stamp)
    pad_x, pad_y = 20, 12
    d.rectangle([x, y, x + tw + pad_x * 2, y + 52], outline=color, width=3)
    d.text((x + pad_x, y + 11), label, font=f_stamp, fill=color)
    x += tw + pad_x * 2 + 22

# footer url
f_url = ImageFont.truetype(MONO_B, 28)
d.text((72, 540), "hermes-monitor-kuliah.pages.dev", font=f_url, fill=HIJAU)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "og-image.png")
img.save(out, "PNG", optimize=True)
print("saved", out, os.path.getsize(out), "bytes")
