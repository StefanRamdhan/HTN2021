# uses python3

import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.signal import savgol_filter

from datetime import datetime, timedelta
from datetime import date

from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json

app = Flask(__name__, static_url_path='')

covidInfoLoc = ''
db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    return app.send_static_file('index.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */

@app.route('/api/calculator, methods=['GET'])
def calcRisk():

    # https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask
    means_of_transport = request.args.get('transport')  # if key doesn't exist, returns None
    city = request.args.get('city')  # if key doesn't exist, returns None
    var1 = request.args.get('var1')  # if key doesn't exist, returns None
    var2 = request.args.get('var2')  # if key doesn't exist, returns None
    var3 = request.args.get('var3')  # if key doesn't exist, returns None
    var4 = request.args.get('var4')  # if key doesn't exist, returns None

    if client:
        data = {
            'transport': means_of_transport,
            'city': city,
            'var1': var1,
            'var2': var2,
            'var3': var3,
            'var4': var4
        }
        my_document = db.create_document(data)
    else:
        print('No database')
        return jsonify(data)

# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */

@app.route('/api/visualize', methods=['GET'])
def visualize():
    user = request.json['name']



@app.route('/api/history, methods=['GET'])
def printHistory():
    if client:
        return jsonify(list(map(lambda doc: doc['name'], db)))
    else:
        print('No database')
        return jsonify([])

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)


