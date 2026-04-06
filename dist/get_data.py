# konfig
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from argparse import Action
import pandas as pd
import time
#import importlib
import random
import os
import re

def help(instance,var):
    '''Get list of functions'''
    instance.isdone = 0
    instance.log_message(f"List of available functions:")

    for nama, objek in globals().items():
        if (callable(objek) and 
            not nama.startswith("__") and 
            nama not in ["mainfunc", "get_list_data", "update_temp_value","By", "WebDriverWait", "TimeoutException", "Keys", "EC", "Select", "Action", "datetime"] ):
            
            # Ambil docstring-nya, kalau kosong kasih teks default
            deskripsi = objek.__doc__ if objek.__doc__ else ""# "Tidak ada deskripsi."

            # print output
            instance.log_area.insert("end", f"[-]")
            instance.log_area.insert("end", f" {nama}" ,"red_tag")
            instance.log_area.insert("end", f" ({deskripsi.strip().lower()})\n")
            instance.log_area.see("end")

    instance.log_area.insert("end", "\n")
    instance.isdone = 1

def clear(instance, var):
    '''Clear log message'''
    # Hapus dari index '1.0' (awal) sampai 'end' (akhir)
    instance.isdone = 1
    instance.log_area.delete('1.0', "end")
    instance.log_message("Cleared! Aplikasi dimulai. Selamat datang!")
    if instance.vwrite.get() == 1:
        instance.log_message(f"Pilihan Write data.csv: Rewrite")
    else:
        instance.log_message(f"Pilihan Write data.csv: Append")
    if instance.v.get() == 1:
        instance.log_message(f"Pilihan approve: Ya, sekalian diapprove")
    else :
        instance.log_message(f"Pilihan approve: Gausa diapprove")

def gettime(instance, var):
    '''Get current time'''
    instance.isdone = 0
    #time.sleep(1)
    instance.log_message(f"Getting time...")
    instance.log_message(time.strftime("%H:%M:%S", time.localtime()) )
    instance.isdone = 1

def getrandom(instance, waktu): 
    '''Get a random number'''
    instance.isdone = 0
    time.sleep(int(waktu))
    instance.log_message(f"Hasil angka random {random.random()}")
    instance.isdone = 1

def getdata(instance, var):
    '''Get detail data pada csv dan index data terpilih [Pake "NonApprov" ya]'''
    instance.isdone = 0
    filename = instance.filename_entry.get()
    try:
        idx = int(instance.start_row_entry.get())
    except:
        idx = 0
    #time.sleep(1)
    instance.log_message(f"Getting detail data {filename} on index {idx}...")
    # GETTING DATA FROM FASIH OPEN DETAIL
    try:
        df = pd.read_csv(filename, sep=",")
        instance.log_message(f"\n{df.loc[idx]}")
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return
    instance.log_message("Done. Please enlarge the window")
    instance.isdone = 1


def getkurs(instance, var):
    '''Convert kurs data dari IDR.json hasil dari api web exchangerate-api.com [Pake "NonApprov"] [https://v6.exchangerate-api.com/v6/API-KEY/latest/IDR]'''
    instance.isdone = 0
    filename = instance.filename_entry.get()
    try:
        import json
        import csv
        # Membaca file JSON
        with open(filename, 'r') as f:
            data = json.load(f)

        if data["result"] == "success":
            rates = data["conversion_rates"]
            last_update = data["time_last_update_utc"]
            date_obj = datetime.strptime(data["time_last_update_utc"][:16].strip(), "%a, %d %b %Y")

            # Menulis ke file CSV
            with open('IDR.csv', 'w', newline='') as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow(["Info", f"Last Update: {last_update}"])
                writer.writerow(["kurs", date_obj.strftime("%B")])
                # write idr n usd first
                for code in ['IDR','USD']:
                    if code in rates:
                        # Rumus konversi balik karena base-nya IDR
                        rate_to_idr = 1 / rates[code]
                        writer.writerow([code, round(rate_to_idr, 2)])
                # other
                filteredkurs = [code for code in rates.keys() if code not in ["USD", "IDR"]]
                for code in filteredkurs:
                    if code in rates:
                        # Rumus konversi balik karena base-nya IDR
                        rate_to_idr = 1 / rates[code]
                        writer.writerow([code, round(rate_to_idr, 2)])
                
            instance.log_message(f"Selesai! Data rapi sudah ada di: IDR.csv")
        else:
            instance.log_message("Data JSON tidak valid.")
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return
    
    instance.log_message("Done. Please check the csv", tag="green_tag")
    instance.isdone = 1


def inputwebdash(instance, var):
    '''Input Webdash entri kegiatan, akan generate .json. Kalo udah dieksekusi, delete aja'''
    # FUNC MODDED FOR WEBDASH ENTRI KEGIATAN
    # cek if file ada, klo gada generate new, abistu delete deh klo dah diup
    import os
    import json

    if not os.path.exists("data-webdash.json"):
        # jika file tidak ada, buat file baru dengan struktur dasar
        dt = {
            "jeniskeg": ['Siaran Pers','Sensus dan Survey','Statistik Lain'],
            "tanggal": ['yyyy-mm-dd'],
            "image": ['E:/code/del.png'],
            "judul_ind": ['Lorem_Ipsum'],
            "rincian_ind": ['Lorem_ipsum.\n_dolot_sit_amet'],
            "tag": ['lorem, ipsum, dolor'],
        }
        with open('data-webdash.json', 'a') as f:
            f.write(json.dumps(dt, ensure_ascii=False, indent=4))
        instance.log_message("File data-webdash.json created. Silakan mengulangi program kembali", tag="green_tag")
        # back to top
        instance.isdone = 1
        return

    else:
        try:
            # jika ada, load file
            instance.log_message("File data-webdash.json already exists, skipping creation." )
            instance.log_message("Pastikan image sudah <150KB untuk upload webdash", tag="red_tag")
            time.sleep(2)
            instance.log_message("Loading file")
            with open('data-webdash.json', 'r') as file:
                dt = json.load(file)
            instance.log_message(str(dt))

            # cek image size
            def get_image_size_kb(image_path, limitsize_kb=150):
                """Mengembalikan ukuran file gambar dalam kilobyte (KB). Returns (size_kb, morelimit)"""
                if not os.path.exists(image_path):
                    #return f"File tidak ditemukan di: {image_path}"
                    return (0, True)
                
                # Dapatkan ukuran dalam byte
                size_bytes = os.path.getsize(image_path)
                size_kb = size_bytes / 1024

                # cek 150 kb
                morelimit = False
                if size_kb > limitsize_kb:
                    morelimit = True
                return (size_kb, morelimit) # Format 2 angka desimal

            # eksekusi cek size image
            sizekb, morelimit = get_image_size_kb(dt['image'][0])
            instance.log_message(f"Ukuran file {dt['image'][0]}: {sizekb:.2f} KB")
            if morelimit:
                instance.log_message(f"Ukuran file >150KB atau <0KB, silakan perbaiki dulu sebelum melanjutkan.", tag="red_tag")
                instance.isdone = 1
                return

            # eksekusi translate
            # buka gtranslate
            #driver.switch_to.new_window('tab')
            instance.driver.get('https://translate.google.com/?sl=id&tl=en&op=translate')
            time.sleep(2)

            # translate judul
            instance.driver.find_element(By.XPATH, "//textarea").clear()
            instance.driver.find_element(By.XPATH, "//textarea").send_keys(""+dt['judul_ind'][0])
            time.sleep(5) #tunggu translate
            dt['judul_eng'] = [instance.driver.find_element(By.XPATH, '//span[@lang="en"]').text]

            # translate rincian
            instance.driver.find_element(By.XPATH, "//textarea").clear()
            instance.driver.find_element(By.XPATH, "//textarea").send_keys(""+dt['rincian_ind'][0])
            time.sleep(5) #tunggu translate
            dt['rincian_eng'] = [instance.driver.find_element(By.XPATH, '//span[@lang="en"]').text]

            # cek result
            instance.log_message(dt)

            # eksekusi ngisi webdash
            instance.driver.get('https://webdash.web.bps.go.id/beritaTambah')
            try: #login sso 
                WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                    EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
                instance.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(instance.username_entry.get())
                instance.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(instance.password_entry.get())
                instance.driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
                WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                    EC.presence_of_element_located((By.XPATH, "//h4[@class='card-title']")) )
                #log_area.insert(tk.END, f"[{timestamp}] Login SSO ulang \n")
                #log_area.see(tk.END)
                instance.driver.get('https://webdash.web.bps.go.id/beritaTambah')
            except:
                pass

            # isi tanggal 
            instance.driver.get('https://webdash.web.bps.go.id/beritaTambah')
            time.sleep(2)
            instance.driver.get('https://webdash.web.bps.go.id/beritaTambah')
            instance.driver.execute_script("document.body.style.zoom='33%'")
            time.sleep(2)
            instance.driver.find_element(By.XPATH, "id('date')").send_keys(dt['tanggal'][0])
            instance.driver.find_element(By.XPATH, "id('date')").send_keys(Keys.RETURN)

            # isi jenis kegiatan
            instance.driver.find_element(By.XPATH, "id('jenis_kegiatan')").send_keys(""+dt['jeniskeg'][0])
            # isi image
            instance.driver.find_element(By.XPATH, "id('foto')").send_keys(dt['image'][0])

            # isi ind
            instance.driver.find_element(By.XPATH, "id('nav-indo-tab')").click()
            # isi judul_ind
            instance.driver.find_element(By.XPATH, "id('judul_ind_get')").send_keys(dt['judul_ind'][0])
            # isi rincian_ind
            instance.driver.find_element(By.XPATH, "id('rincian_ind')/div[@class='ql-editor ql-blank']").send_keys(dt['rincian_ind'][0])
            # isi eng
            instance.driver.find_element(By.XPATH, "id('nav-eng-tab')").click()
            # isi judul_eng
            instance.driver.find_element(By.XPATH, "id('judul_eng_get')").send_keys(dt['judul_eng'][0])
            # isi rincian_eng
            instance.driver.find_element(By.XPATH, "id('rincian_eng')/div[@class='ql-editor ql-blank']").send_keys(dt['rincian_eng'][0])

            # isi tag
            instance.driver.find_element(By.XPATH, "id('tags')").send_keys(dt['tag'][0])

            time.sleep (2)
            #driver.close()
            #driver.switch_to.window(driver.window_handles[0])

            instance.log_message("Data webdash sudah diisi semua, silakan dicek dan disubmit jika sudah benar.", tag="green_tag")
            instance.log_message("Silakan dihapus file-nya juga jika udah diupload: data-webdash.json")
            instance.isdone = 1
        except Exception as e:
            instance.log_message(f"Error: {str(e)}", "red_tag")
            instance.isdone=1
            return

