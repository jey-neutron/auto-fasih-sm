# Welcome to Auto-Fasih-SM🤖

(Program auto approve Fasih-SM kerjaan B P S)

Disini kita menggunakan Chromedriver untuk mengautomasi browser Chrome anda. Download aja folder [`dist`](/dist) dan jalankan file [`.exe`](/dist/Selenium_vpn_tkinter.exe)nya. 
> Saat ini pakai Chrome versi 144, jadi harus disamain versinya. Kalau pake Chrome versi lain, chromedriver harus sama versinya juga biar lanjay.

Ketika file [`Selenium_vpn_tkinter.exe`](/dist/Selenium_vpn_tkinter.exe) udah jalan, maka muncul window aplikasi baru:
1. Masukkan `username` dan `password` untuk login SSO. Kemudian di bawahnya ada `Link target`. Default target link-nya adalah web Fasih-SM.
2. Kemudian `Open Browser` dan aplikasi akan auto membuka browser. `Goto Link` maka browser akan menuju link sesuai `Link target` yang terisi pada langkah 1. 
	> Target link  jika terisi default (fasih-sm.bps.go.id) atau sso.bps.go.id maka akan auto login ke SSO. Biarin browsernya jalan sendiri gausah diganggu. 
3. Fitur `Get List Data` akan mengambil list row pada tab data di Fasih-SM dan akan menyimpannya di file `data.csv` di folder yang sama. 
	> Jika anda menggunakan fitur ini, maka setelah browser menuju link, anda perlu search/click survei **manual** sampai ke **tab data** di Fasih-SM, baru klik `Get List Data`

	> Tujuan fitur ini adalah mendapatkan link per row di Fasih-SM (perlu dilakukan jika mau auto-approve/get-data di Fasih-SM)

	- `Rewrite` data.csv: membuat file baru (jika file belum ada) atau menimpa data.csv (jika sebelumnya udah ada file ini)
	- `Append` data.csv: menambahkan list data pada data.csv yang udah ada

4. Jika ingin run auto-approve, ada beberapa parameter yang perlu dimasukkan:
	- `"Baris mulai"`, diisi bilangan bulat `0,1,2,...`, isi `0` jika mulai dari awal atau biar dia ga error,
	- `"Nama file"`, adalah nama file csv yang ingin dipake. Jika tadi pake file data dari fitur `Get List Data` (dan ga merename file outputnya) maka isi `data.csv`,
	- `"Input Tambahan"`, ini modul yang dapat anda modifikasi untuk mendapatkan data di Fasih-SM, atau web lain, contoh yang ada di sini adalah `getdataPES` (untuk mendapatkan isian Fasih PES) atau `inputsbr` (untuk menginput GC matchapro dari excel, tapi perlu modheader).
		> Jika kosong, maka program akan tetap jalan tanpa mengambil data, misal mau approve aja
		
		> Jika ingin menjalankan program diluar Fasih-SM, maka di bawahnya pilih `NonFasih`

		> Anda bisa menambahkan function sendiri di [`get_data.py`](/dist/get_data.py) kemudian memasukkan nama functionnya itu di field ini
	-  `Sekalian approve Fasih` jika terpilih `True` maka akan auto-approve dengan user SSO yang udah login. Kalau `False` maka ya ngga approve, misal jika ingin mengambil datanya aja (tapi juga perlu nambah kode).

5. Klik `Run Function` and the program will do it for u.
	> Data yang udah dieksekusi biasanya akan ada perubahan value suatu kolom di file dengan `Nama File` yang terpilih tadi.

Semoga tidak membingung 🍵😇
