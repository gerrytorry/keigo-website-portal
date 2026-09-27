from functools import wraps
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse,FileResponse,Http404
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError,PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction,IntegrityError
from django.db.models import Q,F
from django.forms import inlineformset_factory
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.conf import settings
from .models import *
from .forms import *
from .services import *
from . import content
import hashlib,hmac,io,csv

def staff_required(fn):
 @login_required
 @wraps(fn)
 def wrapped(request,*args,**kwargs):
  if not request.user.is_staff:raise PermissionDenied
  return fn(request,*args,**kwargs)
 return wrapped

def page(request,template,**ctx):
 titles={'home':'Pelatihan Bahasa Jepang di Brebes','student_dashboard':'Ringkasan Siswa','cv':'CV Saya','cv_review':'Tinjau CV','documents':'Dokumen Siswa','jobs':'Lowongan Jepang','job_detail':'Detail Lowongan','apply':'Pengajuan ke LPK','applications':'Pengajuan Saya','application_detail':'Detail Pengajuan','notifications':'Notifikasi','admin_dashboard':'Ringkasan Operasional','admin_students':'Siswa & CV','admin_student':'Detail Siswa','admin_jobs':'Kelola Lowongan','admin_job':'Detail Lowongan','admin_applications':'Kandidat & Seleksi','admin_application':'Detail Kandidat','audit':'Riwayat Audit'}
 ctx.setdefault('title',titles.get(template,'Portal Keigo'))
 return render(request,'core/'+template+'.html',ctx)
def paginate(request,qs):return Paginator(qs,20).get_page(request.GET.get('page'))
def profile(request):
 if request.user.is_staff:raise PermissionDenied('Akun admin tidak memiliki CV siswa.')
 return get_object_or_404(StudentProfile,user=request.user)
def err(request,e):messages.error(request,' '.join(e.messages) if isinstance(e,ValidationError) else str(e))
def throttle(request,identity):
 key=hmac.new(settings.SECRET_KEY.encode(),(request.META.get('REMOTE_ADDR','')+'|'+identity.casefold()).encode(),hashlib.sha256).hexdigest()
 with transaction.atomic():
  a,_=LoginAttempt.objects.select_for_update().get_or_create(key=key)
  if timezone.now()-a.started_at>__import__('datetime').timedelta(minutes=15):a.count=0;a.started_at=timezone.now()
  a.count+=1;a.save()
  return a.count>10

def home(request):return page(request,'home',programs=content.PROGRAMS,gallery=content.GALLERY,steps=content.STEPS)
def public_page(request,slug):
 if slug not in content.PAGES:raise Http404
 return page(request,'public_page',**content.PAGES[slug],gallery=content.GALLERY if slug=='fasilitas' else [],steps=content.STEPS if slug=='alur' else [])
def register(request):
 if request.user.is_authenticated:return redirect('dashboard')
 form=RegisterForm(request.POST or None)
 if request.method=='POST':
  if throttle(request,'register'):form.add_error(None,'Terlalu banyak percobaan. Coba kembali dalam 15 menit.')
  elif form.is_valid():
   try:
    with transaction.atomic():
     u=form.save();StudentProfile.objects.create(user=u,full_name=form.cleaned_data['full_name']);audit(u,'ACCOUNT_REGISTERED',u)
    login(request,u);return redirect('dashboard')
   except IntegrityError:form.add_error('email','Email sudah digunakan.')
 return page(request,'auth',form=form,title='Mulai langkahmu bersama Keigo',subtitle='Buat akun, lalu lengkapi CV secara bertahap.',register=True)
def sign_in(request):
 if request.user.is_authenticated:return redirect('dashboard')
 form=LoginForm(request,data=request.POST or None)
 if request.method=='POST':
  # A per-IP counter prevents username rotation bypass; per-identity adds targeted protection.
  limited=throttle(request,'login') or throttle(request,request.POST.get('username',''))
  if limited:form.add_error(None,'Terlalu banyak percobaan. Coba lagi dalam 15 menit.')
  elif form.is_valid():login(request,form.get_user());return redirect('dashboard')
 return page(request,'auth',form=form,title='Selamat datang kembali',subtitle='Masuk untuk melanjutkan perjalananmu.',register=False)
