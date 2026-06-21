# app.py, kode coba2 get response, mungkin bisa updated
# find komen ====== for needed update or needed parsing to main py (app_autof.py -> Auto_Fasih_SM.py // get_data.py -> willbe in dist)
# find komen BAB untuk setiap func, yg harusnya diiringi run_*()
# 
import subprocess

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
import time
import os
import pandas as pd


def get_credentials():
        try:
            path = os.path.join(os.getcwd(), 'tempuser.txt')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    lines = f.read().splitlines()
                    return lines[0], lines[1], lines[2], "Loaded"
        except: pass
        return "jey.neutron", "password", "approv1", "Default"

def get_playwright_page(cdp_url="http://localhost:9222"):
    """
    Fungsi helper untuk connect ke browser Chrome yang sudah terbuka.
    Bisa dipanggil di mana saja.
    """
    p_instance = sync_playwright().start()
    try:
        print("Mengecek browser yang terbuka...")
        browser = p_instance.chromium.connect_over_cdp(cdp_url)
        # Ambil page pertama yang aktif
        page = browser.contexts[0].pages[0]
        print("Berhasil terhubung ke browser yang sudah ada!")
        return p_instance, browser, page
    except Exception as e:
        print("Browser tidak ditemukan. Membuka browser baru...")
        subprocess.Popen(r'start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"', shell=True)
        time.sleep(5)
        # Loop sampai port aktif
        import socket
        port_siap = False
        while not port_siap:
            try:
                with socket.create_connection(("127.0.0.1", 9222), timeout=1):
                    port_siap = True
            except (ConnectionRefusedError, socket.timeout):
                time.sleep(0.5) # Cek ulang setiap 0.5 detik
        try:
            browser = p_instance.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            print("Berhasil terhubung ke browser baru!")
            return p_instance, browser, page
        except Exception:
            print("Gagal terhubung ke Chrome. Pastikan port 9222 tidak diblokir.")

def log_message(txt, tag=''): #fungsi biar jalan aja dulu
    print('# '+ str(txt))

# --- BAB ADD PENAWARAN MITRA ---
def run_addpenawaran(page):
    namafile = 'tempdata.csv'
    df = pd.read_csv(namafile)
    log_message('csv read')
    gagal = 0
    j = 0
    
    for i in range(len(df)):
        log_message(f"# {df.loc[i, 'Nama']} otw")

        if df.loc[i, 'status'] == 'skip' or df.loc[i, 'status'] == 'done' or df.loc[i, 'status'] == 'kosong':
            log_message('already done')
            continue
        page.get_by_role("textbox", name="Cari").click()
        page.get_by_role("textbox", name="Cari").fill(df.loc[i, 'Nama'])
        time.sleep(1)
        try:
            # el = page.locator("div:nth-child(2) > .col-12.col-md-6")
            el = page.locator("div").filter(has_text=df.loc[i, 'Nama'][:17] ).first
            try:
                el.wait_for(timeout=1000, state="visible")
            # if el.count() > 0:
                stat = el.first.text_content() 
                if 'Sudah Terdaftar' in stat:
                    df.loc[i,'status'] = 'skip'
                    log_message('sudah daftar')
                    df.to_csv(namafile)
                    continue
                page.locator(".fa.fa-plus.text-success").click()
                df.loc[i,'status'] = 'done'

                j += 1
                time.sleep(0.5)

            # else:
            except PlaywrightTimeoutError:
                df.loc[i,'status'] = 'kosong'
                log_message('kosong')
                df.to_csv(namafile)
                continue
            
        except Exception as e:
            df.loc[i, 'status'] = 'error'
            log_message(e)
            gagal +=1
            if gagal > 3: break
            df.to_csv(namafile)
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
            df.to_csv(namafile)
            j=0
            # break
            continue


    log_message('SLESE')
# --- END ADD PENAWARAN ---


