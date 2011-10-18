# -*- encoding: utf8 -*-
NOME_APLICACAO = "vestat"
VERSAO = "1.0rc10"

### NÃO ALTERE NADA DAQUI PRA FRENTE SE NÃO SOUBER O QUE ESTÁ FAZENDO ###

import os
import os.path

BASE_DIR = os.path.join(os.getcwd())
BANCO_DE_DADOS = os.path.join(BASE_DIR, NOME_APLICACAO + '.sqlite')

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': BANCO_DE_DADOS,                      # Or path to database file if using sqlite3.
    }
}

DATE_FORMAT = "j \de F \de Y"
DATE_INPUT_FORMATS = "%d/%m/%Y",

DATETIME_FORMAT = "j \de F \de Y, H:i"

SHORT_DATE_FORMAT = "d/m/Y"
SHORT_DATETIME_FORMAT = "d/m/Y H:i"

DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3

TIME_ZONE = 'America/Sao_Paulo'
LANGUAGE_CODE = 'pt-br'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_URL = 'http://localhost:8000/m/'
MEDIA_PREFIX = '/m/'
SECRET_KEY = 'e*fg6gmbnx_+4*ftc&biozg+7+zkshn97yyltu9z7)j(gn$=cs'
TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'vestat.middleware.AutocreateDatabaseMiddleware',
)
ROOT_URLCONF = 'vestat.urls'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates")
)
INSTALLED_APPS = (
    'django.contrib.sessions',
    'vestat.caixa',
    'vestat.relatorios',
    'django_evolution',
)