@require_POST
@login_required
def sign_out(request):logout(request);return redirect('home')
@login_required
def dashboard(request):
 if request.user.is_staff:return redirect('admin_dashboard')
 p=profile(request);return page(request,'student_dashboard',p=p,completion=completeness(p),applications=p.applications.select_related('job')[:5],notes=p.notes.filter(visibility='STUDENT').order_by('-created_at')[:5],documents=p.documents.filter(is_current=True),notifications=request.user.notifications.filter(read_at=None)[:5])

SECTIONS=[('identitas','Identitas',PERSONAL),('fisik','Fisik & paspor',PHYSICAL),('bahasa','Bahasa & karakter',LANGUAGE),('pendidikan','Pendidikan',Education,EducationForm,'educations'),('pekerjaan','Pengalaman kerja',WorkExperience,WorkForm,'work_experiences'),('keluarga','Keluarga',FamilyMember,FamilyForm,'family_members'),('sertifikat','Sertifikat',Certificate,CertificateForm,'certificates'),('tambahan','Informasi tambahan',EXTRA),('jepang','Riwayat di Jepang',JapanHistory,JapanForm,'japan_history')]
@login_required
def cv(request,section='identitas',student_id=None):
 if student_id:
  if not request.user.is_staff:raise PermissionDenied
  p=get_object_or_404(StudentProfile,pk=student_id)
 else:p=profile(request)
 s=next((x for x in SECTIONS if x[0]==section),None)
 if not s:raise Http404
 is_set=len(s)>3;form=None;formset=None;readonly=p.status in ['SUBMITTED','UNDER_REVIEW']
 if is_set:
  factory=inlineformset_factory(StudentProfile,s[2],form=s[3],extra=0,can_delete=True,max_num=100,validate_max=True,absolute_max=110)
  formset=factory(request.POST or None,instance=p,prefix='rows')
 else:form=ProfileForm(request.POST or None,instance=p,section=s[2],initial={'revision':p.revision})
 if request.method=='POST':
  valid=formset.is_valid() if is_set else form.is_valid()
  if valid:
   try:
    if is_set:
     with transaction.atomic():
      fresh=StudentProfile.objects.select_for_update().get(pk=p.pk);editable(fresh)
      try:revision=int(request.POST.get('revision','-1'))
      except ValueError:raise ValidationError('Versi tidak valid.')
      claim_revision(fresh,revision);formset.save()
      if fresh.status=='VERIFIED':fresh.status='REVERIFICATION_REQUIRED'
      fresh.save();audit(request.user,'CV_ROWS_UPDATED',fresh,{'section':section,'revision':fresh.revision});p=fresh
    else:p=save_profile(p,form,request.user)
    if request.headers.get('X-Requested-With')=='autosave':return JsonResponse({'ok':True,'revision':p.revision,'row_ids':[f.instance.pk for f in formset.forms] if is_set else None})
    messages.success(request,'Perubahan tersimpan.')
    nxt=request.POST.get('next')
    return redirect(('admin_cv' if student_id else 'cv'),**({'student_id':student_id} if student_id else {}),section=nxt if nxt in [x[0] for x in SECTIONS] else section)
   except ValidationError as e:
    if request.headers.get('X-Requested-With')=='autosave':return JsonResponse({'ok':False,'error':' '.join(e.messages)},status=409)
    err(request,e)
  elif request.headers.get('X-Requested-With')=='autosave':return JsonResponse({'ok':False,'error':'Periksa isian yang belum valid.','errors':form.errors.get_json_data() if form else {}},status=422)
 return page(request,'cv',required_for_submit=REQUIRED,p=p,form=form,formset=formset,section=section,section_title=s[1],sections=SECTIONS,completion=completeness(p),readonly=readonly,admin_edit=bool(student_id),next_section=SECTIONS[(SECTIONS.index(s)+1)%len(SECTIONS)][0])
def submission_json(request):
 return request.headers.get('X-Requested-With')=='cv-submit' or 'application/json' in request.headers.get('Accept','')

def submission_missing(p):
 result=[]
 for slug,label,fields,*rest in SECTIONS:
  if rest:continue
  for field in fields:
   if field in REQUIRED and (getattr(p,field) is None or getattr(p,field)==''):
    result.append({'label':str(p._meta.get_field(field).verbose_name),'url':f'/student/cv/{slug}/'})
 for relation,label,slug in [('educations','Riwayat pendidikan','pendidikan'),('family_members','Data keluarga','keluarga')]:
  if not getattr(p,relation).exists():result.append({'label':label,'url':f'/student/cv/{slug}/'})
 return result

