from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobListing
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import UploadedFile

class UserRegistrationForm(UserCreationForm):
    """Form for user registration using Django's built-in UserCreationForm."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
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
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field - we'll use email as username
        if 'username' in self.fields:
            del self.fields['username']
            
        # Override help_text that comes with Django's UserCreationForm
        for field_name in ['password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].help_text = None
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def save(self, commit=True):
        # Save the User instance first using UserCreationForm's save
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        # Use email as username
        user.username = self.cleaned_data.get('email')
        
        if commit:
            user.save()
            
        return user

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