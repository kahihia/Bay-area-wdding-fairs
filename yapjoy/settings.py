# Django settings for yapjoy project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'app39782801@heroku.com'
EMAIL_HOST_PASSWORD = '7tahzw8m0499'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
LOGIN_URL = '/login/'
ADMINS = (
    ('Adeel K', 'adeelpkpk@gmail.com'),
)
import os
import pusher

pusher.app_id = '267806'
pusher.key = '235681c2c1c1ae380308'
pusher.secret = '3db12c2387c3be546481'

MANAGERS = ADMINS
DEFAULT_FROM_EMAIL = 'support@yapjoy.com'
DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'yapjoy',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'postgres',
        'PASSWORD': 'asd',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
        # 'CONN_MAX_AGE': 60,
    },
    #
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'dbi2kdfu97vnne',                      # Or path to database file if using sqlite3.
    #     # The following settings are not used with sqlite3:
    #     'USER': 'ue89o346vmgrnj',
    #     'PASSWORD': 'pe4josv6oq78uibqbd4vpjvatf6',
    #     'HOST': 'ec2-52-207-133-11.compute-1.amazonaws.com',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    #     'PORT': '5432',                      # Set to empty string for default.
    #     'CONN_MAX_AGE': 60,
    # }
    # PGPASSWORD='?!yapjoy!!11*?' pg_dump -Fc --no-acl --no-owner -h yapjoy.cytgypehlwaw.us-west-2.rds.amazonaws.com -U yapjoy yapjoy > amazonYapjoy.dump
    # heroku pg:backups restore 'https://s3-us-west-2.amazonaws.com/yapjoy-static/static/storage/db/amazonYapjoy.dump' DATABASE --app yapjoy
    # PGPASSWORD=?!yapjoy!!11*? pg_dump -Fc --no-acl --no-owner -h 127.0.0.1 -U yapjoy yapjoy > mydb.dump
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    # # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'yapjoy',  # Or path to database file if using sqlite3.
    #     # The following settings are not used with sqlite3:
    #     'USER': 'yapjoy',
    #     'PASSWORD': '?!yapjoy!!11*?',
    #     'HOST': 'yapjoy.cytgypehlwaw.us-west-2.rds.amazonaws.com',
    # # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    #     'PORT': '5432',  # Set to empty string for default.
    #     'CONN_MAX_AGE': 60,
    # }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'yapjoy',                      # Or path to database file if using sqlite3.
    #     # The following settings are not used with sqlite3:
    #     'USER': 'postgres',
    #     'PASSWORD': 'asd',
    #     'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    #     'PORT': '5432',                      # Set to empty string for default.
    # }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'dbf9p7mq7lsq80',                      # Or path to database file if using sqlite3.
    #     # The following settings are not used with sqlite3:
    #     'USER': 'qolxdvgffhlidb',
    #     'PASSWORD': 'gF6hNkmeUwrfOf5JqwcTLio9d-',
    #     'HOST': 'ec2-50-16-229-91.compute-1.amazonaws.com',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    #     'PORT': '5432',                      # Set to empty string for default.
    # }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['www.yapjoy.com','yapjoy.herokuapp.com','https://s3-us-west-2.amazonaws.com','.facebook.com','http://yui.yahooapis.com']
SITE_NAME = 'https://www.yapjoy.com/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__)) + '/..'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = ""
if not DEBUG:
    STATIC_ROOT = os.path.join('static')
# STATIC_URL = 'https://s3-us-west-2.amazonaws.com/yapjoy-static/static/'

