# app.py, kode coba2 get response, mungkin bisa updated
# find ====== for needed update or needed parsing to main py (app_autof.py -> Auto_Fasih_SM.py // get_data.py -> willbe in dist)
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
        
        # var2 mainfunc
        # filename = 'data.csv'
        # mulai = 0
        # func = None
        # instance = None
        # cekapprov = True
        # idlog = 'Kode Identitas'
        # sep = ','
        # def check_stop(instance):
        #     print('# '+instance)
        # isdone = 0
        # import sys

        # # read data csv result from get list data
        # try:
        #     df = pd.read_csv(filename, sep=sep)
        #     if 'approved' not in df.columns:
        #         df['approved'] = ""
        # except Exception as e:
        #     log_message(f'ERROR: {e}', tag="red_tag")
        #     df = None
        #     isdone = 1
        #     return
        
        # # cek approv or not
        # msgapprov = ' and approving' if cekapprov else ''
        # log_message(f"# Loading for {len(df)-int(mulai)} data, length dataframe: {len(df)} data{msgapprov}...")

        # # start loop per df
        # if mulai <0 : i=-1
        # else: i = mulai-1
        # while True: 
        #     check_stop(instance)
        #     # LOOOOOOOOOP
        #     i += 1
        #     if i >= len(df):
        #         log_message(f"# DONEEE file {filename} updated ---------------------------------")
        #         break
        #     try:
        #         # CEK DAH APPROVED LOM ke0 (cek dari hasil csv)------------------------------------------------------------
        #         if df.loc[i, 'approved'] == True:
        #             log_message(f"# {i,str(df[idlog][i])[:20]} | Dah approved, skip")
        #             continue

        #         # goto web
        #         page.goto(df.link[i])
        #         # tapi ada error disini biasanya gamau load page, hmm. tpi klo load normal haruse pass
        #         page.wait_for_load_state("networkidle", timeout=5000) #stabil sebelum cek field
        #         page.evaluate("document.body.style.zoom='0.5'")

        #         # function tambahan here
        #         if func:
        #             try:
        #                 resultDict = func(instance)
        #                 # get a dict value per row from web (init dict from func)
        #                 for key,value in resultDict.items():
        #                     df.loc[i, key] = value
        #                 df.to_csv(filename, index=False)
                        
        #             except ValueError as e:
        #                 instance.log_message(f"# Terjadi error: ")
        #                 instance.log_message(str(e).split("Stacktrace:")[0], "red_tag")
        #                 # logging
        #                 df.loc[i, 'approved'] = str(e).split("Stacktrace:")[0]
        #                 df.to_csv(filename, index=False)
        #                 continue
        #         # 

        #         # mulai approve jika approv 
        #         # OR MUNGKIN BISA PAKE HEADER APPROV ======
        #         if cekapprov:
        #             try:
        #                 cekbtn = page.get_by_role("button", name="Open menu") 
        #                 cekbtn.first.wait_for( #cek jika visible juga
        #                     state="visible", 
        #                     timeout=10000
        #                 )
        #                 cekbtn.click() #click btuton menu
        #                 page.locator("button[class*='rounded-full'][class*='bg-success']").click() #approv
        #                 page.get_by_role("button", name="Konfirmasi").click() #konfirm modal
        #                 # wait
        #                 page.wait_for_timeout(1500)
        #                 time.sleep(2)

        #             except:
        #                 log_message(f"# {i,str(df[idlog][i])[:20]} | Not Found Approve button, skip")
        #                 # logging
        #                 df.loc[i, 'approved'] = True
        #                 df.to_csv(filename, index=False)
        #                 continue

        #         # end result if success
        #         df.loc[i, 'approved'] = True
        #         df.to_csv(filename, index=False)
                
        #     except Exception as e:
        #         # coba refresh n login ulang
        #         try:
        #             if 'Server Not Found' in page.title(): 
        #                 instance.log_message(f"# Error server not found, CEK VPN -------------------------------------------\n", "red_tag")
        #                 break
        #             # reload
        #             page.goto(df.link[i])
        #             if i < -1: i=-1
        #             instance.log_message(f"# Terjadi error: ")
        #             instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
        #             # try relogin sso ====== need update
        #             #
        #             continue

        #         except:
        #             exc_type, exc_obj, exc_tb = sys.exc_info()
        #             instance.log_message(f"# Terjadi error: {str(exc_tb.tb_lineno)} ")
        #             instance.log_message(str(e).split("Stacktrace:")[0]+"\n", "red_tag")
        #             continue
            
        #     # jika satu row dah selesai, entah error or sukses    
        #     instance.log_message(f"# {i,str(df[idlog][i])[:20]} | Done")
        #     continue

        # instance.isdone = 1


        # cek pes for dummy, LOOOOOOOOOP 1x 

        #print('5103BR1P1B51 - Raj tikha - [IN] India')
        #page.goto("https://fasih-sm.bps.go.id/app/assignment/061565d1-00f1-424a-88db-c3e06b4e5edf/c733a02a-7c82-4d21-b716-c6159ef4fee2")
        #print('5103BR1P1B51 - Rajiv - [IN] India')
        #page.goto("https://fasih-sm.bps.go.id/app/assignment/061565d1-00f1-424a-88db-c3e06b4e5edf/57697835-6725-49bf-9129-3aec4454c255")
        #page.goto("https://fasih-sm.bps.go.id/app/assignment/061565d1-00f1-424a-88db-c3e06b4e5edf/a53e128c-3640-4e8d-8f02-a1cda2a0548e")

        # --- END MAIN FUNC ---


        # ---HEADER GET LIST DATA ---
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
        # log_message('here')
        # from playwright.sync_api import expect
        # import re
        # try:
        
        #     #instance.log_message("Masuk ke fungsi get data PES")
        #     # list id blok 4
        #     ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
        #     # init a dict for data
        #     col_list = \
        #         [f"r{i}" for i in range(1,6)] + \
        #         ["r5b"] + [f"r{i}" for i in range(6,9)] + ["r9ab","r9ac"] + \
        #         [f"r9b{j}" for j in range(1,6)] + [f"r9b{j}c" for j in range(1,6)] + \
        #         [f"r10.{j}.1" for j in range(1,14)] + \
        #         [f"r10.{j}.2" for j in range(1,14)] + \
        #         [f"r11.{j}" for j in range(1,5)] + ['r12'] + ids4 + \
        #         [f"r{i}" for i in range(14,18)] + \
        #         [f"r18a_{k}" for k in ['arrival','departure']] + [f"r18b_{k}" for k in ['arrival','departure']] + [f"r18c_{k}" for k in ['arrival','departure']] + \
        #         [f"r19_{j}" for j in range(1,15)] +\
        #         [f"r{i}" for i in range(20,27)]
        #     d = dict.fromkeys(col_list, '--')
        #     #5b,9ac,9b[1,6],9b[1,6]c,10.[1,13], 11.[1,5], ids4, r18[a,b,c]_[arrival,departure], r19_[1,15], 

            
        #     def menubar(idblok):
        #         time.sleep(2)
        #         page.locator(f'xpath=//div[@id="fasih-form"]/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{idblok}]/DIV[1]').click()

            
        #     def cek_inner( location, timeout=5000):
        #         # 1. Kunci elemen tombol dropdown
        #         elem = page.locator(location)
        #         # 2. Tunggu maksimal t detik sampai teksnya BUKAN "Select an option" atau ""
        #         try:
        #             page.wait_for_function(
        #                 "el => el.innerText.strip() !== '' && el.innerText.strip() !== 'Select an option' && el.innerText.strip() !== 'Pilih salah satu'",
        #                 arg=elem.element_handle(),
        #                 timeout=timeout )
        #         except Exception:
        #             pass  # Abaikan error timeout jika memang halaman web sengaja mengosongkannya
        #         return elem.inner_text().strip()
            
        #     # BLOK1, click tab di sidebar
        #     log_message('blok1')
        #     menubar(1)

        #     d['r1'] = page.locator("//div[@id='name']//input[@type='text']").input_value()
        #     d['r2'] = page.locator("//div[@id='age']//input[@type='text']").input_value()
        #     d['r3'] = page.locator("//div[@id='sex']").locator("input[type='radio']:checked").get_attribute('value')
            
        #     d['r4'] = cek_inner( "//div[@id='nationality']//button[@aria-haspopup='dialog']",10000)
        #     d['r5'] = cek_inner("//div[@id='country_residence']//button[@aria-haspopup='dialog']",10000)
        #     d['r5b'] = cek_inner("//div[@id='city_residence']//button[@aria-haspopup='dialog']",10000)
            
        #     d['r6'] = page.locator("//div[@id='main_purpose']").locator("input[type='radio']:checked").get_attribute('value')

        #     # BLOK2
        #     menubar(2)
        #     log_message('blok2')
            
        #     d['r7'] = cek_inner( "//div[@id='port_entry']//button[@aria-haspopup='dialog']")
        #     d['r8'] = page.locator("//div[@id='length_of_stay']//input[@type='text']").input_value()
            
        #     # main dest
        #     #d['r9'] = page.locator("//div[@id='main_destination_prov']//button/div").text
        #     d['r9ab'] = cek_inner( "//div[@id='main_destination_kab']//button[@aria-haspopup='dialog']")
        #     d['r9ac'] = page.locator("//div[@id='len_stay_main_dest']//input[@type='text']").input_value()
            
        #     # other dest
        #     for i in range(1, 6):
        #         #a = page.locator(f"//div[@id='other_destination_prov_{i}']//button[@aria-haspopup='dialog']").inner_text()
        #         a = cek_inner(f"//div[@id='other_destination_prov_{i}']//button[@aria-haspopup='dialog']", 10000)
        #         if a in ["", "Select an option", "Pilih salah satu"]: continue
                
        #         d[f"r9b{i}"] = cek_inner(f"//div[@id='other_destination_kab_{i}']//button[@aria-haspopup='dialog']")
        #         d[f"r9b{i}c"] = page.locator(f"//div[@id='len_stay_other_dest_{i}']//input[@type='text']").input_value()
            
        #     # BLOK3
        #     # get radio: tourism_attraction_05
        #     menubar(3)
        #     log_message('blok3')
            
        #     for i in range(1,14):
        #         d[f"r10.{i}.1"] = page.locator(f"//div[@id='tourism_attraction_{i:02}']").locator("input[type='radio']:checked").get_attribute('value')
        #         # jika ada terpilih
        #         if d[f"r10.{i}.1"] == '1':
        #             d[f"r10.{i}.2"] = page.locator(f"//div[@id='len_stay_tourism_{i}']//input[@type='text']").input_value()
                
        #         # for switch
        #         #d[f"r10.{i}"] = page.locator(f"//div[@id='tourism_attraction_{i:02}']//input[@type='checkbox']").is_selected()

        #     #BLOK4
        #     menubar(4)
        #     log_message('blok4')
        #     # tidak semua datanya diambil sih
        #     for i in range(1,5):
        #         d[f"r11.{i}"] = page.locator(f"//div[@id='accommodation_{i:02}']").locator("input[type='radio']:checked").get_attribute('value')
        #     d[f"r12"] = page.locator(f"//div[@id='use_tour_package']").locator("input[type='radio']:checked").get_attribute('value')

        #     #BLOK5
        #     menubar(5)
        #     log_message('blok5')

        #     # wait biar isiannya muncul dulu            
        #     ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
        #     for id4 in ids4:
        #         #try:
        #         if id4 == 'currency_spending':
        #             d[id4] = cek_inner(f"//div[@id='{id4}']//button[@aria-haspopup='dialog']")
        #         else: d[id4] = page.locator(f"//div[@id='{id4}']//input[@type='text']").input_value()

        #     #BLOK6
        #     menubar(6)
        #     log_message('blok6')
            
        #     d['r14'] = page.locator(f"//div[@id='main_occupation']").locator("input[type='radio']:checked").get_attribute('value')
        #     # r15 skip 
        #     d['r16'] = page.locator("//div[@id='freq_visit']//input[@type='text']").input_value()
        #     #
        #     for i in ['arrival', 'departure']:
        #         d[f'r18a_{i}'] = cek_inner(f"//div[@id='airline_{i}']//button[@aria-haspopup='dialog']")
        #         d[f'r18b_{i}'] = cek_inner(f"//div[@id='currency_{i}']//button[@aria-haspopup='dialog']")
        #         d[f'r18c_{i}'] = page.locator(f"//div[@id='value_{i}']//input[@type='text']").input_value()

        #     #BLOK7
        #     menubar(7)
        #     log_message('blok7')
        #     #
        #     # get switch: activities_06
        #     for i in range(1,15):
        #         d[f'r19_{i}'] = page.locator(f"//div[@id='activities_{i:02}']").locator("input[type='radio']:checked").get_attribute('value')
        #         #d[f'r19_{i}'] = page.locator(f"//div[@id='activities_{i:02}']//input[@type='checkbox']").is_selected()

        #     d['r20'] = page.locator(f"//div[@id='wonderful_indonesia']").locator("input[type='radio']:checked").get_attribute('value')
        #     #
        #     d['r21'] = page.locator(f"//div[@id='ecofriendly_principle']").locator("input[type='radio']:checked").get_attribute('value')
        #     #
        #     d['r22'] = page.locator(f"//div[@id='satisfaction_lvl']").locator("input[type='radio']:checked").get_attribute('value')
        #     #
        #     d['r23'] = page.locator(f"//div[@id='intention_to_visit']").locator("input[type='radio']:checked").get_attribute('value')

        #     #BLOK8
        #     menubar(8)
        #     log_message('blok8')
        #     #
        #     d['r24'] = page.locator(f"//div[@id='note']//textarea").input_value()
        #     d['r25'] = page.locator(f"//div[@id='impression']//textarea").input_value()
        #     d['r26'] = page.locator(f"//div[@id='viplounge']").locator("input[type='radio']:checked").get_attribute('value')

        #     # return d
        #     # Write to file
        #     log_message('Exported')
        #     with open("temp.json", "w") as f:
        #         json.dump(d, f, indent=4)  # indent=4 makes it readable
                
        # except Exception as e:
        #     #instance.log_message(f'Terjadi error: {e}')
        #     import sys
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     log_message(f"Line error: {str(exc_tb.tb_lineno)} ")
        #     log_message(f'Terjadi error: {e}')
        # --- END ---

        print('Title page: ', page.title())
        
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


        # --- CHANGE THIS ---
        # emailbc()
        approv()
        # ---
        page.pause() #debugging, open recorder on playwright
        
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    run()
