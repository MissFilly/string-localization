from app.models import App, String
from django.db.models import Count

web = App.objects.get(name__contains="SuperPhoto", platform="Web")
spa = App.objects.get(name="SuperPhoto", platform="Android")
spfa = App.objects.get(name="SuperPhoto Full", platform="Android")
spios = App.objects.get(name="SuperPhoto", platform="iOS")


def addios(text, key):
    string = String.objects.get(text=text)
    if not string.ios_name_string:
        String.objects.filter(text=text, ios_name_string=key)
    elif key in string.ios_name_string:
        pass
    else:
        actual = string.ios_name_string
        added = actual + "," + key
        String.objects.filter(text=text).update(ios_name_string=added)
        print "Replaced %s for %s" % (actual, added)


def gtext(text):
    return String.objects.get(text=text)


def ftext(text):
    return String.objects.filter(text=text)


def removedup():
    objects = String.objects.values('text').annotate(count=Count('text')).filter(count__gt=1, description='Effect name',
                                                                                 android_name_string=None, wp_name_string=None,
                                                                                 ios_name_string=None, osx_name_string=None,
                                                                                 w8_name_string=None)
    for obj in objects:
        for i in range(obj['count']-1, 0, -1):
            String.objects.get(description='Effect name', android_name_string=None,
                               text=obj['text'],
                               wp_name_string=None, ios_name_string=None, osx_name_string=None,
                               w8_name_string=None)[i].delete()
        print("Deleted %s %s from %s" % (obj['count']-1, obj['text'], obj['count']))
