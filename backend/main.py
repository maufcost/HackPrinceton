# Import required modules for application logic
import time
import string
import random
import json
import base64
import random
from datetime import date

# Import required modules for Flask execution
from flask import Flask, render_template, request, redirect
#
# Google Cloud product modules
from google.auth.transport import requests
from google.cloud import datastore, storage
import google.oauth2.id_token

# Initialize objects to handle Authentication, database storage, and FLask
#firebase_request_adapter = requests.Request()
datastore_client = datastore.Client()
app = Flask(__name__)

####################{UTILITY FUNCTIONS BEGIN HERE}########################


# Generates a random string with specified length using lower and uppercase alphabet + digits
# default len is 6
def random_string_digits(string_len=6):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(string_len))

def blobify(img_data):
    img_blob = base64.b64decode(img_data)
    return img_blob

def upload_blob(file, destination_blob_name):

    storage_client = storage.Client() # Opens a storage client
    bucket = storage_client.bucket("vortex") #our bucket name
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(file, content_type='image/png') #, content_type="image/png"

####################{SERVER FUNCTIONS BEGIN HERE}#########################

@app.route('/')
def main():
    return render_template('landing.html')

####################{SERVER FUNCTIONS END HERE}#########################

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)