# -*- encoding: utf8 -*-
import os
import os.path

import appdirs

from utils import mkdir_p

NOME_APLICACAO = "vestat"
AUTOR = "Lucas Teixeira"
VERSAO = "1.2.1"

dirs = appdirs.AppDirs(NOME_APLICACAO, AUTOR)

BASE_DIR = os.path.join(os.getcwd())
DATA_DIR = dirs.user_data_dir
LOGS_DIR = dirs.user_log_dir

for d in [DATA_DIR, LOGS_DIR]:
    if not os.path.exists(d):
        print("Diretório {d} não existe; criando...".format(**vars()))
        mkdir_p(d)

BANCO_DE_DADOS = os.path.join(DATA_DIR, NOME_APLICACAO + '.sqlite')

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (("Lucas", "lucas@lucasteixeira.com"))
MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': BANCO_DE_DADOS,                      # Or path to database file if using sqlite3.
    }
}

# ID da configuração na tabela do modelo config.models.VestatConfiguration
ID_CONFIG = 1

# Informações pro AutologinMiddleware
AUTOLOGIN_USERNAME = "vestat"
AUTOLOGIN_PASSWORD = "a vespa e o gestalt"

ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d \n\n%(message)s\n\n#################\n'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },

    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'formatter':'verbose',
            'filename': os.path.join(LOGS_DIR, NOME_APLICACAO + '.log'),
            'maxBytes': 1048576,
            'backupCount': 3,

        }
    },
    'loggers': {
        'django': {
            'handlers':['console', 'file'],
            'propagate': True,
            'level':'INFO',
        },

        NOME_APLICACAO: {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        }
    }
}

DATE_FORMAT = "j \de F \de Y"
DATE_INPUT_FORMATS = ("%d/%m/%Y",)

DATETIME_FORMAT = "j \de F \de Y, H:i"

SHORT_DATE_FORMAT = "d/m/Y"

# Formato de data igual ao SHORT_DATE_FORMAT, mas no formato do
# `strftime`.
#
# Usado pra formatar objetos `datetime.date`.
SHORT_DATE_FORMAT_PYTHON = "%d/%m/%Y"

SHORT_DATETIME_FORMAT = "d/m/Y H:i"

DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3

TIME_ZONE = 'America/Sao_Paulo'
LANGUAGE_CODE = 'pt-br'
PYTHON_LOCALE = "pt_BR"
SITE_ID = 1

SITE_URL = "http://localhost:8000/"

USE_I18N = True
USE_L10N = True

MEDIA_URL = '/m/'

ADMIN_MEDIA_PREFIX =  '/static/admin/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

SECRET_KEY = 'e*fg6gmbnx_+4*ftc&biozg+7+zkshn97yyltu9z7)j(gn$=cs'
TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'vestat.middleware.AutocreateDatabaseMiddleware',
    'vestat.middleware.AutocreateConfigMiddleware',
    'vestat.middleware.ExceptionLoggerMiddleware',
    'vestat.middleware.AutologinMiddleware',
    'vestat.caixa.middleware.AutocreateRegistroMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "vestat.context_processors.project_settings",
    "vestat.context_processors.data_hora",
)

ROOT_URLCONF = 'vestat.urls'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates")
)
INSTALLED_APPS = (
    'vestat.config',
    'vestat.calendario',
    'vestat.feriados',
    'vestat.caixa',
    'vestat.relatorios',
    'vestat.contabil',
    'django_evolution',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.auth',
    'django.contrib.staticfiles',
)
