from .base import *

DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-$nm6iy@q2hs1h9884y#sbjr6x*^@ys)*0gi4o*at$+8^4pwc6c')

ALLOWED_HOSTS = ['.zizhizhan.com', 'pkm.cluster.local']

CSRF_TRUSTED_ORIGINS = ['https://*.zizhizhan.com', 'https://*.zizhizhan.com:8443', 'https://127.0.0.1:8000']
