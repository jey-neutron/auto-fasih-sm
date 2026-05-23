# app.py, kode coba2 get response, mungkin bisa updated
# find ====== for needed update or needed parsing to main py (app_autof.py -> Auto_Fasih_SM.py // get_data.py -> willbe in dist)
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


        # --- HEADER MAIN FUNC --- 
        # main func pindah ke bawah pake api. ====== kata kunci:
        # if func : get api detail data, then per survei aja dibuat parse ke csv
        # if cekapprov : get api approv
        # --- END MAIN FUNC ---


        # ---HEADER GET LIST DATA ---

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

        # wait n getting response 
        # namejson = 'data_survey.json'
        # target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        # page.on("response", lambda response: handle_response(response, namejson, target_url))

        # # page.goto("https://fasih-sm.bps.go.id/app/surveys?page=0&perPage=10&layout=list")
        # page.reload()
        # page.wait_for_timeout(2000) 
        # page.locator("h3").first.wait_for(
        #     state="visible", 
        #     timeout=10000
        # )
        # print('# Get response data on page 1')

        # # read json
        # ipage = 1
        # dflist = []
        # listcol = ['id', 'surveyPeriodId', 'codeIdentity', 'assignmentStatusId', 'assignmentStatusAlias', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'dateCreated', 'isActive', 'currentUserUsername','lockedByUser', 'lockedByAnother']
        # dflist = mergejson(dflist, listcol, namejson)

        # # next page        
        # #page.get_by_role("button", name="Go to next page").click()
        # while True:
        #     # 1. Ambil locator tombol next
        #     next_button = page.get_by_role("button", name="Go to next page")
            
        #     # 2. Cek apakah tombol ada, muncul, dan aktif (tidak disabled)
        #     if next_button.is_visible() and next_button.is_enabled():
        #         next_button.click()
        #         ipage += 1
        #         page.wait_for_timeout(2000) # Jeda 1 detik nunggu halaman muat
        #         print(f'# Get response data from page {ipage}')
        #         dflist = mergejson(dflist, listcol, namejson)
        #     else:
        #         print('# Selesai')
        #         os.remove(namejson)
        #         break # Berhenti loop jika tidak bisa diklik

        # time.sleep(2)
        # df = pd.DataFrame(dflist)
        # df.to_csv('data.csv')
        # print('# Export to data.csv')
        # --- END GET LIST DATA ---


        # --- HEADER GET PES ---
        # ====== pake di google colab, parse dari response api json ke csv
        # --- END ---

        
        # --- HEADER EMAIL FASIH BC---
        def emailbc():
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

        # --- HEADER APPROV ---
        def approv():
            try:
                from urllib.parse import unquote
                namejson = 'data_survey.json'
                id = "6a4f9604-dba9-4ef3-a284-7b1c56f127fa"

                # try aja
                h3 = page.locator("h1").first.wait_for(state="visible", timeout=10000)
                log_message(f'Judul: {h3}')

                #target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/revoke-approval"
                target_url = "https://fasih-sm.bps.go.id/app/api/assignment-approval/api/v2/approval"
                # blm nyoba reject by api ======

                # 1. AMBIL COOKIE CSRF DARI BROWSER CONTEXT
                cookies = page.context.cookies()
                csrf_token = ""
                for cookie in cookies:
                    # Biasanya nama cookienya 'XSRF-TOKEN' atau 'csrf_token'
                    if cookie['name'] == 'XSRF-TOKEN': 
                        csrf_token = unquote(cookie['value']) # Decode jika token mengandung %3D atau karakter khusus
                        break
                
                a = 'revoking' if 'revoke' in target_url else 'approving'
                status_approv = 'false' if 'revoke' in target_url else 'true'
                log_message(f'TRY "{a}" with api instead of button pushing')

                # 1. Siapkan data body/payload JSON yang diminta oleh API BPS
                headers = {
                    "Content-Type": "application/json",
                    "X-XSRF-TOKEN": csrf_token, # Ini kunci utamanya!
                    "Referer": "https://bps.go.id"
                }
                payload_data = {
                    "assignmentId": id,
                    "statusApproval": status_approv,
                    "comment": "\"\""
                }

                # 2. Eksekusi POST request memanfaatkan session browser
                log_message(f"Mengirim POST request ke {target_url}...")
                response = page.request.post(
                    target_url,
                    headers=headers,
                    data=payload_data # Playwright otomatis mengubah dict ini menjadi JSON string
                )

                # 3. Handle respon dari server
                if response.ok:
                    response_json = response.json()
                    log_message(f"POST Berhasil! Status: {response.status}")
                    
                    # Simpan hasil respon ke file data_survey.json
                    #with open(namejson, 'w', encoding='utf-8') as f:
                    #    json.dump(response_json, f, indent=4)
                    #log_message(f'# written to {namejson}')

                    # 4. Refresh halaman untuk melihat perubahan di UI
                    page.reload()
                    page.locator("h1").first.wait_for(state="visible", timeout=10000)

                else:
                    log_message(f"POST Gagal! Status: {response.status} - {response.text()}")

            except Exception as e :
                log_message(f'Error: {e}')

            # --- END APPROv ---

        # --- HEADER GABUNGIN 2 FUNC --- ====== perlu cek n update, then apus function atas n bawah
        import json
        from urllib.parse import unquote

        def execute_api_request(page, method, url, target_id, payload=None, filename="data_survey.json"):
            """
            Fungsi tunggal untuk menangani GET dan POST request ke API BPS.
            method: 'GET' atau 'POST'
            """
            try:
                method = method.upper()
                
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

                log_message(f"Mengirim {method} request ke {url}...")

                # 3. EKSEKUSI REQUEST (GET vs POST)
                if method == "POST":
                    # Jika payload tidak diisi manual, buat payload default approval
                    if not payload:
                        status_approv = 'false' if 'revoke' in url else 'true'
                        payload = {
                            "assignmentId": target_id,
                            "statusApproval": status_approv,
                            "comment": "\"\""
                        }
                    response = page.request.post(url, headers=headers, data=payload)
                    
                elif method == "GET":
                    response = page.request.get(url, headers=headers, params={"assignmentId": target_id})
                
                else:
                    log_message(f"Method {method} tidak didukung.")
                    return None

                # 4. HANDLE RESPONSE (Dipakai bersama)
                if response.ok:
                    response_json = response.json()
                    log_message(f"{method} Berhasil! Status: {response.status}")
                    
                    # Jika GET, simpan ke file JSON
                    if method == "GET":
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(response_json, f, indent=4, ensure_ascii=False)
                        log_message(f"[✓] Data disimpan ke '{filename}'")
                    
                    # Jika POST, lakukan UI refresh halaman
                    elif method == "POST":
                        page.reload()
                        page.locator("h1").first.wait_for(state="visible", timeout=10000)
                        
                    return response_json
                else:
                    log_message(f"{method} Gagal! Status: {response.status} - {response.text()}")
                    return None

            except Exception as e:
                log_message(f'Error pada {method} request: {e}')
                return None

            # --- END 2 FUNC ---

        # --- HEADER GET DETAIL DATA ---
        def get_data_by_id(page, base_url, target_id, namejson='data_survey.json'):
            from urllib.parse import unquote
            try:
                # 1. AMBIL COOKIE CSRF DARI BROWSER CONTEXT (Sama seperti POST)
                cookies = page.context.cookies()
                csrf_token = ""
                for cookie in cookies:
                    if cookie['name'] == 'XSRF-TOKEN': 
                        csrf_token = unquote(cookie['value'])
                        break
                
                log_message(f'Mencoba GET data dengan ID: {target_id}')

                # 2. Siapkan headers (Biasanya GET tidak butuh Content-Type, tapi butuh CSRF & Referer)
                headers = {
                    "X-XSRF-TOKEN": csrf_token,
                    "Referer": "https://bps.go.id"
                }

                # 3. Eksekusi GET request memanfaatkan session browser
                # OPSI A: Jika ID dimasukkan sebagai Query Parameter (?id=123 atau ?assignmentId=123)
                response = page.request.get(
                    base_url,
                    headers=headers,
                    params={"assignmentId": target_id} # Playwright otomatis mengubah ini jadi: base_url?assignmentId=target_id
                )

                # OPSI B: Jika ID dimasukkan langsung di dalam URL path (misal: /api/data/123)
                # url_with_id = f"{base_url}/{target_id}"
                # response = page.request.get(url_with_id, headers=headers)

                # 4. Handle respon dari server
                if response.ok:
                    response_json = response.json()
                    log_message(f"GET Berhasil! Status: {response.status}")
                    
                    # Kembalikan atau proses data JSON yang didapat
                    # return response_json
                    with open(namejson, "w", encoding="utf-8") as f:
                        json.dump(response_json, f, indent=4, ensure_ascii=False)
                    print(f"[✓] Status {response.status}. Data disimpan ke '{namejson}'")
                    return True
                else:
                    log_message(f"GET Gagal! Status: {response.status} - {response.text()}")
                    return None

            except Exception as e:
                log_message(f'Error saat GET data: {e}')
                return None

            # --- END GET DETAIL DATA ---


        # --- CHANGE THIS ---
        page.reload()
        print('Title page: ', page.title())
        # emailbc()
        # approv()
        # 
        base_url = "https://fasih-sm.bps.go.id/app/api/assignment-general/api/assignment/get-by-assignment-id"
        target_id = "5451c1cc-5cb3-444e-9696-72b457aa00e8"
        get_data_by_id(page, base_url, target_id)
        # ---
        page.pause() #debugging, open recorder on playwright
        
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    run()
