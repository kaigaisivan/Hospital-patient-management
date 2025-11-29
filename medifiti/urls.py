
from django.urls import path

from medifiti import views

urlpatterns=[
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('services/',views.services,name='services'),
    path('doctors/',views.doctors,name='doctors'),
    path('departments/',views.departments,name='departments'),
]