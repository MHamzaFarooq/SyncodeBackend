from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from syncode.firebase import db

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
