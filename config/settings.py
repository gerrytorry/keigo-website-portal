from pathlib import Path
import os,secrets
BASE_DIR=Path(__file__).resolve().parent.parent
ENV=os.getenv('APP_ENV','development')
DEBUG=ENV=='development'
SECRET_KEY=os.getenv('SECRET_KEY','')
if not SECRET_KEY:
 if not DEBUG: raise RuntimeError('SECRET_KEY wajib di staging/production')
 keyfile=BASE_DIR/'.local-secret'
 if not keyfile.exists(): keyfile.write_text(secrets.token_urlsafe(64))
 SECRET_KEY=keyfile.read_text().strip()
ALLOWED_HOSTS=os.getenv('ALLOWED_HOSTS','127.0.0.1,localhost,testserver').split(',')
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','core.middleware.PrivacyMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','core.context.common']}}]
WSGI_APPLICATION='config.wsgi.application'
if os.getenv('DB_NAME'):
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.environ['DB_NAME'],'USER':os.environ['DB_USER'],'PASSWORD':os.environ['DB_PASSWORD'],'HOST':os.getenv('DB_HOST','127.0.0.1'),'PORT':os.getenv('DB_PORT','5432'),'CONN_MAX_AGE':60}}
else:
 if not DEBUG: raise RuntimeError('Configure PostgreSQL for staging/production')
 DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.getenv('SQLITE_PATH',BASE_DIR/'data.sqlite3'),'OPTIONS':{'timeout':20}}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='id';TIME_ZONE='Asia/Jakarta';USE_I18N=True;USE_TZ=True
STATIC_URL='/static/';STATIC_ROOT=BASE_DIR/'staticfiles'
PRIVATE_MEDIA_ROOT=Path(os.getenv('PRIVATE_MEDIA_ROOT') or BASE_DIR/'private-media')
MEDIA_ROOT=PRIVATE_MEDIA_ROOT;MEDIA_URL='/private-unserved/'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/masuk/';LOGIN_REDIRECT_URL='/student/';LOGOUT_REDIRECT_URL='/'
SESSION_COOKIE_HTTPONLY=True;SESSION_COOKIE_SAMESITE='Lax';SESSION_COOKIE_AGE=28800
SESSION_COOKIE_SECURE=not DEBUG;CSRF_COOKIE_SECURE=not DEBUG
SECURE_SSL_REDIRECT=not DEBUG
SECURE_HSTS_SECONDS=31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_CONTENT_TYPE_NOSNIFF=True;X_FRAME_OPTIONS='DENY'
CSRF_TRUSTED_ORIGINS=[s for s in os.getenv('CSRF_TRUSTED_ORIGINS','').split(',') if s]
DATA_UPLOAD_MAX_MEMORY_SIZE=6*1024*1024;FILE_UPLOAD_MAX_MEMORY_SIZE=5*1024*1024
DATA_UPLOAD_MAX_NUMBER_FIELDS=2500
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST=os.getenv('EMAIL_HOST','');EMAIL_PORT=int(os.getenv('EMAIL_PORT','587'));EMAIL_USE_TLS=True
EMAIL_HOST_USER=os.getenv('EMAIL_HOST_USER','');EMAIL_HOST_PASSWORD=os.getenv('EMAIL_HOST_PASSWORD','')
DEFAULT_FROM_EMAIL=os.getenv('DEFAULT_FROM_EMAIL','noreply@localhost')
PUBLIC_ORIGIN=os.getenv('PUBLIC_ORIGIN','http://127.0.0.1:5190')

PASSWORD_RESET_TIMEOUT=3600
EMAIL_TIMEOUT=15

CSRF_FAILURE_VIEW='core.views.csrf_failure'
