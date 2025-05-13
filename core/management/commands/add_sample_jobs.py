from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import JobListing, EmployerProfile, UserProfile
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Adds sample job listings to the database'

    def handle(self, *args, **options):
        # Sample job data
        job_data = [
            {
                "title": "Machine Learning Engineer",
                "company": "AI Innovations",
                "description": """We're looking for a skilled Machine Learning Engineer to join our team. You'll be working on cutting-edge AI models to solve real-world problems.

Requirements:
- 3+ years of experience with ML frameworks (TensorFlow, PyTorch)
- Strong Python programming skills
- Experience with NLP and computer vision
- Background in statistics and data analysis
- BS/MS in Computer Science, AI, or related field

Benefits:
- Competitive salary and equity
- Flexible work arrangements
- Health and wellness benefits
- Learning and development budget""",
                "interests": "machine learning python tensorflow pytorch",
                "fields": "artificial intelligence data science",
                "experience": "mid-level",
                "job_preferences": "remote full-time"
            },
            {
                "title": "Full Stack Developer",
                "company": "TechSolutions",
                "description": """Join our team as a Full Stack Developer and help build scalable web applications that make a difference.

What you'll do:
- Design and implement frontend interfaces with React
- Develop backend services using Node.js
- Work with databases (SQL and NoSQL)
- Participate in code reviews and team planning

What we're looking for:
- 2+ years experience with React and Node.js
- Knowledge of modern JavaScript/TypeScript
- Experience with SQL and NoSQL databases
- Understanding of API design and implementation
- Strong problem-solving skills""",
                "interests": "javascript typescript react nodejs",
                "fields": "web development software engineering",
                "experience": "junior",
                "job_preferences": "hybrid full-time"
            },
            {
                "title": "Data Scientist",
                "company": "DataDriven",
                "description": """DataDriven is seeking a talented Data Scientist to transform data into actionable insights.

Your responsibilities:
- Analyze large datasets to uncover patterns and trends
- Build predictive models using machine learning
- Create data visualizations to communicate findings
- Collaborate with product teams to drive decision-making

What you need:
- Experience with statistical analysis and machine learning
- Proficiency in Python and data science libraries (pandas, scikit-learn)
- Strong SQL skills
- Excellent communication skills
- Bachelor's or Master's degree in a quantitative field""",
                "interests": "data analysis python sql statistics",
                "fields": "data science analytics",
                "experience": "mid-level",
                "job_preferences": "on-site full-time"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudNative",
                "description": """CloudNative is looking for a DevOps Engineer to help us build and maintain our cloud infrastructure.

Key responsibilities:
- Design and implement CI/CD pipelines
- Manage cloud infrastructure using Terraform
- Monitor system performance and reliability
- Troubleshoot and resolve infrastructure issues
- Implement security best practices

Requirements:
- Experience with AWS, Azure, or GCP
- Knowledge of containerization (Docker, Kubernetes)
- Familiarity with infrastructure as code (Terraform, CloudFormation)
- Experience with CI/CD tools (Jenkins, GitHub Actions)
- Strong scripting skills (Bash, Python)""",
                "interests": "devops cloud kubernetes terraform",
                "fields": "infrastructure cloud engineering",
                "experience": "senior",
                "job_preferences": "remote full-time"
            },
            {
                "title": "UI/UX Designer",
                "company": "DesignFirst",
                "description": """DesignFirst is seeking a UI/UX Designer to create beautiful and intuitive user experiences.

What you'll be doing:
- Create wireframes, prototypes, and user flows
- Conduct user research and usability testing
- Collaborate with developers to implement designs
- Maintain and evolve our design system

Qualifications:
- Portfolio demonstrating strong UI/UX design skills
- Experience with design tools (Figma, Sketch, Adobe XD)
- Understanding of user-centered design principles
- Knowledge of HTML/CSS is a plus
- Excellent communication and presentation skills""",
                "interests": "ui ux design figma user research",
                "fields": "design product",
                "experience": "mid-level",
                "job_preferences": "hybrid full-time"
            },
            {
                "title": "Frontend Developer",
                "company": "WebWizards",
                "description": """WebWizards is looking for a Frontend Developer to create responsive and engaging user interfaces.

Responsibilities:
- Implement UI components using React and TypeScript
- Optimize applications for maximum speed and scalability
- Collaborate with UX designers to implement designs accurately
- Write clean, maintainable code and unit tests

Requirements:
- 1+ years of experience with React
- Strong JavaScript/TypeScript skills
- Knowledge of HTML5 and CSS3
- Understanding of responsive design principles
- Experience with state management (Redux, Context API)""",
                "interests": "react javascript typescript css",
                "fields": "frontend web development",
                "experience": "entry-level",
                "job_preferences": "remote full-time"
            },
            {
                "title": "Backend Engineer",
                "company": "ServerSide",
                "description": """ServerSide is hiring a Backend Engineer to build and maintain our API services.

What you'll do:
- Design and implement RESTful APIs
- Work with relational and NoSQL databases
- Optimize application performance
- Collaborate with frontend developers
- Write automated tests

What we're looking for:
- 3+ years of experience in backend development
- Proficiency in Python, Java, or Go
- Strong knowledge of SQL and database design
- Experience with microservices architecture
- Understanding of security best practices""",
                "interests": "backend api python java microservices",
                "fields": "software engineering backend",
                "experience": "mid-level",
                "job_preferences": "hybrid full-time"
            },
            {
                "title": "Product Manager",
                "company": "ProductPerfect",
                "description": """ProductPerfect is seeking a Product Manager to lead our product development efforts.

Responsibilities:
- Define product vision, strategy, and roadmap
- Gather and prioritize product requirements
- Work with engineering, design, and marketing teams
- Analyze market data and user feedback
- Track product metrics and KPIs

Requirements:
- 3+ years of product management experience
- Strong understanding of product development process
- Experience with agile methodologies
- Excellent communication and leadership skills
- Technical background is a plus""",
                "interests": "product management agile user research",
                "fields": "product management",
                "experience": "senior",
                "job_preferences": "on-site full-time"
            },
            {
                "title": "Cloud Security Engineer",
                "company": "SecureCloud",
                "description": """SecureCloud is looking for a Cloud Security Engineer to help protect our cloud infrastructure and applications.

Key responsibilities:
- Implement and maintain cloud security controls
- Conduct security assessments and penetration testing
- Monitor and respond to security incidents
- Develop security automation tools
- Collaborate with DevOps team on security best practices

Requirements:
- Experience with cloud security (AWS, Azure, or GCP)
- Knowledge of security frameworks and compliance standards
- Familiarity with common vulnerabilities and threats
- Experience with security tools and technologies
- Relevant security certifications (e.g., CISSP, CCSP) are a plus""",
                "interests": "security cloud cybersecurity compliance",
                "fields": "security cloud engineering",
                "experience": "senior",
                "job_preferences": "remote full-time"
            },
            {
                "title": "AI Research Scientist",
                "company": "DeepThought",
                "description": """DeepThought is seeking an AI Research Scientist to push the boundaries of artificial intelligence.

Responsibilities:
- Conduct research in cutting-edge AI fields
- Develop novel algorithms and models
- Publish research findings in top conferences and journals
- Collaborate with engineering team to implement research into products
- Stay current with the latest AI research developments

Requirements:
- PhD in Computer Science, AI, or related field
- Strong publication record in AI/ML
- Experience with deep learning frameworks
- Excellent mathematical and statistical skills
- Strong programming abilities in Python and relevant ML libraries""",
                "interests": "artificial intelligence machine learning research deep learning",
                "fields": "artificial intelligence research",
                "experience": "lead",
                "job_preferences": "hybrid full-time"
            },
        ]

        # Create jobs with varied posting dates
        now = timezone.now()
        job_count = 0
        
        for job in job_data:
            # Set a random posted_at date within the last 30 days
            days_ago = random.randint(0, 30)
            posted_at = now - timedelta(days=days_ago)
            
            # Create the job listing
            JobListing.objects.create(
                title=job["title"],
                company=job["company"],
                description=job["description"],
                interests=job["interests"],
                fields=job["fields"],
                experience=job["experience"],
                job_preferences=job["job_preferences"],
                posted_at=posted_at,
                updated_at=posted_at
            )
            job_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {job_count} sample job listings')) 