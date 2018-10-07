from django.template import Library

register = Library()

@register.filter
def phone_filter(phone_number):
    casted_phone_number = phone_number[:3] + '*'*4 + phone_number[7:]
    return casted_phone_number