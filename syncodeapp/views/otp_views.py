from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from syncodeapp.utils.email_utils import generate_otp, send_otp_email
from syncode.firebase import db


@csrf_exempt
@require_POST
def send_otp_email_view(request):
    data = json.loads(request.body)
    email = data.get('email')

    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    otp = generate_otp()
    cache.set(f'otp_{email}', otp, timeout=600)  # Store OTP for 10 mins

    send_otp_email(email, otp)
    return JsonResponse({'message': 'OTP sent successfully'})


@csrf_exempt
@require_POST
def verify_otp_view(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp = data.get('otp')

    cached_otp = cache.get(f'otp_{email}')
    if cached_otp == otp:
        cache.delete(f'otp_{email}')
        return JsonResponse({'message': 'OTP verified'})
    else:
        return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)



@require_POST
def verify_register_otp(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return JsonResponse({'error': 'Email and OTP are required'}, status=400)

    cached_otp = cache.get(f'otp_{email}')
    if cached_otp != otp:
        return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)

    user_data = cache.get(f'reg_pending_{email}')
    if not user_data:
        return JsonResponse({'error': 'Registration session expired'}, status=400)

    # Finalize registration
    student_ref = db.collection('Students').document()
    student_data = {
        'student_id': student_ref.id,
        'enroll': user_data['enroll'],
        'email': email,
        'username': user_data['username'],
        'password': user_data['password']
    }
    student_ref.set(student_data)

    # Create session
    request.session['student_id'] = student_ref.id
    request.session['student_enroll'] = student_data['enroll']
    request.session['student_email'] = email
    request.session['student_username'] = student_data['username']
    request.session.set_expiry(1209600)

    # Cleanup
    cache.delete(f'otp_{email}')
    cache.delete(f'reg_pending_{email}')

    return JsonResponse({
        'message': 'Student registered and logged in successfully',
        'student_id': student_ref.id,
        'enroll': student_data['enroll'],
        'email': email,
        'username': student_data['username']
    }, status=201)


@require_POST
def verify_login_otp(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return JsonResponse({'error': 'Email and OTP are required'}, status=400)

    cached_otp = cache.get(f'otp_{email}')
    if cached_otp != otp:
        return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)

    user_data = cache.get(f'login_pending_{email}')
    if not user_data:
        return JsonResponse({'error': 'Login session expired'}, status=400)

    # Set session
    request.session['student_id'] = user_data['student_id']
    request.session['student_enroll'] = user_data['enroll']
    request.session['student_email'] = email
    request.session['student_username'] = user_data['username']
    request.session.set_expiry(1209600)

    # Cleanup
    cache.delete(f'otp_{email}')
    cache.delete(f'login_pending_{email}')

    return JsonResponse({
        'message': 'Login successful',
        'student_id': user_data['student_id'],
        'enroll': user_data['enroll'],
        'email': email,
        'username': user_data['username']
    }, status=200)


@csrf_exempt
@require_POST
def resend_otp_view(request):
    data = json.loads(request.body)
    email = data.get('email')

    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    # Check if email has a pending registration or login
    is_pending_register = cache.get(f'reg_pending_{email}') is not None
    is_pending_login = cache.get(f'login_pending_{email}') is not None

    if not is_pending_register and not is_pending_login:
        return JsonResponse({'error': 'No pending OTP process found for this email'}, status=400)

    otp = generate_otp()
    cache.set(f'otp_{email}', otp, timeout=600)  # Reset OTP timeout to 10 mins

    send_otp_email(email, otp)
    return JsonResponse({'message': 'OTP resent successfully'})
