from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from ..models import JobListing, UserProfile
from ..forms import UserProfileForm

def job_list(request):
    jobs = JobListing.objects.all().order_by('-posted_at')
    return render(request, 'core/job_list.html', {'jobs': jobs})

def login_view(request):
    return redirect('social:begin', backend='google-oauth2')

def logout_view(request):
    logout(request)
    return redirect('job_list')

def register(request):
    # Ensure the user is authenticated (after Google OAuth login)
    if not request.user.is_authenticated:
        return redirect('social:begin', backend='google-oauth2')

    # Check if the user already has a profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # If profile exists, redirect to homepage
        return redirect('job_list')
    except UserProfile.DoesNotExist:
        # If no profile, show the form to collect additional fields
        if request.method == 'POST':
            form = UserProfileForm(request.POST)
            if form.is_valid():
                user_profile = form.save(commit=False)
                user_profile.user = request.user
                user_profile.save()
                return redirect('job_list')
            else:
                # If form is invalid, re-render the form with errors
                return render(request, 'core/register.html', {'form': form})
        else:
            form = UserProfileForm()
        return render(request, 'core/register.html', {'form': form})