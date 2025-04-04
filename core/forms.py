from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobListing

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'interests', 'fields', 'experience', 'job_preferences')
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'interests': forms.TextInput(attrs={'class': 'form-control'}),
            'fields': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Select(attrs={'class': 'form-control'}),
            'job_preferences': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'company_website', 'company_description', 'company_logo',
                 'company_size', 'industry', 'location')
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ('title', 'description', 'interests', 'fields', 'experience', 'job_preferences')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'interests': forms.TextInput(attrs={'class': 'form-control'}),
            'fields': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Select(attrs={'class': 'form-control'}),
            'job_preferences': forms.TextInput(attrs={'class': 'form-control'}),
        }