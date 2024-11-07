import requests
from deep_translator import GoogleTranslator
import logging
import time

# Configure logging for better error tracking and debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get the content from Cnfluence
def get_confluence_page_content(page_id, confluence_url, auth_token):
    url = f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage,version"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        content = data['body']['storage']['value']
        title = data['title']
        version = data['version']['number']
        return {'content': content, 'title': title, 'version': version}
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while fetching page {page_id}: {http_err}")
    except Exception as err:
        logging.error(f"Other error occurred while fetching page {page_id}: {err}")
    return None

# Function to translate text from CZ to EN using Google Translator
def translate_text(text, source_lang='cs', target_lang='en'):
    try:
        translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated_text
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        return text  # Return original text in case of failure

# Function to update the Confluence page with translated content
def update_confluence_page(page_id, content, confluence_url, auth_token):
    url = f"{confluence_url}/rest/api/content/{page_id}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    data = {
        "version": {"number": content['version'] + 1},  # Increment version
        "type": "page",
        "title": content['title'],
        "body": {
            "storage": {
                "value": content['content'],  # Updated translated content
                "representation": "storage"
            }
        }
    }
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        logging.info(f"Page '{content['title']}' successfully updated!")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while updating page {page_id}: {http_err}")
    except Exception as err:
        logging.error(f"Other error occurred while updating page {page_id}: {err}")

# Main logic to translate multiple Confluence documents
def translate_confluence_documents(page_ids, confluence_url, auth_token):
    for page_id in page_ids:
        logging.info(f"Processing page ID: {page_id}")
        
        # Get the page content
        page_content = get_confluence_page_content(page_id, confluence_url, auth_token)
        if page_content:
            # Translate the content
            translated_content = translate_text(page_content['content'])  # Translate only the content
            
            # Update the content with the translated text
            page_content['content'] = translated_content  # Update the content with translation
            
            # Update the page with the translated content
            update_confluence_page(page_id, page_content, confluence_url, auth_token)
        
        # Adding a delay to prevent potential rate-limiting or API overload
        time.sleep(1)  # Adjust this time based on your rate limits and use case

# List of page IDs to trnslt
page_ids = ['123456', '123456']  # Replace with actual page IDs
confluence_url = 'https://your-domain.atlassian.net'  # Replace with your Confluence URL
auth_token = 'your-confluence-api-token'  # Replace with your Confluence API token

# Translate the documents
translate_confluence_documents(page_ids, confluence_url, auth_token)
