from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
import getpass
class Command(BaseCommand):
 help='Create an administrator interactively; never seeds a production password.'
 def add_arguments(self,parser):parser.add_argument('--email',required=True)
 def handle(self,*args,**options):
  email=options['email'].lower()
  if User.objects.filter(username=email).exists():raise CommandError('Account already exists; do not overwrite it.')
  password=getpass.getpass('New admin password: ');confirm=getpass.getpass('Repeat password: ')
  if password!=confirm:raise CommandError('Passwords do not match')
  u=User(username=email,email=email,first_name='Admin Keigo',is_staff=True,is_superuser=False)
  validate_password(password,u);u.set_password(password)
  with transaction.atomic():u.save()
  self.stdout.write(self.style.SUCCESS('Administrator created. Sign in at /masuk/.'))
