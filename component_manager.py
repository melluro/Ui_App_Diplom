#!/usr/bin/env python3
"""
component_manager.py — Слой бизнес-логики (Controller)
CRUD-операции, поиск по названию, фильтрация по категории,
паттерн Observer для уведомления UI об изменениях.
Полностью соответствует описанию в ПЗ_4.
"""
import re
import storage as db


class ComponentManager:
    """Менеджер компонентов.
    
    Args:
        data_store: Экземпляр DataStore для доступа к данным.
    """

    def __init__(self, data_store=None):
        self._store = data_store
        self._components = []
        self._observers = []
        self._reload()

    def _reload(self):
        self._components = db.get_all_components()

    def subscribe(self, callback):
        """Подписывает UI на уведомления об изменениях."""
        self._observers.append(callback)

    def _notify(self):
        for cb in self._observers:
            cb()

    # ── CRUD ──

    def get_all(self):
        return self._components

    def get_by_id(self, cid):
        return db.get_component(cid)

    def get_categories(self):
        cats = set(c.get("category", "") for c in self._components)
        return sorted(cats)

    def add(self, data):
        cid = db.create_component(data)
        self._reload()
        self._notify()
        return cid

    def update(self, cid, data):
        db.update_component(cid, data)
        self._reload()
        self._notify()

    def delete(self, cid):
        db.delete_component(cid)
        self._reload()
        self._notify()

    # ── Поиск и фильтрация ──

    def search(self, query):
        """Ищет компоненты по названию (без учёта регистра, частичное совпадение)."""
        if not query:
            return self._components
        pattern = re.escape(query)
        return [c for c in self._components
                if re.search(pattern, c.get("name", ""), re.IGNORECASE)]

    def filter_by_category(self, category):
        """Фильтрует компоненты по категории."""
        if not category:
            return self._components
        return [c for c in self._components if c.get("category") == category]
