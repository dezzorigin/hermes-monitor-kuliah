#!/usr/bin/env python3
"""Scheduler: absen tiap 10 mnt, reminder tiap 60 mnt. Dipanggil cron/n8n."""
import json
CRON = [{"job": "absen", "every_min": 10, "call": "runner.py --mode absen"},
        {"job": "reminder", "every_min": 60, "call": "runner.py --mode reminder"}]
if __name__ == "__main__":
    print(json.dumps(CRON, indent=1))
