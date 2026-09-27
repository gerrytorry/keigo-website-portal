# Kesiapan produksi

**Implementasi lokal telah diuji; belum dinyatakan siap go-live.** Tidak ada deployment, DNS, atau cutover yang dilakukan.

|Area|Status|Tindakan sebelum go-live|
|---|---|---|
|Website, auth, CV, admin, workflow, export|Diuji lokal|Uji penerimaan pengelola|
|PostgreSQL|Konfigurasi tersedia; koneksi belum diuji|Sediakan staging, migrasi, uji transaksi paralel|
|HTTPS, hosting, static/private volume|Panduan tersedia|Pasang TLS, WSGI, reverse proxy, uji cookie/redirect|
|SMTP reset password|Backend/token diuji tanpa kirim eksternal|Isi credential, uji pengiriman nyata|
|Backup|Backup/restore SQLite diuji|Jadwalkan PostgreSQL+media dan restore drill|
|Upload|Validasi ukuran/type/signature/gambar|Belum ada antivirus/quarantine|
|Konten institusi|Mengikuti sumber|Sahkan konten, kontak, hak foto, kebijakan data|
|Data website lama|Belum dimigrasi|Inventaris, mapping, persetujuan cutover|

## Audit demo dan placeholder

- LOCAL-ACCESS.md, data.sqlite3, .local-secret, private-media adalah lingkungan uji lokal, dikecualikan dari ZIP. Jangan bawa database demo ke produksi.
- Siswa/admin/lowongan berlabel uji hanya ada lokal. Tests menggunakan example.test dan database sementara. Migrasi tidak menanam data demo.
- Semua foto publik diekstrak dari company profile, terpusat pada content.py dan static assets. Tidak ada foto stok atau persona rekaan.
- Gaji kosong ditampilkan “belum dicantumkan/dikonfirmasi pengelola”, bukan nominal buatan.
- Statistik PDF yang bertentangan tidak dijadikan klaim publik. Legalitas/mitra/hasil rekrutmen yang belum terverifikasi tidak dibuat-buat. Tautan sosial generik tidak diklaim sebagai akun resmi.
- localhost merupakan default pengembangan. PUBLIC_ORIGIN, ALLOWED_HOSTS dan CSRF origins harus diatur untuk produksi.
- APP_ENV produksi mematikan DEBUG dan menolak start tanpa SECRET_KEY serta PostgreSQL.
- Tidak ada pengiriman notifikasi rekrutmen melalui WhatsApp/email. Tautan kontak WhatsApp dibuka oleh pengguna.

## Batas implementasi

Autosave baris baru menunggu field wajib valid; penghapusan memakai Simpan draft. Tidak ada pemulihan offline setelah tab ditutup sebelum server menyimpan. XLSX mengikuti tabel sumber; teks panjang tetap tersedia utuh pada Data Lengkap/Lanjutan walau bidang cetak utama terbatas. Ekspor PDF opsional belum dibuat. Syarat gender/berat dapat ditulis pada persyaratan; belum ada modul lampiran lowongan terpisah. Perbandingan persyaratan tidak memutuskan kelulusan otomatis.

Belum ada audit keamanan independen, uji beban produksi, pengujian PostgreSQL paralel, atau validasi SMTP/TLS nyata.
