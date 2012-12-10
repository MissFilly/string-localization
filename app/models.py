# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Language(models.Model):
    name = models.CharField(max_length=30, verbose_name='Language name')
    iso_639 = models.CharField(max_length=2, verbose_name='Language code')
    iso_3166 = models.CharField(max_length=2, verbose_name='Subculture code')

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return u'%s (%s-%s)' % (self.name, self.iso_639, self.iso_3166)


class App(models.Model):
    name = models.CharField(max_length=30)
    platform = models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s for %s' % (self.name, self.platform)


class Translator(models.Model):
    user = models.OneToOneField(User)
    language = models.ForeignKey(Language)
    words_translated = models.IntegerField()

    def __unicode__(self):
        return '%s - %s' % (self.user.username, self.language.name)


class String(models.Model):
    app = models.ManyToManyField(App)
    text = models.TextField()
    description = models.TextField(null=True, blank=True)
    language = models.ForeignKey(Language)
    android_name_string = models.CharField(max_length=30, null=True, blank=True)
    ios_name_string = models.CharField(max_length=30, null=True, blank=True)
    wp_name_string = models.CharField(max_length=30, null=True, blank=True)
    web_name_string = models.CharField(max_length=30, null=True, blank=True)
    osx_name_string = models.CharField(max_length=30, null=True, blank=True)
    w8_name_string = models.CharField(max_length=30, null=True, blank=True)
    original_string = models.ForeignKey('self', null=True, blank=True)
    translatable = models.BooleanField(default=True)
    last_modif = models.DateTimeField(default=datetime.now())
    translator = models.ForeignKey(Translator, null=True, blank=True)
    frozen = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s (%s)' % (self.text, self.language.name)