#----------- aws settings ---------------
DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
DEFAULT_S3_PATH = "media"
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
STATIC_S3_PATH = "static"
AWS_ACCESS_KEY_ID = 'AKIAIXFGL3W7R47QWV2A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'yapjoy-static'
AWS_PRELOAD_METADATA = True
MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
MEDIA_URL = 'https://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
STATIC_ROOT = "/%s/" % STATIC_S3_PATH
STATIC_URL = '/static/'#''https://%s.s3.amazonaws.com/static/' % AWS_STORAGE_BUCKET_NAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
#----------- aws settings ---------------
# heroku config:set AWS_ACCESS_KEY_ID="AKIAIXFGL3W7R47QWV2A" AWS_SECRET_ACCESS_KEY="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" --app yapjoy
STATICFILES_DIRS = (
    os.path.join('static'),
#     os.path.join(PROJECT_ROOT, 'static'),
)
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '3ceop(ll0_-)a@sf&vj+#5ppkef!7^^l%du@2fpv5r53&=wt!6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    # 'django.contrib.comments',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    # 'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth', #this is required for admin
    'django.core.context_processors.csrf', #necessary for csrf protection
    'django.core.context_processors.static',
    # 'django.contrib.messages.context_processors.messages',
    # 'social.apps.django_app.context_processors.backends',
    # 'social.apps.django_app.context_processors.login_redirect',
    # 'django.core.context_processors.auth',
    # 'django.core.context_processors.debug',

)
SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email',
    'user_friends',
    'publish_actions',
    'manage_notifications',
    'user_posts',
    'read_mailbox ',
    'manage_pages',
    'read_stream ',
    'publish_pages',
    'rest_framework',
    # 'friends_location',
    # 'status_update',
    # 'read_stream',
    # 'offline_access',
]
INTERNAL_IPS = ('127.0.0.1',)
MIDDLEWARE_CLASSES = (

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'sslify.middleware.SSLifyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'pagination.middleware.PaginationMiddleware',
    # 'django.middleware.gzip.GZipMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

)
REST_SESSION_LOGIN = False
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts

# Static asset configuration

secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https'
}


SOCIAL_AUTH_LOGIN_ERROR_URL = '/'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
        'https://s3-us-west-2.amazonaws.com',
        'http://s3-us-west-2.amazonaws.com',
    )
S3DIRECT_REGION = 'us-east-1'
CORS_ALLOW_METHODS = (
        'GET',
        # 'POST',
        # 'PUT',
        # 'PATCH',
        # 'DELETE',
        # 'OPTIONS'
    )


ROOT_URLCONF = 'yapjoy.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'yapjoy.wsgi.application'



TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates').replace('\\','/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.comments',
    'django.contrib.humanize',
    'django.contrib.admin',
    # 'rest_framework',
    # # 'rest_framework.authtoken',
    # 'rest_auth.registration',
    # 'rest_framework_swagger',
    # 'rest_auth',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # 'sslify',
    'django_comments',
    'yapjoy_api',
    'yapjoy_feed',
    'yapjoy_messages',
    'yapjoy_registration',
    'yapjoy_tasks',
    'yapjoy_accounts',
    'yapjoy_video',
    's3_folder_storage',
    'corsheaders',
    #'yapjoy_forum',
    'yapjoy_events',
    'yapjoy_market',
    'jqchat',
    'yapjoy_forum',
    'django_markdown',
    'fullcalendar',
    # 'social.apps.django_app.default',
    'django_contact_importer',
    'django_wysiwyg',
    'tinymce',
    'ckeditor',
    'pagination',
    'django_instagram',
    'yapjoy_files',
    'yapjoy_shortlist',
    'yapjoy_vendors',
    'yapjoy_teamschat',
    's3direct',
    # 'ckeditor_uploader',
    # 'friendship',

    'bayareaweddingfairs_tickets',
    # 'debug_toolbar',
    # 'cas_consumer',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth.registration',
    'rest_framework_swagger',
    'rest_auth',
    'location_field.apps.DefaultConfig',

)
# DEBUG_TOOLBAR_PATCH_SETTINGS = False
DJANGO_WYSIWYG_FLAVOR = "ckeditor"
# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    }
}
# CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'Custom',
#         'toolbar_Custom': [
#             ['Bold', 'Italic', 'Underline'],
#             ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
#             ['Link', 'Unlink'],
#             ['RemoveFormat', 'Source']
#         ]
#     }
# }

SOCIAL_AUTH_FACEBOOK_KEY='778671392242244'
SOCIAL_AUTH_FACEBOOK_SECRET='571c5632e92b3b1a5ae02ea9dce89e78'

GOOGLE_CLIENT_ID = '920774801939-jjh416fdsoopdtgqm0dgkdnu6ndjrc1d.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'p2qnu-mym1h0-fOvbmvXl4FB'

LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookAppOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
    'yapjoy_registration.backends.CaseInsensitiveModelBackend.CaseInsensitiveModelBackend',
)

