# Laporan Praktikum PBO: Getter, Setter, dan Encapsulation
**Mata Kuliah:** Pemrograman Berorientasi Objek / Kelas A  
**Tugas:** Latihan Getter Setter (Pertemuan 4)  
**Mahasiswa:** Nabil Aulia Dika (Dezz)  
**NPM:** 250810701100090  

---

## 1. Tujuan & Konsep
- Menerapkan konsep **Encapsulation** pada class Java dengan membungkus atribut menggunakan access modifier `private`.
- Mengimplementasikan metode **Getter** untuk membaca nilai atribut dan **Setter** untuk memutasi nilai atribut.
- Menerapkan **validasi data** pada setter sehingga integritas data objek tetap terjaga (khususnya nilai IPK/GPA pada rentang 0.0 s.d. 4.0).

---

## 2. Implementasi Kode Program

### A. `Student.java`
```java
/**
 * Class Student
 * Mengimplementasikan konsep Encapsulation dengan getter, setter, dan validasi data.
 */
public class Student {
    // Atribut dideklarasikan secara private agar tidak dapat diakses langsung dari luar class
    private String nim;
    private String name;
    private String studyProgram;
    private double gpa;

    /**
     * Constructor Student
     * Nilai awal gpa diinisialisasi 0.0 sesuai spesifikasi latihan.
     */
    public Student(String nim, String name, String studyProgram) {
        this.nim = nim;
        this.name = name;
        this.studyProgram = studyProgram;
        this.gpa = 0.0; // Inisialisasi awal
    }

    // --- Getter dan Setter untuk NIM ---
    public String getNim() {
        return nim;
    }

    public void setNim(String nim) {
        this.nim = nim;
    }

    // --- Getter dan Setter untuk Name ---
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    // --- Getter dan Setter untuk Program Studi ---
    public String getStudyProgram() {
        return studyProgram;
    }

    public void setStudyProgram(String studyProgram) {
        this.studyProgram = studyProgram;
    }

    // --- Getter dan Setter untuk GPA (IPK) ---
    public double getGpa() {
        return gpa;
    }

    /**
     * Setter IPK dengan validasi ketat.
     * Hanya menerima nilai antara 0.0 hingga 4.0.
     */
    public void setGpa(double gpa) {
        if (gpa >= 0.0 && gpa <= 4.0) {
            this.gpa = gpa;
        } else {
            System.out.println("Invalid GPA!");
            System.out.println("GPA must be between 0.0 and 4.0.");
        }
    }

    @Override
    public String toString() {
        return "Student [NIM: " + nim + ", Nama: " + name + 
               ", Prodi: " + studyProgram + ", IPK: " + gpa + "]";
    }
}
```

### B. `Main.java`
```java
/**
 * Class Main untuk pengujian class Student
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("==================================================");
        System.out.println("   LATIHAN PEMROGRAMAN JAVA: GETTER & SETTER      ");
        System.out.println("==================================================");

        // 1. Membuat object Student baru
        System.out.println("\n[1] Membuat Objek Mahasiswa 1 (Andi):");
        Student s1 = new Student("2024001", "Andi", "Informatika");

        // Menampilkan data awal menggunakan getter
        System.out.println("Data Awal Mahasiswa 1:");
        System.out.println("NIM           : " + s1.getNim());
        System.out.println("Nama          : " + s1.getName());
        System.out.println("Program Studi : " + s1.getStudyProgram());
        System.out.println("IPK Awal      : " + s1.getGpa());

        // 2. Menguji setter dengan IPK valid (3.75)
        System.out.println("\n[2] Menguji setGpa(3.75) - IPK Valid:");
        s1.setGpa(3.75);
        System.out.println("IPK setelah diubah: " + s1.getGpa());

        // 3. Menguji setter dengan IPK tidak valid (5.0)
        System.out.println("\n[3] Menguji setGpa(5.0) - IPK Tidak Valid:");
        s1.setGpa(5.0);
        System.out.println("IPK sekarang (tetap nilai sebelumnya): " + s1.getGpa());

        // 4. Menguji setter dengan IPK tidak valid negatif (-1.0)
        System.out.println("\n[4] Menguji setGpa(-1.0) - IPK Negatif:");
        s1.setGpa(-1.0);
        System.out.println("IPK sekarang: " + s1.getGpa());

        // 5. Membuat objek Mahasiswa 2 (Budi)
        System.out.println("\n[5] Membuat Objek Mahasiswa 2 (Budi):");
        Student s2 = new Student("2024002", "Budi", "Sistem Informasi");
        s2.setGpa(3.50);
        System.out.println(s2);

        System.out.println("\n==================================================");
        System.out.println("              PENGUJIAN SELESAI                   ");
        System.out.println("==================================================");
    }
}
```

---

## 3. Output Eksekusi Program

```text
==================================================
   LATIHAN PEMROGRAMAN JAVA: GETTER & SETTER      
==================================================

[1] Membuat Objek Mahasiswa 1 (Andi):
Data Awal Mahasiswa 1:
NIM           : 2024001
Nama          : Andi
Program Studi : Informatika
IPK Awal      : 0.0

[2] Menguji setGpa(3.75) - IPK Valid:
IPK setelah diubah: 3.75

[3] Menguji setGpa(5.0) - IPK Tidak Valid:
Invalid GPA!
GPA must be between 0.0 and 4.0.
IPK sekarang (tetap nilai sebelumnya): 3.75

[4] Menguji setGpa(-1.0) - IPK Negatif:
Invalid GPA!
GPA must be between 0.0 and 4.0.
IPK sekarang: 3.75

[5] Membuat Objek Mahasiswa 2 (Budi):
Student [NIM: 2024002, Nama: Budi, Prodi: Sistem Informasi, IPK: 3.5]

==================================================
              PENGUJIAN SELESAI                   
==================================================
```

---

## 4. Pembahasan & Analisis
1. **Penerapan Enkapsulasi:** Seluruh atribut `nim`, `name`, `studyProgram`, dan `gpa` bersifat `private`, menjamin tidak adanya akses atau modifikasi ilegal dari luar objek (seperti `s1.gpa = 5.0`).
2. **Mekanisme Validasi:** Melalui method `setGpa()`, batas logika akademis (0.00 – 4.00) diberlakukan. Saat nilai 5.0 atau -1.0 dimasukkan, sistem menolak pembaruan data dan menampilkan peringatan.
