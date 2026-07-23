import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import broadlink
import time
import os
import json
import threading
import subprocess
import re
from datetime import datetime

# Stałe konfiguracyjne
CONFIG_FILE = "config.json"
CODES_FILE = "codes_db.json"
EXPORT_DIR = "codes_export"

# Rozszerzona baza urządzeń Broadlink (Nazwa -> Kod HEX)
BROADLINK_MODELS = {
    "RM4 Pro / RM4c Pro (0x5f36)": "0x5f36",
    "RM4 Pro v2 (0x6026)": "0x6026",
    "RM4 Pro v3 / S (0x653c)": "0x653c",
    "RM4 Mini (0x51da)": "0x51da",
    "RM4 Mini v2 (0x610e)": "0x610e",
    "RM4c Mini (0x62bc)": "0x62bc",
    "RM3 Mini - Black Bean (0x2737)": "0x2737",
    "RM3 Mini v2 (0x27c1)": "0x27c1",
    "RM2 / RM Pro Starszy (0x272a)": "0x272a",
    "RM Pro+ Starszy (0x2787)": "0x2787",
    "RM Plus Starszy (0x278b)": "0x278b",
    "Własny / Custom HEX": "CUSTOM"
}

# Słownik Tłumaczeń (PL / EN)
I18N = {
    "PL": {
        "header_conn": "🔌 USTAWIENIA POŁĄCZENIA BROADLINK",
        "header_action": "🎮 NOWY KOD / AKCJE",
        "header_db": "📚 BAZA ZAPISANYCH KODÓW IR / RF",
        "header_logs": "📜 KONSOLA / SYST_LOGS",
        "label_ip": "IP:",
        "label_mac": "MAC:",
        "label_model": "Model:",
        "label_name": "Nazwa:",
        "label_cat": "Kategoria:",
        "label_search": "Szukaj:",
        "btn_guide": "📜 Instrukcja",
        "btn_arp": "🔍 Skanuj ARP",
        "btn_connect": "⚡ Połącz",
        "btn_learn_ir": "🔴 Ucz IR",
        "btn_learn_rf": "📡 Ucz RF (433/315)",
        "btn_send_input": "🚀 Wyślij wpisany",
        "btn_test": "▶️ Testuj (Wyślij)",
        "btn_copy": "📋 Kopiuj HEX",
        "btn_rename": "✏️ Zmień Nazwę",
        "btn_delete": "🗑️ Usuń Kod",
        "btn_export": "📂 Eksportuj TXT/JSON",
        "col_name": "Nazwa Kodu",
        "col_type": "Typ",
        "col_cat": "Kategoria",
        "col_date": "Data Utworzenia",
        "col_len": "Długość Kodu",
        "default_cat": "Ogólne",
        "msg_err_ip": "Wpisz poprawny adres IP i MAC urządzenia!",
        "msg_connected": "✅ Połączono pomyślnie z urządzeniem Broadlink!",
        "msg_conn_err": "❌ Błąd połączenia:",
        "msg_learning_ir": "🔴 Aktywacja trybu nauki IR... Naciśnij przycisk na pilocie IR.",
        "msg_ir_success": "✅ Pomyślnie przechwycono kod IR dla",
        "msg_ir_timeout": "⏱️ Przekroczono czas oczekiwania na sygnał IR.",
        "msg_rf_step1": "📡 KROK 1: Skanowanie częstotliwości RF... PRZYTRZYMAJ przycisk na pilocie RF.",
        "msg_rf_step2": "⚡ KROK 2: Częstotliwość złapana! PUSZCZAJ I NACISKAJ wielokrotnie przycisk RF...",
        "msg_rf_success": "🎉 Sukces! Zapisano kod RF dla",
        "msg_rf_timeout": "⏱️ Nie przechwycono pakietu danych RF.",
        "msg_sent": "🚀 Wysłano kod:",
        "msg_copied": "📋 Skopiowano HEX dla",
        "msg_renamed": "✏️ Zmieniono nazwę:",
        "msg_deleted": "🗑️ Usunięto z bazy:",
        "msg_exported": "📂 Wyeksportowano kodów:",
        "guide_title": "Instrukcja - Jak znaleźć IP i MAC",
        "guide_content": (
            "📱 METODA 1: Aplikacja BroadLink w telefonie\n"
            "--------------------------------------------------\n"
            "1. Otwórz aplikację BroadLink na smartfonie.\n"
            "2. Wejdź w swoje urządzenie RM4 Pro / Mini.\n"
            "3. Kliknij ikonę '...' (Ustawienia w prawym górnym rogu).\n"
            "4. Przejdź do 'Device Info' (Informacje o urządzeniu).\n"
            "5. Przepisz adres IP oraz MAC tutaj w programie.\n\n"
            "⚠️ BARDZO WAŻNE:\n"
            "W tym samym menu WYŁĄCZ opcję 'Lock device' (Zablokuj urządzenie)!\n"
            "Bez tego urządzenie odrzuca połączenia lokalne z komputera.\n\n"
            "🌐 METODA 2: Panel Routera (DHCP)\n"
            "--------------------------------------------------\n"
            "1. Wejdź na stronę routera (np. 192.168.1.1 lub 192.168.0.1).\n"
            "2. Zobacz zakładkę 'Połączone Urządzenia' / 'DHCP Client List'.\n"
            "3. Szukaj urządzenia z MAC od E8:16:56, 34:EA:E7 lub 78:0F:77."
        )
    },
    "EN": {
        "header_conn": "🔌 BROADLINK CONNECTION SETTINGS",
        "header_action": "🎮 NEW CODE / ACTIONS",
        "header_db": "📚 SAVED IR / RF CODES DATABASE",
        "header_logs": "📜 CONSOLE / SYST_LOGS",
        "label_ip": "IP:",
        "label_mac": "MAC:",
        "label_model": "Model:",
        "label_name": "Name:",
        "label_cat": "Category:",
        "label_search": "Search:",
        "btn_guide": "📜 Guide",
        "btn_arp": "🔍 Scan ARP",
        "btn_connect": "⚡ Connect",
        "btn_learn_ir": "🔴 Learn IR",
        "btn_learn_rf": "📡 Learn RF (433/315)",
        "btn_send_input": "🚀 Send Entered",
        "btn_test": "▶️ Test (Send)",
        "btn_copy": "📋 Copy HEX",
        "btn_rename": "✏️ Rename",
        "btn_delete": "🗑️ Delete Code",
        "btn_export": "📂 Export TXT/JSON",
        "col_name": "Code Name",
        "col_type": "Type",
        "col_cat": "Category",
        "col_date": "Created Date",
        "col_len": "Code Length",
        "default_cat": "General",
        "msg_err_ip": "Please enter a valid IP and MAC address!",
        "msg_connected": "✅ Successfully connected to Broadlink device!",
        "msg_conn_err": "❌ Connection error:",
        "msg_learning_ir": "🔴 Activating IR learning mode... Press button on IR remote.",
        "msg_ir_success": "✅ Successfully captured IR code for",
        "msg_ir_timeout": "⏱️ IR signal reception timed out.",
        "msg_rf_step1": "📡 STEP 1: Scanning RF frequency... HOLD button on RF remote.",
        "msg_rf_step2": "⚡ STEP 2: Frequency captured! RELEASE AND PRESS button repeatedly...",
        "msg_rf_success": "🎉 Success! Saved RF code for",
        "msg_rf_timeout": "⏱️ Failed to capture RF data packet.",
        "msg_sent": "🚀 Code sent:",
        "msg_copied": "📋 Copied HEX for",
        "msg_renamed": "✏️ Renamed:",
        "msg_deleted": "🗑️ Deleted from database:",
        "msg_exported": "📂 Exported codes count:",
        "guide_title": "Guide - How to find IP and MAC",
        "guide_content": (
            "📱 METHOD 1: BroadLink Mobile App\n"
            "--------------------------------------------------\n"
            "1. Open BroadLink app on your smartphone.\n"
            "2. Select your RM4 Pro / Mini device.\n"
            "3. Tap '...' (Settings icon at top right).\n"
            "4. Go to 'Device Info'.\n"
            "5. Copy IP and MAC address into this app.\n\n"
            "⚠️ VERY IMPORTANT:\n"
            "In the same menu, DISABLE 'Lock device' option!\n"
            "Otherwise, device blocks local computer commands.\n\n"
            "🌐 METHOD 2: Router Dashboard (DHCP)\n"
            "--------------------------------------------------\n"
            "1. Open router admin page (e.g. 192.168.1.1 or 192.168.0.1).\n"
            "2. Check 'Connected Devices' / 'DHCP Client List'.\n"
            "3. Look for MAC starting with E8:16:56, 34:EA:E7 or 78:0F:77."
        )
    }
}

