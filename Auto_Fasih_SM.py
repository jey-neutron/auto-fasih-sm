import subprocess
import socket
import time
import tkinter as tk
from tkinter import ttk
import threading
import sys
import os
import re
from PIL import Image, ImageTk

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except: 
    pass

def initlib(callback):
    # var global to store library var
    global datetime; global pd; global scrolledtext
    global np
    global playwright_instance; global sync_playwright; global browser; global page
    global icon; global PlaywrightError
    # global TimeoutException
    # global webdriver; global Keys; 
    # global Select; global EC
    # global WebDriverWait; global By; 

    #  Library
    # from selenium import webdriver
    # from selenium.webdriver.common.keys import Keys
    # from selenium.common.exceptions import TimeoutException
    # from selenium.webdriver.support.ui import Select
    # from selenium.webdriver.support import expected_conditions as EC
    # from selenium.webdriver.support.ui import WebDriverWait
    # from selenium.webdriver.common.by import By
    from playwright.sync_api import sync_playwright
    from playwright._impl._errors import Error as PlaywrightError
    from tkinter import scrolledtext
    from datetime import datetime
    import pandas as pd
    import numpy as np
    icon = AutoApp.getassets('ikonku.ico', True)

    time.sleep(1)
    callback()

#####
# --- Bagian A: Membaca dan Menjalankan Skrip Relatif ---
def load_setting_file(instance, filename="get_data.py", load=True):
    """Membaca dan menjalankan kode dari file relatif."""
    # Pastikan file ada di direktori yang sama dengan .exe
    
    # 1. Tentukan path file
    if getattr(sys, 'frozen', False):
        # Jika berjalan sebagai .exe (PyInstaller)
        application_path = os.path.dirname(sys.executable)
    else:
        # Jika berjalan sebagai skrip Python biasa
        application_path = os.path.dirname(os.path.abspath(__file__))
        
    file_path = os.path.join(application_path, filename)
    
    # 1. Cek apakah file ada di path utama, here
    if not os.path.exists(file_path):
        # 2. Jika tidak ada, cek alternatif di dalam folder 'dist'
        dist_path = os.path.join(application_path, "dist", filename)

        if os.path.exists(dist_path):
            file_path = dist_path  # Alihkan ke path dist jika file ditemukan
        else:
            # 3. Jika di kedua tempat tidak ada, baru cetak error
            if load:
                instance.log_message(message=f"ERROR: File konfigurasi tidak ditemukan di path utama maupun folder dist: {filename}", tag="red_tag")
            return None
    
    if load:
        # 3. Baca dan jalankan
        try:
            # Kita buat namespace khusus untuk menampung fungsi dari file yang di-load
            namespace = {} 
            with open(file_path, 'r') as f:
                code = f.read()
                # Menjalankan kode. Fungsi-fungsi akan tersedia di 'namespace'
                exec(code, namespace)
                
            return namespace
            
        except Exception as e:
            instance.log_message(message=f"ERROR: Gagal memuat file konfigurasi: {e}", tag="red_tag")
            return None
    return True

def get_assets_path():
    """Fungsi otomatis mencari folder 'assets' di direktori skrip atau induknya."""
    # Lokasi file skrip python saat ini
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 1. Cek di direktori saat ini
    path_same_dir = os.path.join(current_dir, "assets")
    if os.path.exists(path_same_dir) and os.path.isdir(path_same_dir):
        return path_same_dir

    # 2. Cek di direktori induk (Parent Directory / naik 1 tingkat)
    parent_dir = os.path.dirname(current_dir)
    path_parent_dir = os.path.join(parent_dir, "assets")
    if os.path.exists(path_parent_dir) and os.path.isdir(path_parent_dir):
        return path_parent_dir

    # Jika tidak ditemukan di kedua tempat
    raise FileNotFoundError("Folder 'assets' tidak ditemukan di direktori skrip maupun induk!")


#####


