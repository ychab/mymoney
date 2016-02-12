from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^list/$',
        views.BankTransactionTagListView.as_view(),
        name='list'
    ),
    url(
        r'^create/$',
        views.BankTransactionTagCreateView.as_view(),
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
