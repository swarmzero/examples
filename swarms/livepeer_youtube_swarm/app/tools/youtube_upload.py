import http.client
import httplib2
import os
import random
import sys
import time
import pickle
import logging
from typing import Optional, List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
from http.client import NotConnected, IncompleteRead, ImproperConnectionState, \
    CannotSendRequest, CannotSendHeader, ResponseNotReady, BadStatusLine

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, NotConnected,
                        IncompleteRead, ImproperConnectionState,
                        CannotSendRequest, CannotSendHeader,
                        ResponseNotReady, BadStatusLine)

# Always retry when a googleapiclient.errors.HttpError with one of these status codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# This OAuth 2.0 access scope allows an application to upload files to the authenticated user's YouTube channel.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def upload_video(
    file: str,
    title: str,
    description: str,
    category: str = "22",
    keywords: Optional[str] = "",
    privacyStatus: str = "unlisted",
    client_secrets_file: str = "client_secret.json",
    credentials_file: str = "token.pickle"
) -> None:
    """
    Uploads a video file to YouTube.

    Args:
        file (str): Path to the video file to upload.
        title (str): Video title.
        description (str): Video description.
        keywords (str): Comma-separated list of video keywords.
    """
    if not os.path.exists(file):
        raise FileNotFoundError(f"Please specify a valid file. '{file}' does not exist.")

    youtube = get_authenticated_service(client_secrets_file, credentials_file)

    tags = None
    if keywords:
        tags = keywords.split(",")

    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category
        ),
        status=dict(
            privacyStatus=privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def get_authenticated_service(client_secrets_file: str, credentials_file: str):
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as token:
            credentials = pickle.load(token)
    # If there are no valid credentials, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"Missing client_secrets.json file: {client_secrets_file}")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes=[YOUTUBE_UPLOAD_SCOPE])
            
            credentials = flow.run_local_server(
                    host='localhost',
                    port=8088,
                    authorization_prompt_message='Please visit this URL: {url}',
                    success_message='The auth flow is complete; you may close this window.',
                    open_browser=True)
        # Save the credentials for the next run.
        with open(credentials_file, 'wb') as token:
            pickle.dump(credentials, token)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." %
                          response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