# Main app
class AutoApp:
    def __init__(self, master):
        # Palette Warna Modern Premium
        self.BG_MAIN = "#121214"       # Dark Background Utama
        self.BG_CARD = "#1A1A22"       # Background Kontainer / Card
        self.BG_INPUT = "#22222E"      # Background Field Input
        self.FG_MAIN = "#FFFFFF"       # Teks Utama
        self.FG_MUTED = "#8E8E9F"      # Teks Redup / Label
        self.ACCENT_BLUE_DARK = "#003380"   # Tombol Primer / Browser
        self.ACCENT_TEAL_DARK = "#00402E"   # Tombol Run / Sukses
        self.ACCENT_RED_DARK = "#660018"    # Tombol Berhenti / Error
        self.ACCENT_BLUE = "#3A86FF"   # Tombol Primer / Browser
        self.ACCENT_TEAL = "#00A378"   # Tombol Run / Sukses
        self.ACCENT_RED = "#FF003C"    # Tombol Berhenti / Error
        self.ACCENT_ORANGE = "#FF9F1C" # Tombol Pendukung
        self.BORDER_COLOR = "#2D2D3D"  # Warna Border

        
        # konfigurasi import fungsi dari get_data.py
        # 1. Load fungsi dari file eksternal
        external_funcs = load_setting_file(self)
        if external_funcs is None:
            time.sleep(10)
            master.destroy()
            return
        # user n sso get
        usersso, passso, approv, msgsso, helper = self.load_credentials()     

        # 2. Ambil fungsi yang dibutuhkan
        global mainfunc
        global get_list_data
        mainfunc = external_funcs.get('mainfunc')
        get_list_data = external_funcs.get('get_list_data')
        appver = external_funcs.get('ver')
        
        # konfigurasi variabel
        self.playwright_instance = None
        self.page = None
        self.isdone = None
        self.vars = None #var kosong buat next if needed
        self.var_input = None
        self.stop_event = threading.Event() # Event untuk menghentikan thread
        self.thread = None

        # Konfigurasi jendela utama
        self.master = master
        #master.iconbitmap("ikonku.ico")
        master.title(f"Aplikasi Auto-Fasih-SM {appver(self)}")
        master.iconbitmap(icon)
        master.geometry("480x800") # Ukuran awal yang sedikit lebih proporsional
        master.attributes("-topmost", True) # Selalu di atas
        master.resizable(True, True) # Memungkinkan resize
        master.configure(bg=self.BG_MAIN)

        # Menangani tombol close (X) pada jendela Tkinter agar bersih
        #master.protocol("WM_DELETE_WINDOW", self.close_browser)

        # Menambahkan frame utama untuk padding
        self.main_frame = tk.Frame(master, padx=15, pady=15, bg=self.BG_MAIN)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Variabel STATUS ---
        self.status_var = tk.StringVar(value="STATUS: Belum dikenapa-napain")
        self.status_label = tk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            fg="#FFFFFF", 
            bg=self.ACCENT_BLUE_DARK, 
            font=('Segoe UI', 10, 'bold'), 
            anchor='w',
            padx=10,
            pady=6,
            bd=0
        )
        self.status_label.pack(fill=tk.X, pady=(0, 15))      

        # --- Input Fields (Field 1: Username) ---
        self.create_input_field("Username SSO:", 'jey.neutron', "username_entry", self.main_frame, value=usersso)
        # --- Input Fields (Field 2: Password) ---
        self.create_input_field("Password SSO:", 'password', "password_entry", self.main_frame, show='*', value=passso)
        
        # --- Input Fields (Field 3: Link) ---
        self.create_input_field("Link target:", "https://fasih-sm.bps.go.id/", "link_entry", self.main_frame)
        
        # --- Tombol Baris 1: Buka Aplikasi & Buka Link ---
        self.btn_frame_1 = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        self.btn_frame_1.pack(fill=tk.X, pady=(7, 5))

        self.btn_open_app = tk.Button(
            self.btn_frame_1, 
            text="Start Browser", 
            command=self.open_browser, 
            bg=self.ACCENT_BLUE, 
            fg=self.FG_MAIN, 
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            activebackground="#266EF1",
            activeforeground=self.FG_MAIN,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_open_app.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_open_link = tk.Button(
            self.btn_frame_1, 
            text="Goto Link", 
            command=self.open_link_in_browser, 
            bg=self.ACCENT_BLUE, 
            fg=self.FG_MAIN, 
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            activebackground="#266EF1",
            activeforeground=self.FG_MAIN,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_open_link.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        self.btn_close_app = tk.Button(
            self.btn_frame_1, 
            text="Close Browser", 
            command=self.close_browser, 
            bg="#2a2a38", 
            fg=self.FG_MAIN, 
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            activebackground="#3d3d52",
            activeforeground=self.FG_MAIN,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_close_app.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # --- Tombol Baris 2: Fungsi 1 & Fungsi 2 ---
        # --- SECTION 1
        self.toggle_btn_getlist = tk.Button(
            self.main_frame,
            text="▶ Get List Data", # Default icon tertutup
            font=('Segoe UI', 9, 'bold'),
            bg=self.BG_CARD,
            fg=self.FG_MAIN,
            bd=0,
            anchor="w", # Teks rata kiri
            command= lambda: self.toggle_section(self.func1_frame, self.toggle_btn_getlist, self.func2_frame, self.toggle_btn) # Hubungkan ke fungsi toggle
        )
        self.toggle_btn_getlist.pack(fill=tk.X, pady=(10, 0))

        #self.func1_frame = tk.Frame(self.main_frame, bg=self.BG_CARD)
        self.func1_frame = tk.LabelFrame(
            self.main_frame, 
            padx=10, 
            pady=10, 
            bg=self.BG_CARD,
            fg=self.FG_MAIN,
            font=('Segoe UI', 9, 'bold')
        )
        # self.func1_frame.pack(fill=tk.X, pady=(10, 3))

        self.btn_frame_2 = tk.Frame(self.func1_frame, bg=self.BG_CARD)
        self.btn_frame_2.pack(fill=tk.X, pady=7)

        # Variabel kontrol untuk menyimpan nilai radiobutton yang dipilih
        self.vwrite = tk.IntVar(value=1)
        # Label untuk menampilkan hasil pilihan
        self.label_hasil = tk.Label(self.btn_frame_2, text="Write data.csv?", bg=self.BG_CARD, fg=self.FG_MAIN, font=('Segoe UI', 9, 'bold'))
        self.label_hasil.pack(pady=5, side=tk.LEFT)
        # radio
        self.rw1= tk.Radiobutton(
            self.btn_frame_2, 
            text='Rewrite', 
            variable=self.vwrite, 
            value=1, 
            indicatoron=0, 
            command=self.update_label_vwrite,
            bg=self.BG_CARD,
            #fg=self.FG_MUTED,
            fg='#c7c7c7',
            selectcolor=self.ACCENT_ORANGE,
            activebackground=self.ACCENT_ORANGE,
            activeforeground=self.BG_CARD,
            relief=tk.FLAT,
            font=('Segoe UI', 8, 'bold'),
            padx=6,
            pady=3,
            cursor="hand2"
        )
        self.rw1.pack(side=tk.LEFT, padx=(5, 2))
        self.rw2= tk.Radiobutton(
            self.btn_frame_2, 
            text='Append', 
            variable=self.vwrite, 
            value=0, 
            indicatoron=0, 
            command=self.update_label_vwrite,
            bg=self.BG_INPUT,
            #fg=self.FG_MUTED,
            fg='#c7c7c7',
            selectcolor=self.ACCENT_ORANGE,
            activebackground=self.ACCENT_ORANGE,
            activeforeground=self.BG_CARD,
            relief=tk.FLAT,
            font=('Segoe UI', 8, 'bold'),
            padx=6,
            pady=3,
            cursor="hand2"
        )
        self.rw2.pack(side=tk.LEFT, padx=2)

        # main btn func 1
        self.btn_func_1 = tk.Button(
            self.btn_frame_2, 
            text="Get List Data", 
            command=self.run_function_1, 
            bg=self.ACCENT_ORANGE, 
            fg=self.FG_MAIN,
            font=('Segoe UI', 9, 'bold'), 
            relief=tk.FLAT,
            activebackground="#E08512",
            activeforeground=self.FG_MAIN,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_func_1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # --- SECTION : Input Fields Khusus Fungsi 2 (LabelFrame) ---
        self.toggle_btn = tk.Button(
            self.main_frame,
            text="▶ Run Main Function", # Default icon tertutup
            font=('Segoe UI', 9, 'bold'),
            bg=self.BG_CARD,
            fg=self.FG_MAIN,
            bd=0,
            anchor="w", # Teks rata kiri
            command= lambda: self.toggle_section(self.func2_frame, self.toggle_btn, self.func1_frame, self.toggle_btn_getlist) # Hubungkan ke fungsi toggle
        )
        self.toggle_btn.pack(fill=tk.X, pady=(10, 0))

        self.func2_frame = tk.LabelFrame(
            self.main_frame, 
            #text="Parameter Fungsi 'Run Function'", 
            padx=10, 
            pady=10, 
            # bd=1, 
            # relief=tk.SOLID,
            bg=self.BG_CARD,
            fg=self.FG_MAIN,
            font=('Segoe UI', 9, 'bold')
        )
        # self.func2_frame.pack(fill=tk.X, pady=(10, 3))

        # Menggunakan func2_frame sebagai parent untuk input ini
        self.create_input_field("Baris Mulai:", "Cth: 0 (untuk mulai dari awal)", "start_row_entry", self.func2_frame)
        self.create_input_field("Nama File:", "Nama_File.csv", "filename_entry", self.func2_frame, value='data.csv')
        self.create_input_field("Input Tambahan:", "Input opsional... (cth: help)", "extra_input_entry", self.func2_frame, value=helper)
        self.create_input_field("Variabel Extra:", "Variabel opsional tambahan...", "var_input_entry", self.func2_frame)
        
        # Variabel kontrol untuk menyimpan nilai radiobutton yang dipilih
        self.val_approv = tk.IntVar(value=1)
        
        # Sub-container frame for inline radios to look cleaner
        self.radio_container = tk.Frame(self.func2_frame, bg=self.BG_CARD)
        self.radio_container.pack(fill=tk.X, pady=(8, 0))

        # Label untuk menampilkan hasil pilihan
        self.label_hasil = tk.Label(self.radio_container, text="Sekalian approve Fasih?", bg=self.BG_CARD, fg=self.FG_MAIN, font=('Segoe UI', 8, 'bold'))
        self.label_hasil.pack(pady=5, side=tk.LEFT)
        # radio
        self.rb1= tk.Radiobutton(
            self.radio_container, 
            text='True', 
            variable=self.val_approv, 
            value=1, 
            indicatoron=0, 
            command=self.update_label,
            bg=self.BG_INPUT,
            #fg=self.FG_MUTED,
            fg='#c7c7c7',
            selectcolor=self.ACCENT_TEAL,
            activebackground=self.ACCENT_TEAL,
            activeforeground=self.FG_MAIN,
            relief=tk.FLAT,
            font=('Segoe UI', 8, 'bold'),
            padx=8,
            pady=3,
            cursor="hand2"
        )
        self.rb1.pack(side=tk.LEFT, padx=(5, 2))
        self.rb2= tk.Radiobutton(
            self.radio_container, 
            text='False', 
            variable=self.val_approv, 
            value=0, 
            indicatoron=0, 
            command=self.update_label,
            bg=self.BG_INPUT,
            #fg=self.FG_MUTED,
            fg='#c7c7c7',
            selectcolor=self.ACCENT_TEAL,
            activebackground=self.ACCENT_TEAL,
            activeforeground=self.FG_MAIN,
            relief=tk.FLAT,
            font=('Segoe UI', 8, 'bold'),
            padx=8,
            pady=3,
            cursor="hand2"
        )
        self.rb2.pack(side=tk.LEFT, padx=2)
        self.rb3= tk.Radiobutton(
            self.radio_container, 
            text='Reject', 
            variable=self.val_approv, 
            value=2, 
            indicatoron=0, 
            command=self.update_label,
            bg=self.BG_INPUT,
            #fg=self.FG_MUTED,
            fg='#c7c7c7',
            selectcolor=self.ACCENT_TEAL,
            activebackground=self.ACCENT_TEAL,
            activeforeground=self.FG_MAIN,
            relief=tk.FLAT,
            font=('Segoe UI', 8, 'bold'),
            padx=8,
            pady=3,
            cursor="hand2"
        )
        self.rb3.pack(side=tk.LEFT, padx=2)
        self.rb4= tk.Radiobutton(
            self.radio_container, 
            text='NonApprov', 
            variable=self.val_approv, 
            value=99, 
            indicatoron=0, 
            command=self.update_label,
            bg=self.BG_INPUT,
            #fg=self.FG_MUTED,
            fg='#c7c7c7',
            selectcolor=self.ACCENT_TEAL,
            activebackground=self.ACCENT_TEAL,
            activeforeground=self.FG_MAIN,
            relief=tk.FLAT,
            font=('Segoe UI', 8, 'bold'),
            padx=8,
            pady=3,
            cursor="hand2"
        )
        self.rb4.pack(side=tk.LEFT, padx=2)

        # --- Tombol Baris 3: Close App & Exit App ---
        self.btn_frame_3 = tk.Frame(self.func2_frame, bg=self.BG_CARD)
        self.btn_frame_3.pack(fill=tk.X, pady=5)

        self.btn_func_2 = tk.Button(
            self.btn_frame_3, 
            text="Run Function", 
            command=self.run_function_2, 
            bg=self.ACCENT_TEAL, 
            fg=self.FG_MAIN,
            font=('Segoe UI', 9, 'bold'), 
            relief=tk.FLAT,
            activebackground="#05A87E",
            activeforeground=self.FG_MAIN,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_func_2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_stop_app = tk.Button(
            self.btn_frame_3, 
            text="Stop Running", 
            command=self.stop_thread, 
            bg=self.ACCENT_RED, 
            fg=self.FG_MAIN,
            font=('Segoe UI', 9, 'bold'), 
            relief=tk.FLAT,
            activebackground="#C2002B",
            activeforeground=self.FG_MAIN,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_stop_app.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        # --- Log Area ---
        # 1. Buat frame horizontal untuk menampung Label dan Tombol Clear
        log_header_frame = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        log_header_frame.pack(fill=tk.X, pady=(5, 5))

        # 2. Label ditaruh di dalam log_header_frame (pack ke KIRI)
        tk.Label(log_header_frame, text="Log Aktivitas:", anchor='w', bg=self.BG_MAIN, fg=self.FG_MUTED, font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, fill=tk.X)
        # 3. Tombol Clear ditaruh di dalam log_header_frame (pack ke KANAN)
        clear_btn = tk.Button(
            log_header_frame,
            text="Clear",
            font=('Segoe UI', 8, 'bold'),
            bg="#2A2A38", 
            fg=self.FG_MAIN,         # Menyesuaikan tema warna Anda
            relief=tk.SOLID,
            bd=1,
            cursor="hand2",          # Mengubah cursor saat hover
            command=self.clear_log   # Fungsi yang dijalankan saat diklik
        )
        clear_btn.pack(side=tk.LEFT)
        self.log_area = scrolledtext.ScrolledText(
            self.main_frame, 
            wrap=tk.WORD, 
            height=20, 
            font=('Consolas', 8),
            bg=self.BG_CARD,
            fg=self.FG_MAIN,
            insertbackground=self.FG_MAIN, # cursor color
            bd=1,
            relief=tk.SOLID,
            highlightthickness=0
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.tag_config("red_tag", foreground=self.ACCENT_RED)
        self.log_area.tag_config("green_tag", foreground=self.ACCENT_TEAL)
        self.log_area.vbar.config(
            troughcolor="#2d2d2d",       # Warna jalur/rel scrollbar
            bg=self.BG_CARD,             # Warna kotak geser (slider)
            activebackground=self.FG_MAIN, # Warna kotak geser saat disorot mouse
            bd=0,                        # Menghilangkan border agar minimalis
            elementborder=0              # Menghilangkan border elemen internal
        )

        # Log pesan awal
        self.log_message("Aplikasi dimulai. Selamat datang!")
        self.log_message(f"Using sso {msgsso}")
        # Set pilihan awal
        self.rw1.select()
        self.update_label_vwrite()
        if approv == "approv4":
            self.rb4.select()
        else: self.rb1.select()
        self.update_label()

    # --- Utility Function untuk membuat field input berulang ---
    def create_input_field(self, label_text, placeholder, attr_name, parent, show='', value=False):
        frame = tk.Frame(parent, bg=parent.cget('bg'))
        frame.pack(fill=tk.X, pady=4)
        
        # Menggunakan font dan layout yang lebih modern & bersih
        tk.Label(
            frame, 
            text=label_text, 
            width=14, 
            anchor='w', 
            bg=parent.cget('bg'), 
            #fg=self.FG_MUTED if parent.cget('bg') == self.BG_MAIN else self.FG_MAIN,
            fg='#ffffff',
            font=('Segoe UI', 9, 'bold')
        ).pack(side=tk.LEFT)
        
        entry = tk.Entry(
            frame, 
            relief=tk.FLAT, 
            show=show,
            bg=self.BG_INPUT,
            fg="#C7C7C7",
            insertbackground=self.FG_MAIN,
            font=('Segoe UI', 9),
            bd=4 # Memberikan visual internal margin/padding yang bersih
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Simpan reference ke entry object
        setattr(self, attr_name, entry) 

        if value:
            # Jika ada VALUE asli, gunakan warna teks utama/terang
            entry.config(fg="#ffffff") # Sesuaikan dengan warna teks aktif Anda
            entry.insert(0, value)
        else:
            # Jika tidak ada value, isi dengan PLACEHOLDER dan warna abu-abu
            entry.config(fg="#C7C7C7")
            entry.insert(0, placeholder) # Menggunakan insert untuk placeholder
        
        # Event handler untuk menghapus placeholder saat fokus
        entry.bind('<FocusIn>', lambda event, e=entry, p=placeholder: self.clear_placeholder(e, p))
        entry.bind('<FocusOut>', lambda event, e=entry, p=placeholder: self.restore_placeholder(e, p))

    # --toggle section frame
    def toggle_section(self, target_frame, target_button, other_frame, other_button):
        # 1. Jika frame yang diklik saat ini sedang terbuka, cukup tutup saja
        if target_frame.winfo_manager():
            target_frame.pack_forget()
            target_button.config(text=target_button.cget("text").replace("▼", "▶"))

        # 2. Jika frame yang diklik sedang tertutup
        else:
            # Tutup frame pasangan terlebih dahulu jika dia sedang terbuka
            if other_frame.winfo_manager():
                other_frame.pack_forget()
                other_button.config(text=other_button.cget("text").replace("▼", "▶"))

            # Tampilkan frame yang diklik tepat di bawah tombol pemicunya
            target_frame.pack(fill=tk.X, pady=(5, 3), after=target_button)
            target_button.config(text=target_button.cget("text").replace("▶", "▼"))

    # --update untuk radiobtn
    def update_label(self):
        """Fungsi yang dipanggil saat radiobutton diklik."""

        match self.val_approv.get():
            case 1:
                self.log_message(f"Pilihan approve: Ya, sekalian diapprove")
            case 0:
                self.log_message(f"Pilihan approve: Gausa diapprove")
            case 2: 
                self.log_message(f"Pilihan approve: Reject")
            case 99:  
                self.log_message(f"Pilihan approve: Bukan approval")
        pass

    # --update untuk radiobtn vwrite
    def update_label_vwrite(self):
        """Fungsi yang dipanggil saat radiobutton diklik."""
        if self.vwrite.get() == 1:
            self.log_message(f"Pilihan Write data.csv: Rewrite")
            self.rw1.config(fg=self.FG_MAIN)
            self.rw2.config(fg=self.FG_MUTED)
        else :
            self.rw2.config(fg=self.FG_MAIN)
            self.rw1.config(fg=self.FG_MUTED)
            cekcsv = load_setting_file(self,filename="data.csv",load=False)
            if cekcsv:
                self.log_message(f"Pilihan Write data.csv: Append to data.csv")
            else:
                self.log_message(f"data.csv tidak ditemukan, harap pilih 'Rewrite'", tag="red_tag")
        pass

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=self.FG_MAIN)
            # Jika ini field password, kembalikan 'show'
            if entry.cget('show') == '*':
                 pass # Tetap tampilkan '*'

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg='#8E8E9F')
            # Jika ini field password, hilangkan 'show'
            if entry.cget('show') == '*':
                 pass # Tetap tampilkan '*'

    # --- change status var function ---
    def change_status(self, new_status, color="blue"):
        self.status_var.set(new_status)
        # Menyesuaikan penamaan warna ke palette baru
        color_map = {
            "blue": self.ACCENT_BLUE_DARK,
            "green": self.ACCENT_TEAL_DARK,
            "red": self.ACCENT_RED_DARK
        }
        actual_color = color_map.get(color, color)
        self.status_label.config(fg="white", bg=actual_color)

    # --- load user ---
    def load_credentials(self):
        try:
            path = os.path.join(os.getcwd(), 'tempuser.txt')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    lines = f.read().splitlines()
                    return lines[0], lines[1], lines[2], "Loaded", lines[3]
        except: pass
        # return "jey.neutron", "password", "approv1", "Default", "Input_Tambahan"
        return False, False, False, "Default", False
    
    # --- Log Message Function ---
    def log_message(self, message, tag=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_area.see(tk.END) # Scroll otomatis ke bawah

    # --- Stop Thread Function ---
    def stop_thread(self):
        self.stop_event.set() # Kirim sinyal untuk berhenti

    # --- Clear log message ---
    def clear_log(self):
        # Hapus dari index '1.0' (awal) sampai 'end' (akhir)
        self.isdone = 1
        self.log_area.delete('1.0', "end")
        self.log_message("Cleared! Aplikasi dimulai. Selamat datang!")

        if self.vwrite.get() == 1:
            self.log_message(f"Pilihan Write data.csv: Rewrite")
        else:
            self.log_message(f"Pilihan Write data.csv: Append")

        if self.val_approv.get() == 1:
            self.log_message(f"Pilihan approve: Ya, sekalian diapprove")
        else :
            self.log_message(f"Pilihan approve: Gausa diapprove")

    # --- Get path os or url path on folder assets ---
    @staticmethod
    def getassets(namafile, ospath = False):
        from pathlib import Path
        try:
            assets_folder = get_assets_path()
            html_file_path = os.path.join(assets_folder, namafile)
            html_url = Path(html_file_path).as_uri()
            if ospath: return html_file_path
            return html_url
        
        except: return None

    # --- Browser App Functions ---
    def open_browser(self):
        self.log_message("Perintah: Membuka browser.")
        try:
            # self.driver = webdriver.Chrome() # Selenium akan otomatis mencari & mendownload ChromeDriver yang sesuai
            if self.playwright_instance is None:
                self.playwright_instance = sync_playwright().start()
            try:
                # 1. Coba hubungkan ke browser yang sudah ada
                self.log_message("Mengecek browser yang terbuka...")
                self.browser = self.playwright_instance.chromium.connect_over_cdp("http://localhost:9222")                    
                self.page = self.browser.contexts[0].pages[0]

                # self.page.goto('https://www.google.com')
                self.page.goto(self.getassets('index.html'))
                self.page.wait_for_load_state("load")
                self.page.wait_for_timeout(2000)
                history_length = self.page.evaluate("window.history.length")
                if history_length > 1:
                    try:
                        self.page.go_back(timeout=3000)
                    except Exception:
                        pass
                else: pass

                self.change_status("STATUS: Browser Ready", color="green")
                self.log_message("Berhasil terhubung ke browser yang sudah ada!")
                self.log_message("Ready for action.")
                
            except PlaywrightError as e:
                # 2. Jika gagal (browser belum dibuka), luncurkan browser baru dari nol
                self.log_message(f"ERROR: ({str(e).split('Call:')[0]})")    
                self.log_message("Browser not found. Open new...")
                # self.browser = p.chromium.launch(headless=False)
                # Opsional: Jika ingin otomatis membuka Chrome asli Anda lewat script,
                # gunakan baris di bawah ini menggantikan p.chromium.launch:
                subprocess.Popen(r'start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"', shell=True)
                time.sleep(3)
                # Loop sampai port aktif
                port_siap = False
                while not port_siap:
                    try:
                        with socket.create_connection(("127.0.0.1", 9222), timeout=5):
                            port_siap = True
                    except (ConnectionRefusedError, socket.timeout):
                        time.sleep(0.5) # Cek ulang setiap 0.5 detik
                try:
                    self.browser = self.playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
                    context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
                    self.page = context.pages[0] if context.pages else context.new_page()
                    self.page.goto(self.getassets('index.html'))
                    self.change_status("STATUS: Browser Ready", color="green")
                    self.log_message("Berhasil terhubung ke browser baru!")
                    self.log_message("Ready for action.")
                except Exception:
                    self.log_message("Gagal terhubung ke Chrome. Pastikan port 9222 tidak diblokir. Coba Start Browser lagi")
                    self.change_status("STATUS: Browser not terhubung", color="red")
                    
            except Exception as e:
                self.change_status("STATUS: Browser Error", color="red")
                self.log_message(f"ERROR: ({str(e).split('Stacktrace:')[0]})", tag="red_tag")    
                
        except Exception as e:
            self.change_status("STATUS: Browser Error", color="red")
            self.log_message(f"ERROR: Gagal membuka browser. ({str(e).split('Stacktrace:')[0]})", tag="red_tag")    

    def close_port_9222(self):
        try:
            # 1. Cari PID yang menggunakan port 9222 lewat netstat
            result = subprocess.check_output('netstat -ano | findstr :9222', shell=True).decode()
            # Ambil semua angka PID yang ada di baris akhir netstat
            pids = set(re.findall(r'\s+(\d+)\s*$', result, re.MULTILINE))
            
            # 2. Kill masing-masing PID tersebut secara spesifik
            for pid in pids:
                if pid != "0": # Pastikan bukan system process
                    subprocess.Popen(f'taskkill /F /PID {pid}', shell=True)
            self.log_message("Chrome di port 9222 berhasil ditutup.")
        except Exception:
            # Jika port 9222 memang sudah mati/tidak ditemukan, netstat akan error (ignore saja)
            self.log_message("Tidak ada Chrome aktif di port 9222.")

    def close_browser(self):
        self.log_message("Perintah: Menutup browser.")
        self.change_status("STATUS: Browser Ditutup", color="blue")
        # Simulasikan pekerjaan
        # if self.driver:
        #     self.driver.quit()
        #     self.driver = None
        if self.playwright_instance:
            self.playwright_instance.stop()
            try:
                self.playwright_instance.stop()
            except Exception as e:
                self.log_message(f"Gagal menghentikan instance: {e}")
            finally:
                # PENTING: Setel ulang menjadi None agar bisa di-start ulang nanti
                self.playwright_instance = None 
                self.browser = None
                self.page = None
        self.close_port_9222()
        self.log_message("Browser telah ditutup.")

    def open_link_in_browser(self):
        link = self.link_entry.get()
        if not link.startswith("http"):
            link = "https://" + link
        if link and link != "https://fasih-sm.bps.go.id/survey-xx":
            self.change_status("STATUS: Menuju link...", color="blue")
            self.log_message(f"Menuju link dengan SSO: {self.username_entry.get()}")
            self.log_message(f"Target link: {link}")
            try:
                #self.driver.get(link)
                self.page.goto(link)
                self.log_message(f"Sukses: link target terbuka. Title Page: {self.page.title()}")
                # try login sso disini
                # Validasi sederhana
                #if "bps.go.id" in self.driver.current_url:
                if "bps.go.id" in self.page.url:
                    if self.username_entry.get() in ["Masukkan Username...", "jey.neutron" ,""]:
                        self.log_message("ERROR: Fungsi 1 dibatalkan. Username tidak valid.", "red_tag")
                        return
                    self.thread = threading.Thread(target=self.login_sso, args=(link,))
                    self.thread.start()
                else:
                    pass
                # end try login sso
            except Exception as e:
                self.change_status("STATUS: Error membuka link", color="red")
                self.log_message(f"ERROR: Gagal membuka browser. Pastikan format link benar atau cek VPN. ({str(e).split('Stacktrace:')[0]})", tag="red_tag")
        else:
            self.log_message("PERINGATAN: Link belum diisi atau masih placeholder.", tag="red_tag")

    # --- Login SSO Function ---
    def login_sso(self, link):
        self.log_message("Mencoba login SSO...")
        try:
            # 1. Coba hubungkan ke browser yang sudah ada
            p = sync_playwright().start()
            browser = p.chromium.connect_over_cdp("http://localhost:9222")                    
            page = browser.contexts[0].pages[0]
            # try: #waiting login sso button
            #     WebDriverWait(self.driver, 10).until( #using explicit wait for x seconds
            #         EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
            #     ).click()
            # except:
            #     pass
            # WebDriverWait(self.driver, 15).until( #using explicit wait for x seconds
            #     EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
            # self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(self.username_entry.get())
            # self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.password_entry.get())
            # self.driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
            if self.stop_event.is_set():
                raise InterruptedError("Process stopped by user.")
            page.get_by_role("link", name="Login SSO BPS").click()
            page.get_by_role("textbox", name="Username or email").click()
            page.get_by_role("textbox", name="Username or email").fill(self.username_entry.get())
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(self.password_entry.get())
            page.get_by_role("button", name="Log In").click()
            time.sleep(5) #wait for redirect
            self.log_message('Login SSO done')
            # self.driver.get(link) #reopen the link after login
            page.goto(link)
            self.change_status("STATUS: Target link ready, waiting your action...", color="green")
            self.log_message("Silakan memilih survei sendiri sampai ke halaman list tabel data.")
        except Exception as e:
            self.log_message(f"Error di thread data loginsso: {e}", tag="red_tag")
            self.isdone= 1
        finally:
            # Selalu tutup p_instance di blok 'finally' agar tidak hang
            self.isdone= 1
            try:
                p.stop()
                #self.log_message("Koneksi Playwright di thread ditutup.")
            except NameError:
                # Terjadi jika get playwright page() gagal total di awal
                pass

    # --- Function 1 ---
    def run_function_1(self):
        # check thread
        if self.thread and self.thread.is_alive():
            self.log_message("ERROR: Running Get_List_Data dibatalkan. Masih ada proses yang berjalan.", "red_tag")
            return
        self.stop_event.clear() #reset signal
        #
        self.isdone = 0
        try:
            self.log_message("Perintah: Memulai Get list data...")
            self.change_status("STATUS: Getting list data...", color="blue")
            
            if self.vwrite.get() == 1:
                mode = 'w'
            elif self.vwrite.get() == 0:
                mode = 'a'
            self.thread = threading.Thread(target=get_list_data, args=(self, "data.csv",mode))
            self.thread.start()
        except Exception as e:
            self.isdone = 1
            self.log_message(f"ERROR: {e}...", tag="red_tag")
        # Mulai pengecekan berkala apakah sudah selesai
        self.check_isdone()

    # --- Function 2 ---
    def run_function_2(self):
        # check thread
        if self.thread and self.thread.is_alive():
            self.log_message("ERROR: Running Function dibatalkan. Masih ada proses yang berjalan.", "red_tag")
            return
        self.stop_event.clear() #reset signal
        #
        self.isdone = 0
        self.log_message("Perintah: Memulai running function...")
        self.change_status("STATUS: Running data...", color="blue")

        # Ambil input spesifik untuk Fungsi 2
        start_row = self.start_row_entry.get()
        filename = self.filename_entry.get()
        extra_input = self.extra_input_entry.get()
        var_input = self.var_input_entry.get()

        # Validasi sederhana untuk baris mulai
        try:
            if (start_row == 'Cth: 0 (untuk mulai dari awal)') and (self.val_approv.get() == 99):
               row_num = 0
            else:            
                row_num = int(start_row)
            if row_num < 0:
                raise ValueError
        except ValueError:
            self.isdone = 1
            self.change_status("STATUS: Running batal", color="blue")
            self.log_message(f"ERROR: Fungsi 2 dibatalkan. Baris Mulai '{start_row}' harus berupa angka positif.", "red_tag")
            return

        self.log_message(f"--- Detail Fungsi 2 ---")
        self.log_message(f"Baris Mulai: {row_num}")
        self.log_message(f"Nama File: {filename}")
        self.log_message(f"Input Tambahan: {extra_input}")

        if extra_input == "Input opsional... (cth: help)" or extra_input.strip() == "":
            self.log_message("Catatan: Tidak ada fungsi tambahan yang dipilih.")
            extra_input_fun = None 
            self.isdone = 1
        else:
            try:
                external_funcs = load_setting_file(self)
                extra_input_fun = external_funcs.get(extra_input)
                self.log_message(f"Modul '{extra_input}' sukses diimpor, loading")
            except Exception as e:
                self.log_message( f"ERROR: Terjadi kesalahan saat import modul/file: {e}", tag="red_tag")

        try:
            if self.val_approv.get() == 99:
                if var_input == "Variabel opsional tambahan..." or var_input == "" or var_input == None: var_input =1
                self.thread = threading.Thread(target=extra_input_fun, args=(self,var_input))
            elif extra_input == "get_list_data" or extra_input == "mainfunc":
                self.log_message(f"ERROR: Fungsi 2 dibatalkan. Input tambahan invalid.", "red_tag")
                return
            else:
                self.page.goto(self.getassets('index.html'))
                self.page.evaluate("document.body.setAttribute('data-status', 'running')")
                if self.val_approv.get() == 1:
                    cekapprove = True
                elif self.val_approv.get() == 0:
                    cekapprove = False
                elif self.val_approv.get() == 2:
                    cekapprove = "Reject"
                self.thread = threading.Thread(target=mainfunc, args=(self, filename, cekapprove, row_num, extra_input_fun))
            self.thread.start()

        except Exception as e:
            self.isdone = 1
            self.log_message(f"ERROR: {e}...", tag="red_tag")

        # Mulai pengecekan berkala apakah sudah selesai
        self.check_isdone()
        
    # check is done function
    def check_isdone(self):
        if self.isdone != 1:
            self.master.after(1000, self.check_isdone)
        else:
            if self.page:
                # return to idx done
                self.page.goto(self.getassets('index.html'))
                self.page.evaluate("document.body.setAttribute('data-status', 'done')")
                # add go back if already done if any page open
                history_length = self.page.evaluate("window.history.length")
                if history_length > 1:
                    try:
                        self.page.go_back(timeout=3000)
                    except Exception:
                        pass
                else: pass
            self.log_message(f"Running program berhasil diproses. Cek file output", tag="green_tag")
            self.change_status("STATUS: DONE! Running selesai", color="green")

def jalankan_aplikasi():
    splash = tk.Tk()
    splash.title("Loading")
    # Atur ukuran dan posisi di tengah layar
    lebar, tinggi = 350, 180
    layar_lebar = splash.winfo_screenwidth()
    layar_tinggi = splash.winfo_screenheight()
    x = (layar_lebar // 2) - (lebar // 2)
    y = (layar_tinggi // 2) - (tinggi // 2)
    splash.geometry(f'{lebar}x{tinggi}+{x}+{y}')
    splash.overrideredirect(True) # Tanpa bingkai
    
    # Modern Dark styling for splash screen
    splash.configure(bg="#22222E")
    # Kolom 0 dan 1 (tempat gambar & teks) akan membagi ruang sama rata secara horizontal
    splash.grid_columnconfigure(0, weight=0)
    splash.grid_columnconfigure(1, weight=1)

    # Tambahkan weight=1 pada baris sebelum dan sesudah konten agar terdorong secara vertikal
    splash.grid_rowconfigure(0, weight=1)  # Ruang kosong atas
    splash.grid_rowconfigure(1, weight=0) 
    splash.grid_rowconfigure(
        2, weight=0
    )  # Baris 1 (Konten Gambar & Judul) -> ketat sesuai isi
    splash.grid_rowconfigure(
        3, weight=0
    )  # Baris 2 (Konten Loading) -> ketat sesuai isi
    splash.grid_rowconfigure(4, weight=1)  # Ruang kosong bawah

    try:
        img_ico = Image.open(AutoApp.getassets('ikonku.ico', ospath=True))
        # Ubah ukuran gambar jika ikon terlalu kecil/besar
        img_ico = img_ico.resize((40, 40), Image.Resampling.LANCZOS)
        img_tampil = ImageTk.PhotoImage(img_ico)

        # Masukkan gambar ke dalam Label Tkinter
        label_gambar = tk.Label(splash, image=img_tampil, bg="#22222E")

    except Exception as e:
        # Label teks cadangan jika file .ico tidak ditemukan
        label_gambar = tk.Label(splash, text="🤖", font=('Segoe UI', 22, 'bold'), fg="#3A86FF", bg="#22222E")

    label_gambar.pack(pady=(10,0))
    label_gambar.grid(row=1, column=0, pady=(0, 0), padx=(40, 5))

    label_teks = tk.Label(splash, text="Auto-Fasih-SM", font=('Segoe UI', 22, 'bold'), fg="#3A86FF", bg="#22222E")#.pack(pady=(0, 0))
    label_teks.grid(row=1, column=1, pady=(0, 0), padx=(0, 40))
    tk.Label(splash, text="Sedang Memuat Aplikasi...", font=('Segoe UI', 9), fg="#c7c7c7", bg="#22222E").grid(row=2, column=0, columnspan=2, pady=(0, 10))#.pack(pady=(0, 10))
    
    # Styling modern progressbar
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Modern.Horizontal.TProgressbar", 
        foreground="#3A86FF", 
        background="#3A86FF", 
        thickness=4, 
        bordercolor="#22222E", 
        troughcolor="#1A1A22"
    )
    
    progress = ttk.Progressbar(splash, mode="indeterminate", length=220, style="Modern.Horizontal.TProgressbar")
    # progress.pack(pady=10)
    progress.grid(row=3, column=0, columnspan=2, pady=(0, 0))
    progress.start(15)

    tk.Label(splash, text="By: jey.neutron", font=('Segoe UI', 8, 'italic'), fg="#c7c7c7", bg="#22222E").grid(row=4, column=0, columnspan=2, padx=1, pady=(0, 10))#.pack(padx=1, pady=(0, 10))

    def pindah_ke_utama():
        """Fungsi untuk menutup splash dan buka aplikasi utama."""
        progress.stop()
        splash.destroy()
        root_utama = tk.Tk()
        app = AutoApp(root_utama)
        root_utama.mainloop()

    # Jalankan proses berat di THREAD TERPISAH agar UI tidak membeku
    thread = threading.Thread(target=initlib, args=(lambda: splash.after(0, pindah_ke_utama),))
    thread.start()

    splash.mainloop()

if __name__ == '__main__':
    jalankan_aplikasi()