"""
URL configuration for online_learning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from students.views import student_dashboard
from instructors.views import instructor_dashboard
from employees.views import dashboard
from django.contrib.auth import views as auth_views
from users.views import user_login,user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_login, name='login'), 
    path('logout/', user_logout, name='logout'),
    path('student/', include('students.urls', namespace='students')),  
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('instructor/', include('instructors.urls', namespace='instructors')),
    path('employee/dashboard/', dashboard, name='employee_dashboard'),
    path('employee/', include('employees.urls', namespace='employees')),  

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)