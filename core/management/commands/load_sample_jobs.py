from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, EmployerProfile, JobListing
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Loads sample jobs into the database'

    def handle(self, *args, **kwargs):
        # Create a sample employer if it doesn't exist
        try:
            employer_user = User.objects.get(username='sample_employer')
        except User.DoesNotExist:
            employer_user = User.objects.create_user(
                username='sample_employer',
                email='employer@example.com',
                password='sample123',
                first_name='Sample',
                last_name='Employer'
            )
        
        # Create or get employer profile
        employer_profile, _ = EmployerProfile.objects.get_or_create(
            user_profile=UserProfile.objects.get_or_create(
                user=employer_user,
                defaults={
                    'role': 'employer',
                    'interests': 'AI, Machine Learning, Software Development',
                    'fields': 'Technology, Software, AI',
                    'experience': 'senior',
                    'job_preferences': 'full-time, remote'
                }
            )[0],
            defaults={
                'company_name': 'Tech Innovations Inc.',
                'company_website': 'https://techinnovations.example.com',
                'company_description': 'A leading technology company specializing in AI and software solutions.',
                'company_size': '51-200',
                'industry': 'Technology',
                'location': 'San Francisco, CA'
            }
        )

        # Sample jobs data
        sample_jobs = [
            {
                'title': 'Senior AI Engineer',
                'company': 'Tech Innovations Inc.',
                'description': 'We are looking for a Senior AI Engineer to join our team. You will be responsible for developing and implementing AI solutions, working with machine learning models, and collaborating with cross-functional teams.',
                'interests': 'AI, Machine Learning, Python, TensorFlow',
                'fields': 'Artificial Intelligence, Software Engineering',
                'experience': 'senior',
                'job_preferences': 'full-time, remote',
                'employer': employer_profile
            },
            {
                'title': 'Frontend Developer',
                'company': 'Tech Innovations Inc.',
                'description': 'Join our frontend team to build beautiful and responsive web applications. You will work with modern frameworks like React and Vue.js, and collaborate with designers and backend developers.',
                'interests': 'JavaScript, React, Vue.js, CSS',
                'fields': 'Web Development, Frontend Engineering',
                'experience': 'mid-level',
                'job_preferences': 'full-time, hybrid',
                'employer': employer_profile
            },
            {
                'title': 'Data Scientist',
                'company': 'Tech Innovations Inc.',
                'description': 'We are seeking a Data Scientist to analyze complex data sets and develop predictive models. You will work with large datasets, implement machine learning algorithms, and communicate insights to stakeholders.',
                'interests': 'Python, R, Machine Learning, Statistics',
                'fields': 'Data Science, Analytics',
                'experience': 'mid-level',
                'job_preferences': 'full-time, remote',
                'employer': employer_profile
            },
            {
                'title': 'DevOps Engineer',
                'company': 'Tech Innovations Inc.',
                'description': 'Looking for a DevOps Engineer to help us build and maintain our cloud infrastructure. You will work with AWS, Docker, Kubernetes, and CI/CD pipelines to ensure smooth deployments and operations.',
                'interests': 'AWS, Docker, Kubernetes, CI/CD',
                'fields': 'DevOps, Cloud Computing',
                'experience': 'senior',
                'job_preferences': 'full-time, remote',
                'employer': employer_profile
            },
            {
                'title': 'Product Manager',
                'company': 'Tech Innovations Inc.',
                'description': 'We need a Product Manager to lead our product development efforts. You will work with cross-functional teams, define product strategy, and ensure successful product launches.',
                'interests': 'Product Management, Agile, User Research',
                'fields': 'Product Management, Business',
                'experience': 'senior',
                'job_preferences': 'full-time, hybrid',
                'employer': employer_profile
            }
        ]

        # Create sample jobs
        for job_data in sample_jobs:
            job, created = JobListing.objects.get_or_create(
                title=job_data['title'],
                defaults=job_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created job: {job.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Job already exists: {job.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample jobs')) 