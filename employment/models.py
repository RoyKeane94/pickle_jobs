from django.db import models
from accounts.models import EmployerProfile, EmployeeProfile


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
