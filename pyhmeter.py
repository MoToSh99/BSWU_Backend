from __future__ import division
import csv
from emosent import get_emoji_sentiment_rank

# Converts from one scale to another (used for emojis)
def rescale(X,A,B,C,D,force_float=False):
    retval = ((float(X - A) / (B - A)) * (D - C)) + C
    if not force_float and all(map(lambda x: type(x) == int, [X,A,B,C,D])):
        return int(round(retval))
    return retval

def load_scores():
    file1 = csv.reader(open("Hedonometer.csv", "r"), delimiter=',')
    for x in range(4):  # strip header info
        next(file1)

    file = csv.reader(open("Emoji_Sentiment_Data_v1.0.csv", "r"), delimiter=',')
    for x in range(4):  # strip header info
        next(file)

    words = {row[1]: float(row[3]) for row in file1}
    emojis = {row[0]: float("{:.2f}".format(rescale(get_emoji_sentiment_rank(row[0])["sentiment_score"], -1, 1, 1, 9))) for row in file}
    
    return {**words, **emojis}

def load_scores_word():
    file1 = csv.reader(open("Hedonometer.csv", "r"), delimiter=',')
    for x in range(4):  # strip header info
        next(file1)

    file = csv.reader(open("Emoji_Sentiment_Data_v1.0.csv", "r"), delimiter=',')
    for x in range(4):  # strip header info
        next(file)

    words = {row[1]: float(row[3]) for row in file1}
    emojis = {row[0]: float("{:.2f}".format(rescale(get_emoji_sentiment_rank(row[0])["sentiment_score"], -1, 1, 1, 9))) for row in file}
    
    return words

def load_scores_emoji():
    file1 = csv.reader(open("Hedonometer.csv", "r"), delimiter=',')
    for x in range(4):  # strip header info
        next(file1)

    file = csv.reader(open("Emoji_Sentiment_Data_v1.0.csv", "r"), delimiter=',')
    for x in range(4):  # strip header info
        next(file)

    words = {row[1]: float(row[3]) for row in file1}
    emojis = {row[0]: float("{:.2f}".format(rescale(get_emoji_sentiment_rank(row[0])["sentiment_score"], -1, 1, 1, 9))) for row in file}
    
    return emojis   

class HMeter(object):
    """HMeter is the main class to prepare a text sample for scores. It
    expects a list of individual words, such as those provided by 
    nltk.word_tokenize, as wordlist. It expects a dict of words as k and
    floating point wordscores as v for wordscores. deltah allows us to 
    filter out the most neutral words as stop words."""

    def __init__(self, wordlist, wordscores, deltah=0.0):
        self.wordlist = wordlist
        self.wordscores = wordscores
        self.deltah = deltah

    _deltah = None
    @property
    def deltah(self):
        """Deltah determines stop words. The higher deltah the more neutral 
        words are are discarded from the matchlist."""
        return self._deltah

    @deltah.setter
    def deltah(self, deltah):
        """Each time deltah is set we need to regenerate the matchlist."""
        self._deltah = deltah
        # TODO Should probably raise a range error if deltah is nonsensical
        # first we take every word that matches labMT 1.0
        labmtmatches = (word for word in self.wordlist
                        if word in self.wordscores)

        # then we strip out stop words as described by Dodd paper
        self.matchlist = []
        self.matchValueList= {}
        for word in labmtmatches:
            score = self.wordscores[word]
            if score >= 5.0 + self.deltah or score <= 5.0 - self.deltah:
                self.matchlist.append(word)
                self.matchValueList.update({word : score})

    def happiness_score(self):
        """Takes a list made up of individual words and returns the happiness
        score."""

        happysum = 0
        count = len(self.matchlist)

        for word in self.matchlist:
            happysum += self.wordscores[word]

        if count != 0:  # divide by zero errors are sad.
            return happysum / count
        else:
            pass  # empty lists have no score
 