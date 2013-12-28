from django import template

register = template.Library()

@register.filter
def count_words(text):
    return len(text.split())

@register.filter
def plural(text):
    return count_words(text) > 1

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''
