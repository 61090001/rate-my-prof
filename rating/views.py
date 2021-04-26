from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.db.models import Avg, Count, Case, When, Q
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Course, Professor, Rating, University

# Create your views here.

@csrf_exempt
def createUniversity(request):
    if request.method != "POST":
        raise Http404()
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body)
        name = data['name']

        university = University(name=name)
        university.save()

        return HttpResponse(json.dumps({'ok':True,'id':university.id}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))

@csrf_exempt
def createProfessor(request):
    if request.method != "POST":
        raise Http404()
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body)
        name = data['name']
        university_id = data['university_id']

        if isinstance(university_id, int):
            university = University.objects.get(id=university_id)
        elif isinstance(university_id, str):
            university = University.objects.get(name=university_id)
        else:
            university = None

        professor = Professor(name=name, university=university)
        professor.save()

        return HttpResponse(json.dumps({'ok':True,'id':professor.id}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))

@csrf_exempt
def createCourse(request):
    if request.method != "POST":
        raise Http404()
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body)
        code = data['code']
        name = data['name']
        professor_id = data['professor_id']
        university_id = data['university_id']

        if isinstance(professor_id, int):
            professor = Professor.objects.get(id=professor_id)
        elif isinstance(professor_id, str):
            professor = Professor.objects.get(name=professor_id)
        else:
            professor = None
        
        if isinstance(university_id, int):
            university = University.objects.get(id=university_id)
        elif isinstance(university_id, str):
            university = University.objects.get(name=university_id)
        else:
            university = None

        course = Course(code=code, name=name, professor=professor, university=university)
        course.save()

        return HttpResponse(json.dumps({'ok':True,'id':course.id}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))

@csrf_exempt
def createRating(request):
    if request.method != "POST":
        raise Http404()
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body)
        rating = data['rating']
        difficulty = data['difficulty']
        takeagain = data['takeagain']
        credit = data['credit']
        textbook = data['textbook']
        attendance = data['attendance']
        grade = data['grade']
        comments = data['comments']
        course_code = data['course_code']

        course = Course.objects.get(code=course_code)

        rating = Rating(rating=rating, difficulty=difficulty, takeagain=takeagain, credit=credit, textbook=textbook, attendance=attendance, grade=grade, comments=comments, course=course)
        rating.save()

        return HttpResponse(json.dumps({'ok':True,'id':rating.id}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))

@csrf_exempt
def getProfessors(request):
    if request.method != "GET":
        raise Http404()
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        if offset < 0:
            offset = 0
        if limit < 0:
            limit = 20
        if limit > 50:
            limit = 50

        professors = []

        metrics = Rating.objects.prefetch_related('course').prefetch_related('course__professor').values('course__professor__course__professor__name', 'course__professor__course__professor__id').annotate(
            rating_avg=Avg('rating'),
            difficulty_avg=Avg('difficulty'),
            takeagain_ratio=1.0*Count(Case(When(takeagain=True, then=1)))/Count('takeagain'),
        )

        exclude_id = []
        for professor in metrics:
            exclude_id.append(professor['course__professor__course__professor__id'])
            if offset >= len(metrics) or offset > 0:
                offset -= 1
                continue
            professors.append({
                'id':professor['course__professor__course__professor__id'],
                'name':professor['course__professor__course__professor__name'],
                'rating':professor['rating_avg'],
                'difficulty':professor['difficulty_avg'],
                'takeagain':professor['takeagain_ratio'],
            })
            limit -= 1
            if limit == 0:
                break

        if limit > 0:
            for professor in Professor.objects.exclude(id__in=exclude_id)[offset:offset+limit]:
                professors.append({
                    'id':professor.id,
                    'name':professor.name,
                    'rating':0.0,
                    'difficulty':0.0,
                    'takeagain':0.0,
                })

        return HttpResponse(json.dumps({'ok':True,'professors':professors}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))

@csrf_exempt
def getCourseCode(request, professor_id):
    if request.method != "GET":
        raise Http404()
    try:
        codes = []
        for course in Course.objects.select_related('professor').filter(professor__id=professor_id):
            codes.append(course.code)

        return HttpResponse(json.dumps({'ok':True,'codes':codes}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))

@csrf_exempt
def getRatings(request, professor_id):
    if request.method != "GET":
        raise Http404()
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        if offset < 0:
            offset = 0
        if limit < 0:
            limit = 20
        if limit > 50:
            limit = 50

        ratings = []

        professor = Professor.objects.get(id=professor_id)
        for rating in Rating.objects.select_related('course').filter(course__professor=professor)[offset:offset+limit]:
            ratings.append({
                "id":rating.id,
                "code":rating.course.code,
                "name":rating.course.name,
                "rating":rating.rating,
                "difficulty":rating.difficulty,
                "takeagain":rating.takeagain,
                "credit":rating.credit,
                "textbook":rating.textbook,
                "attendance":rating.attendance,
                "grade":rating.grade,
                "comments":rating.comments,
            })

        return HttpResponse(json.dumps({'ok':True,'ratings':ratings}))

    except Exception as e:
        return HttpResponse(json.dumps({'ok':False,'err':str(e)}))
