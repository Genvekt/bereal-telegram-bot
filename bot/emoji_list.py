import random

from emoji import get_emoji_unicode_dict
emojis = list(get_emoji_unicode_dict('en').values())

def get_random_emoji():
    return random.choice(emojis)