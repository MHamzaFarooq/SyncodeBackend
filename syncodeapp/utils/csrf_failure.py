from django.http import JsonResponse
from django.middleware.csrf import REASON_NO_CSRF_COOKIE

def custom_csrf_failure_view(request,reason=""):    
    return JsonResponse({
        'error': reason if reason else REASON_NO_CSRF_COOKIE
    }, status = 403)
