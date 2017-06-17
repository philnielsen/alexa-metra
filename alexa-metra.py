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
# feed = gtfs_realtime_pb2.FeedMessage()
# response = requests.get('https://gtfsapi.metrarail.com/gtfs/raw/alerts.dat', auth=(accessKey, secretKey))
# feed.ParseFromString(response.content)
# print(feed)

#loader = transitfeed.Loader("C:\Users\Phil\PycharmProjects\\alexa-metra\schedule")


@ask.intent('ReadInboundScheduleIntent',mapping={'stop_passed': 'Stop'})
def read_schedule(stop_passed):
    #Get from Metra the zipped schedule
    schedule_zip = requests.get('https://gtfsapi.metrarail.com/gtfs/raw/schedule.zip', auth=(accessKey, secretKey))
    z = zipfile.ZipFile(StringIO.StringIO(schedule_zip.content))
    loader = transitfeed.Loader(StringIO.StringIO(schedule_zip.content))
    schedule = loader.Load()
    print schedule
    # print schedule.GetTripList()
    #stop_times = schedule.stop()
    for trip_id, trip in schedule.trips.items():
        if trip.route_id == 'UP-NW' and trip.direction_id == '0' and trip.service_id == 'A1':
            print trip.trip_id
            stop_times =  trip.GetStopTimes()
            for stop in stop_times:
                if stop.stop_id == stop_passed.upper():
                    print stop.arrival_time
                    next_train_arrival = stop.arrival_time


        # if stop_times.stop_id == stop_passed.upper():
        #     print stop_times
    # for stop_id, stop in schedule.stops.items():
    #     if stop_id == stop_passed.upper():
    #         print stop
    statement_text = render_template('next_inbound',time=next_train_arrival,stop=stop_passed)
    return statement(statement_text).simple_card("Alexa Metra", statement_text)


@app.template_filter()
def humanize_time(dt):
    morning_threshold = 12
    afternoon_threshold = 17
    evening_threshold = 20
    hour_24 = dt.hour
    if hour_24 < morning_threshold:
        period_of_day = "in the morning"
    elif hour_24 < afternoon_threshold:
        period_of_day = "in the afternoon"
    elif hour_24 < evening_threshold:
        period_of_day = "in the evening"
    else:
        period_of_day = " at night"
    the_time = dt.strftime('%I:%M')
    formatted_time = "{} {}".format(the_time, period_of_day)
    return formatted_time

#read_schedule('Barrington')
if __name__ == '__main__':
    app.run()
