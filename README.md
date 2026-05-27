# ![Logo Auto-Fasih-SM](assets/ikonku.ico) Welcome to Auto-Fasih-SM 

(Program auto approve Fasih-SM kerjaan B P S)

Disini kita menggunakan Playwright di versi 2.0.0 untuk mengautomasi browser Chrome anda, pake beberapa request Get & Post. Download aja folder [`dist`](/dist) dan jalankan file [`.exe`](/dist/Auto_Fasih_SM.exe)nya. 


# Step-by-step 🚗
> **👼Tutorial versi "Bahasa Bayi" [`disini`](/STEP-BY-STEP-%20AUTO-FASIH.pdf)**

Ketika file [`Auto_Fasih_SM.exe`](/dist/Auto_Fasih_SM.exe) udah jalan, maka muncul window aplikasi baru:
1. Masukkan `username` dan `password` untuk login SSO. Kemudian di bawahnya ada `Link target`. Default target link-nya adalah web Fasih-SM.
2. Kemudian `Start Browser` dan aplikasi akan auto membuka browser. `Goto Link` maka browser akan menuju link sesuai `Link target` yang terisi pada langkah 1. 
	> Target link  jika terisi default (fasih-sm.bps.go.id) atau sso.bps.go.id maka akan auto login ke SSO. Biarin browsernya jalan sendiri gausah diganggu. 
3. Fitur `Get List Data` akan mengambil list row pada tab data di Fasih-SM dan akan menyimpannya di file `data.csv` di folder yang sama. 
	> Jika anda menggunakan fitur ini, maka setelah browser menuju link, anda perlu search/click survei **manual** sampai ke **tab data** di Fasih-SM, baru klik `Get List Data`

	> Tujuan fitur ini adalah mendapatkan link per row di Fasih-SM (perlu dilakukan jika mau auto-approve/get-data di Fasih-SM)

	- `Rewrite` data.csv: membuat file baru (jika file belum ada) atau menimpa data.csv (jika sebelumnya udah ada file ini)
	- `Append` data.csv: menambahkan list data pada data.csv yang udah ada

4. Jika ingin run auto-approve, ada beberapa parameter yang perlu dimasukkan:
	- `"Baris mulai"`, diisi bilangan bulat `0,1,2,...`, isi `0` jika mulai dari awal atau biar dia ga error,
	- `"Nama file"`, adalah nama file csv yang ingin dipake. Jika tadi pake file data dari fitur `Get List Data` (dan ga merename file outputnya) maka isi `data.csv`,
	- `"Input Tambahan"`, ini modul yang dapat anda modifikasi untuk mendapatkan data di Fasih-SM, atau web lain, contoh yang ada di sini adalah `getdataPES` (untuk mendapatkan isian Fasih PES).
		> Jika kosong, maka program akan tetap jalan tanpa mengambil data, misal mau approve aja
		
		> Jika ingin menjalankan program diluar Fasih-SM, maka di bawahnya pilih `NonApprov`

		> Anda bisa menambahkan function sendiri di [`get_data.py`](/dist/get_data.py) kemudian memasukkan nama functionnya itu di field ini
	-  `Sekalian approve Fasih` jika terpilih `True` maka akan auto-approve dengan user SSO yang udah login. Kalau `False` maka ya ngga approve, misal jika ingin mengambil datanya aja (perlu code tambahan jika di survei lain). `Reject` buat Reject semua di dalam csv, dan `NonApprov` untuk selain Fasih.

5. Klik `Run Function` and the program will do it for u.
	> Data yang udah dieksekusi biasanya akan ada perubahan value suatu kolom di file dengan `Nama File` yang terpilih tadi. Tergantung code anda juga.

Semoga tidak membingung 🍵😇


# Fitur📱
Fitur yang sudah tersedia di [`get_data.py`](/dist/get_data.py) untuk saat ini:

- **ver** (melihat version app)
- **help** (get list of functions)
- **getrandom** (get a random number)
- **seedata** (get detail data pada csv dan index data terpilih [Pake "NonApprov"])
- **getkurs** (convert kurs data dari idr.json hasil dari api web exchangerate-api.com [pake "NonApprov"] [https://v6.exchangerate-api.com/v6/api-key/latest/idr])
- **getdataAll** (function for getting data general survey (mybe ada kendala, tpi sementara ini deh dan belum dicoba))
- **getdataPES** (function for getting data pes)