FACEBOOK_EXTENDED_PERMISSIONS = ['email']
# FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'ru_RU'}
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'locale': 'ru_RU',
  'fields': 'id, name, email, age_range'
}

S3DIRECT_DESTINATIONS = {
    # Allow anybody to upload any MIME type
    'misc': ('uploads/misc',),

    # Allow staff users to upload any MIME type
    'files': ('uploads/files', lambda u: u.is_staff,),

    # Allow anybody to upload jpeg's and png's.
    'imgs': ('media/images', lambda u: True, ['image/jpeg', 'image/png'],),

    # Allow authenticated users to upload mp4's
    'vids': ('media/videos', lambda u: u.is_authenticated(), ['video/mp4'],),

    # Allow anybody to upload any MIME type with a custom name function, eg:
    'custom_filename': (lambda original_filename: 'images/unique.jpg',),

    # Specify a non-default bucket for PDFs
    'pdfs': ('/', lambda u: True, ['application/pdf'], None, 'pdf-bucket',),

    # Allow logged in users to upload any type of file and give it a private acl:
    'private': (
        'uploads/vids',
        lambda u: u.is_authenticated(),
        '*',
        'private'),

    # Allow authenticated users to upload with cache-control for a month and content-disposition set to attachment
    'cached': (
        'uploads/vids',
        lambda u: u.is_authenticated(),
        '*',
        'public-read',
        # AWS_STORAGE_BUCKET_NAME,
        'max-age=2592000',
        'attachment')
}

# SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
AUTH_PROFILE_MODULE = 'yapjoy_registration.UserProfile'

STRIPE_SECRET_KEY = 'sk_test_D8XQLQXVdpI2X03rn0Ycp5Y0'
STRIPE_PUBLISHABLE_KEY = 'pk_test_06mlzXo9xTcZCRy0XTkwYONA'

STRIPE_SECRET_KEY_BAWF = 'sk_test_z3b8Yfc0Mcuh0P3M7VDfGZkt'
STRIPE_PUBLISHABLE_KEY_BAWF = 'pk_test_ic11SWVPcUHwZ1mDBEBTdSX1'
# STRIPE_SECRET_KEY_BAWF = 'sk_live_n8WrsUoKt0Esb2cfUAIBHWgn'
# STRIPE_PUBLISHABLE_KEY_BAWF = 'pk_live_fqbN9t5DE4vEfGqQEFzTDpZS'

YAHOO_CLIENT_ID = "dj0yJmk9VG90Tm9GTk16clhXJmQ9WVdrOWVWZEVXbWxsTldNbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD05MA--"
YAHOO_CLIENT_SECRET = "e2d3e379c96c8a4e4e34fdcbfb3ef5ee473865bd"

LIVE_CLIENT_ID = "0000000040168962"
LIVE_CLIENT_SECRET = "aS9Zv0EjCUwiEslFPpUovNHXQj89bsLQ"

MERCHANT_SETTINGS = {
     "stripe": {
        "API_KEY": "sk_live_5tw0mrFpx8g33UKhPQZuaKvc",
        "PUBLISHABLE_KEY": "pk_live_Hxwa4UrkwLn3bhUqx6sjbQTF",
    }
}

# DEFAULT_AUTHENTICATION_CLASSES = (
#     # 'rest_framework.authentication.SessionAuthentication',
#     'rest_framework.authentication.BasicAuthentication'
# ),

DEFAULT_AUTHENTICATION_CLASSES = (
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )

}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGINATE_BY': 10
}

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social.pipeline.social_auth.associate_by_email',

    'social.pipeline.user.create_user',

    # 'galt.socialpipeline.update_member_profile',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    'yapjoy_registration.socialpipeline.update_member_profile',
)

def get_cache():
  import os
  try:
    os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS'].replace(',', ';')
    os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
    os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'TIMEOUT': 500,
        'BINARY': True,
        'OPTIONS': { 'tcp_nodelay': True }
      }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

CACHES = get_cache()

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SSLIFY_DISABLE_FOR_REQUEST = [
    lambda request: request.get_full_path().startswith('/crm')
]

# tokbox settings

TOKBOX_KEY = '45284952'
TOKBOX_SECRET = 'b00fa2eb9bf9bd29b7f82e098bee1009f019bc75'
