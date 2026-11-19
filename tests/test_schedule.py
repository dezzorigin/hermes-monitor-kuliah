"""Tes nyata monitor kuliah — tanpa jaringan, tanpa kredensial, tanpa login.

Yang diuji adalah kode ASLI repo (bukan tiruan):
- monitor-kuliah/jadwal.json: valid, 13 MK, 21 SKS, bentrok Sabtu yang
  sudah didokumentasikan (2 MK jam 08:00 yang sama — keduanya dicek).
- monitor-kuliah/scripts/check_schedule.py: load_jadwal + load_absen_done
  + main() end-to-end dengan path di-patch ke fixture lokal.
- monitor-kuliah/scripts/absen_run.py::parse_absensi: parser halaman
  absensi SIMKULIAH (Pola A var-style + status) di atas fixture HTML.
  Modul absen_run di-load dengan stub requests/urllib3/simkuliah_login
  karena import aslinya butuh ddddocr + path /opt/data.
- monitor-kuliah/saas/runner.py --demo + scheduler.py: output demo dan
  jadwal cron (absen 10 mnt, reminder 60 mnt).
"""
import importlib.util
import io
import json
import subprocess
import sys
import types
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
JADWAL = ROOT / "monitor-kuliah" / "jadwal.json"
SCRIPTS = ROOT / "monitor-kuliah" / "scripts"
TZ = ZoneInfo("Asia/Jakarta")

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
HARI_EN = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu",
    "Sunday": "Minggu",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def jadwal():
    return json.loads(JADWAL.read_text())


@pytest.fixture(scope="module")
def check_schedule():
    return load_module("cs_under_test", SCRIPTS / "check_schedule.py")


def test_jadwal_valid_13_mk_21_sks(jadwal):
    mk = jadwal["mata_kuliah"]
    assert len(mk) == 13
    assert sum(m["sks"] for m in mk) == 21
    assert jadwal["timezone"] == "Asia/Jakarta"
    for m in mk:
        assert m["hari"] in HARI
        assert m["jenis"] in ("teori", "praktikum")
        assert m["kode"] and m["nama"] and m["ruang"] and m["kelas"]
        datetime.strptime(m["mulai"], "%H:%M")
        datetime.strptime(m["selesai"], "%H:%M")
        assert m["mulai"] < m["selesai"]


def test_jadwal_bentrok_sabtu_terdokumentasi(jadwal):
    """Sabtu 08:00 ada 2 MK (Prak PBO + Pendidikan Agama) — keduanya dicek,
    sesuai catatan di jadwal.json. Tidak boleh ada bentrok lain."""
    sabtu_0800 = [m for m in jadwal["mata_kuliah"]
                  if m["hari"] == "Sabtu" and m["mulai"] == "08:00"]
    assert {m["kode"] for m in sabtu_0800} == {"SINF2017", "MKWU2001"}
    seen = set()
    for m in jadwal["mata_kuliah"]:
        key = (m["hari"], m["mulai"])
        if key == ("Sabtu", "08:00"):
            continue
        assert key not in seen, f"bentrok tak terdokumentasi: {key}"
        seen.add(key)


def test_jadwal_hari_tercakup(jadwal):
    assert {m["hari"] for m in jadwal["mata_kuliah"]} == {
        "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"}


def test_check_schedule_load_jadwal(check_schedule, tmp_path):
    check_schedule.JADWAL_PATH = str(JADWAL)
    mk = check_schedule.load_jadwal()
    assert len(mk) == 13
    assert mk[0]["kode"] == "SINF2007"


def test_check_schedule_load_absen_done(check_schedule, tmp_path):
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"tanggal": today, "done": ["SINF2007"]}))
    check_schedule.STATE_PATH = str(state)
    assert check_schedule.load_absen_done() == {"SINF2007"}
    # state tanggal basi -> dianggap belum absen
    state.write_text(json.dumps({"tanggal": "2000-01-01", "done": ["SINF2007"]}))
    assert check_schedule.load_absen_done() == set()
    # file hilang -> kosong, bukan error
    check_schedule.STATE_PATH = str(tmp_path / "tidak-ada.json")
    assert check_schedule.load_absen_done() == set()


def test_check_schedule_main_output_asli(check_schedule, tmp_path):
    """main() beneran jalan: stdout = JSON {now, hari, absen_aktif}."""
    check_schedule.JADWAL_PATH = str(JADWAL)
    state = tmp_path / "state.json"
    state.write_text(json.dumps(
        {"tanggal": "2000-01-01", "done": []}))
    check_schedule.STATE_PATH = str(state)
    buf = io.StringIO()
    with redirect_stdout(buf):
        check_schedule.main()
    out = json.loads(buf.getvalue())
    now = datetime.now(TZ)
    assert out["hari"] == HARI_EN[now.strftime("%A")]
    assert isinstance(out["absen_aktif"], list)
    for a in out["absen_aktif"]:
        assert a["kode"] and a["jam"] and a["ruang"]


