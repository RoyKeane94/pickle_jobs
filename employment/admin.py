from django.contrib import admin
from .models import JobPosting, JobSkill, JobStage, JobApplication, Location, School, EmployeeInterest, PickleProfile

# Register your models here.

admin.site.register(JobPosting)
admin.site.register(JobSkill)
admin.site.register(JobStage)
admin.site.register(JobApplication)
admin.site.register(Location)
admin.site.register(School)
admin.site.register(EmployeeInterest)
admin.site.register(PickleProfile)