def inputsbr(instance, var):
    '''Input data SBR dari file csv'''
    from pathlib import Path
    import numpy as np
    from selenium.common.exceptions import NoSuchElementException

    instance.isdone = 0
    driver = instance.driver

    try:
        # Login Matchapro
        driver.get("https://matchapro.web.bps.go.id/dirgc")
        try:
            driver.find_element("xpath", "//a[text()='Sign in with SSO BPS']").click()
            # time.sleep(1)
            driver.find_element("xpath", '//*[@id="username"]').send_keys(instance.username_entry.get()) #username sso
            driver.find_element("xpath", '//*[@id="password"]').send_keys(instance.password_entry.get()) #password sso
            driver.find_element("xpath", '//*[@id="kc-login"]').click()
        except: pass
        
        # cek modheader extension
        time.sleep(1)
        try:
            if driver.find_element("xpath", "//p[contains(text(),'Akses lewat matchapro mobile aja ya')]"):
                instance.log_message("# Anda belum mengaktifkan modheader, aktifin dulu manual di chromenya, abistu run ulang ya", tag="red_tag")
                instance.isdone = 1
                return
                #time.sleep(10)
        except: pass
        instance.log_message("# Modheader aktif, lanjut ke proses berikutnya...")
        driver.execute_script("document.body.style.zoom='33%'")
        
        # Baca Excel
        # cek file ada     
        nama_excel = instance.filename_entry.get()
        file_path = Path(nama_excel)
        if not file_path.exists():
            instance.log_message("# File tidak ditemukan, periksa kembali nama filenya", tag="red_tag")
            instance.isdone = 1
            return
        # read df
        #if file_path.suffix in ['.xls', '.xlsx']:
        if file_path.suffix == '.csv':
            instance.log_message("File found. Membaca data dari file csv...")
            #df = pd.read_excel(nama_excel, sheet_name="Sheet1")
            df = pd.read_csv(nama_excel)
        else:
            instance.log_message("# Format file salah, harus .csv", tag="red_tag")
            instance.isdone = 1
            return

        # read row file
        l1 = []
        for index, row in df.iterrows():
            l1.append(row.to_list())
        #print(l1)
        instance.log_message("Data dari csv dibaca, contoh 1 baris:")
        instance.log_message(str(l1[0]))
        time.sleep(2)

        if len(l1[0]) != 7:
            instance.log_message("# Format csv salah, harus 7 kolom: IDSBR, Nama, Lat, Lon, hasil_gc, hasil_input, user_sso", tag="red_tag")
            instance.log_message("# Perbaiki lalu run ulang")
            instance.isdone = 1
            return

        #Update di Matchapro
        try:
            no = int(instance.start_row_entry.get()) #0
        except:
            no = 0
        for x in l1:
            idsbr = x[0]
            nama = x[1]
            lat = x[2]
            lon = x[3]
            if np.isnan(lat): lat = ""
            if np.isnan(lon): lon = ""
            hasil_gc = x[4]
            hasil_input = x[5]
            user = x[6]
            # print(hasil_input)
            
            if hasil_input != "Berhasil" and user == instance.username_entry.get():
                #input IDSBR
                driver.find_element("xpath", '//div[@id="toggle-filter"]').click()
                time.sleep(2)
                driver.find_element("xpath", '//input[@id="search-idsbr"]').send_keys(Keys.CONTROL, 'a')
                driver.find_element("xpath", '//input[@id="search-idsbr"]').send_keys(idsbr)
                time.sleep(2)
                
                try:
                    # wait till loading ilang
                    time.sleep(2) #5
                    WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'blockUI blockMsg blockPage')))
                    WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'blockUI blockOverlay')))
                    WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'spinner-border')))
                    
                    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="usaha-card "]')))

                    # cek status gc
                    gc_badges = driver.find_elements(By.CSS_SELECTOR, ".usaha-card-title .gc-badge")
                    if len(gc_badges) > 0:
                        instance.log_message(f"{str(no+1)}. SBR {idsbr} dilewati karena sudah berstatus 'Sudah GC'dan Skip Ke IDSBR Selanjutnya")
                        time.sleep(2)
                        continue
                    driver.execute_script("document.body.style.zoom='33%'")
                    driver.find_element("xpath", '//div[@class="usaha-card "]').click()
                
                except NoSuchElementException:
                    instance.log_message(str(no+1)+". Gagal. "+str(idsbr)+" - "+str(nama)+" (Tidak ditemukan di Matchapro)")
                    time.sleep(1)
                    continue
                # time.sleep(1)
                driver.find_element("xpath", '//button[@class="btn-tandai"]').click()
                time.sleep(2)
                driver.find_element("xpath", '//select[@id="tt_hasil_gc"]').send_keys(hasil_gc)
                driver.find_element("xpath", '//input[@id="tt_latitude_cek_user"]').send_keys(lat)
                driver.find_element("xpath", '//input[@id="tt_longitude_cek_user"]').send_keys(lon)
                driver.find_element("xpath", '//button[@id="save-tandai-usaha-btn"]').click()
                time.sleep(3)

                if hasil_gc == 0:
                    driver.find_element("xpath", '//button[@class="swal2-confirm swal2-styled"]').click()
                    time.sleep(3)
            
                # simpan ke excel jika terdapat perubahan
                x[5] = "Berhasil"
                #kolom = pd.read_excel(nama_excel).columns
                kolom = pd.read_csv(nama_excel).columns
                df1 = pd.DataFrame(l1, columns=kolom)
                #df1.to_excel(nama_excel, sheet_name="Sheet1", index=False)
                df1.to_csv(nama_excel, index=False)
            
                no=no+1
                instance.log_message(str(no)+". Berhasil. "+str(idsbr)+" - "+str(nama))
            
                #driver.find_element("xpath", '//button[@class="swal2-confirm swal2-styled"]').click()
                # wait till loading ilang
                WebDriverWait(driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'spinner-border')))
                # wait till ada submit button
                WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="swal2-confirm swal2-styled"]')))
                WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                    EC.presence_of_element_located((By.XPATH, '//button[@class="swal2-confirm swal2-styled"]')) ).click()
            

        instance.log_message('SELESSEEEEEEEEEEEEEEEE', tag="green_tag")
        instance.isdone = 1
    
    except Exception as e:
        instance.log_message(f'Terjadi error: {e}', tag="red_tag")
        instance.isdone = 1

