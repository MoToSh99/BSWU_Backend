from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter
import config
import tweepy as tw

file = pyhmeter.load_scores()

# Gets the Pyhmeter and removes unnecessary symbols from a given tweet
def getPyhmeter(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('(@\w*)|(\|.*)|(#\s*)')
    removedAt = pattern.sub('', tweet_text)
    tk = TweetTokenizer()
    tokens = tk.tokenize(removedAt)
    
    return pyhmeter.HMeter(tokens, file, 1)

# Gets the happiness score from a single tweet
def getHapinessScore(tweet_text):

    global file
    file = pyhmeter.load_scores()
    py = getPyhmeter(tweet_text)
    score = py.happiness_score()


    file = pyhmeter.load_scores_word()
    py2 = getPyhmeter(tweet_text)
    score2 = py2.happiness_score()

    file = pyhmeter.load_scores_emoji()
    py3 = getPyhmeter(tweet_text)
    score3 = py2.happiness_score()

    
    if score != None and score2 != None and len(py3.matchlist) != 0 :
        print("Full Text: " + tweet_text)
        print ("With emoji")
        print(py.matchlist)
        print(score)

        print("Without emoji")
        print(py2.matchlist)
        print(score2)
        print("\n")


# Get all matches from a single tweet along with their individual scores
def getWordsWithScore(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    return pyhmeter.matchValueList

def runtest():

    tweets = [
        "1 goal scored in the past 6 premier league games at Anfield. Absolutely crazy. Everton’s defence were brilliant. Good night 😩😩",
        "What are my memories from Costa Brava? #spain 🥰 Lovely people, delicious food 😋 ",
        "So happy my book is now available in Spanish worldwide. Gracias @rocaeditorial 📖🤩",
        "Happy New Year 🥳❤️ May 2021 be a year of hope, healing and happiness for everyone.",
        "Happy Birthday, Luc Robitaille 🎉 🎊 🎈",
        "Great news about the US rejoining the Paris Agreement 👏 We plan to do our part by meeting our goals on net zero emissions, using 100% renewable energy and reducing greenhouse gas emissions 🌎 ",
        "When I am at my best mental, physical and spiritual health, everything around me falls into alignment.” ✨ #ThisWeekOnInstagram",
        "Start the weekend with a slice of happy. And for more servings of 🙂 check out our story right now. ",
        "Butters finds beauty in his broken heart 💔",
        "The Catholic Boattttt 🛥️",
        "🥶🥶🥶 Within the hour the temperature outside will fall to over -70,000,000°",
        "🧍‍♀️🧍‍♀️ k i’m gonna go workout for an hour and complain about how much i hate squats and food",
        "Today I officially became a homeowner 🥺🏠",
        "We’re so glad you’re feeling the Vday vibes today but if everyone keeps playing Pony you might break the app 🙃",
        "MY FACE IS ON A BILLBOARD IN TIMES SQUARE 😭😭😭 @Spotify #HotCountry you the realest ❤️❤️",
        "I hope you have the loveliest of days today 💜 Currently playing #AnimalCrossing, drinking coffee, and watching the snow. You?",
        "You are looking at the best headset for console gaming ever created. GG Xbox 😍",
        "Happy Valentine's Day, y'all! 💗 #IDareYou to spread a little love today! Whether it's with a significant other, a friend, a family member, or someone random... let's be kind to one another! 🤗",
        "It's almost that time y'all! @NBCTheVoice is back on 3/1 🥳 #TeamKelly",
        "still can’t believe this. Rest Peacefully Sophie. 💔 🙏🏾",
        "one hour & i’ll see u even sooner than that 😌 love u",
        "did you learn all this by searching “twitter slang” on google 🙄",
        "This lady on Facebook gave her dog a maternity shoot omg 😭 😍",
        "Poor little Snowflake... ❄️😢🐩",
        "Trumps should be in Florida and it should be in the shape of a giant dumpster fire to commemorate how terrible it was 😂",
        "TOGETHER WE CAN BEAT THEM!🦾🦍🙌",
        "To anyone wondering about the EQG awards They’re in 4 hours 😎",
        "YES billieeilish knows EVERYTHING about justinbieber 😱If you thought perrikiely was the ultimate belieber… then you just haven’t heard the level of DETAIL Billie Eilish has 😭 You should see her in a crown 🎵😉",
        "Eat what you want my love. Everyone should. Ignore the food snobs. Focus on the great stuff. I mean, you are the author of four best selling books! 😘",
        "I find it inexcusable. I don’t think I could ever be so brazen as to describe English culture or food to and English native.... There are reasons why im a misanthropist. 😘",
        "I’m hungry the only food item in my room was an Easter egg so I sat n broke it up will watching YouTube and ended up eating the whole thing 😂😂 wtf is wrong with me?",
        "ATLANTA!!!! I’m out here!! Sis and I just ate real real good at one of my FAV BRUNCH SPOTS. It was low key with No wait and good food!!  Love my sis @zainab_bosslady_carter ❤️❤️ @ Flying Biscuit Cafe - Roswell"
    ]

    for t in tweets:
        getHapinessScore(t)

runtest()

def randomTweets():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(100)
    
    for t in tweets:
        getHapinessScore(t.full_text)

#randomTweets()