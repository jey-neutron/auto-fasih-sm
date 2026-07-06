# konfig var
APP_VERSION = 'v2.4.2' #add func kiap, app update detach log, update log message, update UI
TIMEOUT_REQUEST = 60000 #ms
ROW_REQUEST = 50 #jml row yg diambil dari request getlistdata
MAX_WORKERS = 3 #jml tab/worker
MAX_RETRY = 30 #jml error trus retrying
CHROME_PORT = "http://localhost:9222"

# konfig
from datetime import datetime
import pandas as pd
import time
import random
import os
import json
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from urllib.parse import unquote
import json
import sys
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, wait
# harus ada di mainapp, import fitur added
from lzstring import LZString
import ast
import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap

# =====================================================================
# FUNC DRAFT 
# =====================================================================

# def inputwebdash(instance, var)
# def assignselect(instance, var)
# def mailbc(instance, var) # mybe, buat ngibar paling, ref from appdev.py ======
# def getnikmitra(instance, var):
#     try:
#         with open(r'D:\OneDrive\~Jimmy\~STIS\PY\Work_py\auto-fasih-sm\dist\temp.json', 'r', encoding='utf-8') as file:
#         df = json.load(file)
        
#         # send and get response (get data detail all)
#         base_url = "https://mitra-api.bps.go.id/api/mitra/reveal-info/nik"
#         response = __run_api_request(instance, , method="get", target_url=base_url, target_id=target_id, msg=f"GetNIK-row-{i}")
#         if response is None:
#             raise ValueError("API tidak mengembalikan data (Response is None)")
#         if response['success'] == False or response['success'] == "false":
#             raise ValueError(response['message'])


# =====================================================================
# FUNC INTRODUCTION 
# =====================================================================

def help(instance,var=''):
    '''Get list of functions'''
    try:
        exclude_fun_list = ["datetime", "sync_playwright",
                            'expect','unquote', 'PlaywrightTimeoutError',
                            'LZString','ThreadPoolExecutor','wait','isdone','chromeport']
        if var == 1:
            instance.isdone = 0
            instance.log_message(f"List of available functions:")

            for nama, objek in globals().items():
                if (callable(objek) and 
                    not nama.startswith("__") and 
                    nama not in exclude_fun_list ):
                    # exclude function main and penunjang, hanya tampilin function side aja
                    
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
        return exclude_fun_list
    except Exception as e:
        instance.log_message('Error:',e)

def getrandom(instance, var): 
    '''Get a random number'''
    instance.isdone = 0
    try:
        for i in range(0,4):
            __check_stop(instance)
            time.sleep(1)
            try:
                instance.log_message(f"Hasil angka random-{i} {int(var)*random.random()}")
            except:
                instance.log_message(f"Hasil angka random-{i} {random.random()}")
    except Exception as e:
        instance.log_message(e,'red_tag')
    instance.isdone = 1

def getrandomcat(instance, var=1):
    '''Who knows'''
    listres=["      /\\___/\\\n     ( - . - )  Zzz\n    /  \\___/  \\\n   (___________)",
            "     /\\_/\\\n   =( -.- )=  Zzz\n    (  \"  )__",
            "   /\\/\\  \n  ( u.u) Zzz\n  (_)(_)__",
            "   /\\_/\\\n  (=-.-=)  zzZ\n  (\")(\")__",
            "  |\\_/,|   \n  | u.u|  zzZ\n  (  w  )  ",
            "    /\\_/\\\n  =( u.u )=  Zzz\n  __(__)",
            "   /\\___/\\\n  ( - . - ) zZz\n  [=======]"]
    if var !=1:
        try:
            var = int(var)
            if var>=len(listres):
                instance.log_message(f'Melebihi max list ({len(listres)})', 'red_tag')
                var=random.randint(0,len(listres)-1)
        except Exception as e:
            instance.log_message(f'Err: {e}', 'red_tag')
            var=random.randint(0,len(listres)-1)
        instance.log_message(f'Selected: {var}')
        res = listres[var]
    else : res= random.choice(listres)
    instance.log_area.insert("end", f"\n{res}\n")
    instance.log_area.see("end")

def render(instance,var):
    """Memanggil index.html dengan pilihan variable terlampir, var='done', 'running', 'ready' """
    p_instance, ctx, page = __get_playwright_page() #konek ke playwr
    instance.log_message(f'Rendering HTML. Var="done", "running", "ready". Chosen: {var} ')
    page.goto(instance.getassets('index.html'))
    if var != 1:
        page.evaluate(f"document.body.setAttribute('data-status', '{var}')")
    instance.log_message('Selesai')
    #instance.isdone=1
    

# =====================================================================
# FUNC SECTION MANAJEMEN MITRA
# =====================================================================
def mitra_geturl(instance=None,var='[]'):
    '''Generate url mitra dari var yg diinput. Var=["id_ms", "id_mitra", "kd_survei", 'id_keg', 'kd_prov']'''

    allowed_keys = ["id_ms", "id_mitra", "kd_survei", 'id_keg', 'kd_prov']
    listvar = ast.literal_eval(var)
    a = dict(zip(allowed_keys, listvar))
    
    # Membuat format string yang di-concat seperti di JS
    concat_str = f"{a.get('id_ms')},{a.get('id_mitra')},{a['kd_survei']},{a['id_keg']},{a['kd_prov']}"
    
    # Ubah string tersebut menjadi format JSON string
    # JS: JSON.stringify(...)
    json_str = json.dumps(concat_str)
    
    # Kompresi menggunakan LZString ke format Encoded URI Component
    lz = LZString()
    compressed = lz.compressToEncodedURIComponent(json_str)
    
    return f"https://mitra.bps.go.id/c/{compressed}"

def mitra_kartu(instance,var):
    '''Generate kartu petugas dari data csv. Df.columns harus ada: nama, sobat_id, id_ms, id_mitra, kd_survei, id_keg, kd_prov'''
    instance.isdone = 0
    namafile = instance.filename_entry.get()
    df = pd.read_csv(namafile).astype('str')
    # cek col
    instance.log_message(f'Data loaded with columns: {df.columns}')
    target_cols = ['nama', 'sobat_id', 'id_ms', 'id_mitra', 'kd_survei', 'id_keg', 'kd_prov']
    missing_cols = list(set(target_cols) - set(df.columns))
    if missing_cols: 
        instance.log_message(f"Missing columns: {missing_cols}", "red_tag")
        raise ValueError('Error, column di csv tidak ditemukan')

    df['url'] = ''
    df['status'] = ''

    # make url from df sekalian generate kartu
    instance.log_message('Creating column url')
    for i in range(len(df)):
        try:
            df.loc[i, 'url'] = mitra_geturl(var=str([df.loc[i,"id_ms"], df.loc[i,"id_mitra"], df.loc[i,"kd_survei"], df.loc[i,"id_keg"], df.loc[i,"kd_prov"]]))
            config = {
                "bg_path": r"cocard-template.png",
                "text_box": (200, 955, 1000, 970), # start x, start y, width box, height box; sementara yg kepake baru y aja
                "qr_box": (450, 1148, 330, 330),
                "font_size": 80, 
                "font_type": r"Raleway-SemiBold.ttf"
            }
            output_name = str(df.loc[i,'nama']) + "_"+ str(df.loc[i,'sobat_id'])[:35]+ '.png'
            res= gen_mergemail(instance, var=None, nama=df.loc[i, 'nama'], data_qr=df.loc[i, 'url'], 
                          cfg=config, output_name=output_name)
            if not res : 
                df.loc[i, 'status'] = 'Gagal'
                raise ValueError('Program dihentikan')
            df.loc[i, 'status'] = 'Sukses'
            instance.log_message(f"Sukses Generate: {output_name}")

        except Exception as e:
            df.loc[i, 'url'] = str(e)
            df.loc[i, 'status'] = str(e)
            instance.log_message(f"Error on row-{i}: {e}", "red_tag")

            instance.isdone=1
            return

    df.to_csv(namafile, index=False)
    instance.isdone = 1

