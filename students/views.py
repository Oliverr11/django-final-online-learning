from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect,HttpResponse,HttpResponseRedirect
from django.http import HttpResponseForbidden,HttpResponseBadRequest
from enrollments.models import LessonProgress
from instructors.models import Instructor
from django.db.models import Q
from courses.forms import AssignmentSubmissionForm

from courses.models import Course,Lesson,Category,Tag,Assignment, AssignmentSubmission
from enrollments.models import Enrollment
from users.decorators import role_required
from .models import Student
    
from django.views.decorators.http import require_http_methods
from courses.forms import AssignmentSubmissionForm
from courses.models import Assignment, AssignmentSubmission
@role_required(['student'])
def student_dashboard(request):

    student = request.user.student_profile
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    courses_with_progress = []
    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = Lesson.objects.filter(course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            student=student, 
            lesson__course=course
        ).count()

        courses_with_progress.append({
            'course': course,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
        })

    upcoming_assignments = [] 
    grades = [] 

    return render(request, 'students/student_dashboard.html', {
        'student': student,
        'courses_with_progress': courses_with_progress,
        'upcoming_assignments': upcoming_assignments,
        'grades': grades,
    }) 


@role_required(['student'])
@require_http_methods(["GET", "POST"])
def lesson_detail(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    student = request.user.student_profile
    enrollment = get_object_or_404(Enrollment, student=student, course_id=course_id)
    completed = LessonProgress.objects.filter(student=student, lesson=lesson).exists()

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        if assignment_id:
            assignment = get_object_or_404(Assignment, id=assignment_id, lesson=lesson)
            submission, created = AssignmentSubmission.objects.get_or_create(
                assignment=assignment,
                student=student
            )
            form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
            if form.is_valid():
                form.save()
                return redirect('students:lesson_detail', course_id=course_id, lesson_id=lesson_id)
        else:
            LessonProgress.objects.get_or_create(student=student, lesson=lesson)
            return redirect('students:lesson_detail', course_id=course_id, lesson_id=lesson_id)
    else:
        form = AssignmentSubmissionForm()

    assignments = lesson.assignments.all()
    for assignment in assignments:
        assignment.submission = AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=student
        ).first()

    return render(request, 'students/lesson_detail.html', {
        'lesson': lesson,
        'course': lesson.course,
        'completed': completed,
        'assignments': assignments,
        'form': form,
    })
@role_required(['student'])
  
def course_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        student = request.user.student_profile
    except:
        return HttpResponseForbidden("Only students can view course lessons.")

    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        return HttpResponseForbidden("You are not enrolled in this course.")
    lessons = Lesson.objects.filter(course=course)
    completed_lessons = LessonProgress.objects.filter(
        student=student, lesson__in=lessons
    ).values_list('lesson_id', flat=True)
    completed_lessons_set = set(completed_lessons)

    context = {
        'course': course,
        'lessons': lessons,
        'completed_lessons': completed_lessons_set,
        'enrollment': enrollment,
    }
    return render(request, 'students/course_lessons.html', context)
@role_required(['student'])

def course_details_public(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('sequence')

    is_enrolled = False
    first_lesson_id = None 
    submissions_dict = {}

    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        is_enrolled = Enrollment.objects.filter(student=student, course=course).exists()
        
        if is_enrolled and lessons.exists():
            first_lesson_id = lessons.first().id

            assignments = Assignment.objects.filter(lesson__in=lessons)
            submissions = AssignmentSubmission.objects.filter(student=student, assignment__in=assignments)

            submissions_dict = {sub.assignment_id: sub for sub in submissions}

    context = {
        'course': course,
        'lessons': lessons, 
        'is_enrolled': is_enrolled,
        'first_lesson_id': first_lesson_id,
        'submissions_dict': submissions_dict,
    }
    return render(request, 'students/course_details_public.html', context)
@role_required(['student'])

def enroll_courses(request):
    student = request.user.student_profile
    
    all_courses = Course.objects.all()

    search_query = request.GET.get('q')
    category_name = request.GET.get('category')
    instructor_id = request.GET.get('instructor')
    tag_name = request.GET.get('tag') 
    if search_query:
        all_courses = all_courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_name:
        all_courses = all_courses.filter(category__name=category_name)

    if instructor_id:
        if instructor_id.isdigit():
            all_courses = all_courses.filter(instructor__id=instructor_id)
            
    if tag_name: 
        all_courses = all_courses.filter(tags__name=tag_name)

    categories = Category.objects.all()
    instructors = Instructor.objects.all()
    tags = Tag.objects.all() 

    message = None

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        enrolled_courses_ids = set(
            Enrollment.objects.filter(student=student).values_list('course_id', flat=True)
        )

        if course.id in enrolled_courses_ids:
            message = "You are already enrolled in this course."
        else:
            Enrollment.objects.create(student=student, course=course)
            message = "Enrollment successful!"
        redirect_url = request.path_info
        query_params = request.GET.urlencode()
        if query_params:
            redirect_url += '?' + query_params
        
        if message:
            if '?' in redirect_url:
                redirect_url += '&enroll_message=' + message.replace(' ', '%20')
            else:
                redirect_url += '?enroll_message=' + message.replace(' ', '%20')
                
        return redirect(redirect_url)

    enrolled_courses_ids = set(
        Enrollment.objects.filter(student=student).values_list('course_id', flat=True)
    )

    message = request.GET.get('enroll_message')

    return render(request, 'students/enroll_courses.html', {
        'courses': all_courses,
        'enrolled_courses': enrolled_courses_ids,
        'categories': categories,
        'instructors': instructors,
        'tags': tags,
        'message': message,
    })
    
    
@role_required(['student'])
    
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    student = get_object_or_404(Student, user=request.user)
    submission, created = AssignmentSubmission.objects.get_or_create(
        assignment=assignment,
        student=student
    )

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('students:dashboard') 
    else:
        form = AssignmentSubmissionForm(instance=submission)

    return render(request, 'students/assignment_submit.html', {
        'assignment': assignment,
        'form': form,
        'submission': submission,
    })