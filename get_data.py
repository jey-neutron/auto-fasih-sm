# konfig
from datetime import datetime
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.select import Select
from argparse import Action
import pandas as pd
import time
import random
import os
import json
from playwright.sync_api import sync_playwright

def get_playwright_page(cdp_url="http://localhost:9222"):
    """
    Fungsi helper untuk connect ke browser Chrome yang sudah terbuka.
    Bisa dipanggil di thread mana saja.
    """
    p_instance = sync_playwright().start()
    try:
        browser = p_instance.chromium.connect_over_cdp(cdp_url)
        # Ambil page pertama yang aktif
        page = browser.contexts[0].pages[0]
        return p_instance, browser, page
    except Exception as e:
        # Jika gagal, pastikan instance playwright ditutup agar tidak memory leak
        p_instance.stop()
        raise RuntimeError(f"Gagal connect ke browser: {e}")
    
def check_stop(instance):
    '''Check if stop button is pressed'''
    if instance.stop_event.is_set():
        raise InterruptedError("Process stopped by user.")
    
def help(instance,var):
    '''Get list of functions'''
    instance.isdone = 0
    instance.log_message(f"List of available functions:")

    for nama, objek in globals().items():
        if (callable(objek) and 
            not nama.startswith("__") and 
            nama not in ["mainfunc", "get_list_data", "update_temp_value", "Action", "datetime","check_stop", "handle_response", 'mergejson','get_playwright_page'] ):
            
            # Ambil docstring-nya, kalau kosong kasih teks default
            deskripsi = objek.__doc__ if objek.__doc__ else ""# "Tidak ada deskripsi."

            # print output
            instance.log_area.insert("end", f"[-]")
            instance.log_area.insert("end", f" {nama}" ,"red_tag")
            instance.log_area.insert("end", f" ({deskripsi.strip().lower()})\n")
            instance.log_area.see("end")

    instance.log_area.insert("end", f"\n[-] Kosongin aja jika misal mau approval aja tanpa get data fasih-sm")
    instance.log_area.insert("end", f"\n[-] Anda bisa mengganti isian default username sso dengan membuat file 'tempuser.txt' dan isinya adalah usernamesso + (enter) + password sso ")
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
    check_stop(instance)
    instance.log_message(f"Hasil angka random {random.random()}")
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
            page.goto('https://translate.google.com/?sl=id&tl=en&op=translate')
            time.sleep(2)

            # translate judul
            page.get_by_role("textbox").fill(""+dt['judul_ind'][0])
            time.sleep(5) #tunggu translate
            dt['judul_eng'] = [page.locator('span[@lang="en"]').text_content()]

            # translate rincian
            page.get_by_role("textbox").fill(""+dt['rincian_ind'][0])
            time.sleep(5) #tunggu translate
            dt['rincian_eng'] = [page.locator('span[@lang="en"]').text_content()]

            # cek result
            instance.log_message(dt)

            # eksekusi ngisi webdash
            page.goto('https://webdash.web.bps.go.id/beritaTambah')
            try: #login sso 
                page.get_by_role("textbox", name="Username or email").click()
                page.get_by_role("textbox", name="Username or email").fill(instance.username_entry.get())
                page.get_by_role("textbox", name="Password").click()
                page.get_by_role("textbox", name="Password").fill(instance.password_entry.get())
                page.get_by_role("button", name="Log In").click()

                page.locator("h4.card-title").wait_for(state="visible", timeout=15000)
                page.goto('https://webdash.web.bps.go.id/beritaTambah')
            except:
                pass

            # isi tanggal 
            page.goto('https://webdash.web.bps.go.id/beritaTambah')
            time.sleep(2)
            page.goto('https://webdash.web.bps.go.id/beritaTambah')
            page.evaluate("document.body.style.zoom='33%'")
            time.sleep(2)
            page.locator("#date").fill(dt['tanggal'][0])
            page.locator("#date").press("Enter")

            # isi jenis kegiatan            
            page.locator("#jenis_kegiatan").fill(str(dt['jeniskeg'][0]))
            # isi image (Input File)
            page.locator("#foto").set_input_files(dt['image'][0])

            # isi ind
            page.locator("#nav-indo-tab").click()
            # isi judul_ind
            page.locator("#judul_ind_get").fill(str(dt['judul_ind'][0]))
            # isi rincian_ind (Quill Rich Text Editor)
            page.locator("#rincian_ind .ql-editor").fill(str(dt['rincian_ind'][0]))

            # isi eng
            page.locator("#nav-eng-tab").click()
            # isi judul_eng
            page.locator("#judul_eng_get").fill(str(dt['judul_eng'][0]))
            # isi rincian_eng (Quill Rich Text Editor)
            page.locator("#rincian_eng .ql-editor").fill(str(dt['rincian_eng'][0]))

            # isi tag
            page.locator("#tags").fill(str(dt['tag'][0]))

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
    '''Assign fasih-sm by selection, tapi upload dulu petugas ke fasih-sm, ada tutor pas run function pertama kali [Pake "NonApprov" ya]'''
    instance.isdone = 0
    driver
    page = instance.page
    instance.log_message("Maaf, fitur belum 100%")
    return
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
        instance.log_area.insert("end", f"[-] ", "red_tag"); instance.log_area.insert("end", f"Masukkan kolom ke-berapa sebagai acuan di field 'Baris mulai', misal di csv ada kolom 'Kode ID'(1), 'NUS'(2), 'KRT'(3), dan kita akan pakai 'Kode ID' untuk search, dan kolom 'KRT' sebagai acuan, maka isi: 13\n")
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
        driver.execute_script("document.body.style.zoom='50%'")
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
        count_gagal_sebelum_nyerah = 20 #perlu dicustom lagi si
        ## jika gagal loop terus :""
        listtimegagal = [] #untuk save time kegagalan
        listgagal = [] #untuk save index row yg gagal
        time.sleep(1)

        instance.log_message('Start assigning fasih --- ', tag="green_tag")
        while True:
            ## loop per row daftar_assign csv
            try:
                for dfrow in range(start,end): ## loop row df
                    check_stop(instance)
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
                instance.log_message('\nError terjadi: '+str(e).split("Stacktrace:")[0], tag="red_tag")
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
                    diff = listtimegagal[4]-listtimegagal[2] #itung delta time
                    #difftime = divmod(diff.days * seconds_in_day + diff.seconds, 1)[0]
                    difftime = diff.seconds
                else: difftime = 4
                
                if(len(set(listgagal))==1 and len(listgagal)>4): #jika gagal lebih dari 4x di index row itu, maka skip aja da
                    df.loc[df.index[dfrow], 'assigned'] = 'error'
                    start = dfrow+1
                    instance.log_message(f'{dfrow} Err mulu, Continuing aja', "green_tag")
                    continue 

                if ((gagal > count_gagal_sebelum_nyerah) or (difftime<3) ): # jika gagal lebih dari threshold maka errorin aja OR !! jika different time gagalnya gagal maka remove aja OR blabla nya
                    #Audio(sound_file, autoplay=True)
                    instance.log_message("WARN: Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e), tag="red_tag")
                    raise Exception("Gagal "+str(gagal)+"X, ada yang salah inih. Dahla nyerah: "+str(e))

                if gagal%3 == 0 : #jika gagal 3x reload trs run ulang
                    instance.log_message('Refreshing', tag="green_tag")
                    driver.refresh()
                    time.sleep(5)
                    driver.execute_script("document.body.style.zoom='50%'")
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
        page = instance.page
        # list id blok 4
        ids4 = ['n#umber_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
        # init a dict for data
        col_list = \
            [f"r{i}" for i in range(1,6)] + \
            ["r5b"] + [f"r{i}" for i in range(6,9)] + ["r9ab","r9ac"] + \
            [f"r9b{j}" for j in range(1,6)] + [f"r9b{j}c" for j in range(1,6)] + \
            [f"r10.{j}.1" for j in range(1,14)] + \
            [f"r10.{j}.2" for j in range(1,14)] + \
            [f"r11.{j}" for j in range(1,5)] + ['r12'] + ids4 + \
            [f"r{i}" for i in range(14,18)] + \
            [f"r18a_{k}" for k in ['arrival','departure']] + [f"r18b_{k}" for k in ['arrival','departure']] + [f"r18c_{k}" for k in ['arrival','departure']] + \
            [f"r19_{j}" for j in range(1,15)] +\
            [f"r{i}" for i in range(20,27)]
        d = dict.fromkeys(col_list, '--')
        #5b,9ac,9b[1,6],9b[1,6]c,10.[1,13], 11.[1,5], ids4, r18[a,b,c]_[arrival,departure], r19_[1,15], 

        def cek_inner( location, timeout=5000):
            # 1. Kunci elemen tombol dropdown
            elem = page.locator(location)
            # 2. Tunggu maksimal t detik sampai teksnya BUKAN "Select an option" atau ""
            try:
                page.wait_for_function(
                    "el => el.innerText.strip() !== '' && el.innerText.strip() !== 'Select an option' && el.innerText.strip() !== 'Pilih salah satu'",
                    arg=elem.element_handle(),
                    timeout=timeout )
            except Exception:
                pass  # Abaikan error timeout jika memang halaman web sengaja mengosongkannya
            return elem.inner_text().strip()
        
        def menubar(idblok):
            time.sleep(2)
            page.locator(f'xpath=//div[@id="fasih-form"]/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{idblok}]/DIV[1]').click()

        # BLOK1, click tab di sidebar
        menubar(1) 
        # 
        d['r1'] = page.locator("//div[@id='name']//input[@type='text']").input_value()
        d['r2'] = page.locator("//div[@id='age']//input[@type='text']").input_value()
        d['r3'] = page.locator("//div[@id='sex']").locator("input[type='radio']:checked").get_attribute('value')
        
        d['r4'] = cek_inner( "//div[@id='nationality']//button[@aria-haspopup='dialog']",10000)
        d['r5'] = cek_inner("//div[@id='country_residence']//button[@aria-haspopup='dialog']",10000)
        d['r5b'] = cek_inner("//div[@id='city_residence']//button[@aria-haspopup='dialog']",10000)
        
        d['r6'] = page.locator("//div[@id='main_purpose']").locator("input[type='radio']:checked").get_attribute('value')

        # BLOK2
        menubar(2)
        
        d['r7'] = cek_inner( "//div[@id='port_entry']//button[@aria-haspopup='dialog']")
        d['r8'] = page.locator("//div[@id='length_of_stay']//input[@type='text']").input_value()
        
        # main dest
        #d['r9'] = page.locator("//div[@id='main_destination_prov']//button/div").text
        d['r9ab'] = cek_inner( "//div[@id='main_destination_kab']//button[@aria-haspopup='dialog']")
        d['r9ac'] = page.locator("//div[@id='len_stay_main_dest']//input[@type='text']").input_value()
        
        # other dest
        for i in range(1, 6):
            #a = page.locator(f"//div[@id='other_destination_prov_{i}']//button[@aria-haspopup='dialog']").inner_text()
            a = cek_inner(f"//div[@id='other_destination_prov_{i}']//button[@aria-haspopup='dialog']", 10000)
            if a in ["", "Select an option", "Pilih salah satu"]: continue
            
            d[f"r9b{i}"] = cek_inner(f"//div[@id='other_destination_kab_{i}']//button[@aria-haspopup='dialog']")
            d[f"r9b{i}c"] = page.locator(f"//div[@id='len_stay_other_dest_{i}']//input[@type='text']").input_value()
        
        # BLOK3
        # get radio: tourism_attraction_05
        menubar(3)
        
        for i in range(1,14):
            d[f"r10.{i}.1"] = page.locator(f"//div[@id='tourism_attraction_{i:02}']").locator("input[type='radio']:checked").get_attribute('value')
            # jika ada terpilih
            if d[f"r10.{i}.1"] == '1':
                d[f"r10.{i}.2"] = page.locator(f"//div[@id='len_stay_tourism_{i}']//input[@type='text']").input_value()
            
            # for switch
            #d[f"r10.{i}"] = page.locator(f"//div[@id='tourism_attraction_{i:02}']//input[@type='checkbox']").is_selected()

        #BLOK4
        menubar(4)
        # tidak semua datanya diambil sih
        for i in range(1,5):
            d[f"r11.{i}"] = page.locator(f"//div[@id='accommodation_{i:02}']").locator("input[type='radio']:checked").get_attribute('value')
        d[f"r12"] = page.locator(f"//div[@id='use_tour_package']").locator("input[type='radio']:checked").get_attribute('value')

        #BLOK5
        menubar(5)

        # wait biar isiannya muncul dulu            
        ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
        for id4 in ids4:
            #try:
            if id4 == 'currency_spending':
                d[id4] = cek_inner(f"//div[@id='{id4}']//button[@aria-haspopup='dialog']")
            else: d[id4] = page.locator(f"//div[@id='{id4}']//input[@type='text']").input_value()

        #BLOK6
        menubar(6)
        
        d['r14'] = page.locator(f"//div[@id='main_occupation']").locator("input[type='radio']:checked").get_attribute('value')
        # r15 skip 
        d['r16'] = page.locator("//div[@id='freq_visit']//input[@type='text']").input_value()
        #
        for i in ['arrival', 'departure']:
            d[f'r18a_{i}'] = cek_inner(f"//div[@id='airline_{i}']//button[@aria-haspopup='dialog']")
            d[f'r18b_{i}'] = cek_inner(f"//div[@id='currency_{i}']//button[@aria-haspopup='dialog']")
            d[f'r18c_{i}'] = page.locator(f"//div[@id='value_{i}']//input[@type='text']").input_value()

        #BLOK7
        menubar(7)
        #
        # get switch: activities_06
        for i in range(1,15):
            d[f'r19_{i}'] = page.locator(f"//div[@id='activities_{i:02}']").locator("input[type='radio']:checked").get_attribute('value')
            #d[f'r19_{i}'] = page.locator(f"//div[@id='activities_{i:02}']//input[@type='checkbox']").is_selected()

        d['r20'] = page.locator(f"//div[@id='wonderful_indonesia']").locator("input[type='radio']:checked").get_attribute('value')
        d['r21'] = page.locator(f"//div[@id='ecofriendly_principle']").locator("input[type='radio']:checked").get_attribute('value')
        d['r22'] = page.locator(f"//div[@id='satisfaction_lvl']").locator("input[type='radio']:checked").get_attribute('value')
        d['r23'] = page.locator(f"//div[@id='intention_to_visit']").locator("input[type='radio']:checked").get_attribute('value')

        #BLOK8
        menubar(8)
        #
        d['r24'] = page.locator(f"//div[@id='note']//textarea").input_value()
        d['r25'] = page.locator(f"//div[@id='impression']//textarea").input_value()
        d['r26'] = page.locator(f"//div[@id='viplounge']").locator("input[type='radio']:checked").get_attribute('value')

        
    except Exception as e:
        instance.log_message(f'Terjadi error: {e}')

    # FINISH
    return d


# Function reject data Fasih
def reject(instance, var, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=','):
    #(instance, filename, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=',')
    '''Reject di fasih-sm berdasarkan file yang dipilih'''
    driver
    instance.log_message("Maaf, fitur belum 100%")
    return
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
        all_window_handles = driver.window_handles
        driver.switch_to.window(all_window_handles[0])
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
            check_stop(instance)
            # CEK DAH EKSEKUSI LOM ke0 ------------------------------------------------------------
            if df.loc[i, 'approved'] == 'REJECTED':
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Dah dieksekusi, skip")
                continue

            ## goto web
            page.goto(df.link[i])
            driver.execute_script("document.body.style.zoom='50%'")
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
            driver.execute_script("document.body.style.zoom='50%'")

            # CEK DAH APPROVED LOM ke1 ------------------------------------------------------------
            try:
                #try revoke
                try:
                    WebDriverWait(instance.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, 'id("buttonRevoke")'))
                    )
                    btn_approve = driver.find_element(By.XPATH,'id("buttonRevoke")')
                    #btn_approve.location_once_scrolled_into_view
                    btn_approve.click()
                    #konfirmasi
                    driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                    time.sleep(1)
                    try:
                        driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                        time.sleep(1)
                    except: pass
                
                except: pass

                # refresh
                driver.refresh()
                ## wait till loading nya ilang
                time.sleep(2) #5
                WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.loading-text > .ng-tns-c4183080771-2')))
                ## wait till rendering form
                driver.execute_script("document.body.style.zoom='50%'")
                time.sleep(2) #3
                WebDriverWait(instance.driver, 100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p.mb-2')))

                # reject
                WebDriverWait(instance.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, 'id("buttonReject")'))
                )
                btn_approve = driver.find_element(By.XPATH,'id("buttonReject")')
                #btn_approve.location_once_scrolled_into_view
                btn_approve.click()
                #konfirmasi
                driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
                time.sleep(1)
                try:
                    driver.find_element(By.CSS_SELECTOR,'button.swal2-confirm').click()
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
                if 'Server Not Found' in driver.title: 
                    #print('# Error server not found, CEK VPN -------------------------------------------')
                    instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
                    #change_text(label_status, "Error, CEK VPN", "red")
                    break
                #driver.refresh()
                page.goto(df.link[i])
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
                    driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(instance.username_entry.get())
                    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(instance.password_entry.get())
                    driver.find_element(By.XPATH, '//*[@id="kc-login"]').send_keys(Keys.RETURN)
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


