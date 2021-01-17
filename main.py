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
from cloudant import query
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json

app = Flask(__name__, static_url_path='')

covidInfoURL = 'https://raw.githubusercontent.com/ShenPaul/HTN2021/main/conposcovidloc.csv'
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

df = pd.read_csv('conposcovidloc.csv') #change to covidInfoURL

# Converting the column to a data format:
df['Accurate_Episode_Date'] =  pd.to_datetime(df['Accurate_Episode_Date'])

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

    calculatedRisk = output_trends(df, city, var1, var2)

    return jsonify(
        population = calculatedRisk[0],
        num = calculatedRisk[1],
        sick = calculatedRisk[2],
        num_fatal = calculatedRisk[3],
        num_resolved = calculatedRisk[4],
        num_sick_past = calculatedRisk[5],
        num_not_resolved = calculatedRisk[6],
        risk_factor = calculatedRisk[7]
    )




@app.route('/api/visualize', methods=['GET'])
def visualize():

    #not really sure what we want to put here, probably get some data from a method and output that to the frontend
    #matplotlib code from Stefan
    # # plotting cases per day and Line of Best Fit
    # plt.plot(out.index, out.to_numpy())
    # # plt.plot(out.index, out.to_numpy())
    # plt.plot(out.index, [model.coef_ * x + model.intercept_ for x in range(len(out.to_numpy()))])
    # plt.xticks(np.arange(0, 60, step=10))  # Set label locations.
    # plt.xticks(rotation=45)
    # plt.title(f"{city} - {prediction[city]} - {model.coef_}")
    # plt.show()
    user = request.json['name']


# /**
#  * Endpoint to get a JSON array of all the query history in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */
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

#%-------------------------------------------------------------------------------------------%

def output_trends(dataframe=df,
                  city='Toronto',
#                   case_resolution='Resolved',
                  trend_data=60,
                  days_omitted=8):
    '''
    city -- one of the population_dict cities
    case_resolution - "Resolved", "Not Resolved", "Fatal"
    trend_data - how many days
    days_omitted - how many days do we skip (from today)
    '''

    data = df.copy()

    # Days:

    end_date = date.today() - timedelta(days=days_omitted)
    start_date = date.today() - timedelta(days=trend_data+days_omitted)

    # Considering only specified range of dates:
    df_current = data[data["Accurate_Episode_Date"].isin(
        pd.date_range(start_date, end_date))]

    # Output df:
    df_out = df_current[df_current['Reporting_PHU_City'] == city]
    out = df_out.groupby('Accurate_Episode_Date').nunique()
    out = out.sort_values(by=['Accurate_Episode_Date'])['Row_ID']

    #Linear Regression
    value = out.to_numpy()
    X = np.array(list(range(len(value)))).reshape(-1, 1)
    model = LinearRegression().fit(X, value)
    prediction = "INCR" if model.coef_ > 0 else "DECR"

    #Dates:
    dates = out.index
    #Values:
    values = savgol_filter(out.to_numpy(), 7,2)
    #Linear regression predictions:
    lin_reg_pred = [model.coef_*x + model.intercept_ for x in range(len(value))]

    return dates, values, lin_reg_pred, model.coef_

