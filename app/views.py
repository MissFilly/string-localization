# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.forms import RegistrationForm, LoginForm, GenerateForm
from app.models import Translator, String
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from localization.utils import extra_funcs, generate

CURRENT_VALUES = {}


def MainPageHandler(request):
    user = request.user
    return render_to_response('index.html', {'user': user},
                              context_instance=RequestContext(request))


def TranslatorRegistration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                                       username=form.cleaned_data['username'],
                                       email=form.cleaned_data['email'],
                                       password=form.cleaned_data['password']
                                       )
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            translator = Translator(user=user,
                                    language=form.cleaned_data['language'],
                                    words_translated=0)
            translator.save()
            return HttpResponseRedirect('/profile/')
        else:
            return render_to_response('register.html', {'form': form},
                                      context_instance=RequestContext(request))
    else:
        ''' User is not submitting the form, show the blank form '''
        form = RegistrationForm()
        context = {'form': form}
        return render_to_response('register.html', context,
                                  context_instance=RequestContext(request))


def LoginRequest(request):
    if request.user.is_authenticated():
        try:
            translator = request.user.get_profile()
            return HttpResponseRedirect('/profile/')
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
                return HttpResponseRedirect('/profile/')
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
        return HttpResponseRedirect('/login/')
    translator = request.user.get_profile
    context = {'translator': translator}
    return render_to_response('profile.html', context,
                              context_instance=RequestContext(request))


@login_required
def TranslationHandler(request):
    try:
        translator = request.user.get_profile()
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html',
                           context_instance=RequestContext(request))
    strings_list = extra_funcs.strings_to_translate(request)
    if request.method == 'POST':
        keys = request.POST.keys()
        keys.remove('csrfmiddlewaretoken')
        words_count = 0

        for key in keys:
            if request.POST.get(key):  # Translation field in form is not empty
                original = String.objects.get(id=int(key))
                # The string already has a translation, it must be updated
                try:
                    string = String.objects.get(language=translator.language,
                                                original_string=original)
                    if string in strings_list:
                        string.text = request.POST.get(key)
                        string.last_modif = datetime.now()
                        string.translator = request.user.get_profile()
                        string.save()
                    else:
                        # The user is trying to submit again translation that
                        # have already been made
                        return HttpResponse('Not allowed!')

                # The translated string must be created
                except String.DoesNotExist:
                    print(original)
                    string = String(language=translator.language,
                                    translator=request.user.get_profile(),
                                    text=request.POST.get(key),
                                    original_string=original)
                    string.save()
                words_count += len(original.text.split())
        translator.words_translated += words_count
        translator.save()
        return HttpResponseRedirect('/i18n/translate/')

    else:
        paginator = Paginator(strings_list, 2)  # Show 15 strings per page
        page = request.GET.get('page')
        try:
            strings = paginator.page(page)
        except PageNotAnInteger:
            strings = paginator.page(1)
        except EmptyPage:
            strings = paginator.page(paginator.num_pages)

        context = {'strings': strings}
        return render_to_response('translate.html', context,
                                  context_instance=RequestContext(request))


@login_required
def ModifyStringsHandler(request):
    try:
        translator = request.user.get_profile()
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html',
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        keys = request.POST.keys()
        keys.remove('csrfmiddlewaretoken')
        global CURRENT_VALUES
        for key in keys:
            if request.POST.get(key) and request.POST.get(key) != \
               CURRENT_VALUES[int(key)]:
                try:
                    String.objects.filter(
                        translator=translator,
                        id=int(key),
                        frozen=False
                        ).update(
                        text=request.POST.get(key)
                        )
                except String.DoesNotExist:
                    return HttpResponse('There was an error!')
            else:
                print("Not replaced: " + key)
        CURRENT_VALUES = {}
        return HttpResponseRedirect('/i18n/modify/')
    else:
        strings_list = String.objects.filter(translator=translator,
                                             frozen=False)
        paginator = Paginator(strings_list, 2)  # Show 15 strings per page
        page = request.GET.get('page')
        try:
            strings = paginator.page(page)
        except PageNotAnInteger:
            strings = paginator.page(1)
        except EmptyPage:
            strings = paginator.page(paginator.num_pages)
        global CURRENT_VALUES
        CURRENT_VALUES = extra_funcs.save_current_values(strings_list)
        context = {'strings': strings}
        return render_to_response('modify.html', context,
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
            elif platform == 'ios':
                return generate.iOS().download_files(language, app)
        else:
            return render_to_response('login.html', {'form': form},
                                      context_instance=RequestContext(request))
    else:
        form = GenerateForm()
        context = {'form': form}
        return render_to_response('generate.html', context,
                                      context_instance=RequestContext(request))
