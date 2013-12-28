from apps.manager.models import String
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
                keys = string.android_name_string.split(',')
                for key in keys:
                    line = etree.SubElement(root, 'string', name=key)
                    line.text = string.text
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
            for string in strings:
                keys = string.original_string.android_name_string.split(',')
                for key in keys:
                    line = etree.SubElement(root, 'string', name=key)
                    line.text = string.text
        content = etree.tostring(root, encoding='utf-8',
                                 xml_declaration=True, pretty_print=True)
        # As our Android strings already have special characters scaped, the
        # automatic scape from lxml would mess them up
        return content.replace('&amp;', '&')

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
        response['Content-Length'] = in_memory.tell()

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
                if app.platform == 'Windows Phone':
                    keys = string.wp_name_string.split(',')
                elif app.platform == 'Windows 8':
                    keys = string.w8_name_string.split(',')
                for key in keys:
                    line = etree.SubElement(
                                 root, 'data',
                                 name=key, attrib=
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
                if app.platform == 'Windows Phone':
                    keys = string.original_string.wp_name_string.split(',')
                elif app.platform == 'Windows 8':
                    keys = string.original_string.w8_name_string.split(',')
                for key in keys:
                    line = etree.SubElement(
                                root, 'data',
                                name=key, attrib=
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
        response['Content-Length'] = in_memory.tell()

        in_memory.seek(0)
        response.write(in_memory.read())
        return response


class iOS():

    def generate_file(self, lang, app):
        content = u''

        if lang.name == 'English':
            strings = String.objects.filter(enabled=True, language=lang,
                                            app=app)
            for string in strings:
                if app.platform == 'iOS':
                    keys = string.ios_name_string.split(',')
                elif app.platform == 'OSX':
                    keys = string.osx_name_string.split(',')
                if string.description:
                    content += '\n\n/* %s */' % string.description
                for key in keys:
                    content += '\n"%s" = "%s";' % (key, string.text)
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
            for string in strings:
                if app.platform == 'iOS':
                    keys = string.original_string.ios_name_string.split(',')
                elif app.platform == 'OSX':
                    keys = string.original_string.osx_name_string.split(',')
                if string.original_string.description:
                    content += '\n\n/* %s */' % \
                                        string.original_string.description
                for key in keys:
                    content += '\n"%s" = "%s";' % (key, string.text)
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
        response['Content-Length'] = in_memory.tell()

        in_memory.seek(0)
        response.write(in_memory.read())
        return response


class Web():

    def generate_file(self, lang, app):
        content = u'# -*- coding: utf-8 -*-\n' + \
                  'class String\n' + \
                  'def t_' + lang.iso_639 + '\n' \
                  'case self\n'
        if app.name == 'All':
            strings = String.objects.filter(enabled='True', language=lang,
                                            original_string__app__platform='Web')
        else:
            strings = String.objects.filter(enabled=True, language=lang,
                                            original_string__app=app)
        for string in strings:
            content += 'when "%s": return "%s"\n' % (string.original_string.text.replace('"', '\\"'),
                                                     string.text.replace('"', '\\"'))
        content += '\nelse return self' + '\nend' * 3
        return content.encode('utf-8')

    def download_files(self, langs, app):
        in_memory = StringIO()

        zip_file = ZipFile(in_memory, 'a')
        for l in langs:
            if l.name == 'English':
                pass
            if langs.filter(iso_639=l.iso_639).count() > 1:
                zip_file.writestr('%s-%s.rb' % (l.iso_639, l.iso_3166),
                                  self.generate_file(l, app))
            else:
                zip_file.writestr('%s.rb' % l.iso_639,
                                  self.generate_file(l, app))

        # Fix for Linux zip files read in Windows
        for file in zip_file.filelist:
            file.create_system = 0

        zip_file.close()

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % \
                                          (app.__unicode__().replace(' ', '-'))
        response['Content-Length'] = in_memory.tell()

        in_memory.seek(0)
        response.write(in_memory.read())
        return response
