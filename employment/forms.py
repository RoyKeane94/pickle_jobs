from django import forms
from django.forms import DateInput
from .models import JobPosting, JobSkill, JobStage

class JobPostingForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=JobSkill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hidden'}),
        required=False
    )
    
    # stage = forms.ModelMultipleChoiceField(
    #     queryset=JobStage.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False
    # )
    
    accepting_application_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = JobPosting
        fields = [
            'title', 
            'description', 
            'location', 
            'hourly_rate', 
            'estimated_hours',
            'skills', 
            # 'stage', 
            'accepting_application_date',
            'additional_info'
        ]
        exclude = ['employer', 'published']
