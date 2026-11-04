# Laporan Praktikum PBO: Composition & Inheritance (Latihan 1 - 3)
**Mata Kuliah:** Pemrograman Berorientasi Objek / Kelas A  
**Tugas:** Latihan Inheritance & Composition (Pertemuan 6 / Slide Bab 5)  
**Mahasiswa:** Nabil Aulia Dika (Dezz)  
**NPM:** 250810701100090  

---

## 1. Pendahuluan
Praktikum ini membahas dua mekanisme utama penggunaan ulang kode (*code reuse*) pada Object-Oriented Programming (OOP):
1. **Composition (*has-a relationship*):** Objek kompleks disusun dari gabungan objek lain yang lebih sederhana.
2. **Inheritance (*is-a relationship*):** Subclass mewarisi atribut dan perilaku dari superclass, dengan kemampuan menambah atribut/metode baru serta melakukan *method overriding*.

---

## 2. Latihan 1: Komposisi Garis (`Line` Tersusun dari 2 `Point`)

### Konsep & UML
Class `Line` memiliki dua referensi atribut bertipe `Point`: `begin` dan `end`. Relasi bernotasi agregasi/komposisi (belah ketupat), dengan multiplisitas 1 Line memiliki 2 Point.

### Kode Program `Line.java`
```java
public class Line {
    private Point begin;
    private Point end;

    public Line(int x1, int y1, int x2, int y2) {
        this.begin = new Point(x1, y1);
        this.end = new Point(x2, y2);
    }

    public Line(Point begin, Point end) {
        this.begin = begin;
        this.end = end;
    }

    public Point getBegin() { return begin; }
    public void setBegin(Point begin) { this.begin = begin; }
    public Point getEnd() { return end; }
    public void setEnd(Point end) { this.end = end; }

    public int getBeginX() { return begin.getX(); }
    public void setBeginX(int x) { begin.setX(x); }
    public int getBeginY() { return begin.getY(); }
    public void setBeginY(int y) { begin.setY(y); }
    public void setBeginXY(int x, int y) { begin.setXY(x, y); }

    public int getEndX() { return end.getX(); }
    public void setEndX(int x) { end.setX(x); }
    public int getEndY() { return end.getY(); }
    public void setEndY(int y) { end.setY(y); }
    public void setEndXY(int x, int y) { end.setXY(x, y); }

    public double getLength() {
        int xDiff = end.getX() - begin.getX();
        int yDiff = end.getY() - begin.getY();
        return Math.sqrt(xDiff * xDiff + yDiff * yDiff);
    }

    @Override
    public String toString() {
        return "Line[begin=" + begin + ", end=" + end + "]";
    }
}
```

---

## 3. Latihan 2: Pewarisan Garis (`LineSub extends Point`)

### Konsep & UML
Pendekatan alternatif di mana garis dipandang sebagai turunan dari titik awal (`Point`), dan hanya menambahkan atribut `end` (`Point`). Pewarisan menggunakan notasi segitiga berongga mengarah ke `Point`.

### Kode Program `LineSub.java`
```java
public class LineSub extends Point {
    private Point end;

    public LineSub(int x1, int y1, int x2, int y2) {
        super(x1, y1); // Menginisialisasi titik awal di superclass Point
        this.end = new Point(x2, y2);
    }

    public LineSub(Point begin, Point end) {
        super(begin.getX(), begin.getY());
        this.end = end;
    }

    public Point getEnd() { return end; }
    public void setEnd(Point end) { this.end = end; }

    public Point getBegin() {
        return new Point(super.getX(), super.getY());
    }

    public void setBegin(Point begin) {
        super.setXY(begin.getX(), begin.getY());
    }

    public int getBeginX() { return super.getX(); }
    public void setBeginX(int x) { super.setX(x); }
    public int getBeginY() { return super.getY(); }
    public void setBeginY(int y) { super.setY(y); }
    public void setBeginXY(int x, int y) { super.setXY(x, y); }

    public int getEndX() { return end.getX(); }
    public void setEndX(int x) { end.setX(x); }
    public int getEndY() { return end.getY(); }
    public void setEndY(int y) { end.setY(y); }
    public void setEndXY(int x, int y) { end.setXY(x, y); }

    public double getLength() {
        int xDiff = end.getX() - super.getX();
        int yDiff = end.getY() - super.getY();
        return Math.sqrt(xDiff * xDiff + yDiff * yDiff);
    }

    @Override
    public String toString() {
        return "LineSub[begin=" + super.toString() + ", end=" + end + "]";
    }
}
```