def cv_review(request):
 wants_json=submission_json(request)
 if not request.user.is_authenticated:
  if wants_json:return JsonResponse({'ok':False,'code':'authentication','error':'Sesi berakhir. Masuk kembali untuk mengajukan CV.','login_url':'/masuk/'},status=401)
  from django.contrib.auth.views import redirect_to_login
  return redirect_to_login(request.get_full_path())
 if request.user.is_staff:
  if wants_json:return JsonResponse({'ok':False,'code':'permission','error':'Pengajuan CV hanya tersedia untuk akun siswa.'},status=403)
  raise PermissionDenied
 p=profile(request);error='';http_status=200
 if request.method=='POST':
  code='validation'
  try:
   if request.POST.get('confirm')!='yes':raise ValidationError('Centang pernyataan bahwa data CV sudah diperiksa.',code='confirmation')
   try:revision=int(request.POST.get('revision',''))
   except (ValueError,TypeError):raise ValidationError('Versi CV tidak valid. Muat ulang halaman tinjauan.',code='conflict')
   v=submit_cv(p,request.user,revision)
   p.refresh_from_db()
   if wants_json:return JsonResponse({'ok':True,'message':'CV berhasil diajukan ke LPK.','status':p.status,'submitted_at':p.submitted_at.isoformat(),'version':v.number,'version_id':v.pk,'dashboard_url':'/student/'})
   messages.success(request,'CV berhasil diajukan ke LPK.');return redirect('dashboard')
  except ValidationError as e:
   error=' '.join(e.messages);code=e.code if hasattr(e,'code') else 'validation';http_status=409 if code in ['already_submitted','conflict'] else 422
  except PermissionDenied:
   error='Pengajuan hanya dapat dilakukan pemilik CV.';code='permission';http_status=403
  except Exception:
   import logging
   logging.getLogger(__name__).exception('CV submission failed student_id=%s',p.pk)
   error='Pengajuan belum dapat dikonfirmasi. Data CV tetap tersimpan. Periksa status dashboard sebelum mencoba lagi.';code='server';http_status=503
  if wants_json:return JsonResponse({'ok':False,'code':code,'error':error,'missing':submission_missing(p) if code!='server' else []},status=http_status)
  if code=='server':return HttpResponse('Pengajuan belum dapat dikonfirmasi. Periksa dashboard sebelum mencoba lagi. <a href="/student/">Buka dashboard</a>',status=503)
  p.refresh_from_db()
 return render(request,'core/cv_review.html',{'title':'Tinjau CV','p':p,'data':snapshot(p),'completion':completeness(p),'missing_items':submission_missing(p),'submission_error':error},status=http_status)
@login_required
def documents(request):
 p=profile(request);form=UploadForm(request.POST or None,request.FILES or None)
 if request.method=='POST' and form.is_valid():
  f=form.cleaned_data['file'];old=None
  try:
   with transaction.atomic():
    if form.cleaned_data.get('replaces'):old=get_object_or_404(Document.objects.select_for_update(),pk=form.cleaned_data['replaces'],student=p,is_current=True)
    if old and old.category!=form.cleaned_data['category']:raise ValidationError('Kategori dokumen pengganti harus sama.')
    digest=hashlib.sha256(f.read()).hexdigest();f.seek(0)
    doc=Document.objects.create(student=p,category=form.cleaned_data['category'],label=form.cleaned_data['label'],file=f,original_name=__import__('pathlib').Path(f.name).name[:250],size=f.size,digest=digest,replaces=old)
    if old:old.is_current=False;old.save()
    audit(request.user,'DOCUMENT_UPLOADED',doc);notify_admin('Dokumen siswa menunggu pemeriksaan.',f'/admin/siswa/{p.pk}/')
   messages.success(request,'Dokumen tersimpan secara privat.');return redirect('documents')
  except ValidationError as e:form.add_error(None,e)
 current=p.documents.filter(is_current=True).order_by('category','id');present=set(current.values_list('category',flat=True))
 return page(request,'documents',form=form,documents=current,missing=[l for k,l in DOC_CATEGORIES[:7] if k not in present])