def genQR(instance=None, var='', namafile='', pathfolder = ''):
    '''Membuat QR code dari variable yg diisikan'''

    namafile = 'qrcode.png' if namafile == '' else str(namafile).replace(" ", "_") + '.png'
    path_simpan = os.path.join(namafile) if pathfolder=='' else os.path.join(pathfolder, namafile)
    var = str(var)
    if var=='':
        return 'Isi_QR_code_kosong'
    
    # Buat QR Code
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(var)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path_simpan)

    # Kembalikan path lengkap untuk disimpan di Excel baru (gunakan double backslash untuk Word)
    path_absolut = os.path.abspath(path_simpan)
    return path_absolut.replace("\\", "\\\\")

def gen_mergemail(instance, var, nama=None, data_qr=None, cfg={}, output_name=''):
    """Mail merge dari template png mengikuti cfg/config dan isian berdasarkan csv"""
    if nama == None and data_qr==None and cfg == {}: 
        # init read dict from config.txt next ======
        return None
    try:
        # Load background RGBA agar warna QR terkunci hitam-putih
        img = Image.open(cfg["bg_path"]).convert("RGBA")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(cfg['font_type'], cfg["font_size"])
    except Exception as e:
        instance.log_message(f"GAGAL LOAD FILE! Detail: {e}", "red_tag")
        return False

    x1, y1, w_box, h_box = cfg["text_box"]
    # 1. Bersihkan String Nama
    nama_clean = str(nama).strip().upper()
    lebar_teks_asli = draw.textlength(nama_clean, font=font)
    
    # Gunakan textwrap dengan width lebih besar agar kata tidak terpotong per huruf
    if lebar_teks_asli > w_box:
        nama_final = nama_clean
        if len(nama_clean) > 35:
            nama_potong = nama_clean[:35]
            words = nama_potong.split()
            if len(words) > 1:
                all_but_last = " ".join(words[:-1])
                nama_final = f"{all_but_last} {words[-1][0]}."
            else:
                nama_final = nama_clean[:20] # Fallback jika hanya 1 kata panjang
            # Jika lebih dari 35 karakter, paksa potong lebih pendek agar otomatis jadi 2 baris yang seimbang
        lines = textwrap.wrap(nama_final, width=20)
    else:
        # Jika di bawah 35 karakter, berikan ruang lebar agar tetap aman dalam 1 baris
        lines = textwrap.wrap(nama_clean, width=30)
    text_to_draw = "\n".join(lines)
    
    x_center = img.width / 2  
    y_floor = y1  
    y_start = y1 - (cfg["font_size"] * (len(lines) - 1) + 20)
    
    # UBAH: Menggunakan anchor="ma" (Middle-Top) dikombinasikan dengan hitungan y_start dinamis di atas
    draw.text((x_center, y_start), text_to_draw, fill="black", font=font, anchor="ma", align="center")

    # 3. Gambar QR Code (Hitam-Putih Bersih)
    qr = qrcode.make(data_qr).convert("RGBA") 
    qr_width = cfg["qr_box"][2]
    qr_height = cfg["qr_box"][3]
    qr = qr.resize((qr_width, qr_height))
    
    qx = cfg["qr_box"][0] + (qr_width - qr.size[0]) #// 2
    qy = cfg["qr_box"][1] + (qr_height - qr.size[1]) #// 2
    img.paste(qr, (qx, qy), mask=qr)
    
    # Simpan instan dalam hitungan milidetik
    final_img = img.convert("RGB")
    # instance.log_message(f"Sukses Generate: {output_name}")
    if output_name == '':
        output_name = 'export_kartu.png' 
    else:
        os.makedirs('export_kartu', exist_ok=True)
        output_name = os.path.join('export_kartu', output_name)
    final_img.save(output_name)
    return True


def mitra_addpenawaran(instance, var):
    '''Manmit autobrowser add to penawaran survey dari mitra kepka, df.columns = nama, status (kosong). Pastikan browser sudah sampe ke menu milih dari kepka.'''
    log_message = instance.log_message
    p_instance, ctx, page = __get_playwright_page() #konek ke playwr
    
    namafile = instance.filename_entry.get()
    df = pd.read_csv(namafile)
    if 'Nama' in df.columns:
        df = df.rename(columns={'Nama': 'nama'})

    log_message('csv read')
    gagal = 0
    j = 0
    
    for i in range(len(df)):
        __check_stop(instance)
        log_message(f"# {df.loc[i, 'nama']} otw")

        if df.loc[i, 'status'] == 'skip' or df.loc[i, 'status'] == 'done' or df.loc[i, 'status'] == 'kosong':
            log_message('already done')
            continue
        page.get_by_role("textbox", name="Cari").click()
        page.get_by_role("textbox", name="Cari").fill(df.loc[i, 'nama'])
        time.sleep(1)
        try:
            # el = page.locator("div:nth-child(2) > .col-12.col-md-6")
            el = page.locator("div").filter(has_text=df.loc[i, 'nama'][:17] ).first
            try:
                el.wait_for(timeout=1000, state="visible")
            # if el.count() > 0:
                stat = el.first.text_content() 
                if 'Sudah Terdaftar' in stat:
                    df.loc[i,'status'] = 'skip'
                    log_message('sudah daftar')
                    df.to_csv(namafile, index=False)
                    continue
                page.locator(".fa.fa-plus.text-success").click()
                df.loc[i,'status'] = 'done'

                j += 1
                time.sleep(0.5)

            # else:
            except PlaywrightTimeoutError:
                df.loc[i,'status'] = 'kosong'
                log_message('kosong')
                df.to_csv(namafile, index=False)
                continue
            
        except Exception as e:
            df.loc[i, 'status'] = 'error'
            log_message(e)
            gagal +=1
            if gagal > 3: break
            df.to_csv(namafile, index=False)
            continue
            
        # page.locator(".fa.fa-plus.text-success").click()
        # page.get_by_role("link", name="Terpilih").click()
        # page.locator(".d-flex.justify-content-between.px-2").first.click()

        #i+= 1
        if j > 20: 
            time.sleep(1)
            page.get_by_role("tab", name="Terpilih").click()
            page.get_by_role("button", name="Tawarkan", exact=False).click()
            # page.locator("#ptMeowOn6p1AEvFE > .modal-dialog > .modal-content > .modal-header > .btn-close").select_option("54")
            page.locator("select.swal2-select").select_option(value="54")
            page.get_by_role("button", name="Ya, Saya Yakin!").click()
            page.get_by_role("button", name="Kosongkan", exact=False ).click()
            page.get_by_role("button", name="Ya", exact=True).click()
            time.sleep(2)
            page.get_by_role("tab", name="Cari").click()
            page.get_by_role("textbox", name="Cari").click()
            df.to_csv(namafile, index=False)
            j=0
            # break
            continue


    log_message('SLESE')
    # instance.isdone = 1

