# Spotify Playback Controller

A Flask-based web application to control Spotify playback using the Spotify Web API. This app supports authentication, playback of songs or playlists, and integration with Telegram for error notifications.

---

## Features

- **Spotify Authentication**: Easily authenticate using the Spotify API.
- **Playback Control**: Start playback on specified devices for songs or playlists.
- **Retry Logic**: Handles playback errors with retry attempts.
- **Error Reporting**: Sends error messages to a Telegram bot for monitoring.

---

## Prerequisites

Ensure you have the following:

- Python 3.7 or above
- A [Spotify Developer Account](https://developer.spotify.com/)
- A Telegram bot token for error reporting
- Flask and required Python dependencies (listed in `requirements.txt`)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/spotify-playback-controller.git
   cd spotify-playback-controller

2. Install Dependencies
   
   ```bash
   pip install -r requirements.txt

3. Set Up Environment Variables
 ```bash

SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
SPOTIPY_REFRESH_TOKEN=your_refresh_token (Optional, generated after authentication)
TELEGRAM_TOKEN=your_telegram_bot_token
```


## Usage

1. **Start the Flask application:**

    ```bash
    python app.py
    ```

2. **Authenticate with Spotify:**

    Visit the `/auth` endpoint to authenticate with Spotify and obtain a refresh token.

3. **Start Playback:**

    Use the `/play` endpoint to start playback.

    - **Request Format:**
      ```
      /play?type={type}&uri={uri}&device={device_name}
      ```

    - **Parameters:**
      - `type`: Either `song` or `playlist`
      - `uri`: Spotify URI of the song or playlist
      - `device`: Name of the device for playback

    - **Example:**

      ```bash
      http://localhost:5000/play?type=playlist&uri=37i9dQZF1DXcBWIGoYBM5M&device=MySpeaker
      ```

  ## PS- I used this to Automate Spotify Playback on my Computer via an NFC tag.


