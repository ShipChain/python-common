import os
import base64

import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key


ENVIRONMENT = 'TEST'


DEBUG = True

DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_enumobject',
        'TEST_NAME': 'test_enumobject'
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'influxdb_metrics',
    'rest_framework',
    'rest_framework_json_api',

    'tests'
]


INFLUXDB_DISABLED = True


REQUESTS_SESSION = requests.session()


SECRET_KEY = 'abcdef123456'


MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


MILLISECONDS_THRESHOLD = 500


OIDC_PUBLIC_KEY_PEM_BASE64 = os.environ.get('OIDC_PUBLIC_KEY_PEM_BASE64', 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0NCk1JR2ZN\
QTBHQ1NxR1NJYjNEUUVCQVFVQUE0R05BRENCaVFLQmdRQ2FmTDBXVVRObFdteTJJdlRPQ2xpNHdqZFMNClk1cWJNaXNQcHlrNVFkamRNMEFuY2gvbm5qTGJ\
aVzAwakw0V0lXM0YzOHZjNThQSzExNzB3OG9maGF1TEJSMEgNCjBsRTZoTTlsV2l3TjZOODFNVWZ5cG1HME9ReG1vYW5XN2Y1ano2Z2tCRkNzc21pQWZxSF\
Z1TTJtSmlJdGJZTVUNCm8vcmtxcm9zQnVadmFKSnJEUUlEQVFBQg0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t')


SIMPLE_JWT = {
    'VERIFYING_KEY': load_pem_public_key(
        data=base64.b64decode(OIDC_PUBLIC_KEY_PEM_BASE64.strip()), backend=default_backend()),
    'ALGORITHM': 'RS256',
    'AUTH_HEADER_TYPES': ('JWT',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.UntypedToken',),
    'USER_ID_CLAIM': 'sub',
    'PRIVATE_KEY': rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend()),
}


SIMPLE_JWT['VERIFYING_KEY'] = SIMPLE_JWT['PRIVATE_KEY'].public_key()
