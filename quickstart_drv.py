from __future__ import print_function
import httplib2
import os

import requests

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import httplib2

import googleapiclient

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_creds():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)


def getFolders():
    credentials = get_creds()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(fields="nextPageToken, files(id, name, parents, mimeType, description)", pageSize=1000).execute()
    items = results.get('files', [])
    
    folders = {}
    if items:
        for item in items:
            if item[u'mimeType'] == u'application/vnd.google-apps.folder':
                folders[item[u'name']] = {}
                for afile in items:
                    if u'parents' in afile:
                        if item[u'id'] in afile[u'parents']:
                            if u'description' in afile.keys():
                                folders[item[u'name']][afile[u'name']] = {"file_id": afile[u'id'], "tags": afile[u'description'].split(';')}
                            else:
                                folders[item[u'name']][afile[u'name']] = {"file_id": afile[u'id'], "tags": []}
    return folders


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_creds()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(fields="nextPageToken, files(id, name)").execute()
    test = service.files().export(fileId=str(results['files'][0]['id']), mimeType= "application/vnd.google-apps.<app>")
    #download_file_from_google_drive(str(results['files'][0]['id']),"pony.txt")


    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print(getFolders().keys())

if __name__ == '__main__':
    main()
