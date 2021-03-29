import tweepy as tw

def setupTwitterAuth(): 
    # Keys for Twitter authentication
    consumer_key= 'DHwbawZ8ivWs4rIA5VTNxzklA'
    consumer_secret= 'xF0c2utAM9J4iU8PU4MYQiATlSlwtYfbz63AwvTyeVaYRmwleF'
    access_token= '1347473963186868224-fhkb9qGMgCNmzPx0ywstICmBDhsGZp'
    access_token_secret= 'Y77pgICcBK20ifWHLGTa0cBxFUp17XNo7PyHqw3fqjujT'

    # Authenticate user
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Use tweepy api
    return tw.API(auth, wait_on_rate_limit=True)