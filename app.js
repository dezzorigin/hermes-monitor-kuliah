/* Hermes Monitor Kuliah — jam WIB live + sorot hari & kelas berjalan.
   Murni presentasi: jadwal di halaman ini statis (dari jadwal.json),
   status monitor di papan kanan berlabel "contoh" di HTML. */
(function () {
  "use strict";

  var HARI_ID = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];

  function wibParts(date) {
    var fmt = new Intl.DateTimeFormat("id-ID", {
      timeZone: "Asia/Jakarta",
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    var parts = {};
    fmt.formatToParts(date).forEach(function (p) { parts[p.type] = p.value; });
    return parts;
  }

  function toMinutes(hhmm) {
    var p = hhmm.split(":");
    return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
  }

  function tick() {
    var now = new Date();
    var p = wibParts(now);
    var dateEl = document.getElementById("today-date");
    var clockEl = document.getElementById("wib-clock");
    var nowEl = document.getElementById("now-class");
    if (!dateEl || !clockEl || !nowEl) return;

    dateEl.textContent = p.weekday + ", " + p.day + " " + p.month + " " + p.year;
    clockEl.textContent = p.hour + "." + p.minute + "." + p.second;
    clockEl.setAttribute("datetime", p.hour + ":" + p.minute + ":" + p.second);

    var hariIni = p.weekday;
    var menit = toMinutes(p.hour + ":" + p.minute);

    document.querySelectorAll(".day").forEach(function (day) {
      day.classList.toggle("is-today", day.getAttribute("data-hari") === hariIni);
    });

    var sedang = null;
    var berikut = null;
    document.querySelectorAll(".day.is-today .lesson").forEach(function (li) {
      var mulai = toMinutes(li.getAttribute("data-mulai"));
      var selesai = toMinutes(li.getAttribute("data-selesai"));
      li.classList.remove("is-now");
      if (menit >= mulai && menit < selesai) {
        li.classList.add("is-now");
        sedang = li;
      } else if (menit < mulai && !berikut) {
        berikut = li;
      }
    });

    if (sedang) {
      var nama = sedang.querySelector(".lesson-body strong").textContent;
      var jam = sedang.querySelector(".time").textContent;
      nowEl.textContent = "Sedang berlangsung: " + nama + " (" + jam + ")";
    } else if (berikut) {
      var namaB = berikut.querySelector(".lesson-body strong").textContent;
      var jamB = berikut.querySelector(".time").textContent;
      nowEl.textContent = "Berikutnya: " + namaB + " (" + jamB + ")";
    } else if (hariIni === "Minggu") {
      nowEl.textContent = "Tidak ada kuliah hari ini — monitor diam.";
    } else {
      nowEl.textContent = "Tidak ada kelas yang sedang berlangsung.";
    }
  }

  tick();
  setInterval(tick, 1000);
})();
