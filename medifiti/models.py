from django.db import models

from django.utils import timezone


# Create your models here.
class Patient(models.Model):
    first_name=models.CharField(max_length=200)
    second_name=models.CharField(max_length=200)
    age=models.IntegerField()
    email=models.EmailField()
    phone_number=models.IntegerField()
    location=models.CharField(max_length=200)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.second_name} {self.age} {self.email} {self.phone_number} {self.date_time}"


#appointment booking
class Appointment(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    service = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Appointment for {self.full_name} on {self.date}"

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


# Patient profile linked one-to-one with Django's User
class PatientProfile(models.Model):
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

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
    )

    # Core identity
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True, help_text='Your date of birth (YYYY-MM-DD)')
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        help_text='Select your gender'
    )

    # Contact information
    phone = models.CharField(
        max_length=15,
        validators=[phone_regex],
        blank=True,
        help_text='Contact phone number (e.g., +1234567890)'
    )
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='USA')

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=150, blank=True, help_text='Full name of emergency contact')
    emergency_contact_relation = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        help_text='Relationship to patient'
    )
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[phone_regex],
        blank=True,
        help_text='Emergency contact phone number'
    )

    # Medical information
    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_TYPE_CHOICES,
        blank=True,
        help_text='Your blood type'
    )
    allergies = models.TextField(
        blank=True,
        help_text='List any allergies (e.g., Penicillin, Peanuts, Shellfish)'
    )
    medications = models.TextField(
        blank=True,
        help_text='Current medications (e.g., Aspirin 500mg daily, Metformin 1000mg)'
    )
    medical_conditions = models.TextField(
        blank=True,
        help_text='Medical conditions (e.g., Diabetes, Hypertension, Asthma)'
    )

    # Insurance information
    insurance_provider = models.CharField(max_length=150, blank=True, help_text='Insurance company name')
    insurance_number = models.CharField(max_length=150, blank=True, help_text='Insurance policy number')

    # Media
    profile_photo_url = models.URLField(blank=True, help_text='URL to your profile photo')

    # Administrative
    date_registered = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_registered']
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"
# Create PatientProfile automatically when a new User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile(sender, instance, created, **kwargs):
	if created:
		PatientProfile.objects.create(user=instance)

