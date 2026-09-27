class PrivacyMiddleware:
 def __init__(self,get_response):self.get_response=get_response
 def __call__(self,request):
  response=self.get_response(request)
  if request.path.startswith(('/student','/admin','/dokumen','/masuk','/daftar','/pulihkan','/pemulihan-selesai')):
   response['Cache-Control']='no-store';response['X-Robots-Tag']='noindex, nofollow'
  response['Referrer-Policy']='same-origin'
  response['Content-Security-Policy']="default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-src https://www.google.com https://maps.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
  return response
