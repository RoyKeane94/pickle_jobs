from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import JobPosting, JobSkill, JobStage, JobApplication, EmployeeExperience, EmployeeEducation, PickleProfile, EmployeeInterest, Location, School
from .forms import JobPostingForm, EmployeeExperienceForm, EmployeeEducationForm
from accounts.models import Company



@login_required
def employer_dashboard(request):
    """
    Renders the employer dashboard with real-time data about job postings,
    applications, and key statistics for the logged-in employer.
    """
    # Ensure user has an employer profile
    if not hasattr(request.user, 'employer_profile'):
        messages.error(request, 'You need an employer profile to access this dashboard.')
        return redirect('core:home')
    
    employer_profile = request.user.employer_profile
    
    # Get all job postings for this employer with optimized queries
    all_jobs = JobPosting.objects.filter(employer=employer_profile).select_related('employer__company')
    
    # Separate active (published) and draft jobs
    active_jobs = all_jobs.filter(published=True).annotate(
        application_count=Count('jobapplication')
    ).order_by('-created_at')
    
    draft_jobs = all_jobs.filter(published=False).order_by('-updated_at')
    
    # Get recent applications for this employer's jobs
    recent_applications = JobApplication.objects.filter(
        job_posting__employer=employer_profile
    ).select_related(
        'employee__user', 'job_posting'
    ).order_by('-created_at')[:5]
    
    # Calculate key statistics
    total_jobs = all_jobs.count()
    active_jobs_count = active_jobs.count()
    draft_jobs_count = draft_jobs.count()
    total_applications = JobApplication.objects.filter(
        job_posting__employer=employer_profile
    ).count()
    
    # Statistics for the dashboard cards
    stats = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs_count,
        'draft_jobs': draft_jobs_count,
        'total_applications': total_applications,
    }
    
    # Messages placeholder - this would come from a messaging system when implemented
    recent_messages = []
    
    context = {
        'stats': stats,
        'active_jobs': active_jobs,
        'draft_jobs': draft_jobs,
        'recent_applications': recent_applications,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'employment/employer/dashboard/employer_dashboard.html', context)

@login_required
def employee_dashboard(request):
    """
    Renders the employee dashboard with job recommendations, applications, and CV status.
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to access this dashboard.')
        return redirect('core:home')
    
    employee_profile = request.user.employee_profile
    
    # Get or create PickleProfile
    pickle_profile, created = PickleProfile.objects.get_or_create(
        employee=employee_profile,
        defaults={'cv_blank': True}
    )
    
    # CV completion status from PickleProfile
    cv_completed = pickle_profile.cv_completed
    cv_blank = pickle_profile.cv_blank
    
    # CV progress tracking
    cv_progress = {
        'cv_started': not pickle_profile.cv_blank,
        'experience_completed': pickle_profile.experience_completed,
        'education_completed': pickle_profile.education_completed,
        'skills_interests_completed': pickle_profile.skills_completed and pickle_profile.interests_completed,
    }
    
    # Get latest job postings (5 most recent)
    latest_jobs = JobPosting.objects.filter(
        published=True,
        accepting_application_date__gte=timezone.now().date()
    ).select_related('employer__company').prefetch_related('skills').order_by('-created_at')[:5]
    
    # Add has_applied flag to jobs
    for job in latest_jobs:
        job.has_applied = JobApplication.objects.filter(
            job_posting=job,
            employee=employee_profile
        ).exists()
    
    # Get user's applications
    my_applications = JobApplication.objects.filter(
        employee=employee_profile
    ).select_related('job_posting__employer__company', 'stage').order_by('-created_at')[:5]
    
    # Get upcoming interviews (placeholder - would need Interview model)
    upcoming_interviews = []
    
    # Get recent messages (placeholder)
    recent_messages = []
    
    # Calculate statistics
    total_applications = JobApplication.objects.filter(employee=employee_profile).count()
    pending_applications = JobApplication.objects.filter(
        employee=employee_profile,
        stage__name__in=['Applied', 'Under Review']
    ).count()
    interviews = 0  # Placeholder
    available_jobs = JobPosting.objects.filter(
        published=True,
        accepting_application_date__gte=timezone.now().date()
    ).count()
    
    stats = {
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'interviews': interviews,
        'available_jobs': available_jobs,
    }
    
    context = {
        'stats': stats,
        'latest_jobs': latest_jobs,
        'my_applications': my_applications,
        'upcoming_interviews': upcoming_interviews,
        'recent_messages': recent_messages,
        'cv_completed': cv_completed,
        'cv_blank': cv_blank,
        'cv_progress': cv_progress,
        'pickle_profile': pickle_profile,
    }
    
    return render(request, 'employment/employee/dashboard/employee_dashboard.html', context)

@login_required
def employee_jobs_overview(request):
    """
    Display all available jobs with search and filtering capabilities.
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to access this page.')
        return redirect('core:home')
    
    employee_profile = request.user.employee_profile
    
    # Base queryset for published jobs
    jobs = JobPosting.objects.filter(
        published=True,
        accepting_application_date__gte=timezone.now().date()
    ).select_related('employer__company').prefetch_related('skills')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(employer__company__name__icontains=search_query)
        )
    
    # Location filter
    location_filter = request.GET.get('location', '')
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
    
    # Skills filter
    skills_filter = request.GET.get('skills', '')
    if skills_filter:
        jobs = jobs.filter(skills__id=skills_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-hourly_rate', 'hourly_rate', 'title']
    if sort_by in valid_sorts:
        jobs = jobs.order_by(sort_by)
    else:
        jobs = jobs.order_by('-created_at')
    
    # Add application status to each job
    for job in jobs:
        job.has_applied = JobApplication.objects.filter(
            job_posting=job,
            employee=employee_profile
        ).exists()
        job.application_count = JobApplication.objects.filter(job_posting=job).count()
    
    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    locations = JobPosting.objects.filter(published=True).values_list('location', flat=True).distinct()
    skills = JobSkill.objects.all()
    
    context = {
        'jobs': page_obj,
        'page_obj': page_obj,
        'total_jobs': jobs.count(),
        'locations': locations,
        'skills': skills,
    }
    
    return render(request, 'employment/employee/jobs/jobs_overview.html', context)

@login_required
def employee_cv_create(request):
    """
    Handle CV creation for employees.
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to create a CV.')
        return redirect('core:home')
    
    employee_profile = request.user.employee_profile
    
    # Get or create PickleProfile
    pickle_profile, created = PickleProfile.objects.get_or_create(
        employee=employee_profile,
        defaults={'cv_blank': True}
    )
    
    if request.method == 'POST':
        has_experience = False
        has_education = False
        has_skills = False
        
        # Process experience forms
        experience_count = 0
        while f'job_title_{experience_count}' in request.POST:
            job_title = request.POST.get(f'job_title_{experience_count}')
            if job_title:  # Only create if job title is provided
                experience = EmployeeExperience(
                    employee=employee_profile,
                    job_title=job_title,
                    experience_level=request.POST.get(f'experience_level_{experience_count}', ''),
                    experience_description=request.POST.get(f'experience_description_{experience_count}', ''),
                    experience_start_date=request.POST.get(f'experience_start_date_{experience_count}') or None,
                    experience_end_date=request.POST.get(f'experience_end_date_{experience_count}') or None,
                )
                experience.save()
                has_experience = True
                
                # Handle skills
                skills = request.POST.getlist(f'skills_{experience_count}')
                if skills:
                    experience.skills.set(skills)
                    has_skills = True
            
            experience_count += 1
        
        # Process education forms
        education_count = 0
        while f'school_name_{education_count}' in request.POST:
            school_name = request.POST.get(f'school_name_{education_count}')
            if school_name:  # Only create if school name is provided
                education = EmployeeEducation(
                    employee=employee_profile,
                    level=request.POST.get(f'level_{education_count}', ''),
                    field_of_study=request.POST.get(f'field_of_study_{education_count}', ''),
                    start_date=request.POST.get(f'education_start_date_{education_count}') or None,
                    end_date=request.POST.get(f'education_end_date_{education_count}') or None,
                )
                education.save()
                has_education = True
            
            education_count += 1
        
        # Update PickleProfile flags
        pickle_profile.cv_blank = False
        pickle_profile.experience_completed = has_experience
        pickle_profile.education_completed = has_education
        pickle_profile.skills_completed = has_skills
        
        # Check if CV is fully completed
        pickle_profile.cv_completed = (
            pickle_profile.experience_completed and 
            pickle_profile.education_completed and 
            pickle_profile.skills_completed
        )
        
        pickle_profile.save()
        
        messages.success(request, 'Your PickleCV has been created successfully!')
        return redirect('employment:employee_dashboard')
    
    # GET request - show form
    experience_form = EmployeeExperienceForm()
    education_form = EmployeeEducationForm()
    
    context = {
        'experience_form': experience_form,
        'education_form': education_form,
    }
    
    return render(request, 'employment/employee/cv/forms/cv_creation_form.html', context)

@login_required
def employee_cv_update(request):
    """
    Handle CV updates for employees.
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to update your CV.')
        return redirect('core:home')
    
    employee_profile = request.user.employee_profile
    
    # Get or create PickleProfile
    pickle_profile, created = PickleProfile.objects.get_or_create(
        employee=employee_profile,
        defaults={'cv_blank': True}
    )
    
    # Get existing data
    existing_experiences = EmployeeExperience.objects.filter(employee=employee_profile)
    existing_educations = EmployeeEducation.objects.filter(employee=employee_profile)
    
    if request.method == 'POST':
        # Clear existing data
        existing_experiences.delete()
        existing_educations.delete()
        
        has_experience = False
        has_education = False
        has_skills = False
        
        # Process experience forms (same logic as create)
        experience_count = 0
        while f'job_title_{experience_count}' in request.POST:
            job_title = request.POST.get(f'job_title_{experience_count}')
            if job_title:
                experience = EmployeeExperience(
                    employee=employee_profile,
                    job_title=job_title,
                    experience_level=request.POST.get(f'experience_level_{experience_count}', ''),
                    experience_description=request.POST.get(f'experience_description_{experience_count}', ''),
                    experience_start_date=request.POST.get(f'experience_start_date_{experience_count}') or None,
                    experience_end_date=request.POST.get(f'experience_end_date_{experience_count}') or None,
                )
                experience.save()
                has_experience = True
                
                # Handle skills
                skills = request.POST.getlist(f'skills_{experience_count}')
                if skills:
                    experience.skills.set(skills)
                    has_skills = True
            
            experience_count += 1
        
        # Process education forms
        education_count = 0
        while f'school_name_{education_count}' in request.POST:
            school_name = request.POST.get(f'school_name_{education_count}')
            if school_name:
                education = EmployeeEducation(
                    employee=employee_profile,
                    level=request.POST.get(f'level_{education_count}', ''),
                    field_of_study=request.POST.get(f'field_of_study_{education_count}', ''),
                    start_date=request.POST.get(f'education_start_date_{education_count}') or None,
                    end_date=request.POST.get(f'education_end_date_{education_count}') or None,
                )
                education.save()
                has_education = True
            
            education_count += 1
        
        # Update PickleProfile flags
        pickle_profile.cv_blank = False
        pickle_profile.experience_completed = has_experience
        pickle_profile.education_completed = has_education
        pickle_profile.skills_completed = has_skills
        
        # Check if CV is fully completed
        pickle_profile.cv_completed = (
            pickle_profile.experience_completed and 
            pickle_profile.education_completed and 
            pickle_profile.skills_completed
        )
        
        pickle_profile.save()
        
        messages.success(request, 'Your PickleCV has been updated successfully!')
        return redirect('employment:employee_dashboard')
    
    # GET request - show form with existing data
    all_skills = JobSkill.objects.all()
    
    context = {
        'existing_experiences': existing_experiences,
        'existing_educations': existing_educations,
        'all_skills': all_skills,
    }
    
    return render(request, 'employment/employee/cv/forms/cv_update_form.html', context)

@login_required
def employer_application_create(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.employer = request.user.employer_profile
            job_posting.published = False
            job_posting.save()

            # Handle skills - clear first, then set if any are selected
            job_posting.skills.clear()
            if 'skills' in form.cleaned_data and form.cleaned_data['skills']:
                job_posting.skills.set(form.cleaned_data['skills'])
            
            messages.success(request, 'Job posting saved successfully! Please review before publishing.')
            return redirect('employment:employer_application_review', job_id=job_posting.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobPostingForm()
    
    context = {
        'form': form,
    }
    return render(request, 'employment/employer/application/employer_application_creation.html', context)

@login_required
def employer_application_review(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    context = {
        'job_posting': job_posting,
    }
    return render(request, 'employment/employer/application/employer_application_review.html', context)

@login_required
def employer_application_edit(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            edited_posting = form.save(commit=False)
            edited_posting.published = False
            edited_posting.save()

            # Handle skills - clear first, then set if any are selected
            edited_posting.skills.clear()
            if 'skills' in form.cleaned_data and form.cleaned_data['skills']:
                edited_posting.skills.set(form.cleaned_data['skills'])
            
            messages.success(request, 'Job posting updated successfully! Please review before publishing.')
            return redirect('employment:employer_application_review', job_id=job_posting.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobPostingForm(instance=job_posting)
    
    context = {
        'form': form,
        'job_posting': job_posting, 
    }
    return render(request, 'employment/employer/application/employer_application_creation.html', context)

@login_required
def employer_application_submit(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        job_posting.published = True
        job_posting.save()
        messages.success(request, f'Job posting "{job_posting.title}" has been published successfully!')
        return redirect('employment:employer_dashboard')
    
    context = {
        'job_posting': job_posting,
    }
    return render(request, 'employment/employer/application/employer_application_review.html', context)

@login_required
def employer_application_delete(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        title = job_posting.title
        job_posting.delete()
        messages.success(request, f'Job posting "{title}" has been deleted successfully!')
        return redirect('employment:employer_dashboard')
    
    context = {
        'job_posting': job_posting,
    }
    return render(request, 'employment/employer/application/employer_application_delete_confirm.html', context)

@login_required
def employee_cv_create_employment(request):
    """
    Handle employment section of CV creation (Step 1 of 3).
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to create a CV.')
        return redirect('core:home')
    
    employee_profile = request.user.employee_profile
    
    if request.method == 'POST':
        # Store employment data in session
        employment_data = []
        experience_count = 0
        
        while f'job_title_{experience_count}' in request.POST:
            job_title = request.POST.get(f'job_title_{experience_count}')
            if job_title:  # Only store if job title is provided
                experience_data = {
                    'job_title': job_title,
                    'employer': request.POST.get(f'employer_{experience_count}', ''),
                    'location': request.POST.get(f'location_{experience_count}', ''),
                    'experience_level': request.POST.get(f'experience_level_{experience_count}', ''),
                    'experience_description': request.POST.get(f'experience_description_{experience_count}', ''),
                    'experience_start_date': request.POST.get(f'experience_start_date_{experience_count}', ''),
                    'experience_end_date': request.POST.get(f'experience_end_date_{experience_count}', ''),
                    'skills': request.POST.getlist(f'skills_{experience_count}')
                }
                employment_data.append(experience_data)
            experience_count += 1
        
        # Store in session
        request.session['cv_employment_data'] = employment_data
        
        messages.success(request, 'Employment information saved! Now add your education.')
        return redirect('employment:employee_cv_create_education')
    
    # GET request - show form
    experience_form = EmployeeExperienceForm()
    
    context = {
        'experience_form': experience_form,
    }
    
    return render(request, 'employment/employee/cv/forms/creation/cv_creation_employment_form.html', context)

@login_required
def employee_cv_create_education(request):
    """
    Handle education section of CV creation (Step 2 of 3).
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to create a CV.')
        return redirect('core:home')
    
    # Check if employment data exists in session
    if 'cv_employment_data' not in request.session:
        messages.warning(request, 'Please complete the employment section first.')
        return redirect('employment:employee_cv_create_employment')
    
    employee_profile = request.user.employee_profile
    
    if request.method == 'POST':
        # Store education data in session
        education_data = []
        education_count = 0
        
        while f'school_name_{education_count}' in request.POST:
            school_name = request.POST.get(f'school_name_{education_count}')
            if school_name:  # Only store if school name is provided
                education_item = {
                    'school_name': school_name,
                    'location': request.POST.get(f'location_{education_count}', ''),
                    'level': request.POST.get(f'level_{education_count}', ''),
                    'field_of_study': request.POST.get(f'field_of_study_{education_count}', ''),
                    'start_date': request.POST.get(f'start_date_{education_count}', ''),
                    'end_date': request.POST.get(f'end_date_{education_count}', ''),
                }
                education_data.append(education_item)
            education_count += 1
        
        # Store in session
        request.session['cv_education_data'] = education_data
        
        messages.success(request, 'Education information saved! Now add your skills and interests.')
        return redirect('employment:employee_cv_create_skills_interests')
    
    # GET request - show form
    education_form = EmployeeEducationForm()
    
    context = {
        'education_form': education_form,
    }
    
    return render(request, 'employment/employee/cv/forms/creation/cv_creation_education_form.html', context)

@login_required
def employee_cv_create_skills_interests(request):
    """
    Handle skills & interests section of CV creation (Step 3 of 3).
    """
    # Check if user has employee profile
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'You need an employee profile to create a CV.')
        return redirect('core:home')
    
    # Check if previous data exists in session
    if 'cv_employment_data' not in request.session:
        messages.warning(request, 'Please complete the employment section first.')
        return redirect('employment:employee_cv_create_employment')
    
    if 'cv_education_data' not in request.session:
        messages.warning(request, 'Please complete the education section first.')
        return redirect('employment:employee_cv_create_education')
    
    employee_profile = request.user.employee_profile
    
    if request.method == 'POST':
        # Get skills and interests from form
        selected_skills = request.POST.getlist('skills')
        selected_interests = request.POST.getlist('interests')
        
        # Get data from session
        employment_data = request.session.get('cv_employment_data', [])
        education_data = request.session.get('cv_education_data', [])
        
        # Create PickleProfile and set completion flags
        pickle_profile, created = PickleProfile.objects.get_or_create(
            employee=employee_profile,
            defaults={'cv_blank': True}
        )
        
        # Clear existing data
        EmployeeExperience.objects.filter(employee=employee_profile).delete()
        EmployeeEducation.objects.filter(employee=employee_profile).delete()
        
        has_experience = False
        has_education = False
        has_skills = bool(selected_skills)
        has_interests = bool(selected_interests)
        
        # Create experience records
        for exp_data in employment_data:
            if exp_data.get('job_title'):
                # Get or create Company and Location
                company = get_or_create_company(exp_data.get('employer'))
                location = get_or_create_location(exp_data.get('location'))
                
                experience = EmployeeExperience(
                    employee=employee_profile,
                    job_title=exp_data['job_title'],
                    employer=company,
                    location=location,
                    experience_level=exp_data.get('experience_level', ''),
                    experience_description=exp_data.get('experience_description', ''),
                    experience_start_date=exp_data.get('experience_start_date') or None,
                    experience_end_date=exp_data.get('experience_end_date') or None,
                )
                experience.save()
                has_experience = True
                
                # Add skills to experience
                if exp_data.get('skills'):
                    experience.skills.set(exp_data['skills'])
        
        # Create education records
        for edu_data in education_data:
            if edu_data.get('school_name'):
                # Get or create School and Location
                school = get_or_create_school(edu_data.get('school_name'))
                location = get_or_create_location(edu_data.get('location'))
                
                education = EmployeeEducation(
                    employee=employee_profile,
                    school_name=school,
                    location=location,
                    level=edu_data.get('level', ''),
                    field_of_study=edu_data.get('field_of_study', ''),
                    start_date=edu_data.get('start_date') or None,
                    end_date=edu_data.get('end_date') or None,
                )
                education.save()
                has_education = True
        
        # Handle interests
        if selected_interests:
            # Clear existing interests
            EmployeeInterest.objects.filter(employee=employee_profile).delete()
            
            # Create new interests
            for interest_id in selected_interests:
                try:
                    from .models import Interest
                    interest = Interest.objects.get(id=interest_id)
                    EmployeeInterest.objects.create(
                        employee=employee_profile,
                        interest=interest
                    )
                except Interest.DoesNotExist:
                    pass
        
        # Update PickleProfile flags
        pickle_profile.cv_blank = False
        pickle_profile.experience_completed = has_experience
        pickle_profile.education_completed = has_education
        pickle_profile.skills_completed = has_skills
        pickle_profile.interests_completed = has_interests
        
        # Check if CV is fully completed
        pickle_profile.cv_completed = (
            pickle_profile.experience_completed and 
            pickle_profile.education_completed and 
            (pickle_profile.skills_completed or pickle_profile.interests_completed)
        )
        
        pickle_profile.save()
        
        # Clear session data
        if 'cv_employment_data' in request.session:
            del request.session['cv_employment_data']
        if 'cv_education_data' in request.session:
            del request.session['cv_education_data']
        
        messages.success(request, 'Your PickleCV has been created successfully!')
        return redirect('employment:employee_dashboard')
    
    # GET request - show form
    all_skills = JobSkill.objects.all()
    
    # Get interests from Interest model if it exists
    try:
        from .models import Interest
        all_interests = Interest.objects.all()
    except ImportError:
        all_interests = []
    
    context = {
        'skills': all_skills,
        'interests': all_interests,
    }
    
    return render(request, 'employment/employee/cv/forms/creation/cv_creation_skills_interests_form.html', context)

# Autocomplete API endpoints
@require_http_methods(["GET"])
def company_autocomplete(request):
    """
    Optimized API endpoint for company name autocomplete suggestions.
    """
    query = request.GET.get('term', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Optimized query with limit and only select name field
    companies = Company.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).order_by('name')[:8]  # Reduced to 8 for faster response
    
    # Convert to list to avoid query execution delay
    suggestions = [{'label': name, 'value': name} for name in list(companies)]
    return JsonResponse(suggestions, safe=False)

@require_http_methods(["GET"])
def location_autocomplete(request):
    """
    Optimized API endpoint for location name autocomplete suggestions.
    """
    query = request.GET.get('term', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Optimized query with limit and only select name field
    locations = Location.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).order_by('name')[:8]  # Reduced to 8 for faster response
    
    # Convert to list to avoid query execution delay
    suggestions = [{'label': name, 'value': name} for name in list(locations)]
    return JsonResponse(suggestions, safe=False)

@require_http_methods(["GET"])
def school_autocomplete(request):
    """
    Optimized API endpoint for school name autocomplete suggestions.
    """
    query = request.GET.get('term', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Optimized query with limit and only select name field
    schools = School.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).order_by('name')[:8]  # Reduced to 8 for faster response
    
    # Convert to list to avoid query execution delay
    suggestions = [{'label': name, 'value': name} for name in list(schools)]
    return JsonResponse(suggestions, safe=False)

def get_or_create_company(company_name):
    """
    Helper function to get or create a Company instance.
    """
    if not company_name:
        return None
    
    company, created = Company.objects.get_or_create(
        name=company_name,
        defaults={'description': ''}
    )
    return company

def get_or_create_location(location_name):
    """
    Helper function to get or create a Location instance.
    """
    if not location_name:
        return None
    
    location, created = Location.objects.get_or_create(
        name=location_name
    )
    return location

def get_or_create_school(school_name):
    """
    Helper function to get or create a School instance.
    """
    if not school_name:
        return None
    
    school, created = School.objects.get_or_create(
        name=school_name
    )
    return school
