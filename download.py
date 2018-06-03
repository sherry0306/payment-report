from __future__ import print_function
import httplib2
import os
import argparse
from datetime import datetime, timedelta
from dateutil.parser import parse

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from attachment import save
import convert

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python'
USER_ID = 'me'

def get_credentials():
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
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def search_all(service):
    query_str = "subject:\"%s\"" % ("ReportServer: DailyOrderbyStripe_andALL")
    print("Searching... by keyword: '%s'" % query_str)
    results = service.users().messages().list(userId = USER_ID, q = query_str).execute()
    messages = results.get('messages', [])
    return messages

def search_by_date(service, date=datetime.now()):
    query_str = "subject:\"%s\" filename:%s" % ("ReportServer: DailyOrderbyStripe_andALL", date.strftime("%d.%m.%Y"))
    print("Searching... by keyword: '%s'" % query_str)
    results = service.users().messages().list(userId = USER_ID, q = query_str).execute()
    messages = results.get('messages', [])
    return messages

def search_after_date(service, date=datetime.now()):
    query_str = "subject:\"%s\" after:%s" % ("ReportServer: DailyOrderbyStripe_andALL", date.strftime("%Y/%m/%d"))
    print("Searching... by keyword: '%s'" % query_str)
    results = service.users().messages().list(userId = USER_ID, q = query_str).execute()
    messages = results.get('messages', [])
    return messages

def fetch_attachments(service, msgId):
    content = service.users().messages().get(userId = USER_ID, id = msgId).execute()
    attachments = []
    for part in content['payload']['parts']:
        attachments.extend(p for p in part['parts'] if 'attachmentId' in p['body'].keys())
        # print('filename: %s, attachment id: %s' % (p['filename'], p['body']['attachmentId']))
    return attachments

def download():
    pass

def parse_args():
    parser = argparse.ArgumentParser(description='Gmail Report Downloader')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--all", action="store_true")
    group.add_argument("-d", "--date", metavar='<DATE>', type=str, default=0,
                        help='Sepecified date. If this option is omitted, the date will be Today.')
    return parser.parse_args()

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    args = parse_args()
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    messages = []
    if args.all:
        print("Download all reports...")
        messages = search_all(service)

    elif args.date:
        d = parse(args.date)
        print("Download for %s" % d.strftime('%d.%m.%Y'))
        messages = search_by_date(service, d)

    else:
        res = convert.last_update()
        if res:
            _, _, date = res
            oneday = timedelta(days = 1)
            print("Checking latest download...%s" % date)
            messages = search_after_date(service, date + oneday)
        else:
            print("No records now, fallback to donwload Today's report")
            messages = search_by_date(service)

    if not messages:
        print('No messages found.')
    else:
        print("%d messages found." % len(messages))
        
        convert.clean_files('./')

        for message in messages:
            msg_id = message['id']
            for att in fetch_attachments(service, msg_id):
                print('Checking attachment: %s' % att['filename'])
                if convert.is_file_exists(att['filename']):
                    print('Attachment records exists! Skip...')
                else:
                    print('Saving file: %s' % att['filename'])
                    save(service, msg_id, att['body']['attachmentId'], './', att['filename'])
        print('Convert to DB...')
        convert.write_to_db('./')
        convert.clean_files('./')

        print('\n\n Done! Bye~')
        
if __name__ == '__main__':
    main()
