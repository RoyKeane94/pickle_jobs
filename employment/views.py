from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import JobPosting, JobSkill, JobStage, JobApplication
from .forms import JobPostingForm



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
    # Placeholder data - replace with actual data from your models
    applied_jobs_data = [
        {
            "title": "Senior Frontend Developer",
            "company": "Tech Solutions Inc.",
            "location": "San Francisco, CA (Remote)",
            "status": "Application Received",
            "applied_date": "Aug 15, 2023",
        },
        {
            "title": "UX/UI Designer",
            "company": "Creative Agency",
            "location": "San Francisco, CA (Hybrid)",
            "status": "Under Review",
            "applied_date": "Aug 20, 2023",
        }
    ]
    
    recommended_jobs_data = [
        {
            "title": "Backend Developer",
            "company": "Software Solutions Corp",
            "location": "Remote",
            "salary": "$120,000 - $150,000",
            "posted_ago": "3 days ago"
        },
        {
            "title": "Software Engineer",
            "company": "Tech Innovations",
            "location": "New York, NY",
            "salary": "$100,000 - $130,000",
            "posted_ago": "1 week ago"
        },
        {
            "title": "Product Designer",
            "company": "Design World",
            "location": "Austin, TX (Hybrid)",
            "salary": "$90,000 - $110,000",
            "posted_ago": "2 days ago"
        }
    ]
    
    recent_activity_data = [
        {
            "action": "Profile viewed",
            "company": "Tech Solutions Inc.",
            "date": "Yesterday"
        },
        {
            "action": "Resume downloaded",
            "company": "Creative Agency",
            "date": "3 days ago"
        }
    ]
    
    context = {
        'applied_jobs': applied_jobs_data,
        'recommended_jobs': recommended_jobs_data,
        'recent_activity': recent_activity_data,
        # Add other context variables your template might need
    }
    return render(request, 'employment/employee/dashboard/employee_dashboard.html', context)

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
        messages.success(request, 'Job posting published successfully!')
        return redirect('employment:employer_dashboard')
    
    return redirect('employment:employer_application_review', job_id=job_posting.id)

@login_required
def employer_application_delete(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        job_title = job_posting.title
        job_posting.delete()
        messages.success(request, f'Job posting "{job_title}" has been deleted successfully.')
        return redirect('employment:employer_dashboard')
    
    # If not POST, redirect back to review page
    return redirect('employment:employer_application_review', job_id=job_posting.id)
