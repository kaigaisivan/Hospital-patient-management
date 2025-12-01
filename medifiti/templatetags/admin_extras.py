from django import template
from ..models import Contact

register = template.Library()


@register.inclusion_tag('admin/recent_contacts.html')
def recent_contacts(count=5):
    """Return the most recent Contact entries for admin dashboard."""
    qs = Contact.objects.all().order_by('-created_at')[:count]
    return {'contacts': qs}
