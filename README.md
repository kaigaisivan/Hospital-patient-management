# Hospital Patient Management (Django)
https://hospital-patient-management.onrender.com/

Local development for a small hospital patient management demo built with Django.

Quick start

- Create and activate a virtualenv (optional if you already have `.venv`).
- Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt || pip install django pillow
```

- Run migrations and create an admin user:

```bash
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py createsuperuser
```

- Seed demo services and doctors (management command available):

```bash
./.venv/bin/python manage.py populate_doctors
# or use the provided shell one-liner in the repo to create Services
```

- Run the development server:

```bash
./.venv/bin/python manage.py runserver
```

Testing

Run the Django tests (the test suite uses an in-memory email backend):

```bash
./.venv/bin/python manage.py test
```

Notes

- Emails are configured to use the console backend by default for development. Update `DoctorsBooking/settings.py` with SMTP credentials and `ADMINS` for real email delivery.
- Media files are served in `DEBUG` mode from `MEDIA_URL`/`MEDIA_ROOT` configured in settings.
