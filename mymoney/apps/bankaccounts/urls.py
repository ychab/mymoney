from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^$',
        views.BankAccountListView.as_view(),
        name='list'
    ),
    url(
        r'^create/$',
        views.BankAccountCreateView.as_view(),
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
