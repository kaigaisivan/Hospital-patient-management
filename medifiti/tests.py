from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from .models import Contact, Doctor, Appointment


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactBookingTests(TestCase):
	def test_contact_post_creates_contact_and_sends_email(self):
		data = {
			'full_name': 'Test User',
			'email': 'test@example.com',
			'message': 'Hello, this is a test.'
		}
		resp = self.client.post(reverse('contact'), data)
		# Contact saved
		self.assertEqual(Contact.objects.filter(email='test@example.com').count(), 1)
		# At least one email sent (confirmation to user)
		self.assertGreaterEqual(len(mail.outbox), 1)

	def test_book_appointment_creates_and_sends_emails(self):
		doctor = Doctor.objects.create(name='Test Doc', specialty='General', description='Test')
		url = reverse('book_appointment', args=[doctor.id])
		data = {
			'patient_name': 'Alice',
			'patient_email': 'alice@example.com',
			'patient_phone': '1234567890',
			'appointment_date': '2025-12-01',
			'appointment_time': '09:00',
			'reason': 'Routine checkup',
		}
		resp = self.client.post(url, data, follow=True)
		self.assertEqual(Appointment.objects.filter(patient_email='alice@example.com').count(), 1)
		# At least one email (confirmation to patient and/or admin)
		self.assertGreaterEqual(len(mail.outbox), 1)
