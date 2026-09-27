# Keigo Indonesia Bagus

Website institusi, portal siswa, dan operasional rekrutmen LPK. Versi lokal: **http://127.0.0.1:5190/**. Gunakan **HTTP**, bukan HTTPS, pada development server ini.

## Menjalankan lokal

Python 3.12+ diperlukan. Dari folder ini pada PowerShell:

```powershell
./start-local.ps1
```

Script membuat `.venv` bila belum tersedia, menginstal requirements, menjalankan migrasi, lalu server lokal. Instalasi pertama perlu internet. Port dapat diganti dengan `-Port 5191`. Ctrl+C menghentikan server. Data bertahan di `data.sqlite3` dan `private-media`.

Alternatif: buat dan aktifkan venv, lalu:

```text
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:5190
```

## Akun

Siswa mendaftar di `/daftar/`. Admin dibuat interaktif:

```text
python manage.py bootstrap_admin --email admin@domain-anda.com
```

Tidak ada pendaftaran admin publik atau password produksi bawaan. Semua akun masuk lewat `/masuk/`. Akses dataset uji yang sedang berjalan ada pada `LOCAL-ACCESS.md`, khusus mesin ini dan dikecualikan dari ZIP distribusi.

## Alur penggunaan

1. Siswa mengisi sembilan bagian CV, menyimpan draft, mengunggah dokumen, meninjau dan mengajukan CV.
2. Admin memeriksa CV/dokumen; revisi disertai alasan. CV terverifikasi dapat dipakai memilih lowongan.
3. Admin menerbitkan lowongan. Pengajuan siswa diproses melalui LPK, bukan langsung kepada perusahaan.
4. Setiap pengajuan menyimpan snapshot CV. Admin mengelola kandidat, tahap, wawancara, catatan, dan ekspor XLSX/CSV.
5. Notifikasi dalam aplikasi dapat ditandai dibaca. Catatan internal tidak ditampilkan kepada siswa.

Autosave bekerja pada profil dan baris riwayat yang valid. Baris baru membutuhkan kolom wajib lengkap. Penghapusan baris memakai Simpan draft. Periksa status “Tersimpan” sebelum menutup halaman. Ketika koneksi gagal, formulir tetap terbuka dan ada peringatan keluar.

## Pengujian

```text
python manage.py test core --noinput
python manage.py check
python manage.py makemigrations --check --dry-run
```

Lihat `docs/test-report.md`, `docs/final-report.md`, dan `docs/production-readiness.md`. Development server tidak digunakan sebagai server publik.

## Struktur

- `config/`: settings, URL, WSGI.
- `core/models.py`, `services.py`, `views.py`, `forms.py`: data, transaksi, otorisasi, validasi.
- `core/templates/core/`, `core/static/core/`: UI dan aset lokal.
- `core/exports.py`, `templates/cv/keigo.xlsx`: mapping dan template CV tersanitasi.
- `core/migrations/`, `core/tests.py`: skema dan pengujian.
- `scripts/backup_local.py`: backup/restore SQLite.
- `docs/`: audit sumber, field map, arsitektur, operasional, traceability.

PDF dan workbook asli tidak dibundel. Data personal dalam workbook contoh tidak diimpor. Foto/logo bersumber dari materi Keigo; tidak ada foto stok atau statistik alumni rekaan.
