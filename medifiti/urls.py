
from django.urls import path

from medifiti import views

urlpatterns=[
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('services/',views.services,name='services'),
    path('doctors/',views.doctors,name='doctors'),
    path('departments/',views.departments,name='departments'),
    path('register/',views.register,name='register'),
    path('login/',views.login_user,name='login'),
    path('profile/',views.profile,name='profile'),
    path('logout/',views.logout_user,name='logout'),
    # Dashboard feature views
    path('appointments/',views.appointments,name='appointments'),
    path('prescriptions/',views.prescriptions,name='prescriptions'),
    path('medical-history/',views.medical_history,name='medical-history'),
    path('change-password/',views.change_password,name='change-password'),
    path('emergency-contact/',views.emergency_contact,name='emergency-contact'),
    path('medical-files/',views.medical_files,name='medical-files'),

]