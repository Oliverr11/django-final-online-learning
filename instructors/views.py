from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from courses.models import Course, Lesson, Tag, Category ,Assignment,AssignmentSubmission
from enrollments.models import Enrollment
from instructors.models import Instructor
from courses.forms import CourseForm
from courses.forms import LessonForm,AssignmentForm,AssignmentSubmissionForm
from django.contrib import messages
from django.db.models import Q 
from django.views.decorators.http import require_http_methods
from users.decorators import role_required


@role_required(['instructor'])
def instructor_dashboard(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    courses = Course.objects.filter(instructor=instructor)

    course_data = []
    total_enrollments = 0

    for course in courses:
        enrollments = Enrollment.objects.filter(course=course)


        course_data.append({
            "course": course,
            "enrollment_count": enrollments.count(),
        })

        total_enrollments += enrollments.count()

    context = {
        "instructor": instructor,
        "course_data": course_data,
        "total_courses": courses.count(),
        "total_enrollments": total_enrollments,
    }
    return render(request, 'instructors/instructor_dashboard.html', context)

@role_required(['instructor'])
def manage_courses(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    courses = Course.objects.filter(instructor=instructor).order_by('-created_at')
    search_query = request.GET.get('q')
    category_id = request.GET.get('category')
    tag_name = request.GET.get('tag') 

    if search_query:
        courses = courses.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    if category_id:
        courses = courses.filter(category__id=category_id)

    if tag_name:
        courses = courses.filter(tags__name__iexact=tag_name)
    categories = Category.objects.filter(course__instructor=instructor).distinct().order_by('name')
    tags = Tag.objects.filter(course__instructor=instructor).distinct().order_by('name')

    context = {
        'courses': courses,
        'categories': categories,
        'tags': tags, 
        'search_query': search_query,
        'selected_category': category_id,
        'selected_tag': tag_name, 
    }
    return render(request, 'instructors/manage_courses.html', context)

@role_required(['instructor'])
def course_create(request):
    instructor = get_object_or_404(Instructor, user=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = instructor
            course.save()
            form.save_m2m()
            messages.success(request, f'Course "{course.title}" created successfully.')
            return redirect('instructors:manage_courses')
    else:
        form = CourseForm()

    return render(request, 'instructors/course_form.html', {
        "form": form,
        "title": "Create Course"
    })
    
@role_required(['instructor'])
def course_edit(request, course_id):
    instructor = get_object_or_404(Instructor, user=request.user)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully.')
            return redirect('instructors:manage_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'instructors/course_form.html', {
        'form': form,
        'title': f'Edit Course: {course.title}',
    })
    
@role_required(['instructor'])
def course_delete(request, course_id):
    instructor = get_object_or_404(Instructor, user=request.user)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)

    if request.method == "POST":
        course.delete()
        messages.success(request, f'Course "{course.title}" deleted successfully.')
        return redirect('instructors:manage_courses')

    return render(request, 'instructors/course_confirm_delete.html', {'course': course})

@role_required(['instructor'])
def course_detail(request, course_id):
    instructor = get_object_or_404(Instructor, user=request.user)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)

    lessons = course.lessons.all().order_by('sequence')
    
    enrolled_students = Enrollment.objects.filter(course=course).select_related('student').order_by('student__full_name')

    context = {
        'course': course,
        'lessons': lessons,
        'enrolled_students': enrolled_students,
    }
    return render(request, 'instructors/course_detail.html', context)


@role_required(['instructor'])
def lesson_detail(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    assignments = Assignment.objects.filter(lesson=lesson)
    
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.lesson = lesson
            assignment.save()
            return redirect('instructors:lesson_detail', course_id=course_id, lesson_id=lesson_id)
    else:
        form = AssignmentForm()

    context = {
        'lesson': lesson,
        'course': lesson.course,
        'assignments': assignments,
        'form': form,
    }
    return render(request, 'instructors/lesson_detail.html', context)


@role_required(['instructor'])

def lesson_create(request, course_id):
    instructor = get_object_or_404(Instructor, user=request.user)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" added successfully to {course.title}.')
            return redirect('instructors:lesson_detail', course_id=course.id, lesson_id=lesson.id)
        else:
            messages.error(request, 'There was an error creating the lesson. Please check your input.')
    else:
        last_lesson = course.lessons.order_by('-sequence').first()
        initial_sequence = (last_lesson.sequence + 1) if last_lesson else 1
        form = LessonForm(initial={'sequence': initial_sequence})
        
    context = {
        'form': form,
        'course': course,
        'is_new_lesson': True
    }
    return render(request, 'instructors/lesson_form.html', context)

@role_required(['instructor'])
def lesson_edit(request, course_id, lesson_id):
    instructor = get_object_or_404(Instructor, user=request.user)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lesson "{lesson.title}" updated successfully.')
            return redirect('instructors:lesson_detail', course_id=course.id, lesson_id=lesson.id)
        else:
            messages.error(request, 'There was an error updating the lesson. Please check your input.')
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'instructors/lesson_form.html', {'form': form, 'course': course, 'lesson': lesson})

@role_required(['instructor'])
def lesson_delete(request, course_id, lesson_id):
    instructor = get_object_or_404(Instructor, user=request.user)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, f'Lesson "{lesson.title}" deleted successfully.')
        return redirect('instructors:course_detail', course_id=course.id)
    
    return render(request, 'instructors/lesson_confirm_delete.html', {'course': course, 'lesson': lesson})
@role_required(['instructor'])

def assignment_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor__user=request.user)
    assignments = lesson.assignments.all()
    return render(request, 'instructors/assignment_list.html', {
        'lesson': lesson,
        'assignments': assignments,
    })
@role_required(['instructor'])

def assignment_create(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id, course__instructor__user=request.user)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)  
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.lesson = lesson
            assignment.save()
            return redirect('instructors:lesson_detail', course_id=course_id, lesson_id=lesson_id)
    else:
        form = AssignmentForm()

    return render(request, 'instructors/assignment_form.html', {
        'form': form,
        'lesson': lesson,
    })

    
    
@role_required(['instructor'])
    
def assignment_delete(request, course_id, lesson_id, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        lesson_id=lesson_id,
        lesson__course_id=course_id,
        lesson__course__instructor__user=request.user,
    )

    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Assignment deleted successfully.")
        return redirect('instructors:lesson_detail', course_id=course_id, lesson_id=lesson_id)

    return render(request, 'instructors/assignment_confirm_delete.html', {
        'assignment': assignment,
        'course_id': course_id,
        'lesson_id': lesson_id,
    })
@role_required(['instructor'])
    
def assignment_detail(request, course_id, lesson_id, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, lesson__id=lesson_id, lesson__course__id=course_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')

    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        score = request.POST.get('score')
        feedback = request.POST.get('feedback')

        submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment=assignment)
        if score.isdigit():
            submission.score = int(score)
            submission.feedback = feedback
            submission.save()
            return redirect('instructors:assignment_detail', course_id=course_id, lesson_id=lesson_id, assignment_id=assignment_id)

    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'instructors/assignment_detail.html', context)
    
@role_required(['instructor'])
    
def assignment_submissions_review(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')

    return render(request, 'instructors/assignment_submissions_review.html', {
        'assignment': assignment,
        'submissions': submissions,
    })
    
