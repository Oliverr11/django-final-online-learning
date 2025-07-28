from django.db import models
from users.models import CustomUser
class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')

    profile_image = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)


    def clean(self):
        from django.core.exceptions import ValidationError
        if self.user.role != 'employee':
            raise ValidationError("User role must be 'employee' for Employee profile.")
    def __str__(self):
        return self.name
