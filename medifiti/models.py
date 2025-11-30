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