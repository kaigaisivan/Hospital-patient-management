from django.contrib import admin
from django.contrib.auth.models import User
from .models import(Patient)
from .models import(Appointment)
from .models import(PatientProfile)
# Register your models here.
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(PatientProfile)
