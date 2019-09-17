
DEBUG = True


INSTALLED_APPS = [
    'influxdb_metrics',
    'rest_framework',
    'rest_framework_json_api',
]


SECRET_KEY = 'abcdef123456'


MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