@login_required
def download_document(request,pk):
 d=get_object_or_404(Document,pk=pk)
 if not request.user.is_staff and d.student.user_id!=request.user.pk:raise Http404
 try:stream=d.file.open('rb')
 except (FileNotFoundError,OSError):raise Http404('Dokumen tidak tersedia. Hubungi admin.')
 if request.user.is_staff:audit(request.user,'DOCUMENT_DOWNLOADED',d)
 return FileResponse(stream,as_attachment=True,filename=d.original_name)

def jobs(request):
 qs=Job.objects.filter(status='OPEN').filter(Q(deadline__isnull=True)|Q(deadline__gte=timezone.localdate()))
 q=request.GET.get('q','')[:150];program=request.GET.get('program','');industry=request.GET.get('industry','')[:100]
 if q:qs=qs.filter(Q(title__icontains=q)|Q(company__icontains=q)|Q(code__icontains=q)|Q(prefecture__icontains=q))
 if program:qs=qs.filter(program=program)
 if industry:qs=qs.filter(industry=industry)
 return page(request,'jobs',jobs=paginate(request,qs),q=q,program=program,industries=Job.objects.filter(status='OPEN').values_list('industry',flat=True).distinct(),selected_industry=industry)
def job_detail(request,pk):
 j=get_object_or_404(Job,pk=pk)
 historical=request.user.is_authenticated and Application.objects.filter(student__user=request.user,job=j).exists()
 if j.status!='OPEN' and not (request.user.is_staff or historical):raise Http404
 p=getattr(request.user,'profile',None) if request.user.is_authenticated else None
 return page(request,'job_detail',job=j,eligibility=eligibility(p,j) if p else [],p=p,completion=completeness(p) if p else None,application=Application.objects.filter(student=p,job=j).first() if p else None)
@login_required
def apply_job(request,pk):
 p=profile(request);j=get_object_or_404(Job,pk=pk)
 if request.method=='POST':
  try:
   if request.POST.get('confirm')!='yes':raise ValidationError('Konfirmasi pengajuan terlebih dahulu.')
   app=select_job(p,j,request.user);messages.success(request,'Pengajuan diterima Admin LPK KEIGO.');return redirect('application_detail',pk=app.pk)
  except (ValidationError,IntegrityError) as e:err(request,e if isinstance(e,ValidationError) else ValidationError('Anda sudah memilih lowongan ini.'))
 return page(request,'apply',job=j,p=p,completion=completeness(p))
@login_required
def applications(request):
 p=profile(request);return page(request,'applications',applications=paginate(request,p.applications.select_related('job','cv_version')))
@login_required
def application_detail(request,pk):
 app=get_object_or_404(Application.objects.select_related('job','cv_version'),pk=pk,student__user=request.user)
 return page(request,'application_detail',app=app,history=app.history.all(),interviews=app.interviews.all())
@login_required
def notifications(request):
 if request.method=='POST':
  request.user.notifications.filter(pk=request.POST.get('id'),read_at=None).update(read_at=timezone.now());return redirect('notifications')
 return page(request,'notifications',notifications=paginate(request,request.user.notifications.all()))
@staff_required
def admin_dashboard(request):
 return page(request,'admin_dashboard',counts={'Siswa':StudentProfile.objects.count(),'CV perlu diperiksa':StudentProfile.objects.filter(status__in=['SUBMITTED','UNDER_REVIEW','REVERIFICATION_REQUIRED']).count(),'CV perlu revisi':StudentProfile.objects.filter(status='NEEDS_REVISION').count(),'CV terverifikasi':StudentProfile.objects.filter(status='VERIFIED').count(),'Lowongan terbuka':Job.objects.filter(status='OPEN').count(),'Pengajuan baru':Application.objects.filter(status='SUBMITTED_TO_LPK').count()},pending=StudentProfile.objects.filter(status__in=['SUBMITTED','UNDER_REVIEW','REVERIFICATION_REQUIRED'])[:8],interviews=Interview.objects.filter(scheduled_at__gte=timezone.now(),result='PENDING').select_related('application__student','application__job').order_by('scheduled_at')[:8])
