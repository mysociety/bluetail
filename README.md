# Bluetail BODS project

https://en.wikipedia.org/wiki/Himalayan_bluetail - first described in 1845.

Create conf/config.py from conf/config.py-example

Copying an existing project and vagrant so for the moment:
Python 3.5
Django 2.2.8

Django project is configured to talk to the local postgres database. 

Get working server with:

```vagrant up
vagrant ssh
script/server
```

http://127.0.0.1:8000/test