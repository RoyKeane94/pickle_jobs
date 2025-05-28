from django.contrib import admin
from .models import JobPosting, JobSkill, JobStage, JobApplication

# Register your models here.

admin.site.register(JobPosting)
admin.site.register(JobSkill)
admin.site.register(JobStage)
admin.site.register(JobApplication)
