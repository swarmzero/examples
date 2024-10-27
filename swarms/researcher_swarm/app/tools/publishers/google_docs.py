import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

def publish_to_google_docs(title: str, results_text: str) -> str:
    """
    Publishes results to a new Google Docs document.

    Args:
        title (str): The title of the Google Docs document.
        results_text (str): The content to be published in the document.

    Returns:
        str: The URL of the created Google Docs document.

    Raises:
        FileNotFoundError: If the Google credentials file is missing.
        Exception: If an error occurs during the publishing process.
    """

    GOOGLE_SCOPES = os.getenv(
        "GOOGLE_SCOPES",
        "https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/drive.file",
    ).split()
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"
    )
    token_path = "token.json"

    creds = None
    if os.path.exists(token_path):
        logger.debug("Loading existing credentials from token file")
        creds = Credentials.from_authorized_user_file(token_path, GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
                logger.error(f"Credentials file '{GOOGLE_APPLICATION_CREDENTIALS}' not found")
                raise FileNotFoundError(
                    f"Missing '{GOOGLE_APPLICATION_CREDENTIALS}' file."
                )
            logger.info("Initiating OAuth2 flow for new credentials")
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        logger.debug("Saving new credentials to token file")
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        logger.info("Initializing Google Docs service")
        docs_service = build("docs", "v1", credentials=creds)
        
        logger.info(f'Creating new document with title: "{title}"')
        doc = docs_service.documents().create(body={"title": title}).execute()
        document_id = doc.get("documentId")
        document_url = f"https://docs.google.com/document/d/{document_id}/edit"
        logger.info(f'Document created successfully with ID: {document_id}')

        requests_batch = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": f"{title}\n\n{results_text}"
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": 1,
                        "endIndex": len(title) + 1
                    },
                    "paragraphStyle": {
                        "namedStyleType": "HEADING_1"
                    },
                    "fields": "namedStyleType"
                }
            }
        ]

        logger.debug("Updating document with content")
        docs_service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests_batch}
        ).execute()

        logger.info("Content successfully published to Google Docs")
        return document_url

    except Exception as e:
        logger.error(f"Failed to publish document: {str(e)}", exc_info=True)
        return None
