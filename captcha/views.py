from captcha.conf import settings
from captcha.helpers import captcha_image_url
from captcha.models import get, create
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import random
import re
import tempfile
import os
import subprocess

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import Image
    import ImageDraw
    import ImageFont

import redis
try:
    import json
except ImportError:
    from django.utils import simplejson as json

NON_DIGITS_RX = re.compile('[^\d]')
# Distance of the drawn text from the top of the captcha image
from_top = 4


def getsize(font, text):
    if hasattr(font, 'getoffset'):
        return [x + y for x, y in zip(font.getsize(text), font.getoffset(text))]
    else:
        return font.getsize(text)


def captcha_image(request, key, scale=1):
    store = get(key)

    challenge, response = store.split('\x00')

    if settings.CAPTCHA['FONT_PATH'].lower().strip().endswith('ttf'):
        font = ImageFont.truetype(settings.CAPTCHA['FONT_PATH'], settings.CAPTCHA['FONT_SIZE'] * scale)
    else:
        font = ImageFont.load(settings.CAPTCHA['FONT_PATH'])

    size = getsize(font, challenge)
    size = (size[0] * 2, int(size[1] * 1.4))
    image = Image.new('RGB', size, settings.CAPTCHA['BACKGROUND_COLOR'])

    try:
        PIL_VERSION = int(NON_DIGITS_RX.sub('', Image.VERSION))
    except:
        PIL_VERSION = 116
    xpos = 2

    charlist = []
    for char in challenge:
        if char in settings.CAPTCHA['PUNCTUATION'] and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)
    for char in charlist:
        fgimage = Image.new('RGB', size, settings.CAPTCHA['FOREGROUND_COLOR'])
        charimage = Image.new('L', getsize(font, ' %s ' % char), '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')
        if settings.CAPTCHA['LETTER_ROTATION']:
            if PIL_VERSION >= 116:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA['LETTER_ROTATION']), expand=0, resample=Image.BICUBIC)
            else:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA['LETTER_ROTATION']), resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', size)

        maskimage.paste(charimage, (xpos, from_top, xpos + charimage.size[0], from_top + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in settings.noise_functions():
        draw = f(draw, image)
    for f in settings.filter_functions():
        image = f(image)

    out = StringIO()
    image.save(out, "PNG")
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    response.write(out.read())
    response['Content-length'] = out.tell()

    return response


def captcha_audio(request, key):
    if not settings.CAPTCHA['FLITE_PATH']:
        raise Http404()

    store = get(key)

    challenge, response = store.split('\x00')

    if 'captcha.helpers.math_challenge' == settings.CAPTCHA['CHALLENGE_FUNCT']:
        challenge = challenge.replace('*', 'times').replace('-', 'minus')
    else:
        challenge = ', '.join(list(challenge))
    path = str(os.path.join(tempfile.gettempdir(), '%s.wav' % key))
    cline = '%s -t "%s" -o "%s"' % (settings.CAPTCHA['FLITE_PATH'], challenge, path)
    os.popen(cline).read()

    if os.path.isfile(path):
        response = HttpResponse()
        f = open(path, 'rb')
        response['Content-Type'] = 'audio/x-wav'
        response.write(f.read())
        f.close()
        os.unlink(path)

        return response


def captcha_refresh(request):
    """  Return json with new captcha for ajax refresh request """
    if not request.is_ajax():
        raise Http404

    challenge, response = settings.get_challenge()()

    new_key = create(challenge, response)
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
    }
    return HttpResponse(json.dumps(to_json_response), content_type='application/json')