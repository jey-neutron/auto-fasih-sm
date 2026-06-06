APP_VERSION = 'v2.3.0' 
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
# harus ada di mainapp, import fitur added
from lzstring import LZString
import ast
import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap
    

###################################
# FUNC DRAFT 
###################################

# def inputwebdash(instance, var)
# def assignselect(instance, var)
# def mailbc(instance, var) # mybe, buat ngibar paling, ref from appdev.py ======
# def getnikmitra(instance, var):
#     try:
#         with open(r'D:\OneDrive\~Jimmy\~STIS\PY\Work_py\auto-fasih-sm\dist\temp.json', 'r', encoding='utf-8') as file:
#         df = json.load(file)
        
#         # send and get response (get data detail all)
#         base_url = "https://mitra-api.bps.go.id/api/mitra/reveal-info/nik"
#         response = run_api_request(instance, page, method="get", target_url=base_url, target_id=target_id, msg=f"GetNIK-row-{i}")
#         if response is None:
#             raise ValueError("API tidak mengembalikan data (Response is None)")
#         if response['success'] == False or response['success'] == "false":
#             raise ValueError(response['message'])


###################################
# FUNC INTRODUCTION 
###################################

def ver(instance, var=''): 
    '''Get a version app'''
    if var==1:
        instance.isdone = 0
        instance.log_message(f"Application version: {APP_VERSION}")
        instance.isdone = 1
    return APP_VERSION

def help(instance,var=''):
    '''Get list of functions'''
    exclude_fun_list = ["mainfunc", "get_list_data", "datetime", "sync_playwright","check_stop", "handle_response", 
                        'mergejson','run_api_request','get_playwright_page','expect','unquote', 'PlaywrightTimeoutError',
                        'LZString']
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

def getrandom(instance, var): 
    '''Get a random number'''
    instance.isdone = 0
    check_stop(instance)
    for i in range(0,4):
        time.sleep(1)
        try:
            instance.log_message(f"Hasil angka random-{i} {int(var)*random.random()}")
        except:
            instance.log_message(f"Hasil angka random-{i} {random.random()}")
    instance.isdone = 1

def render(instance,var):
    """Memanggil index.html dengan pilihan variable terlampir var='done', 'running', 'ready' """
    p_instance, browser, page = get_playwright_page() #konek ke playwr
    instance.log_message(f'Rendering HTML. Var="done", "running", "ready". Chosen: {var} ')
    page.goto(instance.getassets('index.html'))
    if var != 1:
        page.evaluate(f"document.body.setAttribute('data-status', '{var}')")
    instance.log_message('Selesai')
    #instance.isdone=1
    

###################################
# FUNC SECTION MANAJEMEN MITRA
###################################
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
    p_instance, browser, page = get_playwright_page() #konek ke playwr
    
    namafile = instance.filename_entry.get()
    df = pd.read_csv(namafile)
    if 'Nama' in df.columns:
        df = df.rename(columns={'Nama': 'nama'})

    log_message('csv read')
    gagal = 0
    j = 0
    
    for i in range(len(df)):
        check_stop(instance)
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
# END SECTION MANAJEMEN MITRA ###################################


###################################
# FUNC ADDED
###################################
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


###################################
# FUNC SECTION FUNGSI TAMBAHAN MAINFUNC 
###################################
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
# END SECTION FUNC TAMBAHAN MAINFUNC ###################################


