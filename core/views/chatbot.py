import requests
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from ..models import JobListing, UserProfile

logger = logging.getLogger(__name__)

@login_required
def chatbot(request):
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request headers: {request.headers}")

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
        logger.debug(f"User input: {user_input}")
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
            logger.debug(f"Ollama response status: {ollama_response.status_code}")
            logger.debug(f"Ollama response content: {ollama_response.text}")
            raw_response = ollama_response.json().get('response', 'Sorry, I couldn’t process that.')

            # Format the response as HTML
            if "Sorry, I cannot proceed with that" in raw_response:
                response = f"<p>{raw_response}</p>"
            else:
                # Split the response into sections
                lines = raw_response.split('\n')
                formatted_response = []
                in_list = False

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Handle job recommendation (e.g., "**Senior Python Engineer at Windsor.ai**")
                    if line.startswith("**") and line.endswith("**"):
                        job_title = line.strip("**")
                        formatted_response.append(f'<p>Here’s a job that might be a good fit: <strong>{job_title}</strong></p>')
                    # Handle list items (e.g., "* Interests: AI (mentioned as one of your interests)")
                    elif line.startswith("*"):
                        if not in_list:
                            formatted_response.append('<ul>')
                            in_list = True
                        item = line.lstrip("* ").strip()
                        # Split the item into label and description (e.g., "Interests: AI (mentioned as one of your interests)")
                        if ":" in item:
                            label, desc = item.split(":", 1)
                            formatted_response.append(f'<li><strong>{label.strip()}:</strong> {desc.strip()}</li>')
                        else:
                            formatted_response.append(f'<li>{item}</li>')
                    else:
                        if in_list:
                            formatted_response.append('</ul>')
                            in_list = False
                        formatted_response.append(f'<p>{line}</p>')

                if in_list:
                    formatted_response.append('</ul>')

                response = "".join(formatted_response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama: {str(e)}")
            response = "<p>Error connecting to the AI service.</p>"
        except ValueError as e:
            logger.error(f"Error parsing Ollama response as JSON: {str(e)}")
            response = "<p>Error: Invalid response from AI service.</p>"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            logger.debug("Detected AJAX request, returning JSON response")
            return JsonResponse({'response': mark_safe(response)})

    return render(request, 'core/chatbot.html', {'response': response})