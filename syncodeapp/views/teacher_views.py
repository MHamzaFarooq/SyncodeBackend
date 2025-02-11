from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from syncode.firebase import db
from syncodeapp.utils.hashing import hash_password, verify_password

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