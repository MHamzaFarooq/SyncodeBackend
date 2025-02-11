from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from syncode.firebase import db

@require_POST
def create_video(request):
    try:
        data = json.loads(request.body)
        required_fields = ['course_id', 'name', 'duration']

        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

        course_ref = db.collection('Courses').document(data['course_id'])
        if not course_ref.get().exists:
            return JsonResponse({'error': 'Course not found'}, status=404)

        video_ref = db.collection('Videos').document()
        video_data = {
            'video_id': video_ref.id,
            'course_id': data['course_id'],
            'name': data['name'],
            'duration': data['duration']
        }

        video_ref.set(video_data)
        return JsonResponse({'message': 'Video created successfully', 'video_id': video_ref.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
