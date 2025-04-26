import cloudinary
import cloudinary.uploader
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from syncode.firebase import db
from decouple import config
import json

# Configuration       
cloudinary.config( 
    cloud_name = config('CLOUDINARY_CLOUD_NAME'), 
    api_key = config('CLOUDINARY_API_KEY'), 
    api_secret = config('CLOUDINARY_API_SECRET'), 
    secure=True
)


@csrf_exempt
@require_POST
def create_video(request):
    try:
        course_id = request.POST.get('course_id')
        name = request.POST.get('name')
        events_json = request.POST.get('events')
        audio_file = request.FILES.get('audio')

        if not course_id or not name or not events_json or not audio_file:
            return JsonResponse({'error':'Missing required fields'}, status=400)
        
        # Check if course exists
        course_ref = db.collection('Courses').document(course_id)
        if not course_ref.get().exists:
            return JsonResponse({'error':'Course not found'}, status=404)
        
        upload_result = cloudinary.uploader.upload(audio_file,resource_type="auto")
        audio_url = upload_result.get('secure_url')

        if not audio_url:
            return JsonResponse({'error':'Failed to upload audio to Cloudinary'})
        
        # Create a video document in Firestore
        video_ref = db.collection('Videos').document()
        video_data = {
            'video_id': video_ref.id,
            'course_id': course_id,
            'name': name,
            'events': events_json,
            'audio_url': audio_url,
            'uploaded_at': datetime.now().isoformat()
        }

        video_ref.set(video_data)
        return JsonResponse({'message': 'Video created successfully', 'video_id': video_ref.id}, status=201)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_GET
def get_video(request):
    try:
        video_id = request.GET.get('video_id')

        if not video_id:
            return JsonResponse({'error': 'Missing video_id parameter'}, status=400)

        # Fetch video document from Firestore
        video_ref = db.collection('Videos').document(video_id)
        video_doc = video_ref.get()

        if not video_doc.exists:
            return JsonResponse({'error': 'Video not found'}, status=404)

        video_data = video_doc.to_dict()
        return JsonResponse({'video': video_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def delete_video(request):
    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')

        if not video_id:
            return JsonResponse({'error': 'Missing video_id parameter'}, status=400)

        # Fetch the video document
        video_ref = db.collection('Videos').document(video_id)
        video_doc = video_ref.get()

        if not video_doc.exists:
            return JsonResponse({'error': 'Video not found'}, status=404)

        video_data = video_doc.to_dict()
        audio_url = video_data.get('audio_url')

        # Extract public_id from Cloudinary URL
        if audio_url:
            # Cloudinary URL format: https://res.cloudinary.com/<cloud_name>/video/upload/v<timestamp>/<public_id>.<ext>
            public_id = audio_url.split('/')[-1].split('.')[0]
            try:
                cloudinary.uploader.destroy(public_id, resource_type="video")
            except Exception as cloud_err:
                return JsonResponse({'error': f'Failed to delete from Cloudinary: {cloud_err}'}, status=500)

        # Delete video document from Firestore
        video_ref.delete()

        return JsonResponse({'message': 'Video deleted successfully'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
