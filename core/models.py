from django.db import models
from django.contrib.auth.models import User

class JobListing(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.CharField(max_length=200, help_text="E.g., AI, web development, cybersecurity")
    fields = models.CharField(max_length=200, help_text="E.g., software engineering, data science")
    experience = models.CharField(max_length=100, choices=[
        ('entry-level', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid-level', 'Mid-Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead/Principal'),
    ])
    job_preferences = models.CharField(max_length=200, help_text="E.g., remote, full-time, startup")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"