from django.conf.urls import url

from . import views

app_name = 'banktransactionanalytics'
urlpatterns = [
    url(
        r'^(?P<bankaccount_pk>\d+)/ratio/$',
        views.RatioView.as_view(),
        name='ratio',
    ),
    url(
        r'^(?P<bankaccount_pk>\d+)/ratio/summary/(?P<tag_id>\d+)/$',
        views.RatioSummaryView.as_view(),
        name='ratiosummary',
    ),
    url(
        r'^(?P<bankaccount_pk>\d+)/trendtime/$',
        views.TrendTimeView.as_view(),
        name='trendtime',
    ),
    url(
        r'^(?P<bankaccount_pk>\d+)/trendtime/summary/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$',
        views.TrendTimeSummaryView.as_view(),
        name='trendtimesummary',
    ),
]
