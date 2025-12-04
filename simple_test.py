#!/usr/bin/env python3
import requests

BASE = "http://127.0.0.1:7000"

print("\n=== TEST SIMPLE ===\n")

print("[1] /admin/ (admin dashboard)")
r = requests.get(f"{BASE}/admin/")
print(f"Status: {r.status_code}")
print(f"Es HTML: {'<!doctype' in r.text.lower() or '<html' in r.text.lower()}")
print(f"Primeros 200 chars: {r.text[:200]}\n")

print("[2] /dashboard (client dashboard)")
r = requests.get(f"{BASE}/dashboard")
print(f"Status: {r.status_code}")
print(f"Es HTML: {'<!doctype' in r.text.lower() or '<html' in r.text.lower()}")
print(f"Primeros 200 chars: {r.text[:200]}\n")
