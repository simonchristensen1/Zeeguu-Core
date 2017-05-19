# -*- coding: utf8 -*-
import datetime
import re

import flask_sqlalchemy
import os
import zeeguu
from flask import Flask

# zeeguu.db must be setup before we load the model classes the first time
from zeeguu.algos.algo_service import AlgoService

if __name__ == "__main__":

    print ("!!!! in populate...")
    zeeguu.app = Flask("Zeeguu-Core-Test")

    config_file = os.path.expanduser('~/.config/zeeguu/core.cfg')
    if os.environ.has_key("CONFIG_FILE"):
        config_file = os.environ["CONFIG_FILE"]
    zeeguu.app.config.from_pyfile(config_file, silent=False)  # config.cfg is in the instance folder

    zeeguu.db = flask_sqlalchemy.SQLAlchemy(zeeguu.app)
    print ("running with DB: " + zeeguu.app.config.get("SQLALCHEMY_DATABASE_URI"))

from zeeguu.model.url import Url
from zeeguu.model.text import Text
from zeeguu.model.exercise_outcome import ExerciseOutcome
from zeeguu.model.exercise_source import ExerciseSource
from zeeguu.model.user_word import UserWord
from zeeguu.model.exercise import Exercise
from zeeguu.model.bookmark import Bookmark
from zeeguu.model.bookmark_priority_arts import BookmarkPriorityARTS
from zeeguu.model.language import Language
from zeeguu.model.user import User

WORD_PATTERN = re.compile("\[?([^{\[]+)\]?( {[^}]+})?( \[[^\]]\])?")

TEST_PASS='test'
TEST_EMAIL='i@mir.lu'

TEST_BOOKMARKS_COUNT = 2


def drop_current_tables(db):
    # We have to do a commit() before the drop_all()
    # Otherwise the system just freezes sometimes!
    db.session.commit()
    db.session.close_all()
    # Initial cleanup
    db.reflect()
    db.drop_all()
    # Creating the tables again
    db.create_all()


def add_bookmark(db, user, original_language, original_word, translation_language, translation_word,  date, the_context, the_url, the_url_title):

    url = Url.find (the_url)
    text = Text.find_or_create(the_context, translation_language, url)
    origin = UserWord.find(original_word, original_language)
    translation = UserWord.find(translation_word, translation_language)

    b1 = Bookmark(origin, translation, user, text, date)
    db.session.add_all([url,text,origin,translation,b1])
    db.session.commit()

    add_bookmark_priority_arts(db, b1, 1)

    return b1


def add_bookmark_priority_arts(db, bookmark, priority):
    bp = BookmarkPriorityARTS(bookmark, priority)
    db.session.add(bp)
    db.session.commit()

#
def create_minimal_test_db(db):

    drop_current_tables(db)

    # Some common test fixtures
    de = Language("de", "German")
    en = Language("en", "English")
    nl = Language("nl", "Dutch")
    ro = Language("ro", "Romanian")

    db.session.add_all([en, de, nl]);

    mir = User(TEST_EMAIL, "Mircea", TEST_PASS, de, en)

    db.session.add(mir)

    show_solution = ExerciseOutcome("Show solution", False)
    retry = ExerciseOutcome("Retry", False)
    correct = ExerciseOutcome("Correct", True)
    wrong = ExerciseOutcome("Wrong", False)
    typo = ExerciseOutcome("Typo", False)
    too_easy = ExerciseOutcome("Too easy", True)

    db.session.add_all([show_solution, retry,
                        correct, wrong, typo,
                        too_easy]);

    recognize = ExerciseSource("Recognize")
    translate = ExerciseSource("Translate")

    db.session.add_all([recognize, translate])

    b1 = add_bookmark(db, mir, de, "Schaf", en, "sheep",
                      datetime.datetime(2011, 01, 01, 01, 01, 01),
                    "Bitte... zeichne mir ein Schaf!",
                    "http://www.derkleineprinz-online.de/text/2-kapitel/",
                    "Der Kleine Prinz - Kapitel 2")

    b2 = add_bookmark(db, mir, de, "sprang", en, "jumped",
                      datetime.datetime(2011, 01, 01, 01, 01, 01),
                    "Ich sprang auf die Fusse.",
                    "http://www.derkleineprinz-online.de/text/2-kapitel/",
                    "Der Kleine Prinz - Kapitel 2")

    # create exercises
    e1 = Exercise(wrong, recognize, 1500, datetime.datetime(2011, 01, 02, 01, 01, 01))
    e2 = Exercise(correct, recognize, 1000, datetime.datetime(2011, 01, 03, 01, 01, 01))
    e3 = Exercise(typo, recognize, 1800, datetime.datetime(2011, 01, 04, 01, 01, 01))
    db.session.add(e1)
    db.session.add(e2)
    db.session.add(e3)

    b1.add_new_exercise(e1)
    b1.add_new_exercise(e2)
    b2.add_new_exercise(e3)

    db.session.commit()



    global TEST_BOOKMARKS_COUNT
    TEST_BOOKMARKS_COUNT = 2
    db.session.commit()




