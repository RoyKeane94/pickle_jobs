from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company, EmployeeProfile, EmployerProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_staff', 'is_active')

class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company__name')
    list_filter = ('company',)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(EmployeeProfile, EmployeeProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)
