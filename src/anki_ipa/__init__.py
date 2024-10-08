# -*- coding: utf-8 -*-

"""
This file is part of the Anki IPA add-on for Anki.
Main Module, hooks add-on methods into Anki.
Copyright: (c) m-rtin <https://github.com/m-rtin>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import os
import urllib
import logging


from anki.hooks import addHook, wrap
from aqt import mw
from aqt.editor import Editor
from aqt.utils import showInfo

from . import consts, parse_ipa_transcription, utils, batch_adding
from .config import setup_synced_config, get_default_lang, set_default_lang
from typing import List, Callable

filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "app.log")
logging.basicConfig(filename=filename, level=logging.DEBUG)

ADDON_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(ADDON_PATH, "icons", "button.png")
CONFIG = mw.addonManager.getConfig(__name__)

select_elm = ("""<select onchange='pycmd("IPALang:" +"""
              """ this.selectedOptions[0].text)' """
              """style='vertical-align: top;'>{}</select>""")


def paste_ipa(editor: Editor) -> None:
    """ Paste IPA transcription into the IPA field of the Anki editor.

    :param editor: Anki editor window
    """
    lang_alias = editor.ipa_lang_alias
    note = editor.note

    # Get content of text field
    try:
        field_text = note[CONFIG["WORD_FIELD"]]
    except KeyError:
        showInfo(f"Field '{CONFIG['WORD_FIELD']}' doesn't exist.")
        return
    logging.debug(f"Field text: {field_text}")

    field_text = field_text.lower()

    # get word list from text field
    words = utils.get_words_from_field(field_text)
    logging.debug(f"Word list: {words}")

    # parse IPA transcription for every word in word list
    try:
        ipa = parse_ipa_transcription.transcript(words=words, language=lang_alias,
                                                 strip_syllable_separator=CONFIG["STRIP_SYLLABLE_SEPARATOR"],
                                                 all_transcriptions=CONFIG["ALL_TRANSCRIPTIONS"])
    except (urllib.error.HTTPError, IndexError):
        showInfo("IPA not found.")
        return
    logging.debug(f"IPA transcription string: {ipa}")

    # paste IPA transcription of every word in IPA transcription field
    try:
        note[CONFIG["IPA_FIELD"]] = ipa
    except KeyError:
        showInfo(f"Field '{CONFIG['IPA_FIELD']}' doesn't exist.")
        return

    # update editor
    editor.loadNote()
    editor.web.setFocus()


def on_setup_buttons(buttons: List[str], editor: Editor) -> List[str]:
    """ Add Addon button and Addon combobox to card editor.

    :param buttons: HTML codes of the editor buttons (e.g. for bold, italic, ...)
    :param editor: card editor object
    :return: updated list of buttons
    """
    shortcut_keys = CONFIG.get("KEYBOARD_SHORTCUT", "Ctrl+Shift+Z")

    # add HTML button
    button = editor.addButton(
        ICON_PATH,
        "IPA",
        paste_ipa,
        keys=shortcut_keys,
        tip=f"IPA transcription ({shortcut_keys})"
    )
    buttons.append(button)

    # create list of language options
    previous_lang = get_default_lang(mw)
    options = [f"""<option>{previous_lang}</option>"""]  # first entry is the last selection

    options += [
        f"""<option>{language}</option>"""
        for language in sorted(consts.LANGUAGES_MAP.keys(), key=str.lower)
        if language != previous_lang
    ]

    # add HTML combobox
    combo = select_elm.format("".join(options))
    buttons.append(combo)

    return buttons


def on_ipa_language_select(editor: Editor, lang: str) -> None:
    """ Set new default IPA language.

    :param editor: Anki editor window
    :param lang: name of selected language
    """
    alias = consts.LANGUAGES_MAP[lang]
    set_default_lang(mw, lang)
    editor.ipa_lang_alias = alias


def init_ipa(editor: Editor, *args, **kwargs) -> None:
    """ Get the last selected/default IPA language.

    :param editor: Anki editor window
    """
    previous_lang = get_default_lang(mw)
    editor.ipa_lang_alias = consts.LANGUAGES_MAP.get(previous_lang, "")


def on_bridge_cmd(editor: Editor, command: str, _old: Callable) -> None:
    """ React when new combobox selection is made.

    :param editor: Anki editor window
    :param command: editor command (e.g. own IPALang or focus, blur, key, ...)
    :param _old: old editor.onBridgeCmd method
    """
    # old commands are executed like before
    if not command.startswith("IPALang"):
        _old(editor, command)
    # new language gets selected in the combobox
    else:
        _, lang = command.split(":")
        on_ipa_language_select(editor, lang)


addHook("profileLoaded", setup_synced_config)
# Overwrite Editor methods
addHook("setupEditorButtons", on_setup_buttons)
Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, on_bridge_cmd, "around")
Editor.__init__ = wrap(Editor.__init__, init_ipa)

# Batch editing
addHook("browser.setupMenus", batch_adding.setup_menu)
