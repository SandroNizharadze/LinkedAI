import requests
from django.shortcuts import render
from ..models import JobListing

# Expanded list of relevant words
RELEVANT_WORDS = [
    # Software-related terms
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'swift', 'kotlin', 'php', 'rust', 'scala', 'perl', 'haskell', 'typescript', 'r', 'matlab', 'lua', 'dart', 'groovy',
    'html', 'css', 'react', 'angular', 'vue', 'node', 'nodejs', 'django', 'flask', 'express', 'laravel', 'asp.net', 'jquery', 'bootstrap', 'sass', 'webpack', 'nextjs', 'nuxtjs', 'svelte',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite', 'oracle', 'cassandra', 'redis', 'dynamodb', 'firebase', 'elasticsearch',
    'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'terraform', 'ansible', 'puppet', 'chef', 'nginx', 'apache', 'linux', 'unix', 'bash',
    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'kanban', 'testing', 'debugging', 'ci/cd', 'deployment', 'devops', 'cloud', 'serverless', 'frontend', 'backend', 'fullstack', 'oop', 'object-oriented', 'functional', 'security', 'encryption', 'authentication', 'scalability',

    # Job-related terms
    'developer', 'job', 'jobs', 'engineer', 'programmer', 'architect', 'analyst', 'tester', 'designer', 'devops', 'sysadmin', 'administrator', 'data scientist', 'machine learning', 'ai', 'artificial intelligence', 'frontend', 'backend', 'fullstack', 'mobile', 'web', 'software', 'qa', 'quality assurance', 'ui', 'ux', 'cybersecurity', 'blockchain', 'embedded', 'systems', 'network', 'database', 'dba',
    'full-time', 'part-time', 'freelance', 'contract', 'remote', 'internship', 'temporary', 'permanent', 'consultant', 'consulting', 'gig', 'seasonal', 'volunteer',
    'junior', 'mid-level', 'senior', 'lead', 'entry-level', 'graduate', 'experienced', 'beginner', 'intermediate', 'advanced', 'expert', 'principal', 'associate',
    'coding', 'programming', 'problem-solving', 'teamwork', 'communication', 'leadership', 'management', 'design', 'analysis', 'troubleshooting', 'optimization', 'documentation', 'mentoring', 'collaboration',
    'looking for', 'seeking', 'applying', 'interested in', 'searching', 'hiring', 'recruiting', 'interviewing', 'working', 'job hunting', 'career', 'employment', 'opportunity', 'openings', 'vacancy',

    # General terms
    'tech', 'technology', 'software', 'it', 'information technology', 'startup', 'enterprise', 'finance', 'healthcare', 'education', 'gaming', 'e-commerce', 'retail', 'manufacturing', 'telecom', 'automotive', 'fintech', 'edtech',
    'remote', 'on-site', 'hybrid', 'work from home', 'office', 'relocate', 'relocation', 'local', 'international', 'usa', 'uk', 'india', 'canada',
    'pay', 'salary', 'compensation', 'benefits', 'bonus', 'package', 'wage', 'hourly', 'annually', 'stock', 'equity', 'perks',
    'startup', 'corporation', 'agency', 'consultancy', 'firm', 'sme', 'small business', 'multinational', 'big tech', 'faang',
    'resume', 'cv', 'portfolio', 'experience', 'skills', 'certification', 'degree', 'training', 'bootcamp', 'project', 'team', 'role', 'position', 'promotion', 'growth', 'development',

    # Niche terms
    'penetration testing', 'ethical hacking', 'incident response',
    'smart contract', 'decentralized', 'cryptocurrency',
    'neural network', 'deep learning', 'natural language processing',

    # Company names
    'facebook', 'amazon', 'apple', 'netflix', 'google', 'microsoft', 'ibm', 'oracle', 'salesforce', 'stripe', 'airbnb', 'uber', 'slack'
]

def chatbot(request):
    response = ""
    jobs = JobListing.objects.all()[:5]
    job_context = "\n".join([f"- {job.title} at {job.company}: {job.description}" for job in jobs])

    if request.method == "POST":
        user_input = request.POST.get('user_input', '').strip().lower()
        prompt_words = user_input.split()

        if not any(word in RELEVANT_WORDS for word in prompt_words):
            response = "Sorry, I can’t process that. I’m here to help with job recommendations in the software industry. Please include something about jobs, skills, or software (e.g., 'Python developer job')."
        else:
            prompt = f"Here are some available jobs:\n{job_context}\n\nBased on the user input: '{user_input}', suggest a suitable job and explain why. If the input is unclear, ask for more details."
            try:
                ollama_response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': 'llama3',
                        'prompt': prompt,
                        'stream': False
                    }
                )
                response = ollama_response.json().get('response', 'Sorry, I couldn’t process that.')
            except requests.exceptions.RequestException:
                response = "Error connecting to the AI service."

    return render(request, 'core/chatbot.html', {'response': response})