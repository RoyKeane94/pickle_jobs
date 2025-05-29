from django import forms
from django.forms import DateInput
from .models import JobPosting, JobSkill, JobStage

class JobPostingForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=JobSkill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hidden'}),
        required=False
    )
    
    accepting_application_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = JobPosting
        fields = [
            # General
            'title', 
            'description', 
            'location', 
            'skills', 
            # Process
            'accepting_application_date',
            # Compensation
            'hourly_rate', 
            'estimated_hours',
            # Additional
            'additional_info'
        ]
        exclude = ['employer', 'published']
