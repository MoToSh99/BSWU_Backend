from nltk.tokenize import sent_tokenize, word_tokenize
import pyhmeter

EXAMPLE_TEXT = "Hello Mr. Smith, how are you doing today? The weather is great, and Python is awesome. The sky is pinkish-blue. You shouldn't eat cardboard."

tokens = word_tokenize(EXAMPLE_TEXT)

h = pyhmeter.HMeter(tokens)
h.matchlist(['love', 'pancakes', 'laughter', 'and', 'hate', 'terrorism'])
print(h.happiness_score())