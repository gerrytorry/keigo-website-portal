from django.test import TestCase,Client,override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db import IntegrityError,transaction
from .models import *
from .services import *
from .exports import make_xlsx
from .forms import *
from io import BytesIO
from PIL import Image
import tempfile,openpyxl,hashlib

class WorkflowTests(TestCase):
 @classmethod
 def setUpTestData(cls):
  cls.admin=User.objects.create_user('admin@example.test','admin@example.test','Local-Admin-Only-973!',is_staff=True)
  cls.u=User.objects.create_user('siswa@example.test','siswa@example.test','Local-Student-Only-973!')
  cls.other=User.objects.create_user('other@example.test','other@example.test','Local-Student-Only-973!')
  cls.p=StudentProfile.objects.create(user=cls.u,full_name='Siswa Uji Keigo');cls.p2=StudentProfile.objects.create(user=cls.other,full_name='Siswa Kedua')
 def setUp(self):
  self.media=tempfile.TemporaryDirectory();self.override=override_settings(PRIVATE_MEDIA_ROOT=self.media.name,MEDIA_ROOT=self.media.name);self.override.enable()
  self.addCleanup(self.override.disable);self.addCleanup(self.media.cleanup)
 def fill(self):
  p=StudentProfile.objects.get(pk=self.p.pk)
  for k,v in {'gender':'M','birth_date':date(2001,5,10),'birth_place':'Brebes','address':'Alamat data sintetis','phone':'081234567890','marital_status':'SINGLE','height':170,'weight':60,'smoking':False,'alcohol':False,'tattoo':False,'passport':True,'study_months':6,'japanese_certificate':'JLPT N4','strengths':'Disiplin','weaknesses':'Masih belajar','hobbies':'Membaca'}.items():setattr(p,k,v)
  p.save();Education.objects.create(student=p,start_date=date(2016,7,1),end_date=date(2019,6,1),level='SMA',institution='SEKOLAH UJI',major='IPA');FamilyMember.objects.create(student=p,name='Keluarga Uji',relationship='Ayah',age=50,occupation='Wiraswasta');return p
 def job(self):return Job.objects.create(code='TEST-001',title='Lowongan Uji',company='Perusahaan Uji',program='MAGANG',industry='Manufaktur',prefecture='Osaka',status='OPEN')
 def verified(self):
  p=self.fill();submit_cv(p,self.u,p.revision);p.refresh_from_db();review_cv(p,self.admin,{'revision':p.revision,'status':'VERIFIED','note':'Sesuai'});p.refresh_from_db();return p
 def test_public_routes(self):
  for url in ['/','/tentang/','/program/','/fasilitas/','/alur/','/kontak/','/privasi/','/daftar/','/masuk/','/lowongan/','/robots.txt','/sitemap.xml']:
   with self.subTest(url=url):self.assertEqual(self.client.get(url).status_code,200)
 def test_registration_login_logout_real(self):
  response=self.client.post('/daftar/',{'full_name':'Siswa Baru','email':'new@example.test','password1':'Aman!BelajarKeigo-735','password2':'Aman!BelajarKeigo-735','consent':'on','is_staff':'true'})
  self.assertEqual(response.status_code,302);u=User.objects.get(username='new@example.test');self.assertFalse(u.is_staff);self.assertTrue(u.check_password('Aman!BelajarKeigo-735'));self.assertNotEqual(u.password,'Aman!BelajarKeigo-735')
  self.assertEqual(self.client.get('/keluar/').status_code,405);self.client.post('/keluar/');self.assertEqual(self.client.get('/student/').status_code,302)
  self.assertEqual(self.client.post('/masuk/',{'username':'new@example.test','password':'Aman!BelajarKeigo-735'}).status_code,302)
 def test_registration_duplicate(self):
  r=self.client.post('/daftar/',{'full_name':'Duplicate','email':self.u.email,'password1':'Aman!BelajarKeigo-735','password2':'Aman!BelajarKeigo-735','consent':'on'});self.assertContains(r,'Email ini sudah digunakan')
 def test_authorization(self):
  self.assertEqual(self.client.get('/admin/').status_code,302);self.assertEqual(self.client.get('/student/').status_code,302)
  self.client.force_login(self.u)
  for url in ['/admin/','/admin/siswa/','/admin/lowongan/baru/',f'/admin/siswa/{self.p2.pk}/',f'/admin/siswa/{self.p2.pk}/cv/identitas/','/admin/audit/']:
   self.assertEqual(self.client.get(url).status_code,403,url)
  self.assertEqual(self.client.post('/admin/lowongan/baru/',{'title':'Injected'}).status_code,403)
 def test_student_pages(self):
  self.client.force_login(self.u)
  for url in ['/student/','/student/dokumen/','/student/lowongan/','/student/lamaran/','/student/notifikasi/','/student/cv/tinjau/']+[f'/student/cv/{s}/' for s in ['identitas','fisik','bahasa','pendidikan','pekerjaan','keluarga','sertifikat','tambahan','jepang']]:
   with self.subTest(url=url):self.assertEqual(self.client.get(url).status_code,200)
 def test_admin_pages(self):
  p=self.verified();j=self.job();a=select_job(p,j,self.u);self.client.force_login(self.admin)
  for url in ['/admin/','/admin/siswa/','/admin/lowongan/','/admin/lowongan/baru/','/admin/lamaran/','/admin/audit/',f'/admin/siswa/{p.pk}/',f'/admin/lowongan/{j.pk}/',f'/admin/lowongan/{j.pk}/edit/',f'/admin/lamaran/{a.pk}/',f'/admin/lamaran/{a.pk}/wawancara/']:
   with self.subTest(url=url):self.assertEqual(self.client.get(url).status_code,200)
 def test_autosave_resume_concurrency_and_mass_assignment(self):
  self.client.force_login(self.u)
  payload={'revision':0,'full_name':'Nama Draft','phone':'08123456789','status':'VERIFIED','user':self.other.pk}
  r=self.client.post('/student/cv/identitas/',payload,HTTP_X_REQUESTED_WITH='autosave');self.assertEqual(r.status_code,200);self.assertEqual(r.json()['revision'],1)
  self.p.refresh_from_db();self.assertEqual(self.p.full_name,'Nama Draft');self.assertEqual(self.p.status,'DRAFT');self.assertEqual(self.p.user_id,self.u.pk)
  self.assertContains(self.client.get('/student/cv/identitas/'),'Nama Draft')
  self.assertEqual(self.client.post('/student/cv/identitas/',payload,HTTP_X_REQUESTED_WITH='autosave').status_code,409)
 def test_submit_revision_verify_snapshot(self):
  p=self.fill();self.client.force_login(self.u)
  r=self.client.post('/student/cv/tinjau/',{'revision':p.revision,'confirm':'yes'});self.assertEqual(r.status_code,302);p.refresh_from_db();self.assertEqual(p.status,'SUBMITTED')
  self.assertRaises(ValidationError,submit_cv,p,self.u,p.revision)
  self.client.force_login(self.admin);r=self.client.post(f'/admin/siswa/{p.pk}/',{'revision':p.revision,'status':'NEEDS_REVISION','note':'Periksa alamat'});self.assertEqual(r.status_code,302);p.refresh_from_db();self.assertEqual(p.status,'NEEDS_REVISION')
  self.client.force_login(self.u);r=self.client.post('/student/cv/tinjau/',{'revision':p.revision,'confirm':'yes'});self.assertEqual(r.status_code,302);p.refresh_from_db()
  self.client.force_login(self.admin);self.client.post(f'/admin/siswa/{p.pk}/',{'revision':p.revision,'status':'VERIFIED','note':'Sesuai'});p.refresh_from_db();self.assertEqual(p.status,'VERIFIED')
  j=self.job();a=select_job(p,j,self.u);old=a.cv_version.data['address'];p.address='Alamat diperbarui';p.save();self.assertEqual(Application.objects.get(pk=a.pk).cv_version.data['address'],old)
 def test_revision_note_required(self):self.assertFalse(CVReviewForm({'revision':0,'status':'NEEDS_REVISION','note':''}).is_valid())
 def test_incomplete_submit(self):self.assertRaises(ValidationError,submit_cv,self.p,self.u,0)
 def test_duplicate_and_closed_job(self):
  p=self.verified();j=self.job();select_job(p,j,self.u);self.assertRaises(ValidationError,select_job,p,j,self.u);j.status='CLOSED';j.save();self.assertRaises(ValidationError,select_job,p,j,self.u)
 def test_verified_changes_require_review(self):
  p=self.verified();form=ProfileForm({'revision':p.revision,'health':'Baik','height':170,'weight':61,'smoking':'False','alcohol':'False','tattoo':'False','passport':'True'},instance=p,section=PHYSICAL);self.assertTrue(form.is_valid(),form.errors);save_profile(p,form,self.u);p.refresh_from_db();self.assertEqual(p.status,'REVERIFICATION_REQUIRED')
 def test_application_status_history_and_idor(self):
  p=self.verified();a=select_job(p,self.job(),self.u);self.client.force_login(self.other);self.assertEqual(self.client.get(f'/student/lamaran/{a.pk}/').status_code,404);self.assertEqual(self.client.post(f'/admin/lamaran/{a.pk}/',{'status':'PASSED'}).status_code,403)
  change_stage(a,self.admin,{'revision':0,'status':'ADMIN_REVIEW','note':'Sedang diperiksa'});self.assertEqual(a.history.count(),2);a.refresh_from_db();self.assertEqual(a.status,'ADMIN_REVIEW');self.assertTrue(self.u.notifications.filter(text__contains='Diperiksa').exists())
 def test_private_documents(self):
  self.client.force_login(self.u);buf=BytesIO();Image.new('RGB',(20,20),'white').save(buf,format='PNG')
  r=self.client.post('/student/dokumen/',{'category':'PHOTO','label':'Uji','file':SimpleUploadedFile('test.png',buf.getvalue(),content_type='image/png')});self.assertEqual(r.status_code,302);d=Document.objects.get(student=self.p)
  download=self.client.get(f'/dokumen/{d.pk}/');self.assertEqual(download.status_code,200);download.close();self.client.force_login(self.other);self.assertEqual(self.client.get(f'/dokumen/{d.pk}/').status_code,404);self.client.logout();self.assertEqual(self.client.get(f'/dokumen/{d.pk}/').status_code,302);self.assertEqual(self.client.get('/private-unserved/'+d.file.name).status_code,404)
 def test_upload_rejects_bad_content_and_size(self):
  for f in [SimpleUploadedFile('bad.exe',b'MZ'),SimpleUploadedFile('bad.png',b'not an image'),SimpleUploadedFile('bad.pdf',b'<script>'),SimpleUploadedFile('big.pdf',b'%PDF-'+b'0'*(5*1024*1024))]:
   self.assertFalse(UploadForm({'category':'KTP'},{'file':f}).is_valid())
 def test_document_review_and_notification(self):
  self.client.force_login(self.u);self.client.post('/student/dokumen/',{'category':'KTP','file':SimpleUploadedFile('test.pdf',b'%PDF-1.4\n%%EOF')});d=Document.objects.get(student=self.p);self.client.force_login(self.admin)
  self.assertEqual(self.client.post(f'/admin/dokumen/{d.pk}/',{'revision':0,'status':'NEEDS_REVISION','note':'Foto kurang jelas'}).status_code,302);d.refresh_from_db();self.assertEqual(d.status,'NEEDS_REVISION');self.assertTrue(self.u.notifications.filter(text__contains='Dokumen').exists())
 def test_internal_notes_private(self):
  AdminNote.objects.create(student=self.p,actor=self.admin,text='INTERNAL-SECRET-TEST',visibility='INTERNAL');AdminNote.objects.create(student=self.p,actor=self.admin,text='Visible note',visibility='STUDENT');self.client.force_login(self.u);r=self.client.get('/student/');self.assertNotContains(r,'INTERNAL-SECRET-TEST');self.assertContains(r,'Visible note')
 def test_csrf(self):
  c=Client(enforce_csrf_checks=True);c.force_login(self.u);self.assertEqual(c.post('/student/cv/identitas/',{'revision':0}).status_code,403);self.assertEqual(c.post('/keluar/').status_code,403);self.assertEqual(c.get('/student/')['Referrer-Policy'],'same-origin')
 def test_invalid_login_and_throttle(self):
  for i in range(11):r=self.client.post('/masuk/',{'username':self.u.email,'password':'wrong'})
  self.assertContains(r,'Terlalu banyak percobaan');self.assertNotIn('_auth_user_id',self.client.session)
 def test_export_mapping_overflow_and_formula(self):
  p=self.fill();p.full_name='=HYPERLINK("evil")';p.save()
  for i in range(4):Education.objects.create(student=p,start_date=date(2000+i,1,1),level='SD',institution='Tambahan '+str(i))
  WorkExperience.objects.create(student=p,start_date=date(2020,1,1),company='PT UJI',industry='Manufaktur',description='Operator')
  Certificate.objects.create(student=p,date=date(2021,2,1),name='JLPT N4',kind='LANGUAGE')
  v=version(p,self.admin);before=hashlib.sha256((settings.BASE_DIR/'templates/cv/keigo.xlsx').read_bytes()).hexdigest();blob=make_xlsx(v);w=openpyxl.load_workbook(BytesIO(blob));s=w['Form CV']
  self.assertEqual(s['E5'].value,"'=HYPERLINK(\"evil\")");self.assertEqual(s['M5'].value,'男 Pria');self.assertEqual(s['G19'].value,'PT UJI');self.assertEqual(s['B28'].value,'Keluarga Uji');self.assertGreater(w['Lanjutan'].max_row,3);self.assertIn('Data Lengkap',w.sheetnames);self.assertNotIn('Contoh Pengisian CV',w.sheetnames);self.assertEqual(hashlib.sha256((settings.BASE_DIR/'templates/cv/keigo.xlsx').read_bytes()).hexdigest(),before)
 def test_export_endpoint_audit(self):
  p=self.verified();a=select_job(p,self.job(),self.u);self.client.force_login(self.u);self.assertEqual(self.client.post(f'/admin/siswa/{p.pk}/export/').status_code,403);self.client.force_login(self.admin);r=self.client.post(f'/admin/siswa/{p.pk}/export/',{'application':a.pk});self.assertEqual(r.status_code,200);b=b''.join(r.streaming_content);self.assertEqual(openpyxl.load_workbook(BytesIO(b))['Form CV']['E5'].value,p.full_name);self.assertTrue(AuditEvent.objects.filter(action='CV_EXPORTED').exists())
 def test_interview_and_read_notification(self):
  p=self.verified();a=select_job(p,self.job(),self.u);self.client.force_login(self.admin);r=self.client.post(f'/admin/lamaran/{a.pk}/wawancara/',{'revision':0,'scheduled_at':'2026-10-20T09:00','location':'Ruang Keigo','notes':'Datang 15 menit lebih awal','result':'PENDING'});self.assertEqual(r.status_code,302);self.client.force_login(self.u);self.assertContains(self.client.get(f'/student/lamaran/{a.pk}/'),'Ruang Keigo');n=self.u.notifications.first();self.client.post('/student/notifikasi/',{'id':n.pk});n.refresh_from_db();self.assertIsNotNone(n.read_at)
 def test_session_revoked(self):
  self.client.force_login(self.u);s=self.client.session;s.flush();self.assertEqual(self.client.get('/student/').status_code,302)
 def test_xss_escaped(self):
  self.p.full_name='<script>alert(1)</script>';self.p.save();self.client.force_login(self.u);r=self.client.get('/student/');self.assertContains(r,'&lt;script&gt;');self.assertNotContains(r,'<script>alert(1)</script>')
 def test_repeatable_ownership_create_delete(self):
  self.client.force_login(self.u)
  foreign=Education.objects.create(student=self.p2,start_date=date(2010,1,1),level='SD',institution='Other')
  payload={'revision':0,'rows-TOTAL_FORMS':1,'rows-INITIAL_FORMS':1,'rows-MIN_NUM_FORMS':0,'rows-MAX_NUM_FORMS':100,'rows-0-id':foreign.pk,'rows-0-start_date':'2016-07-01','rows-0-level':'SMA','rows-0-institution':'Tampered'}
  self.client.post('/student/cv/pendidikan/',payload);foreign.refresh_from_db();self.assertEqual(foreign.institution,'Other')
  self.p.refresh_from_db();payload.update({'revision':self.p.revision,'rows-INITIAL_FORMS':0,'rows-0-id':''})
  self.assertEqual(self.client.post('/student/cv/pendidikan/',payload).status_code,302)
  row=self.p.educations.get();self.assertEqual(row.institution,'Tampered')
  self.p.refresh_from_db();payload.update({'revision':self.p.revision,'rows-INITIAL_FORMS':1,'rows-0-id':row.pk,'rows-0-DELETE':'on'})
  self.assertEqual(self.client.post('/student/cv/pendidikan/',payload).status_code,302);self.assertFalse(self.p.educations.exists())
 def test_document_replacement_retains_original(self):
  self.client.force_login(self.u)
  self.client.post('/student/dokumen/',{'category':'KTP','file':SimpleUploadedFile('first.pdf',b'%PDF-1.4\n%%EOF')})
  old=Document.objects.get(student=self.p)
  self.client.post('/student/dokumen/',{'category':'KTP','replaces':old.pk,'file':SimpleUploadedFile('second.pdf',b'%PDF-1.5\n%%EOF')})
  old.refresh_from_db();self.assertFalse(old.is_current);self.assertEqual(Document.objects.get(student=self.p,is_current=True).replaces_id,old.pk)
 def test_expired_job_and_stale_stage(self):
  p=self.verified();j=self.job();j.deadline=date(2000,1,1);j.save();self.assertRaises(ValidationError,select_job,p,j,self.u)
  j.deadline=None;j.save();a=select_job(p,j,self.u)
  change_stage(a,self.admin,{'revision':0,'status':'ADMIN_REVIEW'});self.assertRaises(ValidationError,change_stage,a,self.admin,{'revision':0,'status':'PASSED'})
 def test_job_crud_and_conflict(self):
  self.client.force_login(self.admin)
  payload={'revision':0,'code':'NEW-TEST','title':'Posisi Sintetis','company':'Uji','program':'MAGANG','industry':'Uji','prefecture':'Osaka','quota':2,'status':'OPEN'}
  self.assertEqual(self.client.post('/admin/lowongan/baru/',payload).status_code,302)
  j=Job.objects.get(code='NEW-TEST');payload.update({'revision':j.revision,'status':'ARCHIVED'})
  self.assertEqual(self.client.post(f'/admin/lowongan/{j.pk}/edit/',payload).status_code,302)
  payload['title']='Stale change';self.client.post(f'/admin/lowongan/{j.pk}/edit/',payload);j.refresh_from_db();self.assertEqual(j.title,'Posisi Sintetis')
 def test_export_failure_preserves_data(self):
  from unittest.mock import patch
  p=self.fill();self.client.force_login(self.admin)
  with self.assertLogs('core.views',level='ERROR'), patch('core.exports.make_xlsx',side_effect=ValueError('simulated')):
   self.assertEqual(self.client.post(f'/admin/siswa/{p.pk}/export/').status_code,302)
  p.refresh_from_db();self.assertEqual(p.full_name,'Siswa Uji Keigo')

 def test_repeatable_autosave_returns_persistent_ids(self):
  self.client.force_login(self.u)
  data={'revision':0,'rows-TOTAL_FORMS':1,'rows-INITIAL_FORMS':0,'rows-MIN_NUM_FORMS':0,'rows-MAX_NUM_FORMS':100,'rows-0-start_date':'2016-07-01','rows-0-level':'SMA','rows-0-institution':'Autosave Uji'}
  r=self.client.post('/student/cv/pendidikan/',data,HTTP_X_REQUESTED_WITH='autosave');self.assertEqual(r.status_code,200)
  data.update({'revision':r.json()['revision'],'rows-INITIAL_FORMS':1,'rows-0-id':r.json()['row_ids'][0],'rows-0-institution':'Updated'})
  self.assertEqual(self.client.post('/student/cv/pendidikan/',data,HTTP_X_REQUESTED_WITH='autosave').status_code,200)
  self.assertEqual(self.p.educations.count(),1);self.assertEqual(self.p.educations.get().institution,'Updated')
 def test_missing_document_file_is_safe(self):
  d=Document.objects.create(student=self.p,category='KTP',file='documents/missing.pdf',original_name='missing.pdf',size=1,digest='x')
  self.client.force_login(self.u);self.assertEqual(self.client.get(f'/dokumen/{d.pk}/').status_code,404)

 @override_settings(EMAIL_HOST='test.invalid',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
 def test_password_reset_token_one_time_and_no_enumeration(self):
  from django.core import mail
  import re
  r=self.client.post('/pulihkan/',{'email':self.u.email});self.assertContains(r,'Periksa email Anda.');self.assertEqual(len(mail.outbox),1)
  url=re.search(r'https?://testserver(/pulihkan/[^\s]+)',mail.outbox[0].body).group(1)
  r=self.client.get(url);self.assertEqual(r.status_code,302);secure_url=r.url
  r=self.client.post(secure_url,{'new_password1':'Replacement-Uji-892!','new_password2':'Replacement-Uji-892!'})
  self.assertEqual(r.status_code,302);self.u.refresh_from_db();self.assertTrue(self.u.check_password('Replacement-Uji-892!'))
  r=self.client.get(url,follow=True);self.assertContains(r,'Tautan tidak valid')
  r=self.client.post('/pulihkan/',{'email':'missing@example.test'});self.assertContains(r,'Periksa email Anda.');self.assertEqual(len(mail.outbox),1)
 @override_settings(EMAIL_HOST='')
 def test_reset_without_smtp_is_honest(self):
  self.assertContains(self.client.post('/pulihkan/',{'email':self.u.email}),'Pemulihan email belum diaktifkan')

 def test_bulk_stage_confirm_and_stale_rollback(self):
  p=self.verified();j=self.job();a=select_job(p,j,self.u);self.client.force_login(self.admin)
  endpoint=f'/admin/lowongan/{j.pk}/bulk/'
  self.assertEqual(self.client.get(endpoint).status_code,405)
  self.assertEqual(self.client.post(endpoint,{'ids':[a.pk]}).status_code,200)
  a.refresh_from_db();self.assertEqual(a.status,'SUBMITTED_TO_LPK')
  data={'ids':[a.pk],'confirm':'yes','status':'ADMIN_REVIEW',f'revision_{a.pk}':0}
  self.assertEqual(self.client.post(endpoint,data).status_code,302)
  data['status']='CANDIDATE';self.client.post(endpoint,data);a.refresh_from_db();self.assertEqual(a.status,'ADMIN_REVIEW')
  self.assertEqual(self.client.post(endpoint,{'ids':['not-an-id']}).status_code,302)
 def test_job_closes_after_confirmation_page(self):
  p=self.verified();j=self.job();self.client.force_login(self.u)
  url=f'/student/lowongan/{j.pk}/pilih/'
  self.assertEqual(self.client.get(url).status_code,200)
  j.status='CLOSED';j.save();self.client.post(url,{'confirm':'yes'});self.assertFalse(Application.objects.exists())
 def test_public_filter_markup_and_template_sanitized(self):
  self.assertContains(self.client.get('/lowongan/'),'<option value="MAGANG"')
  w=openpyxl.load_workbook(settings.BASE_DIR/'templates/cv/keigo.xlsx')
  self.assertTrue(all(not c.hyperlink and not c.comment for sh in w for row in sh for c in row))

from datetime import date

class DateWidgetTests(TestCase):
 def test_iso_dates_survive_localized_render(self):
  p=StudentProfile(full_name='Uji',birth_date=date(2000,5,15))
  self.assertIn('value="2000-05-15"',str(ProfileForm(instance=p)['birth_date']))
  e=Education(start_date=date(2016,7,1),end_date=date(2019,6,1))
  self.assertIn('value="2016-07-01"',str(EducationForm(instance=e)['start_date']))
  j=Job(deadline=date(2027,1,2))
  self.assertIn('value="2027-01-02"',str(JobForm(instance=j)['deadline']))
  from datetime import datetime
  i=Interview(scheduled_at=datetime(2027,1,2,9,30))
  self.assertIn('value="2027-01-02T09:30"',str(InterviewForm(instance=i)['scheduled_at']))
