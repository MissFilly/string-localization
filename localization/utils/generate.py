# -*- coding: utf-8 -*-

from app.models import String
from django.http import HttpResponse
from zipfile import ZipFile
from StringIO import StringIO
from lxml import etree


class Android():

    def generate_file(self, lang, app):
        root = etree.Element('resources')
        if lang.name == 'English':
            strings = String.objects.filter(enabled=True, language=lang,
                                            app=app)
            for string in strings:
                line = etree.SubElement(root, 'string',
                                        name=string.android_name_string)
                line.text = string.text
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
            for string in strings:
                line = etree.SubElement(
                                root, 'string',
                                name=string.original_string.android_name_string
                                )
                line.text = string.text
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
                # There's more than one language register with that language
                # code. Subculture code must be specified.
                if langs.filter(iso_639=l.iso_639).count() > 1:
                    zip_file.writestr('values-%s-r%s/strings.xml' %
                                      (l.iso_639, l.iso_3166),
                                      self.generate_file(l, app))
                else:
                    zip_file.writestr('values-%s/strings.xml' % l.iso_639,
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


class WindowsPhone():

    def generate_file(self, lang, app):
        root = etree.Element('root')
        if lang.name == 'English':
            strings = String.objects.filter(enabled=True, language=lang,
                                            app=app)
            for string in strings:
                line = etree.SubElement(
                                root, 'data',
                                name=string.wp_name_string, attrib=
                                {'{http://www.w3.org/XML/1998/namespace}space':
                                'preserve'})
                value = etree.SubElement(line, 'value')
                value.text = string.text
                if string.description:
                    comment = etree.SubElement(line, 'comment')
                    comment.text = string.description
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
            for string in strings:
                line = etree.SubElement(
                            root, 'string',
                            name=string.original_string.wp_name_string, attrib=
                            {'{http://www.w3.org/XML/1998/namespace}space':
                            'preserve'})
                value = etree.SubElement(line, 'value')
                value.text = string.text
                if string.original_string.description:
                    comment = etree.SubElement(line, 'comment')
                    comment.text = string.original_string.description
        content = etree.tostring(root, encoding='utf-8', pretty_print=True)
        return content

    def download_files(self, langs, app):
        in_memory = StringIO()

        zip_file = ZipFile(in_memory, 'a')
        for l in langs:
            if l.name == 'English':
                zip_file.writestr('Strings-AppResources.xml',
                                  self.generate_file(l, app))
            else:
                zip_file.writestr('Strings-AppResources.%s-%s.xml' %
                                  (l.iso_639, l.iso_3166),
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

    def generate_file(self, lang, app):
        content = u""
        if lang.name == 'English':
            strings = String.objects.filter(enabled=True, language=lang,
                                            app=app)
            for string in strings:
                if string.description:
                    content += '\n\n/* %s */' % string.description
                content += '\n"%s" = "%s";' % (string.ios_name_string,
                                               string.text)
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
            for string in strings:
                if string.original_string.description:
                    content += '\n\n/* %s */' % \
                                        string.original_string.description
                content += '\n"%s" = "%s";' % \
                                       (string.original_string.ios_name_string,
                                        string.text)
        return content.encode('utf-16')

    def download_files(self, langs, app):
        in_memory = StringIO()

        zip_file = ZipFile(in_memory, 'a')
        for l in langs:
            if langs.filter(iso_639=l.iso_639).count() > 1:
                zip_file.writestr('%s_%s.lproj/Localizable.strings' %
                                  (l.iso_639, l.iso_3166),
                                  self.generate_file(l, app))
            else:
                zip_file.writestr('%s.lproj/Localizable.strings' % l.iso_639,
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
