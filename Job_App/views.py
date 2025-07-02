from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from django.contrib.auth import login
from django.http import HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import FileResponse
from django.conf import settings
from django.contrib.auth.hashers import make_password
import os
from django.http import JsonResponse
from .models import User,Skill
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate,logout as auth_logout 
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Job
from .forms import JobForm
from .models import Company
from .forms import CompanyForm
from .forms import JobApplicationForm
from .models import JobApplication
from .models import Company
import pandas as pd
import json
from PIL import Image
############################################################################################################
def My_Home(request):
    return render(request, 'Home/index.html')
############################################################################################################
def My_Aboutus(request):
    return render(request,'Home/AboutUs.html')
############################################################################################################
def My_Services(request):
    return render(request,'Home/Services.html')
###########################################################################################################
def My_Virtual_Tour(request):
    return render(request,'Home/Virtual_tour.html')
###########################################################################################################
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Save to database
        Contact.objects.create(
            name=name,
            email=email,
            Phone_number=phone,
            message=message
        )

        request.session['contact_success'] = True  # Set flag
        return redirect('contact')

    show_success = request.session.pop('contact_success', False)
    return render(request, 'Home/contact.html', {'show_success': show_success})

##################################################################################################################
User = get_user_model()
###########################################################################################################################
def signup(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            role = request.POST.get('role')
            phone_number = request.POST.get('phone_number')
            bio = request.POST.get('bio')
            profile_picture = request.FILES.get('profile_picture')
            if password1 != password2:
                return JsonResponse({'success': False, 'message': 'Passwords do not match!'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists!'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists!'}, status=400)
            try:
                # Use create_user to properly hash password and handle user creation
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                # Set additional fields
                user.role = role
                user.phone_number = phone_number
                user.bio = bio
                if profile_picture:
                    user.profile_picture = profile_picture
                user.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Account created successfully!',
                    'redirect_url': '/login/'  # Replace with your actual login URL
                })
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return render(request, 'Home/User/User_SignUp.html')
##############################################################################################################################
def login_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Redirect based on user role
            if user.role == 'ADMIN':
                redirect_url = '/admin-dashboard/'  # Replace with your admin dashboard URL
            elif user.role == 'EMPLOYER':
                redirect_url = '/employer-dashboard/'  # Replace with your employer dashboard URL
            elif user.role == 'JOB_SEEKER':
                redirect_url = '/jobseeker-dashboard/'  # Replace with your jobseeker dashboard URL
            else:
                redirect_url = '/'  # Default fallback
            return JsonResponse({
                'success': True,
                'message': 'Login successful!',
                'redirect_url': redirect_url
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials.'}, status=401)
    return render(request, 'Home/User/User_SignIn.html')
#########################################################################################################################################
def Admin_Dashboard(request):
    users=User.objects.all()
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
    }
    return render(request, 'User_Admin/Admin_Dashboard.html', context)
###########################################################################################################
def User_Management(request):
    users=User.objects.all()
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
    }
    return render(request,'User_Admin/UserManagement.html',context)
#######################################################################################################################
@require_POST
def search_user(request):
    """
    Ajax: look up a user by username (case-insensitive) and
    return profile data for auto-fill, including picture URL.
    """
    username = (request.POST.get('username') or "").strip()

    if not username:
        return JsonResponse(
            {"status": "error", "message": "Please choose a user first."},
            status=400
        )

    try:
        user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "User not found."},
            status=404
        )

    data = {
        "username"    : user.username,
        "email"       : user.email or "",
        "phone_number": user.phone_number or "",
        "role"        : user.role,                 # ADMIN / EMPLOYER / JOB_SEEKER
        "bio"         : user.bio or "",
        "profile_pic" : user.profile_picture.url if user.profile_picture else "",
    }
    return JsonResponse({"status": "success", "data": data})
