from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(
        r'^list/$',
        login_required(views.BankTransactionTagListView.as_view()),
        name='list'
    ),
    url(
        r'^create/$',
        permission_required(
            ('banktransactiontags.add_banktransactiontag',),
            raise_exception=True
        )(views.BankTransactionTagCreateView.as_view()),
        name='create'
    ),
    url(
        r'^(?P<pk>\d+)/update/$',
        views.BankTransactionTagUpdateView.as_view(),
        name='update'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        views.BankTransactionTagDeleteView.as_view(),
        name='delete',
    ),
]