# --- BAB EMAIL FASIH BC---
def run_emailbc(namafile, page):
    """df columns: nama,idsbr,email"""
    #id = "5103020002000305 - UMK - 26"
    #id = "5103010006001218 - UMK - 10"
    #email="niluhsekarastuti96@gmail.com"

    ggl = 0
    sks = 0
    df = pd.read_csv(namafile, dtype=str)#.astype(str)
    
    if 'approved' not in df.columns:
        df['approved'] = ""
    # print(df.head(5))

    for i in range(len(df)):
        # cek done yet
        if df.loc[i, 'approved'] == 'done':
            log_message(f"# {i,str(df['nama'][i])[:20]} | Dah dieksekusi, skip")
            sks+=1
            continue
        if df.loc[i, 'idsbr'] == '' or pd.isna(df.loc[i, 'idsbr']) or df.loc[i, 'idsbr'] == 'nan':
            log_message(f"# {i,str(df['nama'][i])[:20]} | Not found idsbr")
            continue
        

        id = df['idsbr'][i]
        email = str(df['email'][i]).lower()
        if email == "" or email == '-':
            log_message(f"# {i,str(df['nama'][i])[:20]} | Not found email")
            continue

        log_message(f"# {i,str(df['nama'][i])[:20]} | {df['idsbr'][i]} {df['email'][i]}")
        try:
            page.get_by_role("textbox", name="Cari...").click()
            page.get_by_role("textbox", name="Cari...").fill(id)
            time.sleep(2)
            #page.get_by_role("button", name=id).click()
            page.get_by_role("cell", name=id).click(button="right")
            page.get_by_role("menuitem", name="Pengaturan Email").click()
            time.sleep(1)

            # cek dlu apakah sama emailnya
            email_locator = page.locator("span").filter(has_text=email)
            # Cek apakah elemen tersebut ada di halaman (jumlahnya lebih dari 0)
            if email_locator.count() > 0:
                log_message("- Email sama. Skip / Continue ke proses berikutnya.")
                # Gunakan 'continue' jika kode ini berada di dalam perulangan (loop)
                # continue  
            else:
                log_message("- Eksekusi kode...")
                page.get_by_role("button", name="Ganti Email").click()
                page.get_by_role("textbox", name="Ganti Email").click()
                page.get_by_role("textbox", name="Ganti Email").fill(email)
                time.sleep(1)
                page.get_by_role("button", name="Ganti Email").click()
                page.get_by_role("button", name="Broadcast Email").click()
                page.get_by_role("button", name="Broadcast Email").click()
                time.sleep(1)
                teks_toast = page.locator("li[data-sonner-toast][data-front='true']").inner_text()
                print(f"Status {id}: {teks_toast}")                    
                
            time.sleep(1)
            page.keyboard.press("Escape")
            #page.get_by_role("button", name="Close").click()
            time.sleep(1)
            df.loc[i, 'approved'] = 'done'
            sks += 1

        except Exception as e:
            ggl += 1
            if ggl%10 == 0:
                break

            log_message(f"# {i,str(df['nama'][i])[:20]} | ERRR")
            log_message(f"Error: {e}")
            df.loc[i, 'approved'] = 'error'
            time.sleep(2)
            continue

        finally:
            df.to_csv(namafile, index=False)
    print(f"gagal:{ggl}, sukses:{sks}")
    # --- ENDEMAIL FASIH BC ---


# --- BAB REQ API ---
from urllib.parse import unquote

def run_api_request(page, method, target_url, target_id, msg="", payload=None, filename="data_survey.json"):
    """
    Fungsi tunggal untuk menangani GET dan POST request ke API BPS.
    method: 'GET' atau 'POST'
    """
    try:
        method = method.upper()
        msg = method if msg == "" else msg
        
        # 1. AMBIL COOKIE CSRF (Dipakai bersama)
        csrf_token = ""
        for cookie in page.context.cookies():
            if cookie['name'] == 'XSRF-TOKEN': 
                csrf_token = unquote(cookie['value'])
                break
        
        # 2. SELEKSI HEADERS BERDASARKAN METHOD
        headers = {
            "X-XSRF-TOKEN": csrf_token,
            "Referer": "https://bps.go.id"
        }
        if method == "POST":
            headers["Content-Type"] = "application/json"

        log_message(f"- Try {msg} request...")

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
            response = page.request.post(target_url, headers=headers, data=payload)
            
        elif method == "GET":
            # Jika target_id dimasukkan sebagai Query Parameter (?assignmentId=123)
            response = page.request.get(target_url, headers=headers, params={"assignmentId": target_id}) # ====== gaperlukah payload di GET? next
        elif method == "GET2":
            # Jika ID dimasukkan langsung di dalam URL path (misal: /api/data/123)
            url_with_id = f"{target_url}/{target_id}"
            response = page.request.get(url_with_id, headers=headers)
        
        else:
            log_message(f"- Method {method} tidak didukung.")
            return None

        # 4. HANDLE RESPONSE (Dipakai bersama)
        if response.ok:
            response_json = response.json()
            log_message(f"- {msg} success!")
            
            # Jika GET, simpan ke file JSON
            if method == "GET":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(response_json, f, indent=4, ensure_ascii=False)
                #log_message(f"- Data disimpan ke '{filename}'")
            
            # Jika POST, lakukan UI refresh halaman
            # elif method == "POST":
            #     page.reload()
            #     page.locator("h1").first.wait_for(state="visible", timeout=10000)
                
            return response_json
        else:
            log_message(f"- {method} Gagal! Status: {response.status} - {response.text()}")
            return None

    except Exception as e:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_message(f"- Terjadi error pada {method} req on line: {str(exc_tb.tb_lineno)} {e} ")
        # log_message(f'- Error pada {method} request: {e}')
        return None

    # --- END REQ API ---

