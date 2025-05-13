# LinkedAI - AI-Powered Job Platform

LinkedAI is a modern job platform that leverages artificial intelligence to connect job seekers with employers. The platform provides intelligent job matching, AI-powered career guidance, and a seamless job application process.

<img width="1141" alt="image" src="https://github.com/user-attachments/assets/e2682ced-68cc-4c24-be1d-0861e24e5511" />


<img width="1108" alt="image" src="https://github.com/user-attachments/assets/b80542b8-5caa-48d2-bf97-1a44b8b2a3be" />



## Features

### For Job Seekers
- **AI-Powered Job Matching**: Get personalized job recommendations based on your profile
- **Career Assistant**: Chat with an AI assistant for career guidance and advice
- **Profile Management**: Create and manage your professional profile
- **Job Applications**: Easy application process with resume and cover letter submission

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
- **AI Integration**: Custom AI chatbot for career guidance (supports both Llama2 and Llama3)
- **Containerization**: Docker and Docker Compose

## Docker Installation


1. Clone the repository:
```bash
git clone https://github.com/SandroNizharadze/LinkedAI.git
cd LinkedAI
```

2. Create a `.env` file with the necessary environment variables:
```
DEBUG=True
SECRET_KEY=your_secret_key
DB_NAME=linked_ai_db
DB_USER=postgres
DB_PASSWORD=postgres
GOOGLE_OAUTH2_KEY=your_google_oauth2_key
GOOGLE_OAUTH2_SECRET=your_google_oauth2_secret
```

3. Start the Ollama service locally (see AI Setup section below)

4. Build and start the Docker containers:
```bash
docker-compose up -d
```

5. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

6. Access the application at http://localhost:8000

## AI Setup

The project uses Llama models for AI-powered features. Due to performance considerations, it's recommended to run Ollama locally instead of within Docker to take advantage of GPU acceleration.

### Prerequisites
- [Ollama](https://ollama.ai/) installed on your system
- At least 8GB of RAM (16GB recommended)
- GPU with CUDA support (recommended for Llama3)

### Ollama Installation

1. Install Ollama:
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

2. Pull the Llama model (choose one based on your hardware capabilities):
```bash
# For systems with powerful GPUs
ollama pull llama3

# For less powerful machine
ollama pull llama2

```

3. Start the Ollama service:
```bash
ollama serve
```

### Why Ollama Runs Locally?

I've designed the application to use a locally running Ollama instance instead of containerizing it for the following reasons:

 **GPU Acceleration**: Docker has limitations accessing GPU resources (I'm using MacOs)
 **Resource Usage**: Running LLMs in Docker with CPU-only is extremely slow and memory-intensive

The web application container is configured to connect to your local Ollama instance through `host.docker.internal`.

### Modifying the LLM Model

To switch between Llama2 and Llama3 models:

1. Edit the `core/views/chatbot.py` file and change the model parameter:
```python
# For Llama3
'model': 'llama3',

# For Llama2
'model': 'llama2',
```

2. Restart the application after changing the model

## Key Features Implementation

### Job Listings
- Job creation and management

<img width="1159" alt="image" src="https://github.com/user-attachments/assets/18f7a349-e8e6-48c2-8522-798d2feaa45e" />

- Detailed job pages

<img width="1113" alt="image" src="https://github.com/user-attachments/assets/7af70acb-f3a0-49c8-9add-ef616b5460ac" />


### User Profiles
- Role-based access (Job Seeker/Employer)

<img width="1186" alt="image" src="https://github.com/user-attachments/assets/d022d868-625d-43ea-b493-7ced281bc562" />

<img width="1105" alt="image" src="https://github.com/user-attachments/assets/4750605f-70da-4cb1-be56-1564f3292f47" />


- Profile completion tracking
- Company profiles for employers

### Admin Profile
- Django administration interface


<img width="1512" alt="image" src="https://github.com/user-attachments/assets/a19bbe0e-7a9c-414e-91b4-ec734674eb31" />


### AI Integration
- Career guidance chatbot
- Job matching algorithm


<img width="1053" alt="image" src="https://github.com/user-attachments/assets/2cba8697-8b99-4509-a048-f3499b94f5b4" />



