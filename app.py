# app.py, kode coba2 get response, mungkin bisa updated
from playwright.sync_api import sync_playwright
import json
import time
import os
import pandas as pd

def handle_response(response, namejson='data_survey.json', target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"):
    # Filter URL spesifik yang ingin Anda ambil datanya
    
    if target_url in response.url:
        #print(f"\n[!] API Terdeteksi: {response.url}")
        #print(f"Status Code: {response.status}")
        
        try:
            # Ambil data dalam bentuk JSON
            data = response.json()
            #print("[✓] Berhasil mengambil JSON!")
            
            # Simpan data ke file lokal agar bisa Anda cek di VS Code
            with open(namejson, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[✓] Status {response.status}. Data disimpan ke '{namejson}'")
            
        except Exception as e:
            # Jika respon bukan JSON (misal HTML/Text)
            #print("Gagal convert ke JSON, mengambil teks biasa...")
            print(f'Gagal {response.text()[:500]}') # Cetak 500 karakter pertama


def mergejson(dictlist, listcol, namejson='data_survey.json'):
    '''Merge hasil response dari namejson ke dictlist existing dengan filtering listcol yang sama '''
    with open(namejson, 'r') as file:
        data = json.load(file)
    #data['searchData'][0]#.keys()
    for i in range(len(data['searchData'])):
        dictlist.append({key: data['searchData'][i][key] for key in listcol if key in data['searchData'][i]})
    return dictlist


def run():
    with sync_playwright() as p:
        # #launch from 0
        # browser = p.chromium.launch(headless=False)
        # page = browser.new_page()
        # #connect to existing: start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0] # Ini adalah tab pertama Anda

        # var
        username = 'jimmy.nickelson'
        #password = 

        # 1. Interaksi Login
        # print('# Goto web')
        # print('# Login SSO')
        # page.goto("https://fasih-sm.bps.go.id/oauth_login.html")
        # page.get_by_role("link", name="Login SSO BPS").click()
        # page.get_by_role("textbox", name="Username or email").click()
        # page.get_by_role("textbox", name="Username or email").fill(username)
        # page.get_by_role("textbox", name="Password").click()
        # page.get_by_role("textbox", name="Password").fill(password)
        # page.get_by_role("button", name="Log In").click()
        # print('# Logged in')

        # wait n getting response
        namejson = 'data_survey.json'
        target_url = "https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/datatable-all-user-survey-periode"
        page.on("response", lambda response: handle_response(response, namejson, target_url))

        # page.goto("https://fasih-sm.bps.go.id/app/surveys?page=0&perPage=10&layout=list")
        page.reload()
        page.wait_for_timeout(2000) 
        page.locator("h3").first.wait_for(
            state="visible", 
            timeout=10000
        )
        print('# Get response data on page 1')

        # read json
        ipage = 1
        dflist = []
        listcol = ['id', 'surveyPeriodId', 'codeIdentity', 'assignmentStatusId', 'assignmentStatusAlias', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'dateCreated', 'isActive', 'currentUserUsername','lockedByUser', 'lockedByAnother']
        dflist = mergejson(dflist, listcol, namejson)

        # next page        
        #page.get_by_role("button", name="Go to next page").click()
        while True:
            # 1. Ambil locator tombol next
            next_button = page.get_by_role("button", name="Go to next page")
            
            # 2. Cek apakah tombol ada, muncul, dan aktif (tidak disabled)
            if next_button.is_visible() and next_button.is_enabled():
                next_button.click()
                ipage += 1
                page.wait_for_timeout(2000) # Jeda 1 detik nunggu halaman muat
                print(f'# Get response data from page {ipage}')
                dflist = mergejson(dflist, listcol, namejson)
            else:
                print('# Selesai')
                os.remove(namejson)
                break # Berhenti loop jika tidak bisa diklik

        time.sleep(2)
        df = pd.DataFrame(dflist)
        df.to_csv('data.csv')
        print('# Export to data.csv')
        #page.pause() #debugging, open recorder on playwright
        
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    run()