class WordCache(object):
    def __init__(self):
        self.cache = {}

    def __getitem__(self, args):
        word = self.cache.get(args, None)
        if word is None:
            word = UserWord(*args)
            zeeguu.db.session.add(word)
            self.cache[args] = word
        return word


def populate(from_, to, dict_file):
    cache = WordCache()
    with open(dict_file, "r") as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                return
            orig = cache[clean_word(parts[0]), from_]
            trans = cache[clean_word(parts[1]), to]
            if trans not in orig.translations:
                orig.translations.append(trans)


def filter_word_list(word_list):
    filtered_word_list = []
    lowercase_word_list = []
    for word in word_list:
         if word.lower() not in lowercase_word_list:
            lowercase_word_list.append(word.lower())
    for lc_word in lowercase_word_list:
        for word in word_list:
            if word.lower()  == lc_word:
                filtered_word_list.append(word)
                break
    return filtered_word_list


def path_of_language_resources():
    """
    the easiest way to make sure that the langauge dictionary files
    are found when running the test cases, either from IDE or from the
    command line is to
    - compute the path relative to this file
    :return:
    """
    import os
    path = os.path.dirname(__file__)
    return path+"/language_data/"


def test_word_list(lang_code):

    words_file = open(path_of_language_resources()+lang_code+"-test.txt")
    words_list = words_file.read().splitlines()
    return words_list

def clean_word(word):
    match = re.match(WORD_PATTERN, word)
    if match is None:
        return word.decode("utf8")
    return match.group(1).decode("utf8")



