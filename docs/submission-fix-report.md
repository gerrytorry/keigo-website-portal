# Perbaikan pengajuan CV — 27 September 2026

## Pekerjaan yang dipulihkan

Implementasi sebelumnya dilanjutkan tanpa membangun ulang aplikasi. Validasi checkbox, daftar kekurangan, submission nyata, timestamp/snapshot, dan tes awal sudah tersedia. Yang belum selesai: uji koneksi/retry, pemeriksaan ulang admin/database, regresi akhir dan paket distribusi. Semuanya dilanjutkan dari keadaan tersebut.

Direktori bukan repository Git; git diff tidak tersedia. Kode ditinjau langsung dan dibandingkan dengan ZIP sebelumnya. Perbandingan 53 berkas juga mencakup perbedaan format baris, bukan 53 perubahan fungsional. Tidak ada pekerjaan sebelumnya yang dibatalkan.

## Penyebab yang teramati

Handler generik form[data-confirm] mencegat submit pertama untuk membuka konfirmasi kedua. Setelah tombol Lanjutkan pada dialog ditekan, backend lama sebenarnya berhasil menyimpan; kegagalan database pada jalur awal itu tidak berhasil direproduksi. Perbaikan menghapus konfirmasi kedua khusus CV, menggunakan checkbox sebagai konfirmasi, dan menambahkan state loading/error/retry/sukses server. Profil sebelumnya juga belum memiliki timestamp dan FK versi pengajuan secara eksplisit.

## Berkas perubahan

- core/models.py: submitted_at dan submitted_version pada StudentProfile.
- core/migrations/0002_studentprofile_submitted_at_and_more.py: migrasi aditif.
- core/migrations/0003_backfill_submission_reference.py: backfill dari audit nyata.
- core/services.py: kepemilikan, status, revision, transaksi dan snapshot.
- core/views.py: validasi konfirmasi, respons JSON, autentikasi/CSRF/error dan fallback POST biasa.
- core/static/core/cv-submit.js: checkbox, busy guard, timeout, loading, hasil dan recovery.
- core/templates/core/cv_review.html: missing fields, konfirmasi tunggal dan hasil persisten.
- core/templates/core/student_dashboard.html: status, waktu/versi dan langkah berikutnya.
- core/templates/core/admin_student.html: waktu/versi pengajuan untuk admin.
- core/test_submission.py: 18 tes submission; core/tests_cv_submit.mjs: tes frontend.
- Laporan pengujian, ZIP dan manifest distribusi.

## Frontend, backend dan transaksi

Tombol aktif hanya ketika CV lengkap dan checkbox dicentang. Saat request berlangsung: Mengajukan CV..., disabled, aria-busy dan feedback. Hanya respons sukses backend yang menghasilkan sukses UI. Error memulihkan tombol dengan pesan Indonesia dan tautan pemulihan. Native POST tanpa JavaScript tetap tersedia.

Backend memakai pemilik dari sesi, mengabaikan student_id kiriman browser, dan mempertahankan aturan wajib yang sudah ada. JSON guest 401, staff/permission/CSRF 403, validasi 422, duplikat/revision conflict 409, kegagalan pengajuan tertangkap 503. CSRF tidak dinonaktifkan.

Dalam transaksi atomik: row dikunci, revision diperiksa/dinaikkan, status canonical SUBMITTED disimpan, CVVersion dibuat, timestamp UTC dan FK versi disimpan, audit CV_SUBMITTED dan notifikasi admin dibuat. Kegagalan menggulung balik semuanya. Status SUBMITTED/UNDER_REVIEW dan revision mencegah retry membuat snapshot ganda. Editing saat pemeriksaan tetap terkunci. Tes revision/resubmission memastikan snapshot historis tidak berubah.

Pengajuan CV tetap memakai StudentProfile dan CVVersion; Application tetap berarti pemilihan lowongan dengan snapshotnya sendiri. Tidak dibuat status/tabel paralel. Migrasi lokal diterapkan setelah backup SQLite. Backfill memakai timestamp audit pengajuan dan versi milik siswa yang sama; tidak mengarang waktu jika audit tidak ada.

## Skenario A–L

