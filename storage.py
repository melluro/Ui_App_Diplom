#!/usr/bin/env python3
"""JSON-хранилище компонентов UI System"""
import json
import os
import shutil
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_system.json")
BACKUP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_system_backup.json")


def _load():
    if not os.path.exists(DATA_PATH):
        return {"components": [], "next_id": 1, "versions": {}}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_db():
    if not os.path.exists(DATA_PATH):
        _save({"components": [], "next_id": 1, "versions": {}})


# ── CRUD ──────────────────────────────────────────────────────

def get_all_components(category="", status="", search=""):
    data = _load()
    results = []
    for c in data["components"]:
        if category and c["category"] != category:
            continue
        if status and c["status"] != status:
            continue
        if search:
            s = search.lower()
            if s not in c["name"].lower() and s not in c.get("description", "").lower():
                continue
        results.append(c)
    results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return results


def get_component(cid):
    data = _load()
    for c in data["components"]:
        if c["id"] == cid:
            return c
    return None


def get_versions(cid):
    data = _load()
    return data["versions"].get(str(cid), [])


def create_component(data):
    db = _load()
    cid = db["next_id"]
    db["next_id"] += 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    component = {
        "id": cid,
        "name": data["name"],
        "category": data["category"],
        "description": data.get("description", ""),
        "code": data.get("code", ""),
        "variants": data.get("variants", "[]"),
        "props": data.get("props", "{}"),
        "status": data.get("status", "✅ Готов"),
        "author": data.get("author", ""),
        "version": data.get("version", "1.0.0"),
        "dependencies": data.get("dependencies", ""),
        "preview_text": data.get("preview_text", ""),
        "created_at": now,
        "updated_at": now,
    }
    db["components"].append(component)
    db["versions"][str(cid)] = []
    _save(db)
    return cid


def update_component(cid, data):
    db = _load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i, c in enumerate(db["components"]):
        if c["id"] == cid:
            db["components"][i].update({
                "name": data["name"],
                "category": data["category"],
                "description": data.get("description", ""),
                "code": data.get("code", ""),
                "variants": data.get("variants", "[]"),
                "props": data.get("props", "{}"),
                "status": data.get("status", "✅ Готов"),
                "author": data.get("author", ""),
                "version": data.get("version", "1.0.0"),
                "dependencies": data.get("dependencies", ""),
                "preview_text": data.get("preview_text", ""),
                "updated_at": now,
            })
            break
    _save(db)


def delete_component(cid):
    db = _load()
    db["components"] = [c for c in db["components"] if c["id"] != cid]
    db["versions"].pop(str(cid), None)
    _save(db)


def save_version(cid, version, code, comment):
    db = _load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vid = len(db["versions"].get(str(cid), [])) + 1
    entry = {"id": vid, "version": version, "code": code, "comment": comment, "created_at": now}
    db["versions"].setdefault(str(cid), []).insert(0, entry)
    # обновить версию в компоненте
    for c in db["components"]:
        if c["id"] == cid:
            c["version"] = version
            c["updated_at"] = now
            break
    _save(db)


def get_stats():
    db = _load()
    total = len(db["components"])
    by_cat = {}
    by_status = {}
    total_versions = sum(len(v) for v in db["versions"].values())
    for c in db["components"]:
        by_cat[c["category"]] = by_cat.get(c["category"], 0) + 1
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    recent = sorted(db["components"], key=lambda x: x.get("updated_at", ""), reverse=True)[:5]
    return {
        "total": total,
        "by_cat": [{"category": k, "cnt": v} for k, v in sorted(by_cat.items(), key=lambda x: -x[1])],
        "by_status": [{"status": k, "cnt": v} for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
        "total_versions": total_versions,
        "recent": recent,
    }