def update_temp_value(gagal=False):
    # Menentukan lokasi file temp (misal: 'temp.txt')
    path = os.path.join(os.getcwd(), 'temp.txt')
    
    # Baca nilai lama (default 0 jika file belum ada)
    val = int(open(path).read()) if os.path.exists(path) else 0
    #print(f"a={val}")
    
    # Update nilai: 0->1, 1->2, 2->0
    if not gagal:
        idxrand = (val + 1) % 3
    else:
        idxrand = val

    # Simpan kembali ke file temp
    with open(path, 'w') as f:
        f.write(str(idxrand))

def assignselect(instance, var): 
    '''Assign fasih-sm by selection, tapi upload dulu petugas ke fasih-sm, [Pake "NonApprov" ya]'''
    instance.isdone = 0
    driver = instance.driver
    # cek val counter di temp
    path = os.path.join(os.getcwd(), 'temp.txt')
    val = int(open(path).read()) if os.path.exists(path) else 0
    # cek var
    try:
        idx = int(instance.start_row_entry.get())
    except:
        idx = 0
    filename = instance.filename_entry.get()
    if instance.v.get() != 99:
        instance.log_message('Mohon maaf, fungsi ini sementara hanya bisa dipilih di NonApprov, walaupun memang di Fasih, tapi ikuti aja deh', "red_tag")
        instance.isdone = 1
        return
    # read csv
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return
    
    # A
    if val == 0: 
        instance.log_message("A.) TUTORIAL README", tag="red_tag")
        instance.log_area.insert("end", f"[-]","red_tag"); instance.log_area.insert("end", f" Upload petugas dan pengawas ke fasih-sm dulu agar bisa assign by selection\n")
        instance.log_area.insert("end", f"[-]","red_tag"); instance.log_area.insert("end", f" Masukkan email petugas dan pengawas di csv, tambahkan kolom 'ppl' dan 'pml', pastikan emailnya sama dengan yang di fasih-sm\n")
        instance.log_area.insert("end", f"[-] ", "red_tag"); instance.log_area.insert("end", f"Masukkan kolom ke berapa sebagai acuan di field 'Baris mulai', misal di csv ada kolom 'Kode ID'(1), 'NUS'(2), 'KRT'(3), dan kita akan pakai 'Kode ID' untuk search, dan kolom 'KRT' sebagai acuan, maka isi: 13\n")
        instance.log_area.insert("end", f"[-] ", "red_tag"); instance.log_area.insert("end", f"Pergi ke tab data di fasih-sm, jika sudah klik tombol RUN lagi\n")
        update_temp_value()

    # B
    elif val == 1: 
        instance.log_message("B.) CEK SAMPEL", tag="red_tag")
        # get kol usersaatini
        idxuser = df.columns.get_loc('User Saat ini')
        # get kol in fasih
        try:
            headusersaatini = driver.find_element(By.XPATH, f"id('assignmentDatatable')/thead/tr/td[{idxuser + 2}]").text
        except:
            instance.log_message(f'ERROR: {e}', tag="red_tag")
            instance.isdone = 1
            return
        #headusersaatini = 'GANTI OI'
        cek = 1
        # cek df
        if 'ppl' not in df.columns or 'pml' not in df.columns:
            instance.log_message("[-] Kolom 'ppl' dan 'pml' tidak ditemukan di csv. Pastikan sudah diisi dengan email yang sesuai di fasih-sm", tag="red_tag")
            df['ppl'] = '--'
            df['pml'] = '--'
            df.to_csv(filename, index=False)
            update_temp_value(gagal=True)
            cek = 0
        if len(str(idx)) > 2 or len(str(idx)) < 2:
            instance.log_message("[-] Nilai field 'Baris mulai' invalid. Pastikan angka sesuai.", tag="red_tag")
            update_temp_value(gagal=True)
            cek = 0
        # print sampel
        if cek == 1:
            idxpencari = int(str(idx)[0])-1
            idxacuan = int(str(idx)[1])-1
            instance.log_message(f"Menggunakan kolom '{df.columns[idxpencari]}' dan '{df.columns[idxacuan]}'")
            randsamp = len(df) if len(df)<6 else 6
            for i in random.sample(range(randsamp), 2):
                instance.log_area.insert("end", f"[-] Mencari: {str(df.iloc[i, idxpencari])} \n")
                instance.log_area.insert("end", f"[-] Acuan: {str(df.iloc[i, idxacuan])} (baris ke-{i}) \n")
                instance.log_area.insert("end", f"[-] Petugas: {str(df.iloc[i]['ppl'])}\n")
                instance.log_area.insert("end", f"[-] Pengawas: {str(df.iloc[i]['pml'])}\n")
                instance.log_area.insert("end", f"[-] User ({headusersaatini}): {str(df.iloc[i, idxuser])}\n\n")
            instance.log_area.insert("end", f"Jika benar maka klik RUN lagi, jika ada yang salah silakan delete file 'temp.txt' di folder aplikasi, lalu RUN ulang\n")
            update_temp_value()
    
    # C
    elif val == 2: 
        idxpencari = int(str(idx)[0])-1
        idxacuan = int(str(idx)[1])-1
        idxuser = df.columns.get_loc('User Saat ini')
        instance.log_message("C.) ASSIGNING", tag="red_tag")
        instance.driver.execute_script("document.body.style.zoom='50%'")
        # delete temp gajadi deh, nanti kalo reassign ulang biar ga repot
        #if os.path.exists(path):
        #    os.remove(path)        
        if 'assigned' not in df.columns:
            df['assigned'] = ""
        df['pml'] = df['pml'].apply(lambda x: x.split('@')[0] if '@bps.go.id' in x else x)
        
        # run here, apus inputsbr
        ## Assign
        start = 0 #perlu dicustom lagi si
        end = len(df)
        gagal = 0
        rowgada = 0
        count_gagal_sebelum_nyerah = 50 #perlu dicustom lagi si
        ## jika gagal loop terus :""
        listtimegagal = [] #untuk save time kegagalan
        listgagal = [] #untuk save index row yg gagal
        time.sleep(1)

        instance.log_message('Start assigning fasih --- ', tag="green_tag")
        while True:
            ## loop per row daftar_assign csv
            try:
                for dfrow in range(start,end): ## loop row df
                    ## Search by namalamat
                    now = datetime.now()
                    #instance.log_message(f"{df.index[dfrow]}/{len(df)} {str(df.iloc[dfrow, idxpencari])[:20]} , {str(df.iloc[dfrow, idxacuan])[:20]}")
                    instance.log_area.insert("end", f"[{now.strftime('%H:%M:%S')}] {df.index[dfrow]}/{len(df)} {str(df.iloc[dfrow, idxpencari])[:20]}, {str(df.iloc[dfrow, idxacuan])[:20]} ")
                    ## skip
                    if df.loc[dfrow, 'assigned'] == True or df.loc[dfrow, 'assigned'] == "True" or df.loc[dfrow, 'assigned']=="notfound" or str(df.loc[dfrow, 'assigned']).startswith('skip, assigned'):
                        instance.log_area.insert("end", f"| Skip\n")
                        instance.log_area.see("end")
                        continue
                    searchbar = driver.find_element(By.XPATH, 'id("assignmentDatatable_filter")/LABEL[1]/INPUT[1]')
                    searchbar.clear()
                    searchbar.send_keys(str(df.iloc[dfrow, idxpencari]), Keys.RETURN)
                    time.sleep(2)

                    ## match (nama DAFTAR SAMPEL.csv HARUS SAMA DENGAN DAFTAR SAMPEL FASIH)
                    try: 
                        ## cek ada isian row ato tidak
                        WebDriverWait(driver, 5).until( #using explicit wait for x seconds
                            EC.presence_of_element_located((By.XPATH, 'id("assignmentDatatable")/TBODY/TR[1]/TD[3]')) )
                        pass
                    except: 
                        ## jika kosong maka CONT
                        instance.log_area.insert("end", f"| kosong\n")
                        instance.log_area.see("end")
                        df.loc[df.index[dfrow], 'assigned'] = 'notfound'
                        df.to_csv(filename, index=False)
                        continue
                        
                    ## Jumlah row yang ditampilin di fasih
                    #jml_row = 10+1
                    jml_row = int(driver.find_element(By.CSS_SELECTOR, 'div#assignmentDatatable_info').text.split()[3]) + 1
                    
                    for i in range(1,jml_row): ## loop row fasih, cek row yang diinginkan                
                        id_web = driver.find_element(By.XPATH, f"id('assignmentDatatable')/tbody/tr/td[{idxpencari + 2}]").text + \
                            driver.find_element(By.XPATH, f"id('assignmentDatatable')/tbody/tr/td[{idxacuan + 2}]").text
                        usersaatini = driver.find_element(By.XPATH, f"id('assignmentDatatable')/tbody/tr/td[{idxuser + 2}]").text
                        #driver.find_element_by_xpath('id("assignmentDatatable")/TBODY[2]/TR['+i+']/TD[5]').text()

                        ## cek kesamaan
                        if (str(df.loc[dfrow, df.columns[idxpencari]])+str(df.loc[dfrow, df.columns[idxacuan]]) == id_web):
                            #print('== ')
                            rowgada = 0 #lanjut karna dah nemu yang sama
                            break #break loop row fasih
                        else:
                            rowgada = 1 #akan next loop
                            pass
                    ## jika gada row yang sama maka CONT next loop,
                    if (rowgada == 1):
                        instance.log_area.insert("end", f"| ganemu, mungkin kosong\n")
                        instance.log_area.see("end")
                        df.loc[df.index[dfrow], 'assigned'] = 'notfound'
                        df.to_csv(filename, index=False)
                        continue
                    ## cek row matching and tick jika user saat ini masi ()
                    tick = 0
                    if (usersaatini !='()'): 
                        ## jika dah ke assign maka CONT
                        instance.log_area.insert("end", f"| skip dah ke assign ke {usersaatini}\n")
                        instance.log_area.see("end")
                        df.loc[df.index[dfrow], 'assigned'] = f'skip, assigned ke {usersaatini}'
                        df.to_csv(filename, index=False)
                        continue #next loop row df
                    else:
                        tick = 1
                        ## tick centang buat select by assign
                        driver.find_elements(By.CSS_SELECTOR, '.ng-star-inserted:nth-child('+str(i)+') > td > .ng-untouched')[0].click()
                        #.ng-star-inserted:nth-child(2) > td > .ng-untouched

                    ## dropdown assign
                    driver.find_elements(By.CSS_SELECTOR,'.btn-group:nth-child(3) > .dropdown-toggle')[0].click() #dropdown assign button
                    driver.find_elements(By.CSS_SELECTOR, '.show > .dropdown-item:nth-child(1)')[0].click() #pilihan assign by selection
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, "//BODY/NGB-MODAL-WINDOW[1]/DIV[1]/DIV[1]/APP-MODAL-ASSIGN[1]/DIV[2]/DIV[1]/DIV[1]/NGX-SELECT[1]/DIV[1]/DIV[2]/DIV[1]")) #finding the element
                    )
                    time.sleep(1.2)
                    ## assign pengawas
                    driver.find_elements(By.CSS_SELECTOR, '.form-group:nth-child(1) > .col-md-6 .ngx-select__toggle')[0].click()
                    driver.find_elements(By.CSS_SELECTOR, 'input.ngx-select__search')[0].send_keys( df.iloc[dfrow]['pml'] )
                    time.sleep(1.2)
                    driver.find_elements(By.CSS_SELECTOR, 'a.ngx-select__item')[0].click()
                    time.sleep(1)
                    ## assign petugas
                    driver.find_elements(By.CSS_SELECTOR, '.form-group:nth-child(2) > .col-md-6 .ngx-select__toggle')[0].click()
                    driver.find_elements(By.CSS_SELECTOR, 'input.ngx-select__search')[0].send_keys( df.iloc[dfrow]['ppl'])
                    time.sleep(1)
                    driver.find_elements(By.CSS_SELECTOR, 'a.ngx-select__item')[0].click()
                    ## konfirm ok assign 
                    #driver.find_elements_by_css_selector('button.btn-primary:nth-child(1)')[0].send_keys(Keys.RETURN) 
                    ## klik assign btn
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary:nth-child(1)")) #assign btn
                    ).click()
                    ## klik konfirmasi 
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        #EC.presence_of_element_located((By.XPATH, "//BODY/DIV[2]/DIV[1]/DIV[6]/BUTTON[1]")) #konfirmasi
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm")) #konfirmasi
                    ).click()
                    
                    ## jika gamau ilang modalnya setelah konfirm
                    try:
                        time.sleep(1)
                        WebDriverWait(driver, 10).until( #using explicit wait for x seconds
                            EC.presence_of_element_located((By.XPATH, "//button[@class='swal2-close']"))
                            #EC.presence_of_element_located((By.CSS_SELECTOR, "button.swal2-close")) #close berhasil tapi error jika ada
                        ).click()
                        ## close modal selection petugas
                        # SOMEHOW INI KESKIP, JADI BLM NUTUP MODALNYA
                        ##
                        driver.find_elements(By.CSS_SELECTOR, 'button.close')[0].click()
                        status_msg = WebDriverWait(driver,2).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "ngb-modal-window.modal")))
                        Action.move_to_element(status_msg).perform()
                        status_msg.find_element_by_css_selector("button.close").click()
                    except: pass
                    
                    if (tick == 1): #then untick
                        # replace demgam metode tick all then untick all
                        driver.find_element(By.NAME, 'selectAllId').click(); time.sleep(0.2) #tick all
                        driver.find_element(By.NAME, 'selectAllId').click(); time.sleep(0.2) #untick all
                        tick = 0
                    #print(f'{df.index[dfrow]}| sukses assign ke '+df.email_petugas[dfrow])
                    ## write log
                    df.loc[df.index[dfrow], 'assigned'] = True
                    instance.log_area.insert("end", f"| Done\n")
                    instance.log_area.see("end")
                    df.to_csv(filename, index=False)

                instance.log_message('SLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEESE')
                break
                            
            ## jika gagal print error
            except Exception as e:
                instance.log_message('Error terjadi: '+str(e).split("Stacktrace:")[0], tag="red_tag")
                listtimegagal.append(now)
                listgagal.append(df.index[dfrow])
                start = dfrow-1
                if start <0: start = 0
                gagal += 1
                instance.log_message(f'Gagal: {str(gagal)}, 6 list index gagal: {listgagal}', tag="red_tag")
                ## lemme ngitung diff time each attempt yang gagal. 
                ## 7annya cuman pengen kalo 5x attempt gagal waktunya cuman < 3s maka BREAK, biar ga lama2 sampe 100 baru break
                #difftime = 4
                if len(listtimegagal)>5:
                    listtimegagal.pop(0) #remove timegagal index pertama
                    listgagal.pop(0) #remove index row yang pertama yg gagal
                    diff = listtimegagal[4]-listtimegagal[0] #itung delta time
                    #difftime = divmod(diff.days * seconds_in_day + diff.seconds, 1)[0]
                    difftime = diff.seconds
                else: difftime = 4
                
                if(len(set(listgagal))==1 and len(listgagal)>4): #jika gagal lebih dari 4x di index row itu, maka skip aja da
                    df.loc[df.index[dfrow], 'assigned'] = 'error'
                    start = dfrow+1
                    instance.log_message('Continuing aja')
                    continue 

                if ((gagal > count_gagal_sebelum_nyerah) or (difftime<3) ): # jika gagal lebih dari threshold maka errorin aja OR !! jika different time gagalnya gagal maka remove aja OR blabla nya
                    #Audio(sound_file, autoplay=True)
                    instance.log_message("WARN: Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e), tag="red_tag")
                    raise Exception("Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))

                if gagal%3 == 0 : #jika gagal 3x reload trs run ulang
                    instance.log_message('Refreshing', tag="green_tag")
                    driver.refresh()
                    time.sleep(5)
                    instance.driver.execute_script("document.body.style.zoom='50%'")
                    ########
                    ## !! Komen di bawah ini perlu jika tiap refresh bulan surveinya berbeda. or apalah ketentuannya
                    ########
                    instance.log_message("Periode Survei benar?: "+str( Select(driver.find_element(By.CSS_SELECTOR, 'select.custom-select')).first_selected_option.text ), tag="green_tag")
                    # show 100 row
                    try:
                        selectshow=Select(driver.find_element(By.XPATH, 'id("assignmentDatatable_length")/LABEL[1]/SELECT[1]'))
                        selectshow.select_by_index(3)
                    except:
                        pass
                    time.sleep(5)
                    instance.log_message("Restart lagi at row: "+str(start))
                    WebDriverWait(driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'td.sorting_disabled:nth-child(2)')) )
                    continue

                    
                instance.log_message("Restart lagi at row: "+str(start))
                continue
            
        # end run
        #df.to_csv(str(this_path)+"/log "+df_name)
        #instance.log_message('Log result hasil dapat diliat di '+str(this_path)+"/log "+df_name)
        #return("Program selesai di jalankan. NOTE!!!!! Kalo download result, bakalan langsung ke page home", df)
        df.to_csv(filename, index=False)
    instance.isdone = 1

