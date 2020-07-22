"""
For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket
import sys

import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
SITE_ROOT = '/'

DEBUG = True

if DEBUG:
    IS_LIVE = False
    STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'
else:
    IS_LIVE = True
    STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

if os.path.exists(os.path.join(BASE_DIR, "conf", "config.py")):
    from conf.config import *  # stores database and key outside repo
else:
    from conf.config_defaults import *

ALLOWED_HOSTS = [
    "127.0.0.1",
    "0.0.0.0",
    "localhost",
    "testserver",
]

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

# Define some custom locations at which the staticfiles app can find our
# files, which it will collect in the directory defined by `STATIC_ROOT`.
# django-pipeline will then compile them from there (if required).
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, "web"),
    os.path.join(PROJECT_PATH, "bluetail", "web"),
    (
        "bootstrap",
        os.path.join(PROJECT_PATH, "vendor", "bootstrap", "scss"),
    ),
    (
        "html5shiv",
        os.path.join(PROJECT_PATH, "vendor", "html5shiv"),
    ),
    (
        "jquery",
        os.path.join(PROJECT_PATH, "vendor", "jquery"),
    ),
    (
        "bootstrap",
        os.path.join(PROJECT_PATH, "vendor", "bootstrap", "dist", "js"),
    )
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

    # "cove",
    "cove.input",
    # "cove_ocds",

    'bluetail',
    'django_pgviews',
]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': dj_database_url.config(env="DATABASE_URL", default=DATABASE_URL)
}

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

# Set variable to "TRUE" to enable
STORE_OCDS_IN_S3 = os.getenv('STORE_OCDS_IN_S3') == 'TRUE'
if STORE_OCDS_IN_S3:
    S3_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'spendnetwork-silvereye')
    AWS_LOCATION = 'media'
    AWS_DEFAULT_ACL = None

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
                'sass/main.scss',
            ),
            'output_filename': 'css/main.css',
        },
    },

    'CSS_COMPRESSOR': 'django_pipeline_csscompressor.CssCompressor',
    'DISABLE_WRAPPER': True,
    'COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
    ),
    'SHOW_ERRORS_INLINE': False,
    # Use the libsass commandline tool (that's bundled with libsass) as our
    # sass compiler, so there's no need to install anything else.
    'SASS_BINARY': SASSC_LOCATION,
}
