from django.conf.urls import patterns, include, url
from polls.views import HomeView, PollView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view()),
    url(r'^poll/(?P<pk>[0-9]+)/$', PollView.as_view(), name='poll_views_poll'),
    url(r'^admin/', include(admin.site.urls)),
)
