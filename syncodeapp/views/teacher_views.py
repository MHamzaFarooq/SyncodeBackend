from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from syncode.firebase import db, firestore
from syncodeapp.utils.hashing import hash_password, verify_password
from django.views.decorators.csrf import csrf_exempt


@require_POST
def create_teacher(request):
    try:
        data = json.loads(request.body)
        required_fields = ['name','username', 'password']

        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

        teachers_ref = db.collection('Teachers')
        existing_teachers = teachers_ref.where('username','==',data['username']).stream()
        if any(existing_teachers):
            return JsonResponse({'error':'Username already exists'}, status=400)
        
        
        hashed_password = hash_password(data['password'])

        teacher_ref = db.collection('Teachers').document()
        teacher_data = {
            'teacher_id': teacher_ref.id,
            'name': data['name'],
            'username': data['username'],
            'password': hashed_password.decode('utf-8')
        }

        teacher_ref.set(teacher_data)
        return JsonResponse({'message': 'Teacher created successfully', 'teacher_id': teacher_ref.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def login_teacher(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error':'Username and Password are required'}, status=400)
        
        teachers_ref = db.collection('Teachers').where('username','==',data['username']).stream()
        teacher = next(teachers_ref,None)

        if not teacher:
            return JsonResponse({'error':'Invalid username or password'}, status=401)
        
        teacher_data = teacher.to_dict()

        if not verify_password(password,teacher_data['password']):
            return JsonResponse({'error':'Invalid username or password'})
        
        request.session['teacher_id'] = teacher_data['teacher_id']
        request.session['teacher_username'] = teacher_data['username']
        request.session['teacher_name'] = teacher_data['name']

        request.teacher_session.set_expiry(1209600)

        return JsonResponse({
            'message': 'Login Successful',
            'teacher_id': teacher_data['teacher_id'],
            'username': teacher_data['username'],
            'name':teacher_data['name']
        }, status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)
        

@require_POST
def logout_teacher(request):
    try:
        # Check for teacher session data
        if not any(k.startswith('teacher_') for k in request.session.keys()):
            return JsonResponse({'error': 'No active teacher session found'}, status=401)
        
        # request.teacher_session = request.session
        # if 'teacher_id' not in request.teacher_session:
        #     return JsonResponse({'error':'No active session found'}, status=401)
        
        # request.teacher_session.flush()

        # Clear only teacher-related session data
        teacher_keys = [k for k in request.session.keys() if k.startswith('teacher_')]
        for key in teacher_keys:
            del request.session[key]


        return JsonResponse({'message':'Logged out succcessfully'}, status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)
    
@csrf_exempt
@require_POST
def add_feedback(request):
    try:
        data = json.loads(request.body)
        required_fields = ['submission_id', 'teacher_id', 'feedback']

        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing field: {field}'}, status=400)

        submission_ref = db.collection('Submissions').document(data['submission_id'])

        if not submission_ref.get().exists:
            return JsonResponse({'error': 'Submission not found'}, status=404)

        submission_ref.update({
            'feedback': data['feedback'],
            'feedback_given_by': data['teacher_id'],
            'feedback_given_at': firestore.SERVER_TIMESTAMP
        })

        return JsonResponse({'message': 'Feedback added successfully'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.views.decorators.http import require_GET
from django.http import JsonResponse

@csrf_exempt
@require_GET
def get_teacher_submissions(request):
    try:
        teacher_id = request.GET.get('teacher_id')
        if not teacher_id:
            return JsonResponse({'error': 'Missing teacher_id'}, status=400)

        # Step 1: Get all courses created by the teacher
        courses = db.collection('Courses').where('teacher_id', '==', teacher_id).stream()
        course_ids = [course.id for course in courses]

        if not course_ids:
            return JsonResponse({'submissions': []}, status=200)

        # Step 2: Get all assignments under those courses
        assignments = db.collection('Assignments').where('course_id', 'in', course_ids).stream()
        assignment_map = {}
        assignment_ids = []

        for assignment in assignments:
            assignment_ids.append(assignment.id)
            assignment_map[assignment.id] = assignment.to_dict().get('name', '')  # Save assignment name

        if not assignment_ids:
            return JsonResponse({'submissions': []}, status=200)

        # Step 3: Get all submissions for those assignments
        submissions = []
        for aid in assignment_ids:
            sub_docs = db.collection('Submissions').where('assignment_id', '==', aid).stream()
            for sub in sub_docs:
                submission_data = sub.to_dict()
                submission_data['submission_id'] = sub.id

                # Add assignment name
                submission_data['name'] = assignment_map.get(aid, '')

                # Fetch student enroll using student_id
                student_id = submission_data.get('student_id')
                if student_id:
                    student_ref = db.collection('Students').document(student_id).get()
                    if student_ref.exists:
                        student_data = student_ref.to_dict()
                        submission_data['enroll'] = student_data.get('enroll', '')
                    else:
                        submission_data['enroll'] = ''
                else:
                    submission_data['enroll'] = ''

                submissions.append(submission_data)

        return JsonResponse({'submissions': submissions}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

