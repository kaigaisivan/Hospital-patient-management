from django.contrib import admin
from django.contrib.auth.models import User
from .models import(Patient)
from .models import(Appointment)
# Register your models here.
admin.site.register(Patient)
admin.site.register(Appointment)
