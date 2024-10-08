# -*- coding: utf-8 -*-

"""
This file is part of the Anki IPA add-on for Anki.
Synchronize addon configuration.
Copyright: (c) m-rtin <https://github.com/m-rtin>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from aqt import mw


def setup_synced_config() -> None:
    """Create new configuration if not already done."""
    conf_name = "anki_ipa_conf"

    if conf_name not in mw.col.conf:
        mw.col.conf[conf_name] = {
            "defaultlangperdeck": 1,
            "deckdefaultlang": {},  # default addon language for specific decks
            "lang": "eng"
        }


def get_deck_name(main_window: mw) -> str:
    """ Get the name of the current deck.

    :param main_window: main window of Anki
    :return: name of selected deck
    """
    try:
        deck_name = main_window.col.decks.current()['name']
    except AttributeError:
        # No deck opened?
        deck_name = None
    return deck_name


def get_default_lang(main_window: mw) -> str:
    """ Get the IPA default language.

    :param main_window: main window of Anki
    :return: default IPA language for Anki or Anki deck
    """
    config = mw.col.conf['anki_ipa_conf']
    lang = config['lang']
    if config['defaultlangperdeck']:
        deck_name = get_deck_name(main_window)
        if deck_name and deck_name in config['deckdefaultlang']:
            lang = config['deckdefaultlang'][deck_name]
    return lang


def set_default_lang(main_window: mw, lang: str) -> None:
    """ Set new IPA default language.

    :param main_window: main window of Anki
    :param lang: new default language
    """
    config = mw.col.conf['anki_ipa_conf']
    config['lang'] = lang  # Always update the overall default
    if config['defaultlangperdeck']:
        deck_name = get_deck_name(main_window)
        if deck_name:
            config['deckdefaultlang'][deck_name] = lang