# --- BAB FUNC REALOKASI N REASSIGN ---
def run_resubs(realokasisubs,namafile, delete_assignment=False):
    df = pd.read_csv(namafile)
    lendf = len(df)
    print('\n')
    if 'KET' not in df.columns:
        df['KET'] = ''
    for i in range(len(df)):
        nm = df.loc[i,'Nama Perusahaan']
        idsubs = df.loc[i,'idsubsls']
        idsubs = str(idsubs).strip()
        idcari = df.loc[i,'idd']
        if idcari == '' or pd.isna(idcari) or idcari=='v': #jika gada yg dicari, skip
            continue
        if '5103' not in str(idsubs):
            if delete_assignment and 'delete' in str(idsubs):
                pass
            else:
                print(f'# Skip idsubs not valid: {nm}')
                continue
        if df.loc[i,'KET'] == 'done' or 'skip' in str(df.loc[i,'KET']): #jika udah or flag skip, mk skip
            print(f'# Skip: {nm}')
            continue
        
        # Proses pemotongan teks (Slicing Python)
        kdprov   = idsubs[:2]        # LEFT($A2:A,2)
        kdkab  = idsubs[2:4]       # RIGHT(LEFT($A2:A,4),2)
        kdkec  = idsubs[4:7]       # RIGHT(LEFT($A2:A,7),3)
        kddes = idsubs[7:10]      # RIGHT(LEFT($A2:A,10),3)
        kdsls = idsubs[10:14]     # RIGHT(LEFT($A2:A,14),4)
        kdsubs = idsubs[14:16]     # RIGHT(LEFT($A2:A,16),2)

        # CARI
        print(f'# {i}/{lendf}| Processing {nm}, to {idsubs} with id {idcari}')
        try:
            page.get_by_role("textbox", name="Cari...").click()
            page.get_by_role("textbox", name="Cari...").fill(idcari)
            time.sleep(1)
            page.get_by_role("button", name=idcari).click(button="right")#, timeout=10000)
        except Exception as e:
            print(f'Tidak ditemukan: {e}')
            df.loc[i,'KET'] = 'kosong'
            continue

        try:
            # DELETE ASSIGNMENT FLAGGED DELETE
            if 'delete' in str(idsubs) and delete_assignment:
                page.get_by_role("menuitem", name="Hapus Assignment").click()
                time.sleep(0.5)
                page.get_by_role("button", name="Ya, Hapus Assignment").click()
                time.sleep(1)
                teks_toast = page.locator("li[data-sonner-toast][data-front='true']").inner_text()
                print(f"Status {nm}: {teks_toast}")                    
                df.loc[i,'KET'] = 'done'
                time.sleep(1)
                continue

            # REALOKASI SUB
            if realokasisubs:
                page.get_by_role("menuitem", name="Ganti Wilayah").click()
                time.sleep(1)

                page.get_by_role("combobox").first.click()
                page.get_by_label("", exact=True).fill(kdprov)
                page.get_by_label("", exact=True).press("Enter")
                time.sleep(0.5)
                page.get_by_role("combobox").nth(1).click()
                page.get_by_label("", exact=True).fill(kdkab)
                page.get_by_label("", exact=True).press("Enter")
                time.sleep(0.5)
                page.get_by_role("combobox").nth(2).click()
                page.get_by_label("", exact=True).fill(kdkec)
                page.get_by_label("", exact=True).press("Enter")
                time.sleep(0.5)
                page.get_by_role("combobox").nth(3).click()
                page.get_by_label("", exact=True).fill(kddes)
                page.get_by_label("", exact=True).press("Enter")
                time.sleep(0.5)
                page.get_by_role("combobox").nth(4).click()
                page.get_by_label("", exact=True).fill(kdsls)
                page.get_by_label("", exact=True).press("Enter")
                time.sleep(0.5)
                page.get_by_role("combobox").filter(has_text="Pilih wilayah").click()
                page.get_by_label("", exact=True).fill(kdsubs)
                page.get_by_label("", exact=True).press("Enter")
                time.sleep(0.5)
                # page.get_by_role("button", name="Ubah Wilayah Assignment").click()
                # page.get_by_role("button", name="Close toast").click()
                # Mengambil teks yang terlihat oleh pengguna di layar
                # time.sleep(1)
                # time.sleep(1)

                # ASSIGN
                # page.get_by_role("button", name=idcari).click(button="right")
                # page.get_by_role("menuitem", name="Assign Petugas").click()
                page.get_by_role("combobox", name="Pengawas").click()
                page.get_by_role("option").first.click()
                time.sleep(0.5)
                page.get_by_role("combobox", name="Pencacah").click()
                page.get_by_role("option").first.click()
                # page.get_by_role("button", name="Assign Petugas").click()
                page.get_by_role("button", name="Ubah Wilayah Assignment").click()
                time.sleep(1)
                teks_toast = page.locator("li[data-sonner-toast][data-front='true']").inner_text()
                print(f"Status REALOKASI: {teks_toast}")
                # teks_toast = page.locator("li[data-sonner-toast][data-front='true']").inner_text()
                # print(f"Status ASSIGN: {teks_toast}")
                time.sleep(1)
            
            else: #if assign_only
                # page.get_by_role("button", name=idcari).click(button="right")
                page.get_by_role("menuitem", name="Assign Petugas").click()
                page.get_by_role("combobox", name="Pengawas").click()
                page.get_by_role("option").first.click()
                time.sleep(0.5)
                page.get_by_role("combobox", name="Pencacah").click()
                page.get_by_role("option").first.click()
                page.get_by_role("button", name="Assign Petugas").click()
                # page.get_by_role("button", name="Ubah Wilayah Assignment").click()
                time.sleep(1)
                teks_toast = page.locator("li[data-sonner-toast][data-front='true']").inner_text()
                # print(f"Status REALOKASI: {teks_toast}")
                # teks_toast = page.locator("li[data-sonner-toast][data-front='true']").inner_text()
                print(f"Status ASSIGN: {teks_toast}")
                if 'sudah di assign' in teks_toast:
                    page.keyboard.press("Escape")
                time.sleep(1)

            df.loc[i,'KET'] = 'done'
        
        except Exception as e:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"# Terjadi error on line: {str(exc_tb.tb_lineno)} {e} ")
            df.loc[i,'KET'] = f'Err line {exc_tb.tb_lineno} ({e})'
            continue
    
        df.to_csv(namafile,index=False)

    print('seleseeeeeee')

