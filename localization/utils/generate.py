# -*- coding: utf-8 -*-

from app.models import String
from django.http import HttpResponse
from zipfile import ZipFile
from StringIO import StringIO
from lxml import etree


class Android():

    def generate_file(self, lang, app):
        if lang.name == 'English':
            strings = String.objects.filter(enabled=True, language=lang,
                                            app=app)
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
        root = etree.Element('resources')
        for string in strings:
            try:
                line = etree.SubElement(root, "string",
                                        name=string.android_name_string)
                line.text = string.text
            # This is just to handle this error while developing.
            # This error should NOT happen once the database y properly populated
            except TypeError:
                pass
        content = etree.tostring(root, encoding='utf-8',
                                 xml_declaration=True, pretty_print=True)
        return content

    def download_files(self, langs, app):
        in_memory = StringIO()

        zip_file = ZipFile(in_memory, 'a')
        for l in langs:
            if l.name == 'English':
                zip_file.writestr('values/strings.xml',
                                  self.generate_file(l, app))
            else:
                zip_file.writestr('values-' + l.iso_639 + '/strings.xml',
                                  self.generate_file(l, app))

        # Fix for Linux zip files read in Windows
        for file in zip_file.filelist:
            file.create_system = 0

        zip_file.close()

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % \
                                          (app.__unicode__().replace(' ', '-'))
        response['Content-Length'] = in_memory.tell

        in_memory.seek(0)
        response.write(in_memory.read())
        return response


class iOS():

    def generate_file():
        pass


class WindowsPhone():

    def generate_file(self, lang, app):
        if lang.name == 'English':
            strings = String.objects.filter(enabled=True, language=lang,
                                            app=app)
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
        root = etree.Element('root')
        for string in strings:
            try:
                line = etree.SubElement(root, "data",
                                        name=string.wp_name_string)
                value = etree.SubElement(line, "value")
                value.text = string.text
            except TypeError:
                pass
        content = etree.tostring(root, encoding='utf-8',
                                 xml_declaration=True, pretty_print=True)
        return content

    def download_files(self, langs, app):
        in_memory = StringIO()

        zip_file = ZipFile(in_memory, 'a')
        for l in langs:
            zip_file.writestr('values-%s-%s.xml' % (l.iso_639, l.iso_3166),
                              self.generate_file(l, app))

        # Fix for Linux zip files read in Windows
        for file in zip_file.filelist:
            file.create_system = 0

        zip_file.close()

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % \
                                          (app.__unicode__().replace(' ', '-'))
        response['Content-Length'] = in_memory.tell

        in_memory.seek(0)
        response.write(in_memory.read())
        return response
