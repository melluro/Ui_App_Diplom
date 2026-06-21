#!/usr/bin/env python3
"""
UI System Desktop — Модульная система компонентов интерфейса
Точка входа с инъекцией зависимостей.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

os.environ['UI_SYSTEM_ROOT'] = os.path.dirname(os.path.abspath(__file__))

from data_store import DataStore
from component_manager import ComponentManager

# Инъекция зависимостей: данные -> бизнес-логика -> UI
store = DataStore()
manager = ComponentManager(store)

# UI подключается к manager через Observer внутри ui_app
# Импортируем и запускаем
import ui_app

if __name__ == "__main__":
    # Получаем app и передаём manager
    app = ui_app.UISystemApp()
    app.set_manager(manager)
    app.run()
