from django.core.management.base import BaseCommand
from medifiti.models import Doctor

class Command(BaseCommand):
    help = 'Populate sample doctors data'

    def handle(self, *args, **options):
        doctors_data = [
            {
                'name': 'John Mwangi',
                'specialty': 'General Physician',
                'description': 'Experienced in routine check-ups, diagnosis, and preventive care.'
            },
            {
                'name': 'Sarah Achieng',
                'specialty': 'Dentist',
                'description': 'Specialist in dental check-ups, cleaning, and oral health treatment.'
            },
            {
                'name': 'Kelvin Otieno',
                'specialty': 'Cardiologist',
                'description': 'Expert in heart health, cardiovascular diagnosis, and treatment.'
            },
        ]

        for doctor_data in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                name=doctor_data['name'],
                defaults={
                    'specialty': doctor_data['specialty'],
                    'description': doctor_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created doctor: Dr. {doctor.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Doctor already exists: Dr. {doctor.name}'))
