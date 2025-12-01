from medifiti.models import Service, LabSample

Service.objects.update_or_create(slug='general-consultation', defaults={
    'title':'General Consultation',
    'short_description':'Professional health check-ups and diagnosis.',
    'description':'Meet our general physicians for routine check-ups, diagnosis and primary care.'
})
Service.objects.update_or_create(slug='emergency-care', defaults={
    'title':'Emergency Care',
    'short_description':'24/7 emergency services with rapid response.',
    'description':'24/7 emergency department with rapid response and ambulance services.'
})
Service.objects.update_or_create(slug='lab-services', defaults={
    'title':'Laboratory Services',
    'short_description':'Accurate lab tests and medical diagnostics.',
    'description':'Comprehensive lab testing including blood tests, urine, microbiology and imaging.'
})

if not LabSample.objects.filter(sample_id='SAMPLE123').exists():
    LabSample.objects.create(sample_id='SAMPLE123', status='Processing', notes='Example sample created for testing.')

print('Services and sample created/ensured.')
