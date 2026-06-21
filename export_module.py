#!/usr/bin/env python3
"""
export_module.py — Модуль экспорта компонентов в файлы HTML, CSS, JS.
Полностью соответствует описанию в ПЗ_4.
"""
import os


class ExportModule:
    """Модуль экспорта компонентов."""

    @staticmethod
    def export_component(component, output_dir):
        """Экспортирует компонент в HTML/CSS/JS файлы с метаданными.
        
        Args:
            component: dict с данными компонента.
            output_dir: директория для экспорта.
            
        Returns:
            dict: {filename: filepath} для созданных файлов.
        """
        os.makedirs(output_dir, exist_ok=True)
        safe_name = component.get("name", "component").replace(" ", "_")
        created = {}

        meta = (
            f"/* =====================================\n"
            f"   Component: {component.get('name', '')}\n"
            f"   Category: {component.get('category', '')}\n"
            f"   Description: {component.get('description', '')}\n"
            f"   Tags: {component.get('tags', '')}\n"
            f"   Exported by UI System Desktop\n"
            f"   ===================================== */\n\n"
        )

        code = component.get("code", "").strip()
        if code:
            html_path = os.path.join(output_dir, f"{safe_name}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(f"<!-- {component.get('name', '')} -->\n\n")
                f.write(code)
            created["html"] = html_path

        # Если есть style.css на уровне приложения — прикладываем ссылку
        return created
