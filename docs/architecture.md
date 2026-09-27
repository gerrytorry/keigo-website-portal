# Arsitektur
Monolit Django 5.2 LTS dengan server-rendered templates dan JavaScript progresif. Dipilih karena autentikasi, sesi, CSRF, ORM, migrations dan validasi matang, serta integrasi ekspor XLSX Python. Tidak memakai frontend-only mock.
SQLite persisten untuk lokal; PostgreSQL untuk staging/produksi melalui konfigurasi lingkungan. Django ORM menjaga skema lintas database. Gunakan satu aplikasi core terstruktur (models, forms, services, exports, views, templates).
Public /; auth /daftar /masuk; student /student; operasi /admin (UI aplikasi khusus, bukan pemasaran). Static public terpisah dari private media. Snapshot merupakan JSON immutable yang sah sebagai catatan historis; profil operasional dan relasinya dinormalisasi.
Dependencies dipin setelah instalasi. WSGI dapat dijalankan Waitress di Windows; staging di belakang reverse proxy HTTPS. Tidak ada cutover otomatis.
