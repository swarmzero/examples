import json
import os
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def publish_to_confluence(title: str, results_text: str) -> str:
    """
    Publishes results to Confluence by creating or updating a page.

    Args:
        title (str): The title of the Confluence page.
        results_text (str): The content to be published on the page.

    Returns:
        str: The URL of the created or updated Confluence page.

    Raises:
        Exception: If an error occurs during the publishing process.
    """

    CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL").rstrip('/')
    if not CONFLUENCE_BASE_URL.endswith('/wiki'):
        CONFLUENCE_BASE_URL = f"{CONFLUENCE_BASE_URL}/wiki"
        
    CONFLUENCE_API_ENDPOINT = f"{CONFLUENCE_BASE_URL}/rest/api/content/"
    CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
    CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
    CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
    CONFLUENCE_PARENT_PAGE_ID = os.getenv("CONFLUENCE_PARENT_PAGE_ID")  # optional

    try:
        # search for existing page
        search_params = {
            "title": title,
            "spaceKey": CONFLUENCE_SPACE_KEY,
            "expand": "version"
        }
        
        search_response = requests.get(
            CONFLUENCE_API_ENDPOINT,
            params=search_params,
            auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
        )
        
        # log response for debugging
        logger.debug(f"Search response status: {search_response.status_code}")
        logger.debug(f"Search response text: {search_response.text}")

        if search_response.status_code == 200:
            search_data = search_response.json()
            
            # update existing page
            if search_data.get("size", 0) > 0:
                page = search_data["results"][0]
                page_id = page["id"]
                version = page["version"]["number"]

                update_data = {
                    "id": page_id,
                    "type": "page",
                    "title": title,
                    "space": {"key": CONFLUENCE_SPACE_KEY},
                    "body": {
                        "storage": {
                            "value": results_text,
                            "representation": "storage"
                        }
                    },
                    "version": {"number": version + 1}
                }

                update_response = requests.put(
                    f"{CONFLUENCE_API_ENDPOINT}{page_id}",
                    json=update_data,
                    auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
                )
                
                if update_response.status_code == 200:
                    return f"{CONFLUENCE_BASE_URL}/spaces/{CONFLUENCE_SPACE_KEY}/pages/{page_id}"
                    
            # create new page
            else:
                create_data = {
                    "type": "page",
                    "title": title,
                    "space": {"key": CONFLUENCE_SPACE_KEY},
                    "body": {
                        "storage": {
                            "value": results_text,
                            "representation": "storage"
                        }
                    }
                }

                create_response = requests.post(
                    CONFLUENCE_API_ENDPOINT,
                    json=create_data,
                    auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
                )
                
                if create_response.status_code in [200, 201]:
                    page = create_response.json()
                    return f"{CONFLUENCE_BASE_URL}/spaces/{CONFLUENCE_SPACE_KEY}/pages/{page['id']}"

        return None

    except Exception as e:
        logger.error("Failed to publish to Confluence", exc_info=True)
        return None
