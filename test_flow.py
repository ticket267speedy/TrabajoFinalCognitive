#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://127.0.0.1:7000"

print("=" * 60)
print("TEST FLUJO ADMIN")
print("=" * 60)

# Test 1: Login
print("\n[1] Login admin1@demo.com...")
try:
    r = requests.post(f"{BASE_URL}/api/login", json={"email": "admin1@demo.com", "password": "pass123"})
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token")
        print(f"    Token: {token[:50]}...")
        print("    ✓ OK")
    else:
        print(f"    ERROR: {r.text}")
        exit(1)
except Exception as e:
    print(f"    ERROR: {e}")
    exit(1)

# Test 2: GET /admin/ sin token
print("\n[2] GET /admin/ sin token...")
try:
    r = requests.get(f"{BASE_URL}/admin/")
    print(f"    Status: {r.status_code}")
    is_html = r.text.startswith("<!doctype") or r.text.startswith("<html") or "<!DOCTYPE" in r.text
    print(f"    Es HTML: {is_html}")
    if r.status_code == 200 and is_html:
        print("    ✓ OK - Dashboard cargado sin token")
    else:
        print(f"    ERROR: {r.text[:200]}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: GET /api/admin/profile con token
print("\n[3] GET /api/admin/profile con token...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/admin/profile", headers=headers)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    Usuario: {data.get('first_name')} {data.get('last_name')}")
        print("    ✓ OK")
    else:
        print(f"    ERROR: {r.text}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 60)
print("TEST FLUJO CLIENTE")
print("=" * 60)

# Test 4: Login cliente
print("\n[4] Login cliente@demo.com...")
try:
    r = requests.post(f"{BASE_URL}/api/login", json={"email": "cliente@demo.com", "password": "pass123"})
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        token_client = data.get("access_token")
        print(f"    Token: {token_client[:50]}...")
        print("    ✓ OK")
    else:
        print(f"    ERROR: {r.text}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 5: GET /dashboard sin token
print("\n[5] GET /dashboard sin token...")
try:
    r = requests.get(f"{BASE_URL}/dashboard")
    print(f"    Status: {r.status_code}")
    is_html = r.text.startswith("<!doctype") or r.text.startswith("<html") or "<!DOCTYPE" in r.text
    print(f"    Es HTML: {is_html}")
    if r.status_code == 200 and is_html:
        print("    ✓ OK - Dashboard cliente cargado")
    else:
        print(f"    ERROR: {r.text[:200]}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print("\n✓ Si ambos dashboards se cargan sin token, el problema está en:")
print("  1. Cache del navegador")
print("  2. localStorage del navegador")
print("  3. Diferencia en cómo se hacen los fetch desde JavaScript")
