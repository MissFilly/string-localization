# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory, formset_factory
from django.db.models import Q, F
from app.forms import LoginForm, GenerateForm, ModifyForm, TranslateForm  # , RegistrationForm
from app.models import Translator, String
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from localization.utils import extra_funcs
from generator import generate


def MainPageHandler(request):
    user = request.user
    return render_to_response('index.html', {'user': user},
                              context_instance=RequestContext(request))


#def TranslatorRegistration(request):
    #if request.user.is_authenticated():
        #try:
            #translator = request.user.get_profile()
            #return HttpResponseRedirect('/i18n/profile/')
        #except Translator.DoesNotExist:
            #return render_to_response('no_translator_profile.html',
                                      #context_instance=RequestContext(request))
    #if request.method == 'POST':
        #form = RegistrationForm(request.POST)
        #if form.is_valid():
            #user = User.objects.create_user(
                                       #username=form.cleaned_data['username'],
                                       #email=form.cleaned_data['email'],
                                       #password=form.cleaned_data['password']
                                       #)
            #user.first_name = form.cleaned_data['first_name']
            #user.last_name = form.cleaned_data['last_name']
            #user.save()
            #translator = Translator(user=user,
                                    #language=form.cleaned_data['language'],
                                    #words_translated=0)
            #translator.save()
            #return HttpResponseRedirect('/profile/')
        #else:
            #return render_to_response('register.html', {'form': form},
                                      #context_instance=RequestContext(request))
    #else:
        #''' User is not submitting the form, show the blank form '''
        #form = RegistrationForm()
        #context = {'form': form}
        #return render_to_response('register.html', context,
                                  #context_instance=RequestContext(request))


def LoginRequest(request):
    if request.user.is_authenticated():
        try:
            translator = request.user.get_profile()
            return HttpResponseRedirect('/i18n/profile/')
        except Translator.DoesNotExist:
            return render_to_response('no_translator_profile.html',
                                      context_instance=RequestContext(request))
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            translator = authenticate(username=username, password=password)
            if translator is not None:
                login(request, translator)
                return HttpResponseRedirect('/i18n/profile/')
            else:
                return render_to_response('login.html', {'form': form},
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('login.html', {'form': form},
                                      context_instance=RequestContext(request))
    else:
        ''' User is not submitting the form, show the login form '''
        form = LoginForm()
        context = {'form': form, 'user': request.user}
        return render_to_response('login.html', context,
                                  context_instance=RequestContext(request))


def LogoutRequest(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def ProfileHandler(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/i18n/login/')
    translator = request.user.get_profile
    context = {'translator': translator}
    return render_to_response('profile.html', context,
                              context_instance=RequestContext(request))


@login_required
def ModifyStringsHandler(request):
    try:
        translator = request.user.get_profile()
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html',
                                  context_instance=RequestContext(request))

    TranslatedFormSet = modelformset_factory(String, form=ModifyForm, extra=0)
    if request.method == 'POST':
        formset = TranslatedFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
        return HttpResponseRedirect('/i18n/modify/')
    else:
        query = String.objects.filter(translator=translator, frozen=False)
        paginator = Paginator(query, 15)  # Show 15 strings per page
        page = request.GET.get('page')
        try:
            strings = paginator.page(page)
        except PageNotAnInteger:
            strings = paginator.page(1)
        except EmptyPage:
            strings = paginator.page(paginator.num_pages)
        page_query = String.objects.filter(id__in=[string.id for string in strings])
        formset = TranslatedFormSet(queryset=page_query)
        context = {'strings': strings, 'formset': formset}
        return render_to_response('modify.html', context,
                                  context_instance=RequestContext(request))


@login_required
def TranslationHandler(request):
    try:
        translator = request.user.get_profile()
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html',
                                  context_instance=RequestContext(request))
    # This query retrieves string in English that either have a translation
    # that is outdated or have no translation (in the translator's language)
    query = String.objects.filter((Q(string__language=translator.language,
                                  string__last_modif__lt=F('last_modif')) |
                                  ~Q(string__language=translator.language)),
                                  enabled=True, translatable=True)
    ToTranslateFormSet = modelformset_factory(String, form=TranslateForm, extra=0)
    if request.method == 'POST':
        words_count = 0
        formset = ToTranslateFormSet(request.POST, request.FILES)
        for form in formset:
            if form.instance in query and form.is_valid() and form.cleaned_data['translation']:
                translation = form.cleaned_data['translation']
                string, created = String.objects.get_or_create(
                                              language=translator.language,
                                              original_string=form.instance
                                              )
                if created:
                    string.text = translation
                    string.translator = translator
                    string.save()
                else:
                    String.objects.filter(id=string.id).update(
                                              text=translation,
                                              translator=translator,
                                              last_modif=datetime.now())
                words_count += len(form.instance.text.split())
        translator.words_translated += words_count
        translator.save()
        return HttpResponseRedirect('/i18n/translate/')

    else:
        paginator = Paginator(query, 15)  # Show 15 strings per page
        page = request.GET.get('page')
        try:
            strings = paginator.page(page)
        except PageNotAnInteger:
            strings = paginator.page(1)
        except EmptyPage:
            strings = paginator.page(paginator.num_pages)
        page_query = String.objects.filter(id__in=[string.id for string in strings])
        formset = ToTranslateFormSet(queryset=page_query)
        context = {'strings': strings, 'formset': formset}
        return render_to_response('translate.html', context,
                                  context_instance=RequestContext(request))


@staff_member_required
def GenerateHandler(request):
    if request.method == 'POST':
        form = GenerateForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language']
            app = form.cleaned_data['app']
            platform = app.platform.replace(' ', '').lower()
            if platform == 'android':
                return generate.Android().download_files(language, app)
            elif platform == 'windowsphone' or platform == 'windows8':
                return generate.WindowsPhone().download_files(language, app)
            elif platform == 'ios' or platform == 'osx':
                return generate.iOS().download_files(language, app)
            elif platform == 'web':
                return generate.Web().download_files(language, app)
        else:
            return render_to_response('generate.html', {'form': form},
                                      context_instance=RequestContext(request))
    else:
        form = GenerateForm()
        context = {'form': form}
        return render_to_response('generate.html', context,
                                  context_instance=RequestContext(request))


def GuidelineHandler(request):
    return render_to_response('guideline.html', context_instance=RequestContext(request))
