from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from syncode.firebase import db
from syncodeapp.utils.hashing import hash_password, verify_password

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