| Skenario | Hasil | Pengujian yang dijalankan |
|---|---|---|
| A Incomplete + unchecked | PASS | Browser disabled; backend menolak tanpa persistence |
| B Incomplete + checked | PASS | Browser disabled, 19 kekurangan bertautan; tes backend missing fields |
| C Complete + unchecked | PASS | Browser disabled; backend tetap menolak tanpa konfirmasi |
| D Complete + checked | PASS | Browser POST nyata, loading, sukses; database SUBMITTED |
| E Rapid/repeated submit | PASS | Node dua event cepat satu fetch; repeated POST backend satu snapshot/audit/notifikasi; browser retry 409 |
| F Refresh | PASS | Reload browser membaca status/waktu/versi tersimpan; tes backend |
| G Logout/login | PASS | Browser profil 3 tetap Diajukan, 08:09 WIB, versi 1; tes backend |
| H Kepemilikan | PASS | Tes injeksi student_id diabaikan, actor lain ditolak; regresi IDOR CV/application/dokumen |
| I Guest | PASS | JSON 401 dan redirect normal; staff/CSRF 403 otomatis |
| J Admin | PASS | Browser antrian profil 3/5; detail profil 5 menampilkan siswa/status/waktu/versi; tes backend |
| K Backend/database gagal | PASS | DatabaseError audit menggulung balik seluruh perubahan; unexpected error terstruktur; Node error tanpa sukses |
| L Network/retry | PASS | Dua kasus browser nyata di bawah, inspeksi SQLite dan tes response-loss |

Fault injection dan fake fetch hanya digunakan dalam tes terisolasi, bukan aplikasi production. K diuji otomatis, bukan merusak DB lokal lewat browser. Aksi browser terutama memakai Space/Enter karena click alat otomasi kadang tidak berpengaruh. Double-click mouse fisik belum diuji; dua submit cepat diuji pada handler dan backend.

## Bukti database dan jaringan

**A, request belum tersimpan:** server lokal dihentikan ketika review profil 3 terbuka. Submit menghasilkan pesan ketidakpastian tanpa sukses. SQLite masih DRAFT, timestamp null, snapshot 0. Server dijalankan kembali, retry berhasil. Database: SUBMITTED, timestamp 2026-09-27T01:09:36.656475+00:00, submitted_version_id 7 (versi 1), snapshot 1, audit pengajuan 1. Refresh dan logout/login membaca nilai tersebut kembali.

**B, commit berhasil tetapi respons hilang:** proxy pengujian di 127.0.0.1:5192 meneruskan request ke backend nyata 5190, menerima respons 200 lengkap, kemudian memutus koneksi sebelum respons dikirim ke browser. Log membuktikan upstream 200 sengaja dibuang. UI menampilkan ketidakpastian, bukan sukses palsu. Sebelum retry: profil 5 milik user 6, SUBMITTED, timestamp 2026-09-27T02:20:28.925540+00:00, submitted_version_id 8, revision 1. Sesudah retry, semua nilai sama, snapshot 1, audit 1, owner versi profil 5. Browser menampilkan “CV sudah diajukan dan sedang diperiksa. Tidak perlu mengajukan ulang.” Dashboard membaca Diajukan, 09:20 WIB, versi 1. Admin menampilkan record yang sama. Proxy hanya alat uji dan tidak disertakan dalam aplikasi/distribusi.

## Regresi yang dijalankan dan batasan

- PASS — python manage.py test core --noinput: 55 tes (37 lama + 18 baru), 88.561 detik, OK.
- PASS — node core/tests_cv_submit.mjs: unchecked/loading/rapid submit/sukses server; HTTP 401/403/409/422/503; network error tanpa sukses palsu.
- PASS — makemigrations --check --dry-run: No changes detected. System check pada suite tidak menemukan issue.
- PASS — suite mencakup editing/autosave, authentication, dashboard siswa/admin, lowongan, applications, dokumen privat, XLSX export, status transitions, permissions dan snapshot.
- PASS — pembacaan console browser pada halaman admin akhir: tidak ada error tercatat.
- PARTIAL — UI error: jaringan/sukses/duplikat diuji browser; setiap status HTTP diuji Node dan backend, tidak semuanya dipicu manual di browser.
- NOT TESTED — concurrency PostgreSQL multi-worker, production/deployment/DNS/HTTPS dan gangguan internet nyata. Pengujian menggunakan SQLite lokal dan akun sintetis.
- NOT TESTED — outage seluruh database saat lookup profil sebelum handler submission. Frontend menangani respons non-JSON tanpa sukses palsu; tampilan server saat outage penuh belum diverifikasi.

Profil 2 pengguna tidak diubah. Tidak ada deploy production. Server pengembangan: http://127.0.0.1:5190/ menggunakan HTTP. Bukti gambar di keluaran keigo-preview: cv-submission-success.png, cv-submission-safe-retry.png, cv-submission-admin.png.
