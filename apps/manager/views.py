from datetime import datetime
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory
from django.db.models import Q, F
from django.contrib.auth import authenticate, login, logout, get_user_model
from apps.manager.forms import LoginForm, GenerateForm, EditionForm, TranslateForm  # , RegistrationForm
from apps.manager.models import Translator, String
from apps.manager import generator


# Index
def MainPageHandler(request):
    return render_to_response('index.html', {'request' : request}, context_instance=RequestContext(request))


#def TranslatorRegistration(request):
    #if request.user.is_authenticated():
        #try:
            #translator = request.user.get_profile()
            #return HttpResponseRedirect('/profile/')
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
    # Check if logged user is a translator
    if request.user.is_authenticated():
        try:
            translator = request.user.get_profile()
            return HttpResponseRedirect('/profile/')
        except Translator.DoesNotExist:
            return render_to_response('no_translator_profile.html', { 'request' : request },
                                     context_instance=RequestContext(request))
    # Form is being submitted
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            translator = authenticate(username=username, password=password)
            # User that just logged in is a translator
            if translator is not None:
                login(request, translator)
                return HttpResponseRedirect('/profile/')
            else:
                return render_to_response('login.html', {'form': form, 'request' : request},
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('login.html', {'form': form, 'request' : request},
                                      context_instance=RequestContext(request))
    # Form must be displayed
    else:        
        form = LoginForm()
        context = {'form': form, 'request' : request }
        return render_to_response('login.html', context,
                                  context_instance=RequestContext(request))


def LogoutRequest(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def ProfileHandler(request):
    try:
        translator = Translator.objects.get(user=request.user)
        context = {'request' : request, 'translator': translator}
        return render_to_response('profile.html', context,
                              context_instance=RequestContext(request))
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html', {'request' : request},
                                  context_instance=RequestContext(request))


@login_required
def StringsEditionHandler(request):
    try:
        translator = Translator.objects.get(user=request.user)
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html', {'request' : request},
                                  context_instance=RequestContext(request))

    TranslatedFormSet = modelformset_factory(String, form=EditionForm, extra=0)
    if request.method == 'POST':
        formset = TranslatedFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
        page = request.GET.get('page')
        if page is not None:
            next_page = str(int(page) + 1)
        else:
            next_page = '2'
        return HttpResponseRedirect('/edit/?page=' + next_page)
    else:
        query = String.objects.filter(translator=translator, frozen=False,
                                      original_string__last_modif__lt=F('last_modif'))
        paginator = Paginator(query, 5)  # Show 5 strings per page
        page = request.GET.get('page')
        try:
            strings = paginator.page(page)
        except PageNotAnInteger:
            strings = paginator.page(1)
        except EmptyPage:
            strings = paginator.page(paginator.num_pages)
        page_query = String.objects.filter(id__in=[string.id for string in strings])
        formset = TranslatedFormSet(queryset=page_query)
        context = {'strings': strings, 'formset': formset, 'request' : request}
        return render_to_response('edit.html', context,
                                  context_instance=RequestContext(request))


@login_required
def TranslationHandler(request):
    try:
        translator = Translator.objects.get(user=request.user)
    except Translator.DoesNotExist:
        return render_to_response('no_translator_profile.html', {'request':request},
                                  context_instance=RequestContext(request))
    # This query retrieves string in English that either have a translation
    # that is outdated or have no translation (in the translator's language)
    query = String.objects.filter((Q(string__language=translator.language,
                                  string__last_modif__lt=F('last_modif')) |
                                  ~Q(string__language=translator.language)),
                                  enabled=True, translatable=True,
                                  language__name='English').distinct()
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
        page = request.GET.get('page')
        if page is not None:
            next_page = str(int(page) + 1)
        else:
            next_page = u'2'
        return HttpResponseRedirect('/translate/?page=' + next_page)

    else:
        paginator = Paginator(query, 5)  # Show 5 strings per page
        page = request.GET.get('page')
        try:
            strings = paginator.page(page)
        except PageNotAnInteger:
            strings = paginator.page(1)
        except EmptyPage:
            strings = paginator.page(paginator.num_pages)
        page_query = String.objects.filter(id__in=[string.id for string in strings])
        formset = ToTranslateFormSet(queryset=page_query)
        words_remaining = 0
        # Count of total words to be translated
        for string in query:
            words_remaining += len(string.text.split())
        context = {'strings': strings, 'formset': formset,
                   'words_remaining': words_remaining,
                   'words_translated': translator.words_translated,
                   'sentences_remaining': len(query),
                   'sentences_translated': len(String.objects.filter(translator=translator, frozen=False,
                                                                     original_string__last_modif__lt=F('last_modif'))),
                   'request' : request
                  }
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
                return generator.generate.Android().download_files(language, app)
            elif platform == 'windowsphone' or platform == 'windows8':
                return generator.generate.WindowsPhone().download_files(language, app)
            elif platform == 'ios' or platform == 'osx':
                return generator.generate.iOS().download_files(language, app)
            elif platform == 'web':
                return generator.generate.Web().download_files(language, app)
        else:
            return render_to_response('generate.html', {'form': form},
                                      context_instance=RequestContext(request))
    else:
        form = GenerateForm()
        context = {'form': form}
        return render_to_response('generate.html', context,
                                  context_instance=RequestContext(request))


def GuidelinesHandler(request):
    return render_to_response('guidelines.html', {'request' : request}, context_instance=RequestContext(request))
