from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import EmployeeExperience, EmployeeEducation, EmployeeInterest, PickleProfile


@receiver(post_save, sender=EmployeeExperience)
def update_experience_completion(sender, instance, created, **kwargs):
    """
    Signal to update PickleProfile when first EmployeeExperience is created.
    Sets cv_blank = False and experience_completed = True.
    """
    if created:
        # Get or create PickleProfile for this employee
        pickle_profile, profile_created = PickleProfile.objects.get_or_create(
            employee=instance.employee
        )
        
        # Check if this is the first experience entry
        experience_count = EmployeeExperience.objects.filter(
            employee=instance.employee
        ).count()
        
        if experience_count == 1:  # First experience entry
            pickle_profile.cv_blank = False
            pickle_profile.experience_completed = True
            pickle_profile.save(update_fields=['cv_blank', 'experience_completed'])


@receiver(post_save, sender=EmployeeEducation)
def update_education_completion(sender, instance, created, **kwargs):
    """
    Signal to update PickleProfile when first EmployeeEducation is created.
    Sets education_completed = True.
    """
    if created:
        # Get or create PickleProfile for this employee
        pickle_profile, profile_created = PickleProfile.objects.get_or_create(
            employee=instance.employee
        )
        
        # Check if this is the first education entry
        education_count = EmployeeEducation.objects.filter(
            employee=instance.employee
        ).count()
        
        if education_count == 1:  # First education entry
            pickle_profile.education_completed = True
            pickle_profile.save(update_fields=['education_completed'])


@receiver(m2m_changed, sender=EmployeeExperience.skills.through)
def update_skills_completion(sender, instance, action, pk_set, **kwargs):
    """
    Signal to update PickleProfile when skills are first added to EmployeeExperience.
    Sets skills_completed = True.
    """
    if action == "post_add" and pk_set:
        # Get or create PickleProfile for this employee
        pickle_profile, profile_created = PickleProfile.objects.get_or_create(
            employee=instance.employee
        )
        
        # Check if skills_completed is not already True
        if not pickle_profile.skills_completed:
            # Check if this employee now has any skills in any experience
            has_skills = EmployeeExperience.objects.filter(
                employee=instance.employee,
                skills__isnull=False
            ).exists()
            
            if has_skills:
                pickle_profile.skills_completed = True
                pickle_profile.save(update_fields=['skills_completed'])


@receiver(post_save, sender=EmployeeInterest)
def update_interests_completion(sender, instance, created, **kwargs):
    """
    Signal to update PickleProfile when first EmployeeInterest is created.
    Sets interests_completed = True.
    """
    if created:
        # Get or create PickleProfile for this employee
        pickle_profile, profile_created = PickleProfile.objects.get_or_create(
            employee=instance.employee
        )
        
        # Check if this is the first interest entry
        interest_count = EmployeeInterest.objects.filter(
            employee=instance.employee
        ).count()
        
        if interest_count == 1:  # First interest entry
            pickle_profile.interests_completed = True
            pickle_profile.save(update_fields=['interests_completed'])


@receiver(post_save, sender=PickleProfile)
def update_cv_completion(sender, instance, **kwargs):
    """
    Signal to update cv_completed when all sections are complete.
    Sets cv_completed = True when all other completion flags are True.
    """
    if (instance.experience_completed and 
        instance.education_completed and 
        instance.skills_completed and 
        instance.interests_completed and 
        not instance.cv_completed):
        
        instance.cv_completed = True
        instance.save(update_fields=['cv_completed'])
