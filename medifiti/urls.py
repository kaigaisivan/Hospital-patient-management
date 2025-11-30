
from django.urls import path

from medifiti import views

urlpatterns=[
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('services/',views.services,name='services'),
    path('doctors/',views.doctors,name='doctors'),
    path('departments/',views.departments,name='departments'),
    path('add/',views.create_patient,name='create_patient'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('update/<int:id>/',views.update_patient,name='update_patient'),
    path('delete/<int:id>/',views.delete_patient,name='delete_patient'),
    path('appointment/', views.book_appointment, name='appointment'),
   path('admin_appointments/', views.admin_appointments, name='admin_appointments'),

]