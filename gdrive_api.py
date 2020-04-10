#!/bin/env python3

from __future__ import print_function
import os.path
import pickle

from datetime import date, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file gdrive_token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def authorize():
    creds = None
    # The file gdrive_token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gdrive_token.pickle'):
        with open('gdrive_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gdrive_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gdrive_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service


def find_file(service, file_name, parent_id):
    page_token = None

    while True:
        response = service.files().list(
            q="name='{0}' and trashed=false and parents in '{1}'".format(
                file_name, parent_id
            ),
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        files = response.get('files', [])

        page_token = response.get('nextPageToken', None)

        if page_token is None:
            return files


def delete_file(service, file_name, parent_id):
    files = find_file(service, file_name, parent_id)

    for file in files:
        service.files().delete(fileId=file.get('id')).execute()

        print('Deleted file: {0} ({1})'.format(
            file.get('name'), file.get('id')
        ))


def upload_file(service, file, parent_id, overwrite=True):
    file_name = os.path.basename(file)

    if overwrite:
        delete_file(service, file_name, parent_id)

    mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    file_metadata = {
        'name': file_name,
        'mimeType': mimeType,
        'parents': [parent_id]
    }

    media = MediaFileUpload(
        file,
        mimetype=mimeType,
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print('Created file: {0} ({1})'.format(file_name, file.get('id')))


def move_file(service, file_name, parent_id, new_parent_id, new_name=None):
    file_id = find_file(service, file_name, parent_id)[0].get('id')
    name = new_name if new_name else file_name

    file_metadata = {
        'name': name
    }

    file = service.files().update(
            fileId=file_id,
            body=file_metadata,
            removeParents=parent_id,
            addParents=new_parent_id,
            fields='id'
    ).execute()

    print('Moved file: {0} to {1} ({2})'.format(
        file_name, name, file.get('id')
    ))


def rename_file(service, file_name, parent_id, new_name):
    file_id = find_file(service, file_name, parent_id)[0].get('id')

    file_metadata = {
        'name': new_name
    }

    file = service.files().update(
        fileId=file_id,
        body=file_metadata,
        fields='id'
    ).execute()

    print('Renamed file: {0} to {1} ({2})'.format(
        file_name, new_name, file.get('id')
    ))


def main():
    parents = {
        'ecdc-csv': '13i1_K7xUvoJMdqJuGMn116PntIZhsgmh',
        'ecdc-csv-archived': '1Kxmr4d5WWbP_V-rIpH4epCeChPrWTSh-',
        'jhu-gis': '1pWEZAcikghLrdDQCyrjU2uVGXD23n8pq',
        'jhu-gis-daily-totals': '1hf3huNWlJbOfoi3phBw5-1wouSLwA49N',
        'worldometer': '1iru7TCaW-cdKwugnPqtzEFsfIOhkIC5_'
    }

    service = authorize()

    today = date.today().strftime('%Y-%m-%d')
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # ecdc-csv data update

    ecdc_csv_files = [
        'ecdc_csv_total.xlsx',
        'ecdc_csv_diff.xlsx'
    ]

    for file_name in ecdc_csv_files:
        move_file(
            service,
            file_name,
            parents['ecdc-csv'],
            parents['ecdc-csv-archived'],
            '{0}_{1}'.format(yesterday, file_name)
        )

        upload_file(
            service,
            'ecdc_csv/data/{0}'.format(file_name),
            parents['ecdc-csv']
        )

    # jhu-gis data update

    jhu_gis_files = [
        'jhu_gis_total.xlsx',
        'jhu_gis_diff.xlsx'
    ]

    for file_name in jhu_gis_files:
        upload_file(
            service,
            'jhu_gis/data/{0}'.format(file_name),
            parents['jhu-gis']
        )

    jhu_gis_daily_total_file = '{0}_jhu_gis_total.xlsx'.format(today)

    upload_file(
        service,
        'jhu_gis/data/daily_totals/{0}'.format(jhu_gis_daily_total_file),
        parents['jhu-gis-daily-totals']
    )

    # worldometer data update

    worldometer_file = '{0}_worldometer_covid.xlsx'.format(yesterday)

    upload_file(
        service,
        'worldometer/data/{0}'.format(worldometer_file),
        parents['worldometer']
    )


if __name__ == '__main__':
    main()
