#!/usr/bin/env python3
"""Quickstart script to:
- Run migrations
- Seed demo data
- Print sample login and JWT usage commands
"""

import os
import sys
import subprocess


def run(cmd: list[str], env: dict | None = None) -> None:
    subprocess.run(cmd, check=True, env=env)


def main() -> int:
    # Ensure Flask CLI knows the app entry
    env = os.environ.copy()
    env.setdefault("FLASK_APP", "run.py")

    # Show DB URL that will be used inside the app
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            db_url = app.config.get("SQLALCHEMY_DATABASE_URI")
            print(f"Using database: {db_url}")
    except Exception as e:
        print(f"Warning: could not load app to inspect DB URL: {e}")

    print("Running migrations...")
    try:
        run([sys.executable, "-m", "flask", "db", "upgrade"], env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return 1

    print("Seeding demo data...")
    try:
        from update_db import update_database
        ok = update_database()
        if not ok:
            print("Seeding failed.")
            return 1
    except Exception as e:
        print(f"Error seeding data: {e}")
        return 1

    print("\nDemo users:")
    print(" - admin@demo.com / Password123")
    print(" - asesor@demo.com / Password123")
    print(" - cliente@demo.com / Password123")

    print("\nSample API calls (PowerShell):")
    print(r"""
$resp = curl -s -Method POST http://localhost:5000/api/login -Headers @{ 'Content-Type' = 'application/json' } -Body '{"email":"admin@demo.com","password":"Password123"}'
$token = ($resp | ConvertFrom-Json).access_token
curl -s http://localhost:5000/api/admin/profile -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json
"""
    )

    print("\nSample API calls (bash):")
    print(r"""
# login
curl -s -X POST http://localhost:5000/api/login -H 'Content-Type: application/json' -d '{"email":"admin@demo.com","password":"Password123"}'
# then call protected endpoint with token
curl -s http://localhost:5000/api/admin/profile -H "Authorization: Bearer <access_token>"
"""
    )

    print("\nHealth check:")
    print("curl http://localhost:5000/health")

    print("\nDone. Start the server:")
    print("python run.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())