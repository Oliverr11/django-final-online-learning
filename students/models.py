from django.db import models
from employees.models import Employee
from users.models import CustomUser
class Student (models.Model):
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=12)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')



    def clean(self):
        if self.user_id and self.user.role != 'student':
            from django.core.exceptions import ValidationError
            raise ValidationError("User role must be 'student' for Student profile.")
    
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.full_name