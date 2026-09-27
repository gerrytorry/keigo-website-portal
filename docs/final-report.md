# Laporan implementasi Keigo

## A–C. Arsitektur dan stack

Monolit Django 5.2 LTS dengan HTML server-rendered, CSS dan vanilla JavaScript; SQLite lokal, PostgreSQL staging/produksi. Django menyediakan auth, session, CSRF, ORM, migration dan validasi; Python/openpyxl memudahkan pemetaan workbook CV. Tidak ada backend palsu, database localStorage, atau kebutuhan microservices. Waitress tersedia untuk WSGI di belakang reverse proxy TLS.

## D–G. Struktur, skema, autentikasi, otorisasi

Struktur rinci pada README. Model operasional dinormalisasi: User, StudentProfile, Education, WorkExperience, FamilyMember, Certificate, JapanHistory, Document, CVVersion, Job, Application, ApplicationHistory, Interview, AdminNote, Notification, AuditEvent, LoginAttempt. JSON digunakan untuk snapshot historis dan metadata audit, bukan pengganti seluruh model CV. Constraint student+job mencegah pengajuan ganda. Foreign key PROTECT menjaga riwayat rekrutmen.

Password di-hash Django; session database, HttpOnly/SameSite, CSRF, throttle login, validasi password, alur reset token satu jam. Admin dibootstrap via CLI. Server memeriksa is_staff dan kepemilikan berdasarkan user sesi. Form tidak dapat menetapkan role administratif. Private download juga memeriksa hak akses; menyembunyikan menu bukan kontrol keamanan.

## H–I. Alur siswa dan admin

Siswa: daftar → CV bertahap → autosave/draft → unggah → tinjau/ajukan → revisi atau verifikasi → pilih lowongan → konfirmasi melalui LPK → timeline dan wawancara. Admin: dashboard → cari siswa → review CV/dokumen → catatan revisi/verifikasi → terbitkan lowongan → kandidat → perubahan tahap/bulk confirmation → wawancara → ekspor → audit. Catatan internal dipisahkan dari catatan yang terlihat siswa.

## J–L. CV, field map, ekspor

Sembilan bagian diturunkan dari workbook: identitas, fisik/paspor, bahasa/karakter, pendidikan, pengalaman kerja, keluarga, sertifikat, tambahan, riwayat Jepang. Mapping lengkap pada cv-field-map.md/field-map.json. Contoh: full_name→E5, birth_date→E6, phone→E11; education→14–16; work→19–23; certificates→25–26; family→28–34. Foto dan bukti bahasa/skill menggunakan area lampiran asli.

Database → snapshot canonical → mapping terisolasi exports.py → template tersanitasi → XLSX baru. Tidak mengedit workbook sumber. Sheet Data Lengkap/Lanjutan mempertahankan nilai panjang/overflow. Formula injection ditangani. Tiap ekspor tercatat audit dengan actor/versi. Export pengajuan memakai versi historis, bukan profil terbaru secara diam-diam.

## M–O. Dokumen, lowongan, audit

Private files memakai UUID dan volume di luar static; upload JPEG/PNG/PDF maksimum 5 MB, validasi server, status review dan replacement yang mempertahankan berkas lama. Download membutuhkan auth dan ownership/admin, no-store, attachment. Image/signature validation bukan antivirus.

Lowongan memiliki status draft/open/closed/selection/completed/archived, search/filter, requirement dan deadline. Selection service memeriksa ulang status/deadline/CV, transaksi dan unique constraint. Perbandingan persyaratan hanya bantuan; tidak mengambil keputusan perekrutan otomatis. Application menunjuk CVVersion dan memiliki append history. Audit mencatat mutasi penting dan ekspor tanpa menyalin isi dokumen/password.

## P–S. Bukti pengujian, batas, placeholder

37 tes backend lulus, browser workflow dan viewport matrix diperiksa, XLSX hasil download dibuka kembali, backup/restore SQLite diuji. Detail dan batas bukti ada pada test-report.md. Tidak ada klaim produksi/SMTP/PostgreSQL sudah berjalan. Seluruh foto publik autentik dari PDF; data pengujian adalah sintetis. Konflik statistik sumber tidak dipublikasikan. Tidak ada job/gaji/mitra/registrasi legal rekaan.

## T–Y. Akses dan operasional

Lokal HTTP port 5190. README menjelaskan start, migrasi dan bootstrap admin; LOCAL-ACCESS.md hanya untuk dataset uji pada mesin ini. operations.md menjelaskan environment, SMTP, staging, WSGI/TLS, pemulihan akun, PostgreSQL, backup/restore dan cutover. production-readiness.md menguraikan pekerjaan infrastruktur yang belum terverifikasi. ZIP distribusi tidak menyertakan runtime database, secrets, dokumen privat, atau akun demo. Website live dan DNS tetap tidak diubah.
