from django.contrib import admin
from django.contrib.auth.models import User

from django.utils.html import format_html

from .models import Patient, Appointment, Service, Doctor


# Register your models here.
admin.site.register(Patient)
admin.site.register(Appointment)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'active', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'short_description', 'description')
    list_filter = ('active', 'created_at')
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'short_description', 'description', 'image', 'image_preview', 'active')}),
    )

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height:200px;"/>', obj.image.url)
        return "(No image)"
    image_preview.short_description = "Image preview"

    @admin.register(Doctor)
    class DoctorAdmin(admin.ModelAdmin):
        list_display = ('name', 'specialty', 'user', 'created_at', 'updated_at')
        search_fields = ('name', 'specialty', 'description')
        list_filter = ('specialty', 'created_at', 'updated_at')
        readonly_fields = ('image_preview', 'created_at', 'updated_at')
        fieldsets = (
            (None, {'fields': ('user', 'name', 'specialty', 'description', 'image', 'image_preview')}),
            ('Timestamps', {'fields': ('created_at', 'updated_at')}),
        )

        def image_preview(self, obj):
            if obj and obj.image:
                return format_html('<img src="{}" style="max-height:200px;"/>', obj.image.url)
            return "(No image)"

        image_preview.short_description = "Image preview"