# enrollments/forms.py
from django import forms
from .models import Enrollment
from students.models  import Student
class EnrollmentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )
    class Meta:
        model = Enrollment
        fields = ['student', 'course']
        widgets = {

            'course': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        }
