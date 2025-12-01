from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Contact, Doctor, Appointment, Service, LabSample
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .decorators import admin_required, doctor_required, patient_required

# Create your views here.
def index(request):
    services_qs = Service.objects.all()[:6]
    return render(request, 'index.html', {'services': services_qs})

def services(request):
    services_qs = Service.objects.all()
    return render(request, 'services.html', {'services': services_qs})


def service_detail(request, slug):
    """Render a simple service detail page for known services.
    Supported slugs: general-consultation, emergency-care, lab-services
    For lab-services we accept a POST with `sample_id` to show a placeholder result.
    """
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

    # Try to load a Service from the database first
    service_obj = None
    try:
        service_obj = Service.objects.get(slug=slug)
    except Service.DoesNotExist:
        service_obj = None

    sample_result = None

    if service_obj:
        # Triage options for general consultation
        triage_options = [
            ('respiratory', 'Fever, cough, sore throat', 'Respiratory / General Physician'),
            ('dental', 'Tooth pain or bleeding gums', 'Dentistry'),
            ('cardiac', 'Chest pain or shortness of breath', 'Cardiology / Emergency'),
            ('abdominal', 'Abdominal pain, nausea', 'General Surgery / Gastroenterology'),
        ]
        triage_result = None
        # Handle triage POST for general consultation
        if request.method == 'POST' and slug == 'general-consultation' and request.POST.get('triage_submit'):
            selected = request.POST.getlist('symptoms')
            # gather departments from selected symptom keys
            depts = []
            for key, label, dept in triage_options:
                if key in selected:
                    depts.append(dept)
            if depts:
                triage_result = 'Recommended departments: ' + ', '.join(sorted(set(depts)))
            else:
                triage_result = 'No symptoms selected; please select at least one symptom.'
        # If lab services, allow lookup via LabSample
        if request.method == 'POST' and slug == 'lab-services':
            sample_id = (request.POST.get('sample_id') or '').strip()
            if sample_id:
                # normalize sample id for lookup (case-insensitive)
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
            'sample_result': sample_result,
            'slug': slug,
            'service_obj': service_obj,
            'triage_options': triage_options,
            'triage_result': triage_result,
        }
        return render(request, 'service_detail.html', context)

    # Fallback to static mapping if no DB service exists
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

def book_appointment(request, doctor_id):
    # Require user to be logged in to book appointment
    if not request.user.is_authenticated:
        return redirect('login')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        patient_email = request.POST.get('patient_email')
        patient_phone = request.POST.get('patient_phone')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        if all([patient_name, patient_email, patient_phone, appointment_date, appointment_time, reason]):
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient_name=patient_name,
                patient_email=patient_email,
                patient_phone=patient_phone,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason
            )
            # Notify admins about new appointment using HTML + text templates
            subject = f"New appointment request: {appointment.patient_name} with Dr. {doctor.name}"
            context = {
                'appointment': appointment,
                'doctor': doctor,
            }
            text_content = render_to_string('emails/appointment_admin.txt', context)
            html_content = render_to_string('emails/appointment_admin.html', context)
            recipients = [email for (_name, email) in getattr(settings, 'ADMINS', [])]
            if recipients:
                try:
                    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, recipients)
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send(fail_silently=True)
                except Exception:
                    pass
            # Send confirmation email to the patient
            try:
                patient_subject = 'Your appointment has been booked'
                patient_text = render_to_string('emails/appointment_patient.txt', context)
                patient_html = render_to_string('emails/appointment_patient.html', context)
                patient_msg = EmailMultiAlternatives(patient_subject, patient_text, settings.DEFAULT_FROM_EMAIL, [appointment.patient_email])
                patient_msg.attach_alternative(patient_html, 'text/html')
                patient_msg.send(fail_silently=True)
            except Exception:
                pass
            messages.success(request, 'Your appointment has been booked successfully! We will confirm it shortly.')
            return redirect('doctors')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {'doctor': doctor}
    return render(request, 'book_appointment.html', context)

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
