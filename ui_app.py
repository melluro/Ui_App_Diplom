#!/usr/bin/env python3
"""
UI System Desktop — Главное приложение
Модульная система компонентов пользовательского интерфейса
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
import tkinter as tk
from tkinter import ttk, messagebox
import storage as db
from component_manager import ComponentManager
from export_module import ExportModule

# ═══════════════════════════════════════════════════════════════
# ЦВЕТА И СТИЛИ
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "bg": "#f0f2f5",
    "bg2": "#e4e7ec",
    "bg_card": "#ffffff",
    "bg_hover": "#eef0ff",
    "text": "#1a1a2e",
    "text_dim": "#555577",
    "text_muted": "#9999b0",
    "accent": "#6C5CE7",
    "accent_hover": "#8B7FF7",
    "accent_bg": "#f0eeff",
    "green": "#22C55E",
    "yellow": "#EAB308",
    "red": "#EF4444",
    "border": "#d8dce6",
    "input_bg": "#ffffff",
    "sidebar_bg": "#ffffff",
    "topbar_bg": "#ffffff",
}

CATEGORIES = [
    ("🔘", "Кнопки", "buttons"),
    ("📝", "Поля ввода", "inputs"),
    ("🃏", "Карточки", "cards"),
    ("🪟", "Модальные окна", "modals"),
    ("🧭", "Навигация", "navigation"),
    ("📋", "Формы", "forms"),
    ("🔔", "Уведомления", "alerts"),
    ("📊", "Таблицы", "tables"),
    ("🏷", "Бейджи", "badges"),
    ("⏳", "Загрузчики", "loaders"),
    ("🔤", "Типографика", "typography"),
    ("📐", "Макеты", "layouts"),
]

STATUSES = ["✅ Готов", "🔄 В разработке", "⚠️ Требует рефакторинга", "📦 В архиве"]

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def make_button(parent, text, command=None, bg=None, fg=None, width=None, height=36, font_size=11):
    """Создаёт стандартную кнопку с единым стилем"""
    btn = tk.Button(parent, text=text, command=command,
                   font=("Segoe UI", font_size),
                   bg=bg or COLORS["accent"],
                   fg=fg or "#ffffff",
                   relief="flat", bd=0,
                   padx=18, pady=6,
                   cursor="hand2",
                   activebackground=COLORS["accent_hover"],
                   activeforeground="#ffffff")
    if width:
        btn.configure(width=width)
    return btn

def make_label(parent, text, font_size=12, bold=False, fg=None, **kwargs):
    return tk.Label(parent, text=text,
                   font=("Segoe UI", font_size, "bold" if bold else "normal"),
                   fg=fg or COLORS["text"], bg=COLORS["bg"], **kwargs)

def make_entry(parent, width=30):
    e = tk.Entry(parent, font=("Segoe UI", 11),
                bg=COLORS["input_bg"], fg=COLORS["text"],
                relief="solid", bd=1,
                highlightthickness=0,
                insertbackground=COLORS["text"])
    e.configure(width=width)
    return e

def make_text(parent, width=60, height=6):
    t = tk.Text(parent, font=("Consolas", 10),
               bg=COLORS["input_bg"], fg=COLORS["text"],
               relief="solid", bd=1,
               highlightthickness=0,
               insertbackground=COLORS["text"],
               padx=8, pady=8, wrap="word")
    t.configure(width=width, height=height)
    return t

def make_combobox(parent, values, width=25):
    cb = ttk.Combobox(parent, values=values, state="readonly", width=width)
    cb.set(values[0])
    return cb


class ScrollFrame(tk.Frame):
    """Прокручиваемая область"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg"], **kwargs)
        self.canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=COLORS["bg"])
        
        self.scroll_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="inner")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mw))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
    
    def _on_mw(self, e):
        self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")


# ═══════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════

class UISystemApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧩 UI System — Каталог компонентов")
        self.root.geometry("1200x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg"])
        
        self.current_view = "dashboard"
        self.search_var = tk.StringVar()
        self.filter_cat = tk.StringVar()
        self.filter_status = tk.StringVar()
        self.manager = None
        self._build_ui()
        
    def set_manager(self, manager):
        """Внедряет ComponentManager через Observer.
        Полностью соответствует архитектуре ПЗ_4."""
        self.manager = manager
        self.manager.subscribe(self._on_data_changed)
        self.show_dashboard()
        
    def _on_data_changed(self):
        """Колбэк Observer — обновление UI при изменении данных."""
        self.show_catalog()
    
    def _build_ui(self):
        # ── Сайдбар ──
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar_bg"], width=240, highlightthickness=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Логотип
        lf = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        lf.pack(fill="x", padx=16, pady=(20, 12))
        tk.Label(lf, text="🧩", font=("Segoe UI", 28), bg=COLORS["sidebar_bg"]).pack(anchor="w")
        tk.Label(lf, text="UI System", font=("Segoe UI", 18, "bold"),
                fg=COLORS["text"], bg=COLORS["sidebar_bg"]).pack(anchor="w")
        tk.Label(lf, text="Каталог компонентов", font=("Segoe UI", 10),
                fg=COLORS["text_dim"], bg=COLORS["sidebar_bg"]).pack(anchor="w")
        
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=8)
        
        # Навигация
        self.nav_buttons = []
        for icon, text, cmd in [
            ("🏠", "Главная", self.show_dashboard),
            ("📦", "Каталог", self.show_catalog),
            ("➕", "Новый компонент", self.show_add),
            ("📊", "Статистика", self.show_stats),
        ]:
            btn = tk.Label(self.sidebar, text=f"  {icon}  {text}",
                          font=("Segoe UI", 12),
                          fg=COLORS["text_dim"], bg=COLORS["sidebar_bg"],
                          anchor="w", padx=16, pady=8, cursor="hand2")
            btn.pack(fill="x", padx=8, pady=1)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["bg2"]))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=COLORS["sidebar_bg"]))
            self.nav_buttons.append(btn)
        
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=8)
        
        # Категории
        tk.Label(self.sidebar, text="  📂  КАТЕГОРИИ",
                font=("Segoe UI", 9, "bold"),
                fg=COLORS["text_muted"], bg=COLORS["sidebar_bg"],
                anchor="w").pack(fill="x", padx=16, pady=(8, 4))
        
        for icon, name, cat_id in CATEGORIES:
            lbl = tk.Label(self.sidebar, text=f"    {icon}  {name}",
                          font=("Segoe UI", 10),
                          fg=COLORS["text_dim"], bg=COLORS["sidebar_bg"],
                          anchor="w", padx=16, pady=3, cursor="hand2")
            lbl.pack(fill="x")
            lbl.bind("<Button-1>", lambda e, c=cat_id: self._filter_by_cat(c))
        
        # ── Основная область ──
        self.main_area = tk.Frame(self.root, bg=COLORS["bg"])
        self.main_area.pack(side="right", fill="both", expand=True)
        
        # Верхняя панель
        self.topbar = tk.Frame(self.main_area, bg=COLORS["topbar_bg"], height=52)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        
        self.topbar_title = tk.Label(self.topbar, text="🏠 Главная",
                                    font=("Segoe UI", 15, "bold"),
                                    fg=COLORS["text"], bg=COLORS["topbar_bg"])
        self.topbar_title.pack(side="left", padx=20, pady=10)
        
        # Поиск в топбаре
        sf = tk.Frame(self.topbar, bg=COLORS["topbar_bg"])
        sf.pack(side="right", padx=12, pady=8)
        
        self.search_entry = make_entry(sf, width=25)
        self.search_entry.pack(side="left", padx=4)
        self.search_entry.insert(0, "🔍 Поиск...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, "end") if self.search_entry.get() == "🔍 Поиск..." else None)
        self.search_entry.bind("<Return>", lambda e: self._search())
        
        btn = make_button(sf, "🔍 Найти", self._search, height=32, font_size=10)
        btn.pack(side="left", padx=2)
        
        # Контент
        self.content_frame = tk.Frame(self.main_area, bg=COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True)
    
    def _clear(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
    
    def _set_title(self, t):
        self.topbar_title.configure(text=t)
    
    def _nav_highlight(self, idx):
        for i, b in enumerate(self.nav_buttons):
            b.configure(bg=COLORS["bg2"] if i == idx else COLORS["sidebar_bg"])
    
    def _search(self):
        self.show_catalog()
    
    def _filter_by_cat(self, cat_id):
        self.filter_cat.set(cat_id)
        self.show_catalog()
    
    # ═══════════════════════════════════════════════════════
    # ДАШБОРД
    # ═══════════════════════════════════════════════════════
    
    def show_dashboard(self):
        self._clear()
        self._nav_highlight(0)
        self._set_title("🏠 Главная панель")
        
        stats = db.get_stats()
        
        # Заголовок
        hf = tk.Frame(self.content_frame, bg=COLORS["bg"])
        hf.pack(fill="x", pady=(24, 16), padx=32)
        
        tk.Label(hf, text="🧩  UI System", font=("Segoe UI", 28, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"]).pack()
        tk.Label(hf, text="Библиотека переиспользуемых компонентов для фронтенд-разработчиков",
                font=("Segoe UI", 12), fg=COLORS["text_dim"], bg=COLORS["bg"]).pack(pady=4)
        
        # Статистика
        sf = tk.Frame(hf, bg=COLORS["bg"])
        sf.pack(pady=12)
        
        for icon, label, val, color in [
            ("📦", "Всего", str(stats["total"]), COLORS["accent"]),
            ("📝", "Черновики", str(stats["by_status"][0]["cnt"]) if stats["by_status"] else "0", COLORS["yellow"]),
            ("✅", "Готово", str(stats["by_status"][1]["cnt"]) if len(stats["by_status"]) > 1 else "0", COLORS["green"]),
            ("📂", "Категорий", str(len(CATEGORIES)), COLORS["accent"]),
        ]:
            card = tk.Frame(sf, bg=COLORS["bg_card"], highlightbackground=COLORS["border"],
                          highlightthickness=1, width=150, height=85)
            card.pack(side="left", padx=5)
            card.pack_propagate(False)
            tk.Label(card, text=icon, font=("Segoe UI", 18), bg=COLORS["bg_card"]).pack(pady=(8, 0))
            tk.Label(card, text=val, font=("Segoe UI", 22, "bold"),
                    fg=color, bg=COLORS["bg_card"]).pack()
            tk.Label(card, text=label, font=("Segoe UI", 9),
                    fg=COLORS["text_dim"], bg=COLORS["bg_card"]).pack()
        
        # Кнопки
        af = tk.Frame(self.content_frame, bg=COLORS["bg"])
        af.pack(pady=12, padx=32, fill="x")
        
        make_button(af, "📦  Открыть каталог", self.show_catalog).pack(side="left", padx=4)
        make_button(af, "➕  Добавить компонент", self.show_add).pack(side="left", padx=4)
        make_button(af, "📊  Статистика", self.show_stats, bg=COLORS["green"]).pack(side="left", padx=4)
        
        if stats["recent"]:
            tk.Label(self.content_frame, text="🕐  Последние обновления",
                    font=("Segoe UI", 13, "bold"),
                    fg=COLORS["text"], bg=COLORS["bg"]
                    ).pack(anchor="w", padx=32, pady=(16, 8))
            for c in stats["recent"]:
                self._make_card(self.content_frame, c).pack(fill="x", padx=32, pady=2)
    
    # ═══════════════════════════════════════════════════════
    # КАТАЛОГ
    # ═══════════════════════════════════════════════════════
    
    def show_catalog(self):
        self._clear()
        self._nav_highlight(1)
        self._set_title("📦 Каталог компонентов")
        
        search = self.search_entry.get() if hasattr(self, 'search_entry') and self.search_entry.get() != "🔍 Поиск..." else ""
        cat = self.filter_cat.get()
        status = self.filter_status.get()
        
        # Фильтры
        ff = tk.Frame(self.content_frame, bg=COLORS["bg"])
        ff.pack(fill="x", padx=24, pady=(12, 8))
        
        tk.Label(ff, text="🔍", font=("Segoe UI", 14), bg=COLORS["bg"]).pack(side="left", padx=2)
        local_search = make_entry(ff, width=20)
        local_search.pack(side="left", padx=4)
        if search:
            local_search.insert(0, search)
        
        make_button(ff, "Найти", lambda: self._search_cat(local_search.get()),
                   height=30, font_size=10).pack(side="left", padx=2)
        
        tk.Label(ff, text="Тип:", font=("Segoe UI", 10), fg=COLORS["text_dim"],
                bg=COLORS["bg"]).pack(side="left", padx=(12, 4))
        
        cat_combo = ttk.Combobox(ff, values=["Все"] + [c[1] for c in CATEGORIES],
                                state="readonly", width=18)
        cat_combo.pack(side="left")
        cat_combo.bind("<<ComboboxSelected>>",
                      lambda e: self._filter_cat_combo(cat_combo.get(), local_search.get()))
        
        make_button(ff, "✕ Сброс", lambda: self._reset_cat(local_search),
                   height=30, font_size=10, bg=COLORS["bg2"], fg=COLORS["text_dim"]).pack(side="left", padx=4)
        
        # Список
        scroll = ScrollFrame(self.content_frame)
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        
        components = db.get_all_components(cat, status, search)
        
        if not components:
            tk.Label(scroll.scroll_frame, text="🧩", font=("Segoe UI", 36),
                    bg=COLORS["bg"]).pack(pady=(40, 8))
            tk.Label(scroll.scroll_frame, text="Компоненты не найдены",
                    font=("Segoe UI", 16, "bold"), fg=COLORS["text"],
                    bg=COLORS["bg"]).pack()
            tk.Label(scroll.scroll_frame, text="Измените параметры или создайте новый",
                    font=("Segoe UI", 11), fg=COLORS["text_dim"],
                    bg=COLORS["bg"]).pack(pady=4)
            make_button(scroll.scroll_frame, "➕ Создать компонент", self.show_add).pack(pady=12)
        else:
            for c in components:
                self._make_card(scroll.scroll_frame, c).pack(fill="x", pady=2, padx=4)
    
    def _search_cat(self, text):
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, text)
        self.show_catalog()
    
    def _filter_cat_combo(self, cat_name, search_text=""):
        for icon, name, cid in CATEGORIES:
            if name == cat_name:
                self.filter_cat.set(cid)
                break
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, search_text)
        self.show_catalog()
    
    def _reset_cat(self, local_search):
        self.filter_cat.set("")
        self.search_entry.delete(0, "end")
        local_search.delete(0, "end")
        self.show_catalog()
    
    def _make_card(self, parent, c):
        card = tk.Frame(parent, bg=COLORS["bg_card"],
                       highlightbackground=COLORS["border"],
                       highlightthickness=1, cursor="hand2")
        
        inner = tk.Frame(card, bg=COLORS["bg_card"])
        inner.pack(fill="both", expand=True, padx=14, pady=8)
        
        # Верх
        top = tk.Frame(inner, bg=COLORS["bg_card"])
        top.pack(fill="x")
        
        cat_icon = "🧩"
        for icon, name, cid in CATEGORIES:
            if cid == c["category"]:
                cat_icon = icon
                break
        
        tk.Label(top, text=f"{cat_icon} {c['category']}", font=("Segoe UI", 10),
                fg=COLORS["accent"], bg=COLORS["bg_card"]).pack(side="left")
        
        sc = COLORS["green"]
        if c["status"].startswith("🔄"): sc = COLORS["yellow"]
        elif c["status"].startswith("⚠"): sc = COLORS["red"]
        tk.Label(top, text=c["status"], font=("Segoe UI", 10),
                fg=sc, bg=COLORS["bg_card"]).pack(side="right")
        
        # Название
        tk.Label(inner, text=c["name"], font=("Segoe UI", 13, "bold"),
                fg=COLORS["text"], bg=COLORS["bg_card"],
                anchor="w").pack(fill="x", pady=(4, 2))
        
        # Описание
        desc = c["description"][:80] + "..." if len(c["description"]) > 80 else (c["description"] or "Нет описания")
        tk.Label(inner, text=desc, font=("Segoe UI", 10),
                fg=COLORS["text_dim"], bg=COLORS["bg_card"],
                anchor="w", wraplength=500).pack(fill="x")
        
        # Низ
        bot = tk.Frame(inner, bg=COLORS["bg_card"])
        bot.pack(fill="x", pady=(6, 0))
        
        tk.Label(bot, text=f"v{c['version']}", font=("Consolas", 9),
                fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(side="left")
        tk.Label(bot, text=c["updated_at"][:10], font=("Segoe UI", 9),
                fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(side="right")
        
        cid = c["id"]
        # Bind click to entire card
        for w in [card, inner, top, bot]:
            w.bind("<Button-1>", lambda e, id=cid: self.show_component(id))
            for ch in w.winfo_children():
                ch.bind("<Button-1>", lambda e, id=cid: self.show_component(id))
        
        card.bind("<Enter>", lambda e: card.configure(bg=COLORS["bg_hover"]))
        card.bind("<Leave>", lambda e: card.configure(bg=COLORS["bg_card"]))
        inner.bind("<Enter>", lambda e: card.configure(bg=COLORS["bg_hover"]))
        inner.bind("<Leave>", lambda e: card.configure(bg=COLORS["bg_card"]))
        
        return card
    
    # ═══════════════════════════════════════════════════════
    # ПРОСМОТР КОМПОНЕНТА
    # ═══════════════════════════════════════════════════════
    
    def show_component(self, cid):
        c = db.get_component(cid)
        if not c:
            messagebox.showerror("Ошибка", "Компонент не найден")
            return
        
        self._clear()
        self._set_title(f"👁 {c['name']}")
        
        scroll = ScrollFrame(self.content_frame)
        scroll.pack(fill="both", expand=True, padx=24, pady=12)
        sc = scroll.scroll_frame
        
        # Заголовок
        hf = tk.Frame(sc, bg=COLORS["bg"])
        hf.pack(fill="x", pady=(0, 12))
        
        mf = tk.Frame(hf, bg=COLORS["bg"])
        mf.pack(fill="x")
        
        cat_icon = "🧩"
        for icon, name, cid2 in CATEGORIES:
            if cid2 == c["category"]:
                cat_icon = icon
                break
        tk.Label(mf, text=f"{cat_icon} {c['category']}", font=("Segoe UI", 11),
                fg=COLORS["accent"], bg=COLORS["bg"]).pack(side="left", padx=(0, 8))
        tk.Label(mf, text=c["status"], font=("Segoe UI", 11),
                fg=COLORS["text_dim"], bg=COLORS["bg"]).pack(side="left")
        tk.Label(mf, text=f"  v{c['version']}", font=("Consolas", 11),
                fg=COLORS["text_muted"], bg=COLORS["bg"]).pack(side="left")
        
        tk.Label(hf, text=c["name"], font=("Segoe UI", 22, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"],
                anchor="w").pack(fill="x", pady=(4, 0))
        
        if c.get("author"):
            tk.Label(hf, text=f"✍️ Автор: {c['author']}", font=("Segoe UI", 11),
                    fg=COLORS["text_dim"], bg=COLORS["bg"]).pack(anchor="w")
        
        # Кнопки
        af = tk.Frame(hf, bg=COLORS["bg"])
        af.pack(fill="x", pady=(10, 0))
        
        make_button(af, "✏️ Редактировать", lambda: self.show_edit(c["id"])).pack(side="left", padx=4)
        make_button(af, "📥 Экспорт", lambda: self._export(c), bg=COLORS["bg2"], fg=COLORS["text"]).pack(side="left", padx=4)
        make_button(af, "🗑 Удалить", lambda: self._delete(c["id"]), bg=COLORS["red"]).pack(side="left", padx=4)
        
        # Описание
        if c.get("description"):
            self._sec(sc, "📝 Описание")
            tk.Label(sc, text=c["description"], font=("Segoe UI", 11),
                    fg=COLORS["text"], bg=COLORS["bg"], wraplength=700,
                    justify="left").pack(anchor="w", padx=16, pady=4)
        
        # Props
        if c.get("props") and c["props"] not in ("{}", ""):
            try:
                props = json.loads(c["props"])
                self._sec(sc, "⚙️ Свойства (Props)")
                for key, val in props.items():
                    pf = tk.Frame(sc, bg=COLORS["bg_card"],
                                highlightbackground=COLORS["border"],
                                highlightthickness=1)
                    pf.pack(fill="x", padx=16, pady=2)
                    tk.Label(pf, text=key, font=("Consolas", 10, "bold"),
                            fg=COLORS["accent"], bg=COLORS["bg_card"],
                            width=18, anchor="w").pack(side="left", padx=8, pady=5)
                    if isinstance(val, dict):
                        tk.Label(pf, text=val.get("type", ""),
                                font=("Segoe UI", 10), fg=COLORS["text_dim"],
                                bg=COLORS["bg_card"], width=12, anchor="w").pack(side="left")
                        tk.Label(pf, text=val.get("default", ""),
                                font=("Segoe UI", 10), fg=COLORS["text_muted"],
                                bg=COLORS["bg_card"], width=12, anchor="w").pack(side="left")
                        tk.Label(pf, text=val.get("description", ""),
                                font=("Segoe UI", 10), fg=COLORS["text"],
                                bg=COLORS["bg_card"], anchor="w").pack(side="left", fill="x", expand=True)
                    else:
                        tk.Label(pf, text=str(val), font=("Segoe UI", 10),
                                fg=COLORS["text"], bg=COLORS["bg_card"],
                                anchor="w").pack(side="left", fill="x", expand=True)
            except: pass
        
        # Variants
        if c.get("variants") and c["variants"] not in ("[]", ""):
            try:
                variants = json.loads(c["variants"])
                self._sec(sc, "🎨 Варианты")
                vf = tk.Frame(sc, bg=COLORS["bg"])
                vf.pack(fill="x", padx=16, pady=4)
                for v in variants:
                    vname = v.get("name", str(v)) if isinstance(v, dict) else str(v)
                    vc = tk.Frame(vf, bg=COLORS["bg_card"],
                                highlightbackground=COLORS["border"],
                                highlightthickness=1)
                    vc.pack(side="left", padx=4, pady=4, fill="x", expand=True)
                    tk.Label(vc, text=vname, font=("Segoe UI", 11, "bold"),
                            fg=COLORS["text"], bg=COLORS["bg_card"]
                            ).pack(anchor="w", padx=10, pady=(8, 2))
                    if v.get("code"):
                        tk.Label(vc, text=v["code"][:60], font=("Consolas", 9),
                                fg=COLORS["text_dim"], bg=COLORS["bg_card"],
                                anchor="w").pack(fill="x", padx=10, pady=(0, 6))
            except: pass
        
        # Зависимости
        if c.get("dependencies"):
            self._sec(sc, "📎 Зависимости")
            tk.Label(sc, text=c["dependencies"], font=("Segoe UI", 11),
                    fg=COLORS["text"], bg=COLORS["bg"]
                    ).pack(anchor="w", padx=16, pady=4)
        
        # Код
        if c.get("code"):
            self._sec(sc, "💻 Код компонента")
            cf = tk.Frame(sc, bg=COLORS["bg2"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
            cf.pack(fill="x", padx=16, pady=4)
            ct = tk.Text(cf, bg=COLORS["bg2"], fg=COLORS["text"],
                        font=("Consolas", 10), relief="flat",
                        bd=0, highlightthickness=0, height=8, wrap="none")
            ct.pack(fill="x", padx=10, pady=8)
            ct.insert("1.0", c["code"])
            ct.configure(state="disabled")
        
        # Версии
        self._sec(sc, "📦 История версий")
        versions = db.get_versions(c["id"])
        if versions:
            for v in versions:
                vf = tk.Frame(sc, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["border"],
                            highlightthickness=1)
                vf.pack(fill="x", padx=16, pady=2)
                tk.Label(vf, text=f"v{v['version']}", font=("Consolas", 10, "bold"),
                        fg=COLORS["accent"], bg=COLORS["bg_card"],
                        width=10, anchor="w").pack(side="left", padx=8, pady=5)
                tk.Label(vf, text=v["created_at"][:16], font=("Segoe UI", 10),
                        fg=COLORS["text_dim"], bg=COLORS["bg_card"],
                        width=18, anchor="w").pack(side="left")
                tk.Label(vf, text=v.get("comment", ""), font=("Segoe UI", 10),
                        fg=COLORS["text"], bg=COLORS["bg_card"],
                        anchor="w").pack(side="left", padx=8)
        else:
            tk.Label(sc, text="Нет сохранённых версий", font=("Segoe UI", 11),
                    fg=COLORS["text_muted"], bg=COLORS["bg"]
                    ).pack(anchor="w", padx=16, pady=4)
        
        # Сохранить версию
        vf = tk.Frame(sc, bg=COLORS["bg"])
        vf.pack(fill="x", padx=16, pady=(16, 24))
        tk.Label(vf, text="💾  Сохранить версию:", font=("Segoe UI", 12, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"]).pack(anchor="w", pady=(0, 6))
        vi = tk.Frame(vf, bg=COLORS["bg"])
        vi.pack(fill="x")
        ver_e = make_entry(vi, width=12)
        ver_e.pack(side="left", padx=4)
        ver_e.insert(0, "1.1.0")
        com_e = make_entry(vi, width=30)
        com_e.pack(side="left", padx=4)
        com_e.insert(0, "Что изменилось?")
        com_e.bind("<FocusIn>", lambda e: com_e.delete(0, "end") if com_e.get() == "Что изменилось?" else None)
        
        cid_local = c["id"]
        code_text_local = c["code"]
        make_button(vi, "💾 Сохранить",
                   lambda: self._save_version(cid_local, ver_e, com_e, code_text_local),
                   height=32, font_size=10).pack(side="left", padx=4)
    
    def _sec(self, parent, text):
        f = tk.Frame(parent, bg=COLORS["bg"])
        f.pack(fill="x", pady=(18, 6))
        tk.Label(f, text=text, font=("Segoe UI", 13, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"]).pack(anchor="w", padx=16)
        tk.Frame(f, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=(6, 0))
    
    # ═══════════════════════════════════════════════════════
    # ДОБАВЛЕНИЕ / РЕДАКТИРОВАНИЕ
    # ═══════════════════════════════════════════════════════
    
    def show_add(self):
        self._clear()
        self._nav_highlight(2)
        self._set_title("➕ Новый компонент")
        self._edit_form({}, "add")
    
    def show_edit(self, cid):
        c = db.get_component(cid)
        if not c:
            messagebox.showerror("Ошибка", "Компонент не найден")
            return
        self._clear()
        self._set_title(f"✏️ Редактировать: {c['name']}")
        self._edit_form(c, "edit")
    
    def _edit_form(self, c, mode):
        scroll = ScrollFrame(self.content_frame)
        scroll.pack(fill="both", expand=True, padx=24, pady=12)
        sc = scroll.scroll_frame
        
        data = {}
        
        def fl(parent, text, **kw):
            tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
                    fg=COLORS["text"], bg=COLORS["bg"],
                    anchor="w").pack(fill="x", padx=4, pady=(10, 2))
        
        # Название
        fl(sc, "📛 Название компонента *")
        ne = make_entry(sc, width=40)
        ne.pack(anchor="w", padx=4, pady=2)
        ne.insert(0, c.get("name", ""))
        
        # Категория
        fl(sc, "📂 Категория *")
        cf = tk.Frame(sc, bg=COLORS["bg"])
        cf.pack(fill="x", pady=2)
        cat_var = tk.StringVar(value=c.get("category", ""))
        for icon, name, cid in CATEGORIES:
            rb = tk.Radiobutton(cf, text=f"{icon} {name}", variable=cat_var, value=cid,
                              bg=COLORS["bg"], fg=COLORS["text"],
                              selectcolor=COLORS["bg"],
                              font=("Segoe UI", 10),
                              activebackground=COLORS["bg"])
            rb.pack(side="left", padx=2)
        
        # Описание
        fl(sc, "📝 Описание")
        dt = make_text(sc, width=70, height=4)
        dt.pack(fill="x", padx=4, pady=2)
        if c.get("description"): dt.insert("1.0", c["description"])
        
        # Статус, версия, автор
        r1 = tk.Frame(sc, bg=COLORS["bg"])
        r1.pack(fill="x", pady=8)
        
        tk.Label(r1, text="📌 Статус", font=("Segoe UI", 10, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"]).pack(side="left", padx=4)
        sv = tk.StringVar(value=c.get("status", STATUSES[0]))
        cb = ttk.Combobox(r1, textvariable=sv, values=STATUSES, state="readonly", width=20)
        cb.pack(side="left", padx=4)
        
        tk.Label(r1, text="📌 Версия", font=("Segoe UI", 10, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"]).pack(side="left", padx=(16, 4))
        ve = make_entry(r1, width=10)
        ve.pack(side="left", padx=4)
        ve.insert(0, c.get("version", "1.0.0"))
        
        tk.Label(r1, text="✍️ Автор", font=("Segoe UI", 10, "bold"),
                fg=COLORS["text"], bg=COLORS["bg"]).pack(side="left", padx=(16, 4))
        ae = make_entry(r1, width=15)
        ae.pack(side="left", padx=4)
        ae.insert(0, c.get("author", ""))
        
        # Зависимости
        fl(sc, "📎 Зависимости")
        de = make_entry(sc, width=40)
        de.pack(anchor="w", padx=4, pady=2)
        de.insert(0, c.get("dependencies", ""))
        
        # Превью
        fl(sc, "👁 Текст для предпросмотра")
        pe = make_entry(sc, width=40)
        pe.pack(anchor="w", padx=4, pady=2)
        pe.insert(0, c.get("preview_text", ""))
        
        # Props JSON
        fl(sc, "⚙️ Свойства (JSON)")
        pt = make_text(sc, width=70, height=5)
        pt.pack(fill="x", padx=4, pady=2)
        if c.get("props"):
            try: pt.insert("1.0", json.dumps(json.loads(c["props"]), indent=2, ensure_ascii=False))
            except: pt.insert("1.0", c["props"])
        else:
            pt.insert("1.0", '{\n  "variant": {"type": "string", "default": "primary", "description": "Стиль"}\n}')
        
        # Variants JSON
        fl(sc, "🎨 Варианты (JSON)")
        vt = make_text(sc, width=70, height=5)
        vt.pack(fill="x", padx=4, pady=2)
        if c.get("variants"):
            try: vt.insert("1.0", json.dumps(json.loads(c["variants"]), indent=2, ensure_ascii=False))
            except: vt.insert("1.0", c["variants"])
        else:
            vt.insert("1.0", '[\n  {"name": "Primary", "code": "<Button>"}\n]')
        
        # Код
        fl(sc, "💻 Код компонента")
        ct = make_text(sc, width=70, height=10)
        ct.pack(fill="x", padx=4, pady=2)
        if c.get("code"): ct.insert("1.0", c["code"])
        else: ct.insert("1.0", "// Код компонента")
        
        # Кнопки
        bf = tk.Frame(sc, bg=COLORS["bg"])
        bf.pack(pady=16)
        
        if mode == "add":
            make_button(bf, "➕ Создать компонент",
                       lambda: self._save(ne, cat_var, dt, sv, ve, ae, de, pe, pt, vt, ct, "add"),
                       height=38, font_size=12).pack(side="left", padx=6)
        else:
            make_button(bf, "💾 Сохранить изменения",
                       lambda: self._save(ne, cat_var, dt, sv, ve, ae, de, pe, pt, vt, ct, "edit", c["id"]),
                       height=38, font_size=12).pack(side="left", padx=6)
        
        make_button(bf, "✕ Отмена",
                   lambda: self.show_component(c["id"]) if mode == "edit" else self.show_dashboard(),
                   height=38, font_size=12, bg=COLORS["bg2"], fg=COLORS["text"]).pack(side="left", padx=6)
    
    def _save(self, ne, cat_var, dt, sv, ve, ae, de, pe, pt, vt, ct, mode, cid=None):
        name = ne.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Название обязательно")
            return
        if not cat_var.get():
            messagebox.showwarning("Ошибка", "Выберите категорию")
            return
        
        data = {
            "name": name,
            "category": cat_var.get(),
            "description": dt.get("1.0", "end-1c"),
            "code": ct.get("1.0", "end-1c"),
            "variants": vt.get("1.0", "end-1c"),
            "props": pt.get("1.0", "end-1c"),
            "status": sv.get(),
            "author": ae.get(),
            "version": ve.get() or "1.0.0",
            "dependencies": de.get(),
            "preview_text": pe.get(),
        }
        
        try:
            if data["props"]: json.loads(data["props"])
            if data["variants"]: json.loads(data["variants"])
        except json.JSONDecodeError:
            messagebox.showwarning("Ошибка", "Некорректный JSON")
            return
        
        if mode == "add":
            cid = db.create_component(data)
            messagebox.showinfo("Готово", f"✅ Компонент «{name}» создан!")
            self.show_component(cid)
        else:
            db.update_component(cid, data)
            messagebox.showinfo("Готово", f"✅ Компонент «{name}» обновлён!")
            self.show_component(cid)
    
    def _delete(self, cid):
        c = db.get_component(cid)
        if c and messagebox.askyesno("Удаление", f"Удалить компонент «{c['name']}»?"):
            db.delete_component(cid)
            messagebox.showinfo("Готово", "🗑 Компонент удалён")
            self.show_catalog()
    
    def _save_version(self, cid, ve, ce, code):
        c = db.get_component(cid)
        if not c: return
        version = ve.get() or c["version"]
        comment = ce.get()
        if comment == "Что изменилось?": comment = ""
        db.save_version(cid, version, code, comment)
        messagebox.showinfo("Готово", f"📦 Версия {version} сохранена!")
        self.show_component(cid)
    
    def _export(self, c):
        """Экспорт компонента в HTML + CSS + JS"""
        import tkinter.filedialog as fd
        folder = fd.askdirectory(title="Выберите папку для экспорта")
        if not folder:
            return
        
        safe_name = c["name"].replace(" ", "_").replace("/", "_").replace("\\", "_")
        comp_folder = os.path.join(folder, safe_name)
        os.makedirs(comp_folder, exist_ok=True)
        
        # ── HTML ──
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{c['name']} — UI Component</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="component-wrapper">
    <div class="component-header">
      <span class="component-badge">{c['category']}</span>
      <span class="component-status {c['status'][0] == '✅' and 'ready' or c['status'][0] == '🔄' and 'wip' or 'alert'}">{c['status']}</span>
      <span class="component-version">v{c['version']}</span>
    </div>
    <h1 class="component-title">{c['name']}</h1>
    <p class="component-desc">{c.get('description', '')}</p>
    <hr>
    <div class="component-demo" id="demo">
      <!-- Сюда рендерится компонент -->
    </div>
  </div>
  <script src="script.js"></script>
</body>
</html>"""
        
        # ── CSS ──
        css = f"""/* {c['name']} — UI Component */
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: 'Segoe UI', -apple-system, sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
}}

.component-wrapper {{
  max-width: 800px;
  width: 100%;
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

.component-header {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}}

.component-badge {{
  background: #f0eeff;
  color: #6C5CE7;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}}

.component-status {{
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
}}
.component-status.ready {{
  background: #dcfce7;
  color: #16a34a;
}}
.component-status.wip {{
  background: #fef9c3;
  color: #ca8a04;
}}
.component-status.alert {{
  background: #fee2e2;
  color: #dc2626;
}}

.component-version {{
  font-family: monospace;
  font-size: 12px;
  color: #9999b0;
  margin-left: auto;
}}

.component-title {{
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
}}

.component-desc {{
  font-size: 14px;
  color: #555577;
  line-height: 1.5;
  margin-bottom: 16px;
}}

hr {{
  border: none;
  border-top: 1px solid #d8dce6;
  margin: 16px 0 24px;
}}

.component-demo {{
  min-height: 100px;
}}
"""
        
        # ── JS ──
        code = c.get("code", "// Нет кода")
        js = f"""// {c['name']} — UI Component
// v{c['version']}

(function() {{
  'use strict';

  const demo = document.getElementById('demo');
  if (!demo) return;

  // ── Код компонента ──
  {code}

}})();
"""
        
        with open(os.path.join(comp_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        with open(os.path.join(comp_folder, "style.css"), "w", encoding="utf-8") as f:
            f.write(css)
        with open(os.path.join(comp_folder, "script.js"), "w", encoding="utf-8") as f:
            f.write(js)
        
        messagebox.showinfo("Готово", f"📥 Экспортировано в:\n{comp_folder}")
    
    # ═══════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════
    
    def show_stats(self):
        self._clear()
        self._nav_highlight(3)
        self._set_title("📊 Статистика библиотеки")
        
        stats = db.get_stats()
        
        # Карточки
        sf = tk.Frame(self.content_frame, bg=COLORS["bg"])
        sf.pack(pady=20, padx=32)
        
        for icon, val, label, color in [
            ("📦", str(stats["total"]), "Всего компонентов", COLORS["accent"]),
            ("📂", str(len(CATEGORIES)), "Категорий", COLORS["accent"]),
            ("🔄", str(stats["total_versions"]), "Версий", COLORS["green"]),
        ]:
            card = tk.Frame(sf, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["border"],
                          highlightthickness=1, width=170, height=85)
            card.pack(side="left", padx=6)
            card.pack_propagate(False)
            tk.Label(card, text=icon, font=("Segoe UI", 18), bg=COLORS["bg_card"]).pack(pady=(6, 0))
            tk.Label(card, text=val, font=("Segoe UI", 26, "bold"),
                    fg=color, bg=COLORS["bg_card"]).pack()
            tk.Label(card, text=label, font=("Segoe UI", 9),
                    fg=COLORS["text_dim"], bg=COLORS["bg_card"]).pack()
        
        # По категориям
        tk.Label(self.content_frame, text="📊  Компонентов по категориям",
                font=("Segoe UI", 15, "bold"), fg=COLORS["text"],
                bg=COLORS["bg"]).pack(anchor="w", padx=32, pady=(24, 8))
        
        if stats["by_cat"]:
            max_cnt = max(item["cnt"] for item in stats["by_cat"])
            for item in stats["by_cat"]:
                cat_icon = "🧩"
                cat_name = item["category"]
                for icon, name, cid in CATEGORIES:
                    if cid == item["category"]:
                        cat_icon = icon
                        cat_name = name
                        break
                
                row = tk.Frame(self.content_frame, bg=COLORS["bg"])
                row.pack(fill="x", padx=32, pady=2)
                
                tk.Label(row, text=f"{cat_icon} {cat_name}", font=("Segoe UI", 11),
                        fg=COLORS["text"], bg=COLORS["bg"],
                        width=25, anchor="w").pack(side="left")
                
                bf = tk.Frame(row, bg=COLORS["bg2"], height=20)
                bf.pack(side="left", fill="x", expand=True, padx=8)
                
                bw = int(item["cnt"] / max_cnt * 300) if max_cnt > 0 else 0
                bar = tk.Frame(bf, bg=COLORS["accent"], width=bw, height=20)
                bar.pack(side="left")
                
                tk.Label(row, text=str(item["cnt"]), font=("Segoe UI", 11, "bold"),
                        fg=COLORS["accent"], bg=COLORS["bg"],
                        width=4).pack(side="left")
        else:
            tk.Label(self.content_frame, text="Нет данных. Добавьте компоненты в каталог.",
                    font=("Segoe UI", 11), fg=COLORS["text_muted"],
                    bg=COLORS["bg"]).pack(padx=32, pady=8)
    
    def run(self):
        self.root.mainloop()
