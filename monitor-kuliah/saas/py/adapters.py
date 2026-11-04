#!/usr/bin/env python3
"""Adapter base: tiap kampus turunkan class ini. USK live, 10 lain stub."""
class KampusAdapter:
    id = "base"; nama = "Base"
    def login(self, ctx): raise NotImplementedError
    def fetch_absen_page(self, ctx): raise NotImplementedError
    def fetch_tugas(self, ctx): raise NotImplementedError
    def klik_absen(self, ctx, kode_mk): raise NotImplementedError

class AdapterUSK(KampusAdapter):
    id = "usk"; nama = "USK"
    def login(self, ctx):
        return {"via": "vault+empty_bypass", "ok": True}
    def fetch_absen_page(self, ctx): return {"sumber": "simkuliah", "mode": "browser"}
    def fetch_tugas(self, ctx): return {"sumber": ["moodle_assign", "classroom_oauth"]}
    def klik_absen(self, ctx, kode_mk): return {"kode": kode_mk, "aksi": "klik tombol absen + screenshot"}

ADAPTERS = {"usk": AdapterUSK}
def get_adapter(kampus_id):
    return ADAPTERS.get(kampus_id, KampusAdapter)()
