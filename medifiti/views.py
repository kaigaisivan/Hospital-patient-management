from django.shortcuts import render

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
