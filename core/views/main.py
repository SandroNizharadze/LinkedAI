from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from ..models import JobListing, UserProfile, EmployerProfile
from ..forms import UserProfileForm, EmployerProfileForm, JobListingForm
import logging

logger = logging.getLogger(__name__)

def is_employer(user):
    """
    Check if a user has employer role and associated employer profile
    """
    try:
        return (user.is_authenticated and 
                hasattr(user, 'userprofile') and 
                user.userprofile.role == 'employer' and
                hasattr(user.userprofile, 'employer_profile'))
    except:
        return False

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')

def job_list(request):
    jobs = JobListing.objects.all().order_by('-posted_at')
    is_employer_user = is_employer(request.user)
    
    return render(request, 'core/job_list.html', {
        'jobs': jobs,
        'is_employer': is_employer_user,
    })

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
            form = UserProfileForm(request.POST, request.FILES)
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
    user_profile = request.user.userprofile
    user_form = UserProfileForm(instance=user_profile)
    employer_form = None
    
    if is_employer(request.user):
        employer_profile, created = EmployerProfile.objects.get_or_create(user_profile=user_profile)
        employer_form = EmployerProfileForm(instance=employer_profile)
        
        if request.method == 'POST':
            user_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            employer_form = EmployerProfileForm(request.POST, request.FILES, instance=employer_profile)
            
            if user_form.is_valid() and employer_form.is_valid():
                user_form.save()
                employer_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
    else:
        if request.method == 'POST':
            user_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
    
    return render(request, 'core/profile.html', {
        'user_form': user_form,
        'employer_form': employer_form,
        'is_employer': is_employer(request.user),
    })

@login_required
@user_passes_test(is_employer)
def employer_jobs(request):
    employer_profile = request.user.userprofile.employer_profile
    jobs = JobListing.objects.filter(employer=employer_profile).order_by('-posted_at')
    
    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer_profile
            job.company = employer_profile.company_name
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('employer_jobs')
    else:
        form = JobListingForm()
    
    return render(request, 'core/employer_jobs.html', {
        'jobs': jobs,
        'form': form
    })

@login_required
def employer_dashboard(request):
    if not is_employer(request.user):
        messages.error(request, "You don't have permission to access the employer dashboard. Please contact an administrator to get employer access.")
        return redirect('job_list')
    
    try:
        employer_profile = request.user.userprofile.employer_profile
        jobs = JobListing.objects.filter(employer=employer_profile).order_by('-posted_at')
        form = JobListingForm()
        
        return render(request, 'core/employer_dashboard.html', {
            'jobs': jobs,
            'form': form,
            'employer_profile': employer_profile
        })
    except EmployerProfile.DoesNotExist:
        messages.error(request, "Your employer profile is not properly set up. Please contact an administrator.")
        return redirect('job_list')

@login_required
def post_job(request):
    if not is_employer(request.user):
        messages.error(request, "Only employers can post jobs. Please contact an administrator to get employer access.")
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.userprofile.employer_profile
            job.company = request.user.userprofile.employer_profile.company_name
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('employer_dashboard')
    else:
        form = JobListingForm()
    
    return render(request, 'core/employer_dashboard.html', {'form': form})

@login_required
def edit_job(request, job_id):
    if not is_employer(request.user):
        messages.error(request, "Only employers can edit jobs. Please contact an administrator to get employer access.")
        return redirect('job_list')
    
    job = get_object_or_404(JobListing, id=job_id)
    if job.employer != request.user.userprofile.employer_profile:
        raise PermissionDenied("You can only edit your own job listings.")
    
    if request.method == 'POST':
        form = JobListingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('employer_dashboard')
    
    return JsonResponse({
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'interests': job.interests,
        'fields': job.fields,
        'experience': job.experience,
        'job_preferences': job.job_preferences,
    })

@login_required
@require_POST
def delete_job(request, job_id):
    if not is_employer(request.user):
        messages.error(request, "Only employers can delete jobs. Please contact an administrator to get employer access.")
        return redirect('job_list')
    
    job = get_object_or_404(JobListing, id=job_id)
    if job.employer != request.user.userprofile.employer_profile:
        raise PermissionDenied("You can only delete your own job listings.")
    
    job.delete()
    messages.success(request, "Job deleted successfully!")
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_admin)
def assign_employer(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    user_profile.role = 'employer'
    user_profile.save()
    
    # Create employer profile
    EmployerProfile.objects.get_or_create(user_profile=user_profile)
    
    messages.success(request, f"{user_profile.user.get_full_name()} has been assigned as an employer.")
    return JsonResponse({'status': 'success'})