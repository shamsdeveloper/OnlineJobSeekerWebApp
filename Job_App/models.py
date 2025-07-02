from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
################################################################################################################
# Create your models here.
class Contact(models.Model):
    name=models.CharField(max_length=250)
    email=models.EmailField()
    Phone_number=models.CharField(max_length=250)
    message=models.TextField()
    added_on=models.DateTimeField(auto_now_add=True)
    is_approved=models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural="Contact Table"
#############################################################################################################################
class User(AbstractUser):
    ROLE_CHOICES = [
        ('JOB_SEEKER', 'Job Seeker'),
        ('EMPLOYER', 'Employer'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
#####################################################################################################################
class Company(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    virtual_tour_url = models.URLField(blank=True)
    founded_date = models.DateField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
###########################################################################################################################
class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    skills = models.ManyToManyField('Skill')
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    preferred_locations = models.CharField(max_length=255, blank=True)
    preferred_job_types = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"
#############################################################################################
class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employers')
    position = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.user.username} ({self.company.name})"
##################################################################################################
class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
######################################################################################################
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERNSHIP', 'Internship'),
        ('REMOTE', 'Remote'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    location = models.CharField(max_length=100)
    skills_required = models.ManyToManyField(Skill)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    salary_range = models.CharField(max_length=100, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    posted_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.title} at {self.company.name}"
###############################################################################################################################
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    application_date = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    resume = models.FileField(upload_to='application_resumes/')
    def __str__(self):
        return f"{self.applicant.username}'s application for {self.job.title}"
################################################################################################################################
class Interview(models.Model):
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='interview')
    scheduled_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    online_meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=30)
    def __str__(self):
        return f"Interview for {self.application.job.title} with {self.application.applicant.username}"
##############################################################################################################
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True)
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
##################################################################################################################
class ChatbotInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chatbot_interactions')
    session_id = models.CharField(max_length=100)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_user_message = models.BooleanField()
    def __str__(self):
        return f"Chatbot interaction with {self.user.username if self.user else 'Anonymous'} at {self.timestamp}"
###########################################################################################################################
class SystemLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('JOB_POST', 'Job Posted'),
        ('JOB_APPLY', 'Job Application'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('SYSTEM_EVENT', 'System Event'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.get_action_display()} by {self.user.username if self.user else 'System'} at {self.timestamp}"