def create_test_db(db):

    drop_current_tables(db)

    de = Language("de", "German")
    da = Language("da", "Danish")
    en = Language("en", "English")
    es = Language("es", "Spanish")
    fr = Language("fr", "French")
    it = Language("it", "Italian")
    no = Language("no", "Norwegian")
    nl = Language("nl", "Dutch")
    pt = Language("pt", "Portughese")
    ro = Language("ro", "Romanian")

    db.session.add(de)
    db.session.add(da)
    db.session.add(en)
    db.session.add(es)
    db.session.add(fr)
    db.session.add(it)
    db.session.add(no)
    db.session.add(nl)
    db.session.add(pt)
    db.session.add(ro)
    db.session.commit()

    show_solution = ExerciseOutcome("Show solution", False)
    retry = ExerciseOutcome("Retry", False)
    correct = ExerciseOutcome("Correct", True)
    wrong = ExerciseOutcome("Wrong", False)
    typo = ExerciseOutcome("Typo", False)
    too_easy = ExerciseOutcome("Too easy", True)

    recognize = ExerciseSource("Recognize")
    translate = ExerciseSource("Translate")
    zeekoe = ExerciseSource("ZeeKoe")

    db.session.add(show_solution)
    db.session.add(retry)
    db.session.add(correct)
    db.session.add(wrong)
    db.session.add(typo)
    db.session.add(too_easy)

    db.session.add(recognize)
    db.session.add(translate)
    db.session.add(zeekoe)

    user = User(TEST_EMAIL, "Mircea", TEST_PASS, de, ro)
    user2 = User("i@ada.lu", "Ada", "pass", fr)

    db.session.add(user)
    db.session.add(user2)

    jan111 = datetime.datetime(2011,01,01,01,01,01)
    ian101 = datetime.datetime(2001,01,01,01,01,01)
    jan14 = datetime.datetime(2014,1,14,01,01,01)

    b1 = add_bookmark(db, user, de, "Schaf", en, "sheep",
                      datetime.datetime(2011, 01, 01, 01, 01, 01),
                      "Bitte... zeichne mir ein Schaf!",
                      "http://www.derkleineprinz-online.de/text/2-kapitel/",
                      "Der Kleine Prinz - Kapitel 2")

    b2 = add_bookmark(db, user, de, "sprang", en, "jumped",
                      datetime.datetime(2011, 01, 01, 01, 01, 01),
                      "Ich sprang auf die Fusse.",
                      "http://www.derkleineprinz-online.de/text/2-kapitel/",
                      "Der Kleine Prinz - Kapitel 2")

    # create exercises
    e1 = Exercise(wrong, recognize, 1500, datetime.datetime(2011, 01, 02, 01, 01, 01))
    e2 = Exercise(correct, recognize, 1000, datetime.datetime(2011, 01, 03, 01, 01, 01))
    e3 = Exercise(typo, recognize, 1800, datetime.datetime(2011, 01, 04, 01, 01, 01))
    db.session.add(e1)
    db.session.add(e2)
    db.session.add(e3)

    b1.add_new_exercise(e1)
    b1.add_new_exercise(e2)
    b2.add_new_exercise(e3)

    today_dict = {
        'sogar':'actually',
        'sperren':'to lock, to close',
        'Gitter':'grates',
        'erfahren':'to experience',
        'treffen':'hit',
        'jeweils':'always',
        'Darstellung':'presentation',
        'Vertreter':'representative',
        'Knecht':'servant',
        'der':'the'
    }

    dict = {
            u'Spaß': 'fun',
            'solche': 'suchlike',
            'ehemaliger': 'ex',
            'betroffen': 'affected',
            'Ufer':'shore',
            u'höchstens':'at most'
            }

    french_dict = {
        'jambes':'legs',
        'de':'of',
        'et':'and'
            }

    story_url = 'http://www.gutenberg.org/files/23393/23393-h/23393-h.htm'
    japanese_story = [
            # ['recht', 'right', 'Du hast recht', story_url],
            ['Holzhauer', 'wood choppers', 'Da waren einmal zwei Holzhauer können', story_url],
            ['Da', 'there', 'Da waren einmal zwei Holzhauer können', story_url],
            ['zwei', 'two', 'Da waren einmal zwei Holzhauer können', story_url],
            [u'Wald','to arrive', u'Um in den Walden zu gelangen, mußten sie einen großen Fluß passieren. Um in den Walden zu gelangen, mußten sie einen großen Fluß passieren. Um in den Walden zu gelangen, mußten sie einen großen Fluß passieren. Um in den Walden zu gelangen, mußten sie einen großen Fluß passieren', story_url],
            ['eingerichtet','established',u'Um in den Wald zu gelangen, mußten sie einen großen Fluß passieren, über den eine Fähre eingerichtet war', story_url],
            [u'vorläufig','temporary',u'von der er des rasenden Sturmes wegen vorläufig nicht zurück konnte', story_url],
            [u'werfen', 'to throw',u'Im Hause angekommen, warfen sie sich zur Erde,', story_url],
            ['Tosen','roar',u'sie Tür und Fenster wohl verwahrt hatten und lauschten dem Tosen des Sturmes.sie Tür und Fenster wohl verwahrt hatten und lauschten dem Tosen des Sturmes.sie Tür und Fenster wohl verwahrt hatten und lauschten dem Tosen des Sturmes',story_url],
            ['Entsetzen','horror','Entsetzt starrte Teramichi auf die Wolke',story_url]
        ]

    for key in today_dict:
        add_bookmark(db, user, de, key, en, today_dict[key], jan111, "Keine bank durfe auf immunitat pochen, nur weil sie eine besonders herausgehobene bedeutung fur das finanzsystem habe, sagte holder, ohne namen von banken zu nennen",
                         "http://url2", "title of url2")

    for key in dict:
        add_bookmark(db, user, de, key, en, dict[key], ian101, "Deutlich uber dem medianlohn liegen beispielsweise forschung und entwicklung, tabakverarbeitung, pharma oder bankenwesen, am unteren ende der skala liegen die tieflohnbranchen detailhandel, gastronomie oder personliche dienstleistungen. ",
                         "http://url1", "title of url1")

    for key in french_dict:
        add_bookmark(db, user, de, key, en, french_dict[key], ian101, "Deutlich uber dem medianlohn liegen beispielsweise forschung und entwicklung, tabakverarbeitung, pharma oder bankenwesen, am unteren ende der skala liegen die tieflohnbranchen detailhandel, gastronomie oder personliche dienstleistungen. ",
                         "http://url1", "title of url1")
    for w in japanese_story:
        add_bookmark(db, user, de, w[0], en, w[1],jan14, w[2],w[3], "japanese story")

    db.session.commit()

    AlgoService.update_exercise_source_stats()


if __name__ == "__main__":

    print ("Populating the db")
    create_test_db(zeeguu.db)
