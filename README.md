# LinkedAI - AI-Powered Job Platform

LinkedAI is a modern job platform that leverages artificial intelligence to connect job seekers with employers. The platform provides intelligent job matching, AI-powered career guidance, and a seamless job application process.

## Features

### For Job Seekers
- **AI-Powered Job Matching**: Get personalized job recommendations based on your profile
- **Career Assistant**: Chat with an AI assistant for career guidance and advice
- **Profile Management**: Create and manage your professional profile
- **Job Applications**: Easy application process with resume and cover letter submission
- **Job Search**: Browse and search through available job listings

### For Employers
- **Job Posting**: Create and manage job listings
- **Company Profile**: Showcase your company with detailed information
- **Dashboard**: Manage all your job postings in one place
- **AI Integration**: Get AI-powered insights for your job postings

## Tech Stack

- **Backend**: Django 5.1.7
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: PostgreSQL
- **Authentication**: Django's built-in authentication + Google OAuth2
- **AI Integration**: Custom AI chatbot for career guidance (llama3)


## Installation

1. Clone the repository:
```bash
git clone https://github.com/SandroNizharadze/LinkedAI.git
cd LinkedAI
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/linked_ai_db
GOOGLE_OAUTH2_KEY=your_google_oauth2_key
GOOGLE_OAUTH2_SECRET=your_google_oauth2_secret
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
LinkedAI/
├── core/                    # Main application
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   ├── static/            # Static files (CSS, JS, images)
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL patterns
│   └── forms.py           # Form definitions
├── linked_ai/             # Project settings
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Key Features Implementation

### Job Listings
- Job creation and management
- Detailed job pages
- Application submission
- Job filtering and search

### User Profiles
- Role-based access (Job Seeker/Employer)
- Profile completion tracking
- Company profiles for employers

### AI Integration
- Career guidance chatbot
- Job matching algorithm
- Resume analysis


