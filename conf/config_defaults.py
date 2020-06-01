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


# URL format provider://username:password@host:port/databasename

DATABASE_URL = os.getenv("DATABASE_URL", 'postgres://bluetail:bluetail@localhost:5432/bluetail')

# This must be set in `config.py` or the environment variable.
SECRET_KEY = os.getenv('SECRET_KEY')
