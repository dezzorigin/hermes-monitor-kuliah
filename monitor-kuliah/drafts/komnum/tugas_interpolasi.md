# Laporan Tugas Komputasi Numerik: Pemecahan Masalah Metode Interpolasi
**Mata Kuliah:** Komputasi Numerik / Kelas A  
**Tugas:** Tugas Interpolasi (Bab VI - Latihan 6.6 Soal 1 s.d. 4)  
**Mahasiswa:** Nabil Aulia Dika (Dezz)  
**NPM:** 250810701100090  

---

## Ringkasan Eksekutif Hasil Perhitungan

| No | Soal Target | Data Input | Linier (Orde 1) | Kuadratik (Orde 2) | Lagrange / Beda Hingga (Orde Tinggi) | Keterangan / Analisis |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | $x = 2{,}4$ | Tabel $x$ vs $y$ | **$9{,}9360$** | **$9{,}9296$** | **$9{,}9296$** | Polinomial asli berorde 2 (selisih kedua konstan $= 0{,}08$). |
| **2** | $x = 1{,}0$ | Tabel $x$ vs $e^x$ | **$2{,}7678$** (Galat $1{,}82\%$) | **$2{,}7064$** (Galat $0{,}43\%$) | **$2{,}7189$** (Galat $0{,}023\%$) | Nilai eksak $e^1 = 2{,}718282$. Akurasi meningkat drastis seiring naiknya orde. |
| **3** | $x = 97{,}66$ | Tabel $x$ vs $y$ | **$13{,}5300$** | **$13{,}5025$** | **$13{,}5024$** | Kurva kuadratik sangat akurat mengapit titik $97{,}66$. |
| **4** | $T = 372{,}1$ | Tabel Suhu $T$ vs Tekanan $p$ | **$178{,}1273$** | **$177{,}8157$** | **$177{,}8304$** | Data termodinamika non-linier terestimasi secara konsisten. |

---

## SOAL 1: Tentukan nilai $y$ untuk $x = 2{,}4$

### Data Masukan:
| $i$ | $x_i$ | $y_i$ |
|:---:|:---:|:---:|
| 0 | 2 | 9,68 |
| 1 | 4 | 10,96 |
| 2 | 6 | 12,32 |
| 3 | 8 | 13,76 |
| 4 | 10 | 15,28 |

### A. Metode 1: Interpolasi Linier (Titik $x_0 = 2, x_1 = 4$)
Rumus:
$$f_1(x) = f(x_0) + \frac{f(x_1) - f(x_0)}{x_1 - x_0} (x - x_0)$$
Substitusi nilai:
$$f_1(2{,}4) = 9{,}68 + \frac{10{,}96 - 9{,}68}{4 - 2} (2{,}4 - 2)$$
$$f_1(2{,}4) = 9{,}68 + \frac{1{,}28}{2} (0{,}4) = 9{,}68 + 0{,}64 \times 0{,}4 = 9{,}68 + 0{,}256 = \mathbf{9{,}9360}$$

### B. Metode 2: Interpolasi Kuadratik (Titik $x_0=2, x_1=4, x_2=6$)
Rumus Polinomial Newton:
$$f_2(x) = b_0 + b_1(x - x_0) + b_2(x - x_0)(x - x_1)$$
Di mana:
- $b_0 = f(x_0) = 9{,}68$
- $b_1 = \frac{f(x_1) - f(x_0)}{x_1 - x_0} = \frac{10{,}96 - 9{,}68}{4 - 2} = 0{,}64$
- $f[x_2, x_1] = \frac{f(x_2) - f(x_1)}{x_2 - x_1} = \frac{12{,}32 - 10{,}96}{6 - 4} = \frac{1{,}36}{2} = 0{,}68$
- $b_2 = \frac{f[x_2, x_1] - b_1}{x_2 - x_0} = \frac{0{,}68 - 0{,}64}{6 - 2} = \frac{0{,}04}{4} = 0{,}01$

