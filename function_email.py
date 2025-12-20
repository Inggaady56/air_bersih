def kirim_email(email_tujuan, nama_user, jumlah, tipe, tgl_jatuh_tempo):
    smtp_server = "......."
    smtp_port = 465
    smtp_user = "......."
    smtp_password = "........." 
    
    msg = EmailMessage()
    msg['Subject'] = f"Tagihan Bulanan {tipe} - {nama_user}"
    msg['From'] = f"Admin Sistem <{smtp_user}>"
    msg['To'] = email_tujuan
    msg.set_content(
        f"Halo {nama_user},\n\n"
        f"Ini adalah tagihan rutin untuk layanan tipe {tipe}.\n"
        f"Total Biaya: Rp{jumlah}\n"
        f"Jatuh Tempo: {tgl_jatuh_tempo}\n\n"
        f"Silakan lakukan pembayaran tepat waktu. Terima kasih."
    )    