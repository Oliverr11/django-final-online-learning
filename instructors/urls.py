from django.urls import path
from . import views
app_name = 'instructors' 

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('courses/manage/', views.manage_courses, name='manage_courses'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),


    path('courses/<int:course_id>/lessons/create/', views.lesson_create, name='lesson_create'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),

    # path('lessons/<int:lesson_id>/assignments/', views.assignment_list, name='assignment_list'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/assignments/create/', views.assignment_create, name='assignment_create'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/assignments/<int:assignment_id>/delete/', views.assignment_delete,name='assignment_delete' ),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/assignments/<int:assignment_id>/',views.assignment_detail,name='assignment_detail'),

    path('assignments/<int:assignment_id>/submissions/', views.assignment_submissions_review, name='assignment_submissions_review'),
]
