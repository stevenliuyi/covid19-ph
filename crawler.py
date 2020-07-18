import pickle
import os.path
import io
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

region_data_files = os.listdir('./regions')

root_folder_id = '1w_O-vweBFbqCgzgmCpux2F0HVB4P6ni2'

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('drive', 'v3', credentials=creds)

results = service.files().list(
    q="'" + root_folder_id + "' in parents",
    fields="nextPageToken, files(id, name, modifiedTime)").execute()
month_folders = results.get('files', [])

# sort by modified date
# month_folders = sorted(month_folders, key=lambda item: item['modifiedTime'])
# curr_month_folder = month_folders[-1]
for curr_month_folder in month_folders:
    #print(u'{0} ({1})'.format(curr_month_folder['name'], curr_month_folder['id']))

    results = service.files().list(
        q="'" + curr_month_folder['id'] + "' in parents",
        fields="nextPageToken, files(id, name, modifiedTime)").execute()
    day_folders = results.get('files', [])

    #day_folders = sorted(day_folders, key=lambda item: item['modifiedTime'])
    #curr_day_folder = day_folders[-1]

    for curr_day_folder in day_folders:
        #print(u'{0} ({1})'.format(curr_day_folder['name'], curr_day_folder['id']))

        date_match = re.search('(20\d{2})(\d{2})(\d{2})',
                               curr_day_folder['name'])
        date = f'{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}'

        if (f'{date}.csv' in region_data_files):
            print(f'{date} - Data existed!')
            continue

        query = u"name contains '{0}' and name contains '{1}' and '{2}' in parents".format(
            'Case Information', 'csv', curr_day_folder['id'])
        results = service.files().list(
            q=query, fields="nextPageToken, files(id, name)").execute()
        curr_data_file = results.get('files', [])

        if (len(curr_data_file) == 0):
            print(f'{date} - Cannot find case information!')
            continue

        curr_data_file = curr_data_file[0]
        #print(u'{0} ({1})'.format(curr_data_file['name'], curr_data_file['id']))

        # download data file
        request = service.files().get_media(fileId=curr_data_file['id'])
        fh = io.FileIO(f'{date}.csv', 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            #print("Download %d%%." % int(status.progress() * 100))
        print(f'{date} - Downloaded!')