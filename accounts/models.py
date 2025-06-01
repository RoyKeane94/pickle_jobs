from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('employee', 'Employee'),
        ('employer', 'Employer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class EmployerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employers')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.company.name}"

# Auto-capitalize last names
@receiver(pre_save, sender=CustomUser)
def capitalize_last_name(sender, instance, **kwargs):
    if instance.last_name:
        instance.last_name = instance.last_name.capitalize()

    if instance.first_name:
        instance.first_name = instance.first_name.capitalize()
