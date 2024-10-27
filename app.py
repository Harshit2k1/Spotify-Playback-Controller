from flask import Flask, request, jsonify, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
import requests
from dotenv import load_dotenv,set_key

project_folder = os.path.expanduser('~/mysite')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

app = Flask(__name__)

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SPOTIPY_REFRESH_TOKEN = os.getenv('SPOTIPY_REFRESH_TOKEN')  # Stored refresh token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize Spotify OAuth object
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope='user-modify-playback-state user-read-playback-state'
)

# Helper function to get a new access token
def get_access_token():
    global SPOTIPY_REFRESH_TOKEN
    token_info = None

    # If a refresh token is available, use it to get a new access token
    if SPOTIPY_REFRESH_TOKEN:
        try:
            token_info = sp_oauth.refresh_access_token(SPOTIPY_REFRESH_TOKEN)
        except spotipy.oauth2.SpotifyOauthError:
            return {"error": "Invalid refresh token. Please re-authenticate by visiting /auth."}, 401
    else:
        return {"error": "Authentication required, visit: /auth"}, 401

    return token_info['access_token']

@app.route('/auth')
def auth():
    # Redirect user to Spotify's authorization page
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Callback route to handle Spotify authentication
@app.route('/callback')
def callback():
    global SPOTIPY_REFRESH_TOKEN

    # Get authorization code from query parameters
    code = request.args.get('code')
    if code:
        # Exchange code for access token and refresh token
        token_info = sp_oauth.get_access_token(code)

        # Update refresh token in memory
        SPOTIPY_REFRESH_TOKEN = token_info['refresh_token']

        # change the ORI variable
        set_key(os.path.join(project_folder, '.env'), "SPOTIPY_REFRESH_TOKEN", SPOTIPY_REFRESH_TOKEN)

        return jsonify({"message": "Authentication successful! Refresh token obtained and saved."}), 200
    else:
        return jsonify({"error": "Authorization failed."}), 400

# Helper function to get device ID by name
def get_device_id_by_name(sp, device_name):
    devices = sp.devices()['devices']
    for device in devices:
        if device['name'].lower() == device_name.lower():
            return device['id']
    return None

# Function to send error messages to Telegram
def send_error_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id=871580978&text={message}"
    try:
        requests.get(telegram_url)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# Function to attempt playback with retry logic
def attempt_playback(sp, device_id, uri, input_type):
    if input_type.lower() == 'playlist':
        response = sp.start_playback(device_id=device_id, context_uri=f'spotify:playlist:{uri}')
    elif input_type.lower() == 'song':
        response = sp.start_playback(device_id=device_id, uris=[f'spotify:track:{uri}'])

    return response

# Route to play a song or playlist using a GET request
@app.route('/play', methods=['GET'])
def play():
    input_type = request.args.get('type')  # Can be 'song' or 'playlist'
    uri = request.args.get('uri')
    device = request.args.get('device')

    if not uri or not device or not input_type:
        return jsonify({"error": "type, uri, and device are required"}), 400

    for attempt in range(2):
        try:
            # Get a valid access token (refresh if needed)
            access_token = get_access_token()
            if isinstance(access_token, dict) and 'error' in access_token:
                return jsonify(access_token), 401  # Error response if token retrieval failed

            # Initialize Spotify object with the access token
            sp = spotipy.Spotify(auth=access_token)

            # Get the device ID based on the device name
            device_id = get_device_id_by_name(sp, device)
            if not device_id:
                error_message = f"No device found with the name: {device}"
                send_error_to_telegram(error_message)
                time.sleep(5)
                continue

            # Attempt to start playback
            response = attempt_playback(sp, device_id, uri, input_type)
            if response is not None and response.get('error'):
                time.sleep(5)
                continue

            return jsonify({"message": f"{input_type.capitalize()} playback started on device!"}), 200

        except Exception as e:
            error_message = str(e)
            send_error_to_telegram(error_message)
            time.sleep(5)

    return jsonify({"error": "Failed to start playback after retries."}), 400

if __name__ == '__main__':
    app.run(debug=True)