###########################################################################################################
# ▲ NEW: Ajax endpoint to save changes
@require_POST
def update_user(request):
    username = (request.POST.get('username') or "").strip()
    if not username:
        return JsonResponse({"status": "error", "message": "Username missing."}, status=400)

    try:
        user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found."}, status=404)

    # --- update scalar fields ---
    user.email        = request.POST.get('email', '').strip()
    user.phone_number = request.POST.get('phone_number', '').strip()
    role              = request.POST.get('role', '')
    if role in dict(User.ROLE_CHOICES):     # validate
        user.role = role
    user.bio = request.POST.get('bio', '').strip()

    # --- update picture if a new file was uploaded ---
    if request.FILES.get('profile_picture'):
        user.profile_picture = request.FILES['profile_picture']

    user.save()

    return JsonResponse({
        "status"      : "success",
        "message"     : "User updated successfully.",
        "profile_pic" : user.profile_picture.url if user.profile_picture else "",
    })
##########################################################################################################################
@require_POST
def delete_user(request):
    """AJAX: delete a user by username."""
    username = request.POST.get('username')
    if not username:
        return JsonResponse({'status': 'error', 'message': 'Username required'}, status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    user.delete()
    return JsonResponse({'status': 'success',
                         'message': f'User {username} has been permanently removed.'})
############################################################################################################################
def user_management(request):
    users=User.objects.all()
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
    }
    return render(request, 'User_Admin/System_Logs.html',context)
##############################################################
def get_user_data(request):
    username = request.GET.get('username')
    try:
        user = User.objects.get(username=username)
        data = {
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'phone_number': user.phone_number,
                'role': user.role,
                'profile_picture': str(user.profile_picture) if user.profile_picture else '',
            }
        }
    except User.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)
###########################################################################################
def update_user1(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.role = request.POST.get('role')
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
##################################################################################################################
def logout(request):
    """
    Handles user logout and redirects to the login page with a success message.
    """
    if request.user.is_authenticated:
        auth_logout(request)  # Call the renamed Django logout method
        messages.success(request, "You have successfully logged out.")
    else:
        messages.warning(request, "You were not logged in.")
    return redirect('login')  # Redirect to the login page
##############################################################################################################################################################
##############################################################################################################################################################
def Employee_Dashboard(request):
    users=User.objects.filter(role='EMPLOYER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    applications = JobApplication.objects.all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
        'applications':applications
    }
    return render(request, 'Employee/Employee_Dashboard.html',context)
######################################################################################
# ────────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD  – add + list + search (all in one)
# ────────────────────────────────────────────────────────────────────────────────
def skill_dashboard(request):
    """
    One-page dashboard that
    • shows all skills
    • handles creation of a new skill
    • handles searching by “q” GET parameter
    """
    # ── 1) CREATE ──────────────────────────────────────────────────────────────
    if request.method == "POST" and "name" in request.POST:
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Skill name cannot be blank.")
            return redirect("skill_dashboard")

        try:
            Skill.objects.create(name=name)
            messages.success(request, "Skill added successfully!")
        except IntegrityError:
            messages.error(request, "That skill already exists.")

        return redirect("skill_dashboard")     # PRG pattern

    # ── 2) READ + SEARCH ───────────────────────────────────────────────────────
    query   = request.GET.get("q", "").strip()
    skills  = Skill.objects.all()
    if query:
        skills = skills.filter(name__icontains=query)
    skills = skills.order_by("name")

    # counts for the cards (you already used these)
    admin_qs     = User.objects.filter(role="ADMIN")
    employee_qs  = User.objects.filter(role="EMPLOYER")
    jobseeker_qs = User.objects.filter(role="JOB_SEEKER")
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context = {
        "skills": skills,
        "search_term": query,
        "total_admin":     admin_qs.count(),
        "total_employee":  employee_qs.count(),
        "total_jobseeker": jobseeker_qs.count(),
        'total_applications':applications.count()
    }
    return render(request, "Employee/Add_Skills.html", context)


# ────────────────────────────────────────────────────────────────────────────────
# UPDATE
# ────────────────────────────────────────────────────────────────────────────────
def update_skill(request, pk):
    """
    Edit an existing skill (tiny form with one <textarea>).
    """
    skill = get_object_or_404(Skill, pk=pk)

    if request.method == "POST":
        new_name = request.POST.get("name", "").strip()
        if not new_name:
            messages.error(request, "Skill name cannot be blank.")
            return redirect("skill_dashboard")

        if new_name != skill.name:                # only write if changed
            skill.name = new_name
            try:
                skill.save()
                messages.success(request, "Skill updated successfully!")
            except IntegrityError:
                messages.error(request, "That skill already exists.")
        return redirect("skill_dashboard")

    return render(request, "Employee/Edit_Skill.html", {"skill": skill})


# ────────────────────────────────────────────────────────────────────────────────
# DELETE
# ────────────────────────────────────────────────────────────────────────────────
def delete_skill(request, pk):
    """
    Permanently delete a skill.
    """
    skill = get_object_or_404(Skill, pk=pk)

    # safety: only accept POST for delete
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill deleted successfully!")
        return redirect("skill_dashboard")

    # simple confirmation page
    return render(request, "Employee/Delete_Skill_Confirm.html", {"skill": skill})
##########################################################################################################################################
@login_required
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            form.save_m2m()
            messages.success(request, "Job posted successfully!")
            return redirect("job_create")
        messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm()

    jobs = Job.objects.filter(posted_by=request.user).order_by("-id")
    users=User.objects.filter(role='EMPLOYER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        "form": form,
        "jobs": jobs,
        'total_applications':applications.count(),
    }
    return render(request, "Employee/job_form.html",context)


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("job_create")
    else:
        form = JobForm(instance=job)

    jobs = Job.objects.filter(posted_by=request.user).order_by("-id")
    users=User.objects.all()
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
        "form": form, 
        "jobs": jobs
    }
    return render(request, "Employee/job_form.html",context)


