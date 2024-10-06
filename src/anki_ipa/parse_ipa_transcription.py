# -*- coding: utf-8 -*-

"""
This file is part of the Anki IPA add-on for Anki.
Parsing methods
Copyright: (c) 2019 m-rtin <https://github.com/m-rtin>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import urllib
import bs4
import re
import requests
from typing import List, Callable

# Create a dictionary for all transcription methods
transcription_methods = {}
transcription = lambda f: transcription_methods.setdefault(f.__name__, f)


@transcription
def british(word: str, strip_syllable_separator: bool=True) -> list:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://en.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        p = re.compile("{{a\|UK}} {{IPA\|en\|([^}]+)}}")
        m = p.search(wikitext)
        if m is None:
            p = re.compile("{{a\|RP}} {{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{IPA\|en\|([^}]+)\|([^}]+)}}")
            m = p.search(wikitext)
            
        ipa = m.group(1)
        return [remove_special_chars(word=ipa, strip_syllable_separator=strip_syllable_separator)]
    except (KeyError, AttributeError):
        return []

@transcription
def american(word: str, strip_syllable_separator: bool=True) -> list:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://en.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        p = re.compile("{{a\|US}} {{IPA\|en\|([^}]+)}}")
        m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{a\|GA}}.*?{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None: 
            p = re.compile("{{a\|GenAm}}.*?{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None:
            p = re.compile("{{IPA\|en\|([^}]+)}}")
            m = p.search(wikitext)
        if m is None:
            p = re.compile("{{IPA\|en\|([^}]+)\|([^}]+)}}")
            m = p.search(wikitext)

        ipa = m.group(1)
        return [remove_special_chars(word=ipa, strip_syllable_separator=strip_syllable_separator)]
    except (KeyError, AttributeError):
        return []

@transcription
def french(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://fr.wiktionary.org/wiki/{word}"
    return parse_website(link, {'title': 'Prononciation API'}, strip_syllable_separator,
                         filter_cb = fr_filter)

def fr_filter(tag: bs4.Tag) -> bool:
    # avoid using non-french transcriptions
    sectionlangue = tag.find_previous('span', {'class': 'sectionlangue'})
    if sectionlangue and sectionlangue['id'] and sectionlangue['id'] != 'fr':
        return False
    # avoid adding results from flextable as it may contain transcriptions for other forms
    if tag.find_parent('table', {'class': 'flextable'}):
        return False
    return True

@transcription
def russian(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://ru.wiktionary.org/wiki/{word}"
    return parse_website(link, {'class': 'IPA'}, strip_syllable_separator)

@transcription
def spanish(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://es.wiktionary.org/wiki/{word}"
    return parse_website(link, {'class': 'ipa'}, strip_syllable_separator)

@transcription
def german(word: str, strip_syllable_separator: bool=True) -> list:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://de.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        p = re.compile("{{IPA}}.*?{{Lautschrift\|([^}]+)")
        m = p.search(wikitext)
        ipa = m.group(1)
        return [ipa]
    except (KeyError, AttributeError):
        return []

@transcription
def polish(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://pl.wiktionary.org/wiki/{word}"
    return parse_website(
        link, {'title': 'To jest wymowa w zapisie IPA; zobacz hasło IPA w Wikipedii'}, strip_syllable_separator)


@transcription
def dutch(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://nl.wiktionary.org/wiki/{word}"
    return parse_website(link, {"class": "IPAtekst"}, strip_syllable_separator)


def parse_website(link: str, css_code: dict, strip_syllable_separator: bool=True,
                  filter_cb: Callable[[bs4.Tag],bool] = None) -> List[str]:
    soup = get_html_content(link)
    if not soup:
        return []
    results = soup.find_all('span', css_code)

    if filter_cb:
        results = filter(filter_cb, results);

    transcriptions = map(lambda result: remove_special_chars(result.getText(), strip_syllable_separator), results)

    _transcriptions = remove_duplicates(transcriptions)
    return _transcriptions

def get_html_content(link: str) -> bs4.BeautifulSoup:
    try:
        website = requests.get(link)
    except requests.exceptions.RequestException as e:
        return None
    return bs4.BeautifulSoup(website.text, "html.parser")


### Removes duplicates from the list without reordering it
def remove_duplicates(seq: list) -> list:
    seen = set()
    rv = list()
    for el in seq:
        if el not in seen:
            rv.append(el)
            seen.add(el)
    return rv

def remove_special_chars(word: str, strip_syllable_separator: bool) -> str:
    word = word.replace("/", "").replace("]", "").replace("[", "").replace("\\", "")
    if strip_syllable_separator:
        word = word.replace(".", "")
    return word

def transcript(words: List[str], language: str, strip_syllable_separator: bool=True) -> str:
    transcription_method = transcription_methods[language]
    transcribed_words = [transcription_method(word, strip_syllable_separator) for word in words]
    if len(words)==1: # only one word, list all found transcriptions
        return ", ".join(transcribed_words[0])
    elif all(el for el in transcribed_words):
        # return only first transcriptions if the line contains several words
        return " ".join(map(lambda lst: lst[0], transcribed_words))
    else: # if transcriptions for some words are missing don't return anything
        return ""
