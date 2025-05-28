from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from .models import CustomUser, Company, EmployeeProfile, EmployerProfile

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'autofocus': True,
            'id': 'email'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '********',
            'id': 'password'
        }),
        label='Password'
    )

    error_messages = {
        'invalid_login': "Please enter a correct email and password.",
        'inactive': "This account is inactive.",
    }

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class RegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('employee', 'I want to find a job'),
        ('employer', 'I want to hire talent'),
    )

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-indigo-600 focus:ring-indigo-500 h-4 w-4 border-gray-300'}),
        label='Account Type'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email'
        }),
        label='Email'
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name'
        }),
        label='First Name'
    )
    
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name'
        }),
        label='Last Name'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password'
        }),
        label='Password'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password'
        }),
        label='Confirm Password'
    )
    
    # For employers only
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter company name'
        }),
        label='Company Name',
        required=False
    )
    
    company_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter company description',
            'rows': 3
        }),
        label='Company Description',
        required=False
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2')
        
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'employer':
            company_name = cleaned_data.get('company_name')
            if not company_name:
                self.add_error('company_name', 'Company name is required for employer accounts')
                
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
            
            # Create the appropriate profile
            if user.user_type == 'employee':
                EmployeeProfile.objects.create(user=user)
            else:
                # Create or get the company
                company = Company.objects.create(
                    name=self.cleaned_data['company_name'],
                    description=self.cleaned_data['company_description']
                )
                EmployerProfile.objects.create(user=user, company=company)
                
        return user
