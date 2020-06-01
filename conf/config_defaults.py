import os
SITE_SLUG = "bluetail"
CORE_APP_NAME = "bluetail"
SITE_NAME = 'bluetail'
LIVE_ROOT = ''
SHARE_IMAGE = ''
TWITTER_SHARE_IMAGE = ''
SITE_DESCRIPTION = ''
SITE_TWITTER = ''
GOOGLE_ANALYTICS_ACCOUNT = ''
SASSC_LOCATION  = 'sassc'

REPOSITORY_DB_HOST = 'localhost'
REPOSITORY_DB_PORT = '5432'
REPOSITORY_DB_USER = 'bluetail'
REPOSITORY_DB_NAME = 'bluetail'
REPOSITORY_DB_PASS = 'bluetail'

DATABASE_URL = 'postgres://bluetail:bluetail@localhost:5432/bluetail'

# This must be set in `config.py` or the environment variable.
SECRET_KEY = os.getenv('SECRET_KEY')
