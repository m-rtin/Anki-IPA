# -*- coding: utf-8 -*-

"""
This file is part of the Anki IPA add-on for Anki.
Test parsing methods
Copyright: (c) 2019 m-rtin <https://github.com/m-rtin>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import unittest
import parse_ipa_transcription as parse_ipa


class TestParseIpa(unittest.TestCase):

    def test_british(self):
        # * {{a|RP}} {{IPA|en|/ˈtʃɑː.kəʊl/}}
        self.assertEqual(parse_ipa.british("charcoal"), ["ˈtʃɑːkəʊl"])
        self.assertEqual(parse_ipa.british("dog"), ["dɒɡ"])
        self.assertEqual(parse_ipa.british("thumb"), ["θʌm"])
        self.assertEqual(parse_ipa.british("box"), ["bɒks"])
        # * {{a|UK}} {{IPA|en|/bɜːst/}}
        self.assertEqual(parse_ipa.british("burst"), ["bɜːst"])
        self.assertEqual(parse_ipa.british("hill"), ["hɪɫ", "hɪl"])
        # {{a|RP|GA}} {{IPA|en|/bæk/|[bæk]|[bak]|[-k̚]|[-ˀk]}}
        self.assertEqual(parse_ipa.british("back"), ["bæk","bak","-k̚","-ˀk"])
        # {{a|RP}} {{IPA|en|/ɹɪˈɡɑːd/}}
        self.assertEqual(parse_ipa.british("regard"), ["ɹɪˈɡɑːd"])
        self.assertEqual(parse_ipa.british("out"), ["aʊt"])

        # A complex phrase
        self.assertEqual(parse_ipa.transcript(["schedule", "advertisement"], 'british'),
                         "ˈʃɛdjuːl ədˈvɜːtɪsmənt")

        # some Generic english test
        self.assertEqual(parse_ipa.british("emmener"), []) # not an English word
        self.assertEqual(parse_ipa.transcript([], 'british'), "") # string with no words


    def test_american(self):
        # * {{a|GA}} {{IPA|en|/ˈt͡ʃɑɹ.koʊl/}}
        self.assertEqual(parse_ipa.american("charcoal"), ["ˈt͡ʃɑɹkoʊl"])
        self.assertEqual(parse_ipa.american("dog"), ["dɔɡ"])
        self.assertEqual(parse_ipa.american("thumb"), ["θʌm"])
        self.assertEqual(parse_ipa.american("box"), ["bɑks"])
        # * {{a|US}} {{IPA|en|/bɝst/}}
        self.assertEqual(parse_ipa.american("burst"), ["bɝst"])
        # {{enPR|hĭl}}, {{IPA|en|/hɪl/|[hɪɫ]}}
        self.assertEqual(parse_ipa.american("hill"), ["hɪɫ", "hɪl"])
        # {{a|RP|GA}} {{IPA|en|/bæk/|[bæk]|[bak]|[-k̚]|[-ˀk]}}
        self.assertEqual(parse_ipa.american("back"), ["bæk","bak","-k̚","-ˀk"])
        # {{a|GenAm}} {{IPA|en|/ɹɪˈɡɑɹd/}}
        self.assertEqual(parse_ipa.american("regard"), ["ɹɪˈɡɑɹd"])
        self.assertEqual(parse_ipa.american("out"), ["aʊt"])

        # A complex phrase
        self.assertEqual(parse_ipa.transcript(["schedule", "advertisement"], 'american'),
                         "ˈskɛd͡ʒʊl ˈædvɚˌtaɪzmənt")

    def test_russian(self):
        self.assertEqual(parse_ipa.russian("спасибо"), ["spɐˈsʲibə"])

    def test_french(self):
        self.assertEqual(parse_ipa.french("occasion"),  [ "ɔkazjɔ̃" ])
        self.assertEqual(parse_ipa.french("rencontre"), [ "ʁɑ̃kɔ̃tʁ" ])
        self.assertEqual(parse_ipa.french("cheval"), [ "ʃəval", "ʃfal", "ʃval", "ʒval", "ʃoval" ])
        self.assertEqual(parse_ipa.french("dog"), []) # not a french word
        self.assertEqual(parse_ipa.transcript(["cheval"], 'french'),
                         "ʃəval, ʃfal, ʃval, ʒval, ʃoval")
        self.assertEqual(parse_ipa.transcript(["le", "chat"], 'french'), "lə ʃa")
        # a string with a non-existing word
        self.assertEqual(parse_ipa.transcript(["le", "boulangery"], 'french'), "")
        self.assertEqual(parse_ipa.transcript([], 'french'), "") # no words

    def test_spanish(self):
        self.assertEqual(parse_ipa.spanish("eternidad"), ["eteɾniˈðað"])
        # has non-spanish entry
        self.assertEqual(parse_ipa.spanish("actor"), ["açˈtoɾ"])
        # has several pronosiations
        self.assertEqual(parse_ipa.spanish("elle"), ["ˈeʝe", "ˈeʎe", "ˈeʃe", "ˈeʒe"])

    def test_german(self):
        self.assertEqual(parse_ipa.german("Land"), ["lant"])
        self.assertEqual(parse_ipa.german("blau"), ["blaʊ̯"])
        self.assertEqual(parse_ipa.german("Kind"), ["kɪnt"])
        self.assertEqual(parse_ipa.german("spielen"), ["ˈʃpiːlən"])
        self.assertEqual(parse_ipa.german("treffen"), ["ˈtʁɛfn̩"])
        self.assertEqual(parse_ipa.german("gelb"), ["ɡɛlp"])
        self.assertEqual(parse_ipa.german("Mensch"), ["mɛnʃ"])
        self.assertEqual(parse_ipa.german("Hund"), ["hʊnt"])
        self.assertEqual(parse_ipa.german("grün"), ["ɡʁyːn"])
        self.assertEqual(parse_ipa.german("rot"), ["ʁoːt"])
        self.assertEqual(parse_ipa.german("blau"), ["blaʊ̯"])
        self.assertEqual(parse_ipa.german("braun"), ["bʁaʊ̯n"])
        self.assertEqual(parse_ipa.german("Hilfe"), ["ˈhɪlfə"])
        self.assertEqual(parse_ipa.german("zwei"), ["t͡svaɪ̯"])
        self.assertEqual(parse_ipa.german("drei"), ["dʁaɪ̯"])
        self.assertEqual(parse_ipa.german("vier"), ["fiːɐ̯"])
        self.assertEqual(parse_ipa.german("zehn"), ["t͡seːn"])
        self.assertEqual(parse_ipa.german("acht"), ["axt"])
        self.assertEqual(parse_ipa.german("neun"), ["nɔɪ̯n"])
        self.assertEqual(parse_ipa.german("nein"), ["naɪ̯n"])
        self.assertEqual(parse_ipa.german("Fenster"), ["ˈfɛnstɐ"])
        self.assertEqual(parse_ipa.german("Ente"), ["ˈɛntə"])
        self.assertEqual(parse_ipa.german("Katze"), ["ˈkat͡sə"])
        self.assertEqual(parse_ipa.german("Buch"), ["buːx"])
        self.assertEqual(parse_ipa.german("Eintrag"), ["ˈaɪ̯nˌtʁaːk"])
        # :{{IPA}} ''standardsprachlich (gemeindeutsch):'' {{Lautschrift|ʃpɛːt}}
        self.assertEqual(parse_ipa.german("spät"), ["ʃpɛːt"])

    def test_polish(self):
        self.assertEqual(parse_ipa.polish("asteroida"), ["ˌastɛˈrɔjda"])
        self.assertEqual(parse_ipa.polish("mały"), ["ˈmawɨ"])

    def test_dutch(self):
        self.assertEqual(parse_ipa.dutch("wit"), ["ʋɪt", "wit", "wɪt"])
        self.assertEqual(parse_ipa.dutch("lucht"), ["lʏxt"])

if __name__ == "__main__":
    unittest.main()