# Klasa tworząca pole z eleganckim placeholderem
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="---.---.---.---", color_dim="#666666", color_active="#eeeeee", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.color_dim = color_dim
        self.color_active = color_active

        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.put_placeholder()

    def put_placeholder(self):
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.config(fg=self.color_dim)

    def _focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.color_active)

    def _focus_out(self, event):
        if not self.get().strip():
            self.put_placeholder()

    def get_val(self):
        val = self.get().strip()
        return "" if val == self.placeholder else val

    def set_val(self, val):
        self.delete(0, tk.END)
        if val and val != self.placeholder:
            self.insert(0, val)
            self.config(fg=self.color_active)
        else:
            self.put_placeholder()


class BroadlinkGUIUltraMax:
    def __init__(self, root):
        self.root = root
        self.root.title("Broadlink CyberHub Pro v5")
        self.root.geometry("1120x760")
        self.root.minsize(1020, 680)

        self.device = None
        self.is_learning = False
        self.lang = "PL"
        
        # Paleta kolorów Cyber-Dark UI
        self.colors = {
            "bg_dark": "#121212",
            "bg_card": "#1e1e1e",
            "bg_entry": "#2d2d2d",
            "accent_blue": "#00adb5",
            "accent_green": "#00e676",
            "accent_orange": "#ff9100",
            "accent_red": "#ff5252",
            "text_light": "#eeeeee",
            "text_dim": "#aaaaaa",
            "border": "#333333"
        }

        self.setup_styles()
        self.load_database()
        self.load_config()

        self.build_ui()
        self.refresh_code_tree()

    def setup_styles(self):
        self.root.configure(bg=self.colors["bg_dark"])
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Kolory dla listy rozwijanej (Combobox Listbox)
        self.root.option_add("*TCombobox*Listbox.background", "#2d2d2d")
        self.root.option_add("*TCombobox*Listbox.foreground", "#eeeeee")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#00adb5")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

        self.style.configure(".", background=self.colors["bg_dark"], foreground=self.colors["text_light"], font=("Segoe UI", 10))
        self.style.configure("Card.TFrame", background=self.colors["bg_card"], relief="flat", borderwidth=1)
        self.style.configure("CardHeader.TLabel", background=self.colors["bg_card"], foreground=self.colors["accent_blue"], font=("Segoe UI", 11, "bold"))

        self.style.configure("Treeview", 
                             background=self.colors["bg_card"], 
                             foreground=self.colors["text_light"], 
                             fieldbackground=self.colors["bg_card"], 
                             rowheight=28,
                             font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", 
                             background="#2a2a2a", 
                             foreground=self.colors["accent_blue"], 
                             font=("Segoe UI", 10, "bold"),
                             padding=5)
        self.style.map("Treeview", background=[("selected", self.colors["accent_blue"])], foreground=[("selected", "#ffffff")])

        # Naprawiony Ciemny Combobox bez białego tła
        self.style.configure("TCombobox", 
                             fieldbackground=self.colors["bg_entry"], 
                             background="#2d2d2d", 
                             foreground=self.colors["text_light"],
                             darkcolor="#1e1e1e",
                             lightcolor="#333333",
                             arrowcolor=self.colors["accent_blue"])
        self.style.map("TCombobox", fieldbackground=[("readonly", self.colors["bg_entry"])], foreground=[("readonly", self.colors["text_light"])])

        self.style.configure("TButton", background="#2d2d2d", foreground=self.colors["text_light"], borderwidth=0, padding=5, font=("Segoe UI", 9, "bold"))
        self.style.map("TButton", background=[("active", self.colors["accent_blue"])], foreground=[("active", "#ffffff")])

        self.style.configure("Accent.TButton", background=self.colors["accent_blue"], foreground="#121212")
        self.style.map("Accent.TButton", background=[("active", "#00d8e2")])

        self.style.configure("Success.TButton", background=self.colors["accent_green"], foreground="#121212")
        self.style.map("Success.TButton", background=[("active", "#33ff99")])

        self.style.configure("Warn.TButton", background=self.colors["accent_orange"], foreground="#121212")
        self.style.map("Warn.TButton", background=[("active", "#ffa733")])

        self.style.configure("Danger.TButton", background=self.colors["accent_red"], foreground="#ffffff")
        self.style.map("Danger.TButton", background=[("active", "#ff7373")])

    def load_config(self):
        self.config = {"ip": "", "mac": "", "type": "0x5f36", "lang": "PL"}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.config["ip"] = data.get("ip", "")
                    self.config["mac"] = data.get("mac", "")
                    self.config["type"] = data.get("type", "0x5f36")
                    self.lang = data.get("lang", "PL")
            except Exception as e:
                self.log(f"⚠️ Błąd wczytywania configu: {e}")

    def save_config(self):
        self.config["ip"] = self.ip_entry.get_val()
        self.config["mac"] = self.mac_entry.get_val().replace(":", "").replace("-", "").upper()
        self.config["type"] = self.type_entry.get().strip()
        self.config["lang"] = self.lang
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.log(f"⚠️ Błąd zapisu configu: {e}")

    def load_database(self):
        self.codes_db = {}
        if os.path.exists(CODES_FILE):
            try:
                with open(CODES_FILE, "r", encoding="utf-8") as f:
                    self.codes_db = json.load(f)
            except Exception:
                self.codes_db = {}

    def save_database(self):
        try:
            with open(CODES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.codes_db, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.log(f"⚠️ Błąd zapisu bazy danych: {e}")

    def build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # 1. HEADER & CONNECTION CARD
        conn_card = ttk.Frame(self.root, style="Card.TFrame", padding=12)
        conn_card.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        header_frame = ttk.Frame(conn_card, style="Card.TFrame")
        header_frame.grid(row=0, column=0, columnspan=8, sticky="ew", pady=(0, 8))
        
        self.lbl_head_conn = ttk.Label(header_frame, text=I18N[self.lang]["header_conn"], style="CardHeader.TLabel")
        self.lbl_head_conn.pack(side="left")

        # Czyste przełączniki języka bez rozbijania na PL PL / GB EN
        lang_box = ttk.Frame(header_frame, style="Card.TFrame")
        lang_box.pack(side="right")
        
        self.btn_lang_pl = tk.Button(lang_box, text="[ PL ]", bg="#00adb5" if self.lang == "PL" else "#2d2d2d", fg="white", activebackground="#00adb5", relief="flat", font=("Segoe UI", 9, "bold"), command=lambda: self.switch_language("PL"))
        self.btn_lang_pl.pack(side="left", padx=2)
        self.btn_lang_en = tk.Button(lang_box, text="[ EN ]", bg="#00adb5" if self.lang == "EN" else "#2d2d2d", fg="white", activebackground="#00adb5", relief="flat", font=("Segoe UI", 9, "bold"), command=lambda: self.switch_language("EN"))
        self.btn_lang_en.pack(side="left", padx=2)

        self.lbl_ip = ttk.Label(conn_card, text=I18N[self.lang]["label_ip"])
        self.lbl_ip.grid(row=1, column=0, sticky="w", padx=(0, 4))
        
        # Czysty Placeholder IP
        self.ip_entry = PlaceholderEntry(conn_card, placeholder="---.---.---.---", width=14, bg=self.colors["bg_entry"], insertbackground="white", relief="flat")
        self.ip_entry.grid(row=1, column=1, padx=(0, 8))
        if self.config.get("ip"):
            self.ip_entry.set_val(self.config.get("ip"))

        self.lbl_mac = ttk.Label(conn_card, text=I18N[self.lang]["label_mac"])
        self.lbl_mac.grid(row=1, column=2, sticky="w", padx=(0, 4))
        
        # Czysty Placeholder MAC
        self.mac_entry = PlaceholderEntry(conn_card, placeholder="XX:XX:XX:XX:XX:XX", width=17, bg=self.colors["bg_entry"], insertbackground="white", relief="flat")
        self.mac_entry.grid(row=1, column=3, padx=(0, 8))
        if self.config.get("mac"):
            self.mac_entry.set_val(self.config.get("mac"))

        self.lbl_model = ttk.Label(conn_card, text=I18N[self.lang]["label_model"])
        self.lbl_model.grid(row=1, column=4, sticky="w", padx=(0, 4))
        
        self.model_combo = ttk.Combobox(conn_card, values=list(BROADLINK_MODELS.keys()), state="readonly", width=25)
        self.model_combo.grid(row=1, column=5, padx=(0, 8))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        self.type_entry = tk.Entry(conn_card, width=7, bg=self.colors["bg_entry"], fg=self.colors["text_light"], insertbackground="white", relief="flat")
        self.type_entry.grid(row=1, column=6, padx=(0, 8))
        
        saved_type = self.config.get("type", "0x5f36")
        self.type_entry.insert(0, saved_type)
        self.set_combo_from_type(saved_type)

        btn_box = ttk.Frame(conn_card, style="Card.TFrame")
        btn_box.grid(row=1, column=7, sticky="e")

        self.btn_guide = ttk.Button(btn_box, text=I18N[self.lang]["btn_guide"], command=self.show_ip_help)
        self.btn_guide.pack(side="left", padx=2)
        self.btn_arp = ttk.Button(btn_box, text=I18N[self.lang]["btn_arp"], command=self.async_action(self.scan_arp_cache))
        self.btn_arp.pack(side="left", padx=2)
        self.btn_connect = ttk.Button(btn_box, text=I18N[self.lang]["btn_connect"], style="Accent.TButton", command=self.async_action(self.connect_device))
        self.btn_connect.pack(side="left", padx=2)

        self.status_canvas = tk.Canvas(conn_card, width=16, height=16, bg=self.colors["bg_card"], highlightthickness=0)
        self.status_canvas.grid(row=1, column=8, padx=(8, 0))
        self.status_light = self.status_canvas.create_oval(2, 2, 14, 14, fill=self.colors["accent_red"])

        # 2. ACTIONS CARD
        action_card = ttk.Frame(self.root, style="Card.TFrame", padding=12)
        action_card.grid(row=1, column=0, sticky="ew", padx=12, pady=6)

        self.lbl_head_action = ttk.Label(action_card, text=I18N[self.lang]["header_action"], style="CardHeader.TLabel")
        self.lbl_head_action.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        self.lbl_name = ttk.Label(action_card, text=I18N[self.lang]["label_name"])
        self.lbl_name.grid(row=1, column=0, sticky="w")
        self.name_entry = tk.Entry(action_card, width=20, bg=self.colors["bg_entry"], fg=self.colors["text_light"], insertbackground="white", relief="flat")
        self.name_entry.grid(row=1, column=1, padx=(4, 10))

        self.lbl_cat = ttk.Label(action_card, text=I18N[self.lang]["label_cat"])
        self.lbl_cat.grid(row=1, column=2, sticky="w")
        self.cat_entry = tk.Entry(action_card, width=15, bg=self.colors["bg_entry"], fg=self.colors["text_light"], insertbackground="white", relief="flat")
        self.cat_entry.grid(row=1, column=3, padx=(4, 10))
        self.cat_entry.insert(0, I18N[self.lang]["default_cat"])

        self.btn_learn_ir = ttk.Button(action_card, text=I18N[self.lang]["btn_learn_ir"], style="Warn.TButton", command=self.async_action(self.learn_ir_code))
        self.btn_learn_ir.grid(row=1, column=4, padx=4)
        self.btn_learn_rf = ttk.Button(action_card, text=I18N[self.lang]["btn_learn_rf"], style="Warn.TButton", command=self.async_action(self.learn_rf_code))
        self.btn_learn_rf.grid(row=1, column=5, padx=4)
        self.btn_send_input = ttk.Button(action_card, text=I18N[self.lang]["btn_send_input"], style="Success.TButton", command=self.async_action(self.send_custom_code))
        self.btn_send_input.grid(row=1, column=6, padx=4)

        # 3. DATABASE TREEVIEW CARD
        db_card = ttk.Frame(self.root, style="Card.TFrame", padding=12)
        db_card.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        db_card.columnconfigure(0, weight=1)
        db_card.rowconfigure(1, weight=1)

        header_db = ttk.Frame(db_card, style="Card.TFrame")
        header_db.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.lbl_head_db = ttk.Label(header_db, text=I18N[self.lang]["header_db"], style="CardHeader.TLabel")
        self.lbl_head_db.pack(side="left")

        self.lbl_search = ttk.Label(header_db, text=I18N[self.lang]["label_search"])
        self.lbl_search.pack(side="right", padx=(10, 4))
        self.search_entry = tk.Entry(header_db, width=20, bg=self.colors["bg_entry"], fg=self.colors["text_light"], insertbackground="white", relief="flat")
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_code_tree())

        columns = ("name", "type", "category", "date", "length")
        self.code_tree = ttk.Treeview(db_card, columns=columns, show="headings", selectmode="browse")
        
        self.update_tree_headings()

        self.code_tree.column("name", width=200)
        self.code_tree.column("type", width=80, anchor="center")
        self.code_tree.column("category", width=140)
        self.code_tree.column("date", width=150, anchor="center")
        self.code_tree.column("length", width=100, anchor="center")

        self.code_tree.grid(row=1, column=0, sticky="nsew")
        self.code_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.code_tree.bind("<Double-1>", lambda e: self.async_action(self.test_selected_code)())

        scrollbar = ttk.Scrollbar(db_card, orient="vertical", command=self.code_tree.yview)
        self.code_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        tbl_btns = ttk.Frame(db_card, style="Card.TFrame")
        tbl_btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        self.btn_test = ttk.Button(tbl_btns, text=I18N[self.lang]["btn_test"], style="Success.TButton", command=self.async_action(self.test_selected_code))
        self.btn_test.pack(side="left", padx=2)
        self.btn_copy = ttk.Button(tbl_btns, text=I18N[self.lang]["btn_copy"], style="Accent.TButton", command=self.copy_selected_code)
        self.btn_copy.pack(side="left", padx=2)
        self.btn_rename = ttk.Button(tbl_btns, text=I18N[self.lang]["btn_rename"], command=self.rename_selected_code)
        self.btn_rename.pack(side="left", padx=2)
        self.btn_delete = ttk.Button(tbl_btns, text=I18N[self.lang]["btn_delete"], style="Danger.TButton", command=self.delete_selected_code)
        self.btn_delete.pack(side="left", padx=2)
        self.btn_export = ttk.Button(tbl_btns, text=I18N[self.lang]["btn_export"], command=self.export_database)
        self.btn_export.pack(side="right", padx=2)

        # 4. LOGS CARD
        log_card = ttk.Frame(self.root, style="Card.TFrame", padding=12)
        log_card.grid(row=3, column=0, sticky="ew", padx=12, pady=(6, 12))
        log_card.columnconfigure(0, weight=1)

        self.lbl_head_logs = ttk.Label(log_card, text=I18N[self.lang]["header_logs"], style="CardHeader.TLabel")
        self.lbl_head_logs.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.log_box = tk.Text(log_card, height=6, bg="#181818", fg=self.colors["accent_green"], font=("Consolas", 9), relief="flat", insertbackground="white")
        self.log_box.grid(row=1, column=0, sticky="ew")

    def switch_language(self, new_lang):
        self.lang = new_lang
        self.save_config()

        # Przełączanie aktywnego koloru przycisku językowego
        self.btn_lang_pl.config(bg="#00adb5" if self.lang == "PL" else "#2d2d2d")
        self.btn_lang_en.config(bg="#00adb5" if self.lang == "EN" else "#2d2d2d")

        self.lbl_head_conn.config(text=I18N[self.lang]["header_conn"])
        self.lbl_head_action.config(text=I18N[self.lang]["header_action"])
        self.lbl_head_db.config(text=I18N[self.lang]["header_db"])
        self.lbl_head_logs.config(text=I18N[self.lang]["header_logs"])
        
        self.lbl_ip.config(text=I18N[self.lang]["label_ip"])
        self.lbl_mac.config(text=I18N[self.lang]["label_mac"])
        self.lbl_model.config(text=I18N[self.lang]["label_model"])
        self.lbl_name.config(text=I18N[self.lang]["label_name"])
        self.lbl_cat.config(text=I18N[self.lang]["label_cat"])
        self.lbl_search.config(text=I18N[self.lang]["label_search"])

        self.btn_guide.config(text=I18N[self.lang]["btn_guide"])
        self.btn_arp.config(text=I18N[self.lang]["btn_arp"])
        self.btn_connect.config(text=I18N[self.lang]["btn_connect"])
        self.btn_learn_ir.config(text=I18N[self.lang]["btn_learn_ir"])
        self.btn_learn_rf.config(text=I18N[self.lang]["btn_learn_rf"])
        self.btn_send_input.config(text=I18N[self.lang]["btn_send_input"])
        self.btn_test.config(text=I18N[self.lang]["btn_test"])
        self.btn_copy.config(text=I18N[self.lang]["btn_copy"])
        self.btn_rename.config(text=I18N[self.lang]["btn_rename"])
        self.btn_delete.config(text=I18N[self.lang]["btn_delete"])
        self.btn_export.config(text=I18N[self.lang]["btn_export"])

        self.update_tree_headings()
        self.log(f"🌐 Switched language to {self.lang}")

    def update_tree_headings(self):
        self.code_tree.heading("name", text=I18N[self.lang]["col_name"])
        self.code_tree.heading("type", text=I18N[self.lang]["col_type"])
        self.code_tree.heading("category", text=I18N[self.lang]["col_cat"])
        self.code_tree.heading("date", text=I18N[self.lang]["col_date"])
        self.code_tree.heading("length", text=I18N[self.lang]["col_len"])

    def on_model_change(self, event):
        selected_label = self.model_combo.get()
        hex_code = BROADLINK_MODELS.get(selected_label, "0x5f36")

        if hex_code == "CUSTOM":
            self.type_entry.config(state="normal")
            self.type_entry.delete(0, tk.END)
            self.type_entry.focus()
        else:
            self.type_entry.config(state="normal")
            self.type_entry.delete(0, tk.END)
            self.type_entry.insert(0, hex_code)

    def set_combo_from_type(self, type_hex):
        for label, code in BROADLINK_MODELS.items():
            if code.lower() == type_hex.lower():
                self.model_combo.set(label)
                return
        self.model_combo.set("Własny / Custom HEX")

    def async_action(self, func):
        def wrapper(*args, **kwargs):
            threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
        return wrapper

    def log(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{now}] {text}\n")
        self.log_box.see(tk.END)

    def set_status(self, connected):
        color = self.colors["accent_green"] if connected else self.colors["accent_red"]
        self.status_canvas.itemconfig(self.status_light, fill=color)

    # DIAGNOSTIC TOOLS & HELP
    def show_ip_help(self):
        messagebox.showinfo(I18N[self.lang]["guide_title"], I18N[self.lang]["guide_content"])

    def scan_arp_cache(self):
        self.log("🔍 Skanowanie systemowej tablicy ARP (ARP Table scan)...")
        broadlink_mac_prefixes = ("e8-16-56", "e8:16:56", "34-ea-e7", "34:ea:e7", "78-0f-77", "78:0f:77", "b4-43-0d", "b4:43:0d", "ec-0b-ae", "ec:0b:ae")
        found = False

        try:
            output = subprocess.check_output("arp -a", shell=True, text=True)
            lines = output.splitlines()

            for line in lines:
                line_lower = line.lower()
                if any(prefix in line_lower for prefix in broadlink_mac_prefixes):
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]+)', line)
                    if match:
                        ip_found = match.group(1)
                        mac_found = match.group(2).replace("-", "").replace(":", "").upper()
                        self.log(f"🎉 ZNALEZIONO DEVICE! IP: {ip_found} | MAC: {mac_found}")
                        
                        self.ip_entry.set_val(ip_found)
                        self.mac_entry.set_val(mac_found)
                        found = True

            if not found:
                self.log("ℹ️ Przeskanowano ARP. Brak nowych adresów / ARP scan complete.")
        except Exception as e:
            self.log(f"❌ Błąd / Error ARP: {e}")

    # BROADLINK CORE FUNCTIONS
    def get_device_info(self):
        ip = self.ip_entry.get_val()
        mac_hex = self.mac_entry.get_val().replace(":", "").replace("-", "")
        dev_type_str = self.type_entry.get().strip()

        if not ip or not mac_hex:
            messagebox.showwarning("Warning", I18N[self.lang]["msg_err_ip"])
            return None, None, None

        try:
            dev_type = int(dev_type_str, 16) if dev_type_str.startswith("0x") else int(dev_type_str)
            mac_bytes = bytes.fromhex(mac_hex)
            return ip, mac_bytes, dev_type
        except Exception as e:
            messagebox.showerror("Error", f"Invalid parameters: {e}")
            return None, None, None

    def connect_device(self):
        ip, mac_bytes, dev_type = self.get_device_info()
        if not ip:
            return None

        try:
            self.log(f"Connecting to {ip} [MAC: {mac_bytes.hex().upper()}]...")
            dev = broadlink.gendevice(dev_type, (ip, 80), mac_bytes)
            dev.auth()
            self.device = dev
            self.save_config()
            self.set_status(True)
            self.log(I18N[self.lang]["msg_connected"])
            return dev
        except Exception as e:
            self.set_status(False)
            self.log(f"{I18N[self.lang]['msg_conn_err']} {e}")
            messagebox.showerror("Error", f"{I18N[self.lang]['msg_conn_err']}\n{e}")
            return None

    # LEARNING IR / RF
    def learn_ir_code(self):
        name = self.name_entry.get().strip()
        category = self.cat_entry.get().strip() or I18N[self.lang]["default_cat"]

        if not name:
            messagebox.showwarning("Warning", "Enter name for new code!")
            return

        dev = self.device or self.connect_device()
        if not dev:
            return

        try:
            self.log(I18N[self.lang]["msg_learning_ir"])
            dev.enter_learning()

            start_time = time.time()
            data = None
            timeout = 12

            while time.time() - start_time < timeout:
                time.sleep(0.8)
                try:
                    data = dev.check_data()
                    if data:
                        break
                except broadlink.exceptions.StorageError:
                    continue

            if data:
                hex_code = data.hex()
                self.save_code_to_db(name, hex_code, "IR", category)
                self.log(f"{I18N[self.lang]['msg_ir_success']} '{name}'!")
                messagebox.showinfo("Success", f"{I18N[self.lang]['msg_ir_success']} '{name}'!")
            else:
                self.log(I18N[self.lang]["msg_ir_timeout"])
                messagebox.showwarning("Timeout", I18N[self.lang]["msg_ir_timeout"])

        except Exception as e:
            self.log(f"❌ Error IR: {e}")

    def learn_rf_code(self):
        name = self.name_entry.get().strip()
        category = self.cat_entry.get().strip() or I18N[self.lang]["default_cat"]

        if not name:
            messagebox.showwarning("Warning", "Enter name for new code!")
            return

        dev = self.device or self.connect_device()
        if not dev:
            return

        try:
            self.log(I18N[self.lang]["msg_rf_step1"])
            dev.sweep_frequency()

            start_time = time.time()
            found_freq = False
            while time.time() - start_time < 15:
                time.sleep(1)
                if dev.check_frequency():
                    found_freq = True
                    break

            if not found_freq:
                self.log("❌ RF frequency not found.")
                messagebox.showwarning("RF Error", "RF frequency not detected.")
                dev.cancel_sweep_frequency()
                return

            self.log(I18N[self.lang]["msg_rf_step2"])
            time.sleep(1)
            dev.find_rf_packet()

            start_time = time.time()
            data = None
            while time.time() - start_time < 12:
                time.sleep(0.8)
                try:
                    data = dev.check_data()
                    if data:
                        break
                except broadlink.exceptions.StorageError:
                    continue

            if data:
                hex_code = data.hex()
                self.save_code_to_db(name, hex_code, "RF", category)
                self.log(f"{I18N[self.lang]['msg_rf_success']} '{name}'!")
                messagebox.showinfo("Success", f"{I18N[self.lang]['msg_rf_success']} '{name}'!")
            else:
                self.log(I18N[self.lang]["msg_rf_timeout"])
                messagebox.showwarning("Timeout", I18N[self.lang]["msg_rf_timeout"])

        except Exception as e:
            self.log(f"❌ Error RF: {e}")

    def save_code_to_db(self, name, hex_code, code_type, category):
        self.codes_db[str(name)] = {
            "hex": hex_code,
            "type": code_type,
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "length": len(hex_code)
        }
        self.save_database()
        self.refresh_code_tree()

    def send_custom_code(self):
        name = str(self.name_entry.get().strip())
        if name in self.codes_db:
            hex_code = self.codes_db[name]["hex"]
            self.send_hex(hex_code, name)
        else:
            messagebox.showwarning("Warning", f"Code '{name}' not in DB.")

    def test_selected_code(self):
        selected = self.code_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select code from table.")
            return

        item_vals = self.code_tree.item(selected[0])["values"]
        name = str(item_vals[0])
        if name in self.codes_db:
            hex_code = self.codes_db[name]["hex"]
            self.send_hex(hex_code, name)

    def send_hex(self, hex_code, name="Kod"):
        dev = self.device or self.connect_device()
        if not dev:
            return

        try:
            dev.send_data(bytes.fromhex(hex_code))
            self.log(f"{I18N[self.lang]['msg_sent']} '{name}'")
        except Exception as e:
            self.log(f"❌ Send Error: {e}")

    # TABLE DATABASE MANAGEMENT
    def refresh_code_tree(self):
        self.code_tree.delete(*self.code_tree.get_children())
        query = self.search_entry.get().lower().strip()

        for name, info in self.codes_db.items():
            name_str = str(name)
            cat = info.get("category", I18N[self.lang]["default_cat"])
            c_type = info.get("type", "IR")
            date = info.get("date", "-")
            length = f"{info.get('length', len(info.get('hex','')))}B"

            if query and query not in name_str.lower() and query not in cat.lower() and query not in c_type.lower():
                continue

            self.code_tree.insert("", tk.END, values=(name_str, c_type, cat, date, length))

    def on_tree_select(self, event):
        selected = self.code_tree.selection()
        if selected:
            item_vals = self.code_tree.item(selected[0])["values"]
            name = str(item_vals[0])
            cat = str(item_vals[2])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            self.cat_entry.delete(0, tk.END)
            self.cat_entry.insert(0, cat)

    def copy_selected_code(self):
        selected = self.code_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select code to copy.")
            return

        name = str(self.code_tree.item(selected[0])["values"][0])
        if name in self.codes_db:
            hex_code = self.codes_db[name]["hex"]
            self.root.clipboard_clear()
            self.root.clipboard_append(hex_code)
            self.root.update()
            self.log(f"{I18N[self.lang]['msg_copied']} '{name}'")
            messagebox.showinfo("Clipboard", f"{I18N[self.lang]['msg_copied']} '{name}'!")

    def rename_selected_code(self):
        selected = self.code_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select code to rename.")
            return

        old_name = str(self.code_tree.item(selected[0])["values"][0])
        new_name = simpledialog.askstring("Rename", f"New name for '{old_name}':")

        if new_name:
            new_name = str(new_name).strip()
            if new_name and new_name != old_name:
                if old_name in self.codes_db:
                    self.codes_db[new_name] = self.codes_db.pop(old_name)
                    self.save_database()
                    self.refresh_code_tree()
                    self.log(f"{I18N[self.lang]['msg_renamed']} {old_name} -> {new_name}")

    def delete_selected_code(self):
        selected = self.code_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select code to delete.")
            return

        name = str(self.code_tree.item(selected[0])["values"][0])
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            if name in self.codes_db:
                del self.codes_db[name]
                self.save_database()
                self.refresh_code_tree()
                self.log(f"{I18N[self.lang]['msg_deleted']} {name}")

    def export_database(self):
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)

        for name, info in self.codes_db.items():
            file_path = os.path.join(EXPORT_DIR, f"{name}.txt")
            with open(file_path, "w") as f:
                f.write(info["hex"])

        self.log(f"{I18N[self.lang]['msg_exported']} {len(self.codes_db)}")
        messagebox.showinfo("Export", f"{I18N[self.lang]['msg_exported']} {len(self.codes_db)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BroadlinkGUIUltraMax(root)
    root.mainloop()