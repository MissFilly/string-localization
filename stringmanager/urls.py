from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'apps.manager.views.MainPageHandler', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^register/$', 'app.views.TranslatorRegistration'),
    url(r'^login/$', 'apps.manager.views.LoginRequest', name='login'),
    url(r'^logout/$', 'apps.manager.views.LogoutRequest', name='logout'),
    url(r'^profile/$', 'apps.manager.views.ProfileHandler', name='profile'),
    url(r'^translate/$', 'apps.manager.views.TranslationHandler', name='translate'),
    url(r'^edit/$', 'apps.manager.views.StringsEditionHandler', name='edit'),
    url(r'^generate/$', 'apps.manager.views.GenerateHandler', name='generate'),
    url(r'^guidelines/$', 'apps.manager.views.GuidelinesHandler', name='guide'),
)