# --- END FUNC REALOKASI N REASSIGN ---

# --- BAB FUNC GET SUBS FROM COORDINATE ---
from shapely import wkt
def get_subsls(coord_text, df):
    if 'skip' in str(coord_text) or 'delete' in str(coord_text):
        return coord_text
    if pd.isna(coord_text) or not coord_text:
        return "Koordinat Kosong"
        
    try:
        # 1. Ubah teks "-8.58, 115.21" menjadi objek Point Shapely (lon dulu baru lat)
        coorsplit = coord_text.split(",")
        point = wkt.loads(f"Point({coorsplit[1].strip()} {coorsplit[0].strip()})")
        
        # 2. Cari polygon yang membungkus point tersebut
        matches = df['polygon'].apply(lambda poly: point.within(poly))
        matching_rows = df[matches]
        
        # 3. Jika ketemu, ambil teks info SLS yang diinginkan
        if not matching_rows.empty:
            row = matching_rows.iloc[0]
            # return f"{row['nmsls']}, Desa {row['nmdesa']}, Kec. {row['nmkec']}"
            return row['idsubsls']
        else:
            return "Di luar Kabupaten Badung"
            
    except Exception as e:
        return "Format Koordinat Salah"
# --- END FUNC GET SUBS ---


# --- BAB FUNC APUS ASSIGNMENT ---
# def run_apus_assign(page):
#     #1. Klik tombol bin (sel kosong / target)
#     import re
#     out = 5000
#     try:
#         while True:
#             page.get_by_role("cell").nth(4).click(timeout=out) #bin btn
#             print('\na. delete btn user click')

