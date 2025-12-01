from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.shortcuts import render

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
)


class CustomUser(AbstractUser):
    """Custom user model with role-based access control."""
    ROLE_ADMIN = 'admin'
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    phone = models.CharField(max_length=15, blank=True, validators=[phone_regex])
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
        role_label = dict(self.ROLE_CHOICES).get(self.role, self.role)
        return f"{self.username} ({role_label})"

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


# python
# File: `medifiti/models.py` — replace the Doctor class with this version
class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='doctor_profile'
    )
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='doctors/', null=True, blank=True)

    # new: services a doctor offers
    services = models.ManyToManyField('Service', blank=True, related_name='doctors')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.name}"


class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('service_detail', args=[self.slug])
    def services(request):
        """
        Return active services ordered by most recently updated first so admin edits
        appear immediately on the public listing.
        """
        services_qs = Service.objects.filter(active=True).order_by('-updated_at')
        return render(request, 'services.html', {'services': services_qs})

    # File: `templates/services.html` (Django template / HTML)


class LabSample(models.Model):
    """Simple model for tracking lab samples (placeholder implementation)."""
    sample_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100, default='Received')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sample_id} - {self.status}"


class Patient(models.Model):
    """Lightweight patient record for non-authenticated or legacy data."""
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, validators=[phone_regex], blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    """Unified appointment model supporting both authenticated patients and guest bookings."""
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    # If booking by a registered user/profile, link here; otherwise use the guest fields
    patient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='appointments'
    )
    patient_profile = models.ForeignKey(
        'PatientProfile', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='appointments'
    )
    # Guest/paper record fallback fields (kept for convenience)
    patient_name = models.CharField(max_length=100, blank=True)
    patient_email = models.EmailField(blank=True)
    patient_phone = models.CharField(max_length=15, validators=[phone_regex], blank=True)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']

    def __str__(self):
        name = self.patient_name
        if not name and self.patient_profile:
            # prefer full name from linked profile's user
            try:
                name = self.patient_profile.user.get_full_name() or self.patient_profile.user.username
            except Exception:
                name = ''
        return f"{name or 'Unknown Patient'} - Dr. {self.doctor.name} - {self.appointment_date} {self.appointment_time}"


class PatientProfile(models.Model):
    """Patient profile linked one-to-one with the user model."""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    )

    BLOOD_TYPE_CHOICES = (
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )

    RELATIONSHIP_CHOICES = (
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True, help_text='Your date of birth (YYYY-MM-DD)')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=15, validators=[phone_regex], blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='USA')

    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_relation = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, validators=[phone_regex], blank=True)

    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)

    insurance_provider = models.CharField(max_length=150, blank=True)
    insurance_number = models.CharField(max_length=150, blank=True)

    profile_photo_url = models.URLField(blank=True)

    date_registered = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_registered']
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        try:
            name = self.user.get_full_name() or self.user.username
        except Exception:
            name = str(self.user)
        return f"{name}'s profile"


# Create PatientProfile automatically when a new User with role 'patient' is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and getattr(instance, 'role', None) == CustomUser.ROLE_PATIENT:
        PatientProfile.objects.create(user=instance)