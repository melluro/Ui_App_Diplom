#!/usr/bin/env python3
"""База данных компонентов UI System"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_system.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT DEFAULT '',
            code TEXT DEFAULT '',
            variants TEXT DEFAULT '[]',
            props TEXT DEFAULT '{}',
            status TEXT DEFAULT '✅ Готов',
            author TEXT DEFAULT '',
            version TEXT DEFAULT '1.0.0',
            dependencies TEXT DEFAULT '',
            preview_text TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS component_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id INTEGER NOT NULL,
            version TEXT NOT NULL,
            code TEXT DEFAULT '',
            comment TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# ── CRUD ──────────────────────────────────────────────────────

def get_all_components(category='', status='', search=''):
    conn = get_conn()
    query = "SELECT * FROM components WHERE 1=1"
    params = []
    if category:
        query += " AND category=?"
        params.append(category)
    if status:
        query += " AND status=?"
        params.append(status)
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s])
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_component(cid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM components WHERE id=?", (cid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_versions(cid):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM component_versions WHERE component_id=? ORDER BY created_at DESC",
        (cid,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_component(data):
    conn = get_conn()
    cur = conn.execute("""INSERT INTO components
        (name, category, description, code, variants, props, status, author, version, dependencies, preview_text)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", tuple(data.values()))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def update_component(cid, data):
    conn = get_conn()
    conn.execute("""UPDATE components SET
        name=?, category=?, description=?, code=?, variants=?, props=?,
        status=?, author=?, version=?, dependencies=?, preview_text=?,
        updated_at=datetime('now','localtime') WHERE id=?""",
        tuple(data.values()) + (cid,))
    conn.commit()
    conn.close()

def delete_component(cid):
    conn = get_conn()
    conn.execute("DELETE FROM component_versions WHERE component_id=?", (cid,))
    conn.execute("DELETE FROM components WHERE id=?", (cid,))
    conn.commit()
    conn.close()

def save_version(cid, version, code, comment):
    conn = get_conn()
    conn.execute("INSERT INTO component_versions (component_id, version, code, comment) VALUES (?,?,?,?)",
                 (cid, version, code, comment))
    conn.execute("UPDATE components SET version=?, updated_at=datetime('now','localtime') WHERE id=?",
                 (version, cid))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) as c FROM components").fetchone()["c"]
    by_cat = conn.execute("SELECT category, COUNT(*) as cnt FROM components GROUP BY category ORDER BY cnt DESC").fetchall()
    by_status = conn.execute("SELECT status, COUNT(*) as cnt FROM components GROUP BY status ORDER BY cnt DESC").fetchall()
    total_versions = conn.execute("SELECT COUNT(*) as c FROM component_versions").fetchone()["c"]
    recent = conn.execute("SELECT * FROM components ORDER BY updated_at DESC LIMIT 5").fetchall()
    conn.close()
    return {
        "total": total,
        "by_cat": [dict(r) for r in by_cat],
        "by_status": [dict(r) for r in by_status],
        "total_versions": total_versions,
        "recent": [dict(r) for r in recent],
    }
