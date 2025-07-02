from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Job_App import views as my_view
urlpatterns = [
    path("admin/", admin.site.urls),
    path("",my_view.My_Home,name='My_Home'),
    path("aboutus/",my_view.My_Aboutus,name='My_Aboutus'),
    path("my-services/",my_view.My_Services,name='My_Services'),
    path("My_Virtual_Tour/",my_view.My_Virtual_Tour,name="My_Virtual_Tour"),
    path('my_contact/',my_view.contact,name='contact'),
#####################################################################################################
    path('signup/',my_view.signup, name='signup'),
    path('login/',my_view.login_view, name='login'),
####################################################################################################
    path('admin-dashboard/',my_view.Admin_Dashboard,name='Admin_Dashboard'),
    path('User_Management/',my_view.User_Management,name='User_Management'),
    path('search-user/',my_view.search_user, name='search_user'),
    path('update-user/',my_view.update_user,  name='update_user'),      # ▲ new
    path('delete-user/',my_view.delete_user, name='delete_user'),
    #######################################################################
    path('user_management/', my_view.user_management, name='user_management'),
    path('get_user_data/', my_view.get_user_data, name='get_user_data'),
    path('update_user1/', my_view.update_user1, name='update_user1'),
####################################################################################
    path('logout/',my_view.logout,name='logout'),
#########################################################################################################
    path('employer-dashboard/',my_view.Employee_Dashboard,name='Employee_Dashboard'),
##############################################################################################
    path("skills/",my_view.skill_dashboard, name="skill_dashboard"),
    path("skills/<int:pk>/edit/",my_view.update_skill, name="update_skill"),
    path("skills/<int:pk>/delete/",my_view.delete_skill, name="delete_skill"),
###############################################################################################################
    path("jobs/create/",my_view.job_create, name="job_create"),
    path("jobs/edit/<int:pk>/",my_view.job_edit, name="job_edit"),
    path("jobs/delete/<int:pk>/",my_view.job_delete, name="job_delete"),
##############################################################################################################
    path('companies/',my_view.company_list_create_view, name='company-list'),
######################################################################################################
    path('jobseeker-dashboard/',my_view.JobSeeker_Dashboard,name='JobSeeker_Dashboard'),
    path('apply/',my_view.apply_for_job, name='apply_for_job'),
    ########################################
    path('applications/',my_view.job_application_list, name='job_application_list'),
    path('edit-application/<int:pk>/',my_view.edit_application, name='edit_application'),
    path('delete-application/<int:pk>/',my_view.delete_application, name='delete_application'),
###########################################################################################################
    path('virtual-tour/create/',my_view.virtual_tour_create, name='virtual-tour-create'),
    path('virtual-tours/',my_view.virtual_tour_list, name='virtual_tour_list'),
    #######################################################################################################################
    path('applications1/',my_view.application_list_view, name='application_list'),
    path('applications/update-status/<int:app_id>/',my_view.update_application_status, name='update_application_status'),
    path('job_application_list1/',my_view.job_application_list1,name='job_application_list1'),
    path('Career_Assistance/',my_view.Career_Assistance,name='Career_Assistance'),
    # path('chatbot-response/',my_view.chatbot_response, name='chatbot_response'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)