from flask import Flask, Response, json, render_template
import json
from flask import request
import requests
from datetime import datetime
from datetime import timedelta, date, time
import time
from urllib.request import urlopen
from json2html import *


app = Flask(__name__)

def get_current_pose():
    response = requests.get('https://api.wheretheiss.at/v1/satellites/25544')
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location')
def location():
    getdate = request.args.get('Date')
    gettime = request.args.get('Time')
    LatestTime = datetime.strptime(gettime, '%H:%M')
    ConvertTime = LatestTime.time()
    CurrentTime = datetime.combine(date.min, ConvertTime)-datetime.min
    timedeltaobj = timedelta(hours=2)
    StartTime = CurrentTime - timedeltaobj
    TimeinEpoch = []
    NewStartTime = []

    while StartTime < CurrentTime:
        StartTime = StartTime + timedelta(minutes=10)
        NewStartTime.append(str(StartTime))
        t = time.mktime(time.strptime(getdate + " " + str(StartTime), "%Y-%m-%d %H:%M:%S"))
        TimeinEpoch.append(int(t))

    strTimeinEpoch = list(map(str, TimeinEpoch))
    FinalTimeinEpoch = ','.join(strTimeinEpoch)
    url = "https://api.wheretheiss.at/v1/satellites/25544/positions?timestamps=" + FinalTimeinEpoch + "&units=miles"
    response = urlopen(url)
    data_json = json.loads(response.read())

    url_people = "http://api.open-notify.org/astros.json"
    response_people = urlopen(url_people)
    data_json_people = json.loads(response_people.read())

    return render_template('location.html', Date1=datetime.strptime(getdate, '%Y-%m-%d').date(),
                           Time1=gettime, NewStartTime=list(NewStartTime),
                           listTime = FinalTimeinEpoch.split(','),
                           people=json2html.convert(json=data_json_people),
                           url = url, test=json2html.convert(json=data_json),
                           initial_pose=get_current_pose())

@app.route('/api/pose')
def pose_stream():

    def __generate__(delay=1.0):
        while True:
            response = get_current_pose()
            response = json.dumps(response)
            yield f"data:{response}\n\n"
            time.sleep(delay)

    return Response(__generate__(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug = False)