from django.contrib import admin
from app.models import Translator, Language, String, App

admin.site.register(Translator)
admin.site.register(Language)
admin.site.register(String)
admin.site.register(App)