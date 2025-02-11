from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from syncode.firebase import db

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


