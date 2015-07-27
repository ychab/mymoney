from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(
        r'^$',
        login_required(views.BankAccountListView.as_view()),
        name='list'
    ),
    url(
        r'^create/$',
        permission_required(
            ('bankaccounts.add_bankaccount',),
            raise_exception=True
        )(views.BankAccountCreateView.as_view()),
        name='create'
    ),
    url(
        r'^(?P<pk>\d+)/update/$',
        views.BankAccountUpdateView.as_view(),
        name='update'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        views.BankAccountDeleteView.as_view(),
        name='delete'
    ),
]