Substitusi $x = 2{,}4$:
$$f_2(2{,}4) = 9{,}68 + 0{,}64(2{,}4 - 2) + 0{,}01(2{,}4 - 2)(2{,}4 - 4)$$
$$f_2(2{,}4) = 9{,}68 + 0{,}256 + 0{,}01(0{,}4)(-1{,}6) = 9{,}936 - 0{,}0064 = \mathbf{9{,}9296}$$

*(Catatan: Beda hingga orde 3 bernilai 0 karena beda kedua konstan, sehingga hasil interpolasi orde 2 sama persis dengan orde 4 Lagrange).*

---

## SOAL 2: Tentukan nilai $y$ untuk $x = 1{,}0$ (Fungsi $y = e^x$)

### Data Masukan:
| $i$ | $x_i$ | $y_i = e^{x_i}$ |
|:---:|:---:|:---:|
| 0 | 0,1 | 1,1052 |
| 1 | 0,6 | 1,8221 |
| 2 | 1,1 | 3,0042 |
| 3 | 1,6 | 4,9530 |
| 4 | 2,1 | 8,1662 |

Nilai Eksak: $y_{\text{eksak}} = e^1 \approx 2{,}7182818$

### A. Metode 1: Interpolasi Linier (Titik terdekat $x_1=0{,}6, x_2=1{,}1$)
$$f_1(1{,}0) = 1{,}8221 + \frac{3{,}0042 - 1{,}8221}{1{,}1 - 0{,}6} (1{,}0 - 0{,}6)$$
$$f_1(1{,}0) = 1{,}8221 + \frac{1{,}1821}{0{,}5} (0{,}4) = 1{,}8221 + 2{,}3642 \times 0{,}4 = \mathbf{2{,}7678}$$
Galat Relatif:
$$\epsilon = \left|\frac{2{,}718282 - 2{,}767780}{2{,}718282}\right| \times 100\% = \mathbf{1{,}821\%}$$

### B. Metode 2: Interpolasi Kuadratik (Titik $x_1=0{,}6, x_2=1{,}1, x_3=1{,}6$)
- $b_0 = 1{,}8221$
- $b_1 = \frac{3{,}0042 - 1{,}8221}{1{,}1 - 0{,}6} = 2{,}3642$
- $f[x_3, x_2] = \frac{4{,}9530 - 3{,}0042}{1{,}6 - 1{,}1} = \frac{1{,}9488}{0{,}5} = 3{,}8976$
- $b_2 = \frac{3{,}8976 - 2{,}3642}{1{,}6 - 0{,}6} = \frac{1{,}5334}{1{,}0} = 1{,}5334$

Substitusi $x = 1{,}0$:
$$f_2(1{,}0) = 1{,}8221 + 2{,}3642(1{,}0 - 0{,}6) + 1{,}5334(1{,}0 - 0{,}6)(1{,}0 - 1{,}1)$$
$$f_2(1{,}0) = 1{,}8221 + 0{,}94568 + 1{,}5334(0{,}4)(-0{,}1) = 2{,}76778 - 0{,}061336 = \mathbf{2{,}706444}$$
Galat Relatif:
$$\epsilon = \left|\frac{2{,}718282 - 2{,}706444}{2{,}718282}\right| \times 100\% = \mathbf{0{,}435\%}$$

### C. Metode 3: Interpolasi Lagrange Orde 4 (Seluruh Titik)
Menggunakan seluruh 5 titik menghasilkan:
$$f_4(1{,}0) = \mathbf{2{,}718917}$$
Galat Relatif:
$$\epsilon = \left|\frac{2{,}718282 - 2{,}718917}{2{,}718282}\right| \times 100\% = \mathbf{0{,}023\%}$$

---

## SOAL 3: Tentukan nilai $y$ untuk $x = 97{,}66$

