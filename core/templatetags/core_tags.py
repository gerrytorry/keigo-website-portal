from django import template
from core.models import StudentProfile
from core.forms import PERSONAL,PHYSICAL,LANGUAGE,EXTRA
register=template.Library()
@register.filter
def profile_pairs(data):
 result=[]
 for f in PERSONAL+PHYSICAL+LANGUAGE+EXTRA:
  field=StudentProfile._meta.get_field(f);v=data.get(f)
  if isinstance(v,bool):v='Ya' if v else 'Tidak'
  elif field.choices:v=dict(field.choices).get(v,v)
  result.append((field.verbose_name,v))
 result.append(('Email',data.get('email')))
 return result
@register.filter
def repeat_groups(data):
 from core.models import Education,WorkExperience,FamilyMember,Certificate,JapanHistory
 out=[]
 for key,title,model in [('educations','Pendidikan',Education),('work_experiences','Pengalaman kerja',WorkExperience),('family_members','Keluarga',FamilyMember),('certificates','Sertifikat',Certificate),('japan_history','Riwayat di Jepang',JapanHistory)]:
  rows=[]
  for row in data.get(key,[]):rows.append([(f.verbose_name,row.get(f.name)) for f in model._meta.fields if f.name not in ['id','student','created_at','updated_at']])
  out.append({'title':title,'rows':rows})
 return out
@register.simple_tag(takes_context=True)
def page_query(context,n):
 q=context['request'].GET.copy();q['page']=n;return '?'+q.urlencode()

@register.filter
def cv_percent(student):
 from core.services import completeness
 return completeness(student)['percent']
