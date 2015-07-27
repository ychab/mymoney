from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _


class MyMoneyAuthenticationForm(AuthenticationForm):
    """
    Override default authentication form for theming only.
    """

    def __init__(self, request=None, *args, **kwargs):
        super(MyMoneyAuthenticationForm, self).__init__(
            request, *args, **kwargs
        )
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Username'),
            'class': 'form-control',
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': _('Password'),
            'class': 'form-control',
        })
