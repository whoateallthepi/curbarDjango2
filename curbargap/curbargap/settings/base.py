"""
Django settings for curbargap project.

Generated by 'django-admin startproject' using Django 3.0.10.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__,os.pardir))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Now set in local.py or pro.py
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DEFAULT_AUTO_FIELD='django.db.models.AutoField' 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weather.apps.WeatherConfig',
    'blog.apps.BlogConfig',
    'forecast.apps.ForecastConfig',
    'chart.apps.ChartConfig',
    'warning.apps.WarningConfig',
    'django_filters',
    'django_tables2',
    'easy_thumbnails',
    'django.contrib.gis',
    'leaflet',
    'djgeojson'
,]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'curbargap.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': [os.path.join(BASE_DIR, 'weather/templates/weather')],  # to load 404.html etc
        'DIRS': [os.path.join(BASE_DIR, 'curbargap/templates')],  # to load base.html, navbar.html, 404.html etc
                                                                  # from project
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'curbargap.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'weather',
#        'USER': 'weather',
#        'PASSWORD': 'wh1tebear',
#    }
#}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')

THUMBNAIL_ALIASES = {
    '': {
        'blog_thumbnail': {'size': (100, 100), 'crop': True},
        'blog_standard': {'size': (200,0), 'crop': False},
        'blog_sidebar' : {'size' : (150,0), 'crop': False },
        
    },
}
# The following are for the Met Office Datahub API calls
DATAHUB_URL = "api-metoffice.apiconnect.ibmcloud.com"
DATAPOINT_URL = "datapoint.metoffice.gov.uk"
CHARTS_URL = "/public/data/image/wxfcs/surfacepressure/json/capabilities?key={datapoint_key}"
SATELLITES_URL = "/public/data/layer/wxobs/all/json/capabilities?key={datapoint_key}"

# the following are for Met Office NSWWS API calls (weather warnings)
NSWWS_BASE_URL = 'prd.nswws.api.metoffice.gov.uk'
NSWWS_FEEDS_URL = '/v1.0/objects/feed'
   
LATITUDE = 53.27041002136657
LONGITUDE = -1.6239021210600733

DEFAULT_STATION = 5 
DEFAULT_FORECAST_STATION = 351418

# Dates
SHORT_DATE_FORMAT = "d/m/Y"
USE_L10 = False
