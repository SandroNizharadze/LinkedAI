import requests
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from ..models import JobListing, UserProfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

def find_and_link_job(job_title):
    """Helper function to find a job by title and create a link to it."""
    logger.debug(f"Searching for job: {job_title}")
    
    # Clean up the title for more accurate matching
    clean_title = job_title.strip().lower()
    
    try:
        # First try exact match
        exact_match = JobListing.objects.filter(title__iexact=clean_title).first()
        if exact_match:
            logger.debug(f"Found exact match for {job_title}: {exact_match.title}")
            return f'/jobs/{exact_match.id}/'
        
        # Then try if the job title is contained in our job listing
        contains_match = JobListing.objects.filter(title__icontains=clean_title).first()
        if contains_match:
            logger.debug(f"Found contains match for {job_title}: {contains_match.title}")
            return f'/jobs/{contains_match.id}/'
            
        # If that doesn't work, try each word in the job title
        words = clean_title.split()
        if len(words) > 1:
            # Try searching by the first two words (often most significant)
            key_terms = ' '.join(words[:2]) 
            word_match = JobListing.objects.filter(title__icontains=key_terms).first()
            if word_match:
                logger.debug(f"Found word match for {job_title} using {key_terms}: {word_match.title}")
                return f'/jobs/{word_match.id}/'
        
        # Last resort - check if any job contains any of these words
        for word in words:
            if len(word) > 3:  # Only use meaningful words (not "the", "and", etc)
                word_match = JobListing.objects.filter(title__icontains=word).first()
                if word_match:
                    logger.debug(f"Found single word match for {job_title} using {word}: {word_match.title}")
                    return f'/jobs/{word_match.id}/'
                    
        logger.debug(f"No job match found for: {job_title}")
        return None
    
    except Exception as e:
        logger.error(f"Error finding job match for '{job_title}': {str(e)}")
        return None

def process_message_with_job_links(message):
    """Process a message to add links to job titles."""
    lines = message.split('\n')
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
                job_url = find_and_link_job(job_title)
                if job_url:
                    # Replace the span with a link
                    line = line.replace(
                        f'<span class="job-title">{job_title}</span>',
                        f'<a href="{job_url}" class="job-title-link"><span class="job-title"><i class="fas fa-briefcase me-2"></i>{job_title}</span></a>'
                    )
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
        
    return "".join(formatted_response)

def get_conversation_name(chat_history):
    """Extract a name for the conversation based on the first message"""
    if not chat_history:
        return "New Conversation"
    
    # First message is from user
    first_message = chat_history[0]
    
    # Truncate long messages
    if len(first_message) > 30:
        # Truncate at the last complete word before 30 chars
        last_space = first_message[:30].rfind(' ')
        if last_space > 10:  # If we found a space at a reasonable position
            return first_message[:last_space] + "..."
        else:
            return first_message[:27] + "..."
    
    return first_message

