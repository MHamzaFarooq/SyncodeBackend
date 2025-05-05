from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from syncode.firebase import db, firestore

@csrf_exempt
@require_POST
def add_assignment(request):
    try:
        data = json.loads(request.body)
        required_fields = ['name','code','course_id']
    
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error':f'Missing required field: {field}'})

        course_ref = db.collection('Courses').document(data['course_id'])
        if not course_ref.get().exists:
            return JsonResponse({'error':'Course not found'}, status=404) 

        assignment_ref = db.collection('Assignments').document()
        assignment_data = {
            'assignment_id': assignment_ref.id,
            'name': data['name'],
            'code': data['code'],
            'course_id': data['course_id']
        }    

        assignment_ref.set(assignment_data)

        return JsonResponse({'message':'Assignment created successfully','assignment_id':assignment_ref.id}, status=201)

    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500) 
    

@csrf_exempt
@require_GET
def get_assignment(request):
    try:
        assignment_id = request.GET.get('assignment_id')
        assignment_ref = db.collection('Assignments').document(assignment_id)
        assignment = assignment_ref.get()

        if not assignment.exists:
            return JsonResponse({'error':'Assignment not found'}, status=404)
        
        return JsonResponse(assignment.to_dict(),status=200)
    
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)

    
@csrf_exempt
@require_GET
def get_assignments_by_course(request):
    try:
        course_id = request.GET.get('course_id')
        # Query assignments where course_id matches
        assignments_query = db.collection('Assignments').where('course_id', '==', course_id).stream()
        
        assignments = []
        for assignment in assignments_query:
            assignments.append(assignment.to_dict())

        return JsonResponse({'assignments': assignments}, status=200, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def submit_assignment(request):
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        student_id = data.get('student_id')
        code = data.get('code') 

        if not all([assignment_id, student_id, code]):
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        # Check if submission already exists
        submissions_ref = db.collection('Submissions')
        existing_query = submissions_ref \
            .where('assignment_id', '==', assignment_id) \
            .where('student_id', '==', student_id) \
            .limit(1) \
            .stream()

        if any(existing_query):
            return JsonResponse({'error': 'Assignment already submitted by this student.'}, status=409)

        # Proceed to save submission
        submission_ref = submissions_ref.document()
        submission_data = {
            'submission_id': submission_ref.id,
            'assignment_id': assignment_id,
            'student_id': student_id,
            'code': code,
            'submitted_at': firestore.SERVER_TIMESTAMP,
            'feedback': '',  # Initially empty
        }

        submission_ref.set(submission_data)
        return JsonResponse({'message': 'Assignment submitted successfully.'}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_GET
def get_assignment_status(request):
    try:
        assignment_id = request.GET.get('assignment_id')
        student_id = request.GET.get('student_id')

        # Query the top-level Submissions collection
        submissions = db.collection('Submissions')\
            .where('assignment_id', '==', assignment_id)\
            .where('student_id', '==', student_id)\
            .limit(1).get()

        is_submitted = len(submissions) > 0

        return JsonResponse({'submitted': is_submitted}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

