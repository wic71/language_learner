from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Lägger till en CSS-klass till ett formulärfält.
    Används i templates som: {{ field|add_class:"my-css" }}
    """
    return field.as_widget(attrs={**field.field.widget.attrs, "class": css_class})