def getdataPES(instance):
    '''FUNCTION FOR GETTING DATA PES'''
    try:
        #instance.log_message("Masuk ke fungsi get data PES")
        driver = instance.driver
        # list id blok 4
        ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
        # init a dict for data
        col_list = \
            [f"r{i}" for i in range(1,6)] + \
            ["r5b"] + [f"r{i}" for i in range(6,9)] + ["r9aa","r9ac"] + \
            [f"r9b{j}" for j in range(1,6)] + [f"r9b{j}c" for j in range(1,6)] + \
            [f"r10.{j}.1" for j in range(1,14)] + \
            [f"r10.{j}.2" for j in range(1,14)] + \
            [f"r11.{j}" for j in range(1,5)] + ['r12'] + ids4 + \
            [f"r{i}" for i in range(14,18)] + \
            [f"r18a_{k}" for k in ['arrival','departure']] + [f"r18b_{k}" for k in ['arrival','departure']] + [f"r18c_{k}" for k in ['arrival','departure']] + \
            [f"r19_{j}" for j in range(1,15)] +\
            [f"r{i}" for i in range(20,26)]
        d = dict.fromkeys(col_list, '--')
        #5b,9ac,9b[1,6],9b[1,6]c,10.[1,13], 11.[1,5], ids4, r18[a,b,c]_[arrival,departure], r19_[1,15], 

        # BLOK1, click tab di sidebar
        blok = 1
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        # wait biar isiannya muncul dulu
        WebDriverWait(driver, 10).until(
            #EC.text_to_be_present_in_element((By.XPATH, f"//div[@id='nationality']//button/div"), "[") )
            lambda d: d.find_element(By.XPATH, "//div[@id='nationality']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='city_residence']//button/div").text.strip() != "")
        #
        d['r1'] = driver.find_element(By.XPATH, "//div[@id='name']//input[@type='text']").get_attribute('value')
        d['r2'] = driver.find_element(By.XPATH, "//div[@id='age']//input[@type='text']").get_attribute('value')
        radios3 = driver.find_elements(By.XPATH, f"//div[@id='sex']//input[@type='radio']")
        for r in radios3:
            if r.is_selected(): break
        d['r3'] = r.get_attribute('value')
        d['r4'] = driver.find_element(By.XPATH, "//div[@id='nationality']//button/div").text #for input dropdown
        d['r5'] = driver.find_element(By.XPATH, "//div[@id='country_residence']//button/div").text
        d['r5b'] = driver.find_element(By.XPATH, "//div[@id='city_residence']//button/div").text
        radios6 = driver.find_elements(By.XPATH, f"//div[@id='main_purpose']//input[@type='radio']")
        for r in radios6:
            if r.is_selected(): break
        d['r6'] = r.get_attribute('value')

        # BLOK2
        blok = 2
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        # wait biar isiannya muncul dulu
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//div[@id='port_entry']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='main_destination_kab']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='other_destination_prov_1']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='other_destination_prov_2']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='other_destination_prov_3']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='other_destination_prov_4']//button/div").text.strip() != ""
        )
        #
        d['r7'] = driver.find_element(By.XPATH, "//div[@id='port_entry']//button/div").text #dropdown
        d['r8'] = driver.find_element(By.XPATH, "//div[@id='length_of_stay']//input[@type='text']").get_attribute('value')
        # main dest
        #d['r9'] = driver.find_element(By.XPATH, "//div[@id='main_destination_prov']//button/div").text
        d['r9aa'] = driver.find_element(By.XPATH, "//div[@id='main_destination_kab']//button/div").text
        d['r9ac'] = driver.find_element(By.XPATH, "//div[@id='len_stay_main_dest']//input[@type='text']").get_attribute('value')
        # other dest
        for i in range (1,6):
            a = driver.find_element(By.XPATH, f"//div[@id='other_destination_prov_{i}']//button/div").text
            if a == 'Select an option': continue
            d[f"r9b{i}"] = driver.find_element(By.XPATH, f"//div[@id='other_destination_kab_{i}']//button/div").text
            d[f"r9b{i}c"] = driver.find_element(By.XPATH, f"//div[@id='len_stay_other_dest_{i}']//input[@type='text']").get_attribute('value')
        
        # BLOK3
        # get radio: tourism_attraction_05
        blok = 3
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        
        for i in range(1,14):
            # get radio value
            radios10 = driver.find_elements(By.XPATH, f"//div[@id='tourism_attraction_{i:02}']//input[@type='radio']")
            for r in radios10:
                if r.is_selected(): break
            # jika ada terpilih
            if r.get_attribute('value') == '1':
                d[f"r10.{i}.2"] = driver.find_element(By.XPATH, f"//div[@id='len_stay_tourism_{i}']//input[@type='text']").get_attribute('value')
            d[f"r10.{i}.1"] = r.get_attribute('value')
            
            # for switch
            #d[f"r10.{i}"] = driver.find_element(By.XPATH, f"//div[@id='tourism_attraction_{i:02}']//input[@type='checkbox']").is_selected()

        #BLOK4
        blok = 4
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        # tidak semua datanya diambil sih
        for i in range(1,5):
            radios12 = driver.find_elements(By.XPATH, f"//div[@id='accommodation_{i:02}']//input[@type='radio']")
            for r in radios12:
                if r.is_selected(): break
            d[f"r11.{i}"] = r.get_attribute('value')
            #d[f"r11.{i}"] = driver.find_element(By.XPATH, f"//div[@id='accommodation_{i:02}']//input[@type='checkbox']").is_selected()
        radios12 = driver.find_elements(By.XPATH, f"//div[@id='use_tour_package']//input[@type='radio']")
        for r in radios12:
            if r.is_selected(): break
        d[f"r12"] = r.get_attribute('value')

        #BLOK5
        blok = 5
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        # wait biar isiannya muncul dulu
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//div[@id='currency_spending']//button/div").text.strip() != ""
        )
        #
        ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
        for id4 in ids4:
            #try:
            if id4 == 'currency_spending':
                d[id4] = driver.find_element(By.XPATH, f"//div[@id='{id4}']//button/div").text 
            else: d[id4] = driver.find_element(By.XPATH, f"//div[@id='{id4}']//input[@type='text']").get_attribute('value')

        #BLOK6
        blok = 6
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        # wait biar isiannya muncul dulu
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//div[@id='airline_departure']//button/div").text.strip() != "" and
                    d.find_element(By.XPATH, "//div[@id='airline_arrival']//button/div").text.strip() != ""
        )
        #
        radios14 = driver.find_elements(By.XPATH, f"//div[@id='main_occupation']//input[@type='radio']")
        for r in radios14:
            if r.is_selected(): break
        d['r14'] = r.get_attribute('value')
        # r15 skip 
        d['r16'] = driver.find_element(By.XPATH, "//div[@id='freq_visit']//input[@type='text']").get_attribute('value')
        #
        for i in ['arrival', 'departure']:
            d[f'r18a_{i}'] = driver.find_element(By.XPATH, f"//div[@id='airline_{i}']//button/div").text 
            d[f'r18b_{i}'] = driver.find_element(By.XPATH, f"//div[@id='currency_{i}']//button/div").text 
            d[f'r18c_{i}'] = driver.find_element(By.XPATH, f"//div[@id='value_{i}']//input[@type='text']").get_attribute('value') 

        #BLOK7
        blok = 7
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        #
        # get switch: activities_06
        for i in range(1,15):
            radios19 = driver.find_elements(By.XPATH, f"//div[@id='activities_{i:02}']//input[@type='radio']")
            for r in radios19:
                if r.is_selected(): break
            d[f'r19_{i}'] = r.get_attribute('value')
            #d[f'r19_{i}'] = driver.find_element(By.XPATH, f"//div[@id='activities_{i:02}']//input[@type='checkbox']").is_selected()
        radios20 = driver.find_elements(By.XPATH, f"//div[@id='wonderful_indonesia']//input[@type='radio']")
        for r in radios20:
            if r.is_selected(): break
        d['r20'] = r.get_attribute('value')
        #
        radios21 = driver.find_elements(By.XPATH, f"//div[@id='ecofriendly_principle']//input[@type='radio']")
        for r in radios21:
            if r.is_selected(): break
        d['r21'] = r.get_attribute('value')
        #
        radios22 = driver.find_elements(By.XPATH, f"//div[@id='satisfaction_lvl']//input[@type='radio']")
        for r in radios22:
            if r.is_selected(): break
        d['r22'] = r.get_attribute('value')
        #
        radios23 = driver.find_elements(By.XPATH, f"//div[@id='intention_to_visit']//input[@type='radio']")
        for r in radios23:
            if r.is_selected(): break
        d['r23'] = r.get_attribute('value')

        #BLOK8
        blok = 8
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        #
        d['r24'] = driver.find_element(By.XPATH,f"//div[@id='note']//textarea").get_attribute('value')
        d['r25'] = driver.find_element(By.XPATH,f"//div[@id='impression']//textarea").get_attribute('value')
    except Exception as e:
        instance.log_message(f'Terjadi error: {e}')

    # FINISH
    return d

