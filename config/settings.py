"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

from dotenv import load_dotenv

REQUEST_HEADER = "header"
REQUEST_BODY = "body"
REQUEST_QUERY = "query"
REQUEST_PATH = "path"

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5=9qd#p44rv-o@r=1ktt@gz(4sb@u5!gt6*58ths@*==y78wzh'

JWT_SECRET = os.getenv("JWT_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        # AccessToken 을 header 에 넣어서 보내야 한다.
        'AccessToken': {
            'type': 'apiKey',
            'name': 'AccessToken',
            'description': '입력형 : `jwt <AccessToken>`',
            'in': 'header'
        },

        # RefreshToken 을 header 에 넣어서 보내야 한다.
        'RefreshToken': {
            'type': 'apiKey',
            'name': 'RefreshToken',
            'description': '입력형 : `jwt <RefreshToken>`',
            'in': 'header'
        },

    },

    # PERSIST_AUTH 를 True 로 설정하면, Swagger 페이지에서 로그인을 한 번 하면, 그 이후에는 로그인을 하지 않아도 된다.
    'PERSIST_AUTH': True,
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "users.apps.UsersConfig",
    "diary.apps.DiaryConfig",
    "diag.apps.DiagConfig",
    # Django 의 RestAPI 를 쉽게 만들어주는 라이브러리
    "rest_framework",
    # Django 의 Swagger 를 쉽게 만들어주는 라이브러리
    "drf_yasg",
    # Cors 에러 처리
    'corsheaders',
    # S3 관련
    'storages',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

##CORS
CORS_ORIGIN_ALLOW_ALL = True  # <- 모든 호스트 허용
CORS_ALLOW_CREDENTIALS = True  # <-쿠키가 cross-site HTTP 요청에 포함될 수 있다

CORS_ALLOW_METHODS = (  # <-실제 요청에 허용되는 HTTP 동사 리스트
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

CORS_ALLOW_HEADERS = (  # <-실제 요청을 할 때 사용될 수 있는 non-standard HTTP 헤더 목록// 현재 기본값
    '*',
)

APPEND_SLASH = False  # <- / 관련 에러 제거

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': os.getenv("MYSQL_DATABASE"),  # Your database name
        'USER': os.getenv("MYSQL_USER"),  # Default MySQL root user, or use a different user if you've created one
        'PASSWORD': os.getenv("MYSQL_PASSWORD"),  # The root password you set when running the MySQL container
        'HOST': os.getenv("MYSQL_HOST"),  # Use the IP address of the MySQL container
        'PORT': '3306',  # Default MySQL port
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

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
