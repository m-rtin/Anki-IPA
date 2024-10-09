Help for configuration options.

&nbsp;

- **`"WORD_FIELD"`**: Field which contains the word or words you would like to get an IPA transcription for.

&nbsp;

- **`"IPA_FIELD"`**: The field name where the IPA transcription should be written into.
&nbsp;

- **`"KEYBOARD_SHORTCUT"`**: Shortcut that can be used to execute the add on.

&nbsp;

- **`"STRIP_SYLLABLE_SEPARATOR"`**: IPA syntax includes a period (.) between two syllables when between two consecutive vowels in hiatus.  For example `kre.entsa`.  By default this is stripped out but if desired it can be retained.

&nbsp;

- `"ALL_TRANSCRIPTIONS"`: if several transcriptions all available for a single-word entry, all of them will be added to the IPA field. If `false` only the best match will be added. Multi-word entries are always transcribed with a single word.

&nbsp;

- `"FAILURE_STRATEGY"`: whether or not to display transcription look-up failures. Possible values are:
    - `'show'` - replace all transcriptions that failed to be retrieved with `~???~`.
    - `'partial'` - replace with error markers only failed transcriptions of specific words. In multi-word phrases, don't display anything if the whole phrase failed.
    - `'whole'` - display an error for whole phrases only. If a transcription for a single word failed in a multi-word phrase, the whole phrase will be displayed as erroneous.
    - `'hide'` - all failure will be silently ignored and no transcriptions will be added. If any word of a multi-word phrase lack a transcription the whole phrase will be dropped.
