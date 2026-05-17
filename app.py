# app.py, kode coba2 get response, mungkin bisa updated
import subprocess

from playwright.sync_api import sync_playwright
import json
import time
import os
import pandas as pd

def handle_response(response, namejson='data_survey.json', target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"):    
    if target_url in response.url:
        try:
            data = response.json()
            with open(namejson, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[✓] Status {response.status}. Data disimpan ke '{namejson}'")
            
        except Exception as e:
            print(f'Gagal {response.text()[:500]}') # Cetak 500 karakter pertama


def mergejson(dictlist, listcol, namejson='data_survey.json'):
    '''Merge hasil response dari namejson ke dictlist existing dengan filtering listcol yang sama '''
    with open(namejson, 'r') as file:
        data = json.load(file)
    #data['searchData'][0]#.keys()
    for i in range(len(data['searchData'])):
        dictlist.append({key: data['searchData'][i][key] for key in listcol if key in data['searchData'][i]})
    return dictlist

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
        try:
            # 1. Coba hubungkan ke browser yang sudah ada
            print("Mengecek browser yang terbuka...")
            browser = playwright_instance.chromium.connect_over_cdp("http://localhost:9222")                    
            page = browser.contexts[0].pages[0]
            print("Berhasil terhubung ke browser yang sudah ada!")
            
        except Exception:
            print("Browser tidak ditemukan. Membuka browser baru...")
            subprocess.Popen(r'start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"', shell=True)
            time.sleep(2)
            try:
                browser = playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
                page = browser.contexts[0].pages[0]
            except Exception:
                print("Gagal terhubung ke Chrome. Pastikan port 9222 tidak diblokir.")

        # var
        usersso, passso, approv, msgsso = load_credentials()  

        # 1. Interaksi Login #UPDATED LOGINNNNNN
        print('# Goto web')
        print('# Login SSO')
        page.goto("https://fasih-sm.bps.go.id/oauth_login.html")
        page.get_by_role("link", name="Login SSO BPS").click()
        page.wait_for_load_state("networkidle", timeout=5000)
        username_field = page.get_by_role("textbox", name="Username or email")
        if username_field.count() > 0:
            username_field.click()
            username_field.fill(usersso)
            password_field = page.get_by_role("textbox", name="Password")
            if password_field.count() > 0:
                password_field.click()
                password_field.fill(passso)
            page.get_by_role("button", name="Log In").click()
        print('# Logged in')

        # --- MAIN FUNC ---
        # cek pes
        print('5103BR1P1B51 - Raj tikha - [IN] India')
        page.goto("https://fasih-sm.bps.go.id/app/assignment/061565d1-00f1-424a-88db-c3e06b4e5edf/c733a02a-7c82-4d21-b716-c6159ef4fee2")
        # tapi ada error disini biasanya gamau load page, hmm. tpi klo load normal haruse pass
        page.wait_for_load_state("networkidle", timeout=5000) #stabil sebelum cek field
        cekbtn = page.get_by_role("button", name="Open menu") 
        cekbtn.first.wait_for( #cek jika visible juga
            state="visible", 
            timeout=10000
        )
        cekbtn.click() #click btuton menu
        page.locator("button[class*='rounded-full'][class*='bg-success']").click() #approv
        page.get_by_role("button", name="Konfirmasi").click() #konfirm modal
        # wait
        page.wait_for_timeout(1500)
        time.sleep(2)

        # next loop
        print('5103BR1P1B51 - Rajiv - [IN] India')
        page.goto("https://fasih-sm.bps.go.id/app/assignment/061565d1-00f1-424a-88db-c3e06b4e5edf/57697835-6725-49bf-9129-3aec4454c255")

        # --- END MAIN FUNC ---


        # --- GET LIST DATA ---
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


        page.pause() #debugging, open recorder on playwright
        
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    run()
