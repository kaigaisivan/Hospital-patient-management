from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .decorators import admin_required, doctor_required, patient_required
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect, get_object_or_404

from .models import Contact, Doctor, Appointment, Service, LabSample

# Your imports
from medifiti.forms import PatientForm
from medifiti.models import Patient, Appointment
from .forms import AppointmentForm

# Jackie’s imports
from .forms import RegisterationForm
from django.contrib.auth.models import User

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


# -----------------------------
# Basic Public Pages
# -----------------------------
def index(request):
    # show only active services, newest first
    services_qs = Service.objects.filter(active=True).order_by('-created_at')[:6]
    return render(request, 'index.html', {'services': services_qs})

def services(request):
    services_qs = Service.objects.filter(active=True).order_by('-updated_at')
    return render(request, 'services.html', {'services': services_qs})
def service_detail(request, slug):
    """
    Try DB first (active services only). If no active DB service found,
    fall back to the static mapping as before.
    """
    # lookup active DB service
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

    # fallback mapping (unchanged behavior)
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
    return render(request,'about.html')

def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if full_name and email and message:
            contact = Contact.objects.create(
                full_name=full_name,
                email=email,
                message=message
            )
            # Notify admins about new contact using HTML + text templates
            subject = f"New contact message from {contact.full_name}"
            context = {
                'contact': contact,
            }
            # Render templates
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
            # Send confirmation email to the user who submitted the contact
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
    
    return render(request,'contact.html')

def doctors(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request,'doctors.html', context)

def departments(request):
    return render(request,'departments.html')

# python
# File: `medifiti/views.py` — ensure only this unified view exists (remove any other `book_appointment` definitions)

def book_appointment(request, doctor_id=None):
    """
    Unified booking view:
    - If doctor_id is provided: show/process `book_appointment.html` (book for specific doctor).
    - If no doctor_id: show/process generic `appointment.html` with AppointmentForm.
    """
    doctor = None
    if doctor_id is not None:
        doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        if doctor:
            # legacy/doctor-specific POST handling (keeps current simple flow)
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
            # generic appointment form handling
            form = AppointmentForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your appointment has been booked successfully!')
                return redirect('index')
            return render(request, 'appointment.html', {'form': form})
    else:
        # GET
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
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@admin_required
def admin_dashboard(request):
    contacts = Contact.objects.all().order_by('-created_at')
    if request.method == 'POST':
        admin = request.user
        admin.notification_email = request.POST.get('notification_email', admin.notification_email)
        admin.notification_method = request.POST.get('notification_method', admin.notification_method)
        admin.save()
        messages.success(request, 'Notification settings updated!')
    return render(request, 'admin_dashboard.html', {'contacts': contacts, 'admin': request.user})

@doctor_required
def doctor_dashboard(request):
    doctor_obj = None
    try:
        doctor_obj = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor_obj = None
    appointments = doctor_obj.appointments.all().order_by('appointment_date') if doctor_obj else []
    return render(request, 'doctor_dashboard.html', {'doctor': doctor_obj, 'appointments': appointments})

@patient_required
def patient_dashboard(request):
    user_appointments = Appointment.objects.filter(patient_email=request.user.email)
    services = Service.objects.all()
    return render(request, 'patient_dashboard.html', {'appointments': user_appointments, 'services': services})
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def doctors(request):
    return render(request, 'doctors.html')

def departments(request):
    return render(request, 'departments.html')


# -----------------------------
# Your Patient CRUD + Admin
# -----------------------------
def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = PatientForm()

    return render(request, 'patient_form.html', {'form': form})


def admin_dashboard(request):
    patients = Patient.objects.all()
    return render(request, 'admin_dashboard.html', {'patients': patients})


def update_patient(request, id):
    patient = Patient.objects.get(id=id)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'patient_form.html', {'form': form})


def delete_patient(request, id):
    patient = Patient.objects.get(id=id)
    patient.delete()
    return redirect('admin_dashboard')


# -----------------------------
# Appointment System
# -----------------------------
def admin_appointments(request):
    appointments = Appointment.objects.all().order_by('-date')
    return render(request, 'admin_appointments.html', {'appointments': appointments})


# -----------------------------
# Jackie’s Authentication System
# -----------------------------
def register(request):
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'index.html')
    else:
        form = RegisterationForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    profile = getattr(request.user, 'patientprofile', None)
    from .forms import PatientProfileForm

    if profile is None:
        from .models import PatientProfile
        profile = PatientProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = PatientProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('index')


# -----------------------------
# Jackie’s Dashboard Views
# -----------------------------
@login_required
def appointments(request):
    return render(request, 'appointments.html')

@login_required
def prescriptions(request):
    return render(request, 'prescriptions.html')

@login_required
def medical_history(request):
    profile = request.user.patientprofile
    return render(request, 'medical_history.html', {'profile': profile})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents logout after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})
def emergency_contact(request):
    return render(request, 'emergency_contact.html')
@login_required
def medical_files(request):
    # We can later extend this to show uploaded files or patient records
    return render(request, 'medical_files.html')

