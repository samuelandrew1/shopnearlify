import os
from pathlib import Path
import environ
from dotenv import load_dotenv
import dj_database_url

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


ALLOWED_HOSTS = ["aajomos.com", "127.0.0.1", "localhost",'qvzpc9-8000.csb.app']


DEBUG = os.environ.get("DEBUG")

SECRET_KEY = os.environ.get("SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "phonenumber_field",
    "jazzmin",
    "django.contrib.admin",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "delivery",
    "gunicorn",
    "corsheaders",
    "PIL",
    "widget_tweaks",
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap4",
    "django_countries",
    "paystack",
    "dotenv",
    "paystackapi",
    "store",
    "star_ratings",
    "django.contrib.humanize",
    "requests",
    "xhtml2pdf",
    "environ",
    "paystack_api",
    "dj_database_url",
    # 'jet_django',
    "settings",
    # 'django_inline_actions'
    "rangefilter",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    "store.middleware.ignore_static_files.IgnoreStaticFilesMiddleware",
]
ROOT_URLCONF = "shopnearlify.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "settings.context_processors.site_settings",
                "store.context_processors.app_list",
            ],
        },
    },
]

WSGI_APPLICATION = "shopnearlify.wsgi.application"


print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"))

# https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    DATABASES = {
        "default": dj_database_url.config(
            # Replace this value with your local database's connection string.
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
        )
    }


else:
    DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
                }
            }


SECRET_KEY = os.environ.get("SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.environ.get(
    "PAYSTACK_PUBLIC_KEY",
)
PAYSTACK_SECRET_KEY = os.environ.get(
    "PAYSTACK_SECRET_KEY",
)

DEBUG_PROPAGATE_EXCEPTIONS = os.environ.get("DEBUG_PROPAGATE_EXCEPTIONS", default=False)
EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
)
EMAIL_PORT = 465
# EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
# Default email address to use for various automated correspondence
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = os.environ.get("EMAIL_HOST_USER")
ACCOUNT_EMAIL_REQUIRED = True


REDACTED = os.environ.get(
    "REDACTED",
)
ADMIN_EMAIL = os.environ.get(
    "ADMIN_EMAIL",
)


AWS_ACCESS_KEY_ID = os.environ.get(
    "AWS_ACCESS_KEY_ID",
)
AWS_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY",
)
AWS_STORAGE_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_BUCKET_NAME",
)
AWS_S3_SIGNATURE_NAME = os.environ.get(
    "AWS_S3_SIGNATURE_NAME",
)
AWS_CLOUDFRONT_KEY_ID = os.environ.get("AWS_CLOUDFRONT_KEY_ID")
aws_cloudfront_key = os.environ.get("AWS_CLOUDFRONT_KEY", "")
AWS_CLOUDFRONT_KEY = aws_cloudfront_key.replace("\\n", "\n").encode("ascii").strip()
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}}
}


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_AUTHENTICATION_METHOD = "username_email"


JAZZMIN_SETTINGS = {
    "site_title": "A.A Jomos Ng ltd",
    "site_header": "A.A Jomos Ng ltd",
    "show_ui_builder": True,
    "site_logo": "assets/images/sitelogo.jpg",
    "site_brand": "A.A JOMOS",
    "login_logo": "assets/images/sitelogo.jpg",
    "welcome_sign": "admin login",
    "usermenu_links": [
        {"model": "auth.user"},
    ],
    "custom_links": {
        "book_store": [  # Use any existing app or a dedicated app name here
            {
                "name": "Homepage",
                "url": "index",  # The name of the URL pattern for your homepage
                "icon": "fas fa-home",  # FontAwesome icon class
                "permissions": [
                    "auth.view_user"
                ],  # Optional: restrict access based on permissions
            },
        ],
    },
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # external url that opens in a new window (Permissions can be added)
        # {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},
        # App with dropdown menu to all its models pages (Permissions checked against models)
        {
            "app": "book_store",
        },
        {
            "app": "delivery",
        },
        {
            "app": "paystack_api",
        },
    ],
}


JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
}
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
USE_L10N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = "/media/"


STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]


# Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)

# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = "storages.backends.s3.S3Storage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Application definition
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = (
    "/profile/"  # Example redirect for authenticated users
)
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = (
    "/login/"  # Example redirect for anonymous users
)

ACCOUNT_AUTHENTICATION_METHOD = "email"
LOGIN_REDIRECT_URL = "store:index"
LOGOUT_REDIRECT_URL = "store:index"
SIGNUP_REDIRECT_URL = "store:index"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Auto-login after email confirmation
# ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1  # Example: 1 day until the confirmation link expires


LOGIN_REDIRECT_URL = "/"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False


CRISPY_TEMPLATE_PACK = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 1,
}


SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# DEBUG_PROPAGATE_EXCEPTIONS = os.environ.get('DEBUG_PROPAGATE_EXCEPTIONS', default=False)

# Custom settings
STAR_RATINGS_STAR_HEIGHT = 20
STAR_RATINGS_STAR_WIDTH = 20
STAR_RATINGS_RERATE = False
SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}}
}

CART_SESSION_ID = "cart"

INTERNAL_IPS = [
    "127.0.0.1",
]

ACCOUNT_FORMS = {
    "add_email": "allauth.account.forms.AddEmailForm",
    "change_password": "allauth.account.forms.ChangePasswordForm",
    "login": "allauth.account.forms.LoginForm",
    "reset_password": "allauth.account.forms.ResetPasswordForm",
    "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
    "set_password": "allauth.account.forms.SetPasswordForm",
    "signup": "allauth.account.forms.SignupForm",
    "user_token": "allauth.account.forms.UserTokenForm",
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME':  'concxyea_aajoms_store_database',
#         'HOST': 'localhost',
#         'USER': 'concxyea_aajomos_admin_root_user',
#         'PASSWORD': 'hKA%hrcTF7o#',
#         'PORT': '3306',
#     }
# }
