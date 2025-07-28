from django.shortcuts import render, redirect, get_object_or_404
from students.models import Student
from students.forms import StudentForm
from instructors.models import Instructor
from instructors.forms import InstructorForm
from django.core.exceptions import ValidationError
from courses.forms import CourseForm,TagForm,CategoryForm,LessonForm
from courses.models import Course,Category,Tag,Lesson
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from users.models import CustomUser
from .models import Employee
from enrollments.models import Enrollment
from enrollments.forms import EnrollmentForm
from django.contrib import messages
from django.db.models import Q

@role_required(['employee'])
def dashboard(request):
    employee_name = Employee.objects.get(user=request.user)
    student_count = Student.objects.count()
    instructor_count = Instructor.objects.count()
    course_count = Course.objects.count()
    enrollment_count = Enrollment.objects.count()

    context = {
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'employee_name': employee_name,
        'enrollment_count': enrollment_count,

        
    }
    return render(request, 'employees/employee_dashboard.html',  context)

# --- Students Management ---
@role_required(['employee'])
def student_list(request):
    students = Student.objects.all()
    return render(request, 'employees/students/student_list.html', {'students': students})


@role_required(['employee'])
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False) 
            student.created_by = Employee.objects.get(user=request.user)
            student.created_at = timezone.now()
            student.save()
            messages.success(request, f"Student '{student.full_name}' added successfully!")
            return redirect('employees:student_list')
        else:
            messages.error(request, "Please correct the errors below.") 
    else:
        form = StudentForm()
    return render(request, 'employees/students/student_form.html', {'form': form})

@role_required(['employee'])
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = student.user 

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save() 
            messages.success(request, f"Student '{student.full_name}' updated successfully!")
            return redirect('employees:student_list')
    else:
        form = StudentForm(instance=student)

    return render(request, 'employees/students/student_form.html', {'form': form, 'student': student})


@role_required(['employee'])
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')
    context = {
            'student': student,
            'enrolled_courses': enrolled_courses,
        }
    return render(request, 'employees/students/student_detail.html', context)


@role_required(['employee'])
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        user = student.user
        student.delete() 
        user.delete()     
        return redirect('employees:student_list')

    return render(request, 'employees/students/student_confirm_delete.html', {'student': student})


# --- Instructors Management ---
@role_required(['employee'])
def instructor_list(request):
    instructors = Instructor.objects.all()
    return render(request, 'employees/instructors/instructor_list.html', {'instructors': instructors})

@role_required(['employee'])
def instructor_add(request):
    if request.method == 'POST':
        form = InstructorForm(request.POST, request.FILES)
        if form.is_valid():
            instructor = form.save(commit=False)
            instructor.created_by = Employee.objects.get(user=request.user) 
            instructor.created_at = timezone.now() 
            instructor.save()
            messages.success(request, f"Instructor '{instructor.full_name}' added successfully!")
            return redirect('employees:instructor_list')
        else:
            messages.error(request, "Please correct the errors below.") 
    else:
        form = InstructorForm()
    return render(request, 'employees/instructors/instructor_form.html', {'form': form})

@role_required(['employee'])
def instructor_detail(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    courses = instructor.courses.all() 
    return render(request, 'employees/instructors/instructor_detail.html', {'instructor': instructor,'courses': courses})

@role_required(['employee'])
def instructor_edit(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        form = InstructorForm(request.POST, request.FILES, instance=instructor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Instructor '{instructor.full_name}' updated successfully!")
            return redirect('employees:instructor_list')
    else:
        form = InstructorForm(instance=instructor)
    return render(request, 'employees/instructors/instructor_form.html', {'form': form, 'instructor': instructor})

@role_required(['employee'])
def instructor_delete(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    courses = instructor.courses.all() 

    if request.method == 'POST':
        user = instructor.user
        user.delete()  
        return redirect('employees:instructor_list')
    return render(request, 'employees/instructors/instructor_confirm_delete.html', {'instructor': instructor,'courses':courses})

# --- Categories Management ---
@role_required(['employee'])
def category_list(request):
    categories = Category.objects.all()
    return render(request, "employees/categories/category_list.html", {"categories": categories})

@role_required(['employee'])
def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("employees:category_list")
    return render(request, "employees/categories/category_form.html", {
        "form": form,
        "title": "Add Category"
    })
@role_required(['employee'])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect("employees:category_list")
    return render(request, "employees/categories/category_form.html", {
        "form": form,
        "title": "Edit Category"
    })

@role_required(['employee'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect("employees:category_list")
    return render(request, "employees/categories/category_confirm_delete.html", {
        "category": category
    })

# --- Tags Management ---
@role_required(['employee'])
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, "employees/tags/tag_list.html", {"tags": tags})
@role_required(['employee'])
def tag_add(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag added successfully.")
            return redirect('employees:tag_list')
    else:
        form = TagForm()
    return render(request, 'employees/tags/tag_form.html', {'form': form, 'title': 'Add Tag'})

@role_required(['employee'])
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag updated successfully.")
            return redirect('employees:tag_list')
    else:
        form = TagForm(instance=tag)
    return render(request, 'employees/tags/tag_form.html', {'form': form, 'title': 'Edit Tag'})

@role_required(['employee'])
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, "Tag deleted successfully.")
        return redirect('employees:tag_list')
    return render(request, 'employees/tags/tag_confirm_delete.html', {'tag': tag})
# --- Courses Management ---
@role_required(['employee'])
def course_list(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    tag_id = request.GET.get("tag")
    instructor_id = request.GET.get("instructor")

    courses = Course.objects.select_related("category", "instructor").prefetch_related("tags")

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(instructor__full_name__icontains=query)
        )

    if category_id:
        courses = courses.filter(category__id=category_id)

    if tag_id:
        courses = courses.filter(tags__id=tag_id)

    if instructor_id:
        courses = courses.filter(instructor__id=instructor_id)

    courses = courses.order_by("title") 

    return render(request, "employees/courses/course_list.html", {
        "courses": courses,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "instructors": Instructor.objects.all(),
        "selected_category": category_id,
        "selected_tag": tag_id,
        "selected_instructor": instructor_id,
        "query": query,
    })

@role_required(['employee'])
def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by_employee = Employee.objects.get(user=request.user)
            course.save()
            form.save_m2m()  
            return redirect('employees:course_list')
    else:
        form = CourseForm()
    return render(request, 'employees/courses/course_form.html', {'form': form})

@role_required(['employee'])
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('employees:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'employees/courses/course_form.html', {'form': form})

@role_required(['employee'])
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('employees:course_list')
    return render(request, 'employees/courses/course_confirm_delete.html', {'course': course})

@role_required(['employee'])  
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'employees/courses/course_detail.html', {'course': course})
@role_required(['employee'])  
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect('employees:course_detail', pk=course.id)
    else:
        form = LessonForm()
    return render(request, 'employees/lessons/lesson_form.html', {'form': form, 'course': course})
@role_required(['employee'])  
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.course.id

    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully.')
        return redirect('employees:course_detail', pk=course_id)

    return render(request, 'employees/lessons/lesson_confirm_delete.html', {'lesson': lesson})
@role_required(['employee'])  
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course  

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('employees:course_detail', pk=course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'employees/lessons/lesson_form.html', {
        'form': form,
        'lesson': lesson,
        'course': course,  
    })
@role_required(['employee'])  

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'employees/lessons/lesson_detail.html', {'lesson': lesson})

@role_required(['employee'])
def enrollment_list(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    tag_id = request.GET.get("tag")
    instructor_id = request.GET.get("instructor")

    enrollments = Enrollment.objects.select_related(
        "student", "course", "course__instructor", "course__category"
    ).prefetch_related("course__tags")

    if query:
        enrollments = enrollments.filter(
            Q(student__full_name__icontains=query) |
            Q(course__title__icontains=query) |
            Q(course__instructor__full_name__icontains=query)
        )
    
    if category_id:
        enrollments = enrollments.filter(course__category__id=category_id)
    
    if tag_id:
        enrollments = enrollments.filter(course__tags__id=tag_id)
    
    if instructor_id:
        enrollments = enrollments.filter(course__instructor__id=instructor_id)

    enrollments = enrollments.order_by("-enrolled_at")

    return render(request, "employees/enrollments/enrollment_list.html", {
        "enrollments": enrollments,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "instructors": Instructor.objects.all(),
        "selected_category": category_id,
        "selected_tag": tag_id,
        "selected_instructor": instructor_id,
        "query": query
    })


@role_required(['employee'])  
def enrollment_add(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Student enrolled successfully!")
                return redirect('employees:enrollment_list')
            except:
                messages.error(request, "This student is already enrolled in that course.")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EnrollmentForm()

    return render(request, 'employees/enrollments/enrollment_form.html', {'form': form})

@role_required(['employee'])
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    return render(request, 'employees/enrollments/enrollment_detail.html', {'enrollment': enrollment})

@role_required(['employee'])
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)

    if request.method == 'POST':
        enrollment.delete()
        return redirect('employees:enrollment_list')

    return render(request, 'employees/enrollments/enrollment_confirm_delete.html', {'enrollment': enrollment})

@role_required(['employee'])
def enrollment_edit(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            return redirect('employees:enrollment_detail', pk=pk)
    else:
        form = EnrollmentForm(instance=enrollment)

    return render(request, 'employees/enrollments/enrollment_form.html', {
        'form': form,
        'enrollment': enrollment,
    })