#             # Ambil semua elemen tombol untuk dicek jumlahnya
#             time.sleep(1)
#             tombol_step2 = page.get_by_role("button") #cek jml nth
#             jumlah_tombol = tombol_step2.count()

#             # JIKA jumlah tombol lebih dari 1, jalankan Step 2
#             # i = jumlah_tombol
#             print(f'a. loop {jumlah_tombol}x')
#             for i in range(1,jumlah_tombol):
#                 if jumlah_tombol == 2: break
#                 if jumlah_tombol > 1:
                    
#                     time.sleep(1)
#                     try:
#                         tombol_step2.nth(i).click(timeout=out) # 2. Klik foreach nth di sana
#                         print(f'b. tombol delete wil ke-{i}')
#                         time.sleep(0.5)
#                         page.get_by_role("button", name="Hapus").click(timeout=out) # konfirm apus
#                         print('c. konfirm delete wil')

#                     except:
#                         time.sleep(0.5)
#                         page.get_by_role("button", name="Hapus").click(timeout=out) # konfirm apus
#                         print('c. konfirm delete wil')
                    
#                     time.sleep(1)
#                     if jumlah_tombol-1 == i: 
#                         # page.get_by_role("button", name="Close").click()
#                         break
#                     page.get_by_role("cell").nth(4).click(timeout=out) #bin btn, then loop foreach
#                     print('\na. delete btn user click')
#                     # i -= 1
                    
#                 # if i == 1: break

#             # 3. Tiap foreach ada konfirmasi hapus (Selalu dijalankan)
#             page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(4).click(timeout=out) #refresh 2x
#             page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(4).click(timeout=out)
#             print('selese --- endings')
#             page.get_by_role("cell").nth(4).click(timeout=out) #bin btn
#             time.sleep(0.2)
#             try:
#                 page.get_by_role("button", name="Hapus").click(timeout=out) #langsung apus
#             except:
#                 continue

#             page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(4).click(timeout=out) #refresh 2x
#             page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(4).click(timeout=out)
#             print('refresh')
#             time.sleep(2)

#     except Exception as e:
#         print(e)
#         import sys
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(f"# Terjadi error di thread getlistdata on line: {str(exc_tb.tb_lineno)} {e} ")
# --- BAB FUNC APUS ASSIGNMENT ---


