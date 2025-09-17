import requests
import os

# --- Step 1: Apply for a Twitter Developer Account ---
# 1. Go to https://developer.twitter.com/en/apply-for-access and apply for a developer account.
#    You will need to answer a few questions about your intended use of the API.
#    Be clear that you are using it for academic purposes or personal projects involving sentiment analysis.
# 2. Once approved, you will be taken to your Developer Portal dashboard.

# --- Step 2: Create a Project and an App ---
# 1. In your Developer Portal, create a new Project.
# 2. Within that Project, create a new App.
# 3. You will be given several keys. For searching public tweets, you only need the "Bearer Token".

# --- Step 3: Store Your Bearer Token Securely ---
# Store your Bearer Token as an environment variable.
# For Windows CMD: set TWITTER_BEARER_TOKEN="YOUR_BEARER_TOKEN"
# For PowerShell:  $env:TWITTER_BEARER_TOKEN="YOUR_BEARER_TOKEN"

BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')

if not BEARER_TOKEN:
    raise ValueError("Twitter Bearer Token not found. Please set the TWITTER_BEARER_TOKEN environment variable.")

# --- Step 4: Search for Recent Tweets ---

def search_recent_tweets(query, bearer_token):
    """
    Searches for recent tweets matching the query using the Twitter API v2.
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    # Query parameters
    # -is:retweet excludes retweets
    # lang:en specifies English language tweets (you can also use 'ts' for Setswana, but it's less common)
    # You can add more complex queries like '(#botswanapolitics OR #bwpolitics)'
    params = {
        'query': query,
        'max_results': 10,
        'tweet.fields': 'created_at,public_metrics,lang' # Specify which fields you want in the response
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        json_response = response.json()
        return json_response.get('data', []) # The tweets are in the 'data' field

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        # Print the full error response from Twitter if available
        if response:
            print(f"Full error response: {response.text}")
        return None

# --- Main Execution ---
if __name__ == "__main__":
    # Example query: looks for tweets about "botswana politics" in English, excluding retweets.
    search_query = '"botswana politics" lang:en -is:retweet'
    
    print(f"Searching for tweets with query: '{search_query}'")
    tweets = search_recent_tweets(search_query, BEARER_TOKEN)

    if tweets:
        print(f"Successfully fetched {len(tweets)} tweets.")
        for tweet in tweets:
            print("\n" + "="*50)
            print(f"Tweet ID: {tweet.get('id')}")
            print(f"Created At: {tweet.get('created_at')}")
            print(f"Language: {tweet.get('lang')}")
            print(f"Text: {tweet.get('text')}")
            metrics = tweet.get('public_metrics', {})
            print(f"Metrics: Retweets: {metrics.get('retweet_count')}, Replies: {metrics.get('reply_count')}, Likes: {metrics.get('like_count')}")
            print("="*50)
    else:
        print("Failed to fetch tweets or no tweets found for the query.")
