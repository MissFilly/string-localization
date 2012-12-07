from app.models import String
from django.http import HttpResponse
from zipfile import ZipFile
from StringIO import StringIO
import elementtree.ElementTree as ET

class Android():
    def __init__(self, app, langs):
        app = app
        langs = langs
    def generate_file(self, lang):
        if lang.name=='English':
            strings = String.objects.filter(enabled=True, language=lang) # Filter for application
    def download_files(self):
        in_memory = StringIO()

        zip_file = ZipFile(in_memory, 'w')
        for l in self.langs:
            if l.name == 'English':
                zip_file.writestr('values/strings.xml', generate_file(l))
            else:
                zip_file.writestr('values-' + l.iso_639 + '/strings.xml',
                                  generate_file(l))
        for file in filelist:
            file.create_system = 0

        zip_file.close()
        compressed = HttpResponse(mimetype='application/zip')
        compressed['Content-Disposition'] = 'attachment; filename='+app.__unicode__()
        return compressed