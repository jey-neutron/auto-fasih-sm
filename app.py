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
        # Coba hubungkan ke browser yang sudah ada
        try:
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

        # --- MAIN FUNC ---
        
        # var2 mainfunc
        # filename = 'data.csv'
        # mulai = 0
        # func = None
        # instance = None
        # cekapprov = True
        # idlog = 'Kode Identitas'
        # sep = ','
        def log_message(txt, tag=''): #fungsi biar jalan aja dulu
            print('# '+ str(txt))
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
        #             if 'Server Not Found' in page.title: 
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


        # --- GET PES ---
        log_message('here')
        from playwright.sync_api import expect
        import re
        try:
        
            #instance.log_message("Masuk ke fungsi get data PES")
            # list id blok 4
            ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
            # init a dict for data
            col_list = \
                [f"r{i}" for i in range(1,6)] + \
                ["r5b"] + [f"r{i}" for i in range(6,9)] + ["r9aa","r9ac"] + \
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

            # BLOK1, click tab di sidebar
            blok = 1
            log_message('blok1')
            page.locator(f'xpath=//div[@id="fasih-form"]/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # wait biar isiannya muncul dulu
            # expect(page.locator("//div[@id='nationality']//button/div")).not_to_be_empty()
            # expect(page.locator("//div[@id='city_residence']//button/div")).not_to_be_empty()
            
            # Daftar ID dropdown yang wajib dicek kontennnya
            # dropdown_ids = ['nationality', 'city_residence']
            # time.sleep(2)
            # for id_name in dropdown_ids:
            #     tombol = page.locator(f"//div[@id='{id_name}']//button[@type='button']")
            #     # Tunggu sampai teks terisi (bukan kosong atau teks default)
            #     expect(tombol).not_to_have_text("", timeout=20000)
            #     expect(tombol).not_to_have_text("Select an option")
            #

            # d['r2'] = page.locator("//div[@id='age']//input[@type='text']").get_attribute('value')
            # radios3 = page.find_elements(By.XPATH, f"//div[@id='sex']//input[@type='radio']")
            # for r in radios3:
            #     if r.is_selected(): break
            # d['r3'] = r.get_attribute('value')
            # d['r4'] = page.locator("//div[@id='nationality']//button/div").text #for input dropdown
            #
            # d['r2'] = page.locator("//div[@id='age']//input[@type='text']").input_value()
            # d['r3'] = page.locator("//div[@id='sex']").locator("input[type='radio']:checked").get_attribute('value')
            # d['r4'] = page.locator("//div[@id='nationality']//button[@aria-haspopup='dialog']").inner_text()
            #
            d['r1'] = page.locator("//div[@id='name']//input[@type='text']").input_value()
            d['r2'] = page.locator("//div[@id='age']//input[@type='text']").input_value()
            d['r3'] = page.locator("//div[@id='sex']").locator("input[type='radio']:checked").get_attribute('value')
            d['r4'] = page.locator("//div[@id='nationality']//button[@aria-haspopup='dialog']").inner_text()
            d['r5'] = page.locator("//div[@id='country_residence']//button[@aria-haspopup='dialog']").inner_text()
            d['r5b'] = page.locator("//div[@id='city_residence']//button[@aria-haspopup='dialog']").inner_text()
            d['r6'] = page.locator("//div[@id='main_purpose']").locator("input[type='radio']:checked").get_attribute('value')

            # BLOK2
            blok = 2
            log_message('blok2')
            page.locator(f'xpath=//div[@id="fasih-form"]/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # # wait biar isiannya muncul dulu
            # expect(page.locator("//div[@id='port_entry']//button/div")).not_to_be_empty()
            # expect(page.locator("//div[@id='main_destination_kab']//button/div")).not_to_be_empty()
            # for i in range(1, 5):
            #     expect(page.locator(f"//div[@id='other_destination_prov_{i}']//button/div")).not_to_be_empty()
            # #
            d['r7'] = page.locator("//div[@id='port_entry']//button[@aria-haspopup='dialog']").inner_text()
            d['r8'] = page.locator("//div[@id='length_of_stay']//input[@type='text']").input_value()
            # main dest
            #d['r9'] = page.locator("//div[@id='main_destination_prov']//button/div").text
            d['r9aa'] = page.locator("//div[@id='main_destination_kab']//button[@aria-haspopup='dialog']").inner_text()
            d['r9ac'] = page.locator("//div[@id='len_stay_main_dest']//input[@type='text']").input_value()
            # other dest
            for i in range(1, 6):
                a = page.locator(f"//div[@id='other_destination_prov_{i}']//button[@aria-haspopup='dialog']").inner_text()
                if a in ["", "Select an option", "Pilih salah satu"]: continue
                
                # ERRRRRR
                d[f"r9b{i}"] = page.locator(f"//div[@id='other_destination_kab_{i}']//button[@aria-haspopup='dialog']").inner_text()
                d[f"r9b{i}c"] = page.locator(f"//div[@id='len_stay_other_dest_{i}']//input[@type='text']").input_value()
            
            # # BLOK3
            # # get radio: tourism_attraction_05
            # blok = 3
            # page.locator(f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            
            # for i in range(1,14):
            #     # get radio value
            #     radios10 = page.find_elements(By.XPATH, f"//div[@id='tourism_attraction_{i:02}']//input[@type='radio']")
            #     for r in radios10:
            #         if r.is_selected(): break
            #     # jika ada terpilih
            #     if r.get_attribute('value') == '1':
            #         d[f"r10.{i}.2"] = page.locator(f"//div[@id='len_stay_tourism_{i}']//input[@type='text']").get_attribute('value')
            #     d[f"r10.{i}.1"] = r.get_attribute('value')
                
            #     # for switch
            #     #d[f"r10.{i}"] = page.locator(f"//div[@id='tourism_attraction_{i:02}']//input[@type='checkbox']").is_selected()

            # #BLOK4
            # blok = 4
            # page.locator(f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # # tidak semua datanya diambil sih
            # for i in range(1,5):
            #     radios12 = page.find_elements(By.XPATH, f"//div[@id='accommodation_{i:02}']//input[@type='radio']")
            #     for r in radios12:
            #         if r.is_selected(): break
            #     d[f"r11.{i}"] = r.get_attribute('value')
            #     #d[f"r11.{i}"] = page.locator(f"//div[@id='accommodation_{i:02}']//input[@type='checkbox']").is_selected()
            # radios12 = page.find_elements(By.XPATH, f"//div[@id='use_tour_package']//input[@type='radio']")
            # for r in radios12:
            #     if r.is_selected(): break
            # d[f"r12"] = r.get_attribute('value')

            # #BLOK5
            # blok = 5
            # page.locator(f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # # wait biar isiannya muncul dulu
            # WebpageWait(page, 10).until(
            #     lambda d: d.locator("//div[@id='currency_spending']//button/div").text.strip() != ""
            # )
            # #
            # ids4 = ['number_group_member', 'currency_spending', 'details_spending', 'var_spending', 'local_package_tour_spending', 'accommodation_spending', 'food_spending', 'domestic_flight_spending', 'local_transport_bus', 'local_transport_train', 'local_transport_water_transport', 'other_local_transportation_spending', 'vehicle_rent_spending', 'shopping_spending', 'entertainment_spending', 'health_spending', 'training_spending', 'charity_spending', 'others_spending', ]
            # for id4 in ids4:
            #     #try:
            #     if id4 == 'currency_spending':
            #         d[id4] = page.locator(f"//div[@id='{id4}']//button/div").text 
            #     else: d[id4] = page.locator(f"//div[@id='{id4}']//input[@type='text']").get_attribute('value')

            # #BLOK6
            # blok = 6
            # page.locator(f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # # wait biar isiannya muncul dulu
            # WebpageWait(page, 10).until(
            #     lambda d: d.locator("//div[@id='airline_departure']//button/div").text.strip() != "" and
            #             d.locator("//div[@id='airline_arrival']//button/div").text.strip() != ""
            # )
            # #
            # radios14 = page.find_elements(By.XPATH, f"//div[@id='main_occupation']//input[@type='radio']")
            # for r in radios14:
            #     if r.is_selected(): break
            # d['r14'] = r.get_attribute('value')
            # # r15 skip 
            # d['r16'] = page.locator("//div[@id='freq_visit']//input[@type='text']").get_attribute('value')
            # #
            # for i in ['arrival', 'departure']:
            #     d[f'r18a_{i}'] = page.locator(f"//div[@id='airline_{i}']//button/div").text 
            #     d[f'r18b_{i}'] = page.locator(f"//div[@id='currency_{i}']//button/div").text 
            #     d[f'r18c_{i}'] = page.locator(f"//div[@id='value_{i}']//input[@type='text']").get_attribute('value') 

            # #BLOK7
            # blok = 7
            # page.locator(f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # #
            # # get switch: activities_06
            # for i in range(1,15):
            #     radios19 = page.find_elements(By.XPATH, f"//div[@id='activities_{i:02}']//input[@type='radio']")
            #     for r in radios19:
            #         if r.is_selected(): break
            #     d[f'r19_{i}'] = r.get_attribute('value')
            #     #d[f'r19_{i}'] = page.locator(f"//div[@id='activities_{i:02}']//input[@type='checkbox']").is_selected()
            # radios20 = page.find_elements(By.XPATH, f"//div[@id='wonderful_indonesia']//input[@type='radio']")
            # for r in radios20:
            #     if r.is_selected(): break
            # d['r20'] = r.get_attribute('value')
            # #
            # radios21 = page.find_elements(By.XPATH, f"//div[@id='ecofriendly_principle']//input[@type='radio']")
            # for r in radios21:
            #     if r.is_selected(): break
            # d['r21'] = r.get_attribute('value')
            # #
            # radios22 = page.find_elements(By.XPATH, f"//div[@id='satisfaction_lvl']//input[@type='radio']")
            # for r in radios22:
            #     if r.is_selected(): break
            # d['r22'] = r.get_attribute('value')
            # #
            # radios23 = page.find_elements(By.XPATH, f"//div[@id='intention_to_visit']//input[@type='radio']")
            # for r in radios23:
            #     if r.is_selected(): break
            # d['r23'] = r.get_attribute('value')

            # #BLOK8
            # blok = 8
            # page.locator(f'id("fasih-form")/DIV[1]/DIV[1]/ASIDE[1]/DIV[2]/DIV[{blok}]/DIV[1]').click()
            # #
            # d['r24'] = page.find_element(By.XPATH,f"//div[@id='note']//textarea").get_attribute('value')
            # d['r25'] = page.find_element(By.XPATH,f"//div[@id='impression']//textarea").get_attribute('value')
            # radios26 = page.find_elements(By.XPATH, f"//div[@id='viplounge']//input[@type='radio']")
            # for r in radios26:
            #     if r.is_selected(): break
            # d['r26'] = r.get_attribute('value')

            # return d
            # Write to file
            log_message('Exported')
            with open("temp.json", "w") as f:
                json.dump(d, f, indent=4)  # indent=4 makes it readable
                
        except Exception as e:
            #instance.log_message(f'Terjadi error: {e}')
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_message(f"Line error: {str(exc_tb.tb_lineno)} ")
            log_message(f'Terjadi error: {e}')
        # --- END ---

        page.pause() #debugging, open recorder on playwright
        
        page.wait_for_timeout(5000)
        # browser.close()

if __name__ == "__main__":
    run()