# =====================================================================
# FUNC SECTION KIAP
# =====================================================================
def kiap_addkeg(instance, var):
    '''Add pelaksanaan kinerja di Kipapp dari csv yg diberikan. Masukkan niplama di Input Variabel. Sementara isian id2 yg perlu diperoleh manual, blm ada func tambahan. Kolom harus ada: id,skpid, rkid, kegiatan, tanggal, tanggalselesai, progres, jammulai, jamselesai, capaian, datadukung, iscapaianskp'''
    # read data csv result from get list data
    try:
        filename = instance.filename_entry.get()
        df = pd.read_csv(filename, sep=',')
        df = df.astype(str)
        if 'status_work' not in df.columns:
            df['status_work'] = ""
        kolwjb = {'id','skpid', 'rkid', 'kegiatan', 'tanggal', 'tanggalselesai', 'progres', 'jammulai', 'jamselesai', 'capaian', 'datadukung', 'iscapaianskp'}
        if not kolwjb.issubset(df.columns) :
            raise ValueError (f"Ada kolom yg tidak ditemukan di csv, silakan update dulu dan liat deskripsi. Nama kolom harus sama")
        lendf = len(df)
        # make df as df list py
        dflist = df.to_dict(orient='records')
    except Exception as e:
        instance.log_message(f'ERROR: {e}', tag="red_tag")
        df = None
        dflist = None
        instance.isdone = 1
        return
    
    # execute
    idlog='kegiatan'
    # get header from reloading page opened rn
    try:
        # 1. var
        row_indices = range(0, lendf)
        target_url = 'https://kipapp.bps.go.id/api/v1/kegiatan'
        if '340' not in str(var):
            raise ValueError('NIP lama bener atau belum diinput?')
        
        p_instance, ctx, page = __get_playwright_page() #konek ke playwr
        captured_req, api_url, api_payload, api_headers = __get_headers(page, f'https://kipapp.bps.go.id/api/v1/dashboard/rkpegawai?niplama={var}')
        time.sleep(1)
        
        # 1. Kembaliin ke page UI user (di tab yg page utama)
        page.goto(instance.getassets('index.html'))
        page.evaluate("document.body.setAttribute('data-status', 'running')")

        # 3. Jalankan Multi-tab Pekerja via ThreadPoolExecutor
        # Sesuaikan `max_workers` dengan kekuatan CPU/RAM (misal: 3 s.d 5 tab sekaligus)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            # Set antrian ke worker
            for idx, i in enumerate(row_indices):
                # CEK approv lom ke 1, cek id jg
                if dflist[i]['status_work'] in [True, "True"]:
                    instance.log_message(f"[tab:0] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Done, skip")
                    continue
                elif dflist[i]["rkid"] in [None, "", "skip", "SKIP",'-']:
                    instance.log_message(f"[tab:0] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | No ID, skip")
                    continue
                # var
                # Masukkan semua key yang Anda butuhkan ke dalam list
                keys = ["skpid", "rkid", "kegiatan", "tanggal", "tanggalselesai", 
                        "progres", "jammulai", "jamselesai", "capaian", "datadukung", "iscapaianskp"]
                # Kode ini otomatis menyusun payload dan mengubah NaN menjadi None
                payload = {key: (None if pd.isna(dflist[i][key]) or dflist[i][key]=='nan' else dflist[i][key]) for key in keys}

                # ngantri worker
                worker_id = (idx % MAX_WORKERS) + 1
                try:
                    f = executor.submit(
                        __row_mainfunc, i, instance, lendf, dflist, idlog, filename, None, 
                        api_headers, False, worker_id, CHROME_PORT, 
                        True,'post', target_url=target_url, payload=payload
                    ) 
                    futures.append(f)
                    # instance.log_message(f"Baris index-{i} berhasil didaftarkan ke Worker {worker_id}")
                    # time.sleep(0.2) # Jeda mikro pendaftaran
                except Exception as e_submit:
                    instance.log_message(f"Gagal memasukkan index-{i} ke Thread Pool: {e_submit}", "red_tag")

            instance.log_message(f"# {len(futures)} work mengantre ({MAX_WORKERS} tab)...")

            # Worker bekerja, sampai semua futures/antrean beres
            from concurrent.futures import wait, FIRST_COMPLETED
            # wait(futures, return_when=ALL_COMPLETED) #jika semua worker selesai, updated diganti bwh:
            curr_retry = 0
            while True:
                # Cek jika ada stop dari user mk batalkan antrean
                if instance.stop_event.is_set() or curr_retry>=MAX_RETRY:
                    if curr_retry >= MAX_RETRY:
                        instance.log_message(f'Sudah melebihi maksimal retry error ({MAX_RETRY})')
                    instance.log_message("Menghentikan seluruh antrean worker...", "red_tag")
                    for f in futures:
                        f.cancel() # Membatalkan antrean yang belum sempat berjalan oleh worker
                    break # Keluar dari loop pemantauan main thread
                
                # Cek apakah ada worker yang meminta pause untuk refresh page utama
                if not worker_resume_on_none.is_set():
                    instance.log_message("Worker mendeteksi API None. Merefresh page utama...", "red_tag")
                    try:
                        # === REFRESH PAGE UTAMA DISINI ===
                        page.go_back(timeout=10000)
                        time.sleep(5)
                        page.reload()
                        time.sleep(5)
                        page.goto(instance.getassets('index.html'))
                        page.evaluate("document.body.setAttribute('data-status', 'running')")
                        time.sleep(2)
                        curr_retry += 1
                        # =================================
                    except Exception as e:
                        instance.log_message(f"Gagal refresh page utama: {e}", "red_tag")
                    finally:
                        instance.log_message("Refresh selesai. Melanjutkan worker...")
                        worker_resume_on_none.set() # Bangunkan semua worker
                
                time.sleep(random.uniform(0.5, 0.9)) 
                # Cek status futures dengan timeout pendek agar loop tetap berjalan
                done, not_done = wait(futures, timeout=1.5, return_when=FIRST_COMPLETED)
                if len(not_done) == 0:
                    global_hitapi_counter = 0
                    break # Semua pekerjaan selesai
            
        # 4. Selesai Semua
        instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
        ##

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
        instance.log_message(f"Error di thread data kiap: {e}", tag="red_tag")
    finally:
        # Selalu tutup p_instance di blok 'finally' agar tidak hang
        isdone(instance, page=page, output=True)
        try:
            p_instance.stop()
            instance.log_message("Koneksi Playwright di thread ditutup.")
        except NameError:
            # Terjadi jika get playwright page() gagal total di awal
            pass

# =====================================================================
# FUNC ADDED
# =====================================================================
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


def seedata(instance, var):
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


