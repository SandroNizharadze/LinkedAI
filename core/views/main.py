from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from ..models import JobListing, UserProfile
from ..forms import UserProfileForm
import logging

logger = logging.getLogger(__name__)

def job_list(request):
    jobs = JobListing.objects.all().order_by('-posted_at')
    profile_incomplete = False
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            profile_incomplete = not profile.is_complete()
        except UserProfile.DoesNotExist:
            profile_incomplete = True
    return render(request, 'core/job_list.html', {'jobs': jobs, 'profile_incomplete': profile_incomplete})

def login_view(request):
    redirect_url = reverse('social:begin', kwargs={'backend': 'google-oauth2'})
    logger.debug(f"Login redirect URL: {request.build_absolute_uri(redirect_url)}")
    return redirect(redirect_url)

def logout_view(request):
    logout(request)
    return redirect('job_list')

def register(request):
    if not request.user.is_authenticated:
        redirect_url = reverse('social:begin', kwargs={'backend': 'google-oauth2'})
        logger.debug(f"Register redirect URL: {request.build_absolute_uri(redirect_url)}")
        return redirect(redirect_url)

    try:
        user_profile = UserProfile.objects.get(user=request.user)
        return redirect('job_list')
    except UserProfile.DoesNotExist:
        if request.method == 'POST':
            form = UserProfileForm(request.POST)
            if form.is_valid():
                user_profile = form.save(commit=False)
                user_profile.user = request.user
                user_profile.save()
                return redirect('job_list')
            else:
                return render(request, 'core/register.html', {'form': form})
        else:
            form = UserProfileForm()
        return render(request, 'core/register.html', {'form': form})

@login_required
def profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('job_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'core/profile.html', {'form': form})