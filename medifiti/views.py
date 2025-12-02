# python
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
from django.db.models import Q

import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.db.models import Prefetch

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required

from .decorators import admin_required, doctor_required, patient_required
from .models import (
    CustomUser, Contact, Doctor, Appointment, Service, LabSample,
    Patient, PatientProfile, Facility,
)
from .forms import (
    PatientForm, AppointmentForm, PatientProfileForm, DoctorProfileForm, FacilityForm,
)


# --- Public pages ---
def index(request):
    services_qs = Service.objects.filter(active=True).order_by('-created_at')[:6]
    facility = Facility.objects.first()  # returns None if not created
    return render(request, 'index.html', {'services': services_qs, 'facility': facility})


@admin_required
def contact_detail(request, id):
    """
    Simple contact detail view for admin.
    """
    contact = get_object_or_404(Contact, id=id)
    return render(request, 'contact_detail.html', {'contact': contact})

@admin_required
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    messages.success(request, 'Contact message deleted.')
    return redirect('admin_dashboard')

def services(request):
    services_qs = Service.objects.filter(active=True).order_by('-updated_at')
    return render(request, 'services.html', {'services': services_qs})


def service_detail(request, slug):
    service_obj = Service.objects.filter(slug=slug, active=True).first()
    sample_result = None

    if service_obj:
        triage_options = [
            ('respiratory', 'Fever, cough, sore throat', 'Respiratory / General Physician'),
            ('dental', 'Tooth pain or bleeding gums', 'Dentistry'),
            ('cardiac', 'Chest pain or shortness of breath', 'Cardiology / Emergency'),
            ('abdominal', 'Abdominal pain, nausea', 'General Surgery / Gastroenterology'),
        ]
        triage_result = None
        if request.method == 'POST' and slug == 'general-consultation' and request.POST.get('triage_submit'):
            selected = request.POST.getlist('symptoms')
            depts = [dept for key, label, dept in triage_options if key in selected]
            triage_result = ('Recommended departments: ' + ', '.join(sorted(set(depts)))) if depts else 'No symptoms selected; please select at least one symptom.'

        if request.method == 'POST' and slug == 'lab-services':
            sample_id = (request.POST.get('sample_id') or '').strip()
            if sample_id:
                try:
                    sample = LabSample.objects.get(sample_id__iexact=sample_id)
                    sample_result = f'Sample {sample.sample_id}: status={sample.status}. Notes: {sample.notes}'
                except LabSample.DoesNotExist:
                    sample_result = f'No tracking record found for sample id "{sample_id}".'

        context = {
            'service': {
                'title': service_obj.title,
                'description': service_obj.short_description or service_obj.description,
                'content': [service_obj.description] if service_obj.description else [],
            },
            'service_obj': service_obj,
            'slug': slug,
            'sample_result': sample_result,
            'triage_options': triage_options,
            'triage_result': triage_result,
        }
        return render(request, 'service_detail.html', context)

    # fallback mapping
    services_map = {
        'general-consultation': {
            'title': 'General Consultation',
            'description': 'Meet our general physicians for routine check-ups, diagnosis and primary care.',
            'content': [
                'If you have symptoms such as fever, cough, persistent pain, or general unwell feeling, book a general consultation.',
                'Our physicians will assess symptoms and refer you to specialists when necessary.'
            ],
            'symptoms': [
                ('Fever, cough, sore throat', 'Respiratory / General Physician'),
                ('Tooth pain or bleeding gums', 'Dentistry'),
                ('Chest pain or shortness of breath', 'Cardiology / Emergency'),
                ('Abdominal pain, nausea', 'General Surgery / Gastroenterology'),
            ]
        },
        'emergency-care': {
            'title': 'Emergency Care',
            'description': '24/7 emergency department with rapid response and ambulance services.',
            'content': [
                'For life-threatening emergencies call our ambulance immediately.',
                'Our emergency team stabilizes and routes patients to the correct specialty.'
            ],
            'phone': '+1234567890'
        },
        'lab-services': {
            'title': 'Laboratory Services',
            'description': 'Comprehensive lab testing with fast turnaround times.',
            'content': [
                'We provide blood tests, urine tests, microbiology, and imaging support.',
                'Use the sample tracking box below to check a sample status (sample tracking is a placeholder).'
            ]
        }
    }

    svc = services_map.get(slug)
    if not svc:
        return render(request, 'services.html', {'error': 'Service not found.'})

    if request.method == 'POST' and slug == 'lab-services':
        sample_id = (request.POST.get('sample_id') or '').strip()
        if sample_id:
            sample_result = f'No tracking record found for sample id "{sample_id}" (placeholder).'

    context = {
        'service': svc,
        'sample_result': sample_result,
        'slug': slug,
    }
    return render(request, 'service_detail.html', context)


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if full_name and email and message:
            contact = Contact.objects.create(full_name=full_name, email=email, message=message)

            subject = f"New contact message from {contact.full_name}"
            context = {'contact': contact}
            text_content = render_to_string('emails/contact_admin.txt', context)
            html_content = render_to_string('emails/contact_admin.html', context)
            recipients = [email for (_name, email) in getattr(settings, 'ADMINS', [])]
            if recipients:
                try:
                    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, recipients)
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send(fail_silently=True)
                except Exception:
                    pass

            try:
                user_subject = 'Thanks for contacting HospitalCare'
                user_ctx = {'contact': contact}
                user_text = render_to_string('emails/contact_user.txt', user_ctx)
                user_html = render_to_string('emails/contact_user.html', user_ctx)
                user_msg = EmailMultiAlternatives(user_subject, user_text, settings.DEFAULT_FROM_EMAIL, [contact.email])
                user_msg.attach_alternative(user_html, 'text/html')
                user_msg.send(fail_silently=True)
            except Exception:
                pass

            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return render(request, 'contact.html')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'contact.html')


