from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'education_summary', 'experience_summary')
    search_fields = ('user__username', 'user__email', 'skills__name')
    filter_horizontal = ('skills',)
    
    def education_summary(self, obj):
        return obj.education[:50] + '...' if len(obj.education) > 50 else obj.education
    education_summary.short_description = 'Education'
    
    def experience_summary(self, obj):
        return obj.experience[:50] + '...' if len(obj.experience) > 50 else obj.experience
    experience_summary.short_description = 'Experience'

class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position')
    search_fields = ('user__username', 'user__email', 'company__name')

    
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    fields = ('name', 'slug', 'description', 'location', 'website', 'logo', 'virtual_tour_url', 'founded_date')

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'posted_date', 'is_active')
    list_filter = ('job_type', 'is_active', 'posted_date', 'company')
    search_fields = ('title', 'description', 'company__name', 'skills_required__name')
    filter_horizontal = ('skills_required',)
    date_hierarchy = 'posted_date'

class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'application_date')
    list_filter = ('status', 'application_date', 'job__company')
    search_fields = ('job__title', 'applicant__username', 'cover_letter')
    readonly_fields = ('application_date',)

class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_date', 'location')
    list_filter = ('scheduled_date',)
    search_fields = ('application__job__title', 'application__applicant__username')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

class ChatbotInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'message_summary', 'is_user_message')
    list_filter = ('is_user_message', 'timestamp')
    search_fields = ('user__username', 'message', 'response')
    
    def message_summary(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_summary.short_description = 'Message'

class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'details', 'ip_address')
    readonly_fields = ('timestamp',)

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(JobSeekerProfile, JobSeekerProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)
admin.site.register(Skill)
admin.site.register(Job, JobAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ChatbotInteraction, ChatbotInteractionAdmin)
admin.site.register(SystemLog, SystemLogAdmin)
admin.site.register(Contact)
####################################################################################
admin.site.site_header="OnlineJobSeekerWeb_App"
admin.site.site_title="Admin Panel"