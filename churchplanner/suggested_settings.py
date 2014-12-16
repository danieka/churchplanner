"""
Django settings for churchplanner project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#Uncomment if you have celery installed
#from celery.schedules import crontab
#import djcelery
#djcelery.setup_loader()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates/'),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'planner',
    'allaccess',
    'crispy_forms',
    "jquery_fields",
    'south', 
    #'djcelery', Uncomment if you have celery
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'planner.middleware.SecurityMiddleware',
)

ROOT_URLCONF = 'churchplanner.urls'

WSGI_APPLICATION = 'churchplanner.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
TIME_ZONE="Europe/Stockholm"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static/'),
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
    'planner.context_processor.event_processor',
)

AUTHENTICATION_BACKENDS = (
    'planner.backend.HashModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allaccess.backends.AuthorizedServiceBackend',
    
)

CRISPY_TEMPLATE_PACK = "uni_form"

LOGIN_REDIRECT_URL="/"
LOGIN_URL="/login"

SITE_ROOT = "localhost:8000"
EMAIL_HOST = "localhost"
EMAIL_PORT = "1025"

SENDER = "admin@example.com"

#Uncomment this whole section if you have celery installed.
# The backend used to store task results - because we're going to be 
# using RabbitMQ as a broker, this sends results back as AMQP messages
#CELERY_RESULT_BACKEND = "amqp"
#CELERY_IMPORTS = ("planner.tasks", )
#CELERY_ALWAYS_EAGER = True

#BROKER_HOST = "localhost"
#BROKER_PORT = 5672
#BROKER_PASSWORD = ""
#BROKER_USER = ""
#BROKER_VHOST = "o"
#BROKER_URL = ""

# The default Django db scheduler
#CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
#CELERYBEAT_SCHEDULE = {
#    "publish": {
#        "task": "planner.tasks.publish_task",
#        "schedule": crontab(hour=12, minute=30),
#        "args": (),
#    },
#    "send_email": {
#        "task": "planner.tasks.send_email_task",
#        "schedule": crontab(hour=12, minute=30),
#        "args": (),
#    },

SEND_REMINDER_EMAIL = False
SEND_PARTICIPATION_EMAIL = False

PUBLISH_TO_FACEBOOK = False
FACEBOOK_APP_ID = ""
FACEBOOK_APP_SECRET =""
FACEBOOB_PAGE_ID = ""   #This is the ID of the page that the events should be published to.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mysite.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'INFO',
        },
        'churchplanner': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
