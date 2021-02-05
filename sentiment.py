from nltk.tokenize import sent_tokenize, word_tokenize
import pyhmeter
import methods
import re

EXAMPLE_TEXT = "@everytime i hear friends or pals talk about their weed habits, i'm starting to think that weed is actually fucking awful"
pattern = re.compile('@\w*')
removedAt = pattern.sub('', EXAMPLE_TEXT)
tokens = word_tokenize(removedAt)

print(tokens)

file = pyhmeter.load_scores("Hedonometer.csv")

h = pyhmeter.HMeter(tokens, file, 1.5)
print(h.matchlist)
print(h.happiness_score()) 

""" allTweets = methods.getTweets("washingtonpost")

avgscore = 0
count = 0
for status in allTweets:
    tokens = word_tokenize(status)
    h = pyhmeter.HMeter(tokens, file, 2)
    #print(h.matchlist)
    currentScore = h.happiness_score()
    if(currentScore != None) :
        avgscore += currentScore
        count += 1

print(avgscore/count)  """

        