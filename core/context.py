from django.conf import settings
from . import content
def common(request):
 return {'institution':content.INSTITUTION,'canonical':settings.PUBLIC_ORIGIN+request.path,'unread_count':request.user.notifications.filter(read_at=None).count() if request.user.is_authenticated else 0,'portal':request.path.startswith(('/student','/admin')),'is_admin_portal':request.path.startswith('/admin')}
