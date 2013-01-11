from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.MainPageHandler'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^register/$', 'app.views.TranslatorRegistration'),
    url(r'^login/$', 'app.views.LoginRequest'),
    url(r'^logout/$', 'app.views.LogoutRequest'),
    url(r'^profile/$', 'app.views.ProfileHandler'),
    url(r'^translate/$', 'app.views.TranslationHandler'),
    url(r'^modify/$', 'app.views.ModifyStringsHandler'),
    url(r'^generate/$', 'app.views.GenerateHandler'),
    url(r'^guidelines/$', 'app.views.GuidelinesHandler'),
)