# --- BAB GET LIST DATA BY SEARCH ---
def run_getlist_search(page, df):
    target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
    # get req payload
    with page.expect_request(target_url) as req_info:
        page.reload()
    time.sleep(1)
    captured_req = req_info.value
    api_url = captured_req.url
    api_headers = captured_req.headers
    api_payload = json.loads(captured_req.post_data)
    # log_message(api_payload)

    # mod req
    per_batch=10
    api_payload['length'] = per_batch 
    # api_payload['start'] = 0 # 50 100 150 dst

    # read df n loop per df
    if 'id' not in df.columns:
        df['id'] = ''
        df['codeIdentity'] =''
    # rows=[]
    for i in range(0,len(df)):
        if pd.notna(df.loc[i, 'codeIdentity']) and df.loc[i, 'codeIdentity'] != '-': #artine udah isi maka skip
            log_message(f"# {i,str(df['nama'][i])[:20]} | skip")
            continue
        time.sleep(1)
        msg = 'belum'
        if df.loc[i, 'idsbr'] == '' or pd.isna(df.loc[i, 'idsbr']) or df.loc[i, 'idsbr'] == 'nan':
            msg = 'idsbr not found'
            log_message(f"# {i,str(df['nama'][i])[:20]} | {msg}")
            continue
        search_value = str(df.loc[i,'idsbr'])
        api_payload['search']['value'] = search_value

        # get response on load
        resp = run_api_request(page, "post", api_url, target_id=None, payload=api_payload)
        # found = False
        # resp = json.loads(resp)
        # total_hit = resp.get('totalHit', 0)

        # Lakukan perulangan untuk mengecek setiap data resp
        try:
            for item in resp.get("searchData",[]):
                log_message(f'- Response {per_batch} idsbr: {item.get("data3")} == {search_value} ?')
                if str(search_value) in str(item.get("data3")):
                    
                    # Logika untuk membuat 'idsub' dari 'codeIdentity'
                    code_id = item.get("codeIdentity", "")
                    idsub = code_id[:16] if code_id.startswith("5103") else "-"

                    data_terpilih = {
                        "id": item.get("id"),
                        "codeIdentity": code_id,
                        "idsub": idsub,
                        "assignmentStatusAlias": item.get("assignmentStatusAlias"),
                        "data1": item.get("data1"),
                        "data2": item.get("data2"),
                        "data3": item.get("data3"),
                        "data6": item.get("data6"),
                        "currentUserUsername": item.get("currentUserUsername"),
                        "currentUserSurveyRoleName": item.get("currentUserSurveyRoleName")
                    }
                    
                    # Masukkan ke dalam list hasil
                    # rows.append(data_terpilih)
                    # found = True
                    msg = 'done'
                    break
            if msg == 'belum':
                # Isi dengan data kosong agar jumlah barisnya tetap pas dengan df_awal
                # rows.append({k: "-" for k in ["id", "codeIdentity", "idsub", "assignmentStatusAlias", "data1", "data2", "data3", "data6", "currentUserUsername", "currentUserSurveyRoleName"]})
                data_terpilih = {k: "-" for k in ["id", "codeIdentity", "idsub", "assignmentStatusAlias", "data1", "data2", "data3", "data6", "currentUserUsername", "currentUserSurveyRoleName"]}
                msg = 'failed'

            for key,value in data_terpilih.items():
                df.at[i, key] = value
            df.to_csv(namafile, index=False)
            log_message(f"# {i,str(df['nama'][i])[:20]} | {msg}")
        except Exception as e:
            import sys
            # log_message(f'Response: {resp}')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_message(f"# Terjadi error on line: {str(exc_tb.tb_lineno)} {e} ")
            df.at[i,'id']=str(e)
            # break
            time.sleep(5)
            page.reload()
            time.sleep(5)
            df.to_csv(namafile, index=False)
            continue
    
    # 4. Ubah list hasil ekstrak menjadi DataFrame baru
    # df_kolom_baru = pd.DataFrame(rows)

    # 5. TEMPELKAN kolom baru tersebut ke DataFrame awal (Menggabungkan ke samping)
    # df_akhir = pd.concat([df, df_kolom_baru], axis=1)
    df_akhir = df

    # Tampilkan hasil akhir
    return df_akhir

# --- END GET LIST DATA BY SEARCH ---


from PIL import Image, ImageDraw, ImageFont
import qrcode
import textwrap

def generate_custom_document(nama, data_qr, config, output_name):
    cfg = config
    try:
        img = Image.open(cfg["bg_path"])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(cfg['font_type'], cfg["font_size"])
    except Exception as e:
        print(f"❌ GAGAL LOAD FILE!")
        print(f"Jenis error: {type(e).__name__}")
        print(f"Detail error: {e}")
        return 

    # 1. Logika Nama Universal (Wrap & Inisial)
    words = nama.split()
    if len(nama) > 35: 
        nama = f"{' '.join(words[:-1])} {words[-1][0]}."
    
    lines = textwrap.wrap(nama, width=15)
    
    # 2. Gambar Teks (Centered)
    x1, y1, w_box, h_box = cfg["text_box"]
    x_center = x1 + (w_box / 2) 
    y_current = y1

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        
        draw.text((x_center, y_current), line, fill="black", font=font, anchor="ma")
        y_current += line_height + 10 

    # 3. Gambar QR Universal (Perbaikan Struktur Indeks agar Kernel Tidak Mati)
    qr = qrcode.make(data_qr)
    qr_width = cfg["qr_box"][2]
    qr_height = cfg["qr_box"][3]
    qr = qr.resize((qr_width, qr_height))
    
    # Hitung posisi paste QR
    qx = cfg["qr_box"][0] + (qr_width - qr.size[0]) // 2
    qy = cfg["qr_box"][1] + (qr_height - qr.size[1]) // 2
    
    img.paste(qr, (qx, qy))
    img.save(output_name)
    print(f"✅ Sukses! Dokumen disimpan dengan nama: {output_name}")

