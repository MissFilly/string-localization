## String localization manager

This is a Django 1.6 application that aims to simplify the management and
localization of strings in mobile and web applications.

This application allows those who have a single mobile app that runs in
different platforms (Android, iOS, Windows Phone, etc.) to keep all strings
in a single place in order to unify them (to avoid sending to translators
two or more strings that have the exact same meaning but use different
sentences).

It also provides an online editor for translators, so there is no need to
send them new files every time texts are added, deleted or modified.
Translators save their translations in the database directly.

## Installation

### Set a Python3.3 virtualenv


```
$ virtualenv -p /usr/bin/python3 stringmanagerenv
$ cd stringmanagerenv/
$ source bin/activate
```

Download the application:


```
$ git clone https://github.com/MissFilly/string-localization.git
```

Sync the database (repository includes fixtures)


```
$ cd string-localization
$ python manage.py syncdb
```
