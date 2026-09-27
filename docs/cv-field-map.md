# Pemetaan CV
Form CV dan Contoh Pengisian CV menjadi template utama. Wajib adalah kebijakan aplikasi untuk submit, bukan syarat yang ditandai workbook. Semua scalar dapat diedit siswa pada draft/revisi dan admin melalui form yang sama dengan audit. Semua diekspor XLSX; tanggal/umur dihitung pada tanggal versi.
|Label sumber (ID / JP)|Field internal|Tipe|Wajib|Validasi|Database|Siswa/Admin|Target XLSX|
|---|---|---|---|---|---|---|---|
|Nama / 氏名|full_name|text|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.full_name|Ya/Ya|Form CV!E5|
|Nama katakana / 氏名|name_kana|text|Tidak|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.name_kana|Ya/Ya|Form CV!E4|
|Jenis kelamin / 性別|gender|choice|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.gender|Ya/Ya|Form CV!M5|
|Tanggal lahir / 生年月日|birth_date|date|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.birth_date|Ya/Ya|Form CV!E6|
|Tempat lahir / 出身|birth_place|text|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.birth_place|Ya/Ya|Form CV!M7|
|Alamat / 現在住所|address|textarea|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.address|Ya/Ya|Form CV!E8|
|Agama / 宗教|religion|choice|Tidak|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.religion|Ya/Ya|Form CV!E10|
|Telepon / 電話番号|phone|tel|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.phone|Ya/Ya|Form CV!E11|
|Status pernikahan / 結婚|marital_status|choice|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.marital_status|Ya/Ya|Form CV!S11|
|Kondisi kesehatan / 健康状況|health|text|Tidak|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.health|Ya/Ya|Form CV!S9|
|Golongan darah / 血液型|blood_type|choice|Tidak|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.blood_type|Ya/Ya|Form CV!U9|
|Tinggi badan (cm) / 身長|height|number|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.height|Ya/Ya|Form CV!O29|
|Berat badan (kg) / 体重|weight|number|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.weight|Ya/Ya|Form CV!T29|
|Merokok / タバコ|smoking|boolean|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.smoking|Ya/Ya|Form CV!O31|
|Alkohol / お酒・ビール|alcohol|boolean|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.alcohol|Ya/Ya|Form CV!T31|
|Tato / 刺青|tattoo|boolean|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.tattoo|Ya/Ya|Form CV!O33|
|Memiliki paspor / パスポート|passport|boolean|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.passport|Ya/Ya|Form CV!T33|
|Lama belajar bahasa Jepang (bulan) / 日本語学習期間|study_months|number|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.study_months|Ya/Ya|Form CV!O27|
|Sertifikat kemampuan Jepang / 日本語能力検定|japanese_certificate|choice|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.japanese_certificate|Ya/Ya|Form CV!T27|
|Kelebihan / 長所|strengths|textarea|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.strengths|Ya/Ya|Form CV!G36|
|Kekurangan / 短所|weaknesses|textarea|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.weaknesses|Ya/Ya|Form CV!G37|
|Hobi / 趣味|hobbies|textarea|Ya|tipe, panjang, rentang; tanggal tidak di masa depan|StudentProfile.hobbies|Ya/Ya|Form CV!G38|

## Data turunan / berulang
|Sumber|Kolom internal / tipe|Database|Validasi|Target|
|---|---|---|---|---|
|年齢 Umur|age / derived|CVVersion reference date|selisih tanggal lahir|L6|
|作成日|created_at / date|CVVersion|server timestamp|M2|
|入学 / 卒業 / 学歴 / 専門|start_date,end_date,level,institution,major|Education|tahun-bulan berurutan, nama wajib; minimal 1 saat submit|B,C,D,F,G,H,Q rows 14–16|
|入社 / 退社 / 会社名 / 業種 / 具体的な作業内容 / 退社理由|start_date,end_date,company,industry,description,leaving_reason|WorkExperience|bulan berurutan; opsional jika belum bekerja|B,C,D,F,G,L,P,T rows 19–23|
|年 / 月 / 資格・免許|date,name,kind|Certificate|bulan dan nama; jenis LANGUAGE/SKILL/OTHER|B,C,D rows 25–26|
|家族氏名 / 関係 / 年齢 / 職業|name,relationship,age,occupation|FamilyMember|umur 0–120; minimal 1 saat submit|B,G,H,J rows 28–34|
|Foto|PHOTO document|Document|JPEG/PNG, 5MB|Q3:U8|
|日本語能力|LANGUAGE document|Document|PDF/PNG/JPEG|B41:J55, lampiran|
|特定技能の評価試験の証明書|SKILL document|Document|PDF/PNG/JPEG|K41:U55, lampiran|

Baris berulang tidak dibatasi kapasitas template; record selebihnya harus masuk sheet Lanjutan, tidak dibuang. Foto contoh/sertifikat contoh tidak disertakan.

## Tambahan sheet Vietnam (opsional)
Email (B12), telepon rumah (B14), penglihatan (O40), tangan dominan (T40), bahasa Inggris (N38), bahasa lain (T38), mata pelajaran favorit (B30), harapan gaji/bidang/durasi/lokasi (M32): StudentProfile kolom opsional. Ekspor sheet Tambahan. Riwayat perusahaan Jepang / kumiai / kontak / alamat (B46–52 tergantung sheet): JapanHistory repeatable, ekspor sheet Tambahan. 採用者側の記入: area admin, tidak menjadi input siswa. Nama kandidat Vietnam tidak diimpor.