def doctors(request):
    doctors_qs = Doctor.objects.all()
    return render(request, 'doctors.html', {'doctors': doctors_qs})


def departments(request):
    return render(request, 'departments.html')


# --- Appointment booking ---
def book_appointment(request, doctor_id=None):
    doctor = None
    if doctor_id is not None:
        doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        if doctor:
            patient_name = request.POST.get('patient_name')
            patient_email = request.POST.get('patient_email')
            patient_phone = request.POST.get('patient_phone')
            appointment_date = request.POST.get('appointment_date')
            appointment_time = request.POST.get('appointment_time')
            reason = request.POST.get('reason')

            if all([patient_name, patient_email, patient_phone, appointment_date, appointment_time, reason]):
                Appointment.objects.create(
                    doctor=doctor,
                    patient_name=patient_name,
                    patient_email=patient_email,
                    patient_phone=patient_phone,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    reason=reason
                )
                messages.success(request, 'Your appointment has been booked successfully! We will confirm it shortly.')
                return redirect('doctors')
            else:
                messages.error(request, 'Please fill in all fields.')
                return render(request, 'book_appointment.html', {'doctor': doctor})
        else:
            form = AppointmentForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your appointment has been booked successfully!')
                return redirect('index')
            return render(request, 'appointment.html', {'form': form})
    else:
        if doctor:
            return render(request, 'book_appointment.html', {'doctor': doctor})
        form = AppointmentForm()
        return render(request, 'appointment.html', {'form': form})


# --- Authentication & Dashboards ---
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            if user.role == CustomUser.ROLE_ADMIN:
                return redirect('admin_dashboard')
            elif user.role == CustomUser.ROLE_DOCTOR:
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    # kept name `login_user` so it matches `medifiti/urls.py`; uses `auth_login` to avoid name clash
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.role == CustomUser.ROLE_ADMIN:
                return redirect('admin_dashboard')
            elif user.role == CustomUser.ROLE_DOCTOR:
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
def logout_user(request):
    auth_logout(request)
    return redirect('index')


@admin_required
def admin_dashboard(request):
    contacts = Contact.objects.all().order_by('-created_at')
    patients = Patient.objects.all()

    if request.method == 'POST':
        admin = request.user
        admin.notification_email = request.POST.get('notification_email', admin.notification_email)
        admin.notification_method = request.POST.get('notification_method', admin.notification_method)
        admin.save()
        messages.success(request, 'Notification settings updated!')
        return redirect('admin_dashboard')

    context = {
        'contacts': contacts,
        'patients': patients,
        'admin': request.user,
    }
    return render(request, 'admin_dashboard.html', context)


