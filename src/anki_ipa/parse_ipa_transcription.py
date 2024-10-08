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
import itertools as it
from typing import List, Callable

# Create a dictionary for all transcription methods
transcription_methods = {}
transcription = lambda f: transcription_methods.setdefault(f.__name__, f)


@transcription
def british(word: str, strip_syllable_separator: bool=True) -> list:
    return english_transcript(word, strip_syllable_separator, ['RP','UK',''])

@transcription
def american(word: str, strip_syllable_separator: bool=True) -> list:
    return english_transcript(word, strip_syllable_separator, ['US','GA','GenAm',''])

def english_transcript(word: str, strip_syllable_separator: bool=True, accents: List[str]=[] ) -> list:
    payload = {'action': 'parse', 'page': word, 'format': 'json', 'prop': 'wikitext'}
    r = requests.get('https://en.wiktionary.org/w/api.php', params=payload)
    try:
        wikitext = r.json()['parse']['wikitext']['*']
        # list of tupeles (accent, ipa),
        # avoid to use set to preserve the order of translation we encountered
        transcriptions = []
        # Next variations of the markup are considered:
        #   * {{IPA|en|/dɒɡ/|a=RP}}
        #   * {{IPA|en|/ˈkæn/|[ˈkʰan]|[ˈkʰæn]|a=RP,Ireland}}
        #   * {{IPA|en|/ˈkæn/|[ˈkʰæn]|[ˈkʰɛən ~ ˈkʰeən]|a=GA,Canada|aa=see {{w|/æ/ raising}}}}
        #   * {{IPA|en|/kən/|[kʰən]|[kʰn̩]}}
        #   * {{IPA|en|[hɪo̯]|[hɪʊ̯]|a=[[w:L-vocalization|l-vocalizing]]:,_,UK,AU,NZ}}
        #   * {{enPR|dôg|a=GA}}, {{IPA|en|/dɔɡ/}}
        for m in re.findall( r"(?:{{enPR\|(.*?)}},?\s*)?{{IPA\|en\|(.+?)}}", wikitext ):
            ipas = []
            ipa_accents = []
            if m[0]:
                for el in m[0].split('|'):
                    if el.startswith("a="):
                        ipa_accents.extend(el[2:].split(','))

            ipa_args = re.sub(r"\[\[\s*(.*?)\s*\|\s*(.*?)\s*\]\]", r'\g<2>', m[1])
            for el in ipa_args.split('|'):
                if '=' in el:
                    if el.startswith("a="):
                        ipa_accents.extend(el[2:].split(','))
                    else:
                        pass # don't process other parameters like 'aa='
                else:
                    ipas.append(el)
            if ipa_accents:
                for ac in ipa_accents:
                    if ipa_accents[0].endswith(':'):
                        break # avoid adding unusual accents groups like 'l-vocalizing:' etc
                    transcriptions.extend(it.product([ac], ipas))
            else:
                transcriptions.extend(it.product([''], ipas))

        wanted_transcriptions = []
        for wanted_acc in accents: # this will both filter and prioterize earlier accents and transcriptions
            for (ac, ipa) in transcriptions:
                if ac == wanted_acc:
                    wanted_transcriptions.append(ipa)
        # if there are some transcriptions but not from the list we want, make sure we will get just something
        if transcriptions and not wanted_transcriptions:
            wanted_transcriptions = translations[0][1]
        wanted_transcriptions = map(lambda ipa: remove_special_chars(ipa, strip_syllable_separator),
                                    wanted_transcriptions)
        return remove_duplicates(wanted_transcriptions)
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
    # avoid adding results from the etymology section
    header3_div = tag.find_previous('div', {'class': 'mw-heading3'})
    if header3_div and header3_div.find('h3', {'id': u'Étymologie'}):
        return False
    return True

@transcription
def russian(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://ru.wiktionary.org/wiki/{word}"
    return parse_website(link, {'class': 'IPA'}, strip_syllable_separator)

@transcription
def spanish(word: str, strip_syllable_separator: bool=True) -> list:
    link = f"https://es.wiktionary.org/wiki/{word}"
    soup = get_html_content(link)

    transcriptions = []
    for tbl in soup.find_all('table', {'class': 'pron-graf'}):
        section_header = tbl.find_previous('div', {'class': 'mw-heading2'})
        if not section_header or not section_header.find('span', {'class': 'headline-lang', 'id': 'es'}):
            continue # it's not a spanish entry
        for raw in tbl.find_all('tr'):
            tds=raw.find_all('td')
            if tds and len(tds) == 2 and tds[0].getText().find('(API)'):
                m = re.match(r'\[(.+?)\]', tds[1].getText())
                if m and m[0]:
                    transcriptions.append(m[0])

    transcriptions = map(lambda t: remove_special_chars(t, strip_syllable_separator), transcriptions)

    return remove_duplicates(transcriptions)

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

def transcript(words: List[str], language: str,
               strip_syllable_separator: bool=True,
               all_transcriptions:bool=True) -> str:
    transcription_method = transcription_methods[language]
    transcribed_words = [transcription_method(word, strip_syllable_separator) for word in words]
    if len(words)==1: # only one word, list all/one IPAs depending on the option
        if all_transcriptions:
            return ", ".join(transcribed_words[0])
        else:
            return transcribed_words[0][0]
    elif all(el for el in transcribed_words):
        # return only first transcriptions if the line contains several words
        return " ".join(map(lambda lst: lst[0], transcribed_words))
    else: # if transcriptions for some words are missing don't return anything
        return ""
