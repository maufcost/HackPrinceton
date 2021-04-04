# Import required modules for application logic
import time
import string
import random
import json
import base64
import random
from datetime import date
import requests as rq
import json

# Import required modules for Flask execution
from flask import Flask, render_template, request, redirect, make_response
from algoliasearch.search_client import SearchClient
# Google Cloud product modules
from google.auth.transport import requests
from google.cloud import datastore, storage
import google.oauth2.id_token

# Initialize objects to handle Authentication, database storage, and FLask
#firebase_request_adapter = requests.Request()
client = SearchClient.create('F6RT7CDBCJ', '47f93b306810243569f255b6c41b51a0')
index = client.init_index('vortex')
datastore_client = datastore.Client()
app = Flask(__name__)

####################{UTILITY FUNCTIONS BEGIN HERE}########################


# Generates a random string with specified length using lower and uppercase alphabet + digits
# default len is 6
def random_string_digits(string_len=6):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(string_len))

# def blobify(img_data):
#     img_blob = base64.b64decode(img_data)
#     return img_blob
#
# def upload_blob(file, destination_blob_name):
#
#     storage_client = storage.Client() # Opens a storage client
#     bucket = storage_client.bucket("vortex") #our bucket name
#     blob = bucket.blob(destination_blob_name)
#     blob.upload_from_string(file, content_type='image/png') #, content_type="image/png"

def create_event(name, desc, gifpic, uid):
    random_key = random_string_digits(10)
    complete_key = datastore_client.key('Event', random_key)
    task = datastore.Entity(key=complete_key)

    # Commented keys are for future features
    task.update({
        'name': name,
        'desc': desc,
        'eid' : random_key,
        'gifpic' : gifpic,
        'owner' : uid
    })

    datastore_client.put(task)
    return random_key

def create_video(vid, eventid, uid):
    complete_key = datastore_client.key('Moment', vid)
    task = datastore.Entity(key=complete_key)

    # Commented keys are for future features
    task.update({
        'eventid': eventid,
        'vid': vid,
        'uid' : uid
    })

    datastore_client.put(task)
    return vid

def get_all_videos_by_event_id(id):
    query = datastore_client.query(kind='Moment')
    query.add_filter('eventid', '=', id)
    results = list(query.fetch())
    return results

def get_event(eid):
    thekey = datastore_client.key('Event', eid) #Make a key with the email
    query = datastore_client.get(thekey)
    return query

def get_all_events():
    query = datastore_client.query(kind='Event')
    results = list(query.fetch())
    return results

def process_algolia_results(list_of_videos):
    frequency_dict = {}
    for each_video in list_of_videos:
        hits = index.search(each_video['vid'])['hits']
        for each_hit in hits:
            for each_label in each_hit['labels']:
                if not each_label in frequency_dict:
                    frequency_dict[each_label] = 1
                else:
                    frequency_dict[each_label] += 1
    res = sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True)
    return res

def process_label_and_ts():
    label_scores = process_algolia_results(all_moments)
    processed = {}
    for each_label_score in label_scores:
        if each_label_score[1] > 1:
            hits = index.search(each_label_score[0])['hits']
            for each_hit in hits:
                if not each_label_score in processed:
                    processed[each_label_score[0]] = [each_hit[each_label_score[0]]]
                else:
                    processed[each_label_score[0]].append(each_hit[each_label_score[0]])
    return processed

def cloud_video_generation(relevant):
    url = "https://api.veed.io/api/renders"
    cloud_video_gen_veed = {"params": {"dimensions":{"width":1920, "height":1080} }, "elements" : []}
    start = 0

    for each_pair in relevant:
        temp_element = {"type":"video", "params":{"source":{"url":each_pair['url']},"duration":{"from":start,"to":each_pair['off']}}}
        cloud_video_gen_veed["elements"].append(temp_element)

    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'key_test_OoZrG9upcHnWFbkv8YJkqVWn',
      'Cookie': 'GCLB=CMuM9Pn6vP3u_wE'
    }

    response = rq.request("POST", url, headers=headers, data=payload).json()

    return response

####################{SERVER FUNCTIONS BEGIN HERE}#########################
@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/join')
def join():
    if request.cookies.get('userID') != None:
        return redirect('/dash')
    return render_template('join.html')

@app.route('/create')
def create_page():
    return render_template('createEvent.html')

@app.route('/dash')
def dashboard_page():
    uname = request.cookies.get('userID')
    events = get_all_events()
    print(events)
    return render_template('dashboard.html', uname=uname, events=events)

@app.route('/event/<id>')
def event_page(id):
    event_details = get_event(id)
    all_moments = get_all_videos_by_event_id(id)
    print(all_moments)

    return render_template("event.html",event=event_details, id=id, moments=all_moments)

@app.route('/setcookie', methods = ['POST'])
def setcookie():
    user = request.form['nm']
    resp = make_response(redirect('/dash'))
    resp.set_cookie('userID', user)
    return resp

@app.route('/createEvent', methods=['POST'])
def create_event_upload():
    uploaded_file = request.files.get('file')
    name = request.form.get('name')
    desc = request.form.get('desc')
    uid = request.cookies.get('userID')

    if not uploaded_file:
        return 'No file uploaded.', 400

    pic_id = random_string_digits(10) + ".gif"
    gcs = storage.Client()
    bucket = gcs.get_bucket("vortexgif")
    blob = bucket.blob(pic_id)
    blob.upload_from_string(uploaded_file.read(),content_type=uploaded_file.content_type)
    eid = create_event(name, desc, pic_id, uid)

    return redirect('/event/'+eid)


@app.route('/upload', methods=['POST'])
def upload():

    uploaded_file = request.files.get('file')
    eventid = request.form.get('eventid')
    uid = request.cookies.get('userID')

    if not uploaded_file:
        return 'No file uploaded.', 400

    vid = random_string_digits(10)
    gcs = storage.Client()
    bucket = gcs.get_bucket("vortexvideo")
    blob = bucket.blob(vid)
    blob.upload_from_string(uploaded_file.read() ,content_type=uploaded_file.content_type)

    create_video(vid, eventid, uid)
    return redirect('/event/'+eventid)
####################{SERVER FUNCTIONS END HERE}#########################

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
