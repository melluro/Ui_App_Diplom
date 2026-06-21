#!/usr/bin/env python3
"""
data_store.py — Слой данных (Model)
Загрузка, сохранение и сериализация библиотеки компонентов в JSON.
Полностью соответствует описанию в ПЗ_4.
"""
import storage as db


class DataStore:
    """Хранилище данных компонентов.
    
    Делегирует операции существующему модулю storage.py.
    """

    def __init__(self):
        db.init_db()

    def load(self):
        """Загружает все компоненты из хранилища."""
        return db.get_all_components()

    def save(self, components):
        """Сохраняет список всех компонентов.
        
        Args:
            components: Полный список компонентов для сохранения.
        """
        for c in components:
            db.update_component(c["id"], c)

    def get_stats(self):
        """Возвращает статистику по компонентам."""
        return db.get_stats()