###################################
# FUNC SECTION MAIN FUNC, DONT DISTURB
###################################
# Function to get list data
def get_list_data (instance, namadf,  mode="w", maxrow=0, sep=","):
    '''Get dataframe dari prelist link fasih untuk dijadikan bahan, kemudian export ke csv juga. '''
    instance.isdone=0
    try:
        p_instance, browser, page = get_playwright_page() #konek ke playwr
        target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        # get req payload
        with page.expect_request(target_url) as req_info:
            page.reload()
        time.sleep(1)
        captured_req = req_info.value
        api_url = captured_req.url
        api_headers = captured_req.headers
        api_payload = json.loads(captured_req.post_data)

        # mod req
        per_batch = 50
        api_payload['length'] = per_batch 
        api_payload['start'] = 0 # 50 100 150 dst
        # get response first load
        resp = run_api_request(instance, page, "post", api_url, target_id=None, payload=api_payload)
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
        instance.log_message(f"# Get {per_batch} batch data pertama")

        # LOOP PENCICILAN (Mulai dari start=50, karena start=0 sudah diambil di atas)
        start_point = per_batch
        while start_point < total_hit:
            check_stop(instance)
            page.goto(instance.getassets('index.html'))
            page.evaluate("document.body.setAttribute('data-status', 'running')")

            instance.log_message(f"# Get data next batch, start from: {start_point+1}...")
            api_payload['start'] = start_point
            
            # Jeda tipis-tipis (politeness policy) agar server tidak mendeteksi serangan
            time.sleep(random.uniform(1.5, 5.0))
            
            # Tembak API untuk batch sekarang
            resp_next = run_api_request(instance, page, "post", api_url, target_id=None, payload=api_payload)
            # resp_next = json.loads(response_json_next)
            
            data_batch = resp_next.get('searchData', [])
            if not data_batch:
                instance.log_message('- Data (sudah) kosong, break')
                break # Jika di tengah jalan data kosong, hentikan loop
                
            master_data_list.extend(data_batch)
            instance.log_message(f"- Berhasil ambil {len(data_batch)} data. Total: {len(master_data_list)}")
            
            # Naikkan kelipatan start (0 -> 50 -> 100 -> 150 dst)
            start_point += per_batch
        
        if master_data_list:
            df = pd.DataFrame(master_data_list)
            listcol = ['id', 'surveyPeriodId', 'codeIdentity', 'assignmentStatusId', 'assignmentStatusAlias', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'dateCreated', 'isActive', 'currentUserUsername','lockedByUser', 'lockedByAnother']
            df = df[[c for c in listcol if c in df.columns]]
            df['link'] = 'https://fasih-sm.bps.go.id/app/assignment/'+ df['surveyPeriodId'].astype(str) + "/" + df['id'].astype(str)

            instance.log_message(f"Done. Link data saved to '{namadf}'. Total baris: {df.shape[0]}","green_tag")

            # save as csv
            if mode=="w":
                df.to_csv(namadf, index=False, sep=sep, mode="w")
            elif mode=="a":
                df.to_csv(namadf, index=False, sep=sep, mode="a", header=False)

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
        instance.isdone = 1
        # Selalu tutup p_instance di blok 'finally' agar tidak hang
        try:
            p_instance.stop()
            instance.log_message("Koneksi Playwright di thread ditutup.")
        except NameError:
            # Terjadi jika get playwright page() gagal total di awal
            pass

# Function penunjang approv (and get data)
def run_api_request(instance, page, method, target_url, target_id, msg="", payload=None, filename="data_survey.json"):
    """
    Fungsi tunggal untuk menangani GET dan POST request ke API BPS. Method: 'GET', 'GET2' atau 'POST'. 'GET' untuk Query Parameter (?assignmentId=123), 'GET2' untuk id di dalam URL path (/api/data/123)
    """
    log_message = instance.log_message
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
        log_message(f'- Error pada {method} request: {e}')
        return None

