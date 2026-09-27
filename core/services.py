from django.db import transaction
from django.db.models import F
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import *
from .forms import PERSONAL,PHYSICAL,LANGUAGE,EXTRA
import json,hashlib
from django.core.serializers.json import DjangoJSONEncoder
REQUIRED=['full_name','gender','birth_date','birth_place','address','phone','marital_status','height','weight','smoking','alcohol','tattoo','passport','study_months','japanese_certificate','strengths','weaknesses','hobbies']
def audit(actor,action,obj,metadata=None):return AuditEvent.objects.create(actor=actor,action=action,entity=type(obj).__name__,entity_id=str(obj.pk),metadata=metadata or {})
def notify(user,text,url):Notification.objects.create(recipient=user,text=text,url=url)
def notify_admin(text,url):
 for u in User.objects.filter(is_staff=True,is_active=True):notify(u,text,url)
def completeness(p):
 missing=[str(p._meta.get_field(f).verbose_name) for f in REQUIRED if getattr(p,f) is None or getattr(p,f)=='']
 if not p.educations.exists():missing.append('Riwayat pendidikan')
 if not p.family_members.exists():missing.append('Data keluarga')
 return {'missing':missing,'percent':round((len(REQUIRED)+2-len(missing))*100/(len(REQUIRED)+2))}
def snapshot(p):
 data={f:getattr(p,f) for f in PERSONAL+PHYSICAL+LANGUAGE+EXTRA};data['email']=p.user.email
 for rel in ['educations','work_experiences','family_members','certificates','japan_history']:
  data[rel]=list(getattr(p,rel).values())
 data['documents']=list(p.documents.filter(is_current=True).values('id','category','label','digest','status'))
 return json.loads(json.dumps(data,cls=DjangoJSONEncoder))
def version(p,actor):
 return CVVersion.objects.create(student=p,number=(p.versions.first().number+1 if p.versions.exists() else 1),data=snapshot(p),actor=actor)
def editable(p):
 if p.status in ['SUBMITTED','UNDER_REVIEW']:raise ValidationError('CV sedang diperiksa. Hubungi admin untuk membuka revisi.')
def claim_revision(p,revision):
 if not StudentProfile.objects.filter(pk=p.pk,revision=revision).update(revision=F('revision')+1):raise ValidationError('Data berubah di sesi lain. Muat ulang halaman sebelum menyimpan kembali.')
 p.revision=revision+1
@transaction.atomic
def save_profile(p,form,actor):
 p=StudentProfile.objects.select_for_update().get(pk=p.pk);editable(p);claim_revision(p,form.cleaned_data['revision'])
 for f in form._meta.fields:
  if f in form.cleaned_data:setattr(p,f,form.cleaned_data[f])
 if p.status=='VERIFIED':p.status='REVERIFICATION_REQUIRED'
 p.save();audit(actor,'CV_UPDATED',p,{'revision':p.revision});return p
@transaction.atomic
def submit_cv(p,actor,revision):
 p=StudentProfile.objects.select_for_update().get(pk=p.pk)
 if actor.pk!=p.user_id or actor.is_staff:
  from django.core.exceptions import PermissionDenied
  raise PermissionDenied('Pengajuan hanya dapat dilakukan pemilik CV.')
 if p.status in ['SUBMITTED','UNDER_REVIEW']:
  raise ValidationError('CV sudah diajukan dan sedang diperiksa. Tidak perlu mengajukan ulang.',code='already_submitted')
 missing=completeness(p)['missing']
 if missing:raise ValidationError('Lengkapi: '+', '.join(missing),code='incomplete')
 if p.revision!=revision:raise ValidationError('Data CV berubah di sesi lain. Muat ulang tinjauan sebelum mengajukan.',code='conflict')
 claim_revision(p,revision)
 p.status='SUBMITTED';p.review_note='';p.submitted_at=timezone.now()
 v=version(p,actor);p.submitted_version=v;p.save()
 audit(actor,'CV_SUBMITTED',p,{'version':v.number,'version_id':v.pk})
 notify_admin('CV baru menunggu pemeriksaan.',f'/admin/siswa/{p.pk}/')
 return v
@transaction.atomic
def review_cv(p,actor,data):
 p=StudentProfile.objects.select_for_update().get(pk=p.pk)
 if p.status not in ['SUBMITTED','UNDER_REVIEW','REVERIFICATION_REQUIRED']:raise ValidationError('CV belum diajukan untuk pemeriksaan.')
 if data['status']=='VERIFIED' and completeness(p)['missing']:raise ValidationError('CV belum lengkap.')
 claim_revision(p,data['revision']);p.status=data['status'];p.review_note=data['note'];p.save();v=version(p,actor);audit(actor,'CV_REVIEWED',p,{'status':p.status,'version':v.number});notify(p.user,'Status CV: '+p.get_status_display(),'/student/cv/')
@transaction.atomic
def select_job(p,job,actor):
 p=StudentProfile.objects.select_for_update().get(pk=p.pk);job=Job.objects.select_for_update().get(pk=job.pk)
 if job.status!='OPEN' or (job.deadline and job.deadline<timezone.localdate()):raise ValidationError('Lowongan sudah ditutup atau melewati batas pengajuan.')
 if p.status!='VERIFIED' or completeness(p)['missing']:raise ValidationError('Lengkapi CV dan tunggu verifikasi admin sebelum memilih lowongan.')
 if Application.objects.filter(student=p,job=job).exists():raise ValidationError('Anda sudah memilih lowongan ini.')
 v=version(p,actor);app=Application.objects.create(student=p,job=job,cv_version=v);ApplicationHistory.objects.create(application=app,status=app.status,actor=actor,note='Pengajuan diterima oleh LPK KEIGO.');audit(actor,'JOB_SELECTED',app,{'cv_version':v.number});notify_admin('Pengajuan lowongan baru menunggu proses.',f'/admin/lamaran/{app.pk}/');return app
@transaction.atomic
def change_stage(app,actor,data):
 app=Application.objects.select_for_update().get(pk=app.pk)
 if app.revision!=data['revision']:raise ValidationError('Tahap sudah berubah. Muat ulang halaman.')
 if app.status==data['status']:raise ValidationError('Pilih tahap yang berbeda.')
 old=app.status;app.status=data['status'];app.revision+=1;app.save();ApplicationHistory.objects.create(application=app,previous_status=old,status=app.status,actor=actor,note=data.get('note',''));audit(actor,'APPLICATION_STAGE_CHANGED',app,{'from':old,'to':app.status});notify(app.student.user,'Pengajuan '+app.job.code+': '+app.get_status_display(),f'/student/lamaran/{app.pk}/')
def eligibility(p,job):
 results=[]
 if p.birth_date:
  t=timezone.localdate();age=t.year-p.birth_date.year-((t.month,t.day)<(p.birth_date.month,p.birth_date.day))
  if job.min_age or job.max_age:results.append(('Rentang usia',not ((job.min_age and age<job.min_age) or (job.max_age and age>job.max_age))))
 if job.min_height:results.append(('Tinggi badan',p.height is not None and p.height>=job.min_height))
 if job.japanese_level:results.append(('Sertifikat bahasa sesuai teks persyaratan',job.japanese_level.casefold() in p.japanese_certificate.casefold()))
 if job.skill:results.append(('Sertifikat keterampilan tercatat',p.certificates.filter(kind='SKILL',name__icontains=job.skill).exists()))
 return results
