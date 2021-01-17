#https://cloud.ibm.com/docs/Cloudant?topic=Cloudant-creating-and-populating-a-simple-ibm-cloudant-database-on-ibm-cloud
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import os
import json

client = None

def main():
    with open('dbuploadcred.json') as f:
        creds = json.load(f)

    serviceUsername = creds['username']
    servicePassword = creds['password']
    serviceURL = creds['url']

    client = Cloudant(serviceUsername, servicePassword, url=serviceURL)
    client.connect()

    databaseName = "coviddb"

    covidDatabase = client.create_database(databaseName)

    if covidDatabase.exists():
        print("'{0}' successfully created.\n".format(databaseName))

    with open('covidInfo.json') as g:
        covid = json.load(g)

    # Retrieve the fields in each row.
    for document in covid:

        # Create a document by using the Database API.
        newDocument = covidDatabase.create_document(document)

        # Check that the documents exist in the database.
        if newDocument.exists():
            print("Document successfully created.")

if __name__=='__main__':
    main()