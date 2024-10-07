"""
Django settings for CoreMysteryBox project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
# Imports.
from pathlib import Path
import os, sys, base64
from dotenv import load_dotenv

# Load the .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False #True #False #True #False

ALLOWED_HOSTS = ['.vercel.app', '.now.sh', '127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'TokenMysteryBox',
    'SolanaMysteryBox',
    'NFTMysteryBox',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CoreMysteryBox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CoreMysteryBox.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'verceldb',
        'USER': 'default',
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    },
}
# I use local database for testing, because the free hosted 
# database doesn't meet Django test requirements(test_verceldb deleting etc.)!
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'Test',
            'USER': 'postgres',
            'PASSWORD': os.getenv('TEST_DATABASE_PASSWORD'),
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

MEDIA_URL = 'img/'
MEDIA_ROOT = BASE_DIR/'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SOLANA SETTINGS
"""
# For mainnet:
SOLANA_API_URL = "https://api.mainnet-beta.solana.com"
TokenMint = ''
TokenMB_Privatekey = base64.b64decode(os.getenv('mainnet_tokenMB_privatekey_base64'))
SolanaMB_Privatekey = base64.b64decode(os.getenv('mainnet_solanaMB_privatekey_base64'))
NFTMB_Privatekey = base64.b64decode(os.getenv('mainnet_NFTMB_privatekey_base64'))
"""
# For devnet:
SOLANA_API_URL = "https://rpc.ankr.com/solana_devnet" # "https://api.devnet.solana.com" 
TokenMint = '6rUfdRzZv56wvE57M8QDadBQR7ozrSVhy1yWVueTHm7D'
TokenMB_Privatekey = base64.b64decode(os.getenv('devnet_tokenMB_privatekey_base64'))
SolanaMB_Privatekey = base64.b64decode(os.getenv('devnet_solanaMB_privatekey_base64'))
NFTMB_Privatekey = base64.b64decode(os.getenv('devnet_NFTMB_privatekey_base64'))

# If I run tests, then I use devnet settings
if 'test' in sys.argv:
    SOLANA_API_URL = "https://rpc.ankr.com/solana_devnet" # "https://api.devnet.solana.com" 
    TokenMint = '6rUfdRzZv56wvE57M8QDadBQR7ozrSVhy1yWVueTHm7D'
    TokenMB_Privatekey = base64.b64decode(os.getenv('devnet_tokenMB_privatekey_base64'))
    SolanaMB_Privatekey = base64.b64decode(os.getenv('devnet_solanaMB_privatekey_base64'))
    NFTMB_Privatekey = base64.b64decode(os.getenv('devnet_NFTMB_privatekey_base64'))
