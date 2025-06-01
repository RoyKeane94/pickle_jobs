from django.urls import path
from . import views

app_name = 'employment'

urlpatterns = [
    #Employer
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/application/create/', views.employer_application_create, name='employer_application_create'),
    path('employer/application/<int:job_id>/review/', views.employer_application_review, name='employer_application_review'),
    path('employer/application/<int:job_id>/edit/', views.employer_application_edit, name='employer_application_edit'),
    path('employer/application/<int:job_id>/submit/', views.employer_application_submit, name='employer_application_submit'),
    path('employer/application/<int:job_id>/delete/', views.employer_application_delete, name='employer_application_delete'),

    #Employee
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/jobs/', views.employee_jobs_overview, name='employee_jobs_overview'),
    path('employee/cv/create/', views.employee_cv_create, name='employee_cv_create'),
    path('employee/cv/create/employment/', views.employee_cv_create_employment, name='employee_cv_create_employment'),
    path('employee/cv/create/education/', views.employee_cv_create_education, name='employee_cv_create_education'),
    path('employee/cv/create/skills-interests/', views.employee_cv_create_skills_interests, name='employee_cv_create_skills_interests'),
    path('employee/cv/update/', views.employee_cv_update, name='employee_cv_update'),
    
    # API endpoints for autocomplete
    path('api/companies/autocomplete/', views.company_autocomplete, name='company_autocomplete'),
    path('api/locations/autocomplete/', views.location_autocomplete, name='location_autocomplete'),
    path('api/schools/autocomplete/', views.school_autocomplete, name='school_autocomplete'),
]
