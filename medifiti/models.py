from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    """Custom user model with role-based access control."""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True)
    notification_email = models.EmailField(blank=True, help_text='Email address for admin alerts')
    notification_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email Only'),
            ('in_app', 'In-App Only'),
            ('both', 'Email & In-App'),
        ],
        default='email',
        help_text='How to receive notifications'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"
    
    class Meta:
        ordering = ['-created_at']


class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient_name = models.CharField(max_length=100)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=15)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient_name} - Dr. {self.doctor.name} - {self.appointment_date}"
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']


class Service(models.Model):
    """Admin-manageable services offered by the hospital."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LabSample(models.Model):
    """Simple model for tracking lab samples (placeholder implementation)."""
    sample_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100, default='Received')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sample_id} - {self.status}"
