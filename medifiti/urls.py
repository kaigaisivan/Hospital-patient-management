from django.urls import path, include
from django.views.generic.base import RedirectView
from medifiti import views

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # moved app admin utilities under `manage/` to avoid collision with Django admin
    path('manage/export/patients/csv/', views.export_patients_csv, name='export_patients_csv'),
    path('manage/contacts/<int:id>/', views.contact_detail, name='contact_detail'),
    path('manage/contacts/<int:id>/delete/', views.delete_contact, name='delete_contact'),
    path('manage/facility/', views.edit_facility, name='edit_facility'),

    # compatibility redirects from old `admin/` paths (non‑permanent)
    path('admin/export/patients/csv/', RedirectView.as_view(pattern_name='export_patients_csv', permanent=False)),
    path('admin/contacts/<int:id>/', RedirectView.as_view(pattern_name='contact_detail', permanent=False)),
    path('admin/contacts/<int:id>/delete/', RedirectView.as_view(pattern_name='delete_contact', permanent=False)),
    path('admin/facility/', RedirectView.as_view(pattern_name='edit_facility', permanent=False)),
    path('facility/', views.facility, name='facility'),
    path('facilities/', views.facilities_list, name='facilities'),
    path('facility/<int:pk>/', views.facility_detail, name='facility_detail'),
    # keep /facility/ for backward compatibility pointing to the list
    path('facility/', views.facilities_list, name='facility'),

    # Explicit redirect to avoid reverse('logout') resolving back to accounts/logout and looping
    path('accounts/logout/', RedirectView.as_view(url='/logout/', permanent=False)),

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
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    # Authentication + dashboards
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),

    # Dashboard feature views
    path('accounts/', include('django.contrib.auth.urls')),
    path('appointments/', views.appointments, name='appointments'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('medical-history/', views.medical_history, name='medical-history'),
    path('change-password/', views.change_password, name='change-password'),
    path('emergency-contact/', views.emergency_contact, name='emergency-contact'),
    path('medical-files/', views.medical_files, name='medical-files'),
]