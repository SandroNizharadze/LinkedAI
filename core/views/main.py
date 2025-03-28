from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ..models import JobListing, UserProfile
from ..forms import UserProfileForm
import logging

# Set up logging
logger = logging.getLogger(__name__)

def job_list(request):
    jobs = JobListing.objects.all().order_by('-posted_at')
    return render(request, 'core/job_list.html', {'jobs': jobs})

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