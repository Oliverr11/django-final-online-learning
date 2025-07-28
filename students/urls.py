from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('courses/<int:course_id>/lessons/', views.course_lessons, name='course_lessons'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('enroll/', views.enroll_courses, name='enroll_courses'),
    path('courses/<int:course_id>/details/', views.course_details_public, name='course_details_public'),

    # path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),

    # path('assignments/<int:assignment_id>/submit/', views.assignment_submit, name='assignment_submit'),
    # path('assignments/<int:assignment_id>/submission/', views.assignment_submission_detail, name='assignment_submission_detail'),
]
