import os

from django.conf import settings


CAPTCHA = {
    'FONT_PATH': os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Vera.ttf')),
    'FONT_SIZE': 22,
    'LETTER_ROTATION': (-35, 35),
    'BACKGROUND_COLOR': '#ffffff',
    'FOREGROUND_COLOR': '#001100',
    'CHALLENGE_FUNCT': 'captcha.helpers.random_char_challenge',
    'NOISE_FUNCTIONS': ('captcha.helpers.noise_arcs', 'captcha.helpers.noise_dots',),
    'FILTER_FUNCTIONS': ('captcha.helpers.post_smooth',),
    'WORDS_DICTIONARY': '/usr/share/dict/words',
    'PUNCTUATION': '''_"',.;:-''',
    'FLITE_PATH': None,
    'TIMEOUT': 5,  # Minutes
    'LENGTH': 4,  # Chars
    'IMAGE_BEFORE_FIELD': True,
    'DICTIONARY_MIN_LENGTH': 0,
    'DICTIONARY_MAX_LENGTH': 99,
    'CAPTCHA_TEST_MODE': getattr(settings, 'CAPTCHA_TEST_MODE', getattr(settings, 'CATPCHA_TEST_MODE', False)),
    'REDIS': {  # Settings for redis database
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PREFIX': 'captcha',
    }
}

captcha_settings = getattr(settings, 'CAPTCHA', {})

if CAPTCHA['IMAGE_BEFORE_FIELD']:
    CAPTCHA['OUTPUT_FORMAT'] = captcha_settings.get('OUTPUT_FORMAT', u'%(image)s %(hidden_field)s %(text_field)s')
else:
    CAPTCHA['OUTPUT_FORMAT'] = captcha_settings.get('OUTPUT_FORMAT', u'%(hidden_field)s %(text_field)s %(image)s')

CAPTCHA.update(captcha_settings)

del captcha_settings

# Failsafe
if CAPTCHA['DICTIONARY_MIN_LENGTH'] > CAPTCHA['DICTIONARY_MAX_LENGTH']:
    CAPTCHA['DICTIONARY_MIN_LENGTH'], CAPTCHA['DICTIONARY_MAX_LENGTH'] = CAPTCHA['DICTIONARY_MAX_LENGTH'], CAPTCHA['DICTIONARY_MIN_LENGTH']


def _callable_from_string(string_or_callable):
    if callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(__import__('.'.join(string_or_callable.split('.')[:-1]), {}, {}, ['']), string_or_callable.split('.')[-1])


def get_challenge():
    return _callable_from_string(CAPTCHA['CHALLENGE_FUNCT'])


def noise_functions():
    if CAPTCHA['NOISE_FUNCTIONS']:
        return map(_callable_from_string, CAPTCHA['NOISE_FUNCTIONS'])
    return []


def filter_functions():
    if CAPTCHA['FILTER_FUNCTIONS']:
        return map(_callable_from_string, CAPTCHA['FILTER_FUNCTIONS'])
    return []
