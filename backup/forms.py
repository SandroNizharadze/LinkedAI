from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobListing
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import UploadedFile

class UserRegistrationForm(forms.Form):
    """Form for user registration that includes all required user fields."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    
    # Add profile fields - all optional
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    interests = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., AI, web development, cybersecurity'
        })
    )
    fields = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., software engineering, data science'
        })
    )
    experience = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select experience level'),
            ('entry-level', 'Entry Level'),
            ('junior', 'Junior'),
            ('mid-level', 'Mid-Level'),
            ('senior', 'Senior'),
            ('lead', 'Lead/Principal'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_preferences = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., remote, full-time, startup'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        # Only validate if a new file is being uploaded
        if profile_picture and isinstance(profile_picture, UploadedFile):
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            if not profile_picture.content_type.startswith('image/'):
                raise forms.ValidationError("File is not an image")
        return profile_picture

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'interests', 'fields', 'experience', 'job_preferences']
        widgets = {
            'interests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., AI, web development, cybersecurity'
            }),
            'fields': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., software engineering, data science'
            }),
            'experience': forms.Select(attrs={'class': 'form-control'}),
            'job_preferences': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., remote, full-time, startup'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        # Only validate if a new file is being uploaded
        if profile_picture and isinstance(profile_picture, UploadedFile):
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            if not profile_picture.content_type.startswith('image/'):
                raise forms.ValidationError("File is not an image")
        return profile_picture

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'company_website', 'company_description', 'company_logo',
                 'company_size', 'industry', 'location')
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company name'
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your company...'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., Technology, Healthcare, Finance'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
        }

    def clean_company_logo(self):
        company_logo = self.cleaned_data.get('company_logo')
        # Only validate if a new file is being uploaded
        if company_logo and isinstance(company_logo, UploadedFile):
            if company_logo.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            if not company_logo.content_type.startswith('image/'):
                raise forms.ValidationError("File is not an image")
        return company_logo

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