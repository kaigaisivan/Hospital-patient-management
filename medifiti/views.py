from django.shortcuts import render, redirect

from medifiti.forms import PatientForm
from medifiti.models import Patient, Appointment
from .forms import AppointmentForm



# Create your views here.
def index(request):
    return render (request,'index.html')
def services(request):
    return render(request,'services.html')
def about(request):
    return render(request,'about.html')
def contact(request):
    return render(request,'contact.html')
def doctors(request):
    return render(request,'doctors.html')
def departments(request):
    return render(request,'departments.html')
def create_patient(request):
    if request.method=="POST":
         form=PatientForm(request.POST)
         if form.is_valid():
          form.save()
          return redirect ('admin_dashboard')
    else:
        form=PatientForm()

    return render (request, 'patient_form.html',{'form':form})

#read records from the db
def admin_dashboard(request):
    patients = Patient.objects.all()  # fetch all patients
    return render(request, 'admin_dashboard.html', {'patients': patients})
def update_patient(request,id):
    patient = Patient.objects.get( id=id)
    form=PatientForm(instance=patient)
    if request.method=="POST":
        form=PatientForm(request.POST,instance=patient)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')

    return render (request, 'patient_form.html',{'form':form})
def delete_patient(request,id):
    patient      = Patient.objects.get( id=id)
    patient.delete()
    return redirect('admin_dashboard')

#appointment
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
    appointments = Appointment.objects.all().order_by('-date')  # newest first
    return render(request, 'admin_appointments.html', {'appointments': appointments})