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
        required_fields = ['teacher_id', 'title', 'description', 'programming_language', 'level', 'status']

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


# @csrf_exempt
# @require_GET
# def get_course_by_id(request):
#     try:
#         course_id = request.GET.get('course_id')

#         if not course_id:
#             return JsonResponse({'error': 'Missing course_id parameter'}, status=400)

#         # Get the course
#         course_ref = db.collection('Courses').document(course_id)
#         course_doc = course_ref.get()

#         if not course_doc.exists:
#             return JsonResponse({'error': 'Course not found'}, status=404)

#         course_data = course_doc.to_dict()

#         # Add teacher name
#         teacher_id = course_data.get('teacher_id')
#         course_data['teacher_name'] = get_teacher_name(teacher_id) if teacher_id else 'Unknown'

#         # Get videos related to the course
#         videos_ref = db.collection('Videos').where('course_id', '==', course_id)
#         videos = [video_doc.to_dict() for video_doc in videos_ref.stream()]
        
#         # Sort videos by uploaded_at timestamp in descending order (newest first)
#         # Handle cases where uploaded_at might be empty for some videos
#         videos.sort(key=lambda x: x.get('uploaded_at', ''), reverse=False)

#         # Add sorted videos to the course data
#         course_data['videos'] = videos

#         return JsonResponse({'course': course_data}, status=200)

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_GET
def get_course_by_id(request):
    try:
        course_id = request.GET.get('course_id')

        if not course_id:
            return JsonResponse({'error': 'Missing course_id parameter'}, status=400)

        # Get the course
        course_ref = db.collection('Courses').document(course_id)
        course_doc = course_ref.get()

        if not course_doc.exists:
            return JsonResponse({'error': 'Course not found'}, status=404)

        course_data = course_doc.to_dict()

        # Add teacher name
        teacher_id = course_data.get('teacher_id')
        course_data['teacher_name'] = get_teacher_name(teacher_id) if teacher_id else 'Unknown'

        # Get videos related to the course
        videos_ref = db.collection('Videos').where('course_id', '==', course_id)
        videos = [video_doc.to_dict() for video_doc in videos_ref.stream()]
        
        # Sort videos by uploaded_at timestamp in ascending order (oldest first)
        videos.sort(key=lambda x: x.get('uploaded_at', ''), reverse=False)
        
        # Add sorted videos to the course data
        course_data['videos'] = videos

        # Get assignments related to the course
        assignments_ref = db.collection('Assignments').where('course_id', '==', course_id)
        assignments = [assignment_doc.to_dict() for assignment_doc in assignments_ref.stream()]

        # Add assignments to the course data
        course_data['assignments'] = assignments

        return JsonResponse({'course': course_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_GET
def get_teacher_courses(request):
    try:
        # Get teacher_id from the request parameters
        teacher_id = request.GET.get('teacher_id')

        if not teacher_id:
            return JsonResponse({'error': 'Missing teacher_id parameter'}, status=400)

        # Query the Courses collection to find courses associated with the teacher_id
        courses_ref = db.collection('Courses').where('teacher_id', '==', teacher_id)
        courses = []

        # Fetch the courses and add teacher name
        for doc in courses_ref.stream():
            course_data = doc.to_dict()
            teacher_name = get_teacher_name(course_data.get('teacher_id'))
            course_data['teacher_name'] = teacher_name
            courses.append(course_data)

        # Return the courses associated with the teacher
        return JsonResponse({'courses': courses}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_GET
def get_teacher_courses_and_vids(request):
    try:
        teacher_id = request.GET.get('teacher_id')

        if not teacher_id:
            return JsonResponse({'error': 'Missing teacher_id parameter'}, status=400)

        courses_ref = db.collection('Courses').where('teacher_id', '==', teacher_id)
        courses = []

        for doc in courses_ref.stream():
            course_data = doc.to_dict()
            course_id = course_data.get('course_id')

            # Add teacher name
            teacher_name = get_teacher_name(teacher_id)
            course_data['teacher_name'] = teacher_name

            # Fetch related videos with only selected fields
            videos_query = db.collection('Videos').where('course_id', '==', course_id)
            videos = []
            for video_doc in videos_query.stream():
                video_data = video_doc.to_dict()

                # Pick only specific fields
                filtered_video = {
                    'video_id': video_data.get('video_id'),
                    'name': video_data.get('name'),
                    'uploaded_at': video_data.get('uploaded_at'),
                }

                videos.append(filtered_video)

            # Attach videos list to the course
            course_data['videos'] = videos

            courses.append(course_data)

        return JsonResponse({'courses': courses}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def delete_course(request):
    try:
        data = json.loads(request.body)
        course_id = data.get('course_id')

        if not course_id:
            return JsonResponse({'error':'Missing course_id parameter'}, status=400)
        
        # Reference to the course document
        course_ref = db.collection('Courses').document(course_id)
        course_doc = course_ref.get()

        if not course_doc.exists:
            return JsonResponse({'error':'Course not found'}, status=404)
        
        # Delete associated videos
        videos_query = db.collection('Videos').where('course_id','==',course_id)
        for video_doc in videos_query.stream():
            video_doc.reference.delete()

        # Delete the course
        course_ref.delete()

        return JsonResponse({'message':f'Course {course_id} and its videos deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)