def getdataSAKpemut(instance):
    '''FUNCTION FOR GETTING DATA Sakernas pemutakhiran'''
    try:
        #instance.log_message("Masuk ke fungsi get data PES")
        driver = instance.driver
        # init a dict for data
        col_list = ['keberadaan','usaha','tagging','catatan']
        d = dict.fromkeys(col_list, '--')

        # BLOK2
        blok = 2
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        # cek keberadaan ruta
        time.sleep(1)
        radios = driver.find_elements(By.XPATH, f'//div[@id="r506"]//input[@type="radio"]')
        for r in radios:
            if r.is_selected(): break
        keberadaan = r.get_attribute('value')
        d['keberadaan'] = keberadaan
        if keberadaan == '3':
            try:
                # BLOK3
                blok = 3
                driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
                valcatatan = driver.find_element(By.XPATH,f"//div[@id='catatan']//textarea").get_attribute('value') or ""
            except:
                valcatatan = "Error getting catatan value"
                pass
            d['catatan'] = f"{valcatatan} | Responden tidak ditemukan di alamat sesuai ruta"
            instance.log_message("Tidak ditemukan ruta, lanjut ke loop berikutnya")
            return d # skip ke loop berikutnya

        # wait biar isiannya muncul dulu
        WebDriverWait(driver, 10).until(
            #EC.text_to_be_present_in_element((By.XPATH, f"//div[@id='nationality']//button/div"), "[") )
            lambda d: d.find_element(By.XPATH, "//div[@id='tagging']//input[@type='text']").get_attribute('value') != "")
        #
        d['tagging'] = driver.find_element(By.XPATH, "//div[@id='tagging']//input[@type='text']").get_attribute('value')
        radios = driver.find_elements(By.XPATH, f"//div[@id='usaha']//input[@type='radio']")
        for r in radios:
            if r.is_selected(): break
        d['usaha'] = r.get_attribute('value')

        # BLOK3
        blok = 3
        driver.find_element(By.XPATH, f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
        d['catatan'] = driver.find_element(By.XPATH,f"//div[@id='catatan']//textarea").get_attribute('value')
        
    except Exception as e:
        instance.log_message(f'Terjadi error: {e}')

    # FINISH
    return d

# Function reject data Fasih
def reject(instance, var, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=','):
    #(instance, filename, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=',')
    '''Reject di fasih-sm berdasarkan file yang dipilih'''
    # konfig
    import sys
    instance.isdone = 0
    filename = instance.filename_entry.get()
    if instance.v.get() != 99:
        instance.log_message('Mohon maaf, fungsi ini sementara hanya bisa dipilih di NonFasih, walaupun memang di Fasih, tapi ikuti aja deh', "red_tag")
        instance.isdone = 1
        return
    # GETTING DATA FROM FASIH OPEN DETAIL
    try:
        df = pd.read_csv(filename, sep=sep)
        if 'approved' not in df.columns:
            df['approved'] = ""
        # Get all window handles & Switch to the first window (index 0)
        all_window_handles = instance.driver.window_handles
        instance.driver.switch_to.window(all_window_handles[0])
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return

    instance.log_message(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data and rejecting in 5sec...")
    time.sleep(5)

    if mulai <0 : i=-1
    else: i = mulai-1
    while True: 
        instance.isdone = 0
        # Pastikan tampilan menggulir ke bagian paling bawah
        #instance.log_area.see(tk.END)
        #timestamp = datetime.now().strftime("%H:%M:%S")
        i += 1
        if i >= len(df):
            #printwarn("# DONEEE ---------------------------------", color='red', font_weight='bold', font_size="30px")
            instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
            #change_text(label_status, f"Running Selesai {adaerr}", "green")
            break
        try:
            # CEK DAH EKSEKUSI LOM ke0 ------------------------------------------------------------
            if df.loc[i, 'approved'] == 'REJECTED':
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Dah dieksekusi, skip")
                continue

            ## goto web
            instance.driver.get(df.link[i])
            instance.driver.execute_script("document.body.style.zoom='50%'")
            #change_text(label_status, f"Processin data {i}/{len(df)}")
                  

            ## click btn review
            time.sleep(3)
            WebDriverWait(instance.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-primary")) ).click()
            ## wait till loading nya ilang
            time.sleep(2) #5
            WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(2) #3
            WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))
            instance.driver.execute_script("document.body.style.zoom='50%'")

            # CEK DAH APPROVED LOM ke1 ------------------------------------------------------------
            try:
                #try revoke
                try:
                    WebDriverWait(instance.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, 'id("buttonRevoke")'))
                    )
                    btn_approve = instance.driver.find_element(By.XPATH,'id("buttonRevoke")')
                    #btn_approve.location_once_scrolled_into_view
                    btn_approve.click()
                    #konfirmasi
                    instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                    time.sleep(1)
                    try:
                        instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                        time.sleep(1)
                    except: pass
                
                except: pass

                # refresh
                instance.driver.refresh()
                ## wait till loading nya ilang
                time.sleep(2) #5
                WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
                ## wait till rendering form
                instance.driver.execute_script("document.body.style.zoom='50%'")
                time.sleep(2) #3
                WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

                # reject
                WebDriverWait(instance.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, 'id("buttonReject")'))
                )
                btn_approve = instance.driver.find_element(By.XPATH,'id("buttonReject")')
                #btn_approve.location_once_scrolled_into_view
                btn_approve.click()
                #konfirmasi
                instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                time.sleep(1)
                try:
                    instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                    time.sleep(1)
                except: pass


            except TimeoutException:
                #print("# Approve button not found or not loaded yet")
                #print(i,df[idlog][i],'| Not Found Approve button, skip')
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Not Found the button, skip", "red_tag")
                # logging
                df.loc[i, 'approved'] = 'REJECTED'
                df.to_csv(filename, index=False)
                continue
            
            # end result if success
            df.loc[i, 'approved'] = 'REJECTED'
            df.to_csv(filename, index=False)

        except Exception as e:
            # coba refresh n login ulang
            # Login SSO
            try:
                if 'Server Not Found' in instance.driver.title: 
                    #print('# Error server not found, CEK VPN -------------------------------------------')
                    instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
                    #change_text(label_status, "Error, CEK VPN", "red")
                    break
                #driver.refresh()
                instance.driver.get(df.link[i])
                #i -= 1
                if i < -1: i=-1
                #print(f'# error {str(e)}, reloading')
                instance.log_message(f"# Terjadi error: ")
                instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                #change_text(label_status, "Running ERROR", "red")
                try:
                    WebDriverWait(instance.driver, 10).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
                    ).click()
                    # input SSO
                    WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
                    instance.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(instance.username_entry.get())
                    instance.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(instance.password_entry.get())
                    instance.driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
                    WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, 'id("Pencacahan")/TBODY[1]/TR[4]/TD[1]/A[1]')) )
                    #print('# login sso ulang')
                    instance.log_message(f"# Login SSO ulang ")
                    adaerr = ""
                except:
                    pass
                continue
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                #print(f"{i,df[idlog][i]} | Err: {str(exc_tb.tb_lineno)} | {str(e)}"  ) 
                #printwarn(f"{i,df[idlog][i]} | Err: {str(exc_tb.tb_lineno)} | {str(e)}", color='red', font_weight='bold', font_size="30px")
                instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
                instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                #change_text(label_status, "Running ERRORRR", "red")
                continue
        
        # jika satu row dah selesai, entah error or sukses    
        #print(i,df[idlog][i],'| Done')
        instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Done")
        #instance.log_message.yview_moveto(1.0)
        continue

    instance.isdone = 1


