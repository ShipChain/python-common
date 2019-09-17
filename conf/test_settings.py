
DEBUG = True


INSTALLED_APPS = [
    'rest_framework',
]


SECRET_KEY = 'abcdef123456'


MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
