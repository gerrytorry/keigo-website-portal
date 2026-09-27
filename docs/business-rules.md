# Aturan bisnis
1. Akun publik selalu STUDENT. ADMIN hanya melalui perintah bootstrap, tanpa registrasi publik.
2. Pengajuan siswa dikirim ke LPK; tidak ada pengiriman otomatis ke perusahaan Jepang.
3. Draft parsial boleh disimpan. Submit memerlukan bidang inti dan minimal satu pendidikan serta satu keluarga; tidak mengharuskan pengalaman/sertifikat jika belum punya. Penetapan wajib adalah kebijakan awal aplikasi, bukan klaim bahwa Excel memberi tanda wajib.
4. Pemilihan lowongan mensyaratkan CV lengkap dan VERIFIED; verifikasi adalah prasyarat sesuai alur utama spesifikasi. Syarat lowongan hanya bantuan perbandingan, bukan keputusan otomatis.
5. Perubahan CV terverifikasi menjadi REVERIFICATION_REQUIRED. CV SUBMITTED/UNDER_REVIEW terkunci sampai admin meminta revisi.
6. Snapshot CV dan dokumen pada pengajuan tidak berubah ketika profil diubah. Satu pengajuan per siswa per lowongan (unik database).
7. Setiap perubahan status mencatat aktor, waktu, status lama/baru dan catatan. Catatan internal tidak terlihat siswa. Revisi wajib menyertakan alasan.
8. Data historis tidak dihapus. Lowongan diarsipkan. Akun dapat dinonaktifkan melalui pengelolaan terkontrol.
9. Waktu disimpan UTC, ditampilkan Asia/Jakarta. Batas lowongan divalidasi kembali di server saat pengajuan.
10. Dokumen PDF/JPEG/PNG maksimal 5 MB, private, nama acak, akses berdasarkan owner/admin. Upload pengganti membuat revisi baru, bukan menimpa file lama.
