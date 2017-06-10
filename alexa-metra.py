import os
import logging
import datetime
import math
import re
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode
from google.transit import gtfs_realtime_pb2
from secrets import accessKey, secretKey
import requests, zipfile, StringIO
import transitfeed
import os

import aniso8601
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

def update_schedule():
    schedule_zip = requests.get('https://gtfsapi.metrarail.com/gtfs/raw/schedule.zip', auth=(accessKey, secretKey))
    z = zipfile.ZipFile(StringIO.StringIO(schedule_zip.content))
    z.extractall("C:\Users\Phil\PycharmProjects\\alexa-metra\schedule")
    return


app = Flask(__name__)
ask = Ask(app, '/')

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://gtfsapi.metrarail.com/gtfs/raw/alerts.dat', auth=(accessKey, secretKey))
feed.ParseFromString(response.content)

update_schedule()

loader = transitfeed.Loader("C:\Users\Phil\PycharmProjects\\alexa-metra\schedule")
schedule = loader.Load()
for stop_id, stop in schedule.stops.items():
    print stop_id

@ask.intent('HelloIntent')
def hello(firstname):
    text = render_template('hello', firstname=firstname)
    return statement(text).simple_card('Hello', text)

if __name__ == '__main__':
    app.run()