# path
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Contoh config untuk template yang berbeda
templates = {
    "id_card": {
        # "bg_path": os.path.join(BASE_DIR, "pelatihanSE", "cocard-template.png"),
        "bg_path": r"D:\jim\auto-fasih-sm\pelatihanSE\cocard-template.png",
        "text_box": (138, 813, 200, 970), # start x, start y, width box, len box
        "qr_box": (460, 1148, 330, 330),
        "font_size": 27,
        # "font_type": os.path.join(BASE_DIR, "pelatihanSE", "raleway-medium.ttf")
        "font_type": r"D:\jim\auto-fasih-sm\pelatihanSE\raleway-medium.ttf"
        # "font_type": "arial.ttf"
    }
}

# UNKOMENNNNN THISSSSSSSSSSSSSSSSSSSSSSSSSS
if __name__ == "__main__":
    # ===== RUN no need browser =====
    # generate_custom_document("Jey Neutron", "link_data", templates["id_card"], "hasil_cocard.png")
    
    # ===== RUN need browser =====
    p_instance, browser, page = get_playwright_page() #konek ke playwr
    
    # usersso, passso, approv, msgsso = get_credentials()  
    # # Interaksi Login #UPDATED LOGINNNNNN ======
    # print('# Goto web')
    # print('# Login SSO')
    # page.goto("https://fasih-sm.bps.go.id/oauth_login.html")
    # page.get_by_role("link", name="Login SSO BPS").click()
    # page.wait_for_load_state("networkidle", timeout=5000)
    # username_field = page.get_by_role("textbox", name="Username or email")
    # if username_field.count() > 0:
    #     username_field.click()
    #     username_field.fill(usersso)
    #     password_field = page.get_by_role("textbox", name="Password")
    #     if password_field.count() > 0:
    #         password_field.click()
    #         password_field.fill(passso)
    #     page.get_by_role("button", name="Log In").click()
    # print('# Logged in')
    # page.reload()
    print('Title page: ', page.title())
    # ===== MAIN FUNC =====

    # RUN change reg and assign
    # /master sls
    # from shapely import wkt
    # dfmaster = pd.read_csv(r"mfd_wilker25.csv")
    # dfmaster['polygon'] = dfmaster['WKT'].apply(wkt.loads)

    # df = pd.read_csv('temp.csv') # columns: Nama Perusahaan, idd, idsubsls, coordinate, KET
    # df['idsubsls'] = df['coordinate'].apply(lambda x:  get_subsls(x, df=dfmaster))
    # df.to_csv('temp.csv', index=False)
    # print('done, cek file')

    # /resub
    # run_resubs(namafile='temp.csv', realokasisubs=True, delete_assignment=True), #assign petugas pake yg first muncul

    # RUN Email broadcast fasih
    # alt 1
    #df: nama, idsbr, email
    # namafile = 'temp.csv'
    # run_emailbc(namafile)
    # log_message('FINISIHED')
    # alt 2
    # 1. Change email
    # target_url = "https://fasih-sm.bps.go.id/app/api/email/api/v2/assignment/change-email?newPin=false"
    # payload = {
    #     "assignmentId": "3adf0903-c295-4584-b3aa-3a3190e5bc23",
    #     "surveyPeriodId": "fd68e454-ba45-4b85-8205-f3bf777ded24",
    #     "email": "deliamanda1218@gmail.com",
    #     "reminder": False
    #     }
    # cek sukses is True
    # run_api_request(page, "post", target_url, )
    # 2. Send email
    # target_url = "https://fasih-sm.bps.go.id/app/api/email/api/v1/assignment/send-email-by-assignment?newPin=false"
    # payload = {
    #     "reminder": False,
    #     "surveyPeriodId": "fd68e454-ba45-4b85-8205-f3bf777ded24",
    #     "assignmentIds": [
    #         "3adf0903-c295-4584-b3aa-3a3190e5bc23"
    #     ]
    #     }
    # cek sukses is True

    # RUN add penawaran
    # run_addpenawaran()

    # RUN get list data by search
    namafile = 'temp.csv'
    df = pd.read_csv(namafile)
    df2 = run_getlist_search(page, df)
    df2.to_csv(namafile, index=False)

    # ===== END MAIN FUNC =====
    # page.pause() #debugging, open recorder on playwright