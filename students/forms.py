# students/forms.py

from django import forms
from students.models import Student
from users.models import CustomUser
from django.core.exceptions import ValidationError

class StudentForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50',
            'placeholder': 'Enter username for login'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50',
            'placeholder': 'Leave blank to keep current password'
        }),
        required=False
    )
    class Meta:
        model = Student
        fields = ['full_name','email', 'phone', 'address', 'gender', 'date_of_birth', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 h-28 resize-y text-gray-800 bg-gray-50', 'placeholder': 'Street Address, City, State/Province, Postal Code'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 text-gray-800 bg-gray-50', 'placeholder': 'YYYY-MM-DD'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'w-full text-gray-800 file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-base file:font-semibold file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200 transition duration-300 cursor-pointer'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].required = False
            self.fields['password'].widget.attrs['placeholder'] = 'Leave blank to keep current password'
        else:
            self.fields['password'].required = True
            self.fields['password'].widget.attrs['placeholder'] = 'Enter a strong password'

    def clean_username(self):
        username = self.cleaned_data['username']
        query = CustomUser.objects.filter(username=username)

        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.user.pk)

        if query.exists():
            raise ValidationError("This username is already taken. Please choose a different one.")
        return username

    def save(self, commit=True):
        if self.instance and self.instance.pk:
            user = self.instance.user
        else:
            user = CustomUser()
            user.role = 'student' 
        user.username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        user.save() 
        student = super().save(commit=False)
        student.user = user 

        if commit: 
            student.save()

        return student