# =====================================================================
# FUNC SECTION FUNGSI TAMBAHAN __mainfunc 
# =====================================================================
def getdataAll(namafile = 'data_survey.json'):
    '''FUNCTION FOR GETTING DATA GENERAL SURVEY (mybe ada kendala, tpi sementara ini deh), PAKE APPROVAL FASIH (TRUE/FALSE)'''
    # Open the file and load its content
    with open(namafile, 'r') as file:
        df = json.load(file)
    dff = json.loads(df['data']['data'])['answers']
    dffT = {item["dataKey"]: item for item in dff}
    d = {}

    try:
        for key, value_dict in dffT.items():
            if 'master' in key:
                continue # Skip 'master' keys
            final_output_value = None # Initialize to None

            if 'answer' in value_dict:
                raw_answer = value_dict['answer']

                if isinstance(raw_answer, list):
                    extracted_item_strings = []
                    for item in raw_answer:
                        extracted_part_for_item = None
                        if isinstance(item, dict):
                            # 1. Special handling for 'maps.google.com' in label
                            if 'label' in item and item['label'] is not None and 'maps.google.com' in str(item['label']):
                                if isinstance(item.get('value'), dict):
                                    values_list = list(item['value'].values())
                                    if values_list:
                                        extracted_part_for_item = str(values_list)
                                    else:
                                        extracted_part_for_item = str(item['value']) # If dict is empty
                                else:
                                    extracted_part_for_item = str(item.get('value', ''))

                                extracted_item_strings.append(str(extracted_part_for_item))
                                break # Stop processing other items in this raw_answer list as per request

                            # 2. General 'label' extraction
                            elif 'label' in item and item['label'] is not None:
                                extracted_part_for_item = item['label']
                            # 3. General 'value' extraction
                            elif 'value' in item and item['value'] is not None:
                                if isinstance(item['value'], dict):
                                    nested_values = [str(v) for v in item['value'].values() if v is not None]
                                    extracted_part_for_item = ", ".join(nested_values) if nested_values else str(item['value'])
                                else:
                                    extracted_part_for_item = item['value']
                            # 4. Fallback: extract values from the dict itself
                            else:
                                nested_values = [str(v) for v in item.values() if v is not None]
                                extracted_part_for_item = ", ".join(nested_values) if nested_values else str(item)
                        else: # Not a dict, directly use the item
                            extracted_part_for_item = item

                        if extracted_part_for_item is not None:
                            extracted_item_strings.append(str(extracted_part_for_item))

                    final_output_value = ", ".join(extracted_item_strings)

                    # If after processing the list, it's still empty, use string representation of raw_answer
                    if not final_output_value: # Catches "" if extracted_item_strings was empty
                        final_output_value = str(raw_answer) # e.g., if raw_answer was [], becomes "[]"

                else: # raw_answer is not a list (e.g., string, int, dict directly)
                    final_output_value = str(raw_answer)
            else: # No 'answer' key in value_dict
                final_output_value = '--' # User requested default if 'answer' key is missing

            # Final check for any remaining empty/None values, including '[]' and '{}' string representations
            if final_output_value is None or final_output_value == '' or final_output_value == 'None' or final_output_value == '[]' or final_output_value == '{}':
                final_output_value = '--'

            d[key] = final_output_value

        return d
    
    except Exception as e:
        with open('dataT-answer-onresponse.json', "w", encoding="utf-8") as f:
            json.dump(dffT, f, indent=4, ensure_ascii=False)
        return {'Err': str(e)}

# getlistdata buat ambil semua list di survey itu, kalo ini search by id
def getdataReview(namafile='data_survey.json'):
    '''Function untuk mengambil data permukaan aja, tanpa get isian dalemnya, sama kayak __get_list_data tpi search by id'''
    # Open the file and load its content
    with open(namafile, 'r') as file:
        df = json.load(file)
        # df = json.dumps(file)
    try:
        dff = json.loads(df['data'])
    except TypeError:
        dff = df['data']
    # remove unwanted key
    # rmkey = ['region','region_metadata','pre_defined_data','data']
    # for key in rmkey:
    #     dff.pop(key, None)
    try:
        listcol = ['_id','id', 'survey_period_id', 'mode','code_identity', 'assignment_status_id', 'assignment_status_alias', 
            'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 
            'date_created','date_modified', 'is_active', 'current_user_username','current_user_survey_role_name','locked_by_user', 'locked_by_another',
            'email','latitude','longitude','pending_upload_assignment_id']
        dff = {k: dff[k] for k in listcol if k in dff}
    except:
        dff = None
    return dff

def getdataPES(namafile='data_survey.json'):
    '''FUNCTION FOR GETTING DATA PES'''
    # Open the file and load its content
    with open(namafile, 'r') as file:
        df = json.load(file)
    dff = json.loads(df['data']['data'])['answers']
    dffT = {item["dataKey"]: item for item in dff}

    ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
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

    d['r1'] = dffT['name']['answer'] if 'name' in dffT else '--'
    d['r2'] = dffT['age']['answer'] if 'age' in dffT else '--'
    d['r3'] = dffT['sex']['answer'][0]['value'] if 'sex' in dffT and dffT['sex'].get('answer') else '--'
    d['r4'] = dffT['nationality']['answer'][0]['label'] if 'nationality' in dffT and dffT['nationality'].get('answer') else '--'
    d['r5'] = dffT['country_residence']['answer'][0]['label'] if 'country_residence' in dffT and dffT['country_residence'].get('answer') else '--'
    d['r5b'] = dffT['city_residence']['answer'][0]['label'] if 'city_residence' in dffT and dffT['city_residence'].get('answer') else '--'
    d['r6'] = dffT['main_purpose']['answer'][0]['value'] if 'main_purpose' in dffT and dffT['main_purpose'].get('answer') else '--'

    # BLOK2
    d['r7'] = dffT['port_entry']['answer'][0]['label'] if 'port_entry' in dffT and dffT['port_entry'].get('answer') else '--'
    d['r8'] = dffT['length_of_stay']['answer'] if 'length_of_stay' in dffT else '--'

    # main dest
    main_dest_kab_key = 'main_destination_kab'
    d['r9ab'] = dffT[main_dest_kab_key]['answer'][0]['label'] if main_dest_kab_key in dffT and dffT[main_dest_kab_key].get('answer') else '--'
    len_stay_main_dest_key = 'len_stay_main_dest'
    d['r9ac'] = dffT[len_stay_main_dest_key]['answer'] if len_stay_main_dest_key in dffT else '--'

    # other dest
    for i in range(1, 6):
        prov_key = f"other_destination_prov_{i}"
        # Check if the key exists and has a non-empty 'answer' list before attempting to access
        if prov_key not in dffT or not dffT[prov_key].get('answer'):
            continue

        # a = dffT[prov_key]['answer'][0]['label']
        # Keeping the original logic for skipping if label is default/empty, though direct `dffT` access might reduce this need
        # if a in ["", "Select an option", "Pilih salah satu"]:
        #    continue
        kab_key = f"other_destination_kab_{i}"
        d[f"r9b{i}"] = dffT[kab_key]['answer'][0]['label'] if kab_key in dffT and dffT[kab_key].get('answer') else '--'

        len_key = f"len_stay_other_dest_{i}"
        d[f"r9b{i}c"] = dffT[len_key]['answer'] if len_key in dffT else '--'

    # BLOK3
    for i in range(1,14):
        key_attr = f"tourism_attraction_{i:02}"
        d[f"r10.{i}.1"] = dffT[key_attr]['answer'][0]['value'] if key_attr in dffT and dffT[key_attr].get('answer') else '--'
        # jika ada terpilih
        if d[f"r10.{i}.1"] == '1':
            key_len = f"len_stay_tourism_{i}"
            d[f"r10.{i}.2"] = dffT[key_len]['answer'] if key_len in dffT else '--'

    #BLOK4
    # tidak semua datanya diambil sih
    for i in range(1,5):
        key_accom = f"accommodation_{i:02}"
        d[f"r11.{i}"] = dffT[key_accom]['answer'][0]['value'] if key_accom in dffT and dffT[key_accom].get('answer') else '--'
    use_tour_package_key = 'use_tour_package'
    d[f"r12"] = dffT[use_tour_package_key]['answer'][0]['value'] if use_tour_package_key in dffT and dffT[use_tour_package_key].get('answer') else '--'

    #BLOK5
    ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
    for id4 in ids4:
        if id4 in dffT: # Check if id4 exists in dffT
            if id4 == 'currency_spending':
                d[id4] = dffT[id4]['answer'][0]['label'] if dffT[id4].get('answer') else '--'
            elif id4 == 'var_spending':
                d[id4] = int(dffT[id4]['answer'].replace(',','')) if dffT[id4].get('answer') else '--'
            else:
                d[id4] = dffT[id4]['answer']
        else:
            d[id4] = '--' # Assign '--' if key not found in dffT

    #BLOK6
    main_occupation_key = 'main_occupation'
    d['r14'] = dffT[main_occupation_key]['answer'][0]['value'] if main_occupation_key in dffT and dffT[main_occupation_key].get('answer') else '--'
    # r15 skip (original comment)
    freq_visit_key = 'freq_visit'
    d['r16'] = dffT[freq_visit_key]['answer'] if freq_visit_key in dffT else '--'
    #
    for i in ['arrival', 'departure']:
        key_airline = f'airline_{i}'
        d[f'r18a_{i}'] = dffT[key_airline]['answer'][0]['label'] if key_airline in dffT and dffT[key_airline].get('answer') else '--'

        key_currency = f'currency_{i}'
        d[f'r18b_{i}'] = dffT[key_currency]['answer'][0]['label'] if key_currency in dffT and dffT[key_currency].get('answer') else '--'

        key_value = f'value_{i}'
        d[f'r18c_{i}'] = dffT[key_value]['answer'] if key_value in dffT else '--'

    #BLOK7
    for i in range(1,15):
        key_activities = f'activities_{i:02}'
        d[f'r19_{i}'] = dffT[key_activities]['answer'][0]['value'] if key_activities in dffT and dffT[key_activities].get('answer') else '--'
        #d[f'r19_{i}'] = page.locator(f"//div[@id='activities_{i:02}']//input[@type='checkbox']").is_selected() # Original commented out

    wonderful_indonesia_key = 'wonderful_indonesia'
    d['r20'] = dffT[wonderful_indonesia_key]['answer'][0]['value'] if wonderful_indonesia_key in dffT and dffT[wonderful_indonesia_key].get('answer') else '--'
    ecofriendly_principle_key = 'ecofriendly_principle'
    d['r21'] = dffT[ecofriendly_principle_key]['answer'][0]['value'] if ecofriendly_principle_key in dffT and dffT[ecofriendly_principle_key].get('answer') else '--'
    satisfaction_lvl_key = 'satisfaction_lvl'
    d['r22'] = dffT[satisfaction_lvl_key]['answer'][0]['value'] if satisfaction_lvl_key in dffT and dffT[satisfaction_lvl_key].get('answer') else '--'
    intention_to_visit_key = 'intention_to_visit'
    d['r23'] = dffT[intention_to_visit_key]['answer'][0]['value'] if intention_to_visit_key in dffT and dffT[intention_to_visit_key].get('answer') else '--'

    #BLOK8
    note_key = 'note'
    d['r24'] = dffT[note_key]['answer'] if note_key in dffT else '--'
    impression_key = 'impression'
    d['r25'] = dffT[impression_key]['answer'] if impression_key in dffT else '--'
    viplounge_key = 'viplounge'
    d['r26'] = dffT[viplounge_key]['answer'][0]['value'] if viplounge_key in dffT and dffT[viplounge_key].get('answer') else '--'

    # FINISH
    return d

