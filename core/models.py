from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils import timezone
import uuid

CV_STATES=[(v,l) for v,l in [('DRAFT','Draft'),('SUBMITTED','Diajukan'),('UNDER_REVIEW','Dalam pemeriksaan'),('NEEDS_REVISION','Perlu revisi'),('VERIFIED','Terverifikasi'),('REVERIFICATION_REQUIRED','Perlu verifikasi ulang')]]
APP_STATES=[(v,l) for v,l in [('SUBMITTED_TO_LPK','Diterima LPK'),('ADMIN_REVIEW','Diperiksa admin'),('CANDIDATE','Kandidat'),('CV_PREPARED','CV disiapkan'),('EXTERNALLY_APPLIED','Diajukan oleh LPK'),('DOCUMENT_SELECTION','Seleksi dokumen'),('INTERVIEW','Wawancara'),('RESERVE','Cadangan'),('PASSED','Lulus'),('FAILED','Belum lulus'),('WITHDRAWN','Ditarik'),('MEDICAL','Pemeriksaan kesehatan'),('DOCUMENT_PROCESS','Pengurusan dokumen'),('DEPARTURE_PROCESS','Persiapan keberangkatan'),('DEPARTED','Berangkat')]]
DOC_STATES=[(v,l) for v,l in [('UPLOADED','Diunggah'),('UNDER_REVIEW','Diperiksa'),('VERIFIED','Terverifikasi'),('NEEDS_REVISION','Perlu revisi')]]
DOC_CATEGORIES=[('KTP','KTP'),('KK','Kartu Keluarga'),('BIRTH','Akta kelahiran'),('EDUCATION','Ijazah'),('HEALTH','Dokumen kesehatan'),('CONSENT','Surat izin keluarga'),('PHOTO','Pas foto'),('PASSPORT','Paspor (jika ada)'),('LANGUAGE','Sertifikat bahasa Jepang'),('SKILL','Sertifikat SSW'),('OTHER','Dokumen lain')]
class Timestamped(models.Model):
 created_at=models.DateTimeField(default=timezone.now,editable=False)
 updated_at=models.DateTimeField(auto_now=True)
 class Meta: abstract=True
class StudentProfile(Timestamped):
 user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='profile')
 full_name=models.CharField('Nama lengkap',max_length=150,blank=True)
 name_kana=models.CharField('Nama katakana',max_length=150,blank=True)
 gender=models.CharField('Jenis kelamin',max_length=10,choices=[('M','Pria'),('F','Wanita')],blank=True)
 birth_date=models.DateField('Tanggal lahir',null=True,blank=True)
 birth_place=models.CharField('Tempat lahir',max_length=150,blank=True)
 address=models.TextField('Alamat lengkap',max_length=1000,blank=True)
 religion=models.CharField('Agama',max_length=40,choices=[(s,s) for s in ['Islam','Kristen','Katolik','Hindu','Buddha','Konghucu','Lainnya','Tidak menyatakan']],blank=True)
 phone=models.CharField('Nomor telepon',max_length=25,blank=True)
 marital_status=models.CharField('Status pernikahan',max_length=20,choices=[('SINGLE','Belum menikah'),('MARRIED','Menikah'),('DIVORCED','Cerai')],blank=True)
 health=models.CharField('Kondisi kesehatan',max_length=300,blank=True)
 blood_type=models.CharField('Golongan darah',max_length=10,choices=[(s,s) for s in ['A','B','AB','O','Belum tahu']],blank=True)
 height=models.PositiveSmallIntegerField('Tinggi badan (cm)',null=True,blank=True,validators=[MinValueValidator(50),MaxValueValidator(250)])
 weight=models.PositiveSmallIntegerField('Berat badan (kg)',null=True,blank=True,validators=[MinValueValidator(20),MaxValueValidator(300)])
 smoking=models.BooleanField('Merokok',null=True,blank=True)
 alcohol=models.BooleanField('Mengonsumsi alkohol',null=True,blank=True)
 tattoo=models.BooleanField('Memiliki tato',null=True,blank=True)
 passport=models.BooleanField('Memiliki paspor',null=True,blank=True)
 study_months=models.PositiveSmallIntegerField('Lama belajar bahasa Jepang (bulan)',null=True,blank=True,validators=[MaxValueValidator(600)])
 japanese_certificate=models.CharField('Sertifikat bahasa Jepang',max_length=25,choices=[(s,s) for s in ['Tidak ada','JFT BASIC A2','JLPT N5','JLPT N4','JLPT N3','JLPT N2','JLPT N1','Lainnya']],blank=True)
 strengths=models.TextField('Kelebihan',max_length=1000,blank=True)
 weaknesses=models.TextField('Kekurangan',max_length=1000,blank=True)
 hobbies=models.TextField('Hobi',max_length=1000,blank=True)
 home_phone=models.CharField('Telepon rumah (opsional)',max_length=25,blank=True)
 eyesight=models.CharField('Penglihatan (opsional)',max_length=100,blank=True)
 dominant_hand=models.CharField('Tangan dominan',max_length=10,choices=[('RIGHT','Kanan'),('LEFT','Kiri'),('BOTH','Keduanya')],blank=True)
 english_level=models.CharField('Kemampuan bahasa Inggris',max_length=100,blank=True)
 other_languages=models.CharField('Bahasa lain',max_length=150,blank=True)
 favorite_subject=models.CharField('Pelajaran favorit',max_length=150,blank=True)
 aspirations=models.TextField('Harapan gaji, bidang, durasi, lokasi (opsional)',max_length=1000,blank=True)
 status=models.CharField(max_length=30,choices=CV_STATES,default='DRAFT',db_index=True)
 revision=models.PositiveIntegerField(default=0)
 review_note=models.TextField(blank=True,max_length=2000)
 submitted_at=models.DateTimeField(null=True,blank=True,editable=False)
 submitted_version=models.ForeignKey('CVVersion',null=True,blank=True,on_delete=models.PROTECT,related_name='+',editable=False)
 def __str__(self): return self.full_name or self.user.username
