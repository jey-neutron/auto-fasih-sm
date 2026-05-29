APP_VERSION = 'v2.1.2' # ada perubahan sih di main app dikit terkait username validation, tpi blm diexport n push
# konfig
from datetime import datetime
import pandas as pd
import time
import random
import os
import json
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from urllib.parse import unquote
    
def ver(instance, var=''): 
    '''Get a version app'''
    if var==1:
        instance.isdone = 0
        instance.log_message(f"Application version: {APP_VERSION}")
        instance.isdone = 1
    return APP_VERSION

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

# def inputwebdash(instance, var)
# def assignselect(instance, var)
# def mailbc(instance, var) # mybe, buat ngibar paling, ref from app.py ======
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

def addpenawaran(instance, var):
    log_message = instance.log_message
    p_instance, browser, page = get_playwright_page() #konek ke playwr
    
    namafile = instance.filename_entry.get()
    df = pd.read_csv(namafile)

    log_message('csv read')
    gagal = 0
    j = 0
    
    for i in range(len(df)):
        check_stop(instance)
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
    instance.isdone = 1


def render(instance,var):
    """Memanggil index.html dengan pilihan variable terlampir"""
    p_instance, browser, page = get_playwright_page() #konek ke playwr
    instance.log_message(f'Rendering HTML. Var="done", "running", "ready". Chosen: {var} ')
    page.goto(instance.getassets('index.html'))
    if var != 1:
        page.evaluate(f"document.body.setAttribute('data-status', '{var}')")
    instance.log_message('Selesai')
    #instance.isdone=1
    
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
            nama not in ["mainfunc", "get_list_data", "update_temp_value", "datetime", "sync_playwright","check_stop", "handle_response", 'mergejson','run_api_request','get_playwright_page','expect','unquote'] ):
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


# Function penunjang assignselect
def update_temp_value(gagal=False):
    '''Function untuk membuat var temp di temp.txt'''
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

def getdataAll(namafile = 'data_survey.json'):
    '''FUNCTION FOR GETTING DATA GENERAL SURVEY (mybe ada kendala, tpi sementara ini deh)'''
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

# Function penunjang to get list data
def handle_response(instance, response, target_url, namejson='data_survey.json'):
    '''Get response terutama buat pas load page di awal biar dapet response dalam json'''
    # Filter URL spesifik yang ingin Anda ambil datanya
    
    if target_url in response.url:
        try:
            data = response.json()
            with open(namejson, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            #instance.log_message(f"[✓] (Status {response.status}). Data disimpan ke '{namejson}'")
            stat = 'OK' if response.status == 200 else 'ERR'
            instance.log_message(f"# Status {stat}")
            
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
    '''Get dataframe dari prelist link fasih untuk dijadikan bahan, kemudian export ke csv juga. '''
    instance.isdone = 0
    try:
        p_instance, browser, page = get_playwright_page() #konek ke playwr
        
        # wait n getting response
        namejson = 'data_survey.json'
        target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        page.on("response", lambda response: handle_response(instance, response, target_url, namejson))

        # page.goto("https://fasih-sm.bps.go.id/app/surveys?page=0&perPage=10&layout=list")
        page.reload()
        time.sleep(2)
        page.wait_for_timeout(2000) 
        #page.evaluate("document.body.style.zoom='0.5'")
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
                page.wait_for_timeout(2000) # Jeda detik nunggu halaman muat
                instance.log_message(f'# Jml data: {len(dflist)}. Getting response data page {ipage}')
                dflist = mergejson(dflist, listcol, namejson)
                time.sleep(1)
            else:
                instance.log_message('# Selesai')
                try: os.remove(namejson)
                except: instance.log_message("File not created", tag='red_tag')
                break # Berhenti loop jika tidak bisa diklik

        time.sleep(2)
        # ngerapiin
        df = pd.DataFrame(dflist)
        lendf = len(df)
        instance.log_message(f"# Get {lendf} rows of data")
        df['link'] = 'https://fasih-sm.bps.go.id/app/assignment/'+ df['surveyPeriodId'].astype(str) + "/" + df['id'].astype(str)
        # page.pause() #debugging, open recorder on playwright
                
        # save as csv
        if mode=="w":
            df.to_csv(namadf, index=False, sep=sep, mode="w")
        elif mode=="a":
            df.to_csv(namadf, index=False, sep=sep, mode="a", header=False)

        #print(f"# Link data saved to {namadf}")
        instance.log_message(f"# Done. Link data saved to {namadf}")
        with open(namadf, 'r', encoding='utf-8') as f: #ngitung jml row only
            next(f)
            totrow = sum(1 for line in f)
        instance.log_message(f"# Total rows now: {totrow}")
    
    except Exception as e:
        instance.log_message(f"Error di thread data getlistdata: {e}", tag="red_tag")
    finally:
        instance.isdone = 1
        instance.log_message("Browser bisa di-previous-page/back jika mau digunakan kembali")
        page.goto(instance.getassets('index.html'))
        page.evaluate("document.body.setAttribute('data-status', 'done')")
        return (df)
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
