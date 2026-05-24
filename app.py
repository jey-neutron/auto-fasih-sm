# app.py, kode coba2 get response, mungkin bisa updated
# find komen ====== for needed update or needed parsing to main py (app_autof.py -> Auto_Fasih_SM.py // get_data.py -> willbe in dist)
# find komen BAB untuk setiap func, yg harusnya diiringi run_*()
# 
import subprocess

from playwright.sync_api import sync_playwright
import json
import time
import os
import pandas as pd


def load_credentials():
        try:
            path = os.path.join(os.getcwd(), 'tempuser.txt')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    lines = f.read().splitlines()
                    return lines[0], lines[1], lines[2], "Loaded"
        except: pass
        return "jey.neutron", "password", "approv1", "Default"

def run():
    with sync_playwright() as playwright_instance:
        # Coba hubungkan ke browser yang sudah ada
        try:
            print("Mengecek browser yang terbuka...")
            browser = playwright_instance.chromium.connect_over_cdp("http://localhost:9222")                    
            page = browser.contexts[0].pages[0]
            print("Berhasil terhubung ke browser yang sudah ada!")
            
        except Exception:
            print("Browser tidak ditemukan. Membuka browser baru...")
            subprocess.Popen(r'start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"', shell=True)
            time.sleep(5)
            try:
                browser = playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
                print("Berhasil terhubung ke browser baru!")
            except Exception:
                print("Gagal terhubung ke Chrome. Pastikan port 9222 tidak diblokir.")

        # var
        # usersso, passso, approv, msgsso = load_credentials()  
  
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

        def log_message(txt, tag=''): #fungsi biar jalan aja dulu
            print('# '+ str(txt))


        # ---BAB GET LIST DATA ---

        # def handle_response(response, namejson='data_survey.json', target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"):    
        #     if target_url in response.url:
        #         try:
        #             data = response.json()
        #             with open(namejson, "w", encoding="utf-8") as f:
        #                 json.dump(data, f, indent=4, ensure_ascii=False)
        #             print(f"[✓] Status {response.status}. Data disimpan ke '{namejson}'")
                    
        #         except Exception as e:
        #             print(f'Gagal {response.text()[:500]}') # Cetak 500 karakter pertama


        # def mergejson(dictlist, listcol, namejson='data_survey.json'):
        #     '''Merge hasil response dari namejson ke dictlist existing dengan filtering listcol yang sama '''
        #     with open(namejson, 'r') as file:
        #         data = json.load(file)
        #     #data['searchData'][0]#.keys()
        #     for i in range(len(data['searchData'])):
        #         dictlist.append({key: data['searchData'][i][key] for key in listcol if key in data['searchData'][i]})
        #     return dictlist

        # def run_getlistdata():
        #     wait n getting response 
        #     namejson = 'data_survey.json'
        #     target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        #     page.on("response", lambda response: handle_response(response, namejson, target_url))

        #     # page.goto("https://fasih-sm.bps.go.id/app/surveys?page=0&perPage=10&layout=list")
        #     page.reload()
        #     page.wait_for_timeout(2000) 
        #     page.locator("h3").first.wait_for(
        #         state="visible", 
        #         timeout=10000
        #     )
        #     print('# Get response data on page 1')

        #     # read json
        #     ipage = 1
        #     dflist = []
        #     listcol = ['id', 'surveyPeriodId', 'codeIdentity', 'assignmentStatusId', 'assignmentStatusAlias', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'dateCreated', 'isActive', 'currentUserUsername','lockedByUser', 'lockedByAnother']
        #     dflist = mergejson(dflist, listcol, namejson)

        #     # next page        
        #     #page.get_by_role("button", name="Go to next page").click()
        #     while True:
        #         # 1. Ambil locator tombol next
        #         next_button = page.get_by_role("button", name="Go to next page")
                
        #         # 2. Cek apakah tombol ada, muncul, dan aktif (tidak disabled)
        #         if next_button.is_visible() and next_button.is_enabled():
        #             next_button.click()
        #             ipage += 1
        #             page.wait_for_timeout(2000) # Jeda 1 detik nunggu halaman muat
        #             print(f'# Get response data from page {ipage}')
        #             dflist = mergejson(dflist, listcol, namejson)
        #         else:
        #             print('# Selesai')
        #             os.remove(namejson)
        #             break # Berhenti loop jika tidak bisa diklik

        #     time.sleep(2)
        #     df = pd.DataFrame(dflist)
        #     df.to_csv('data.csv')
        #     print('# Export to data.csv')

        # --- END GET LIST DATA ---


        # --- BAB GET PES ---
        # parse dari response api json ke csv, khusus untuk PES

        def run_getdataPES(namafile='data_survey.json'):
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

            return d

        # --- END ---

        
        # --- BAB EMAIL FASIH BC---
        def run_emailbc():
            #id = "5103020002000305 - UMK - 26"
            #id = "5103010006001218 - UMK - 10"
            #email="niluhsekarastuti96@gmail.com"

            ggl = 1
            df = pd.read_csv('tempdatasmp.csv')
            
            if 'approved' not in df.columns:
                df['approved'] = ""
            # print(df.head(5))

            for i in range(len(df)):
                # cek done yet
                if df.loc[i, 'approved'] == 'done':
                    log_message(f"# {i,str(df['nama'][i])[:20]} | Dah dieksekusi, skip")
                    continue
                if df.loc[i, 'idsbr'] == '' or pd.isna(df.loc[i, 'idsbr']):
                    log_message(f"# {i,str(df['nama'][i])[:20]} | Not found idsbr")
                    continue
                
                log_message(f"# {i,str(df['nama'][i])[:20]} | {df['idsbr'][i]} {df['email'][i]}")

                id = df['idsbr'][i]
                email = df['email'][i]

                try:
                    page.get_by_role("textbox", name="Cari...").click()
                    page.get_by_role("textbox", name="Cari...").fill(id)
                    time.sleep(2)
                    #page.get_by_role("button", name=id).click()
                    page.get_by_role("cell", name=id).click(button="right")
                    page.get_by_role("menuitem", name="Pengaturan Email").click()
                    page.get_by_role("button", name="Ganti Email").click()
                    page.get_by_role("textbox", name="Ganti Email").click()
                    page.get_by_role("textbox", name="Ganti Email").fill(email)
                    time.sleep(1)
                    page.get_by_role("button", name="Ganti Email").click()
                    page.get_by_role("button", name="Broadcast Email").click()
                    page.get_by_role("button", name="Broadcast Email").click()
                    # ESCCCCC gbasi
                    #page.get_by_role("button", name="Close").click()
                    page.keyboard.press("Escape")
                    time.sleep(2)
                    df.loc[i, 'approved'] = 'done'

                except Exception as e:
                    ggl += 1
                    if ggl%5 == 0:
                        break

                    log_message(f"# {i,str(df['nama'][i])[:20]} | ERRR")
                    log_message(f"Error: {e}")
                    df.loc[i, 'approved'] = 'error'
                    time.sleep(2)
                    continue

                finally:
                    df.to_csv('tempdatasmp.csv', index=False)

            # --- ENDEMAIL FASIH BC ---


        # --- BAB MAIN FUNC --- 
        # main func pindah ke bawah pake api. ====== kata kunci:
        # if func : get api detail data, run_api_request(method=get), then per survei aja dibuat parse ke csv
        # if cekapprov : get api approv, run_api_request(method=post)
        # --- END MAIN FUNC ---

        # --- BAB GABUNGIN 2 FUNC APPROV N GETDATA ALL---
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

                log_message(f"Mencoba {msg} request...")

                # 3. EKSEKUSI REQUEST (GET vs POST)
                if method == "POST":
                    # Jika payload tidak diisi manual, buat payload default approval
                    if not payload:
                        status_approv = 'false' if 'revoke' in target_url else 'true' # ====== buat juga misal ada reject
                        payload = {
                            "assignmentId": target_id,
                            "statusApproval": status_approv,
                            "comment": "\"\""
                        }
                    response = page.request.post(target_url, headers=headers, data=payload)
                    
                elif method == "GET":
                    # Jika target_id dimasukkan sebagai Query Parameter (?assignmentId=123)
                    response = page.request.get(target_url, headers=headers, params={"assignmentId": target_id}) # ====== gaperlukah payload di GET? next
                    # Jika ID dimasukkan langsung di dalam URL path (misal: /api/data/123)
                    # url_with_id = f"{target_url}/{target_id}"
                    # response = page.request.get(url_with_id, headers=headers)
                
                else:
                    log_message(f"Method {method} tidak didukung.")
                    return None

                # 4. HANDLE RESPONSE (Dipakai bersama)
                if response.ok:
                    response_json = response.json()
                    log_message(f"{msg} Berhasil! Status: {response.status}")
                    
                    # Jika GET, simpan ke file JSON
                    if method == "GET":
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(response_json, f, indent=4, ensure_ascii=False)
                        #log_message(f"Data disimpan ke '{filename}'")
                    
                    # Jika POST, lakukan UI refresh halaman
                    # elif method == "POST":
                    #     page.reload()
                    #     page.locator("h1").first.wait_for(state="visible", timeout=10000)
                        
                    return response_json
                else:
                    log_message(f"{method} Gagal! Status: {response.status} - {response.text()}")
                    return None

            except Exception as e:
                log_message(f'Error pada {method} request: {e}')
                return None

            # --- END 2 FUNC ---


        # --- MAIN RUN, CHANGE THIS ---
        page.reload()
        print('Title page: ', page.title())
        # RUN Email broadcast fasih
        # run_emailbc()
        #
        # RUN Approval, revoke, reject fasih by id
        # target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/approval" #approv
        # target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/revoke-approval" #revoke
        # target_url = blm nyoba reject by api ======
        # target_id = "6a4f9604-dba9-4ef3-a284-7b1c56f127fa"
        # ====== if get statusnya udah approv, skip cekapprov
        # run_api_request(page, method="post", target_url=target_url, target_id=target_id, msg="Approving")
        # 
        # RUN Get detail data
        base_url = "https://fasih-sm.bps.go.id/app/api/assignment-general/api/assignment/get-by-assignment-id"
        target_id = "f2ad1748-8b8b-4af4-a1a0-c3af0ed0bdd9"
        response = run_api_request(page, method="get", target_url=base_url, target_id=target_id, msg="GetData")
        print(response)
        if response['success'] == False or response['success'] == "False":
            print(response['message'])
        # 
        # Udah get detail data kan, abistu convert per data survei yg sesuai
        # RUN Get PES
        # ====== ketika apireq get nya success, maka kesini, jika ga, skip. ketika dah selese loop, delete data_survey.json
        resultDict = run_getdataPES()    
        print(resultDict)
        # plan A
        # for key,value in resultDict.items():
        #     df.loc[i, key] = value
        # df.to_csv(filename, index=False)
        # plan B
        df = pd.DataFrame(resultDict, index=[0])
        df.to_csv('tempdata.csv', index=False)
        #
        # ---
        page.pause() #debugging, open recorder on playwright
        
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    run()
