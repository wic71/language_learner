import re

import nltk
from nltk.tokenize import sent_tokenize

# Ladda punktdata (om inte redan laddad)
nltk.download('punkt', quiet=True)

# Språk-mapping från ISO till NLTK språk
ISO_TO_NLTK_LANG = {
    "en": "english",
    "sv": "swedish",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    # OBS: lv, et, lt, fi stöds inte direkt → fallback
}


def split_into_sentences(text, iso_code="en"):
    """
    Dela upp en text i meningar baserat på ISO språk-kod.
    Faller tillbaka till 'english' om språket saknas.
    """
    language = ISO_TO_NLTK_LANG.get(iso_code, "english")
    return sent_tokenize(text, language=language)


def generate_sentences_for_module(module):
    """
    Skapar eller ersätter alla meningar för en Module baserat på dess text.
    """
    from core.models import Sentence  # för att undvika cirkulär import

    # Radera gamla meningar
    module.sentences.all().delete()

    # Splitta texten till meningar
    sentences = split_into_sentences(module.text, module.course.language)

    # Skapa nya meningar
    for order, sentence_text in enumerate(sentences, start=1):
        Sentence.objects.create(module=module, order=order, original_text=sentence_text)


def extract_unique_words(text):
    """Extraherar unika ord från en text"""
    words = re.findall(r'\b\w+\b', text.lower())  # Matcha ord
    unique_words = sorted(set(words))  # Unika och sorterade
    return unique_words
