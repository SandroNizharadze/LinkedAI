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
    response = ""
    user_profile = None

    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    chat_history = request.session['chat_history']

    try:
        user_profile = request.user.userprofile
        profile_complete = user_profile.is_complete()
        missing_fields = []
        
        if not user_profile.interests.strip():
            missing_fields.append("interests")
        if not user_profile.fields.strip():
            missing_fields.append("fields")
        if not user_profile.experience.strip():
            missing_fields.append("experience level")
        if not user_profile.job_preferences.strip():
            missing_fields.append("job preferences")
            
    except UserProfile.DoesNotExist:
        messages.warning(request, "Please create your profile first.")
        return redirect('profile')
    except Exception as e:
        logger.error(f"Error accessing user profile: {str(e)}")
        messages.error(request, "An error occurred accessing your profile.")
        return redirect('profile')

    jobs = JobListing.objects.all().order_by('-posted_at')[:5]
    job_context = "\n".join(
        f"- {job.title} at {job.company} ({job.get_experience_display()})"
        for job in jobs
    )
    
    user_context = {
        'name': user_profile.user.first_name,
        'interests': user_profile.interests,
        'fields': user_profile.fields,
        'experience': user_profile.get_experience_display(),
        'preferences': user_profile.job_preferences,
        'profile_complete': profile_complete,
        'missing_fields': ", ".join(missing_fields) if missing_fields else None
    }

    if request.method == "POST":
        try:
            user_input = request.POST.get('user_input', '').strip()
            logger.debug(f"User input: {user_input}")

            history_context = "\n".join(
                f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
                for i, msg in enumerate(chat_history[-4:])  # Last 2 exchanges
            )

            prompt = f"""You are an AI career assistant. Be natural and conversational in your responses.

Basic context:
- User's name: {user_context['name']}
- Experience level: {user_context['experience'] if user_context['experience'] else 'Not specified'}
- Fields: {user_context['fields'] if user_context['fields'] else 'Not specified'}
- Profile status: {"Complete" if user_context['profile_complete'] else f"Incomplete - missing {user_context['missing_fields']}"}
- Is this the first message? {'Yes' if len(chat_history) == 0 else 'No'}

Previous conversation history:
{history_context}

User's message: {user_input}

Guidelines:
1. Only greet the user (e.g., "Hi!" or "Hello!") in your very first message. For all follow-up responses, do NOT start with a greeting or "Hey!"—just answer naturally.
2. Keep responses brief and natural
3. Only suggest jobs when explicitly asked about job opportunities
4. For job titles, use <span class="job-title">Job Title</span> format (do not use brackets)
5. Do not repeat or reference the user's name
6. Maintain conversation flow based on the chat history
7. If user asks about jobs and their profile is incomplete, kindly remind them to complete their profile for better recommendations
8. When suggesting jobs, prioritize those that match the user's fields and experience level

Available jobs:
{job_context}

Remember: Be conversational, not overly formal, and do not mention the user's name after the first response."""

            ollama_response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=15
            )
            logger.debug(f"Ollama response status: {ollama_response.status_code}")
            raw_response = ollama_response.json().get('response', "Sorry, I couldn't process that.")

            chat_history.append(user_input)
            chat_history.append(raw_response)
            request.session['chat_history'] = chat_history[-10:]  
            request.session.modified = True

            lines = raw_response.split('\n')
            formatted_response = []
            in_list = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if '<span class="job-title">' in line:
                    # Extract job title from the span
                    start = line.find('<span class="job-title">') + len('<span class="job-title">')
                    end = line.find('</span>', start)
                    if start != -1 and end != -1:
                        job_title = line[start:end].replace('<i class="fas fa-briefcase me-2"></i>', '').strip()
                        try:
                            job = JobListing.objects.get(title=job_title)
                            job_url = f'/jobs/{job.id}/'
                            # Replace the span with a link
                            line = line.replace(
                                f'<span class="job-title">{job_title}</span>',
                                f'<a href="{job_url}" class="job-title-link"><span class="job-title"><i class="fas fa-briefcase me-2"></i>{job_title}</span></a>'
                            )
                        except JobListing.DoesNotExist:
                            pass
                    formatted_response.append(f'<p>{line}</p>')
                elif line.startswith("*"):
                    if not in_list:
                        formatted_response.append('<ul class="list-unstyled mb-3">')
                        in_list = True
                    item = line.lstrip("* ").strip()
                    formatted_response.append(
                        f'<li class="mb-2">'
                        f'<i class="fas fa-check-circle text-success me-2"></i>'
                        f'{item}'
                        f'</li>'
                    )
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
            response = '<p class="text-danger"><i class="fas fa-exclamation-circle me-2"></i>Sorry, I encountered a connection error. Please try again.</p>'
        except ValueError as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
            response = '<p class="text-danger"><i class="fas fa-exclamation-circle me-2"></i>Sorry, something went wrong. Please try again.</p>'
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            response = '<p class="text-danger"><i class="fas fa-exclamation-circle me-2"></i>An unexpected error occurred. Please try again.</p>'

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'response': mark_safe(response)})

    return render(request, 'core/chatbot.html', {
        'response': response,
        'is_first_message': len(chat_history) == 0
    })