### Data Masukan:
| $i$ | $x_i$ | $y_i$ |
|:---:|:---:|:---:|
| 0 | 93 | 11,38 |
| 1 | 96,2 | 12,80 |
| 2 | 100 | 14,70 |
| 3 | 104,2 | 17,07 |
| 4 | 108,7 | 19,91 |

### A. Metode 1: Interpolasi Linier (Titik $x_1=96{,}2, x_2=100$)
$$f_1(97{,}66) = 12{,}80 + \frac{14{,}70 - 12{,}80}{100 - 96{,}2} (97{,}66 - 96{,}2)$$
$$f_1(97{,}66) = 12{,}80 + \frac{1{,}90}{3{,}8} (1{,}46) = 12{,}80 + 0{,}5 \times 1{,}46 = 12{,}80 + 0{,}73 = \mathbf{13{,}5300}$$

### B. Metode 2: Interpolasi Kuadratik (Titik $x_1=96{,}2, x_2=100, x_3=104{,}2$)
- $b_0 = 12{,}80$
- $b_1 = \frac{14{,}70 - 12{,}80}{100 - 96{,}2} = 0{,}5$
- $f[x_3, x_2] = \frac{17{,}07 - 14{,}70}{104{,}2 - 100} = \frac{2{,}37}{4{,}2} = 0{,}564286$
- $b_2 = \frac{0{,}564286 - 0{,}5}{104{,}2 - 96{,}2} = \frac{0{,}064286}{8{,}0} = 0{,}0080357$

Substitusi $x = 97{,}66$:
$$f_2(97{,}66) = 12{,}80 + 0{,}5(1{,}46) + 0{,}0080357(1{,}46)(97{,}66 - 100)$$
$$f_2(97{,}66) = 13{,}53 + 0{,}0080357(1{,}46)(-2{,}34) = 13{,}53 - 0{,}027453 = \mathbf{13{,}5025}$$

### C. Metode 3: Interpolasi Lagrange Orde 4 (Seluruh Titik)
$$f_4(97{,}66) = \mathbf{13{,}5024}$$

---

## SOAL 4: Tentukan nilai $p$ pada $T = 372{,}1$

### Data Masukan:
| $i$ | $T_i$ | $p_i$ |
|:---:|:---:|:---:|
| 0 | 361 | 154,9 |
| 1 | 367 | 167,0 |
| 2 | 378 | 191,0 |
| 3 | 387 | 212,5 |
| 4 | 399 | 244,2 |

### A. Metode 1: Interpolasi Linier (Titik $T_1=367, T_2=378$)
$$f_1(372{,}1) = 167{,}0 + \frac{191{,}0 - 167{,}0}{378 - 367} (372{,}1 - 367)$$
$$f_1(372{,}1) = 167{,}0 + \frac{24{,}0}{11} (5{,}1) = 167{,}0 + 2{,}181818 \times 5{,}1 = 167{,}0 + 11{,}12727 = \mathbf{178{,}1273}$$

### B. Metode 2: Interpolasi Kuadratik (Titik $T_1=367, T_2=378, T_3=387$)
- $b_0 = 167{,}0$
- $b_1 = \frac{191{,}0 - 167{,}0}{378 - 367} = 2{,}181818$
- $f[T_3, T_2] = \frac{212{,}5 - 191{,}0}{387 - 378} = \frac{21{,}5}{9} = 2{,}388889$
- $b_2 = \frac{2{,}388889 - 2{,}181818}{387 - 367} = \frac{0{,}207071}{20} = 0{,}0103535$

Substitusi $T = 372{,}1$:
$$f_2(372{,}1) = 167{,}0 + 2{,}181818(5{,}1) + 0{,}0103535(5{,}1)(372{,}1 - 378)$$
$$f_2(372{,}1) = 178{,}12727 + 0{,}0103535(5{,}1)(-5{,}9) = 178{,}12727 - 0{,}31154 = \mathbf{177{,}8157}$$

### C. Metode 3: Interpolasi Lagrange Orde 4 (Seluruh Titik)
$$f_4(372{,}1) = \mathbf{177{,}8304}$$