@staff_required
def admin_students(request):
 qs=StudentProfile.objects.select_related('user');q=request.GET.get('q','')[:150];status=request.GET.get('status','');level=request.GET.get('level','')[:30]
 if q:qs=qs.filter(Q(full_name__icontains=q)|Q(user__email__icontains=q)|Q(phone__icontains=q)|Q(pk=int(q) if q.isdigit() else -1))
 if status:qs=qs.filter(status=status)
 if level:qs=qs.filter(japanese_certificate=level)
 return page(request,'admin_students',students=paginate(request,qs.order_by('-created_at')),q=q,states=CV_STATES,selected_status=status,levels=StudentProfile._meta.get_field('japanese_certificate').choices)
@staff_required
def admin_student(request,pk):
 p=get_object_or_404(StudentProfile.objects.select_related('user'),pk=pk)
 form=CVReviewForm(initial={'revision':p.revision});note_form=NoteForm()
 if request.method=='POST':
  if request.POST.get('action')=='note':
   note_form=NoteForm(request.POST)
   if note_form.is_valid():
    with transaction.atomic():
     n=note_form.save(False);n.student=p;n.actor=request.user;n.save();audit(request.user,'NOTE_ADDED',n,{'visibility':n.visibility})
     if n.visibility=='STUDENT':notify(p.user,'Catatan baru dari admin LPK.','/student/')
    messages.success(request,'Catatan disimpan.');return redirect('admin_student',pk=pk)
  else:
   form=CVReviewForm(request.POST)
   if form.is_valid():
    try:review_cv(p,request.user,form.cleaned_data);messages.success(request,'Status CV diperbarui.');return redirect('admin_student',pk=pk)
    except ValidationError as e:form.add_error(None,e)
 return page(request,'admin_student',p=p,data=snapshot(p),form=form,note_form=note_form,sections=SECTIONS,completion=completeness(p),documents=p.documents.filter(is_current=True),applications=p.applications.select_related('job','cv_version'),notes=p.notes.select_related('actor').order_by('-created_at'),versions=p.versions.all()[:20])
@staff_required
def admin_document(request,pk):
 d=get_object_or_404(Document,pk=pk);form=DocumentReviewForm(request.POST or None,initial={'revision':d.revision,'status':d.status,'note':d.review_note})
 if request.method=='POST' and form.is_valid():
  with transaction.atomic():
   count=Document.objects.filter(pk=d.pk,revision=form.cleaned_data['revision'],is_current=True).update(status=form.cleaned_data['status'],review_note=form.cleaned_data['note'],revision=F('revision')+1)
   if count:audit(request.user,'DOCUMENT_REVIEWED',d,{'status':form.cleaned_data['status']});notify(d.student.user,'Dokumen '+d.get_category_display()+': '+dict(DOC_STATES)[form.cleaned_data['status']],'/student/dokumen/')
  if count:messages.success(request,'Dokumen diperbarui.');return redirect('admin_student',pk=d.student_id)
  form.add_error(None,'Dokumen telah berubah. Muat ulang halaman.')
 return page(request,'form_page',form=form,title='Periksa '+d.get_category_display(),subtitle=str(d.student),document=d)
@staff_required
def admin_jobs(request):
 qs=Job.objects.all();q=request.GET.get('q','')[:150];status=request.GET.get('status','')
 if q:qs=qs.filter(Q(code__icontains=q)|Q(title__icontains=q)|Q(company__icontains=q))
 if status:qs=qs.filter(status=status)
 return page(request,'admin_jobs',jobs=paginate(request,qs),q=q,states=Job._meta.get_field('status').choices,selected_status=status)
@staff_required
def admin_job_edit(request,pk=None):
 obj=get_object_or_404(Job,pk=pk) if pk else Job();revision=obj.revision
 form=JobForm(request.POST or None,instance=obj,initial={'revision':revision})
 if request.method=='POST' and form.is_valid():
  try:
   with transaction.atomic():
    if pk:
     old=Job.objects.select_for_update().get(pk=pk)
     if old.revision!=form.cleaned_data['revision']:raise ValidationError('Lowongan telah berubah. Muat ulang halaman.')
    else:old=None
    j=form.save(False);j.revision=revision+1;j.save();audit(request.user,'JOB_SAVED',j,{'status':j.status})
    if j.status=='OPEN' and (not old or old.status!='OPEN'):
     for user in User.objects.filter(is_staff=False,is_active=True).iterator():notify(user,'Lowongan tersedia: '+j.title,f'/lowongan/{j.pk}/')
   messages.success(request,'Lowongan disimpan.');return redirect('admin_job',pk=j.pk)
  except ValidationError as e:form.add_error(None,e)
 return page(request,'form_page',form=form,title='Ubah lowongan' if pk else 'Buat lowongan',subtitle='Informasi ini ditampilkan kepada siswa saat status Terbuka.')
