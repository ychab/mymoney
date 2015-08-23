from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^list/(?P<bankaccount_pk>\d+)/$',
        views.BankTransactionListView.as_view(),
        name='list',
    ),
    url(
        r'^calendar/(?P<bankaccount_pk>\d+)/',
        views.BankTransactionCalendarView.as_view(),
        name='calendar',
    ),
    url(
        r'^calendar-ajax-events/(?P<bankaccount_pk>\d+)/$',
        views.BankTransactionCalendarEventsAjax.as_view(),
        name='calendar_ajax_events',
    ),
    url(
        r'^calendar-ajax-event/(?P<pk>\d+)/$',
        views.BankTransactionCalendarEventAjax.as_view(),
        name='calendar_ajax_event',
    ),
    url(
        r'^create/(?P<bankaccount_pk>\d+)/$',
        views.BankTransactionCreateView.as_view(),
        name='create',
    ),
    url(
        r'^(?P<pk>\d+)/update/$',
        views.BankTransactionUpdateView.as_view(),
        name='update',
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        views.BankTransactionDeleteView.as_view(),
        name='delete',
    ),
    url(
        r'^delete/(?P<bankaccount_pk>\d+)/$',
        views.BankTransactionDeleteMultipleView.as_view(),
        name='delete_multiple',
    ),
]
