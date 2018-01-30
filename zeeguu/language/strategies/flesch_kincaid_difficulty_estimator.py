import string

from zeeguu import model
from zeeguu.language.difficulty_estimator_strategy import DifficultyEstimatorStrategy
import nltk
import math


class FleschKincaidDifficultyEstimator(DifficultyEstimatorStrategy):
    """
    The Flesch-Kincaid readability index is a classic readability index.
    Wikipedia : https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests
    """

    AVERAGE_SYLLABLE_LENGTH = 2.5  # Simplifies the syllable counting
    CUSTOM_NAMES = ["fk", "fkindex", "flesch-kincaid"]

    @classmethod
    def estimate_difficulty(cls, text: str, language: 'model.Language', user: 'model.User'):
        '''
        Estimates the difficulty based on the Flesch-Kincaid readability index.
        :param text: See DifficultyEstimatorStrategy
        :param language: See DifficultyEstimatorStrategy
        :param user: See DifficultyEstimatorStrategy
        :rtype: dict
        :return: The dictionary contains the keys and return types
                    normalized: float (0<=normalized<=1)
                    discrete: string [EASY, MEDIUM, HARD]
        '''
        flesch_kincaid_index = cls.flesch_kincaid_readability_index(text, language)

        difficulty_scores = dict(
            normalized=cls.normalize_difficulty(flesch_kincaid_index),
            discrete=cls.discrete_difficulty(flesch_kincaid_index)
        )

        return difficulty_scores

    @classmethod
    def __flesch_kincaid_readability_index(cls, text: str, language: 'model.Language'):
        words = nltk.word_tokenize(text)

        number_of_syllables = 0
        number_of_words = 0
        for word in words:
            if word not in string.punctuation:  # Filter punctuation
                syllables_in_word = cls.estimate_number_of_syllables_in_word(word, language)
                number_of_syllables += syllables_in_word
                number_of_words += 1

        number_of_sentences = len(nltk.sent_tokenize(text))

        if language.code == "de":
            starting_constant = 180
            sentence_length_factor = 1
            word_length_factor = 58.5
        else:
            starting_constant = 206.835
            sentence_length_factor = 1.015
            word_length_factor = 84.6

        index = starting_constant - sentence_length_factor * (number_of_words / number_of_sentences) \
                - word_length_factor * (number_of_syllables / number_of_words)
        return index

    @classmethod
    def __estimate_number_of_syllables_in_word(cls, word: str, language: 'model.Language'):
        if len(word) < cls.AVERAGE_SYLLABLE_LENGTH:
            syllables = 1  # Always at least 1 syllable
        else:
            syllables = len(word) / cls.AVERAGE_SYLLABLE_LENGTH
        return int(math.floor(syllables))  # Truncate the number of syllables

    @classmethod
    def __normalize_difficulty(cls, score: int):
        if score < 0:
            return 1
        elif score > 100:
            return 0
        else:
            return 1 - (score * 0.01)

    @classmethod
    def __discrete_difficulty(cls, score: int):
        if score > 80:
            return "EASY"
        elif score > 50:
            return "MEDIUM"
        else:
            return "HARD"