@staff_required
def admin_job(request,pk):
 j=get_object_or_404(Job,pk=pk);qs=j.applications.select_related('student','cv_version');q=request.GET.get('q','')[:100];status=request.GET.get('status','')
 if q:qs=qs.filter(student__full_name__icontains=q)
 if status:qs=qs.filter(status=status)
 return page(request,'admin_job',job=j,applications=paginate(request,qs),states=APP_STATES,q=q,selected_status=status)
@staff_required
def admin_applications(request):
 qs=Application.objects.select_related('student','job','cv_version');status=request.GET.get('status','');q=request.GET.get('q','')[:150]
 if status:qs=qs.filter(status=status)
 if q:qs=qs.filter(Q(student__full_name__icontains=q)|Q(job__code__icontains=q)|Q(job__title__icontains=q))
 return page(request,'admin_applications',applications=paginate(request,qs),states=APP_STATES,q=q,selected_status=status)
@staff_required
def admin_application(request,pk):
 app=get_object_or_404(Application.objects.select_related('student','job','cv_version'),pk=pk);form=StageForm(request.POST or None,initial={'revision':app.revision,'status':app.status})
 if request.method=='POST' and form.is_valid():
  try:change_stage(app,request.user,form.cleaned_data);messages.success(request,'Tahap diperbarui.');return redirect('admin_application',pk=pk)
  except ValidationError as e:form.add_error(None,e)
 return page(request,'admin_application',app=app,form=form,data=app.cv_version.data,history=app.history.select_related('actor'),interviews=app.interviews.all())
@staff_required
def admin_interview(request,app_id,pk=None):
 app=get_object_or_404(Application,pk=app_id);obj=get_object_or_404(Interview,pk=pk,application=app) if pk else Interview(application=app);revision=obj.revision
 form=InterviewForm(request.POST or None,instance=obj,initial={'revision':revision})
 if request.method=='POST' and form.is_valid():
  with transaction.atomic():
   if pk and not Interview.objects.filter(pk=pk,revision=form.cleaned_data['revision']).update(revision=F('revision')+1):form.add_error(None,'Jadwal sudah berubah. Muat ulang halaman.')
   else:
    i=form.save(False);i.revision=revision+1;i.save();audit(request.user,'INTERVIEW_SAVED',i);notify(app.student.user,'Jadwal / hasil wawancara diperbarui.',f'/student/lamaran/{app.pk}/');messages.success(request,'Wawancara disimpan.');return redirect('admin_application',pk=app.pk)
 return page(request,'form_page',title='Jadwal wawancara',subtitle=str(app.student)+' · '+app.job.code,form=form)
@staff_required
def audit_list(request):
 qs=AuditEvent.objects.select_related('actor');q=request.GET.get('q','')[:100]
 if q:qs=qs.filter(Q(action__icontains=q)|Q(entity__icontains=q))
 return page(request,'audit',events=paginate(request,qs),q=q)
