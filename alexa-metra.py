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
import boto3
import os
import aniso8601
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

def update_local_schedule():
    schedule_zip = requests.get('https://gtfsapi.metrarail.com/gtfs/raw/schedule.zip', auth=(accessKey, secretKey))
    z = zipfile.ZipFile(StringIO.StringIO(schedule_zip.content))
    z.extractall("C:\Users\Phil\PycharmProjects\\alexa-metra\schedule")
    return

@ask.launch
def launch():
    welcome_text = render_template('welcome')
    return question(welcome_text)


#update_local_schedule()
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://gtfsapi.metrarail.com/gtfs/raw/alerts.dat', auth=(accessKey, secretKey))
feed.ParseFromString(response.content)
print(feed)

#loader = transitfeed.Loader("C:\Users\Phil\PycharmProjects\\alexa-metra\schedule")



@ask.intent('ReadInboundScheduleIntent')
def read_schedule():
    loader = transitfeed.Loader("https://s3.amazonaws.com/metra-gtfs-data")
    schedule = loader.Load()
    for stop_id, stop in schedule.stops.items():
        print stop_id


if __name__ == '__main__':
    app.run()
