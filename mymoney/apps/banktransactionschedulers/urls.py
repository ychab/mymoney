from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^list/(?P<bankaccount_pk>\d+)/$',
        views.BankTransactionSchedulerListView.as_view(),
        name='list'
    ),
    url(
        r'^create/(?P<bankaccount_pk>\d+)/$',
        views.BankTransactionSchedulerCreateView.as_view(),
        name='create'
    ),
    url(
        r'^(?P<pk>\d+)/update/$',
        views.BankTransactionSchedulerUpdateView.as_view(),
        name='update'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        views.BankTransactionSchedulerDeleteView.as_view(),
        name='delete',
    ),
]