# Function reject data Fasih
def reject(instance, var, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=','):
    #(instance, filename, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=',')
    '''Reject di fasih-sm berdasarkan file yang dipilih'''
    # konfig
    import sys
    instance.isdone = 0
    filename = instance.filename_entry.get()
    if instance.v.get() != 99:
        instance.log_message('Mohon maaf, fungsi ini sementara hanya bisa dipilih di NonApprov, walaupun memang di Fasih, tapi ikuti aja deh', "red_tag")
        instance.isdone = 1
        return
    # GETTING DATA FROM FASIH OPEN DETAIL
    try:
        df = pd.read_csv(filename, sep=sep)
        if 'approved' not in df.columns:
            df['approved'] = ""
        # Get all window handles & Switch to the first window (index 0)
        all_window_handles = instance.driver.window_handles
        instance.driver.switch_to.window(all_window_handles[0])
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return

    instance.log_message(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data and rejecting in 5sec...")
    time.sleep(5)

    if mulai <0 : i=-1
    else: i = mulai-1
    while True: 
        instance.isdone = 0
        # Pastikan tampilan menggulir ke bagian paling bawah
        #instance.log_area.see(tk.END)
        #timestamp = datetime.now().strftime("%H:%M:%S")
        i += 1
        if i >= len(df):
            #printwarn("# DONEEE ---------------------------------", color='red', font_weight='bold', font_size="30px")
            instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
            #change_text(label_status, f"Running Selesai {adaerr}", "green")
            break
        try:
            # CEK DAH EKSEKUSI LOM ke0 ------------------------------------------------------------
            if df.loc[i, 'approved'] == 'REJECTED':
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Dah dieksekusi, skip")
                continue

            ## goto web
            instance.driver.get(df.link[i])
            instance.driver.execute_script("document.body.style.zoom='50%'")
            #change_text(label_status, f"Processin data {i}/{len(df)}")
                  

            ## click btn review
            time.sleep(3)
            WebDriverWait(instance.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-primary")) ).click()
            ## wait till loading nya ilang
            time.sleep(2) #5
            WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(2) #3
            WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))
            instance.driver.execute_script("document.body.style.zoom='50%'")

            # CEK DAH APPROVED LOM ke1 ------------------------------------------------------------
            try:
                #try revoke
                try:
                    WebDriverWait(instance.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, 'id("buttonRevoke")'))
                    )
                    btn_approve = instance.driver.find_element(By.XPATH,'id("buttonRevoke")')
                    #btn_approve.location_once_scrolled_into_view
                    btn_approve.click()
                    #konfirmasi
                    instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                    time.sleep(1)
                    try:
                        instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                        time.sleep(1)
                    except: pass
                
                except: pass

                # refresh
                instance.driver.refresh()
                ## wait till loading nya ilang
                time.sleep(2) #5
                WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
                ## wait till rendering form
                instance.driver.execute_script("document.body.style.zoom='50%'")
                time.sleep(2) #3
                WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

                # reject
                WebDriverWait(instance.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, 'id("buttonReject")'))
                )
                btn_approve = instance.driver.find_element(By.XPATH,'id("buttonReject")')
                #btn_approve.location_once_scrolled_into_view
                btn_approve.click()
                #konfirmasi
                instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                time.sleep(1)
                try:
                    instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                    time.sleep(1)
                except: pass


            except TimeoutException:
                #print("# Approve button not found or not loaded yet")
                #print(i,df[idlog][i],'| Not Found Approve button, skip')
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Not Found the button, skip", "red_tag")
                # logging
                df.loc[i, 'approved'] = 'REJECTED'
                df.to_csv(filename, index=False)
                continue
            
            # end result if success
            df.loc[i, 'approved'] = 'REJECTED'
            df.to_csv(filename, index=False)

        except Exception as e:
            # coba refresh n login ulang
            # Login SSO
            try:
                if 'Server Not Found' in instance.driver.title: 
                    #print('# Error server not found, CEK VPN -------------------------------------------')
                    instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
                    #change_text(label_status, "Error, CEK VPN", "red")
                    break
                #driver.refresh()
                instance.driver.get(df.link[i])
                #i -= 1
                if i < -1: i=-1
                #print(f'# error {str(e)}, reloading')
                instance.log_message(f"# Terjadi error: ")
                instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                #change_text(label_status, "Running ERROR", "red")
                try:
                    WebDriverWait(instance.driver, 10).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
                    ).click()
                    # input SSO
                    WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
                    instance.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(instance.username_entry.get())
                    instance.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(instance.password_entry.get())
                    instance.driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
                    WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, 'id("Pencacahan")/TBODY[1]/TR[4]/TD[1]/A[1]')) )
                    #print('# login sso ulang')
                    instance.log_message(f"# Login SSO ulang ")
                    adaerr = ""
                except:
                    pass
                continue
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                #print(f"{i,df[idlog][i]} | Err: {str(exc_tb.tb_lineno)} | {str(e)}"  ) 
                #printwarn(f"{i,df[idlog][i]} | Err: {str(exc_tb.tb_lineno)} | {str(e)}", color='red', font_weight='bold', font_size="30px")
                instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
                instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                #change_text(label_status, "Running ERRORRR", "red")
                continue
        
        # jika satu row dah selesai, entah error or sukses    
        #print(i,df[idlog][i],'| Done')
        instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Done")
        #instance.log_message.yview_moveto(1.0)
        continue

    instance.isdone = 1


