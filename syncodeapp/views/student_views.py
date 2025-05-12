from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import json
from syncode.firebase import db
from syncodeapp.utils.hashing import hash_password, verify_password
from syncodeapp.utils.email_utils import generate_otp, send_otp_email
from django.core.cache import cache


@require_POST
def create_student(request):
    try:
        data = json.loads(request.body)
        required_fields = ['enroll','email','username','password']

        # Check for required fields
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"error":f"Missing required fields: {field}"},status=400)


        students_ref = db.collection('Students')
        existing_students = students_ref.where('enroll','==',data['enroll']).stream()
        if any(existing_students):
            return JsonResponse({'error':'Enrollment number already exists'}, status=400)
        
        existing_students = students_ref.where('email','==',data['email']).stream()
        if any(existing_students):
            return JsonResponse({'error':'Email already exists'}, status=400)

        # Hash the password
        hashed_password = hash_password(data['password'])

        # Create a new student document
        student_ref = db.collection('Students').document()
        student_data = {
            'student_id': student_ref.id,
            'enroll': data['enroll'],
            'email': data['email'],
            'username': data['username'],
            'password': hashed_password.decode('utf-8')
        }    

        student_ref.set(student_data)

        # Store user data in session 

        request.session['student_id'] = student_data['student_id']
        request.session['student_enroll'] = student_data['enroll']
        request.session['student_email'] = student_data['email']
        request.session['student_username'] = student_data['username']
        # 2 Weeks
        request.session.set_expiry(1209600)

        return JsonResponse({
            'message': "Student created successfully",
            "student_id": student_ref.id,
            'enroll': student_data['enroll'],
            'email': student_data['email'],
            'username':student_data['username']

        }, status = 201)
    
    except Exception as e:
        return JsonResponse({"error": str(e)},status=500)
    

@require_POST
def login_student(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error':'Email and password are required'}, status=400)
        
        students_ref = db.collection('Students').where('email','==',email).stream()
        student = next(students_ref,None)

        if not student:
            return JsonResponse({'error':'Invalid email or password'}, status=401)
        
        student_data = student.to_dict()

        # Verify password
        if not verify_password(password, student_data['password']):
            return JsonResponse({'error':'Invalid email or password'}, status=401)
        
        # Store user data in session 
        request.session['student_id'] = student_data['student_id']
        request.session['student_enroll'] = student_data['enroll']
        request.session['student_email'] = student_data['email']
        request.session['student_username'] = student_data['username']

        # 2 Weeks
        request.session.set_expiry(1209600)

        return JsonResponse({
            'message':'Login Successful',
            'student_id':student_data['student_id'],
            'enroll': student_data['enroll'],
            'email': student_data['email'],
            'username':student_data['username']
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)},status=500)
    

@require_POST
def logout_student(request):
    try:
        if not any(k.startswith('student_') for k in request.session.keys()):
            return JsonResponse({'error':'No active student session found'}, status=401)
        # request.student_session = request.session
        # if 'student_id' not in request.student_session:
        #     return JsonResponse({'error':'No active session found'}, status=401)
        
        # request.student_session.flush()

        student_keys = [k for k in request.session.keys() if k.startswith('student_')]
        for key in student_keys:
            del request.session[key]

        return JsonResponse({'message':'Logged out successfully'}, status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)
    

# @csrf_exempt
@require_GET
def get_student_submissions(request):
    try:
        student_id = request.GET.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Missing student_id'}, status=400)

        submissions_query = db.collection('Submissions').where('student_id', '==', student_id)
        submissions = [doc.to_dict() for doc in submissions_query.stream()]

        return JsonResponse({'submissions': submissions}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_student_feedback_submissions(request):
    try:
        student_id = request.GET.get('student_id')
        if not student_id:
            return JsonResponse({'error': 'Missing student_id'}, status=400)

        # Step 1: Get all submissions by the student
        submissions = db.collection('Submissions').where('student_id', '==', student_id).stream()
        
        feedback_submissions = []
        for sub in submissions:
            sub_data = sub.to_dict()
            feedback = sub_data.get('feedback', '').strip()

            # Step 2: Check if feedback is not empty
            if feedback:
                sub_data['submission_id'] = sub.id

                # Optional: Add assignment name for context
                assignment_id = sub_data.get('assignment_id')
                if assignment_id:
                    assignment_ref = db.collection('Assignments').document(assignment_id).get()
                    if assignment_ref.exists:
                        sub_data['assignment_name'] = assignment_ref.to_dict().get('name', '')
                    else:
                        sub_data['assignment_name'] = ''
                else:
                    sub_data['assignment_name'] = ''

                feedback_submissions.append(sub_data)

        return JsonResponse({'submissions': feedback_submissions}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def pre_register_student(request):
    data = json.loads(request.body)
    required_fields = ['enroll','email','username','password']
    
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({"error":f"Missing required field: {field}"}, status=400)
    
    email = data['email']

    # Check if email/enroll already exists
    students_ref = db.collection('Students')
    if any(students_ref.where('email','==',email).stream()):
        return JsonResponse({'error':'Email already exists'}, status=400)
    if any(students_ref.where('enroll','==',data['enroll']).stream()):
        return JsonResponse({'error':'Enrollment number already exists'}, status=400)

    # Send OTP
    otp = generate_otp()
    cache.set(f'otp_{email}', otp, timeout=600)  # 10 minutes
    send_otp_email(email, otp)

    # Temporarily store user data in cache
    cache.set(f'reg_pending_{email}', {
        'enroll': data['enroll'],
        'username': data['username'],
        'password': hash_password(data['password']).decode('utf-8')
    }, timeout=600)

    return JsonResponse({'message': 'OTP sent to email', 'email': email}, status=200)


@require_POST
def pre_login_student(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)

    students_ref = db.collection('Students').where('email','==',email).stream()
    student = next(students_ref, None)
    if not student:
        return JsonResponse({'error': 'Invalid email or password'}, status=401)
    
    student_data = student.to_dict()
    if not verify_password(password, student_data['password']):
        return JsonResponse({'error': 'Invalid email or password'}, status=401)

    # Send OTP
    otp = generate_otp()
    cache.set(f'otp_{email}', otp, timeout=600)
    send_otp_email(email, otp)

    # Store minimal session data to validate later
    cache.set(f'login_pending_{email}', {
        'student_id': student_data['student_id'],
        'enroll': student_data['enroll'],
        'email': student_data['email'],
        'username': student_data['username']
    }, timeout=600)

    return JsonResponse({'message': 'OTP sent to email', 'email': email}, status=200)