class Education(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='educations')
 start_date=models.DateField('Mulai sekolah');end_date=models.DateField('Lulus / selesai',null=True,blank=True)
 level=models.CharField('Jenjang',max_length=25,choices=[(s,s) for s in ['SD','SMP','SMA','SMK','Diploma','Sarjana','Lainnya']])
 institution=models.CharField('Nama sekolah',max_length=200);major=models.CharField('Jurusan',max_length=150,blank=True)
 class Meta: ordering=['start_date','id']
class WorkExperience(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='work_experiences')
 start_date=models.DateField('Mulai kerja');end_date=models.DateField('Selesai kerja',null=True,blank=True)
 company=models.CharField('Nama perusahaan',max_length=200);industry=models.CharField('Bidang industri',max_length=150,blank=True)
 description=models.TextField('Deskripsi pekerjaan',max_length=1000,blank=True);leaving_reason=models.CharField('Alasan berhenti',max_length=300,blank=True)
 class Meta: ordering=['start_date','id']
class FamilyMember(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='family_members')
 name=models.CharField('Nama keluarga',max_length=150);relationship=models.CharField('Hubungan',max_length=80)
 age=models.PositiveSmallIntegerField('Umur',validators=[MaxValueValidator(120)]);occupation=models.CharField('Pekerjaan',max_length=150,blank=True)
 class Meta: ordering=['id']
class Certificate(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='certificates')
 date=models.DateField('Tanggal diterbitkan');name=models.CharField('Nama sertifikat / ijazah',max_length=250)
 kind=models.CharField('Jenis',max_length=15,choices=[('LANGUAGE','Bahasa'),('SKILL','SSW / keterampilan'),('OTHER','Lainnya')])
 class Meta: ordering=['date','id']
class JapanHistory(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='japan_history')
 company=models.CharField('Perusahaan Jepang',max_length=200);organization=models.CharField('Kumiai / organisasi',max_length=200,blank=True)
 contact=models.CharField('Kontak perusahaan / penanggung jawab',max_length=150,blank=True);address=models.TextField('Alamat perusahaan',max_length=500,blank=True)
 class Meta: ordering=['id']
def private_path(instance,filename): return f'documents/{uuid.uuid4().hex}{__import__("pathlib").Path(filename).suffix.lower()}'
class Document(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.PROTECT,related_name='documents')
 category=models.CharField(max_length=20,choices=DOC_CATEGORIES)
 label=models.CharField('Keterangan (misalnya Ijazah SD)',max_length=150,blank=True)
 file=models.FileField(upload_to=private_path)
 original_name=models.CharField(max_length=250);size=models.PositiveIntegerField();digest=models.CharField(max_length=64)
 status=models.CharField(max_length=20,choices=DOC_STATES,default='UPLOADED')
 is_current=models.BooleanField(default=True)
 replaces=models.ForeignKey('self',null=True,blank=True,on_delete=models.PROTECT)
 review_note=models.TextField(blank=True,max_length=2000)
 revision=models.PositiveIntegerField(default=0)
class CVVersion(models.Model):
 student=models.ForeignKey(StudentProfile,on_delete=models.PROTECT,related_name='versions')
 number=models.PositiveIntegerField();data=models.JSONField();created_at=models.DateTimeField(default=timezone.now)
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
 class Meta: constraints=[models.UniqueConstraint(fields=['student','number'],name='unique_cv_version')];ordering=['-number']