@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully!")
    return redirect("job_create")
###########################################################################################################################
def company_list_create_view(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('company-list')  # Make sure this name matches your URL pattern
    else:
        form = CompanyForm()
    companies = Company.objects.all().order_by('-id')
    users=User.objects.filter(role='EMPLOYER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        "form": form,
        'companies': companies,
        'total_applications':applications.count(),
    }
    return render(request, 'Employee/Add_Company.html',context)
#################################################################################################################################################################
#################################################################################################################################################################
def JobSeeker_Dashboard(request):
    users=User.objects.filter(role='JOB_SEEKER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    my_job = Job.objects.all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
        'my_job':my_job
    }
    return render(request,'JobSeeker/JobSeeker_Dashboard.html',context)
################################################################################################################
@login_required
def apply_for_job(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job_app = form.save(commit=False)
            job_app.applicant = request.user
            job_app.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('apply_for_job')
    else:
        form = JobApplicationForm()
    users=User.objects.filter(role='JOB_SEEKER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'form': form,
        'total_applications':applications.count()
    }
    return render(request, 'JobSeeker/apply_form.html',context)
###################################$$$$$$$$###############################################################################################
def job_application_list(request):
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    users=User.objects.filter(role='JOB_SEEKER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'applications': applications,
        'total_applications':applications.count(),
    }
    return render(request, 'JobSeeker/View_All_Application.html',context)
##################################################################################
def edit_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully!')
            return redirect('job_application_list')
    else:
        form = JobApplicationForm(instance=application)
    users=User.objects.filter(role='JOB_SEEKER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'form': form,
        'total_applications':applications.count(),
    }
    return render(request, 'edit_application.html',context)

def delete_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    application.delete()
    messages.success(request, 'Application deleted successfully!')
    return redirect('job_application_list')
########################################################################################################################################################
def virtual_tour_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        location = request.POST.get('location')
        website = request.POST.get('website')
        virtual_tour_url = request.POST.get('virtual_tour_url')
        founded_date = request.POST.get('founded_date')
        logo = request.FILES.get('logo')
        company = Company(
            name=name,
            description=description,
            location=location,
            website=website,
            virtual_tour_url=virtual_tour_url,
            founded_date=founded_date,
            logo=logo
        )
        company.save()
        messages.success(request, 'Virtual Tour Company added successfully!')
        return redirect('virtual-tour-create')  # use your URL name here
    users=User.objects.all()
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
    }
    return render(request, 'Employee/Add_Virtual_Tour.html',context)
###############################################################################################
def virtual_tour_list(request):
    companies = Company.objects.all()
    users=User.objects.all()
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'total_applications':applications.count(),
        'companies': companies
    }
    return render(request, 'JobSeeker/View_All_Tours.html',context)
