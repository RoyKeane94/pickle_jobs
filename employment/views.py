from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobPosting, JobSkill, JobStage
from .forms import JobPostingForm



def employer_dashboard(request):
    # Placeholder data - replace with actual data from your models
    active_jobs_data = [
        {
            "title": "Senior Frontend Developer",
            "department": "Engineering",
            "location": "San Francisco, CA (Remote)",
            "applications": 18,
            "views": 243,
            "posted_ago": "2 weeks ago"
        },
        {
            "title": "UX/UI Designer",
            "department": "Design",
            "location": "San Francisco, CA (Hybrid)",
            "applications": 12,
            "views": 197,
            "posted_ago": "1 week ago"
        },
        {
            "title": "Backend Developer",
            "department": "Engineering",
            "location": "Remote",
            "applications": 8,
            "views": 120,
            "posted_ago": "3 days ago"
        }
    ]

    recent_messages_data = [

    ]

    recent_applications_data = [
        
    ]

    context = {
        'active_jobs': active_jobs_data,
        'recent_messages': recent_messages_data,
        'recent_applications': recent_applications_data,
        # Add other context variables your template might need, e.g.
        # 'user_company_name': request.user.employer_profile.company_name if hasattr(request.user, 'employer_profile') else request.user.username
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
            job_posting.employer = request.user.employerprofile
            job_posting.published = False
            job_posting.save()

            if 'skills' in form.cleaned_data:
                job_posting.skills.set(form.cleaned_data['skills'])
            
            application_stage_names = request.POST.getlist('application_stages')
            if application_stage_names:
                job_posting.stage.clear()
                for stage_name in application_stage_names:
                    if stage_name.strip():
                        stage, created = JobStage.objects.get_or_create(name=stage_name.strip())
                        job_posting.stage.add(stage)
            
            messages.success(request, 'Job posting saved for review.')
            return redirect('employment:employer_application_review', job_id=job_posting.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobPostingForm()
        existing_stage_names = []
    
    context = {
        'form': form,
        'existing_stage_names': existing_stage_names,
    }
    return render(request, 'employment/employer/application/employer_application_creation.html', context)

@login_required
def employer_application_review(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employerprofile)
    
    context = {
        'job_posting': job_posting,
    }
    return render(request, 'employment/employer/application/employer_application_review.html', context)

@login_required
def employer_application_edit(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employerprofile)
    existing_stage_names = [stage.name for stage in job_posting.stage.all()]
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            edited_posting = form.save(commit=False)
            edited_posting.published = False
            edited_posting.save()

            if 'skills' in form.cleaned_data:
                edited_posting.skills.set(form.cleaned_data['skills'])
            else:
                edited_posting.skills.clear()
            
            application_stage_names = request.POST.getlist('application_stages')
            edited_posting.stage.clear()
            if application_stage_names:
                for stage_name in application_stage_names:
                    if stage_name.strip():
                        stage, created = JobStage.objects.get_or_create(name=stage_name.strip())
                        edited_posting.stage.add(stage)

            messages.success(request, 'Job posting updated and saved for review.')
            return redirect('employment:employer_application_review', job_id=job_posting.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobPostingForm(instance=job_posting)
    
    context = {
        'form': form,
        'job_posting': job_posting, 
        'existing_stage_names': existing_stage_names,
    }
    return render(request, 'employment/employer/application/employer_application_creation.html', context)

@login_required
def employer_application_submit(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employerprofile)
    
    if request.method == 'POST':
        job_posting.published = True
        job_posting.save()
        messages.success(request, 'Job posting published successfully!')
        return redirect('employment:employer_dashboard')
    
    return redirect('employment:employer_application_review', job_id=job_posting.id)
