from django.db import migrations

def backfill(apps,schema_editor):
 Profile=apps.get_model('core','StudentProfile')
 Version=apps.get_model('core','CVVersion')
 Audit=apps.get_model('core','AuditEvent')
 alias=schema_editor.connection.alias
 for p in Profile.objects.using(alias).filter(submitted_at__isnull=True).iterator():
  event=Audit.objects.using(alias).filter(entity='StudentProfile',entity_id=str(p.pk),action='CV_SUBMITTED').order_by('-created_at','-pk').first()
  if not event:continue
  version=Version.objects.using(alias).filter(student_id=p.pk,number=event.metadata.get('version')).first()
  if version:Profile.objects.using(alias).filter(pk=p.pk).update(submitted_at=event.created_at,submitted_version_id=version.pk)

class Migration(migrations.Migration):
 dependencies=[('core','0002_studentprofile_submitted_at_and_more')]
 operations=[migrations.RunPython(backfill,migrations.RunPython.noop)]
