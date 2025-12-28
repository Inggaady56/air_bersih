import csv
import os
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt

FILE_USER = "data_user.csv"
FILE_TAGIHAN = "data_tagihan.csv"
FILE_PROMO = "data_promo.csv"
FILE_VOUCHER = "data_voucher.csv" 

HARGA_TETAP = {"Bawah": 250000, "Menengah": 500000, "Atas": 1000000}
TARIF_PROGRESIF_PER_10M = {"Bawah": 1000, "Menengah": 1500, "Atas": 2500}

def kirim_email_notifikasi(email_tujuan, subjek, pesan, file_lampiran=None):
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_user = ""
    smtp_password = ""
    pesan_email = EmailMessage()
    pesan_email['Subject'] = subjek
    pesan_email['From'] = f"Admin Sistem Air <{smtp_user}>"
    pesan_email['To'] = email_tujuan
    pesan_email.set_content(pesan)
    
    if file_lampiran and os.path.exists(file_lampiran):
        try:
            with open(file_lampiran, 'rb') as berkas:
                data_berkas = berkas.read()
                nama_berkas = os.path.basename(file_lampiran)
            pesan_email.add_attachment(data_berkas, maintype='application', subtype='octet-stream', filename=nama_berkas)
        except Exception as e:
            print(f"⚠️ Gagal melampirkan berkas: {e}")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password) 
            server.send_message(pesan_email)
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ Error: Gagal Login Email. Cek password aplikasi Gmail Anda.")
    except Exception as kesalahan:
        print(f"❌ Gagal mengirim email: {kesalahan}")
    return False

def buat_berkas_struk(username, nama_pelanggan, total_bayar, metode, nominal_diskon, jumlah_tagihan):
    waktu_saat_ini = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama_file_struk = f"struk_{username}_{waktu_saat_ini}.txt"
    
    isi_struk = f"""
==========================================
          STRUK PEMBAYARAN LUNAS
==========================================
Tanggal       : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Username      : {username}
Nama Pelanggan: {nama_pelanggan}
Jumlah Tagihan: {jumlah_tagihan} Periode
------------------------------------------
Total Bayar   : Rp{int(total_bayar):,}
Potongan      : {f"Rp{int(nominal_diskon):,}" if nominal_diskon > 0 else "Tidak Ada"}
Metode Bayar  : {metode}
Status        : LUNAS
------------------------------------------
      Terima Kasih Atas Pembayaran Anda
==========================================
"""
    try:
        with open(nama_file_struk, "w") as berkas:
            berkas.write(isi_struk)
        return nama_file_struk
    except Exception as e:
        print(f"❌ Gagal membuat berkas struk: {e}")
        return None

def baca_data_csv(nama_file):
    daftar_data = []
    try:
        if not os.path.exists(nama_file): 
            return daftar_data
        with open(nama_file, "r", encoding='utf-8') as berkas:
            pembaca = csv.reader(berkas)
            for baris in pembaca:
                daftar_data.append(baris)
    except PermissionError:
        print(f"❌ Error: File {nama_file} sedang dibuka program lain. Tutup file tersebut!")
    except Exception as e:
        print(f"❌ Error saat membaca file {nama_file}: {e}")
    return daftar_data

def simpan_tagihan_baru(username, nominal, jatuh_tempo):
    try:
        with open(FILE_TAGIHAN, "a", newline='') as berkas:
            penulis = csv.writer(berkas)
            penulis.writerow([username, nominal, "Belum Bayar", jatuh_tempo])
    except Exception as e:
        print(f"❌ Gagal menyimpan tagihan: {e}")

def perbarui_status_pembayaran(username):
    try:
        data_tagihan = baca_data_csv(FILE_TAGIHAN)
        with open(FILE_TAGIHAN, "w", newline='') as berkas:
            penulis = csv.writer(berkas)
            for baris in data_tagihan:
                if baris[0] == username and baris[2] == "Belum Bayar":
                    baris[2] = "Lunas"
                penulis.writerow(baris)
    except Exception as e:
        print(f"❌ Gagal memperbarui status: {e}")


