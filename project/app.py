# Import necessary modules from Flask and Google API Client
from flask import Flask, render_template, request
from googleapiclient.discovery import build

# Create a Flask app instance
app = Flask(__name__)

# Define a route for the homepage ('/') that renders a template named 'comments.html'
@app.route('/')
def index():
    return render_template('comments.html')

# Define a route '/get_comments' that accepts POST requests
# This route fetches comments for a specific video ID from the YouTube API
@app.route('/get_comments', methods=['POST'])
def get_comments():
    # Get the video ID from the form submitted in the HTML
    video_id = request.form['video_id']

    # Replace this placeholder with your actual YouTube Data API key
    api_key = request.form['api_key']  # Replace with your actual API key

    # Build a service object for interacting with the YouTube Data API
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Create an empty list to store comments fetched from the YouTube API
    comments = []

    # Make a request to the YouTube API to fetch comment threads for a specific video
    comments_request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100  # Adjust the number of comments to retrieve
    )
    comments_response = comments_request.execute()

    # Iterate through each comment retrieved from the API response
    for comment in comments_response['items']:
        # Extract the comment text and commenter's channel ID
        comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        commenter_channel_id = comment['snippet']['topLevelComment']['snippet']['authorChannelId']['value']

        # Request additional information about the commenter using their channel ID
        channel_info_request = youtube.channels().list(
            part='snippet',
            id=commenter_channel_id
        )
        channel_info_response = channel_info_request.execute()

        # Extract the commenter's name from the channel information
        commenter_name = channel_info_response['items'][0]['snippet']['title']

        # Append the commenter's name and comment text to the 'comments' list
        comments.append({'user': commenter_name, 'text': comment_text})

    # Render the 'comments.html' template with the fetched comments
    return render_template('comments.html', comments=comments)

# Define a route '/get_channel_comments' that accepts POST requests
# This route fetches comments for videos uploaded by a specific channel from the YouTube API
@app.route('/get_channel_comments', methods=['POST'])
def get_channel_comments():
    # Get the channel ID and API key from the form submitted in the HTML
    channel_id = request.form['channel_id']
    api_key = request.form['api_key_channel']

    # Build a service object for interacting with the YouTube Data API using the provided API key
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Initialize variables to store playlist items and set up pagination
    playlist_items = []
    next_page_token = None

    # Fetch the uploads playlist ID of the given channel
    channels_response = youtube.channels().list(
        id=channel_id,
        part='contentDetails'
    ).execute()

    # Extract the uploads playlist ID from the channel information
    for channel in channels_response['items']:
        uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

    # Retrieve video IDs from the user's uploads playlist with pagination
    while True:
        playlist_request = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='contentDetails',
            maxResults=50,  # Adjust as needed
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        # Extend the list of playlist items with the fetched items
        playlist_items.extend(playlist_response['items'])
        next_page_token = playlist_response.get('nextPageToken')

        # Break the loop when no more pages of results are available
        if not next_page_token:
            break

    # Fetch comments for each video in the playlist
    comments = []
    for video_item in playlist_items:
        video_id = video_item['contentDetails']['videoId']
        comments_request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100,  # Adjust as needed
        )
        comments_response = comments_request.execute()

        # Extract comments and commenter information for each video
        for comment in comments_response['items']:
            comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
            commenter_channel_id = comment['snippet']['topLevelComment']['snippet']['authorChannelId']['value']

            channel_info_request = youtube.channels().list(
                part='snippet',
                id=commenter_channel_id
            )
            channel_info_response = channel_info_request.execute()

            commenter_name = channel_info_response['items'][0]['snippet']['title']

            # Append commenter's name and comment text to the 'comments' list
            comments.append({'user': commenter_name, 'text': comment_text})

    # Render the 'comments.html' template with the fetched comments
    return render_template('comments.html', comments=comments)

# Run the Flask app if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