# Function to get list data
def get_list_data(instance, namadf,  mode="w", maxrow=0, sep=","):
    '''Get dataframe dari prelist link fasih untuk dijadikan bahan, kemudian export ke csv juga'''
    instance.isdone = 0
    try:
        # Get all window handles & Switch to the first window (index 0)
        all_window_handles = instance.driver.window_handles
        instance.driver.switch_to.window(all_window_handles[0])
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return
    # get header dataframe
    headdf = []
    for i in instance.driver.find_elements(By.XPATH, 'id("assignmentDatatable")/THEAD/TR[1]/TD'):
        if i.text!='': headdf.append(i.text)
    df = dict.fromkeys(headdf, [])
    df['link'] = []
    # make dataframe df
    df = pd.DataFrame(df)
    #timestamp = datetime.now().strftime("%H:%M:%S")

    # get max row and number of row in current page
    if maxrow==0:
        maxrow = int(instance.driver.find_element(By.XPATH, 'id("assignmentDatatable_info")').text.split()[5].replace(",","")) 
    #maxrow = 11 ## buat coba2
    rowpage = int(instance.driver.find_element(By.XPATH, 'id("assignmentDatatable_info")').text.split()[3].replace(",","")) 
    #print("# Gettin number row data: ",maxrow)
    instance.log_message(f"# Gettin number row data: {maxrow}")
    #change_text(label_status, "Running Selesai", "green")

    # loop per row
    satuloop=False
    if rowpage == maxrow: 
        maxrow +=1
        satuloop=True
    while rowpage < maxrow:
        #timestamp = datetime.now().strftime("%H:%M:%S")
        # wait till load
        time.sleep(2)
        WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.XPATH, 'id("assignmentDatatable_processing")')) )
        
        # getting number of row in current page
        rowpage = int(instance.driver.find_element(By.XPATH, 'id("assignmentDatatable_info")').text.split()[3].replace(",","")) 
        jmlrow = rowpage - int(instance.driver.find_element(By.XPATH,'id("assignmentDatatable_info")').text.split()[1].replace(",","")) +1
        #print(f"# Getting data on row {rowpage} of {maxrow}, total rows now {jmlrow}")
        instance.log_message(f"# Getting data on row {rowpage} of {maxrow}, total rows now {jmlrow}")
        
        # getting data per row in current page
        try:
            for i in range(1,jmlrow+1):
                lisrow = []

                # getting data per column in this row
                alink = instance.driver.find_element(By.XPATH, f"//table[@id='assignmentDatatable']/tbody/tr[{i}]/td[2]/a").get_attribute('href')
                for j in range(2,len(headdf)+2): #ambil kolom, exclude yang centang di kolom 1
                    isi = instance.driver.find_element(By.XPATH, f"//table[@id='assignmentDatatable']/tbody/tr[{i}]/td[{j}]").text
                    lisrow.append(isi)
                lisrow.append(alink)
                # per row as df and merge with main df
                new_row_df = pd.DataFrame([lisrow], columns=df.columns)
                df = pd.concat([df, new_row_df], ignore_index=True)
        except Exception as e:
            #printwarn(f'# Error {str(e).split("Stacktrace")[0]}', color="red")
            #print("# Mungkin dah selesai, ricek ")
            instance.log_message(f"# Mungkin dah selesai, ricek ")
            break
        
        # next page    
        if satuloop: break
        instance.driver.find_element(By.XPATH, 'id("assignmentDatatable_next")').click()
        instance.log_message(f"# Scrolled to next page")
            
    # save as csv
    if mode=="w":
        df.to_csv(namadf, index=False, sep=sep, mode="w")
    elif mode=="a":
        df.to_csv(namadf, index=False, sep=sep, mode="a", header=False)

    #print(f"# Link data saved to {namadf}")
    instance.log_message(f"# Done. Link data saved to {namadf}")
    #change_text(label_status, "Running Selesai", "green")
    #df.tail()
    
    instance.isdone = 1
    return (df)


