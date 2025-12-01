from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Doctor, Service
from .models import Appointment, Patient, PatientProfile

# Use the project's user model
User = get_user_model()


# Patient form (lightweight Patient model)
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'age', 'email', 'phone_number', 'location']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name', 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1234567890', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


# AppointmentForm: expose legacy alias fields for templates (full_name, email, phone, service, date, time, message)
# and map them to the current Appointment model fields in save().
class AppointmentForm(forms.ModelForm):
    # legacy/alias fields (keep for old templates)
    full_name = forms.CharField(max_length=100, required=False, label="Full name",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, label="Email",
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, label="Phone",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    service = forms.CharField(max_length=100, required=False, label="Service",
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    date = forms.DateField(required=True, label="Date",
                           widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    time = forms.TimeField(required=True, label="Time",
                           widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                              label="Message")

    class Meta:
        model = Appointment
        # include canonical model fields so ModelForm validation/saving works
        fields = [
            'doctor',
            'patient_user',
            'patient_profile',
            'patient_name',
            'patient_email',
            'patient_phone',
            'appointment_date',
            'appointment_time',
            'reason',
            'status',
        ]
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient_user': forms.Select(attrs={'class': 'form-control'}),
            'patient_profile': forms.Select(attrs={'class': 'form-control'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'patient_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # If editing an instance, pre-fill alias fields from the instance
        if instance:
            self.fields['full_name'].initial = instance.patient_name
            self.fields['email'].initial = instance.patient_email
            self.fields['phone'].initial = instance.patient_phone
            self.fields['date'].initial = instance.appointment_date
            self.fields['time'].initial = instance.appointment_time
            self.fields['message'].initial = instance.reason

    def clean(self):
        cleaned = super().clean()
        # Ensure date/time are not in the past
        date = cleaned.get('date') or cleaned.get('appointment_date')
        time = cleaned.get('time') or cleaned.get('appointment_time')
        if date and time:
            dt = timezone.datetime.combine(date, time)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_default_timezone())
            if dt < timezone.now():
                raise forms.ValidationError("Appointment date/time cannot be in the past.")
        # Require either a linked patient (user/profile) or guest name/email/phone
        has_linked = cleaned.get('patient_user') or cleaned.get('patient_profile')
        has_guest = cleaned.get('full_name') or cleaned.get('patient_name')
        if not has_linked and not has_guest:
            raise forms.ValidationError("Provide either a registered patient (user/profile) or the guest patient name.")
        return cleaned

    def save(self, commit=True):
        # Map alias fields into the model instance before saving
        instance = super().save(commit=False)

        full_name = self.cleaned_data.get('full_name')
        email = self.cleaned_data.get('email')
        phone = self.cleaned_data.get('phone')
        date = self.cleaned_data.get('date')
        time = self.cleaned_data.get('time')
        message = self.cleaned_data.get('message')
        service = self.cleaned_data.get('service')

        if full_name:
            instance.patient_name = full_name
        if email:
            instance.patient_email = email
        if phone:
            instance.patient_phone = phone
        if date:
            instance.appointment_date = date
        if time:
            instance.appointment_time = time
        if message:
            instance.reason = message
        # Optionally store service info in reason for legacy compatibility
        if service:
            if instance.reason:
                instance.reason = f"{instance.reason}\n\nService requested: {service}"
            else:
                instance.reason = f"Service requested: {service}"

        if commit:
            instance.save()
        return instance


# Registration form using the project's user model
class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes by default
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()


# Backwards-compatible alias for the misspelled form used elsewhere in the codebase
# (views import RegisterationForm — keep this name to avoid ImportError)
RegisterationForm = RegistrationForm


# PatientProfile form
class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        exclude = ('user', 'date_registered', 'last_updated')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure any field without an explicit widget class gets form-control
        for name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


class DoctorProfileForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Doctor
        fields = ('name', 'specialty', 'description', 'image', 'services')