def how_many(dataframe=df,
             city='Toronto',
             trend_data=30,
             case_resolution='Resolved',
             means_of_transport = 'Bus',
             days_omitted=0):
    '''
    means_of_transport = 'Bus'+10%, 'Flight'+15%, 'Car'+0%
    '''

    #this has been stored in the cloud already
    # population_dict = {
    #     'Windsor': 336000,
    #     'Barrie': 145614,
    #     'Port Hope': 16753,
    #     'London': 5454141,
    #     'Toronto': 2731571,
    #     'Hamilton': 767000,
    #     'Whitby': 128377,
    #     'Thorold': 21663,
    #     'Newmarket': 90000,
    #     'Cornwall': 46589,
    #     'Oakville': 193832,
    #     'Kingston': 590940,
    #     'Point Edward': 2037,
    #     'Ottawa': 934243,
    #     'Mississauga': 733083,
    #     'Waterloo': 562000,
    #     'Guelph': 120545,
    #     'Stratford': 31500,
    #     'St. Thomas': 38909,
    #     'Chatham': 103700,
    #     'Simcoe': 13922,
    #     'Brantford': 115000,
    #     'Thunder Bay': 121621,
    #     'New Liskeard': 4402,
    #     'Brockville': 21900,
    #     'Peterborough': 202259,
    #     'Timmins': 41788,
    #     'North Bay': 51027,
    #     'Sudbury': 161531,
    #     'Belleville': 50716,
    #     'Pembroke': 15260,
    #     'Sault Ste. Marie': 75528,
    #     'Owen Sound': 21341,
    #     'Kenora': 15696}

    populationQuery = cloudant.query.Querty (client['population'], selector={'cityField':city})

    for doc in populationQuery:
        #need to get the population size and assign it here
        population = doc ['populationField']

    data = df.copy()

    out = data[data['Reporting_PHU_City'] == city]
    out.keys()

    # Fatal:
    out_fatal = out[out['Outcome1'] == 'Fatal']
    out_fatal = out_fatal.groupby('Accurate_Episode_Date').nunique()
    num_fatal = np.sum(out_fatal['Row_ID'].to_numpy())

    # Resolved:
    out_resolved = out[out['Outcome1'] == 'Resolved']
    out_resolved = out_resolved.groupby('Accurate_Episode_Date').nunique()
    num_resolved = np.sum(out_resolved['Row_ID'].to_numpy())

    # Not Resolved:
    out_not_resolved = out[out['Outcome1'] == 'Not Resolved']
    out_not_resolved = out_not_resolved.groupby(
        'Accurate_Episode_Date').nunique()
    num_not_resolved = np.sum(out_not_resolved['Row_ID'].to_numpy())

    # Got COVID total:
    out = out.groupby('Accurate_Episode_Date').nunique()
    num_sick = np.sum(out['Row_ID'].to_numpy())

    # ---------------------------------------------------------------
    # Days:
    end_date = date.today() - timedelta(days=days_omitted)
    start_date = date.today() - timedelta(days=trend_data+days_omitted)

    # Considering only specified range of dates:
    df_current = data[data["Accurate_Episode_Date"].isin(
        pd.date_range(start_date, end_date))]

    # Output df:
    df_out = df_current[df_current['Reporting_PHU_City'] == city]

    out1 = df_out.groupby('Accurate_Episode_Date').nunique()
    num_sick_past = np.sum(out1['Row_ID'].to_numpy())


    _, _, _, coef = output_trends(city = city)

    # Risk factor:
    risk_factor = 100*(num_not_resolved*np.power(population, 1/3)+coef[0]*30000)/(1.8*(population))

    if risk_factor >= 100:
        risk_factor = 99.99
    elif risk_factor <= 0:
        risk_factor = 1.00
    #     risk_factor = 100*(num_not_resolved*np.power(population_dict[city], 1/3))/(1.8*(population_dict[city]))

    if means_of_transport == 'Bus':
        risk_factor+=10
        if risk_factor >= 100:
            risk_factor = 99.99
    elif means_of_transport == 'Flight':
        risk_factor+=15
        if risk_factor >= 100:
            risk_factor = 99.99



    # Print info:

    print("Destination:\t\t\t\t{}".format(city))
    print("{} population:\t\t\t{:,}".format(city, population))
    print("Total number of cases:\t\t\t{:,}".format(num_sick))
    print("Total number of fatal cases:\t\t{:,}".format(num_fatal))
    print("Total number of resolved cases:\t\t{:,}".format(num_resolved))
    print("Cases for the past {} days:\t\t{:,}".format(
        trend_data, num_sick_past))
    print(
        "Total number of non-resolved cases:\t{:,}".format(num_not_resolved))
    print("Risk factor:\t\t\t\t{:.2f}%".format(risk_factor))

    return population, num_sick, num_fatal, num_resolved, num_sick_past, num_not_resolved, risk_factor