# Function approv (and get data)
def mainfunc(instance, filename, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=','):
    '''Get data dari Fasih dengan membuka linknya dari dataframe df, kemudian export ke csv. Kemudian jika ada cekapprov, maka jika sudah approv akan skip'''
    # konfig
    import sys
    instance.isdone = 0
    # GETTING DATA FROM FASIH OPEN DETAIL
    try:
        df = pd.read_csv(filename, sep=sep)
        if 'approved' not in df.columns:
            df['approved'] = ""
        # Get all window handles & Switch to the first window (index 0)
        all_window_handles = instance.driver.window_handles
        instance.driver.switch_to.window(all_window_handles[0])
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        instance.isdone = 1
        return

    #timestamp = datetime.now().strftime("%H:%M:%S")
    if cekapprov == True:
        #print(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data and approving...")
        instance.log_message(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data and approving...")
    else :
        #print(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data ...")
        instance.log_message(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data ...")

    if mulai <0 : i=-1
    else: i = mulai-1
    while True: 
        # Pastikan tampilan menggulir ke bagian paling bawah
        #instance.log_area.see(tk.END)
        #timestamp = datetime.now().strftime("%H:%M:%S")
        i += 1
        if i >= len(df):
            #printwarn("# DONEEE ---------------------------------", color='red', font_weight='bold', font_size="30px")
            instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
            #change_text(label_status, f"Running Selesai {adaerr}", "green")
            break
        try:
            # CEK DAH APPROVED LOM ke0 (cek dari hasil csv)------------------------------------------------------------
            if df.loc[i, 'approved'] == True:
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Dah approved admin, skip")
                continue

            ## goto web
            instance.driver.get(df.link[i])
            instance.driver.execute_script("document.body.style.zoom='50%'")
            #change_text(label_status, f"Processin data {i}/{len(df)}")
            
            # CEK DAH APPROVED LOM ke1 (cek dari assignment detail fasih) ------------------------------------------------------------
            #if cekapprov:
            #    try:
            #        WebDriverWait(instance.driver, 10).until(
            #            EC.presence_of_element_located((By.XPATH, 'id("datatable")')) )
            #        approvtxt = instance.driver.find_element(By.XPATH, 'id("datatable")').text
            #        # Pola Regex:
            #        # \d+           -> Mencari angka urutan (misal: 12)
            #        # \s+           -> Spasi setelah angka
            #        # (.*?)         -> Group 1: Ini adalah status yang kita ambil (non-greedy)
            #        # \s+           -> Spasi sebelum tanggal
            #        # \d{2}/\d{2}/  -> Pola tanggal (DD/MM/YYYY)
            #        pattern = r"\d+\s+(.*?)\s+\d{2}/\d{2}/\d{4}"
            #        matches = re.findall(pattern, approvtxt)
            #        if matches:
            #            if 'APPROVED' in matches[-1]:
            #                #print(i,df[idlog][i],'| Dah approved admin, skip')
            #                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Dah terapprov, skip")
            #                continue
            #    except TimeoutException:
            #        pass
        
            ## click btn review
            time.sleep(3)
            WebDriverWait(instance.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-primary")) ).click()
            ## wait till loading nya ilang
            time.sleep(2) #5
            WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
            ## wait till rendering form
            time.sleep(2) #3
            WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))
            instance.driver.execute_script("document.body.style.zoom='50%'")

            # CEK DAH APPROVED LOM ke2 (cek dari adakah button approve fasih) ------------------------------------------------------------
            if cekapprov:
                try:
                    WebDriverWait(instance.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, 'id("buttonApprove")'))
                    )
                except TimeoutException:
                    #print("# Approve button not found or not loaded yet")
                    #print(i,df[idlog][i],'| Not Found Approve button, skip')
                    instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Not Found Approve button, skip")
                    # logging
                    df.loc[i, 'approved'] = True
                    df.to_csv(filename, index=False)
                    continue

            if func:
                try:
                    # START GETTING DATA
                    #modul = importlib.import_module(func.split(".")[0])
                    #modulfunc = getattr(modul, func.split(".")[1])
                    #instance.log_message(f"# Modul fungsi {func} terdeteksi")
                    #modulfunc = globals()[func]
                    #instance.log_message(f"# Modul fungsi {func} ready")
                    #resultDict = modulfunc(instance)
                    resultDict = func(instance)
                    # export to csv
                    #if not os.path.exists(namaexport):
                    #    writetocsv([list(resultDict.keys())], filename=namaexport, sep=sep)
                    #writetocsv([list(resultDict.values())], filename=namaexport, sep=sep)
                    #df.loc[i,'koord'] = str(iters)
                    for key,value in resultDict.items():
                        df.loc[i, key] = value
                    df.to_csv(filename, index=False)
                except ValueError as e:
                    #print(f'# Terjadi error {str(e)}')
                    instance.log_message(f"# Terjadi error: ")
                    instance.log_message(str(e).split("Stacktrace:")[0], "red_tag")
                    # logging
                    df.loc[i, 'approved'] = str(e).split("Stacktrace:")[0]
                    df.to_csv(filename, index=False)
                    continue

            # APPROVE
            if cekapprov:
                ## klik approve
                btn_approve = instance.driver.find_element(By.XPATH,'id("buttonApprove")')
                #btn_approve.location_once_scrolled_into_view
                btn_approve.click()

                #konfirmasi
                instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                time.sleep(1)
                try:
                    instance.driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                    time.sleep(1)
                except: pass
            
            # end result if success
            df.loc[i, 'approved'] = True
            df.to_csv(filename, index=False)

        except Exception as e:
            # coba refresh n login ulang
            # Login SSO
            try:
                if 'Server Not Found' in instance.driver.title: 
                    #print('# Error server not found, CEK VPN -------------------------------------------')
                    instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
                    #change_text(label_status, "Error, CEK VPN", "red")
                    break
                #driver.refresh()
                instance.driver.get(df.link[i])
                #i -= 1
                if i < -1: i=-1
                #print(f'# error {str(e)}, reloading')
                instance.log_message(f"# Terjadi error: ")
                instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                #change_text(label_status, "Running ERROR", "red")
                try:
                    WebDriverWait(instance.driver, 10).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, "id('login-in')/A[2]")) #finding the element
                    ).click()
                    # input SSO
                    WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, 'id("kc-login")')) )
                    instance.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(instance.username_entry.get())
                    instance.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(instance.password_entry.get())
                    instance.driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
                    WebDriverWait(instance.driver, 15).until( #using explicit wait for x seconds
                        EC.presence_of_element_located((By.XPATH, 'id("Pencacahan")/TBODY[1]/TR[4]/TD[1]/A[1]')) )
                    #print('# login sso ulang')
                    instance.log_message(f"# Login SSO ulang ")
                    adaerr = ""
                except:
                    pass
                continue
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                #print(f"{i,df[idlog][i]} | Err: {str(exc_tb.tb_lineno)} | {str(e)}"  ) 
                #printwarn(f"{i,df[idlog][i]} | Err: {str(exc_tb.tb_lineno)} | {str(e)}", color='red', font_weight='bold', font_size="30px")
                instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
                instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                #change_text(label_status, "Running ERRORRR", "red")
                continue
        
        # jika satu row dah selesai, entah error or sukses    
        #print(i,df[idlog][i],'| Done')
        instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Done")
        #instance.log_message.yview_moveto(1.0)
        continue

    instance.isdone = 1
