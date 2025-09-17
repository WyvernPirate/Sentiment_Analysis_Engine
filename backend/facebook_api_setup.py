import requests
import os

# --- Step 1 & 2: Facebook Developer Setup & Access Token ---
# Follow the instructions from the previous steps to get your access token.
# Make sure it has the 'pages_read_engagement' permission.

# --- Step 3: Store Your Credentials Securely ---
# Set your access token as an environment variable.
# For Windows CMD: set FB_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
# For PowerShell:  $env:FB_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"

ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
PAGE_NAME = 'BWGovernment' # The username of the page you want to scrape

if not ACCESS_TOKEN:
    raise ValueError("Facebook Access Token not found. Please set the FB_ACCESS_TOKEN environment variable.")

# --- Step 4: Helper functions to get Page ID and Posts ---

def get_page_id(page_name, access_token):
    """
    Gets the numerical ID for a Facebook Page name.
    """
    url = f"https://graph.facebook.com/v18.0/{page_name}"
    print(f"DEBUG: Calling Graph API URL for page ID: {url}")
    params = {
        'access_token': access_token,
        'fields': 'id'
    }
    try:
        response = requests.get(url, params=params)
        print(f"DEBUG: API Response Status Code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        return data.get('id')
    except requests.exceptions.RequestException as e:
        print("--- ERROR FETCHING PAGE ID ---")
        print(f"Request to {url} failed with error: {e}")
        print("DEBUG: Full API Error Response:")
        try:
            print(response.json())
        except Exception as json_e:
            print(f"Could not parse JSON from response. Raw text: {response.text}")
        print("--- END ERROR ---")
        return None

def get_facebook_page_posts(page_id, access_token):
    """
    Fetches the most recent posts from a public Facebook page using its ID.
    """
    url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
    print(f"DEBUG: Calling Graph API URL for posts: {url}")
    params = {
        'access_token': access_token,
        'fields': 'id,message,created_time,comments.summary(true),reactions.summary(true)',
        'limit': 10
    }
    try:
        response = requests.get(url, params=params)
        print(f"DEBUG: API Response Status Code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        return data.get('data')
    except requests.exceptions.RequestException as e:
        print("--- ERROR FETCHING POSTS ---")
        print(f"Request to {url} failed with error: {e}")
        print("DEBUG: Full API Error Response:")
        try:
            print(response.json())
        except Exception as json_e:
            print(f"Could not parse JSON from response. Raw text: {response.text}")
        print("--- END ERROR ---")
        return None

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Attempting to find Page ID for username: '{PAGE_NAME}'")
    page_id = get_page_id(PAGE_NAME, ACCESS_TOKEN)

    if page_id:
        print(f"Successfully found Page ID: {page_id}")
        posts = get_facebook_page_posts(page_id, ACCESS_TOKEN)

        if posts:
            print(f"Successfully fetched {len(posts)} posts.")
            for post in posts:
                print("\n" + "="*50)
                print(f"Post ID: {post.get('id')}")
                print(f"Created Time: {post.get('created_time')}")
                print(f"Message: {post.get('message', 'No message content')}")
                if 'reactions' in post:
                    print(f"Reactions: {post['reactions']['summary']['total_count']}")
                if 'comments' in post:
                    print(f"Comments: {post['comments']['summary']['total_count']}")
                print("="*50)
        else:
            print("Failed to fetch posts for the page.")
    else:
        print(f"Failed to find Page ID for '{PAGE_NAME}'.")
        print("Please check the following:")
        print("1. The page username is correct and the page is public.")
        print("2. Your Access Token is valid and has not expired.")
        print("3. Your Access Token has the 'pages_read_engagement' permission.")
        print("4. Your Facebook account is in good standing and has no restrictions.")