def ver(instance, var=''): 
    '''Get a version app'''
    if var==1:
        instance.isdone = 0
        instance.log_message(f"Application version: {APP_VERSION}")
        instance.isdone = 1
    return APP_VERSION

def chromeport(instance, var=''): 
    '''Get a port of a chrome'''
    if var==1:
        instance.isdone = 0
        instance.log_message(f"Chrome Port: {CHROME_PORT}")
        instance.isdone = 1
    return CHROME_PORT

# =====================================================================
# FUNC SECTION MAIN FUNC, DONT DISTURB
# =====================================================================
# Function to get list data
def __get_list_data (instance, namadf,  mode="w", maxrow=0, sep=","):
    '''Get dataframe dari prelist link fasih untuk dijadikan bahan, kemudian export ke csv juga. '''
    instance.isdone=0
    try:
        p_instance, ctx, page = __get_playwright_page() #konek ke playwr
        target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        # get req payload from reloading page
        captured_req, api_url, api_payload, api_headers = __get_headers(page, target_url=target_url)
        
        # mod req
        api_payload['length'] = ROW_REQUEST 
        api_payload['start'] = 0 # 50 100 150 dst
        # get response first load
        resp = __run_api_request(instance, ctx, "post", api_url, target_id=None, payload=api_payload, headers=api_headers)
        if resp is None:
            raise ValueError("API tidak mengembalikan data (Response is None)")
        if 'success' in resp and resp['success'] in [False, "false"]:
            raise ValueError(resp['message'])
        # resp = json.loads(response_json)
        total_hit = resp.get('totalHit', 0)
        instance.log_message(f"# Total data terdeteksi: {total_hit}")

        # gatekeeper
        if total_hit > 1000: 
            instance.log_message(f"ERROR: Total data ({total_hit}) melebihi batas 1000!", "red_tag")
            raise ValueError("Silakan perkecil kriteria wilayah filter Anda di Fasih terlebih dahulu.")
        
        # lolos <=1000
        master_data_list = []
        data_awal = resp.get('searchData', []) 
        master_data_list.extend(data_awal)
        instance.log_message(f"# Get {ROW_REQUEST} batch data pertama")

        # LOOP PENCICILAN (Mulai dari start=50, karena start=0 sudah diambil di atas)
        start_point = ROW_REQUEST
        while start_point < total_hit:
            __check_stop(instance)
            page.goto(instance.getassets('index.html'))
            page.evaluate("document.body.setAttribute('data-status', 'running')")

            instance.log_message(f"# Get data next batch, start from: {start_point+1}...")
            api_payload['start'] = start_point
            
            # Jeda tipis-tipis (politeness policy) agar server tidak mendeteksi serangan
            time.sleep(random.uniform(1.5, 5.0))
            
            # Tembak API untuk batch sekarang
            resp_next = __run_api_request(instance, ctx, "post", api_url, target_id=None, payload=api_payload, headers=api_headers)
            if resp_next is None:
                raise ValueError("API tidak mengembalikan data (Response is None)")
            if 'success' in resp_next and resp_next['success'] in [False, "false"]:
                raise ValueError(resp_next['message'])
            # resp_next = json.loads(response_json_next)
            
            data_batch = resp_next.get('searchData', [])
            if not data_batch:
                instance.log_message('- Data (sudah) kosong, break')
                break # Jika di tengah jalan data kosong, hentikan loop
                
            master_data_list.extend(data_batch)
            instance.log_message(f"- Berhasil ambil {len(data_batch)} data. Total: {len(master_data_list)}")
            
            # Naikkan kelipatan start (0 -> 50 -> 100 -> 150 dst)
            start_point += ROW_REQUEST
        
        if master_data_list:
            df = pd.DataFrame(master_data_list)
            listcol = ['id', 'surveyPeriodId', 'codeIdentity', 'assignmentStatusId', 'assignmentStatusAlias', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'dateCreated', 'isActive', 'currentUserUsername','lockedByUser', 'lockedByAnother']
            df = df[[c for c in listcol if c in df.columns]]
            df['link'] = 'https://fasih-sm.bps.go.id/app/assignment/'+ df['surveyPeriodId'].astype(str) + "/" + df['id'].astype(str)

            # save as csv
            if mode=="w":
                df.to_csv(namadf, index=False, sep=sep, mode="w")
            elif mode=="a":
                df.to_csv(namadf, index=False, sep=sep, mode="a", header=False)

            # get csv jml row
            with open (namadf,'r') as file:
                reader = csv.reader(file)
                jml_brs = len(list(reader)) - 1 #minus header
            instance.log_message(f"Done. Link data saved to '{namadf}'. Total baris: {jml_brs}","green_tag")
            
            # return df
        else:
            instance.log_message("Tidak ada data yang berhasil dikumpulkan.", "red_tag")
            return None

        # with open("resp.json", "w", encoding="utf-8") as f:
        #     json.dump(response_json, f, indent=4, ensure_ascii=False)
        # instance.log_message('exportedddddddddddddddddd')

    except Exception as e:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        instance.log_message(f"# Terjadi error di thread getlistdata on line: {str(exc_tb.tb_lineno)} {e} ", "red_tag")
    finally:
        time.sleep(1)
        isdone(instance, page=page, output=True)
        # Selalu tutup p_instance di blok 'finally' agar tidak hang
        try:
            p_instance.stop()
            instance.log_message("Koneksi Playwright di thread ditutup.")
        except NameError:
            # Terjadi jika get playwright page() gagal total di awal
            pass

