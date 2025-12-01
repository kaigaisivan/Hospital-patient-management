import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','DoctorsBooking.settings')
import django
django.setup()
from django.core.mail import mail_admins
print('Sending test mail_admins...')
mail_admins('Test admin mail','This is a test from console backend')
print('Done')
