from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?:i18n/)?$', 'app.views.MainPageHandler'),
    url(r'^(?:i18n/)?admin/', include(admin.site.urls)),
    #url(r'^register/$', 'app.views.TranslatorRegistration'),
    url(r'^(?:i18n/)?login/$', 'app.views.LoginRequest'),
    url(r'^(?:i18n/)?logout/$', 'app.views.LogoutRequest'),
    url(r'^(?:i18n/)?profile/$', 'app.views.ProfileHandler'),
    url(r'^(?:i18n/)?translate/$', 'app.views.TranslationHandler'),
    url(r'^(?:i18n/)?modify/$', 'app.views.ModifyStringsHandler'),
    url(r'^(?:i18n/)?generate/$', 'app.views.GenerateHandler'),
    url(r'^(?:i18n/)?guidelines/$', 'app.views.GuidelinesHandler'),
)