#########################################################################################################################################################################
def application_list_view(request):
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    users=User.objects.filter(role='JOB_SEEKER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'applications': applications,
        'total_applications':applications.count(),
    }
    return render(request, 'Employee/Update_Application.html',context)
####################################################################
@csrf_exempt
def update_application_status(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(JobApplication, id=app_id)
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            app.status = new_status
            app.save()
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        return JsonResponse({'success': False, 'message': 'Invalid status'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})
###########################################################################################################
def job_application_list1(request):
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    users=User.objects.filter(role='JOB_SEEKER')
    admin_qs     = User.objects.filter(role='ADMIN')
    employee_qs  = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    context={
        'total_admin':     admin_qs.count(),     # ints only
        'total_employee':  employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users':users,
        'applications': applications,
        'total_applications':applications.count()
    }
    return render(request, 'User_Admin/View_All_Application.html',context)
######################################################################################################################################################################
##############################################################################################################################################################
def Career_Assistance(request):
    users = User.objects.filter(role='JOB_SEEKER')
    admin_qs = User.objects.filter(role='ADMIN')
    employee_qs = User.objects.filter(role='EMPLOYER')
    jobseeker_qs = User.objects.filter(role='JOB_SEEKER')
    applications = JobApplication.objects.select_related('job', 'applicant').all()
    
    context = {
        'total_admin': admin_qs.count(),
        'total_employee': employee_qs.count(),
        'total_jobseeker': jobseeker_qs.count(),
        'users': users,
        'total_applications': applications.count()
    }
    
    return render(request, 'JobSeeker/Create_Virtual_Assistance.html', context)

# def chatbot_response(request):
#     if request.method == 'POST':
#         message = request.POST.get('message', '').strip()
#         session_data = json.loads(request.POST.get('session_data', '{}'))
        
#         # Get real job listings from database
#         job_listings =Job.objects.all().values()
#         job_listings_df = pd.DataFrame.from_records(job_listings)
        
#         # Initialize session data if empty
#         if not session_data:
#             session_data = {
#                 'user_type': None,
#                 'job_seeker_profile': {},
#                 'employer_profile': {},
#                 'job_listings': job_listings_df.to_dict(orient='records'),
#                 'applications': [],
#                 'conversation_context': {}
#             }
#         # Ensure job_listings is always in dict format for the chatbot
#         elif isinstance(session_data.get('job_listings'), list):
#             session_data['job_listings'] = pd.DataFrame(session_data['job_listings']).to_dict(orient='records')
        
#         # Get response from chatbot
#         response, updated_session = chatbot.respond(message, session_data)
        
#         # Convert pandas DataFrames to dict for JSON serialization
#         for key in ['job_listings', 'applications']:
#             if isinstance(updated_session.get(key), pd.DataFrame):
#                 updated_session[key] = updated_session[key].to_dict(orient='records')
        
#         return JsonResponse({
#             'response': response,
#             'session_data': updated_session
#         })
    
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

