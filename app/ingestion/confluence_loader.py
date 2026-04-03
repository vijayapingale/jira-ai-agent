import requests
import os

def fetch_confluence_pages():
    url = "https://your-domain.atlassian.net/wiki/rest/api/content"
    
    response = requests.get(
        url,
        auth=(os.getenv("CONF_USER"), os.getenv("CONF_API_KEY"))
    )

    return response.json()