# Function penunjang approv (and get data)
def __run_api_request(instance, context, method, target_url, target_id, msg="", payload=None, filename="data_survey.json", headers="", prefix_log=''):
    """
    Fungsi tunggal untuk menangani GET dan POST request ke API BPS. Method: 'GET', 'GET2' atau 'POST'. 'GET' untuk Query Parameter (?assignmentId=123), 'GET2' untuk id di dalam URL path (/api/data/123)
    """
    log_message = instance.log_message
    try:
        method = method.upper()
        msg = method if msg == "" else msg
        
        # 1. AMBIL COOKIE CSRF (Dipakai bersama)
        csrf_token = ""
        for cookie in context.cookies():
            if cookie['name'] == 'XSRF-TOKEN': 
                csrf_token = unquote(cookie['value'])
                break
        
        # 2. SELEKSI HEADERS BERDASARKAN METHOD
        if headers == "":
            headers = {
                "X-XSRF-TOKEN": csrf_token,
                "Referer": "https://bps.go.id"
            }
            if method == "POST":
                headers["Content-Type"] = "application/json"

        log_message(f"{prefix_log}- Try {msg} request...")

        # 3. EKSEKUSI REQUEST (GET vs POST)
        if method == "POST":
            # Jika payload tidak diisi manual, buat payload default approval
            if not payload:
                status_approv = 'false' if 'revoke' in target_url else 'true' 
                payload = {
                    "assignmentId": target_id,
                    "statusApproval": status_approv,
                    "comment": "\"\""
                }
            response = context.request.post(target_url, headers=headers, data=payload, timeout=TIMEOUT_REQUEST)
            
        elif method == "GET":
            # Jika target_id dimasukkan sebagai Query Parameter (?assignmentId=123)
            response = context.request.get(target_url, headers=headers, params={"assignmentId": target_id},timeout=TIMEOUT_REQUEST) # ====== gaperlukah payload di GET? next
        elif method == "GET2":
            # Jika ID dimasukkan langsung di dalam URL path (misal: /api/data/123)
            url_with_id = f"{target_url}/{target_id}"
            response = context.request.get(url_with_id, headers=headers,timeout=TIMEOUT_REQUEST)
        
        else:
            log_message(f"{prefix_log}- Method {method} tidak didukung.")
            return None

        # 4. HANDLE RESPONSE (Dipakai bersama)
        if response.ok:
            response_json = response.json()
            log_message(f"{prefix_log}- {msg} success!")
            
            # Jika GET, simpan ke file JSON
            if method == "GET":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(response_json, f, indent=4, ensure_ascii=False)
                #log_message(f"- Data disimpan ke '{filename}'")
                
            return response_json
        else:
            log_message(f"{prefix_log}- {method} Gagal! Status: {response.status} - {response.text()}")
            return None

    except Exception as e:
        log_message(f"{prefix_log}- Error pada {method} request: {str(e).split('Call log:')[0]}")
        return None

# Function penunjang get header utk diinject
def __get_headers(page, target_url):
    # get header from reloading page
    # with page.expect_request(target_url) as req_info:
        # page.reload()
    # captured_req = req_info.value
    ## modded captured_req
    captured_req = []
    def request_handler (request):
        if target_url in request.url:
            captured_req.append(request)
    page.on('request',request_handler)
    page.reload()
    page.wait_for_load_state('networkidle') #get semua req dlu
    page.remove_listener('request',request_handler) #remove listener save memori
    if not captured_req:
        raise ValueError('No Match Request sent')
    captured_req = captured_req[-1]
    ##
    api_url = captured_req.url
    #### moded headers
    # moded payload
    api_payload = None
    if captured_req.post_data:
        try:
            api_payload = json.loads(captured_req.post_data)
        except json.JSONDecodeError:
            # Jika bukan JSON (misal form submission biasa), ambil text mentahnya
            api_payload = captured_req.post_data
    # moded headers
    api_headers = dict(captured_req.headers)  # Dibuat dict agar bisa di-pop
    pseudo_headers = [":authority", ":method", ":path", ":scheme", "content-length"]
    for key in pseudo_headers:
        api_headers.pop(key, None)
    # moded csrf token refreshing
    csrf_token = ""
    for cookie in page.context.cookies():
        if cookie['name'] == 'XSRF-TOKEN': 
            csrf_token = unquote(cookie['value'])
            break
    if csrf_token:
        api_headers["X-XSRF-TOKEN"] = csrf_token
    ### end moded headers
    return captured_req, api_url, api_payload, api_headers

# Lock untuk mengamankan penulisan dari beberapa thread sekaligus
csv_lock = threading.Lock()    
tab_lock = threading.Lock()
log_lock = threading.Lock()
hitapi_counter_lock = threading.Lock()
worker_resume_on_none = threading.Event()
worker_resume_on_none.set() # True berarti jalan, False berarti pause, butuh refresh
worker_resume_on_jeda = threading.Event()
worker_resume_on_jeda.set() # True berarti jalan, False berarti pause, jeda berkala
global_hitapi_counter = 0
global_hitretry = 0

