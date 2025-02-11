from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def get_csrf_token(request):
    """This view sets the CSRF token in a cookie"""
    response = JsonResponse({"message": "CSRF token set"})
    csrf_token = request.COOKIES.get('csrftoken')
    if csrf_token:
        response['X-CSRFToken'] = csrf_token
    return response