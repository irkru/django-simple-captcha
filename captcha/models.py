from captcha.conf import settings as captcha_settings
from django.db import models
from django.conf import settings
import datetime
import random
import time
import unicodedata
from django.http import Http404

import redis

# Heavily based on session key generation in Django
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_RANDOM_KEY = 18446744073709551616L     # 2 << 63


try:
    from hashlib import sha1 as sha_digest
except ImportError:
    import sha as sha_digest # sha for Python 2.4 (deprecated in Python 2.6)


def get_safe_now():
    try:
        from django.utils.timezone import utc
        if settings.USE_TZ:
            return datetime.datetime.utcnow().replace(tzinfo=utc)
    except:
        pass
    return datetime.datetime.now()

def create(challenge, response, hashkey=None):
    response = response.lower()

    expiration = int(captcha_settings.CAPTCHA['TIMEOUT'])*60

    if not hashkey:
        key_ = unicodedata.normalize('NFKD', str(randrange(0, MAX_RANDOM_KEY)) + str(time.time()) + unicode(challenge)).encode('ascii', 'ignore') + unicodedata.normalize('NFKD', unicode(response)).encode('ascii', 'ignore')

        hashkey = sha_digest(key_).hexdigest()

    client = redis.StrictRedis(host=captcha_settings.CAPTCHA['REDIS']['HOST'], port=captcha_settings.CAPTCHA['REDIS']['PORT'],
        db=captcha_settings.CAPTCHA['REDIS']['DB'])

    client.setex('%s.%s' % (captcha_settings.CAPTCHA['REDIS']['PREFIX'], hashkey), expiration, '\x00'.join([challenge, response]))

    return hashkey


def get(hashkey):
    client = redis.StrictRedis(host=captcha_settings.CAPTCHA['REDIS']['HOST'], port=captcha_settings.CAPTCHA['REDIS']['PORT'],
        db=captcha_settings.CAPTCHA['REDIS']['DB'])

    store = client.get('%s.%s' % (captcha_settings.CAPTCHA['REDIS']['PREFIX'], hashkey))
    if not store:
        raise Http404()

    return store

def delete(response, hashkey):
    client = redis.StrictRedis(host=captcha_settings.CAPTCHA['REDIS']['HOST'], port=captcha_settings.CAPTCHA['REDIS']['PORT'],
        db=captcha_settings.CAPTCHA['REDIS']['DB'])

    key = '%s.%s' % (captcha_settings.CAPTCHA['REDIS']['PREFIX'], hashkey)
    store = client.get(key)
    if not store:
        raise ValueError()

    challenge, stored_response = store.split('\x00')
    if response != stored_response:
        raise ValueError()

    client.delete(key)