class Job(Timestamped):
 code=models.CharField('Kode lowongan',max_length=40,unique=True)
 title=models.CharField('Posisi',max_length=200);company=models.CharField('Perusahaan',max_length=200)
 program=models.CharField('Program',max_length=30,choices=[('MAGANG','Magang'),('SSW','Tokutei Ginou')])
 industry=models.CharField('Bidang',max_length=100);prefecture=models.CharField('Prefektur',max_length=100)
 location=models.CharField('Lokasi',max_length=200,blank=True)
 salary=models.CharField('Informasi gaji (sertakan mata uang)',max_length=200,blank=True)
 schedule=models.CharField('Jadwal kerja',max_length=200,blank=True);overtime=models.CharField('Lembur',max_length=200,blank=True)
 quota=models.PositiveSmallIntegerField('Kuota',default=1,validators=[MinValueValidator(1)])
 requirements=models.TextField('Persyaratan',max_length=5000,blank=True)
 min_age=models.PositiveSmallIntegerField('Usia minimum',null=True,blank=True,validators=[MaxValueValidator(100)])
 max_age=models.PositiveSmallIntegerField('Usia maksimum',null=True,blank=True,validators=[MaxValueValidator(100)])
 min_height=models.PositiveSmallIntegerField('Tinggi minimum (cm)',null=True,blank=True,validators=[MaxValueValidator(250)])
 japanese_level=models.CharField('Sertifikat bahasa yang diperlukan',max_length=80,blank=True)
 skill=models.CharField('Sertifikat keterampilan',max_length=150,blank=True)
 education=models.CharField('Pendidikan',max_length=100,blank=True);experience=models.CharField('Pengalaman',max_length=300,blank=True)
 interview_at=models.DateTimeField('Jadwal wawancara',null=True,blank=True);interview_method=models.CharField('Metode wawancara',max_length=200,blank=True)
 deadline=models.DateField('Batas pengajuan',null=True,blank=True)
 notes=models.TextField('Catatan publik',max_length=3000,blank=True)
 status=models.CharField('Status',max_length=20,choices=[('DRAFT','Draft'),('OPEN','Terbuka'),('CLOSED','Ditutup'),('SELECTION','Seleksi'),('COMPLETED','Selesai'),('ARCHIVED','Diarsipkan')],default='DRAFT',db_index=True)
 revision=models.PositiveIntegerField(default=0)
 class Meta: ordering=['-created_at']
 def __str__(self): return f'{self.code} · {self.title}'
class Application(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.PROTECT,related_name='applications')
 job=models.ForeignKey(Job,on_delete=models.PROTECT,related_name='applications')
 cv_version=models.ForeignKey(CVVersion,on_delete=models.PROTECT)
 status=models.CharField(max_length=30,choices=APP_STATES,default='SUBMITTED_TO_LPK',db_index=True)
 revision=models.PositiveIntegerField(default=0)
 class Meta: constraints=[models.UniqueConstraint(fields=['student','job'],name='unique_student_job')];ordering=['-created_at']
class ApplicationHistory(models.Model):
 application=models.ForeignKey(Application,on_delete=models.PROTECT,related_name='history')
 previous_status=models.CharField(max_length=30,blank=True);status=models.CharField(max_length=30,choices=APP_STATES)
 note=models.TextField(max_length=2000,blank=True);actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
 created_at=models.DateTimeField(default=timezone.now)
 class Meta: ordering=['created_at','id']
class Interview(Timestamped):
 application=models.ForeignKey(Application,on_delete=models.PROTECT,related_name='interviews')
 scheduled_at=models.DateTimeField('Tanggal dan waktu');location=models.CharField('Lokasi / tautan online',max_length=400)
 notes=models.TextField('Catatan untuk siswa',max_length=2000,blank=True)
 result=models.CharField('Hasil',max_length=50,choices=[('PENDING','Belum ada hasil'),('PASSED','Lulus'),('FAILED','Belum lulus'),('RESERVE','Cadangan'),('CANCELLED','Dibatalkan')],default='PENDING')
 revision=models.PositiveIntegerField(default=0)
class AdminNote(Timestamped):
 student=models.ForeignKey(StudentProfile,on_delete=models.PROTECT,related_name='notes')
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
 text=models.TextField('Catatan',max_length=3000)
 visibility=models.CharField('Visibilitas',max_length=20,choices=[('INTERNAL','Internal admin'),('STUDENT','Terlihat siswa')],default='INTERNAL')
class Notification(models.Model):
 recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications')
 text=models.CharField(max_length=400);url=models.CharField(max_length=250);created_at=models.DateTimeField(default=timezone.now);read_at=models.DateTimeField(null=True,blank=True)
 class Meta: ordering=['-created_at']
class AuditEvent(models.Model):
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True)
 action=models.CharField(max_length=100);entity=models.CharField(max_length=50);entity_id=models.CharField(max_length=80)
 metadata=models.JSONField(default=dict);created_at=models.DateTimeField(default=timezone.now)
 class Meta: ordering=['-created_at']
class LoginAttempt(models.Model):
 key=models.CharField(max_length=64,unique=True);count=models.PositiveIntegerField(default=0);started_at=models.DateTimeField(default=timezone.now)
