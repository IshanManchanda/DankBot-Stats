# DankBot Stats

DankBot is a Telegram Bot which can send, generate, and fry memes.  
DankBot-Stats is a simple Flask app that monitors DankBot and provides statistics using static log analysis.

<b> Live Website Link: </b> https://dankbot-stats.herokuapp.com/  
Note: Website might be slow to load initially due to
[Heroku's Automatic Dyno Sleeping](https://devcenter.heroku.com/articles/free-dyno-hours#dyno-sleeping). 

### Major Technologies Used
- Python 3
- Flask
- MongoDB
- Redis
- Papertrail API

### Things I've Learnt
- Using static log analysis to gain usage and performance insights
- Using the Flask microframework to make a simple webserver in Python
- Using MongoDB for schema-less data storage
- Using a master-slave architecture to efficiently handle background tasks
- Using Redis to queue background tasks
- Using the Python Requests module to interact with APIs (Papertrail)
- Using API Pagination to prevent overloading resources
