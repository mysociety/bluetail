"""
For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEBUG = True

if DEBUG:
    IS_LIVE = False
    STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'
else:
    IS_LIVE = True
    STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

from conf.config import *  # stores database and key outside repo

ALLOWED_HOSTS = ["127.0.0.1", "testserver"]

LANGUAGE_CODE = 'en-uk'

PROJECT_PATH = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            PROJECT_PATH + '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'proj.universal.universal_context',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MEDIA_ROOT = PROJECT_PATH + "/media/"

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, "web"),
    os.path.join(PROJECT_PATH, "theme"),
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'pipeline',
    'bluetail',
]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': REPOSITORY_DB_NAME,
        'USER': REPOSITORY_DB_USER,
        'PASSWORD': REPOSITORY_DB_PASS,
        'HOST': REPOSITORY_DB_HOST,
        'PORT': REPOSITORY_DB_PORT,
    }
}

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

ROOT_URLCONF = 'proj.urls'

WSGI_APPLICATION = 'proj.wsgi.application'

HTML_MINIFY = not DEBUG

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = "/media/"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

PIPELINE = {
    'STYLESHEETS': {
        'main': {
            'source_filenames': (
                'sass/global.scss',
            ),
            'output_filename': 'css/main.css',
        },
    },

    'CSS_COMPRESSOR': 'django_pipeline_csscompressor.CssCompressor',
    'DISABLE_WRAPPER': True,
    'COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
    ),
    'SHOW_ERRORS_INLINE':False,
    # Use the libsass commandline tool (that's bundled with libsass) as our
    # sass compiler, so there's no need to install anything else.
    'SASS_BINARY': SASSC_LOCATION
}
