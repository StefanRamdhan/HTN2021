#https://cloud.ibm.com/docs/Cloudant?topic=Cloudant-creating-and-populating-a-simple-ibm-cloudant-database-on-ibm-cloud
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import os
import json

client = None

population_dict = {
        'Windsor': 336000,
        'Barrie': 145614,
        'Port Hope': 16753,
        'London': 5454141,
        'Toronto': 2731571,
        'Hamilton': 767000,
        'Whitby': 128377,
        'Thorold': 21663,
        'Newmarket': 90000,
        'Cornwall': 46589,
        'Oakville': 193832,
        'Kingston': 590940,
        'Point Edward': 2037,
        'Ottawa': 934243,
        'Mississauga': 733083,
        'Waterloo': 562000,
        'Guelph': 120545,
        'Stratford': 31500,
        'St. Thomas': 38909,
        'Chatham': 103700,
        'Simcoe': 13922,
        'Brantford': 115000,
        'Thunder Bay': 121621,
        'New Liskeard': 4402,
        'Brockville': 21900,
        'Peterborough': 202259,
        'Timmins': 41788,
        'North Bay': 51027,
        'Sudbury': 161531,
        'Belleville': 50716,
        'Pembroke': 15260,
        'Sault Ste. Marie': 75528,
        'Owen Sound': 21341,
        'Kenora': 15696}

def main():
    with open('dbuploadcred.json') as f:
        creds = json.load(f)

    serviceUsername = creds['username']
    servicePassword = creds['password']
    serviceURL = creds['url']

    client = Cloudant(serviceUsername, servicePassword, url=serviceURL)
    client.connect()

    databaseName = "population"

    popDatabase = client.create_database(databaseName)

    if popDatabase.exists():
        print("'{0}' successfully created.\n".format(databaseName))



    # Retrieve the fields in each row.
    for key in population_dict:
        city_name = key
        popSize = population_dict[key]

        #  Create a JSON document that represents all the data in the row.
        jsonDocument = {
            "cityField": city_name,
            "populationField": popSize,
        }

        # Create a document by using the Database API.
        newDocument = popDatabase.create_document(jsonDocument)

        # Check that the documents exist in the database.
        if newDocument.exists():
            print("Document successfully created.")

if __name__=='__main__':
    main()