# Function penunjang process per row
def __row_mainfunc(i, instance, lendf, dflist, idlog, filename, func, api_headers, cekapprov, idwork, cdp_url, 
                    single=False,method='get', target_url=None, payload=None):
    # Buat context dan tab baru khusus untuk thread ini agar tidak bentrok
    # instance.log_message(f"[tab:{idwork}] # {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | loading")
    
    __check_stop(instance)
    log_msg_list = []
    # Fungsi pembantu lokal agar kode di bawah tetap bersih
    def log_local(message, tag=None):
        log_msg_list.append((message, tag))
    class LogWrapper:
        def log_message(self, msg, tag=None): log_local(msg, tag)
    local_logger = LogWrapper()

    # Fungsi jeda
    def check_hitapi_rate_and_pause():
        global global_hitapi_counter
        # 1. Cek / Tunggu jika page utama sedang refresh until resume event di set kembali
        worker_resume_on_none.wait()
        worker_resume_on_jeda.wait()
        
        # 2. Hitung kelipatan 10 global
        with hitapi_counter_lock:
            global_hitapi_counter += 1
            current_count = global_hitapi_counter
            
        if current_count % 100 == 0 and current_count != 0:
            worker_resume_on_jeda.clear()
            instance.log_message(f'Udah hit: {current_count}, rehat dulu 30s-60s...','green_tag')
            instance.log_message(f'Bisa clear log biar ga berat...', 'green_tag')
            getrandomcat(instance)
            time.sleep(60)
            worker_resume_on_jeda.set() #resume, end jeda

        elif current_count % (10*MAX_WORKERS) == 0 and current_count != 0:
            worker_resume_on_jeda.clear()
            instance.log_message(f'Udah hit: {current_count}, rehat dulu 30s-60s...','green_tag')
            instance.log_message(f'Bisa clear log biar ga berat...', 'green_tag')
            getrandomcat(instance)
            time.sleep(30)
            worker_resume_on_jeda.set() #resume, end jeda

    with sync_playwright() as p_instance:
        ctx = None
        try:
            __check_stop(instance)
            # 0. CEK DAH APPROVED LOM ke1 -> pindah ke main thread, disini pengaman aja
            if dflist[i]['status_work'] in [True, "True"]:
                log_local(f"[tab:{idwork}] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Approv'd, skip")
                err_msg=None
                return
            # perlukah cek approv yg ke2? ======

            # 1. CONNECT CONTEXT
            with tab_lock:
                # p_instance = sync_playwright().start()
                browser = p_instance.chromium.connect_over_cdp(cdp_url)
                ctx = browser.contexts[0]#()
                # page = browser.contexts[0].new_page()
                time.sleep(0.2)  # Jeda mikro agar websocket browser stabil
        
            __check_stop(instance)
            # 2. FUNCTION TAMBAHAN HERE
            target_id = dflist[i]['id']
            if func:
                try:
                    base_url = "https://fasih-sm.bps.go.id/app/api/assignment-general/api/assignment/get-by-assignment-id"
                    response = __run_api_request(local_logger, ctx, method=method, target_url=base_url, target_id=target_id, msg=f"GetData-row-{i}", headers=api_headers, prefix_log=f'[tab:{idwork}] ')
                    
                    if response is None:
                        worker_resume_on_none.clear() # Perintahkan main thread untuk pause & refresh
                        worker_resume_on_none.wait()  # Worker ini ikut tertidur menunggu refresh selesai
                        raise ValueError("API tidak mengembalikan data (Response is None)")
                    if 'success' in response and response['success'] in [False, "false"]:
                        raise ValueError(response['message'])
                    
                    # ketika apireq get nya success, maka kesini, jika ga, skip. 
                    # get a dict value per row from web (init dict from func)
                    resultDict = func()

                    for key, value in resultDict.items():
                        if "err" in key.lower():
                            log_local(f"Ada error dengan value: {value}")
                            raise ValueError(f"Ada error dengan value: {value}")
                    
                    # Update data 
                    dflist[i].update(resultDict)
                    time.sleep(random.uniform(1, 2)) #kasih jeda
                    
                except ValueError as e: #err on resultDict 
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    err_msg = str(e).split("Stacktrace:")[0]
                    log_local(f"# Terjadi error on GetData [tab:{idwork}] on id: {target_id}")
                    log_local(err_msg, "red_tag")
                    
                    return

            # 3. PROSES APPROVE / REJECT
            if cekapprov != False:
                try:
                    if cekapprov == True:
                        payload = {
                            "assignmentId": target_id,
                            "statusApproval": 'true',
                            "comment": "\"\""
                        }
                        msg = f"Approving-row-{i}"

                    elif cekapprov == "Reject":
                        target_url = f"https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/get-button-approval?assignmentId={target_id}"
                        response = __run_api_request(local_logger, ctx, method="post", target_url=target_url, target_id=target_id, msg=f"Cek-status-row-{i}", payload={}, headers=api_headers, prefix_log=f'[tab:{idwork}] ') 
                        time.sleep(1)
                        
                        if response['data'] >= 2: # Sudah diapprove pengawas
                            target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/revoke-approval" # Revoke
                            response = __run_api_request(local_logger, ctx, method="post", target_url=target_url, target_id=target_id, msg=f"Revoking-row-{i}", headers=api_headers, prefix_log=f'[tab:{idwork}] ') 
                            time.sleep(1)
                        elif response['data'] == 1: 
                            pass
                        else: 
                            raise ValueError(f"{response['message']} - Error code {response['errorCode']}")

                        payload = {
                            "assignmentId": target_id,
                            "statusApproval": "false",
                            "comment": "\"\""
                        }
                        msg = f"Rejecting-row-{i}"
                    
                    # reject or approv
                    target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/approval"
                    response = __run_api_request(local_logger, ctx, method="post", target_url=target_url, target_id=target_id, msg=msg, payload=payload, headers=api_headers, prefix_log=f'[tab:{idwork}] ') 

                    if response is None:
                        worker_resume_on_none.clear() # Perintahkan main thread untuk pause & refresh
                        worker_resume_on_none.wait()  # Worker ini ikut tertidur menunggu refresh selesai
                        raise ValueError("API tidak mengembalikan data (Response is None)")
                            
                    if 'success' in response and response['success'] in [False, "false"]:
                        raise ValueError(response['message'])

                    time.sleep(random.uniform(1, 2)) #jeda

                except Exception as e:
                    err_msg = str(e).split("Stacktrace:")[0]
                    log_local(f"[tab:{idwork}] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Skip gabisa approv")
                    log_local(f"Error approv {e}", "red_tag")
                    
                    return

            # 4. JIKA GADA APA APA
            if not cekapprov and not func and not single: # artine ga approv ga get data juga
                log_local('NGAPAIN BRUH?', 'red_tag')
                return
                # log_local(f"[tab:{idwork}] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | bisa approv si") # buat coba2 tadi
                # check_hitapi_rate_and_pause()
                # time.sleep(2)
            elif single:
                try:
                    response = __run_api_request(local_logger, ctx, method=method, target_url=target_url, 
                                                target_id=target_id, msg=f"Do-row-{i}", headers=api_headers, 
                                                payload=payload, prefix_log=f'[tab:{idwork}] ')
                    
                    if response is None:
                        worker_resume_on_none.clear() # Perintahkan main thread untuk pause & refresh
                        worker_resume_on_none.wait()  # Worker ini ikut tertidur menunggu refresh selesai
                        raise ValueError("API tidak mengembalikan data (Response is None)")
                    if 'success' in response and response['success'] in [False, "false"]:
                        raise ValueError(response['message'])
                    
                    # ketika apireq get nya success, maka kesini tpi sementara single dikosongin
                    time.sleep(random.uniform(1, 3)) #kasih jeda
                    check_hitapi_rate_and_pause()
                    
                except ValueError as e: #err on resultDict 
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    err_msg = str(e).split("Stacktrace:")[0]
                    log_local(f"# Terjadi error on GetData [tab:{idwork}] on id: {target_id}")
                    log_local(err_msg, "red_tag")
                    return
            else: # artine ada hit api req
                # PANGGIL fungsi hitung & jeda sebelum request API
                check_hitapi_rate_and_pause()

            # 5. END RESULT IF SUCCESS
            err_msg = None

        except Exception as e:
            # if 'Server Not Found' in page.title(): 
            #     log_local(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
            #     return
            # page.goto(dflist[i]['link'])
            # try relogin sso ====== need update
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_local(f"# Terjadi error process row on line: {str(exc_tb.tb_lineno)} ")
            log_local(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                
        finally:
            with log_lock:
                log_local(f"[tab:{idwork}] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Done")
                # log to main app
                for msg, tag in log_msg_list: instance.log_message(msg, tag)
            # end and save to csv
            dflist[i]['status_work'] = err_msg if err_msg else True
            with csv_lock:
                dfbaru = pd.DataFrame(dflist)
                dfbaru.to_csv(filename, index=False)
            time.sleep(0.2)
            # context.close()

# Function approv (and get data)
def __mainfunc(instance, filename, cekapprov, mulai=0, func=None, idlog='codeIdentity', sep=','):
    '''Get data dari Fasih dengan membuka linknya dari dataframe df, kemudian export ke csv. Kemudian akan approv juga jika tercentang sekalian approv'''
    # konfig
    instance.isdone = 0

    try:
        p_instance, ctx, page = __get_playwright_page() #konek ke playwr
        if page:
            page.goto(instance.getassets('index.html'))
            page.evaluate("document.body.setAttribute('data-status', 'running')")
        # read data csv result from get list data
        try:
            df = pd.read_csv(filename, sep=sep)
            df = df.astype(str)
            if 'status_work' not in df.columns:
                df['status_work'] = ""
            kolwjb = {idlog, 'id'}
            #if idlog not in df.columns or 'id' not in df.columns:
            if not kolwjb.issubset(df.columns) :
                raise ValueError (f"Kolom '{idlog}' tidak ditemukan di csv, silakan update dulu")
            lendf = len(df)
            # make df as df list py
            dflist = df.to_dict(orient='records')
        except Exception as e:
            instance.log_message(f'ERROR: {e}', tag="red_tag")
            df = None
            dflist = None
            instance.isdone = 1
            return
        
        # cek approv or not
        if cekapprov == True: msgapprov = ' and approving'
        elif cekapprov == "Reject": msgapprov = ' and rejecting'
        else: msgapprov=""
        instance.log_message(f"# Loading for {lendf-int(mulai)} data, length dataframe: {lendf}-mulai data{msgapprov}...")

        # back first to fsh-sm
        history_length = page.evaluate("window.history.length")
        if history_length > 1:
            try:
                page.go_back(timeout=5000)
            except Exception:
                pass
        else: pass
        # get header from reloading page opened rn
        captured_req, api_url, api_payload, api_headers = __get_headers(page, page.url)
        time.sleep(1)
        # 1. Kembaliin ke page UI user (di tab yg page utama)
        page.goto(instance.getassets('index.html'))
        page.evaluate("document.body.setAttribute('data-status', 'running')")

        # start loop per df, ## UPDATED
        # 2. Tentukan Index Awal Loop
        if mulai < 0: 
            start_idx = -1
        else: 
            start_idx = mulai - 1
        row_indices = range(start_idx + 1, lendf)

        # 3. Jalankan Multi-tab Pekerja via ThreadPoolExecutor
        # Sesuaikan `max_workers` dengan kekuatan CPU/RAM (misal: 3 s.d 5 tab sekaligus)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # cek inputan tombol
            if not cekapprov and not func:
                raise ValueError ('Robot bingung mau ngapain, gada approv, gada getdata juga')
            futures = []
            # Set antrian ke worker
            for idx, i in enumerate(row_indices):
                # CEK approv lom ke 1, cek id jg
                if dflist[i]['status_work'] in [True, "True"]:
                    instance.log_message(f"[tab:0] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Approv'd, skip")
                    continue
                elif dflist[i]["id"] in [None, "", "skip", "SKIP",'-']:
                    instance.log_message(f"[tab:0] {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | No ID, skip")
                    continue
                # ngantri worker
                worker_id = (idx % MAX_WORKERS) + 1
                try:
                    f = executor.submit(
                        __row_mainfunc, i, instance, lendf, dflist, idlog, filename, func, 
                        api_headers, cekapprov, worker_id, CHROME_PORT
                    ) 
                    futures.append(f)
                    # instance.log_message(f"Baris index-{i} berhasil didaftarkan ke Worker {worker_id}")
                    # time.sleep(0.2) # Jeda mikro pendaftaran
                except Exception as e_submit:
                    instance.log_message(f"Gagal memasukkan index-{i} ke Thread Pool: {e_submit}", "red_tag")

            instance.log_message(f"# {len(futures)} work mengantre ({MAX_WORKERS} tab)...")

            # Worker bekerja, sampai semua futures/antrean beres
            from concurrent.futures import wait, FIRST_COMPLETED
            # wait(futures, return_when=ALL_COMPLETED) #jika semua worker selesai, updated diganti bwh:
            curr_retry = 0
            while True:
                # Cek jika ada stop dari user mk batalkan antrean
                if instance.stop_event.is_set() or curr_retry>=MAX_RETRY:
                    if curr_retry >= MAX_RETRY:
                        instance.log_message(f'Sudah melebihi maksimal retry error ({MAX_RETRY})')
                    instance.log_message("Menghentikan seluruh antrean worker...", "red_tag")
                    for f in futures:
                        f.cancel() # Membatalkan antrean yang belum sempat berjalan oleh worker
                    break # Keluar dari loop pemantauan main thread
                
                # Cek apakah ada worker yang meminta pause untuk refresh page utama
                if not worker_resume_on_none.is_set():
                    instance.log_message("Worker mendeteksi API None. Merefresh page utama...", "red_tag")
                    try:
                        # === REFRESH PAGE UTAMA DISINI ===
                        page.go_back(timeout=10000)
                        time.sleep(5)
                        page.reload()
                        time.sleep(5)
                        page.goto(instance.getassets('index.html'))
                        page.evaluate("document.body.setAttribute('data-status', 'running')")
                        time.sleep(2)
                        curr_retry += 1
                        # =================================
                    except Exception as e:
                        instance.log_message(f"Gagal refresh page utama: {e}", "red_tag")
                    finally:
                        instance.log_message("Refresh selesai. Melanjutkan worker...")
                        worker_resume_on_none.set() # Bangunkan semua worker
                
                time.sleep(random.uniform(0.5, 0.9)) 
                # Cek status futures dengan timeout pendek agar loop tetap berjalan
                done, not_done = wait(futures, timeout=1.5, return_when=FIRST_COMPLETED)
                if len(not_done) == 0:
                    global_hitapi_counter = 0
                    break # Semua pekerjaan selesai
            
        # 4. Selesai Semua
        instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
        ##

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
        instance.log_message(f"Error di thread data __mainfunc: {e}", tag="red_tag")
    finally:
        # Selalu tutup p_instance di blok 'finally' agar tidak hang
        try: 
            instance.log_message('Removing temporary file')
            os.remove('data_survey.json')
        except: 
            instance.log_message("Ups, File emang gada")
        isdone(instance, page=page, output=True)
        try:
            p_instance.stop()
            instance.log_message("Koneksi Playwright di thread ditutup.")
        except NameError:
            # Terjadi jika get playwright page() gagal total di awal
            pass

def __get_playwright_page(cdp_url=CHROME_PORT):
    """
    Fungsi helper untuk connect ke browser Chrome yang sudah terbuka.
    Bisa dipanggil di thread mana saja.
    """
    try:
        p_instance = sync_playwright().start()
        browser = p_instance.chromium.connect_over_cdp(cdp_url, timeout=10000)
        context = browser.contexts[0]
        # Ambil page pertama yang aktif
        page = browser.contexts[0].pages[0]
        return p_instance, context, page
    except PlaywrightTimeoutError as e:
        # Jika gagal, pastikan instance playwright ditutup agar tidak memory leak
        if p_instance: p_instance.stop()
        if browser and not browser.contexts:
            raise RuntimeError("Browser terhubung tapi tidak ada context/halaman aktif")
        raise RuntimeError(f"Gagal connect ke browser: {e}")

def __check_stop(instance):
    '''Check if stop button is pressed'''
    if instance.stop_event.is_set():
        raise InterruptedError("Process stopped by user.")

def isdone(instance, page=None,output=None):
    '''Alternatif instance.isdone=1 karena bug'''
    instance.change_status("STATUS: DONE! Running selesai", color="green")
    instance.set_button_disabled(instance.btn_stop_app,disabled=True, active_bg=instance.BG_INPUT)
    if page:
        page.goto(instance.getassets('index.html'))
        page.evaluate("document.body.setAttribute('data-status', 'done')")
    if output:
        instance.log_message(f"Running program berhasil diproses. Cek file output", tag="green_tag")        
    else:
        instance.log_message(f"Running program berhasil diproses. Cek file output", tag="green_tag")        
