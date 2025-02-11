from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware

class StudentSessionMiddleware(SessionMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.session_key = 'student_session'

    def process_request(self, request):
        request.student_session = None
        super().process_request(request)
        request.student_session = request.session
    
    def process_response(self, request, response):
        if hasattr(request,'student_session'):
            if request.student_session and any(k.startswith('student_') for k in request.student_session.keys()):
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME_STUDENT,
                    request.student_session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    path=settings.SESSION_COOKIE_PATH,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                ) 
        return response

class TeacherSessionMiddleware(SessionMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.session_key = 'teacher_session'
    
    def process_request(self, request):
        request.teacher_session = None
        super().process_request(request)
        request.teacher_session = request.session
    
    def process_response(self, request, response):
        if hasattr(request, 'teacher_session'):
            # Only set the cookie if there's teacher session data
            if request.teacher_session and any(k.startswith('teacher_') for k in request.teacher_session.keys()):
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME_TEACHER,
                    request.teacher_session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    path=settings.SESSION_COOKIE_PATH,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                )
        return response