@doctor_required
def doctor_dashboard(request):
    doctor_obj, _ = Doctor.objects.get_or_create(user=request.user, defaults={'name': request.user.get_full_name() or request.user.username})
    # Prefetch patient profiles to avoid N+1 and include patient_user
    appointments = Appointment.objects.filter(doctor=doctor_obj).select_related('patient_user', 'patient_profile').order_by('appointment_date', 'appointment_time')
    return render(request, 'doctor_dashboard.html', {
        'doctor': doctor_obj,
        'appointments': appointments,
    })
@doctor_required
def doctor_profile(request):
    doctor_obj, created = Doctor.objects.get_or_create(user=request.user, defaults={'name': request.user.get_full_name() or request.user.username})
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorProfileForm(instance=doctor_obj)
    return render(request, 'doctor_profile.html', {'form': form, 'doctor': doctor_obj})
@patient_required
def patient_dashboard(request):
    user_appointments = Appointment.objects.filter(Q(patient_email=request.user.email) | Q(patient_user=request.user) | Q(patient_profile__user=request.user)).distinct()
    services_qs = Service.objects.all()
    return render(request, 'patient_dashboard.html', {'appointments': user_appointments, 'services': services_qs})


# --- Patient CRUD for admin ---
def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = PatientForm()
    return render(request, 'patient_form.html', {'form': form})


def update_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patient_form.html', {'form': form})


def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    patient.delete()
    return redirect('admin_dashboard')


# --- Admin appointments listing ---
@admin_required
def admin_appointments(request):
    appointments = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')
    return render(request, 'admin_appointments.html', {'appointments': appointments})


# --- Patient profile & account views ---
@login_required
def profile(request):
    profile, _created = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = PatientProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form})


@login_required
def appointments(request):
    appointments_qs = Appointment.objects.filter(
        Q(patient_user=request.user) |
        Q(patient_profile__user=request.user) |
        Q(patient_email__iexact=(request.user.email or ''))
    ).distinct().order_by('-appointment_date', '-appointment_time')
    return render(request, 'appointments.html', {'appointments': appointments_qs})


@login_required
def prescriptions(request):
    return render(request, 'prescriptions.html')


@login_required
def medical_history(request):
    profile, _created = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, 'medical_history.html', {'profile': profile})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def emergency_contact(request):
    profile, _created = PatientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('emergency_contact_name', '').strip()
        relation = request.POST.get('emergency_contact_relation', '').strip()
        phone = request.POST.get('emergency_contact_phone', '').strip()

        if name or relation or phone:
            profile.emergency_contact_name = name
            profile.emergency_contact_relation = relation
            profile.emergency_contact_phone = phone
            profile.save()
            messages.success(request, 'Emergency contact updated.')
            return redirect('emergency-contact')
        else:
            messages.error(request, 'Please provide at least one emergency contact field.')

    return render(request, 'emergency_contact.html', {'profile': profile})


@login_required
def medical_files(request):
    return render(request, 'medical_files.html')
def facilities_list(request):
    facilities = Facility.objects.all().order_by('-updated_at')
    return render(request, 'facilities.html', {'facilities': facilities})

def facility_detail(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    return render(request, 'facility.html', {'facility': facility})
def facility(request):
    """
    Public facility page showing the single Facility instance (if any).
    """
    facility = Facility.objects.first()
    return render(request, 'facility.html', {'facility': facility})


@admin_required
def edit_facility(request):
    facility, _ = Facility.objects.get_or_create(pk=1, defaults={'name': 'Our Facility'})
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facility information updated.')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FacilityForm(instance=facility)
    return render(request, 'edit_facility.html', {'form': form, 'facility': facility})

@admin_required
def export_patients_csv(request):
    """
    Export patients as CSV for admin.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'first_name', 'last_name', 'age', 'email', 'phone_number', 'location', 'created_at'])
    for p in Patient.objects.all().order_by('-created_at'):
        writer.writerow([p.id, p.first_name, p.last_name, p.age or '', p.email or '', p.phone_number or '', p.location or '', p.created_at])
    return response

@login_required
def dashboard_redirect(request):
    """
    Central named 'dashboard' view used by built-in auth redirect.
    Sends users to their role-specific dashboard so `reverse('dashboard')` works.
    """
    user = request.user
    role = getattr(user, 'role', None)
    if role == CustomUser.ROLE_ADMIN:
        return redirect('admin_dashboard')
    if role == CustomUser.ROLE_DOCTOR:
        return redirect('doctor_dashboard')
    # default for patients and anonymous fallback
    return redirect('patient_dashboard' if user.is_authenticated else 'index')