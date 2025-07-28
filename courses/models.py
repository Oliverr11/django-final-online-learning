from django.db import models
from instructors.models import Instructor
from employees.models import Employee
from students.models import Student 

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True,  related_name='courses' )
    created_by_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True)  

    def __str__(self):
        return self.title
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)

    document = models.FileField(upload_to='lesson_docs/', blank=True, null=True)
    sequence = models.PositiveIntegerField(help_text="Order of this lesson in the course")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return f"{self.course.title} - Lesson {self.sequence}: {self.title}"
    
    
    
class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.PositiveIntegerField()
    file = models.FileField(upload_to='assignment_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    uploaded_file = models.FileField(upload_to='assignment_submissions/', null=True, blank=True)

    score = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"