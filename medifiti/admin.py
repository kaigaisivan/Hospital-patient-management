from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    CustomUser, Patient, PatientProfile, Appointment,
    Service, Doctor, LabSample, Contact, Facility
)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Role & preferences'), {'fields': ('role', 'notification_email', 'notification_method')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'active', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'short_description', 'description')
    list_filter = ('active', 'created_at', 'updated_at')
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'short_description', 'description', 'image', 'image_preview', 'active')}),
    )

    def image_preview(self, obj):
        if obj and getattr(obj, 'image', None):
            return format_html('<img src="{}" style="max-height:200px;"/>', obj.image.url)
        return "(No image)"
    image_preview.short_description = "Image preview"


class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    fields = ('get_patient_display', 'appointment_date', 'appointment_time', 'reason', 'status')
    readonly_fields = ('get_patient_display',)
    show_change_link = True

    def get_patient_display(self, obj):
        if obj.patient_name:
            return obj.patient_name
        if obj.patient_profile and getattr(obj.patient_profile, 'user', None):
            try:
                return obj.patient_profile.user.get_full_name() or obj.patient_profile.user.username
            except Exception:
                return str(obj.patient_profile)
        if obj.patient_user:
            try:
                return obj.patient_user.get_full_name() or obj.patient_user.username
            except Exception:
                return str(obj.patient_user)
        return '(guest)'
    get_patient_display.short_description = 'Patient'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'user', 'services_list', 'created_at', 'updated_at')
    search_fields = ('name', 'specialty', 'description', 'user__username', 'user__email', 'services__title')
    list_filter = ('specialty', 'created_at', 'updated_at')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'name', 'specialty', 'description', 'image', 'image_preview', 'services')}),
    )
    filter_horizontal = ('services',)
    inlines = [AppointmentInline]

    def image_preview(self, obj):
        if obj and getattr(obj, 'image', None):
            return format_html('<img src="{}" style="max-height:200px;"/>', obj.image.url)
        return "(No image)"
    image_preview.short_description = "Image preview"

    def services_list(self, obj):
        return ", ".join([s.title for s in obj.services.all()]) if obj.pk else ""
    services_list.short_description = "Services"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'get_patient_display', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient_name', 'patient_email', 'patient_phone', 'doctor__name', 'patient_profile__user__username')
    date_hierarchy = 'appointment_date'
    ordering = ('-appointment_date', '-appointment_time')
    actions = ['mark_as_confirmed', 'mark_as_pending', 'mark_as_cancelled']

    def get_patient_display(self, obj):
        if obj.patient_name:
            return obj.patient_name
        if obj.patient_profile and getattr(obj.patient_profile, 'user', None):
            try:
                return obj.patient_profile.user.get_full_name() or obj.patient_profile.user.username
            except Exception:
                return str(obj.patient_profile)
        if obj.patient_user:
            try:
                return obj.patient_user.get_full_name() or obj.patient_user.username
            except Exception:
                return str(obj.patient_user)
        return '(guest)'
    get_patient_display.short_description = 'Patient'

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status=Appointment.STATUS_CONFIRMED)
        self.message_user(request, f"{updated} appointment(s) marked as confirmed.")
    mark_as_confirmed.short_description = "Mark selected appointment(s) as confirmed"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status=Appointment.STATUS_PENDING)
        self.message_user(request, f"{updated} appointment(s) marked as pending.")
    mark_as_pending.short_description = "Mark selected appointment(s) as pending"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status=Appointment.STATUS_CANCELLED)
        self.message_user(request, f"{updated} appointment(s) marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected appointment(s) as cancelled"


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('created_at',)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'blood_type', 'date_registered', 'last_updated')
    search_fields = ('user__username', 'user__email', 'phone', 'insurance_provider', 'insurance_number')
    readonly_fields = ('date_registered', 'last_updated')
    list_filter = ('blood_type', 'date_registered')


@admin.register(LabSample)
class LabSampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'status', 'created_at')
    search_fields = ('sample_id', 'notes')
    list_filter = ('status', 'created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'created_at')
    search_fields = ('full_name', 'email', 'message')
    date_hierarchy = 'created_at'
@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'updated_at')
    readonly_fields = ('logo_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'address', 'phone', 'email', 'emergency_phone', 'description', 'logo', 'logo_preview')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def logo_preview(self, obj):
        if obj and getattr(obj, 'logo', None):
            return format_html('<img src="{}" style="max-height:150px;"/>', obj.logo.url)
        return "(No logo)"
    logo_preview.short_description = "Logo preview"