# Function approv (and get data)
def mainfunc(instance, filename, cekapprov, mulai=0, func=None, idlog='codeIdentity', sep=','):
    '''Get data dari Fasih dengan membuka linknya dari dataframe df, kemudian export ke csv. Kemudian akan approv juga jika tercentang sekalian approv'''
    # konfig
    import sys
    instance.isdone = 0    

    try:
        p_instance, browser, page = get_playwright_page() #konek ke playwr
        # read data csv result from get list data
        try:
            df = pd.read_csv(filename, sep=sep)
            df = df.astype(str)
            if 'approved' not in df.columns:
                df['approved'] = ""
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

        # start loop per df
        if mulai <0 : i=-1
        else: i = mulai-1
        while True: 
            check_stop(instance)
            # LOOOOOOOOOP
            i += 1
            if i >= lendf:
                instance.log_message(f"# DONEEE file {filename} updated ---------------------------------")
                break
            try:
                # CEK DAH APPROVED LOM ke1 (cek dari hasil csv)------------------------------------------------------------
                # if df.loc[i, 'approved'] == True or df.loc[i, 'approved'] == "True":
                if dflist[i]['approved'] == True or dflist[i]['approved'] == "True":
                    instance.log_message(f"# {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Approv'd, skip")
                    continue

                # perlukah cek approv yg ke2? ======

                # function tambahan here
                target_id = dflist[i]['id']
                if func:
                    try:
                        # send and get response (get data detail all)
                        base_url = "https://fasih-sm.bps.go.id/app/api/assignment-general/api/assignment/get-by-assignment-id"
                        response = run_api_request(instance, page, method="get", target_url=base_url, target_id=target_id, msg=f"GetData-row-{i}")
                        if response is None:
                            raise ValueError("API tidak mengembalikan data (Response is None)")
                        if response['success'] == False or response['success'] == "false":
                            raise ValueError(response['message'])
                        
                        # ketika apireq get nya success, maka kesini, jika ga, skip. 
                        # get a dict value per row from web (init dict from func)
                        resultDict = func()

                        for key,value in resultDict.items():
                            if "err" in key.lower():
                                instance.log_message(f"Ada error dengan value: {value}")
                                raise ValueError(f"Ada error dengan value: {value}")
                            # df.at[i, key] = value
                        # update as df list 
                        dflist[i].update(resultDict)
                        dfbaru = pd.DataFrame(dflist)
                        dfbaru.to_csv(filename, index=False)

                        # kasih jeda
                        time.sleep(random.uniform(1, 2))
                        
                    except ValueError as e:
                        instance.log_message(f"# Terjadi error on GetData: ")
                        instance.log_message(str(e).split("Stacktrace:")[0], "red_tag")
                        # logging
                        dflist[i]['approved'] = str(e).split("Stacktrace:")[0]
                        # df.to_csv(filename, index=False)
                        dfbaru = pd.DataFrame(dflist)
                        dfbaru.to_csv(filename, index=False)
                        #continue
                        break
                # 

                # mulai approve jika approv 
                if cekapprov != False:
                    try:
                        # send and get response (approv)
                        if cekapprov == True:
                            payload = {
                                "assignmentId": target_id,
                                "statusApproval": 'true',
                                "comment": "\"\""
                            }
                            msg = f"Approving-row-{i}"

                        elif cekapprov == "Reject":
                            # revoke dlu if assignment udah diacc pengawas/admin
                            # cek by gettin btn approval
                            target_url = f"https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/get-button-approval?assignmentId={target_id}"
                            #instance, page, method, target_url, target_id, msg="", payload=None, filename="data_survey.json"
                            response = run_api_request(instance, page, method="post", target_url=target_url, target_id=target_id, msg=f"Cek-status-row-{i}", payload={}) 
                            time.sleep(1)
                            if response['data'] >= 2: #artinya udah approv
                                # makanya revoke
                                target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/revoke-approval" #revoke
                                response = run_api_request(instance, page, method="post", target_url=target_url, target_id=target_id, msg=f"Revoking-row-{i}") 
                                time.sleep(1)
                            elif response['data'] == 1: pass
                            else: 
                                #instance.log_message(f"{response['message']} - Error code {response['errorCode']}")
                                raise ValueError(f"{response['message']} - Error code {response['errorCode']}")

                            # baru abistu reject
                            payload = {
                                "assignmentId": target_id,
                                "statusApproval": "false",
                                "comment": "\"\""
                            }
                            msg = f"Rejecting-row-{i}"
                            #instance.log_message('cek reject target url')
                            #raise ValueError("Maaf reject blm nyoba")
                        
                        # reject or approv
                        target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/approval" 
                        response = run_api_request(instance, page, method="post", target_url=target_url, target_id=target_id, msg=msg, payload=payload) 

                        if response is None:
                            raise ValueError("API tidak mengembalikan data (Response is None)")
                        if response['success'] == False or response['success'] == "false":
                            raise ValueError(response['message'])

                        # kasih jeda
                        time.sleep(random.uniform(1, 2))

                    except Exception as e:
                        instance.log_message(f"# {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Skip gabisa approv")
                        instance.log_message(f"Error approv {e}", "red_tag")
                        # logging
                        dflist[i]['approved'] = str(e).split("Stacktrace:")[0]
                        # df.to_csv(filename, index=False)
                        dfbaru = pd.DataFrame(dflist)
                        dfbaru.to_csv(filename, index=False)
                        continue

                if not cekapprov and not func:
                    instance.log_message('NGAPAIN BRUH?', 'red_tag')
                    break

                # end result if success
                dflist[i]['approved'] = True
                # df.to_csv(filename, index=False)
                dfbaru = pd.DataFrame(dflist)
                dfbaru.to_csv(filename, index=False)
                
                # kasih jeda
                if i%10 == 0 and i!=0: time.sleep(30); instance.log_message('# Waiting...')
                if i%100 == 0 and i!=0: time.sleep(60); instance.log_message('# Waiting...')
                
            except Exception as e:
                # coba refresh n login ulang
                try:
                    if 'Server Not Found' in page.title(): 
                        instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
                        break
                    # reload
                    page.goto(dflist[i]['link'])
                    if i < -1: i=-1
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    instance.log_message(f"# Terjadi error on line: {str(exc_tb.tb_lineno)} ")
                    instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                    # try relogin sso ====== need update
                    #
                    continue

                except:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    instance.log_message(f"# Terjadi error on line: {str(exc_tb.tb_lineno)} ")
                    instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
                    continue
            
            # jika satu row dah selesai, entah error or sukses    
            instance.log_message(f"# {i}/{lendf-1} | {str(dflist[i][idlog])[:20]} | Done")
            continue


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
        instance.log_message(f"Error di thread data mainfunc: {e}", tag="red_tag")
    finally:
        # Selalu tutup p_instance di blok 'finally' agar tidak hang
        instance.isdone = 1
        try: 
            instance.log_message('Removing temporary file')
            os.remove('data_survey.json')
        except: instance.log_message("Ups, File emang gada")
        try:
            p_instance.stop()
            instance.log_message("Koneksi Playwright di thread ditutup.")
        except NameError:
            # Terjadi jika get playwright page() gagal total di awal
            pass

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

# END SECTION MAIN FUNC ###################################