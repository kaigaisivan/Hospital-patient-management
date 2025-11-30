from django.shortcuts import render, redirect
from .forms import RegisterationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.
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
    # Ensure the user has a profile (signal should create it on user creation)
    profile = getattr(request.user, 'patientprofile', None)
    from .forms import PatientProfileForm

    if profile is None:
        # create profile if missing
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


# Dashboard Feature Views (Placeholder Pages)
@login_required
def appointments(request):
    """View for patient appointments"""
    return render(request, 'appointments.html')


@login_required
def prescriptions(request):
    """View for patient prescriptions"""
    return render(request, 'prescriptions.html')


@login_required
def medical_history(request):
    """View for patient medical history"""
    profile = request.user.patientprofile
    return render(request, 'medical_history.html', {'profile': profile})


@login_required
def change_password(request):
    """View for changing password"""
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully updated!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})


@login_required
def emergency_contact(request):
    """View for emergency contact information"""
    profile = request.user.patientprofile
    
    if request.method == 'POST' and request.POST.get('edit_emergency') == 'true':
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.emergency_contact_relation = request.POST.get('emergency_contact_relation', '')
        profile.save()
        messages.success(request, 'Emergency contact information updated successfully!')
        return redirect('emergency-contact')
    
    return render(request, 'emergency_contact.html', {'profile': profile})


@login_required
def medical_files(request):
    """View for uploading/downloading medical files"""
    return render(request, 'medical_files.html')
