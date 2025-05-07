from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobListing
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import UploadedFile

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

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your last name'
    }))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        # Add help text for password requirements
        self.fields['password1'].help_text = """
            <ul class="password-requirements">
                <li>Your password must be at least 8 characters long</li>
                <li>Your password can't be too similar to your personal information</li>
                <li>Your password can't be a commonly used password</li>
                <li>Your password can't be entirely numeric</li>
            </ul>
        """
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("First name is required.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("Last name is required.")
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user