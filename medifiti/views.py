from django.shortcuts import render, redirect

# Your imports
from medifiti.forms import PatientForm
from medifiti.models import Patient, Appointment
from .forms import AppointmentForm

# Jackie’s imports
from .forms import RegisterationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


# -----------------------------
# Basic Public Pages
# -----------------------------
def index(request):
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
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AppointmentForm()

    return render(request, 'appointment.html', {'form': form})


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
            return render(request, 'login.html')
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
    from
