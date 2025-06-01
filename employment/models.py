from django.db import models
from accounts.models import EmployerProfile, EmployeeProfile, Company


# Job Skills

class JobSkill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# Job Stages

class JobStage(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# Job Postings from the Employer's Perspective

class JobPosting(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_hours = models.IntegerField(null=False, blank=False, default=0)
    skills = models.ManyToManyField(JobSkill)
    stage = models.ManyToManyField(JobStage)
    accepting_application_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    successful_completion = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True)

    def __str__(self):
        return self.title + " - " + self.employer.company.name

# Job Applications from the Employee's Perspective

class JobApplication(models.Model):
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    stage = models.ForeignKey(JobStage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offer_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job_posting.title} - {self.stage.name}"
    
class Location(models.Model):
    name = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=12, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
    
class EmployeeExperience(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    employer = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    experience_level = models.CharField(max_length=255)
    experience_description = models.TextField()
    experience_start_date = models.DateField()
    experience_end_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(JobSkill)

    def __str__(self):
        return self.employee.user.first_name + " - " + self.job_title
    
class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class EmployeeEducation(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('GCSE', 'GCSE'),
        ('A-Level', 'A-Level'),
        ('BTEC', 'BTEC'),
        ('Degree', 'Degree'),
        ('Masters', 'Masters'),
        ('PhD', 'PhD'),
    ]
    
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    school_name = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    level = models.CharField(max_length=255, choices=EDUCATION_LEVEL_CHOICES, default='GCSE')
    field_of_study = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    
class PickleProfile(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.employee.user.first_name + " - " + self.employee.user.last_name
