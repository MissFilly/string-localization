from django.contrib import admin
from apps.manager.models import Translator, Language, String, App

class StringAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('app', 'language')
    exclude = ('original_string',)

admin.site.register(Translator)
admin.site.register(Language)
admin.site.register(String, StringAdmin)
admin.site.register(App)