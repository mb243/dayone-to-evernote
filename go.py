#!/usr/bin/env python3

from evernote.api.client import EvernoteClient, Store
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

from time import time
import json

from datetime import datetime

import markdown
import webbrowser
import urllib.parse

# The follow two lines are a workaround to supress the following error message:
# ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
#

# https://dev.evernote.com/doc/articles/authentication.php
# https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#web-application-flow
authorization_base_url = 'https://sandbox.evernote.com/oauth'
client_id = ''
client_secret = ''
callback_url = 'localhost'
token_url = 'https://sandbox.evernote.com/oauth'
use_sandbox = True


json_path = ''  # path to unzipped contents
journal_json = json_path + '/Journal.json'  # full path to Journal.json


def create_notebook(note_store: Store, notebook_name: str) -> str:
    notebook = Types.Notebook()
    notebook.name = notebook_name
    notebook = note_store.createNotebook(notebook)
    return notebook.guid


def create_note(note_store: Store, note_title: str, note_content: str, 
        notebook_guid: str = "", time_created: int = 0, time_updated: int = 0) -> Types.Note:
    note = Types.Note()
    note.notebookGuid = notebook_guid
    note.title = note_title

    # Timestamps are epoch milliseconds as int
    if not time_created:
        time_created = int(time()*1000)
    if not time_updated:
        time_updated = int(time()*1000)
    note.created = time_created
    note.updated = time_updated

    # Insert required wrapping around the note content
    header = '<?xml version="1.0" encoding="UTF-8"?>'
    header += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    header += '<en-note>'
    footer = '</en-note>'

    note.content = header + note_content + footer

    try:
        note = note_store.createNote(note)
    except Errors.EDAMUserException as edue:
        print("EDAMUserException: " + edue)
    except Errors.EDAMNotFoundException:
        print("EDAMNotFoundException: Invalid parent notebook GUID")

    return note


def get_client_by_dev_token(dev_token: str) -> EvernoteClient:
    client = EvernoteClient(token=dev_token)
    return client

def get_client_by_access_token(access_token: str, use_sandbox: bool) -> EvernoteClient:
    # https://stackoverflow.com/questions/41710896/getuser-return-edamsystemexception-errorcode-8
    client = EvernoteClient(token=access_token, sandbox=use_sandbox)
    return client

def get_oauth_client(client_id: str, client_secret: str, use_sandbox: bool) -> str:
    client = EvernoteClient(
        consumer_key = client_id, 
        consumer_secret = client_secret,
        sandbox=use_sandbox
    )
    request_token = client.get_request_token('localhost')
    url = client.get_authorize_url(request_token)
    print("Opening a web browser to the following URL to approve access:")
    print(url)
    webbrowser.open(url, new=1, autoraise=True)
    authorization_response = input('\nOnce approved, enter the full callback URL here: ')
    parsed_url = urllib.parse.urlparse(authorization_response)
    oauth_verifier = urllib.parse.parse_qs(parsed_url.query)["oauth_verifier"][0]
    access_token = client.get_access_token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'],
        oauth_verifier
    )
    return access_token

# Comment out the following line if using a production dev token
access_token = get_oauth_client(client_id, client_secret, use_sandbox)
# print(access_token)

client = get_client_by_access_token(access_token, use_sandbox)

userStore = client.get_user_store()
# user = userStore.getUser()
# print("Logged in as: " + user.username)

noteStore = client.get_note_store()
noteStore.listNotebooks()

notebook_guid = create_notebook(noteStore, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

with open(journal_json, 'r') as journal_file:
    data = json.load(journal_file)

for entry in data["entries"]:
    if "text" in entry:  # skip over empty entries
        entry_uuid = entry["uuid"]
        entry_text = entry["text"]
        entry_html = markdown.markdown(entry_text, extensions=['fenced_code'])
        entry_text = entry_text.replace('\\', '')  # strip out unneeded backslashes
        #   "creationDate" : "2018-06-06T16:00:00Z"
        entry_time = int(datetime.strptime(entry["creationDate"], '%Y-%m-%dT%H:%M:%S%z').timestamp() * 1000)

        first_line = entry_html.partition('\n')[0]

        if "<h1>" in first_line:  # If the first line is a formatted title, use it as the title line and remove it from the body
            title = first_line.replace('<h1>', '').replace('</h1>', '')
            entry_html = '\n'.join(entry_html.split('\n')[1:])
        else:  # Title it literally 'Untitled'
            title = 'Untitled'

        print("UUID: " + entry_uuid)
        print("Timestamp: " + str(entry_time))
        print("title: " + str(title))

        note = create_note(noteStore, title, entry_html, notebook_guid, entry_time, entry_time)
        print("Note created.")
