import tweepy as tw

def setupTwitterAuth(): 
    # Keys for Twitter authentication
    consumer_key= 'XhZTPqiT0wsJJxPez6gjMSvSz'
    consumer_secret= 'Qpr5duOtcGKIQJx68zM0AlLLrBW86dTlmrEIJ9LHCEq1TIOLml'
    access_token= '1347473963186868224-HGJshd4cYrcEn27jPr7iuKV80H6gqp'
    access_token_secret= '5Wy037PaxA8gTa83Ly69NYx15m1unCDfYunx0wlDxJo8S'

    # Authenticate user
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Use tweepy api
    return tw.API(auth, wait_on_rate_limit=False)