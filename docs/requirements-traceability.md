# Traceability spesifikasi

PASS = tersedia dan diperiksa pada lingkungan lokal sesuai bukti. PARTIAL = batas eksplisit di bawah; bukan klaim produksi. Rincian tes aktual ada di test-report.md. Seluruh 105 bagian ditinjau. Tidak ada cutover tanpa persetujuan.

|Bagian|Requirement|Status|Implementasi / bukti / batas|
|---|---|---|---|
|1|PRIMARY OBJECTIVE|PARTIAL|Alur inti lokal terintegrasi; deployment nyata menunggu prasyarat infrastruktur. **Batas:** Go-live belum dilakukan.|
|2|SOURCE MATERIALS — READ BEFORE CODING|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|3|DO NOT START CODING IMMEDIATELY|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|4|REQUIREMENT TRACEABILITY|PASS|Traceability 105 bagian; final-report.md dan test-report.md.|
|5|PRODUCT ARCHITECTURE|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|6|USER ROLES|PASS|Role admin/siswa, auth server, CLI bootstrap; tes role, ownership, hashing, sesi.|
|7|PUBLIC WEBSITE VISUAL DIRECTION|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|8|PHOTO / DEMO POLICY|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|9|DEMO POLICY|PASS|Dataset sintetis lokal; tidak ada seed demo pada migrasi/distribusi.|
|10|PUBLIC WEBSITE|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|11|HERO|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|12|PROCESS TIMELINE|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|13|FACILITIES|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|14|REGISTRATION ARCHITECTURE|PASS|Role admin/siswa, auth server, CLI bootstrap; tes role, ownership, hashing, sesi.|
|15|AUTHENTICATION|PASS|Role admin/siswa, auth server, CLI bootstrap; tes role, ownership, hashing, sesi.|
|16|STUDENT DASHBOARD|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|17|DIGITAL CV|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|18|CV FORM UX|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|19|REPEATING CV DATA|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|20|CV INPUT QUALITY|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|21|CV STATUS|PASS|State CV dan versioning, snapshot immutable pengajuan; tes revisi, verifikasi, perubahan historis.|
|22|CV VERSIONING|PASS|State CV dan versioning, snapshot immutable pengajuan; tes revisi, verifikasi, perubahan historis.|
|23|APPLICATION SNAPSHOT|PASS|State CV dan versioning, snapshot immutable pengajuan; tes revisi, verifikasi, perubahan historis.|
|24|DOCUMENT MANAGEMENT|PASS|Private upload/download/replacement/review; tes ownership, ukuran/type, missing file.|
|25|PRIVATE FILE SECURITY|PASS|Private upload/download/replacement/review; tes ownership, ukuran/type, missing file.|
|26|JOB VACANCIES|PARTIAL|Job CRUD/status/archive, search/filter/detail, pengajuan melalui LPK; tes job dan browser. **Batas:** Lampiran lowongan terpisah belum dibuat; syarat khusus memakai teks persyaratan.|
|27|JOB STATUS|PASS|Job CRUD/status/archive, search/filter/detail, pengajuan melalui LPK; tes job dan browser.|
|28|STUDENT JOB EXPERIENCE|PASS|Job CRUD/status/archive, search/filter/detail, pengajuan melalui LPK; tes job dan browser.|
|29|JOB ACTION WORDING|PASS|Job CRUD/status/archive, search/filter/detail, pengajuan melalui LPK; tes job dan browser.|
|30|CV COMPLETENESS CHECK|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|31|ELIGIBILITY ASSISTANCE|PASS|Perbandingan syarat terstruktur sebagai bantuan; keputusan tetap admin.|
|32|APPLICATION ENTITY|PASS|Application unique student+job, snapshot dan append history; tes duplicate, closed, tahap, browser timeline.|
|33|APPLICATION WORKFLOW|PASS|Application unique student+job, snapshot dan append history; tes duplicate, closed, tahap, browser timeline.|
|34|APPLICATION HISTORY|PASS|Application unique student+job, snapshot dan append history; tes duplicate, closed, tahap, browser timeline.|
|35|ADMIN DASHBOARD|PASS|Custom admin UI, unified student page, notes visibility, candidate status/progress; tests dan browser.|
|36|ADMIN STUDENT DETAIL|PASS|Custom admin UI, unified student page, notes visibility, candidate status/progress; tests dan browser.|
|37|ADMIN NOTES|PASS|Custom admin UI, unified student page, notes visibility, candidate status/progress; tests dan browser.|
|38|JOB CANDIDATE MANAGEMENT|PASS|Custom admin UI, unified student page, notes visibility, candidate status/progress; tests dan browser.|
|39|BULK CANDIDATE OPERATIONS|PARTIAL|Bulk stage dengan konfirmasi/revision; CSV; tes perubahan dan stale rollback. Ekspor CV individual. **Batas:** Bulk stage dan CSV tersedia; bulk ZIP CV belum tersedia (opsional).|
|40|INTERVIEW / MENSET SU MANAGEMENT|PASS|Wawancara jadwal/lokasi/hasil, in-app notification dan read state; tes backend.|
|41|NOTIFICATIONS|PASS|Wawancara jadwal/lokasi/hasil, in-app notification dan read state; tes backend.|
|42|CV EXPORT — CRITICAL|PASS|XLSX template mapping; download browser/reopen/visual render, overflow dan formula safety.|
|43|EXCEL EXPORT ARCHITECTURE|PASS|XLSX template mapping; download browser/reopen/visual render, overflow dan formula safety.|
|44|SOURCE EXCEL MUST REMAIN UNTOUCHED|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|45|EXCEL EXPORT VERIFICATION|PASS|XLSX template mapping; download browser/reopen/visual render, overflow dan formula safety.|
|46|DATABASE DESIGN|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|47|DO NOT STORE EVERYTHING AS JSON|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|48|AUDIT LOG|PASS|Audit actor/action/entity/time/version tanpa isi file/password; tes mutasi dan ekspor.|
|49|DATA PRIVACY|PASS|Role admin/siswa, auth server, CLI bootstrap; tes role, ownership, hashing, sesi.|
|50|SECURITY REVIEW|PARTIAL|Server safeguards, CSRF/IDOR/XSS/throttle/uploads; suite keamanan aplikasi lokal. **Batas:** Belum audit independen/antivirus/infra produksi.|
|51|ADMIN ACCOUNT|PASS|Role admin/siswa, auth server, CLI bootstrap; tes role, ownership, hashing, sesi.|
|52|STUDENT ACCOUNT SECURITY|PARTIAL|Reset token 1 jam/sekali pakai dan SMTP env; locmem diuji, SMTP nyata belum. **Batas:** Credential SMTP belum tersedia.|
|53|VALIDATION|PASS|Role admin/siswa, auth server, CLI bootstrap; tes role, ownership, hashing, sesi.|
|54|CONCURRENCY / DUPLICATES|PARTIAL|Transaksi/revision/unique constraint; stale request, closed-after-confirm, duplicate tests. **Batas:** Belum load/concurrency test PostgreSQL paralel.|
|55|ERROR HANDLING|PASS|Validation/errors, missing/empty/failure states; tes backend dan browser.|
|56|RESPONSIVE DESIGN|PARTIAL|Lima viewport 320/375/430/768/1440 pada alur publik/siswa/admin; browser overflow dan screenshot. **Batas:** Ultrawide 2560px diperiksa pada homepage dan dashboard siswa, belum seluruh halaman.|
|57|ACCESSIBILITY|PARTIAL|Semantic forms, label/error/focus, dialog native/keyboard; reduced-motion CSS. **Batas:** Belum audit screen-reader independen.|
|58|PERFORMANCE|PARTIAL|Aset lokal terkompresi, lazyload, CSS/JS kecil, server pagination20. **Batas:** Belum load test dataset produksi.|
|59|DESIGN SYSTEM|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|60|ROUTING|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|61|SEO — PUBLIC WEBSITE|PASS|Title/canonical/OG/robots/sitemap publik; private noindex/no-store.|
|62|PRODUCTION DATABASE|PARTIAL|PostgreSQL wajib staging/production, SQLite dev; migrasi lengkap, check tanpa drift. **Batas:** Belum ada koneksi PostgreSQL nyata.|
|63|FILE STORAGE|PARTIAL|Private upload/download/replacement/review; tes ownership, ukuran/type, missing file. **Batas:** Persistent volume produksi belum tersedia.|
|64|ENVIRONMENT CONFIGURATION|PASS|PostgreSQL wajib staging/production, SQLite dev; migrasi lengkap, check tanpa drift.|
|65|DEVELOPMENT / STAGING / PRODUCTION|PARTIAL|PostgreSQL wajib staging/production, SQLite dev; migrasi lengkap, check tanpa drift. **Batas:** Staging belum dideploy.|
|66|DATABASE MIGRATIONS|PASS|PostgreSQL wajib staging/production, SQLite dev; migrasi lengkap, check tanpa drift.|
|67|BACKUP & RESTORE|PARTIAL|Backup SQLite+media dan restore ke folder baru diuji; panduan pg_dump/pg_restore. **Batas:** Jadwal otomatis dan restore PostgreSQL belum dijalankan.|
|68|LOGGING|PASS|Audit actor/action/entity/time/version tanpa isi file/password; tes mutasi dan ekspor.|
|69|CONTENT MANAGEMENT|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|70|JOB ARCHIVING|PASS|Job CRUD/status/archive, search/filter/detail, pengajuan melalui LPK; tes job dan browser.|
|71|SAFE DELETION|PASS|Tidak ada endpoint destructive delete siswa/job. Job diarsipkan; relasi historis PROTECT.|
|72|SEARCH|PASS|Pencarian siswa/job/kandidat, filter dan pagination server; routes diuji.|
|73|ADMIN OPERATIONAL UX|PASS|Custom admin UI, unified student page, notes visibility, candidate status/progress; tests dan browser.|
|74|STUDENT UX|PASS|Dashboard CV/progress/missing; CV form, validasi, repeated rows dan review; tes workflow dan browser.|
|75|APPLICATION TIMELINE|PASS|Application unique student+job, snapshot dan append history; tes duplicate, closed, tahap, browser timeline.|
|76|NOTIFICATION READ STATE|PASS|Wawancara jadwal/lokasi/hasil, in-app notification dan read state; tes backend.|
|77|PHOTO MANAGEMENT|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|78|PRODUCTION READINESS AUDIT|PARTIAL|Readiness audit demo/secrets/localhost/SMTP/hosting; tidak mengklaim go-live. **Batas:** TLS/SMTP/PostgreSQL/monitoring masih perlu diaktifkan.|
|79|TEST DATA|PASS|Dataset sintetis lokal; tidak ada seed demo pada migrasi/distribusi.|
|80|CRITICAL END-TO-END TEST — STUDENT|PASS|Student flow diuji melalui gabungan browser nyata dan Django integration tests; rincian test-report.|
|81|CRITICAL END-TO-END TEST — ADMIN|PASS|Admin flow diuji melalui browser dan Django integration tests; revisi/resubmit backend, export browser.|
|82|AUTHORIZATION TESTS|PASS|Role/ownership/CSRF/escalation/private download; 37 tes suite backend.|
|83|FAILURE TESTS|PASS|Invalid login/form/upload, missing file, expired/closed/duplicate, export failure, reset token tests.|
|84|RESPONSIVE TESTS|PASS|Lima viewport 320/375/430/768/1440 pada alur publik/siswa/admin; browser overflow dan screenshot.|
|85|REGRESSION TESTING|PASS|Run-fix-retest sampai suite lulus; ISO tanggal, dialog, autosave, filter dan header CSRF diperbaiki.|
|86|SELF-REPAIR LOOP|PASS|Run-fix-retest sampai suite lulus; ISO tanggal, dialog, autosave, filter dan header CSRF diperbaiki.|
|87|NO FAKE COMPLETION|PASS|Traceability 105 bagian; final-report.md dan test-report.md.|
|88|TECHNOLOGY CHOICE|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|89|KEEP OPERATIONS SIMPLE|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|90|EXISTING WEBSITE MIGRATION|PASS|Situs live dan DNS tidak diubah; cutover hanya setelah persetujuan pengelola.|
|91|SOURCE PRESERVATION|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|92|FACTUAL INTEGRITY|PASS|Audit sumber; source-audit.md, cv-field-map.md; sumber asli read-only.|
|93|LANGUAGE|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|94|VISUAL QUALITY|PASS|Konten publik/foto sumber, hero, program, fasilitas, kontak dan CTA; public route tests dan browser.|
|95|EMPTY STATES|PASS|Validation/errors, missing/empty/failure states; tes backend dan browser.|
|96|DATE / TIME|PASS|USE_TZ dan Asia/Jakarta; ISO HTML inputs; server date validation dan WIB timeline.|
|97|DATA EXPORT TRACE|PASS|XLSX template mapping; download browser/reopen/visual render, overflow dan formula safety.|
|98|FUTURE EXTENSIBILITY|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|99|DEFINITION OF DONE|PARTIAL|Alur inti lokal terintegrasi; deployment nyata menunggu prasyarat infrastruktur. **Batas:** Definisi produksi belum penuh tanpa staging/infra.|
|100|IMPLEMENTATION ORDER|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|101|PRIORITY ORDER|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|
|102|FINAL VERIFICATION|PARTIAL|Traceability 105 bagian; final-report.md dan test-report.md. **Batas:** Batas infrastruktur dan fitur opsional dicatat terbuka.|
|103|FINAL REPORT|PASS|Traceability 105 bagian; final-report.md dan test-report.md.|
|104|FINAL AUTONOMY INSTRUCTION|PASS|Traceability 105 bagian; final-report.md dan test-report.md.|
|105|MOST IMPORTANT MENTAL MODEL|PASS|Monolit Django; arsitektur dan normalized models/migrations terdokumentasi.|

Fitur opsional PDF CV dan bulk ZIP tidak dipaksakan untuk menggantikan prioritas XLSX individual yang telah diuji. Fitur lampiran lowongan dapat ditambahkan tanpa mengubah data CV. Seluruh PARTIAL infrastruktur memerlukan lingkungan/credential yang belum disediakan; hal tersebut tidak diakali dengan deployment palsu.