# Function penunjang to get list data
def handle_response(instance, response, namejson='data_survey.json', target_url="https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"):
    # Filter URL spesifik yang ingin Anda ambil datanya
    
    if target_url in response.url:
        try:
            # Ambil data dalam bentuk JSON
            data = response.json()
            # Simpan data ke file lokal agar bisa Anda cek di VS Code
            with open(namejson, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            instance.log_message(f"[✓] (Status {response.status}). Data disimpan ke '{namejson}'")
            
        except Exception as e:
            # Jika respon bukan JSON (misal HTML/Text)
            instance.log_message(f'Gagal: {response.text()[:500]}') # Cetak 500 karakter pertama

# Function penunjang to get list data
def mergejson(dictlist, listcol, namejson='data_survey.json'):
    '''Merge hasil response dari namejson ke dictlist existing dengan filtering listcol yang sama '''
    with open(namejson, 'r') as file:
        data = json.load(file)
    #data['searchData'][0]#.keys()
    for i in range(len(data['searchData'])):
        dictlist.append({key: data['searchData'][i][key] for key in listcol if key in data['searchData'][i]})
    return dictlist


# Function to get list data
def get_list_data(instance, namadf,  mode="w", maxrow=0, sep=","):
    '''Get dataframe dari prelist link fasih untuk dijadikan bahan, kemudian export ke csv juga. Update ngambilnya dari response URL API'''
    instance.isdone = 0
    try:
        p_instance, browser, page = get_playwright_page() #konek ke playwr
        
        # wait n getting response
        namejson = 'data_survey.json'
        target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        page.on("response", lambda response: handle_response(response, response, namejson, target_url))

        # page.goto("https://fasih-sm.bps.go.id/app/surveys?page=0&perPage=10&layout=list")
        page.reload()
        page.wait_for_timeout(2000) 
        page.evaluate("document.body.style.zoom='0.5'")
        page.locator("h3").first.wait_for(
            state="visible", 
            timeout=10000
        )
        instance.log_message('# Get response data on page 1')

        # read json
        ipage = 1
        dflist = []
        listcol = ['id', 'surveyPeriodId', 'codeIdentity', 'assignmentStatusId', 'assignmentStatusAlias', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'dateCreated', 'isActive', 'currentUserUsername','lockedByUser', 'lockedByAnother']
        dflist = mergejson(dflist, listcol, namejson)

        # next page        
        #page.get_by_role("button", name="Go to next page").click()
        while True:
            check_stop(instance)
            # 1. Ambil locator tombol next
            next_button = page.get_by_role("button", name="Go to next page")
            
            # 2. Cek apakah tombol ada, muncul, dan aktif (tidak disabled)
            if next_button.is_visible() and next_button.is_enabled():
                next_button.click()
                ipage += 1
                page.wait_for_timeout(2000) # Jeda 1 detik nunggu halaman muat
                instance.log_message(f'# Get response data from page {ipage}')
                dflist = mergejson(dflist, listcol, namejson)
            else:
                instance.log_message('# Selesai')
                try: os.remove(namejson)
                except: instance.log_message("File not created", tag='red_tag')
                break # Berhenti loop jika tidak bisa diklik

        time.sleep(2)
        # ngerapiin
        df = pd.DataFrame(dflist)
        df['link'] = 'https://fasih-sm.bps.go.id/app/assignment/'+ df['surveyPeriodId'].astype(str) + "/" + df['id'].astype(str)
        #page.pause() #debugging, open recorder on playwright
                
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
    
    except Exception as e:
        instance.log_message(f"Error di thread data: {e}", tag="red_tag")
    finally:
        # Selalu tutup p_instance di blok 'finally' agar tidak hang
        try:
            p_instance.stop()
            instance.log_message("Koneksi Playwright di thread ditutup.")
        except NameError:
            # Terjadi jika get_playwright_page() gagal total di awal
            pass

# Function approv (and get data)
def mainfunc(instance, filename, mulai=0, func=None, cekapprov=True, idlog='Kode Identitas', sep=','):
    '''Get data dari Fasih dengan membuka linknya dari dataframe df, kemudian export ke csv. Kemudian akan approv juga jika tercentang sekalian approv'''
    # konfig
    import sys
    instance.isdone = 0

    # read data csv result from get list data
    try:
        df = pd.read_csv(filename, sep=sep)
        if 'approved' not in df.columns:
            df['approved'] = ""
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        df = None
        isdone = 1
        return
    
    # cek approv or not
    msgapprov = ' and approving' if cekapprov else ''
    instance.log_message(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data{msgapprov}...")

    # start loop per df
    if mulai <0 : i=-1
    else: i = mulai-1
    while True: 
        check_stop(instance)
        # LOOOOOOOOOP
        i += 1
        if i >= len(df):
            instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
            break
        try:
            # CEK DAH APPROVED LOM ke1 (cek dari hasil csv)------------------------------------------------------------
            if df.loc[i, 'approved'] == True:
                instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Dah approved, skip")
                continue

            # goto web
            instance.page.goto(df.link[i])
            # tapi ada error disini biasanya gamau load page, hmm. tpi klo load normal haruse pass
            instance.page.wait_for_load_state("networkidle", timeout=5000) #stabil sebelum cek field
            instance.page.evaluate("document.body.style.zoom='0.5'")

            # perlukah cek approv yg ke2? ======

            # function tambahan here
            if func:
                try:
                    resultDict = func(instance)
                    # get a dict value per row from web (init dict from func)
                    for key,value in resultDict.items():
                        df.loc[i, key] = value
                    df.to_csv(filename, index=False)
                    
                except ValueError as e:
                    instance.instance.log_message(f"# Terjadi error: ")
                    instance.instance.log_message(str(e).split("Stacktrace:")[0], "red_tag")
                    # logging
                    df.loc[i, 'approved'] = str(e).split("Stacktrace:")[0]
                    df.to_csv(filename, index=False)
                    continue
            # 

            # mulai approve jika approv 
            if cekapprov:
                try:
                    cekbtn = instance.page.get_by_role("button", name="Open menu") 
                    cekbtn.first.wait_for( #cek jika visible juga
                        state="visible", 
                        timeout=10000
                    )
                    cekbtn.click() #click btuton menu
                    instance.page.locator("button[class*='rounded-full'][class*='bg-success']").click() #approv
                    instance.page.get_by_role("button", name="Konfirmasi").click() #konfirm modal
                    # wait
                    instance.page.wait_for_timeout(1500)
                    time.sleep(2)

                except:
                    instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Not Found Approve button, skip")
                    # logging
                    df.loc[i, 'approved'] = True
                    df.to_csv(filename, index=False)
                    continue

            # end result if success
            df.loc[i, 'approved'] = True
            df.to_csv(filename, index=False)
            
        except Exception as e:
            # coba refresh n login ulang
            try:
                if 'Server Not Found' in instance.page.title: 
                    instance.instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
                    break
                # reload
                instance.page.goto(df.link[i])
                if i < -1: i=-1
                instance.instance.log_message(f"# Terjadi error: ")
                instance.instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                # try relogin sso ====== need update
                #
                continue

            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                instance.instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
                instance.instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                continue
        
        # jika satu row dah selesai, entah error or sukses    
        instance.instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Done")
        continue

    instance.isdone = 1