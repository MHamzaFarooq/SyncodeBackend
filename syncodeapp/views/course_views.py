from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from syncode.firebase import db


def get_teacher_name(teacher_id):
    """Fetch teacher name using teacher_id from Firestore."""
    teacher_ref = db.collection('Teachers').document(teacher_id)
    teacher_doc = teacher_ref.get()

    if teacher_doc.exists:
        return teacher_doc.to_dict().get('name','Unknown')
    
    return 'Unknown'

@csrf_exempt
@require_POST
def create_course(request):
    try:
        data = json.loads(request.body)
        required_fields = ['teacher_id', 'title', 'description', 'hours', 'programming_language', 'level', 'status']

        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

        teacher_ref = db.collection('Teachers').document(data['teacher_id'])
        if not teacher_ref.get().exists:
            return JsonResponse({'error': 'Teacher not found'}, status=404)

        course_ref = db.collection('Courses').document()
        course_data = {
            'course_id': course_ref.id,
            'teacher_id': data['teacher_id'],
            'title': data['title'],
            'description': data['description'],
            'hours': data['hours'],
            'programming_language': data['programming_language'],
            'level': data['level'],
            'status': data['status']
        }

        course_ref.set(course_data)
        return JsonResponse({'message': 'Course created successfully', 'course_id': course_ref.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_GET
def get_all_courses(request):
    try:
        courses_ref = db.collection('Courses')
        courses = []

        for doc in courses_ref.stream():
            course_data = doc.to_dict()
            teacher_id = course_data.get('teacher_id',None)

            if teacher_id:
                course_data['teacher_name'] = get_teacher_name(teacher_id)
            else:
                course_data['teacher_name'] = 'Unknown'
        
            courses.append(course_data)

        return JsonResponse({'courses':courses}, status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)
    

@csrf_exempt
@require_GET
def get_available_courses(request):
    try:
        courses_ref = db.collection('Courses').where('status','==','available')
        courses = []

        for doc in courses_ref.stream():
            course_data = doc.to_dict()
            teacher_id = course_data.get('teacher_id',None)
            
            if teacher_id:
                course_data['teacher_name'] = get_teacher_name(teacher_id)
            else:
                course_data['teacher_name'] = 'Unknown'

            courses.append(course_data)

        return JsonResponse({'courses':courses}, status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)
    


@csrf_exempt
@require_GET
def get_upcoming_courses(request):
    try:
        courses_ref = db.collection('Courses').where('status','==','upcoming')
        courses = []

        for doc in courses_ref.stream():
            course_data = doc.to_dict()

            teacher_id = course_data.get('teacher_id',None)
            
            if teacher_id:
                course_data['teacher_name'] = get_teacher_name(teacher_id)
            else:
                course_data['teacher_name'] = 'Unknown'

            courses.append(course_data)

        return JsonResponse({'courses':courses}, status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)