def test_window_check_schedule_untuk_mk_hari_ini(check_schedule):
    """Jendela check_schedule: mulai-15 mnt s/d mulai+30 mnt.
    Diuji pada MK pertama hari ini (kalau ada) dengan jam sintetis."""
    check_schedule.JADWAL_PATH = str(JADWAL)
    mk_list = check_schedule.load_jadwal()
    now = datetime.now(TZ)
    hari_ini = HARI_EN[now.strftime("%A")]
    hari_ini_mk = [m for m in mk_list if m["hari"] == hari_ini]
    if not hari_ini_mk:
        pytest.skip("tidak ada MK hari ini (Minggu)")
    m = hari_ini_mk[0]
    mulai = datetime.strptime(m["mulai"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=TZ)
    win_start = mulai - timedelta(minutes=check_schedule.WINDOW_PRE_MIN)
    win_end = mulai + timedelta(minutes=check_schedule.WINDOW_POST_MIN)
    assert check_schedule.WINDOW_PRE_MIN == 15
    assert check_schedule.WINDOW_POST_MIN == 30
    assert win_start < mulai < win_end
    assert (win_end - win_start) == timedelta(minutes=45)


def _load_absen_run_with_stubs():
    """Load absen_run.py tanpa requests/dddocr/vault asli."""
    urllib3 = types.ModuleType("urllib3")
    urllib3.disable_warnings = lambda *a, **k: None
    urllib3.exceptions = types.SimpleNamespace(
        InsecureRequestWarning=Warning)
    requests = types.ModuleType("requests")
    sk = types.ModuleType("simkuliah_login")
    sk.login = lambda *a, **k: (None, [])
    sk.konfirmasi = lambda *a, **k: ""
    sys.modules["urllib3"] = urllib3
    sys.modules["requests"] = requests
    sys.modules["simkuliah_login"] = sk
    spec = importlib.util.spec_from_file_location(
        "absen_run_under_test", SCRIPTS / "absen_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ABSENSI_FIXTURE = """
<html><body>
<p>Anda belum absen</p>
<table><tr><td>SINF2015</td><td>PEMROGRAMAN BERORIENTASI OBJEK</td></tr></table>
<button id="konfirmasi-kehadiran-12345">Konfirmasi Kehadiran</button>
<script>
$("#konfirmasi-kehadiran-12345").on("click", function() {
  var kelas = 'A';
  var kd_mt_kul_8 = 'SINF2015';
  var jadwal_mulai = '08:00';
  var jadwal_berakhir = '09:40';
  var pertemuan = '5';
  var sks_mengajar = '2';
  var id = '6123456';
});
</script>
</body></html>
"""


def test_parse_absensi_pola_a_dan_status():
    mod = _load_absen_run_with_stubs()
    info = mod.parse_absensi(ABSENSI_FIXTURE)
    assert info["status_teks"] is None  # "Anda belum absen" bukan keyword lama
    assert info["rows"] == ["SINF2015"]
    assert len(info["tombol"]) == 1
    params = info["tombol"][0]["params"]
    assert params == {
        "kelas": "A", "kd_mt_kul8": "SINF2015",
        "jadwal_mulai": "08:00", "jadwal_berakhir": "09:40",
        "pertemuan": "5", "sks_mengajar": "2", "id": "6123456",
    }


def test_parse_absensi_status_sudah_absen():
    mod = _load_absen_run_with_stubs()
    info = mod.parse_absensi("<html>Anda sudah absen, terima kasih</html>")
    assert info["status_teks"] == "anda sudah absen"
    assert info["tombol"] == []


def test_parse_absensi_tanpa_tombol():
    mod = _load_absen_run_with_stubs()
    info = mod.parse_absensi("<html>Dosen belum absen</html>")
    assert info["status_teks"] == "dosen belum absen"
    assert info["tombol"] == []


def test_runner_demo_output():
    r = subprocess.run(
        [sys.executable, str(ROOT / "monitor-kuliah" / "saas" / "runner.py"),
         "--demo"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "OK runner searah pipeline_v2.json" in r.stdout
    assert "absen=True" in r.stdout


def test_scheduler_cron_10_dan_60_menit():
    r = subprocess.run(
        [sys.executable, str(ROOT / "monitor-kuliah" / "saas" / "py"
                             / "scheduler.py")],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    jobs = {j["job"]: j["every_min"] for j in json.loads(r.stdout)}
    assert jobs == {"absen": 10, "reminder": 60}
