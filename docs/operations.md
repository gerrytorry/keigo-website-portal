# Operasional, staging, dan produksi

## Environment

`.env.example` mendokumentasikan variabel. Aplikasi membaca environment proses, **tidak otomatis memuat `.env`**. Simpan rahasia pada secret store hosting/environment service.

|Variabel|Kegunaan|
|---|---|
|APP_ENV|development; staging/production mewajibkan PostgreSQL dan SECRET_KEY|
|SECRET_KEY|Rahasia acak panjang berbeda per lingkungan; lokal memakai .local-secret|
|ALLOWED_HOSTS|Hostname sah tanpa skema, dipisah koma|
|PUBLIC_ORIGIN|URL HTTPS canonical staging/produksi|
|CSRF_TRUSTED_ORIGINS|Origin HTTPS yang sah|
|DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT|PostgreSQL terpisah per lingkungan, role database non-superuser|
|PRIVATE_MEDIA_ROOT|Volume persisten privat di luar document root|
|SQLITE_PATH|Opsional untuk lokal; default data.sqlite3|
|EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL|SMTP TLS untuk pemulihan password|

Token reset berlaku satu jam dan sekali pakai. Tanpa SMTP, UI menyatakan layanan belum aktif. Notifikasi rekrutmen saat ini hanya dalam aplikasi.

## Staging

1. Siapkan hostname staging, TLS, PostgreSQL dan private volume terpisah. Gunakan data sintetis.
2. Instal requirements dalam venv. Set APP_ENV=staging dan variabel di atas.
3. Jalankan `python manage.py migrate --noinput`, `python manage.py collectstatic --noinput`, dan `python manage.py check --deploy`.
4. Jalankan WSGI lewat service manager: `waitress-serve --listen=127.0.0.1:8000 --url-scheme=https config.wsgi:application`, di belakang reverse proxy TLS. Port WSGI hanya dapat dicapai secara lokal. Reverse proxy meneruskan Host yang sah; jangan percaya forwarded header klien umum.
5. Reverse proxy melayani `/static/` dari staticfiles. Request lain masuk aplikasi. **Jangan** membuat alias publik ke private-media. Batasi body 6 MB dan request rate. Redaksi token pada access log `/pulihkan/`.
6. Buat admin dengan bootstrap CLI. Uji cookie Secure, CSRF, redirect HTTPS, ownership, upload, ekspor, SMTP dan backup/restore PostgreSQL.
7. Database dan private volume harus bertahan saat code release berubah. Ambil backup sebelum migrasi; jangan menghapus database untuk update rutin.

## Cutover

Website lama tetap aktif. Pekerjaan ini tidak mengubah DNS atau situs live. Pengelola perlu mengesahkan konten, domain, kebijakan data, akun, SMTP, monitoring, backup dan hasil staging. Migrasi WordPress/pendaftaran lama membutuhkan inventaris dan mapping terpisah. Cutover memerlukan persetujuan pengelola. Siapkan rollback ke rilis dan backup yang kompatibel.

## Pemulihan akun

Gunakan alur email bila SMTP tersedia. Jika belum, pengelola memverifikasi identitas melalui prosedur lembaga lalu operator berwenang menggunakan `python manage.py changepassword email@akun`. Jangan meminta password lama. Password baru dimasukkan privat. Pergantian password membuat sesi lama tidak valid. Akun dengan is_active=False tidak dapat masuk.

## Backup lokal

Hentikan penulisan/unggahan selama backup agar database dan file konsisten. Dari folder aplikasi, gunakan tujuan **folder baru**:

```text
python scripts/backup_local.py backup . ../../work/backup-keigo-baru
python scripts/backup_local.py restore ../../work/backup-keigo-baru ../../work/restore-keigo-baru
```

Tool memakai SQLite backup API, integrity_check, private-media dan manifest SHA256. Restore tidak menimpa database aktif. Jalankan hasil restore dengan kode kompatibel dan arahkan SQLITE_PATH serta PRIVATE_MEDIA_ROOT ke folder hasil restore. Secret disimpan terpisah; kehilangan secret membatalkan sesi/token, bukan menghapus CV. Tool lokal mengasumsikan nama data.sqlite3 dan private-media default; path kustom perlu dibackup secara eksplisit.

## Backup PostgreSQL produksi

Belum ada jadwal backup otomatis. Pengelola harus menjadwalkannya:

1. Maintenance singkat untuk menghentikan penulisan/unggahan.
2. `pg_dump -Fc -f keigo.dump DATABASE_NAME`, memakai credential service/PGPASSFILE, bukan password pada command line.
3. Snapshot/salin seluruh PRIVATE_MEDIA_ROOT pada waktu yang sama. Simpan manifest hash dan identifier rilis/migrasi.
4. Enkripsi backup, simpan off-host dan batasi operator. Usulan retensi awal: harian 14 hari + mingguan 8 minggu; pengelola menetapkan kebijakan final.
5. Restore drill ke database baru: `createdb keigo_restore`, lalu `pg_restore --no-owner --dbname=keigo_restore keigo.dump`. Pulihkan file ke volume baru; validasi jumlah record/relasi dan uji download/ekspor.
6. Setelah lolos, alihkan environment saat maintenance. Jangan menguji restore langsung pada database produksi.

Backup/restore PostgreSQL belum dijalankan karena instance tidak tersedia. Backup/restore SQLite dengan data sintetis dan media telah dijalankan.

## Logging dan file

Audit tersedia pada `/admin/audit/`: tindakan, ID, versi, bukan isi file/password. Error ekspor tercatat pada server dengan pesan UI umum. Atur rotasi log/alert pada service manager. Upload memeriksa ukuran, extension, signature PDF dan decode gambar; ini bukan antivirus. Kontrol malware/quarantine, enkripsi volume/backup, monitoring dan pembatasan akses harus dipasang pada infrastruktur produksi.
