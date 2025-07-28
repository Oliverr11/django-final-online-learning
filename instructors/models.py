from django.db import models
from employees.models import Employee  # optional
from users.models import CustomUser
class Instructor(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to='instructor_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='instructor_profile')

    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instructors_created'
    )
    
    def clean(self):
        # Check only if user exists
        if self.user_id and self.user.role != 'instructor':
            from django.core.exceptions import ValidationError
            raise ValidationError("User role must be 'instructor' for Student profile.")

    def save(self, *args, **kwargs):
        self.full_clean()  # triggers the clean() method
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.full_name
