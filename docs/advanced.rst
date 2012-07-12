Advanced topics
===============

Configuration toggles
+++++++++++++++++++++

The following configuration elements can be defined (in your ``settings.py``)

CAPTCHA['FONT_PATH']
-----------------

Full path and filename of a TrueType (TTF), OpenType, or pilfont font file used to render text.

Defaults to: ``fonts/Vera.ttf`` (included in the application, GPL font).

Note that your PIL installation must support TTF and/or OpenFont if you want to use these kind of glyphs (most modern distributions of PIL do.)

CAPTCHA['FONT_SIZE']
-----------------

Font-size in pixels of the rendered text.

Defaults to '22'.

CAPTCHA['LETTER_ROTATION']
-----------------------

A random rotation in this interval is applied to each letter in the challenge text.

Defaults to ``(-35,35)``.

New in version 0.1.6: set this to None to disable letter roation.

CAPTCHA['BACKGROUND_COLOR']
------------------------

Background-color of the captcha. Can be expressed as html-style #rrggbb, rgb(red, green, blue), or common html names (e.g. "red").

Defaults to: ``'#ffffff'``

CAPTCHA['FOREGROUND_COLOR']
------------------------

Foreground-color of the captcha.

Defaults to ``'#001100'``

CAPTCHA['CHALLENGE_FUNCT']
------------------------

String representing a python callable (i.e. a function) to use as challenge generator.

See Generators below for a list of available generators and a guide on how to write your own.

Defaults to: ``'captcha.helpers.random_char_challenge'``

CAPTCHA['NOISE_FUNCTIONS']
------------------------

List of strings of python callables that take a PIL ``DrawImage`` object and an ``Image`` image as input, modify the ``DrawImage``, then return it.

Defaults to: ``('captcha.helpers.noise_arcs','captcha.helpers.noise_dots',)``


CAPTCHA['FILTER_FUNCTIONS']
------------------------

List of strings of python callables that take a PIL ``Image`` object as input, modify it and return it.

These are called right before the rendering, i.e. after the noise functions.

Defaults to: ``('captcha.helpers.post_smooth',)``


CAPTCHA['WORDS_DICTIONARY']
------------------------

Required for the ``word_challenge`` challenge function only. Points a file containing a list of words, one per line.

Defaults to: ``'/usr/share/dict/words'``

CAPTCHA['FLITE_PATH']
------------------------

Full path to the ``flite`` executable. When defined, will automatically add audio output to the captcha.

Defaults to: ``None`` (no audio output)

CAPTCHA['TIMEOUT']
-----------------------
Integer. Lifespan, in minutes, of the generated captcha.

Defaults to: 5

CAPTCHA['LENGTH']
------------------------

Sets the length, in chars, of the generated captcha. (for the ``'captcha.helpers.random_char_challenge'`` challenge)

Defaults to: 4

CAPTCHA['DICTIONARY_MIN_LENGTH']
-----------------------------

When using the word_challenge challenge function, controls the minimum length of the words to be randomly picked from the dictionary file.

Defaults to: 0

CAPTCHA['DICTIONARY_MAX_LENGTH']
-----------------------------

When using the word_challenge challenge function, controls the maximal length of the words to be randomly picked from the dictionary file.

Defaults to: 99

Note: it's perfectly safe to specify e.g. ``CAPTCHA['DICTIONARY_MIN_LENGTH'] = CAPTCHA['DICTIONARY_MAX_LENGTH'] = 6`` but it's considered an error to define ``CAPTCHA['DICTIONARY_MAX_LENGTH']`` to be smaller than ``CAPTCHA['DICTIONARY_MIN_LENGTH']``.

CAPTCHA['OUTPUT_FORMAT']
------------------------

New in version 0.1.6

Specify your own output format for the generated markup, when e.g. you want to position the captcha image relative to the text field in your form.

Defaults to: ``u'%(image)s %(hidden_field)s %(text_field)s'``

Note: the three keys have to be present in the format string or an error will be thrown at runtime.


CAPTCHA['REDIS']
-----------------

Settings for Redis database connection ::

    REDIS': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PREFIX': 'captcha',
    }


Generators and modifiers
++++++++++++++++++++++++

Random chars
------------

.. image:: http://django-simple-captcha.googlecode.com/files/Random%20chars.png

Classic captcha that picks four random chars. This is case insensitive. ::

    CAPTCHA['CHALLENGE_FUNCT'] = 'captcha.helpers.random_char_challenge'


Simple Math
------------

.. image:: http://django-simple-captcha.googlecode.com/files/Math.png

Another classic, that challenges the user to resolve a simple math challenge by randomly picking two numbers between one and nine, and a random operator among plus, minus, times. ::

    CAPTCHA['CHALLENGE_FUNCT'] = 'captcha.helpers.math_challenge'


Dictionary Word
----------------

.. image:: http://django-simple-captcha.googlecode.com/files/Dictionary.png

Picks a random word from a dictionary file. Note, you must define ``CAPTCHA['WORDS_DICTIONARY']`` in your cofiguration to use this generator. ::

    CAPTCHA['_CHALLENGE_FUNCT'] = 'captcha.helpers.word_challenge'


Roll your own
-------------

To have your own challenge generator, simply point ``CAPTCHA['CHALLENGE_FUNCT']`` to a function that returns a tuple of strings: the first one (the challenge) will be rendered in the captcha, the second is the valid response to the challenge, e.g. ``('5+10=', '15')``, ``('AAAA', 'aaaa')``

This sample generator that returns six random digits::

    import random

    def random_digit_challenge():    
        ret = u''
        for i in range(6):
            ret += str(random.randint(0,9))
        return ret, ret

