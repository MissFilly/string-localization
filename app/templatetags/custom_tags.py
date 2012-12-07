from django import template

register = template.Library()

@register.filter
def count_words(text):
    return len(text.split())

@register.filter
def plural(text):
    return count_words(text) > 1