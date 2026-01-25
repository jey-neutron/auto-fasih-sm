# Library
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import importlib
import os
import pandas as pd
import tkinter as tk
import threading
from tkinter import scrolledtext
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import csv
import numpy as np
import sys

# import fungsi dari file lain
#from get_data import mainfunc
#from get_data import get_list_data
#CONFIG_FILE = "setting_kode.py"

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
    
    # 2. Cek apakah file ada
    if not os.path.exists(file_path):
        instance.log_message(message=f"ERROR: File konfigurasi tidak ditemukan: {filename}", tag="red_tag")
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

#####

# Main app
class SimpleApp:
    def __init__(self, master):
        # konfigurasi import fungsi dari get_data.py
        # 1. Load fungsi dari file eksternal
        external_funcs = load_setting_file(self)
        if external_funcs is None:
            time.sleep(10)
            root.destroy()
            return
        # 2. Ambil fungsi yang dibutuhkan
        global mainfunc
        global get_list_data
        mainfunc = external_funcs.get('mainfunc')
        get_list_data = external_funcs.get('get_list_data')
        
        # konfigurasi variabel
        self.driver = None
        self.isdone = None

        # Konfigurasi jendela utama
        self.master = master
        master.title("Aplikasi AutoFasih")
        master.geometry("450x700") # Ukuran awal
        master.attributes("-topmost", True) # Selalu di atas
        master.resizable(True, True) # Memungkinkan resize

        # Menambahkan frame utama untuk padding
        self.main_frame = tk.Frame(master, padx=15, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Variabel STATUS ---
        self.status_var = tk.StringVar(value="STATUS: Belum dikenapa-napain")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var, 
                                     fg="white", bg="blue", font=('Arial', 10, 'bold'), anchor='w')
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        # --- Input Fields (Field 1: Username) ---
        self.create_input_field("Username SSO:", "jimmy.nx", "username_entry", self.main_frame)
        
        # --- Input Fields (Field 2: Password) ---
        self.create_input_field("Password SSO:", "pass", "password_entry", self.main_frame, show='*')
        
        # --- Input Fields (Field 3: Link) ---
        self.create_input_field("Link target:", "https://fasih-sm.bps.go.id/", "link_entry", self.main_frame)
        
        # 

        # --- Tombol Baris 1: Buka Aplikasi & Buka Link ---
        self.btn_frame_1 = tk.Frame(self.main_frame)
        self.btn_frame_1.pack(fill=tk.X, pady=(15, 5))

        self.btn_open_app = tk.Button(self.btn_frame_1, text="Open Browser", command=self.open_browser, bg="#E6F7FF", relief=tk.RAISED)
        self.btn_open_app.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_open_link = tk.Button(self.btn_frame_1, text="Goto Link", command=self.open_link_in_browser, bg="#E6F7FF", relief=tk.RAISED)
        self.btn_open_link.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # --- Tombol Baris 2: Fungsi 1 & Fungsi 2 ---
        self.btn_frame_2 = tk.Frame(self.main_frame)
        self.btn_frame_2.pack(fill=tk.X, pady=10)

        # Variabel kontrol untuk menyimpan nilai radiobutton yang dipilih
        self.vwrite = tk.IntVar(value=1)
        # Label untuk menampilkan hasil pilihan
        self.label_hasil = tk.Label(self.btn_frame_2, text="Write data.csv?")
        self.label_hasil.pack(pady=5, side=tk.LEFT)
        # radio
        self.rw1= tk.Radiobutton(self.btn_frame_2, text='Rewrite', variable=self.vwrite, value=1, indicatoron=0, command=self.update_label_vwrite)
        self.rw1.pack(side=tk.LEFT, padx=0)
        self.rw2= tk.Radiobutton(self.btn_frame_2, text='Append', variable=self.vwrite, value=0, indicatoron=0, command=self.update_label_vwrite)
        self.rw2.pack(side=tk.LEFT, padx=0)

        # main btn func 1
        self.btn_func_1 = tk.Button(self.btn_frame_2, text="Get List Data", command=self.run_function_1, bg="#FFF2E6", relief=tk.RAISED)
        self.btn_func_1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))

        #self.btn_func_2 = tk.Button(self.btn_frame_2, text="Run Function", command=self.run_function_2, bg="#FFF2E6", relief=tk.RAISED)
        #self.btn_func_2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # --- SECTION : Input Fields Khusus Fungsi 2 (LabelFrame) ---
        self.func2_frame = tk.LabelFrame(self.main_frame, text="Parameter Fungsi 'Run Function'", padx=10, pady=5, bd=2, relief=tk.GROOVE)
        self.func2_frame.pack(fill=tk.X, pady=(10, 15))

        # Menggunakan func2_frame sebagai parent untuk input ini
        self.create_input_field("Baris Mulai:", "Cth: 0 (untuk mulai dari awal)", "start_row_entry", self.func2_frame)
        self.create_input_field("Nama File:", "data.csv", "filename_entry", self.func2_frame)
        self.create_input_field("Input Tambahan:", "Input opsional...", "extra_input_entry", self.func2_frame)
        
        # Variabel kontrol untuk menyimpan nilai radiobutton yang dipilih
        self.v = tk.IntVar(value=1)
        # Label untuk menampilkan hasil pilihan
        self.label_hasil = tk.Label(self.func2_frame, text="Sekalian approve Fasih?")
        self.label_hasil.pack(pady=5, side=tk.LEFT)
        # radio
        self.rb1= tk.Radiobutton(self.func2_frame, text='True', variable=self.v, value=1, indicatoron=0, command=self.update_label)
        self.rb1.pack(side=tk.LEFT, padx=0)
        self.rb2= tk.Radiobutton(self.func2_frame, text='False', variable=self.v, value=0, indicatoron=0, command=self.update_label)
        self.rb2.pack(side=tk.LEFT, padx=0)
        self.rb3= tk.Radiobutton(self.func2_frame, text='NonFasih', variable=self.v, value=99, indicatoron=0, command=self.update_label)
        self.rb3.pack(side=tk.LEFT, padx=0)

        # --- Tombol Baris 3: Close App & Exit App ---
        self.btn_frame_3 = tk.Frame(self.main_frame)
        self.btn_frame_3.pack(fill=tk.X, pady=15)

        self.btn_func_2 = tk.Button(self.btn_frame_3, text="Run Function", command=self.run_function_2, bg="#FFF2E6", relief=tk.RAISED)
        self.btn_func_2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(1, 5))

        self.btn_close_app = tk.Button(self.btn_frame_3, text="Close Browser", command=self.close_browser, bg="#E6F7FF", relief=tk.RAISED)
        self.btn_close_app.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 1))

        #self.btn_exit = tk.Button(self.btn_frame_3, text="Exit App", command=master.quit, bg="#FFEEEE", relief=tk.RAISED)
        #self.btn_exit.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # --- Log Area ---
        tk.Label(self.main_frame, text="Log Aktivitas:", anchor='w').pack(fill=tk.X, pady=(10, 5))
        self.log_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=15, font=('Consolas', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.tag_config("red_tag", foreground="red")
        self.log_area.tag_config("green_tag", foreground="green")

        # Log pesan awal
        # Set pilihan awal
        self.log_message("Aplikasi dimulai. Selamat datang!")
        self.rw1.select()
        self.update_label_vwrite()
        self.rb1.select()
        self.update_label()

    # --- Utility Function untuk membuat field input berulang ---
    def create_input_field(self, label_text, placeholder, attr_name, parent, show=''):
        #frame = tk.Frame(self.main_frame)
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        tk.Label(frame, text=label_text, width=12, anchor='w').pack(side=tk.LEFT)
        
        entry = tk.Entry(frame, relief=tk.SUNKEN, show=show)
        entry.insert(0, placeholder) # Menggunakan insert untuk placeholder
        entry.config(fg='gray')
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Simpan reference ke entry object
        setattr(self, attr_name, entry) 
        
        # Event handler untuk menghapus placeholder saat fokus
        entry.bind('<FocusIn>', lambda event, e=entry, p=placeholder: self.clear_placeholder(e, p))
        entry.bind('<FocusOut>', lambda event, e=entry, p=placeholder: self.restore_placeholder(e, p))

    # --update untuk radiobtn
    def update_label(self):
        """Fungsi yang dipanggil saat radiobutton diklik."""
        # Nilai dari radiobutton yang dipilih otomatis tersimpan di self.pilihan_var.
        # Kita hanya memastikan label display sudah menampilkan nilai terbaru.
        if self.v.get() == 1:
            self.log_message(f"Pilihan approve: Ya, sekalian diapprove")
        else :
            self.log_message(f"Pilihan approve: Gausa diapprove")
        # Karena kita menggunakan textvariable, label akan otomatis terupdate.
        pass

    # --update untuk radiobtn vwrite
    def update_label_vwrite(self):
        """Fungsi yang dipanggil saat radiobutton diklik."""
        # Nilai dari radiobutton yang dipilih otomatis tersimpan di self.pilihan_var.
        # Kita hanya memastikan label display sudah menampilkan nilai terbaru.
        if self.vwrite.get() == 1:
            self.log_message(f"Pilihan Write data.csv: Rewrite")
        else :
            cekcsv = load_setting_file(self,filename="data.csv",load=False)
            if cekcsv:
                self.log_message(f"Pilihan Write data.csv: Append to data.csv")
            else:
                self.log_message(f"data.csv tidak ditemukan, harap pilih 'Rewrite'", tag="red_tag")
        # Karena kita menggunakan textvariable, label akan otomatis terupdate.
        pass

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')
            # Jika ini field password, kembalikan 'show'
            if entry.cget('show') == '*':
                 pass # Tetap tampilkan '*'

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg='gray')
            # Jika ini field password, hilangkan 'show'
            if entry.cget('show') == '*':
                 pass # Tetap tampilkan '*'

    # --- change status var function ---
    def change_status(self, new_status, color="blue"):
        self.status_var.set(new_status)
        self.status_label.config(fg="white", bg=color)

    # --- Log Message Function ---
    def log_message(self, message, tag=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_area.see(tk.END) # Scroll otomatis ke bawah

    # --- Browser App Functions ---
    def open_browser(self):
        self.log_message("Perintah: Membuka browser.")
        try:
            service = Service(executable_path="chromedriver.exe") 
            #service = Service(executable_path="geckodriver.exe") 
            self.driver = webdriver.Chrome(service=service)
            #self.driver = webdriver.Firefox(service=service)
            self.log_message("Ready for action.")
            self.change_status("STATUS: Browser Ready", color="green")
        except Exception as e:
            self.change_status("STATUS: Browser Error", color="red")
            self.log_message(f"ERROR: Gagal membuka browser. ({str(e).split('Stacktrace:')[0]})", tag="red_tag")    

    def close_browser(self):
        self.log_message("Perintah: Menutup browser.")
        self.change_status("STATUS: Browser Ditutup", color="blue")
        # Simulasikan pekerjaan
        if self.driver:
            self.driver.quit()
            self.driver = None
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
                self.driver.get(link)
                self.log_message("Sukses: link target terbuka.")
                # try login sso disini
                # Validasi sederhana
                if self.username_entry.get() in ["Masukkan Username...", "jimmy.nx" ,""]:
                    self.log_message("ERROR: Fungsi 1 dibatalkan. Username tidak valid.")
                    return
                if "bps.go.id" in self.driver.current_url:
                    login_thread = threading.Thread(target=self.login_sso, args=(link,))
                    login_thread.start()
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
        try: #waiting login sso button
            WebDriverWait(self.driver, 10).until( #using explicit wait for x seconds
                EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
            ).click()
        except:
            pass
        WebDriverWait(self.driver, 15).until( #using explicit wait for x seconds
            EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
        self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(self.username_entry.get())
        self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.password_entry.get())
        self.driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
        time.sleep(5) #wait for redirect
        self.log_message('Login SSO done')
        self.driver.get(link) #reopen the link after login
        self.change_status("STATUS: Target link ready, waiting your action...", color="green")
        self.log_message("Silakan memilih survei sendiri sampai ke halaman list tabel data.")

    # --- Function 1 ---
    def run_function_1(self):
        self.isdone = 0
        try:
            self.log_message("Perintah: Memulai Get list data...")
            self.change_status("STATUS: Getting list data...", color="blue")
            
            if self.vwrite.get() == 1:
                mode = 'w'
            elif self.vwrite.get() == 0:
                mode = 'a'
            fungsi1_thread = threading.Thread(target=get_list_data, args=(self, "data.csv",mode))
            fungsi1_thread.start()
            #fungsi1_thread.join()  # Tunggu hingga thread selesai
        except Exception as e:
            self.isdone = 1
            self.log_message(f"ERROR: {e}...", tag="red_tag")
        # Mulai pengecekan berkala apakah sudah selesai
        self.check_isdone()

    # --- Function 2 ---
    def run_function_2(self):
        self.isdone = 0
        self.log_message("Perintah: Memulai proses approving...")
        self.change_status("STATUS: Running data...", color="blue")

        # Ambil input spesifik untuk Fungsi 2
        start_row = self.start_row_entry.get()
        filename = self.filename_entry.get()
        extra_input = self.extra_input_entry.get()

        # Validasi sederhana untuk baris mulai
        try:
            row_num = int(start_row)
            if row_num < 0:
                 raise ValueError
        except ValueError:
            self.isdone = 1
            self.change_status("STATUS: Running batal", color="blue")
            self.log_message(f"ERROR: Fungsi 2 dibatalkan. Baris Mulai '{start_row}' harus berupa angka positif.")
            return

        self.log_message(f"--- Detail Fungsi 2 ---")
        self.log_message(f"Baris Mulai: {row_num}")
        self.log_message(f"Nama File: {filename}")
        self.log_message(f"Input Tambahan: {extra_input}")

        if extra_input == "Input opsional..." or extra_input.strip() == "":
            self.log_message("Catatan: Tidak ada fungsi tambahan yang dipilih.")
            extra_input_fun = None 
        else:
            try:
                #import importlib
                external_funcs = load_setting_file(self)
                extra_input_fun = external_funcs.get(extra_input)
                self.log_message(f"Modul '{extra_input}' berhasil dimuat untuk fungsi tambahan.")
                #importlib.import_module(extra_input)
            #except ModuleNotFoundError:
            #    self.log_message(f"ERROR: Modul '{extra_input}' tidak ditemukan. Pastikan file .py ada di direktori yang sama.", tag="red_tag")
            #    return
            #except FileNotFoundError:
            #    self.log_message(f"ERROR: File '{extra_input}' tidak ditemukan di lokasi .exe.", tag="red_tag")
            except Exception as e:
                self.log_message( f"ERROR: Terjadi kesalahan saat import modul/file: {e}", tag="red_tag")

        try:
            #if extra_input == "getrandom":
            if self.v.get() == 99:
                #external_funcs = load_setting_file(self)
                #mainfunc = external_funcs.get('getrandom')
                fungsi2_thread = threading.Thread(target=extra_input_fun, args=(self,1))
            elif extra_input == "get_list_data" or extra_input == "mainfunc":
                self.log_message(f"ERROR: Fungsi 2 dibatalkan. Input tambahan invalid.")
                return
            else:
                if self.v.get() == 1:
                    cekapprove = True
                elif self.v.get() == 0:
                    cekapprove = False
                fungsi2_thread = threading.Thread(target=mainfunc, args=(self, filename, row_num, extra_input_fun, cekapprove))
            fungsi2_thread.start()
            #fungsi2_thread.join()  # Tunggu hingga thread selesai

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
            self.log_message(f"Running program berhasil diproses. Cek file output", tag="green_tag")
            self.change_status("STATUS: DONE! Running selesai", color="green")

if __name__ == '__main__':
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()

