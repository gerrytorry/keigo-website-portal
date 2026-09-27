from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import *
from PIL import Image
from pathlib import Path
import re

class RegisterForm(UserCreationForm):
 email=forms.EmailField(label='Email',max_length=150)
 full_name=forms.CharField(label='Nama lengkap',max_length=150)
 consent=forms.BooleanField(label='Saya memahami bahwa data CV dan dokumen digunakan LPK untuk memproses pelatihan dan pengajuan lowongan.')
 class Meta: model=User;fields=['full_name','email','password1','password2','consent']
 def clean_email(self):
  email=self.cleaned_data['email'].lower()
  if User.objects.filter(username=email).exists(): raise ValidationError('Email ini sudah digunakan. Silakan masuk.')
  return email
 def save(self,commit=True):
  user=super().save(False);user.username=self.cleaned_data['email'];user.email=user.username;user.first_name=self.cleaned_data['full_name'];user.is_staff=False;user.is_superuser=False
  if commit:user.save()
  return user
class LoginForm(AuthenticationForm):
 username=forms.EmailField(label='Email');password=forms.CharField(label='Kata sandi',widget=forms.PasswordInput)

PERSONAL=['full_name','name_kana','gender','birth_date','birth_place','address','religion','phone','marital_status']
PHYSICAL=['health','blood_type','height','weight','smoking','alcohol','tattoo','passport']
LANGUAGE=['study_months','japanese_certificate','strengths','weaknesses','hobbies']
EXTRA=['home_phone','eyesight','dominant_hand','english_level','other_languages','favorite_subject','aspirations']
class ProfileForm(forms.ModelForm):
 revision=forms.IntegerField(widget=forms.HiddenInput,min_value=0)
 class Meta:
  model=StudentProfile;fields=PERSONAL+PHYSICAL+LANGUAGE+EXTRA
  widgets={'birth_date':forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'}),'address':forms.Textarea(attrs={'rows':3}),'strengths':forms.Textarea(attrs={'rows':3}),'weaknesses':forms.Textarea(attrs={'rows':3}),'hobbies':forms.Textarea(attrs={'rows':3}),'aspirations':forms.Textarea(attrs={'rows':3}),'phone':forms.TextInput(attrs={'type':'tel'})}
 def __init__(self,*args,section=None,**kwargs):
  super().__init__(*args,**kwargs)
  if section:
   for k in list(self.fields):
    if k not in section+['revision']:self.fields.pop(k)
  for n in ['smoking','alcohol','tattoo','passport']:
   if n in self.fields:self.fields[n]=forms.TypedChoiceField(label=self.fields[n].label,choices=[('','Pilih jawaban'),('True','Ya'),('False','Tidak')],coerce=lambda v:v=='True',empty_value=None,required=False)
 def clean_birth_date(self):
  d=self.cleaned_data['birth_date']
  if d and (d>timezone.localdate() or d.year<1900):raise ValidationError('Masukkan tanggal lahir yang valid.')
  return d
 def clean_phone(self):
  p=self.cleaned_data['phone']
  if p and not re.fullmatch(r'\+?[0-9 ()-]{8,25}',p):raise ValidationError('Masukkan nomor telepon yang valid.')
  return p
class DateRangeForm(forms.ModelForm):
 def clean(self):
  d=super().clean();a=d.get('start_date');b=d.get('end_date')
  if a and a>timezone.localdate():self.add_error('start_date','Tanggal mulai tidak boleh di masa depan.')
  if a and b and b<a:self.add_error('end_date','Tanggal selesai harus setelah tanggal mulai.')
  return d
class EducationForm(DateRangeForm):
 class Meta:model=Education;fields=['start_date','end_date','level','institution','major'];widgets={n:forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'}) for n in ['start_date','end_date']}
class WorkForm(DateRangeForm):
 class Meta:model=WorkExperience;fields=['start_date','end_date','company','industry','description','leaving_reason'];widgets={**{n:forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'}) for n in ['start_date','end_date']},'description':forms.Textarea(attrs={'rows':2})}
class FamilyForm(forms.ModelForm):
 class Meta:model=FamilyMember;fields=['name','relationship','age','occupation']
class CertificateForm(forms.ModelForm):
 class Meta:model=Certificate;fields=['date','name','kind'];widgets={'date':forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'})}
 def clean_date(self):
  d=self.cleaned_data['date']
  if d>timezone.localdate():raise ValidationError('Tanggal sertifikat tidak boleh di masa depan.')
  return d
class JapanForm(forms.ModelForm):
 class Meta:model=JapanHistory;fields=['company','organization','contact','address'];widgets={'address':forms.Textarea(attrs={'rows':2})}
class UploadForm(forms.Form):
 category=forms.ChoiceField(label='Jenis dokumen',choices=DOC_CATEGORIES)
 label=forms.CharField(label='Keterangan',max_length=150,required=False,help_text='Untuk ijazah, tuliskan jenjang SD/SMP/SMA agar tersimpan terpisah.')
 file=forms.FileField(label='Dokumen',help_text='PDF, JPEG, atau PNG. Maksimal 5 MB. Pas foto harus JPEG/PNG.')
 replaces=forms.IntegerField(required=False,widget=forms.HiddenInput)
 def clean(self):
  d=super().clean();f=d.get('file')
  if not f:return d
  ext=Path(f.name).suffix.lower()
  if f.size>5*1024*1024:raise ValidationError('Ukuran maksimum 5 MB.')
  if not f.size:raise ValidationError('File kosong.')
  if ext not in ['.pdf','.jpg','.jpeg','.png']:raise ValidationError('Jenis file tidak didukung.')
  head=f.read(8);f.seek(0)
  if ext=='.pdf':
   if d.get('category')=='PHOTO':raise ValidationError('Pas foto harus berupa JPEG atau PNG.')
   if not head.startswith(b'%PDF-'):raise ValidationError('Isi file bukan PDF yang valid.')
  else:
   try:
    im=Image.open(f)
    if im.format not in ('JPEG','PNG') or im.width*im.height>30000000:raise ValueError()
    im.verify()
   except Exception:raise ValidationError('Gambar tidak valid atau terlalu besar.')
   finally:f.seek(0)
  return d
class JobForm(forms.ModelForm):
 revision=forms.IntegerField(widget=forms.HiddenInput,initial=0)
 class Meta:
  model=Job;exclude=['created_at','updated_at'];widgets={'deadline':forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'}),'interview_at':forms.DateTimeInput(format='%Y-%m-%dT%H:%M',attrs={'type':'datetime-local'}),'requirements':forms.Textarea(attrs={'rows':4}),'notes':forms.Textarea(attrs={'rows':3})}
 def clean(self):
  d=super().clean()
  if d.get('min_age') and d.get('max_age') and d['min_age']>d['max_age']:self.add_error('max_age','Usia maksimum harus >= usia minimum.')
  if d.get('status')=='OPEN' and d.get('deadline') and d['deadline']<timezone.localdate():self.add_error('deadline','Lowongan terbuka tidak boleh melewati batas pengajuan.')
  return d
class CVReviewForm(forms.Form):
 status=forms.ChoiceField(label='Keputusan pemeriksaan',choices=[x for x in CV_STATES if x[0] in ['UNDER_REVIEW','NEEDS_REVISION','VERIFIED']])
 note=forms.CharField(label='Catatan untuk siswa',required=False,max_length=2000,widget=forms.Textarea(attrs={'rows':3}))
 revision=forms.IntegerField(widget=forms.HiddenInput)
 def clean(self):
  d=super().clean()
  if d.get('status')=='NEEDS_REVISION' and not d.get('note','').strip():self.add_error('note','Alasan revisi wajib diisi.')
  return d
class DocumentReviewForm(CVReviewForm):
 status=forms.ChoiceField(label='Status dokumen',choices=DOC_STATES)
class StageForm(forms.Form):
 status=forms.ChoiceField(label='Tahap baru',choices=APP_STATES)
 note=forms.CharField(label='Catatan yang terlihat siswa',required=False,max_length=2000,widget=forms.Textarea(attrs={'rows':3}))
 revision=forms.IntegerField(widget=forms.HiddenInput)
 confirm=forms.BooleanField(label='Saya sudah memeriksa perubahan tahap ini.')
class NoteForm(forms.ModelForm):
 class Meta:model=AdminNote;fields=['text','visibility'];widgets={'text':forms.Textarea(attrs={'rows':3})}
class InterviewForm(forms.ModelForm):
 revision=forms.IntegerField(widget=forms.HiddenInput,initial=0)
 class Meta:model=Interview;fields=['scheduled_at','location','notes','result'];widgets={'scheduled_at':forms.DateTimeInput(format='%Y-%m-%dT%H:%M',attrs={'type':'datetime-local'}),'notes':forms.Textarea(attrs={'rows':3})}
 def clean_location(self):
  val=self.cleaned_data['location']
  if '://' in val and not val.startswith('https://'):raise ValidationError('Tautan online harus menggunakan HTTPS.')
  return val
