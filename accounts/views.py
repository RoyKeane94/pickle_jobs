from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import LoginForm, RegistrationForm

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on user type
        if request.user.user_type == 'employee':
            return redirect('employment:employee_dashboard')
        else:
            return redirect('employment:employer_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            
            if user is not None:
                login(request, user)
                # Redirect to appropriate dashboard based on user type
                if user.user_type == 'employee':
                    return redirect('employment:employee_dashboard')
                else:
                    return redirect('employment:employer_dashboard')
        else:
            # Form is not valid, but we don't need to do anything special
            # The template will display the errors
            pass
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on user type
        if request.user.user_type == 'employee':
            return redirect('employment:employee_dashboard')
        else:
            return redirect('employment:employer_dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            
            messages.success(request, "Account created successfully!")
            
            # Redirect to appropriate dashboard based on user type
            if user.user_type == 'employee':
                return redirect('employment:employee_dashboard')
            else:
                return redirect('employment:employer_dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    user_was_authenticated = request.user.is_authenticated
    logout(request)
    if user_was_authenticated:
        messages.success(request, "You have been successfully logged out.")
    return redirect('accounts:login')
