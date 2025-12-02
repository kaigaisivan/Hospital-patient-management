# python
# File: `medifiti/forms.py`
from django import forms
from .models import Doctor, Service, Patient, Appointment, PatientProfile, Facility
from django.contrib.auth import get_user_model
from .models import Facility
User = get_user_model()

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ('first_name', 'last_name', 'age', 'email', 'phone_number', 'location')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Appointment
        fields = (
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
        )
        widgets = {
            'patient_user': forms.Select(attrs={'class': 'form-select'}),
            'patient_profile': forms.Select(attrs={'class': 'form-select'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'patient_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        # ensure either a linked user/profile or guest contact details are provided
        if not cleaned.get('patient_user') and not cleaned.get('patient_profile'):
            if not (cleaned.get('patient_name') and cleaned.get('patient_email')):
                raise forms.ValidationError('Provide either a patient account/profile or guest name and email.')
        return cleaned

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = (
            'date_of_birth', 'gender', 'phone', 'address_line1', 'address_line2',
            'city', 'state_province', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_relation', 'emergency_contact_phone',
            'blood_type', 'allergies', 'medications', 'medical_conditions',
            'insurance_provider', 'insurance_number', 'profile_photo_url'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'insurance_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class DoctorProfileForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select services this doctor offers."
    )

    class Meta:
        model = Doctor
        fields = ('name', 'specialty', 'description', 'image', 'services')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full name', 'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'placeholder': 'e.g. Cardiology', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'services':
                field.widget.attrs.setdefault('class', 'form-check')
                continue
            widget = field.widget
            if not isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault('class', 'form-control')

        if self.instance and getattr(self.instance, 'pk', None):
            self.fields['services'].initial = self.instance.services.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance



class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = ('name', 'address', 'phone', 'email', 'emergency_phone', 'description', 'logo')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }