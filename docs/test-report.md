# Hasil pengujian aktual

Tanggal: 27 September 2026. Lokal Windows, Python 3.12, Django 5.2.17, SQLite. Semua data pengujian sintetis.

## Otomatis

`python manage.py test core --noinput`: **37 tes lulus**, 32.962 detik pada run lengkap terakhir. Database sementara dibuat dan dibuang oleh test runner. Tes tidak memakai data personal workbook sumber.

Cakupan: public/protected routes; register/login/logout/password hash; duplicate email; mass assignment/role escalation; CSRF; login throttle; ownership profil/aplikasi/dokumen; autosave dan revision conflict; repeated rows create/edit/delete/ownership; tanggal ISO setelah render lokal Indonesia; submit/revisi/resubmit/verifikasi; snapshot pengajuan; perubahan verified profile; closed/expired job; job closes setelah halaman konfirmasi; duplicate application; stage/history; bulk confirmation/stale update; job create/edit/archive conflict; private download; invalid/oversize upload; replacement/history; missing file; document review/notification; internal notes; notification read state; interview; session revocation; XSS; formula injection; XLSX mapping/overflow/sanitization/source preservation; simulated export failure; password-reset token sekali pakai dan generic response; SMTP tidak aktif.

Pengujian benturan memakai revision token/stale requests. Belum ada uji beban paralel atau PostgreSQL multi-worker.

`manage.py check`: tidak ada issue. `makemigrations --check --dry-run`: tidak ada perubahan skema tertinggal. `node --check core/static/core/site.js`: lulus.

`manage.py check --deploy` dijalankan memakai konfigurasi staging sementara (tanpa koneksi database). Dua warning tersisa: W005 HSTS includeSubDomains dan W021 preload. Tidak diaktifkan otomatis karena cakupan semua subdomain belum disahkan. Ini adalah pemeriksaan konfigurasi, **bukan** bukti deploy, koneksi PostgreSQL, atau TLS nyata.

## Browser nyata

Registrasi siswa → isi identitas → autosave → refresh → tanggal/nilai tetap ada → tambah pendidikan → simpan. Data wajib lain dilengkapi melalui fixture sintetis untuk melanjutkan pengujian. Review CV → checkbox → dialog konfirmasi → submit berhasil. Admin login → temukan siswa → verifikasi → ekspor XLSX melalui tombol download. Siswa login → pilih lowongan uji → konfirmasi → pengajuan dan timeline muncul. Admin membuka kandidat → ubah tahap → history bertambah. Riwayat kerja ditambah melalui browser; autosave bertahan setelah refresh dan status CV memerlukan verifikasi ulang. Snapshot pengajuan tetap versi sebelumnya. Gambar dokumen sintetis diunggah melalui file chooser; status privat muncul.

Menu mobile diuji dengan keyboard; galeri dibuka, next, ArrowLeft, ESC, focus/close diamati. Console browser terakhir: tidak ada warning/error aplikasi. Interaksi keyboard digunakan karena sebagian aksi klik pada kontrol otomasi browser tidak mengaktifkan elemen; pemeriksaan ini tidak diklaim sebagai matriks perangkat touch nyata.

## Responsive

Ukuran 320, 375, 430, 768, 1440 diuji pada homepage, login, registrasi, CV pendidikan, upload, daftar/detail lowongan, dashboard siswa, timeline aplikasi, dashboard admin, daftar lowongan admin, form lowongan, serta detail siswa admin. Lebar scroll halaman tidak melebihi viewport. Screenshot visual diperiksa pada homepage desktop, formulir 320px, dan timeline 375px. Sidebar portal memiliki scroll horizontal terkontrol pada mobile; halaman tidak overflow. Homepage dan dashboard siswa juga diperiksa pada 2560px tanpa overflow. Galeri mobile 320px diperiksa secara visual.

## XLSX

File yang diunduh browser `CV_KEIGO_1_v4.xlsx` dibuka kembali menggunakan openpyxl. Nama E5, telepon E11 termasuk nol awal, sekolah H14, keluarga B28 benar. Template tidak memiliki hyperlink/comment personal. Ekspor sintetis juga dirender menjadi gambar untuk memeriksa tabel secara visual. Field tetap pada struktur tabel sumber; teks panjang disertakan pada Data Lengkap, baris overflow pada Lanjutan. Pengujian bukan sertifikasi kesamaan cetak di setiap versi Microsoft Excel.

SHA256 workbook asli setelah pengujian:

`c9b3df7414c0f6b47ae1ce857e3a4f651fb8c149b19a946bd6ca4ebd10270047`

Sama dengan hash audit awal. Workbook sumber tidak berubah.

## Backup

Backup SQLite+private media ke folder baru, restore ke folder baru lain, manifest SHA256 dan SQLite integrity_check berhasil. Belum ada jadwal backup otomatis; backup PostgreSQL belum diuji.

## Perbaikan dari pengujian

Format DateInput ISO setelah reload; selector tombol dialog konfirmasi; antrean autosave; IDs baris baru setelah autosave; opsi filter Magang yang markup-nya salah; title halaman; aria-label menu setelah ESC; pembersihan hyperlink template; close stream download pada tes Windows; path route pada tes job CRUD; regex skema HTTPS pada tes reset. Header Referrer-Policy sempat menyebabkan Origin null pada browser; dikembalikan ke same-origin, logout diuji ulang berhasil. Run lengkap diulang sampai semua 37 tes lulus.


## Verifikasi pengajuan CV terbaru — 27 September 2026

PASS: 55 tes backend dan tes frontend submission. Uji browser koneksi terputus sebelum commit dan respons hilang sesudah commit, refresh/login, admin serta database selesai. Detail dan batasan: [submission-fix-report.md](submission-fix-report.md).