@staff_required
@require_POST
def export_cv(request,student_id):
 from .exports import make_xlsx
 p=get_object_or_404(StudentProfile,pk=student_id)
 v=None
 if request.POST.get('application'):
  app=get_object_or_404(Application,pk=request.POST['application'],student=p);v=app.cv_version
 elif request.POST.get('version'):v=get_object_or_404(CVVersion,pk=request.POST['version'],student=p)
 if v is None:
  with transaction.atomic():p=StudentProfile.objects.select_for_update().get(pk=p.pk);v=version(p,request.user)
 try:blob=make_xlsx(v)
 except Exception:
  import logging;logging.getLogger(__name__).exception('CV export failed version_id=%s',v.pk);messages.error(request,'Ekspor belum berhasil. Data tetap tersimpan. Hubungi pengelola sistem.');return redirect('admin_student',pk=p.pk)
 audit(request.user,'CV_EXPORTED',v,{'format':'XLSX','student_id':p.pk,'application':request.POST.get('application')})
 return FileResponse(io.BytesIO(blob),as_attachment=True,filename=f'CV_KEIGO_{p.pk}_v{v.number}.xlsx',content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
@staff_required
def candidate_csv(request,pk):
 j=get_object_or_404(Job,pk=pk);response=HttpResponse(content_type='text/csv; charset=utf-8');response['Content-Disposition']=f'attachment; filename="kandidat-{j.pk}.csv"';response.write('\ufeff');writer=csv.writer(response);writer.writerow(['ID','Nama','Email','Lowongan','Tahap','Versi CV','Tanggal'])
 def safe(v):
  s=str(v);return "'"+s if s.startswith(('=','+','-','@','\t','\r')) else s
 for a in j.applications.select_related('student__user','cv_version').iterator():writer.writerow([a.pk,safe(a.student.full_name),safe(a.student.user.email),safe(j.code),a.get_status_display(),a.cv_version.number,a.created_at.isoformat()])
 audit(request.user,'CANDIDATES_EXPORTED',j,{'format':'CSV'});return response
@staff_required
@require_POST
def bulk_stage(request,pk):
 j=get_object_or_404(Job,pk=pk);ids=request.POST.getlist('ids')
 if not ids or len(ids)>100 or any(not i.isdigit() for i in ids):messages.error(request,'Pilih 1–100 kandidat yang valid.');return redirect('admin_job',pk=pk)
 qs=j.applications.filter(pk__in=ids).select_related('student')
 if request.POST.get('confirm')=='yes':
  status=request.POST.get('status');note=request.POST.get('note','')[:2000]
  if status not in dict(APP_STATES):raise PermissionDenied
  try:
   with transaction.atomic():
    for app in qs.select_for_update():change_stage(app,request.user,{'revision':int(request.POST.get('revision_'+str(app.pk),'-1')),'status':status,'note':note})
   messages.success(request,'Tahap kandidat terpilih diperbarui.');return redirect('admin_job',pk=pk)
  except (ValidationError,ValueError) as e:err(request,e)
 return page(request,'bulk',job=j,applications=qs,states=APP_STATES)

def robots(request):return HttpResponse('User-agent: *\nDisallow: /student/\nDisallow: /admin/\nDisallow: /dokumen/\nDisallow: /masuk/\nDisallow: /daftar/\n',content_type='text/plain')
def sitemap(request):
 from xml.sax.saxutils import escape
 urls=['/','/tentang/','/program/','/fasilitas/','/alur/','/kontak/','/lowongan/']
 return HttpResponse('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(settings.PUBLIC_ORIGIN+p)+'</loc></url>' for p in urls)+'</urlset>',content_type='application/xml')


def password_reset(request):
 from django.contrib.auth.forms import PasswordResetForm
 form=PasswordResetForm(request.POST or None)
 if request.method=='POST':
  if throttle(request,'reset'):form.add_error(None,'Terlalu banyak percobaan. Coba lagi dalam 15 menit.')
  elif form.is_valid():
   if not settings.EMAIL_HOST:
    form.add_error(None,'Pemulihan email belum diaktifkan. Hubungi pengelola melalui kontak resmi untuk verifikasi identitas.')
   else:
    try:
     form.save(request=request,use_https=not settings.DEBUG,from_email=settings.DEFAULT_FROM_EMAIL,email_template_name='core/reset_email.txt',subject_template_name='core/reset_subject.txt')
     return page(request,'reset_done',title='Periksa email Anda')
    except Exception:
     import logging;logging.getLogger(__name__).error('Password reset email delivery failed')
     form.add_error(None,'Email belum dapat dikirim. Coba kembali atau hubungi pengelola.')
 return page(request,'password_reset',form=form,title='Pulihkan kata sandi')

def csrf_failure(request,reason=''):
 if request.path=='/student/cv/tinjau/' and submission_json(request):return JsonResponse({'ok':False,'code':'csrf','error':'Sesi atau token keamanan berubah. Muat ulang halaman, lalu masuk kembali bila diminta.'},status=403)
 return render(request,'403.html',status=403)