@login_required
def chatbot(request):
    response = ""
    user_profile = None

    # Initialize conversations dictionary if it doesn't exist
    if 'conversations' not in request.session:
        request.session['conversations'] = {}
    
    # Clean up empty conversations first - remove any empty conversations except the most recent one
    conversations = request.session['conversations']
    empty_convs = []
    for conv_id, conv_data in conversations.items():
        # Check if conversation is empty
        if isinstance(conv_data, dict) and not conv_data.get('messages', []):
            empty_convs.append((conv_id, conv_data.get('created_at', '')))
    
    # Sort empty conversations by created_at (newest first)
    empty_convs.sort(key=lambda x: x[1], reverse=True)
    
    # Keep only the newest empty conversation, delete the rest
    if len(empty_convs) > 1:
        for i, (conv_id, _) in enumerate(empty_convs):
            if i > 0:  # Skip the first (newest) one
                del request.session['conversations'][conv_id]
        request.session.modified = True
    
    # Handle conversation_id from GET or POST
    requested_conv_id = request.GET.get('conversation_id', None) or request.POST.get('conversation_id', None)
    creating_new_chat = bool(request.GET.get('new_chat'))
    
    # Case 1: User clicked "New Chat" button
    if creating_new_chat:
        # Check if there's already an empty conversation
        newest_empty_conv = empty_convs[0][0] if empty_convs else None
        
        if newest_empty_conv:
            # Use the existing empty conversation
            conversation_id = newest_empty_conv
        else:
            # Create a new one
            conversation_id = str(uuid.uuid4())
            request.session['conversations'][conversation_id] = {
                'messages': [],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        
        request.session['conversation_id'] = conversation_id
        is_new_chat = True
        
    # Case 2: User selected a specific conversation
    elif requested_conv_id and requested_conv_id in request.session['conversations']:
        conversation_id = requested_conv_id
        request.session['conversation_id'] = conversation_id
        is_new_chat = False
        
    # Case 3: Use the current conversation
    elif 'conversation_id' in request.session and request.session['conversation_id'] in request.session['conversations']:
        conversation_id = request.session['conversation_id']
        is_new_chat = False
        
    # Case 4: No valid conversation exists, create a new one
    else:
        conversation_id = str(uuid.uuid4())
        request.session['conversation_id'] = conversation_id
        request.session['conversations'][conversation_id] = {
            'messages': [],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        is_new_chat = True
    
    # Get the current conversation's chat history
    chat_data = request.session['conversations'][conversation_id]
    if isinstance(chat_data, list):  # Handle legacy format
        chat_history = chat_data
        # Convert to new format
        request.session['conversations'][conversation_id] = {
            'messages': chat_history,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        chat_data = request.session['conversations'][conversation_id]
    
    chat_history = chat_data.get('messages', [])

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
4. IMPORTANT: When mentioning ANY job title, ALWAYS wrap it in <span class="job-title">Job Title</span> tags. This enables the system to create links to those jobs.
5. Do not repeat or reference the user's name
6. Maintain conversation flow based on the chat history
7. If user asks about jobs and their profile is incomplete, kindly remind them to complete their profile for better recommendations
8. When suggesting jobs, prioritize those that match the user's fields and experience level

Available jobs (always use exact spelling and include these in <span class="job-title"> tags):
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
            request.session['conversations'][conversation_id]['messages'] = chat_history[-10:]  
            request.session.modified = True

            # Process the response to add job links
            response = process_message_with_job_links(raw_response)

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
            return JsonResponse({
                'response': mark_safe(response),
                'conversation_id': conversation_id
            })

    # Get all conversations for the user to show in the sidebar
    conversations = request.session.get('conversations', {})
    conversation_list = [
        {
            'id': conv_id,
            'name': get_conversation_name(conv_data.get('messages', []) if isinstance(conv_data, dict) else conv_data),
            'created_at': conv_data.get('created_at', 'Unknown date') if isinstance(conv_data, dict) else 'Unknown date',
            'is_active': conv_id == conversation_id,
            'preview': conv_data.get('messages', [])[0] if isinstance(conv_data, dict) and conv_data.get('messages', []) else "New conversation"
        }
        for conv_id, conv_data in conversations.items()
    ]

    # Sort by created_at descending (newest first)
    conversation_list.sort(key=lambda x: x['created_at'], reverse=True)

    # Format chat history for display
    formatted_chat_history = []
    for i, message in enumerate(chat_history):
        role = "user" if i % 2 == 0 else "ai"
        if role == "ai":
            # Format AI messages with the same logic used for responses
            message_content = process_message_with_job_links(message)
        else:
            # User messages don't need special formatting
            message_content = message
            
        formatted_chat_history.append({
            "role": role,
            "content": message_content
        })

    # Clean up existing duplicate "New Conversation" entries
    # This is a one-time cleanup for any existing duplicates before our fix
    new_conv_ids = []
    for conv_id, conv_data in request.session.get('conversations', {}).items():
        if isinstance(conv_data, dict):
            conv_messages = conv_data.get('messages', [])
            if not conv_messages:  # Empty conversation
                conv_name = get_conversation_name(conv_messages)
                if conv_name == "New Conversation":
                    new_conv_ids.append(conv_id)
    
    # Keep only the most recent "New Conversation" if multiple exist
    if len(new_conv_ids) > 1:
        newest_id = None
        newest_time = ""
        
        # Find the newest empty conversation
        for conv_id in new_conv_ids:
            conv_time = request.session['conversations'][conv_id].get('created_at', '')
            if not newest_id or conv_time > newest_time:
                newest_id = conv_id
                newest_time = conv_time
        
        # Delete all other empty "New Conversation" entries
        for conv_id in new_conv_ids:
            if conv_id != newest_id:
                del request.session['conversations'][conv_id]
        
        request.session.modified = True
        
        # If the current conversation was deleted, switch to the newest one
        if conversation_id not in request.session['conversations']:
            conversation_id = newest_id
            request.session['conversation_id'] = conversation_id
            # Re-fetch chat history for the new conversation
            chat_history = request.session['conversations'][conversation_id].get('messages', [])

    return render(request, 'core/chatbot.html', {
        'response': response,
        'is_first_message': len(chat_history) == 0,
        'conversation_id': conversation_id,
        'conversations': conversation_list,
        'is_new_chat': is_new_chat,
        'chat_history': formatted_chat_history
    })

@login_required
def clear_conversation(request, conversation_id):
    """Clear a specific conversation history."""
    if 'conversations' in request.session and conversation_id in request.session['conversations']:
        # Remove the conversation from the dictionary
        del request.session['conversations'][conversation_id]
        request.session.modified = True
        messages.success(request, "Conversation cleared successfully.")
    
    # If we deleted the active conversation, set a new one
    if request.session.get('conversation_id') == conversation_id:
        # Either use the first available conversation or create a new one
        if request.session.get('conversations'):
            request.session['conversation_id'] = list(request.session['conversations'].keys())[0]
        else:
            # No conversations left, redirect to new chat
            return redirect('chatbot')
    
    # Redirect back to chatbot view
    return redirect('chatbot')