def tampilkan_grafik_pendapatan():
    try:
        data_tagihan = baca_data_csv(FILE_TAGIHAN)
        total_lunas = 0
        total_piutang = 0
        
        for baris in data_tagihan:
            try:
                nominal = int(baris[1].replace(".", ""))
                if baris[2] == "Lunas":
                    total_lunas += nominal
                else:
                    total_piutang += nominal
            except (ValueError, IndexError):
                continue

        if total_lunas == 0 and total_piutang == 0:
            print("❌ Data tagihan masih kosong.")
            return

        label_status = ['Lunas (Pendapatan)', 'Belum Bayar (Piutang)']
        nilai_nominal = [total_lunas, total_piutang]
        warna_grafik = ['#2ecc71', '#e74c3c']

        plt.figure(figsize=(10, 6))
        batang = plt.bar(label_status, nilai_nominal, color=warna_grafik)
        plt.title('Laporan Statistik Keuangan Tagihan Air', fontsize=14)
        plt.ylabel('Jumlah Rupiah (Rp)', fontsize=12)
        
        for b in batang:
            tinggi = b.get_height()
            plt.text(b.get_x() + b.get_width()/2., tinggi, f'Rp{int(tinggi):,}', ha='center', va='bottom')

        print("📊 Membuka grafik laporan... Tutup jendela grafik untuk kembali.")
        plt.show()
    except Exception as e:
        print(f"❌ Error saat menampilkan grafik: {e}")

def cek_validasi_voucher(kode_input):
    data_voucher = baca_data_csv(FILE_VOUCHER)
    for v in data_voucher:
        if v[0] == kode_input.upper():
            return float(v[1])
    return 0

def ambil_promo_aktif():
    data_promo = baca_data_csv(FILE_PROMO)
    if len(data_promo) > 1: 
        return data_promo[1][0], float(data_promo[1][1])
    return None, 0

def registrasi_pengguna():
    print("\n" + "="*35 + "\n   REGISTRASI PELANGGAN BARU \n" + "="*35)
    username = input("Username baru: ").lower()
    password = input("Password baru: ")
    nama_lengkap = input("Nama Lengkap: ")
    email = input("Alamat Email: ")
    print("\nPilih Tipe Layanan:\n1. Bawah\n2. Menengah\n3. Atas")
    pilihan_tipe = input("Pilihan (1/2/3): ")
    tipe_layanan = "Bawah" if pilihan_tipe == '1' else "Menengah" if pilihan_tipe == '2' else "Atas"
    
    try:
        with open(FILE_USER, "a", newline='') as berkas:
            csv.writer(berkas).writerow([username, password, nama_lengkap, "user", email, tipe_layanan])
        print(f"✅ Registrasi Berhasil untuk {nama_lengkap}!")
    except Exception as e:
        print(f"❌ Gagal registrasi: {e}")

def validasi_akses(username_input, password_input):
    data_user = baca_data_csv(FILE_USER)
    for user in data_user:
        if len(user) >= 6:
            if username_input == user[0] and password_input == user[1]:
                return True, user[2], user[3], user[4], user[5]
    return False, None, None, None, None

