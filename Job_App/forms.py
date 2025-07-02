from django import forms
from .models import Job
from django import forms
from .models import Company
from .models import JobApplication
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        # all fields you let the user touch
        fields = [
            "title",
            "description",
            "company",
            "location",
            "skills_required",
            "job_type",
            "salary_range",
            "expiration_date",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "skills_required": forms.SelectMultiple(attrs={"class": "form-select"}),
            "job_type": forms.Select(attrs={"class": "form-select"}),
            "expiration_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
###########################################################################################
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'slug', 'description', 'location', 'website', 'logo', 'virtual_tour_url', 'founded_date']
#########################################################################################################
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['job', 'cover_letter', 'resume', 'status']
        widgets = {
            'job': forms.Select(attrs={'class': 'form-select'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }