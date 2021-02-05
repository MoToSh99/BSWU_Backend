import tweepy as tw

def setupTwitterAuth(): 
    # Keys for Twitter authentication
    consumer_key= '8XJfacAcQtqyyqkcK924dz63o'
    consumer_secret= '71KcvzZhSOGWipDiTfcKXp9o1nF31X3HBWJJuSTZjuxTRaJW38'
    access_token= '1347473963186868224-iW0Fzp9Zrjt04uipB4Uap34X3CfO0f'
    access_token_secret= 'QwYU6arYs7N9uERLRbW94oJ2wvWrymsUjaCR2uvue0tHQ'

    # Authenticate user
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Use tweepy api
    return tw.API(auth, wait_on_rate_limit=True)