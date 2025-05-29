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
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
]
