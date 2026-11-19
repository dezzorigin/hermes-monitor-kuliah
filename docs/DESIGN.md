# DESIGN.md — Hermes Monitor Kuliah (landing etalase)

Kontrak arah desain — ditulis SEBELUM coding, mengikuti
`~/workspace/github-actions/ui-anti-slop.md`.

## Referensi (tour 19 Nov 2026)

Kebutuhan: etalase monitor kuliah — jadwal mingguan yang gampang dibaca
sekilas + papan status monitoring (gerbang absen, jendela, dedupe).
Keyword: `class schedule timetable dashboard`, `school app dashboard`.

Kandidat:
1. **NEVERBLAND — "School Education App: timetable V2"** (Dribbble,
   https://dribbble.com/shots/1111355-School-Education-App-timetable-V2)
   — baris jadwal berisi nomor pertemuan, jam, ruang, dan ikon pelajaran;
   ada penanda "hari ini" dan tampilan minggu. Struktur paling dekat
   dengan isi repo ini (jadwal.json = 13 MK Senin–Sabtu).
2. **Smit M. Solanki — "EduView: School App Dashboard"** (Dribbble,
   http://dribbble.com/shots/26566489-School-App-Dashboard-Student-Parent-Experience)
   — struktur bento, warna netral sebagai dasar + aksen semantik untuk
   status; pengelompokan yang jelas tanpa membebani pembaca.
3. **Ronas IT — "Student Portal Dashboard"** (Dribbble,
   https://dribbble.com/shots/26239990-Student-Portal-Dashboard-Mobile-App-UI-Design)
   — jadwal mingguan dengan minggu yang bisa dipilih + kartu tugas
   berstatus yang bisa difilter.

**Pemenang: #1 NEVERBLAND timetable V2.** Yang di-clone strukturnya:
daftar jadwal per hari (jam + ruang + kode MK + jenis teori/praktikum),
strip hari aktif, dan penanda kelas yang sedang berlangsung.
Yang diubah dan kenapa: timetable V2 itu layar aplikasi mobile; di sini
dijadikan papan pengumuman desktop dua kolom — kiri tabel jadwal mingguan
penuh (13 MK), kanan papan status monitor (gerbang, jendela absen, dedupe
tugas) + alur 4 langkah cara kerja monitor. Warna dan tipografi diganti
penuh ke palet kampus terang di bawah (referensi aslinya netral-abu;
kami butuh papan yang terbaca seperti pengumuman ditempel, bukan
aplikasi abu-abu). Status tugas diambil dari struktur EduView (#2):
kartu status berlabel jujur, bukan angka vanity.

## Palet (5 warna bernama + 1 garis netral)

| Nama | Hex | Peran |
|---|---|---|
| Kertas Papan | `#FFFEF9` | latar halaman — kertas pengumuman |
| Tinta | `#1E2430` | teks utama, garis tegas, header papan |
| Hijau Papan | `#14684E` | warna primer — header, tombol utama, MK teori |
| Stabilo | `#F7C948` | sorot — kelas yang sedang berlangsung, highlight |
| Merah Absen | `#B3261E` | urgensi — jendela absen hampir tutup / gagal |
| Abu Garis | `#D8D5CC` | garis pemisah tabel (netral, bukan warna aksi) |

Tidak ada gradient (P0), tidak ada ungu/biru hero, palet bukan satu hue.

## Tipografi (≤ 2 keluarga)

- Display: **Fraunces** (serif editorial, judul papan + nama MK besar).
- Body/data: **IBM Plex Sans** (teks, label, angka jam dengan
  `font-variant-numeric: tabular-nums`).

## Layout (satu kalimat)

Papan pengumuman kampus: header papan + strip "hari ini", kolom kiri
tabel jadwal mingguan Senin–Sabtu, kolom kanan papan status monitor
(gerbang + jendela + dedupe) lalu alur 4 langkah di bawah.

## Detail khas (signature)

**Stempel status karet** — chip status berbentuk stempel miring dengan
garis tepi ganda (`HADIR`, `MENUNGGU DOSEN`, `DI LUAR JENDELA`,
`BELUM WAKTU`), plus baris kelas yang sedang berlangsung disorot
Stabilo seperti habis di-stabilo. Tidak ada kartu 3-simetris, tidak ada
ikon emoji (ikon = SVG garis tipis 1.5px).

## Beda dari repo #43 (lyric-popup-kelas-it)

| Sumbu | #43 | Repo ini |
|---|---|---|
| Palet | panggung gelap `#171310` + krem + amber/ungu | terang: kertas `#FFFEF9` + hijau papan + stabilo |
| Tipografi | Anton + Space Grotesk | Fraunces + IBM Plex Sans |
| Layout | satu kolom, kotak lirik melayang | dua kolom papan: jadwal + status monitor |
| Radius/spacing | kotak melayang rounded besar | radius 6px tajam, bayangan offset keras 3px |
| Detail khas | kotak lirik melayang | stempel status karet + sorot stabilo |

Beda 5 dari 5 sumbu.

## Larangan yang dipatuhi

P0: tanpa gradient, tanpa Inter/Roboto/system-untuk-semua, tanpa hero
tengah + 3 kartu identik, tanpa emoji sebagai ikon, tanpa statistik
vanity (angka yang tampil = data asli `jadwal.json`: 13 MK, 21 SKS,
6 hari; status monitor dilabeli "contoh" kalau simulasi), tanpa
headline satu kata diwarnai, tanpa tema Tailwind mentah, tanpa
`rounded-2xl shadow-lg` di semua permukaan, tanpa footer 4 kolom,
tanpa copy generik. Orde-kedua: tanpa krim+terracotta, near-black+lime,
label mono all-caps di mana-mana, hiasan 01/02/03, palet satu hue,
dark blue/slate, espresso+oranye, beige/sand.

## Data di landing

Jadwal = data ASLI `monitor-kuliah/jadwal.json` (13 MK, 21 SKS,
Senin–Sabtu, USK, WIB). Status monitor ("gate", jendela absen, contoh
laporan cron) = **simulasi berlabel "contoh"** — landing ini etalase,
produknya automation Python yang jalan lewat cron di server. Jam
"sekarang" di strip hari-ini dihitung live di browser pengunjung.
