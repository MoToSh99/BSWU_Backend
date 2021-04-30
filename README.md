## Backend for HappyTweet

Collects Tweets from a user, performs sentiment analysis, and returns a JSON-object with all necessary data for the frontend.

Developed in Python.

## Installation and Setup Instructions

Clone down this repository. You will need `python`.

To Start Server:

`python app.py`  

To Visit App:

`http://0.0.0.0:5000/`

### API endpoints

|     Endpoint    |        Request arguments       |                                                                      Usage                                                                      |
|:---------------:|:------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------:|
|        /        |                                |                                                            A welcome page for the API                                                           |
|    /userinfo    |        Twitter username        | Returns information about the Twitter user: Name, username, location, followers count, Tweets count, friends count, and their profile image URL |
| /gettwitterdata |        Twitter username        |                                                 Calls the Twitter API to fetch the user's Tweets and analyzes the data for the Twitter user                                                |                                             |                                               |                                                |
|     /rating     | Twitter username, and a number |                                                      Used to send a rating to the database                                                      |
