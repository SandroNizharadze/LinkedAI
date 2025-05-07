67:def register(request):
68-    if request.user.is_authenticated:
69-        return redirect('job_list')
70-    
71-    if request.method == 'POST':
72-        form = UserRegistrationForm(request.POST, request.FILES)
73-        if form.is_valid():
74-            try:
75-                # Get the form data
76-                email = form.cleaned_data.get('email')
77-                password = form.cleaned_data.get('password1')
78-                first_name = form.cleaned_data.get('first_name')
79-                last_name = form.cleaned_data.get('last_name')
80-                
81-                # Step 1: Create Django User object
82-                user = User.objects.create_user(
83-                    username=email,  # Use email as username
84-                    email=email,
85-                    password=password,
86-                    first_name=first_name,
87-                    last_name=last_name
88-                )
89-                
90-                # Step 2: Create the UserProfile instance manually from form data
91-                user_profile = UserProfile(
92-                    user=user,
93-                    role='user',  # Default role
94-                    profile_picture=form.cleaned_data.get('profile_picture'),
95-                    interests=form.cleaned_data.get('interests', ''),
96-                    fields=form.cleaned_data.get('fields', ''),
97-                    experience=form.cleaned_data.get('experience', ''),
98-                    job_preferences=form.cleaned_data.get('job_preferences', '')
99-                )
100-                
101-                # Step 3: Save the profile
102-                user_profile.save()
103-                
104-                # Log the user in
105-                user.backend = 'django.contrib.auth.backends.ModelBackend'
106-                login(request, user)
107-                messages.success(request, "Registration successful! Welcome to Linked AI.")
108-                return redirect('job_list')
109-            except Exception as e:
110-                # If any error occurs during user creation, delete the user to prevent orphaned data
111-                if 'user' in locals() and user is not None and user.id is not None:
112-                    try:
113-                        user.delete()
114-                    except:
115-                        # If we can't delete the user, just continue to show the error
116-                        pass
117-                messages.error(request, f"Registration error: {str(e)}")
118-        else:
119-            messages.error(request, "Please correct the errors below.")
120-    else:
121-        form = UserRegistrationForm()
122-    
123-    return render(request, 'core/register.html', {'form': form})
124-
125-@login_required
126-def profile(request):
127-    user_profile = request.user.userprofile
