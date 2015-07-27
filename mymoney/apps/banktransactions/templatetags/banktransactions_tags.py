from django import template

register = template.Library()


@register.filter(is_safe=True)
def banktransactionfield(form, pk):
    """
    Just a dictionary accessor.
    """
    try:
        return form['banktransaction_' + str(pk)]
    except KeyError:
        pass
