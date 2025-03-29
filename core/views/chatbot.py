import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import JobListing, UserProfile

@login_required
def chatbot(request):
    try:
        user_profile = request.user.userprofile
        if not user_profile.is_complete():
            messages.warning(request, "You need to complete your profile before accessing the AI chatbot.")
            return redirect('profile')
    except UserProfile.DoesNotExist:
        messages.warning(request, "You need to create your profile before accessing the AI chatbot.")
        return redirect('profile')

    response = ""
    jobs = JobListing.objects.all()[:5]
    job_context = "\n".join([f"- {job.title} at {job.company}: {job.description}" for job in jobs])
    
    user_context = f"User Profile:\n- Interests: {user_profile.interests}\n- Fields: {user_profile.fields}\n- Experience: {user_profile.experience}\n- Job Preferences: {user_profile.job_preferences}"

    if request.method == "POST":
        user_input = request.POST.get('user_input', '').strip().lower()
        prompt_words = user_input.split()

        
        prompt = f" <<DO NOT INCLUDE THINKING PROCESS>> I want this chatbot to communicate with users. answer as you would answer to me.  \n\n this is user's information: {user_context} \n\n this is the job information: {job_context} \n\n\n Here is user prompt: {user_input}\n if its vague or unclear just say 'Sorry, I cannot proceed with that' (just remember to not include thinking process, if the input is somehow vague just discard it), if not you can find appropriate job for user (if user asks for it) and give them a response.. if its vague or unclear just say 'Sorry, I cannot proceed with that'. \n\nAgain <<DO NOT INCLUDE THINKING PROCESS>>\n\n" 
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