while True:
    print("\n" + "—"*30 + "\n  SISTEM INFORMASI TAGIHAN AIR\n" + "—"*30)
    print("1. Login Pengguna\n2. Registrasi Pelanggan\n3. Keluar Sistem")
    pilihan_awal = input("Pilih menu: ")

    if pilihan_awal == '1':
        user_masuk = input("Username: ").lower()
        pass_masuk = input("Password: ")
        
        status_login, nama_user, peran_user, email_user, tipe_user = validasi_akses(user_masuk, pass_masuk)

        if status_login:
            print(f"\n✅ Login Berhasil! Selamat datang, {nama_user}.")
            while True:
                if peran_user == "admin":
                    print("\n--- DASHBOARD ADMIN ---")
                    print("1. Kirim Tagihan\n2. Kelola Promo\n3. Buat Voucher\n4. Laporan Grafik\n5. Logout")
                    pilihan_admin = input("Pilih: ")
                    
                    if pilihan_admin == '1':
                        target = input("Username pelanggan: ").lower()
                        semua_user = baca_data_csv(FILE_USER)
                        ditemukan = False
                        for baris in semua_user:
                            if baris[0] == target:
                                tipe_pilih = baris[5]
                                try:
                                    kubik_input = input(f"Masukkan pemakaian m3 untuk {baris[2]}: ")
                                    kubik = float(kubik_input)                                   
                                    biaya_tetap = HARGA_TETAP[tipe_pilih]
                                    biaya_tambahan = (kubik / 10) * TARIF_PROGRESIF_PER_10M[tipe_pilih]
                                    subtotal = biaya_tetap + biaya_tambahan                                    
                                    nama_promo, persen_diskon = ambil_promo_aktif()
                                    potongan_promo = subtotal * (persen_diskon / 100)
                                    total_setelah_promo = subtotal - potongan_promo
                                    pajak = total_setelah_promo * 0.10
                                    total_akhir = total_setelah_promo + pajak
                                    fmt_biaya_tetap = f"{int(biaya_tetap):,}".replace(",", ".")
                                    fmt_biaya_tambahan = f"{int(biaya_tambahan):,}".replace(",", ".")
                                    fmt_pajak = f"{int(pajak):,}".replace(",", ".")
                                    format_total = f"{int(total_akhir):,}".replace(",", ".")
                                    
                                    info_promo_msg = ""
                                    if nama_promo:
                                        fmt_potongan = f"{int(potongan_promo):,}".replace(",", ".")
                                        info_promo_msg = f"- Promo ({nama_promo}) : -Rp{fmt_potongan}\n"

                                    msg_full = (f"Halo {baris[2].title()}.\n\n"
                                               f"Rincian Tagihan ({tipe_pilih}):\n"
                                               f"- Biaya Tetap : Rp{fmt_biaya_tetap}\n"
                                               f"- Pemakaian berlebih : Rp{fmt_biaya_tambahan}\n"
                                               f"{info_promo_msg}"
                                               f"- Pajak (10%) : Rp{fmt_pajak}\n"
                                               f"----------------------------\n"
                                               f"TOTAL AKHIR : Rp{format_total}")

                                    tgl_jt = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                                    
                                    if kirim_email_notifikasi(baris[4], f"Tagihan Air - {baris[2].title()}", msg_full):
                                        print(f"✔ Email rincian dikirim ke {baris[4]}.")
                                    
                                    simpan_tagihan_baru(target, format_total, tgl_jt)
                                    print(f"✔ Tagihan berhasil diproses.")
                                except ValueError:
                                    print("❌ Error: Input pemakaian harus berupa angka.")
                                ditemukan = True; break
                        if not ditemukan: print("❌ User tidak ditemukan.")

                    elif pilihan_admin == '4':
                        tampilkan_grafik_pendapatan()
                    elif pilihan_admin == '5': break

                elif peran_user == "user":
                    print("\n--- MENU PELANGGAN ---")
                    print("1. Cek Riwayat Tagihan\n2. Bayar\n3. Logout")
                    pilihan_user = input("Pilih: ")

                    if pilihan_user == '1':
                        semua_tagihan = baca_data_csv(FILE_TAGIHAN)
                        print("\n--- DATA TAGIHAN ANDA ---")
                        ada = False
                        for t in semua_tagihan:
                            if t[0] == user_masuk:
                                print(f"Rp{t[1]} | {t[2]} | JT: {t[3]}")
                                ada = True
                        if not ada: print("Belum ada data tagihan.")

                    elif pilihan_user == '2':
                        semua_tagihan = baca_data_csv(FILE_TAGIHAN)
                        akumulasi_biaya = 0
                        jumlah_item = 0
                        for t in semua_tagihan:
                            if t[0] == user_masuk and t[2] == "Belum Bayar":
                                akumulasi_biaya += int(t[1].replace(".", ""))
                                jumlah_item += 1
                        
                        if jumlah_item > 0:
                            print(f"\nTotal Tagihan ( {jumlah_item} Periode ): Rp{akumulasi_biaya:,}")
                            kode = input("Masukkan Voucher (Kosongkan jika tidak ada): ")
                            potongan = cek_validasi_voucher(kode) if kode else 0
                            
                            bayar_akhir = max(0, akumulasi_biaya - potongan)
                            print(f"Total Bayar: Rp{int(bayar_akhir):,}")
                            metode = "Transfer" if input("Metode (1. Bank | 2. E-Wallet): ") == '1' else "E-Wallet"
                            
                            perbarui_status_pembayaran(user_masuk)
                            berkas = buat_berkas_struk(user_masuk, nama_user, bayar_akhir, metode, potongan, jumlah_item)
                            
                            if kirim_email_notifikasi(email_user, "Pembayaran Lunas", "Terima kasih, pembayaran Anda telah kami terima.", berkas):
                                print(f"✅ Sukses! Struk dikirim ke {email_user}.")
                            else:
                                print(f"✅ Sukses! Struk disimpan: {berkas} (Email Gagal).")
                        else: print("❌ Tidak ada tagihan tertunggak.")

                    elif pilihan_user == '3': break
        else: print("❌ Login Gagal. Periksa kembali username/password.")

    elif pilihan_awal == '2':
        registrasi_pengguna()
    elif pilihan_awal == '3':
        break
