# Welcome to Auto-Fasih-sm🤖

(Program auto approve Fasih-sm)

Here, we'll be using Chromedriver with Google Chrome version 144, so make sure you're using that version for smooth operation.
Just download the [`dist`](/dist) folder and run the [`.exe`](/dist/Selenium_vpn_tkinter.exe) file. You can add your own function which can be added in [`get_data.py`](/dist/get_data.py)
1. Enter your `username` and `password` to log in to fasih-sm. The default target link is the fasih-sm homepage.
2. The program will open your chrome browser and go to the link. Then search/click for the survey **manually** until you reach the **data tab**.
3. `Get List data` to retrieve the dataframe there (this is to get the link). The program will run automatically and be exported as `data.csv`, see there. There are two options if you do `Get list data` several times, namely `'rewrite'` the output data (data.csv) or add (`'append'`) the output data to the existing data.csv. 
4. If you want to run auto-approve, you can enter parameters, such as 

> - "Baris mulai" / start line, with integer value, `0,1,2,...`
> - "Nama file" / file name (this is the name of the file used; if you're using the data from the get list, you'll use `data.csv`),
> - "Input Tambahan" / optional additional input (this can be modified if you want to **retrieve data** as well, or something else, you can modify it in get_data.py, then just fill the field with the created function, for example, `getrandom`).
> - And there's an additional option: whether to approve or not. The "False" option is usually used if you only want to get data and not approve, and this field requires an additional input field or adding your own function. U can add your own function that not related with Fasih and choosing the "NonFasih".
5. Then hit `Run Function` and the program will do it for u
