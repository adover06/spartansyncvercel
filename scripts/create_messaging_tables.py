"""Create missing DB tables (safe to run multiple times).

Usage:
  source venv/bin/activate && python scripts/create_messaging_tables.py

This will call SQLAlchemy `create_all()` to ensure new models' tables exist.
"""
import os
import sys

# Ensure project root is on path when running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print("Creating/updating database tables with db.create_all()...")
        db.create_all()
        # print list of tables
        from sqlalchemy import text
        res = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        tables = [r[0] for r in res]
        print("Tables now in DB:")
        for t in sorted(tables):
            print(" - ", t)
        print("Done.")
