from app.models import String


def strings_to_translate(request):

    ''' This function returns the list of strings that need to be translated '''
    translator = request.user.get_profile()
    translatable_strings = String.objects.filter(translatable=True,
                                                 language__name="English",
                                                 enabled=True)
    translated_strings = String.objects.filter(language=translator.language,
                                               original_string__enabled=True)
    strings = []  # List of strings that need to be translated

    # Strings that are translatable and don't have a translation for the
    # translator's language
    for string in translatable_strings:
        if not String.objects.filter(language=translator.language,
                                     original_string=string).exists():
            strings.append(string)

    # Translated strings that are out of date
    for string in translated_strings:
        if string.last_modif < string.original_string.last_modif:
            strings.append(string.original_string)
    return strings


def save_current_values(string_list):
    strings_dic = {}
    for string in string_list:
        strings_dic[string.id] = string.text
    return strings_dic