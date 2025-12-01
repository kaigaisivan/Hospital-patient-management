from django.urls import path
from medifiti import views

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('doctors/', views.doctors, name='doctors'),
    path('departments/', views.departments, name='departments'),

    # Appointment booking
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('appointment/', views.book_appointment, name='appointment'),
    path('admin_appointments/', views.admin_appointments, name='admin_appointments'),

    # Patient management + admin routes
    path('add/', views.create_patient, name='create_patient'),
    path('update/<int:id>/', views.update_patient, name='update_patient'),
    path('delete/<int:id>/', views.delete_patient, name='delete_patient'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Authentication + dashboards
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),

    # Dashboard feature views
    path('appointments/', views.appointments, name='appointments'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('medical-history/', views.medical_history, name='medical-history'),
    path('change-password/', views.change_password, name='change-password'),
    path('emergency-contact/', views.emergency_contact, name='emergency-contact'),
    path('medical-files/', views.medical_files, name='medical-files'),
]