---

## 4. Latihan 3: Titik Tiga Dimensi (`Point3D extends Point`)

### Konsep & UML
Class `Point3D` memperluas representasi koordinat 2D `Point(x, y)` menjadi ruang 3 dimensi dengan menambahkan atribut `z`. `Point3D` melakukan *method overriding* pada `toString()` untuk mencetak format 3D.

### Kode Program `Point3D.java`
```java
public class Point3D extends Point {
    private int z;

    public Point3D() {
        super();
        this.z = 0;
    }

    public Point3D(int x, int y, int z) {
        super(x, y);
        this.z = z;
    }

    public int getZ() { return z; }
    public void setZ(int z) { this.z = z; }

    @Override
    public String toString() {
        return "(" + super.getX() + ", " + super.getY() + ", " + z + ")";
    }
}
```

---

## 5. Hasil Pengujian Program (`TestAll.java`)

```text
==================================================================
     PENGUJIAN TUGAS PBO - LATIHAN INHERITANCE & COMPOSITION      
==================================================================

>>> [LATIHAN 1: Composition (Line has two Points)] <<<
line1 dibuat dengan koordinat (1, 2) ke (4, 6):
Representasi line1 : Line[begin=(1, 2), end=(4, 6)]
Panjang line1      : 5.0 (Harusnya 5.0)

line2 dibuat dengan objek Point p1(0,0) dan p2(3,4):
Representasi line2 : Line[begin=(0, 0), end=(3, 4)]
Panjang line2      : 5.0 (Harusnya 5.0)
Setelah modifikasi setEndXY(6, 8):
Representasi line2 : Line[begin=(0, 0), end=(6, 8)]
Panjang baru line2 : 10.0 (Harusnya 10.0)

>>> [LATIHAN 2: Inheritance (LineSub extends Point)] <<<
lineSub1 dibuat dengan koordinat (2, 3) ke (5, 7):
Representasi lineSub1: LineSub[begin=(2, 3), end=(5, 7)]
Titik awal (super)   : (2, 3)
Titik akhir (end)    : (5, 7)
Panjang lineSub1     : 5.0 (Harusnya 5.0)
Setelah modifikasi setBeginXY(0,0) dan setEndXY(3,4):
Representasi lineSub1: LineSub[begin=(0, 0), end=(3, 4)]
Panjang baru lineSub1: 5.0 (Harusnya 5.0)

>>> [LATIHAN 3: Inheritance (Point3D extends Point)] <<<
Point3D default constructor: (0, 0, 0)
Point3D berparameter (10, 20, 30):
Representasi p3d: (10, 20, 30)
Koordinat X (diwarisi dari superclass): 10
Koordinat Y (diwarisi dari superclass): 20
Koordinat Z (milik subclass)          : 30
Setelah setter diubah menjadi (15, 25, 35): (15, 25, 35)

==================================================================
              SEMUA PENGUJIAN SELESAI & SUKSES!                   
==================================================================
```

---

## 6. Perbandingan Komposisi vs Pewarisan
1. **Desain Garis (Latihan 1 vs 2):** Pendekatan Komposisi (`Line has-a Point`) jauh lebih intuitif dan bersih secara semantik daripada Pewarisan (`Line is-a Point`), karena garis bukanlah sebuah titik, melainkan kumpulan titik.
2. **Pewarisan Alami (Latihan 3):** `Point3D is-a Point` merupakan penerapan pewarisan yang sangat tepat dan natural, karena titik 3D memperluas sifat titik bidang 2D secara matematis.
