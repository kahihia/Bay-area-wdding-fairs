from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
import re
register = template.Library()

@register.filter(name='addcss')
def addcss(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
@stringfilter
def stripjs(value):
    stripped = re.sub(r'<script(?:\s[^>]*)?(>(?:.(?!/script>))*</script>|/>)', \
                      '', force_unicode(value), flags=re.S)
    return mark_safe(stripped)

@register.filter
def get_at_index(list, index):
    try:
        return list[index]
    except Exception as e:
        print "myfilterspy 24: ",e