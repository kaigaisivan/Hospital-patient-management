from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Contact, Doctor, Appointment, CustomUser

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'notification_email', 'notification_method')}),
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email')
    readonly_fields = ('created_at',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty')
    search_fields = ('name', 'specialty')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient_name', 'patient_email', 'doctor__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'patient_email', 'patient_phone')
        }),
        ('Appointment Details', {
            'fields': ('doctor', 'appointment_date', 'appointment_time', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )


from .models import Service, LabSample


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)


@admin.register(LabSample)
class LabSampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'status', 'created_at')
    search_fields = ('sample_id',)
