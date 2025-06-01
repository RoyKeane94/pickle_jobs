from django import forms
from django.forms import DateInput
from .models import JobPosting, JobSkill, JobStage, EmployeeExperience, EmployeeEducation, Location, School, Company

class JobPostingForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=JobSkill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hidden'}),
        required=False
    )
    
    accepting_application_date = forms.DateField(
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
        })
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
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300',
                'placeholder': 'Job Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 resize-none',
                'rows': 4,
                'placeholder': 'Job Description'
            }),
            'location': forms.Select(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300',
                'placeholder': 'Hours per week'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 resize-none',
                'rows': 3,
                'placeholder': 'Additional Information'
            }),
        }

class EmployeeExperienceForm(forms.ModelForm):
    # Use autocomplete text field for employer/company
    employer = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 autocomplete-company',
            'placeholder': 'e.g. Google, Microsoft',
            'autocomplete': 'off',
            'data-autocomplete-url': '/employment/api/companies/autocomplete/'
        })
    )
    
    # Use autocomplete text field for location
    location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 autocomplete-location',
            'placeholder': 'e.g. London, UK',
            'autocomplete': 'off',
            'data-autocomplete-url': '/employment/api/locations/autocomplete/'
        })
    )
    
    skills = forms.ModelMultipleChoiceField(
        queryset=JobSkill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
        required=False
    )
    
    experience_start_date = forms.DateField(
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
        })
    )
    
    experience_end_date = forms.DateField(
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
        }),
        required=False
    )
    
    class Meta:
        model = EmployeeExperience
        fields = [
            'job_title',
            'employer',
            'location',
            'experience_level',
            'experience_description',
            'experience_start_date',
            'experience_end_date',
            'skills'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300',
                'placeholder': 'e.g. Software Engineer'
            }),
            'experience_level': forms.TextInput(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300',
                'placeholder': 'e.g. Senior, Junior, Lead'
            }),
            'experience_description': forms.Textarea(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 resize-none',
                'rows': 4,
                'placeholder': 'Describe your responsibilities and achievements...'
            }),
        }

class EmployeeEducationForm(forms.ModelForm):
    # Use autocomplete text field for school/institution
    school_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 autocomplete-school',
            'placeholder': 'e.g. University of Oxford',
            'autocomplete': 'off',
            'data-autocomplete-url': '/employment/api/schools/autocomplete/'
        })
    )
    
    # Use autocomplete text field for location
    location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300 autocomplete-location',
            'placeholder': 'e.g. Oxford, UK',
            'autocomplete': 'off',
            'data-autocomplete-url': '/employment/api/locations/autocomplete/'
        })
    )
    
    start_date = forms.DateField(
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
        }),
        required=False
    )
    
    end_date = forms.DateField(
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
        }),
        required=False
    )
    
    class Meta:
        model = EmployeeEducation
        fields = [
            'school_name',
            'location',
            'level',
            'field_of_study',
            'start_date',
            'end_date'
        ]
        widgets = {
            'field_of_study': forms.TextInput(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300',
                'placeholder': 'e.g. Computer Science, Business Administration'
            }),
            'level': forms.Select(attrs={
                'class': 'appearance-none bg-transparent border-none w-full text-gray-700 py-2 px-3 leading-tight focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 rounded-md border border-gray-300'
            }),
        }
