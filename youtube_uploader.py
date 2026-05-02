import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import (
    YOUTUBE_SECRETS_FILE,
    YOUTUBE_TOKEN_FILE,
    YOUTUBE_PRIVACY,
    YOUTUBE_CATEGORY_ID,
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_authenticated_service():
    """
    Authenticate with OAuth2 and return a YouTube API service object.
    On first run this opens a browser window for Google sign-in.
    After that the token is cached in token.pickle.
    """
    if not os.path.exists(YOUTUBE_SECRETS_FILE):
        raise FileNotFoundError(
            f"\n'{YOUTUBE_SECRETS_FILE}' not found.\n"
            "Follow the setup steps in README_SETUP.txt to create it."
        )

    credentials = None

    # Load cached token if it exists
    if os.path.exists(YOUTUBE_TOKEN_FILE):
        with open(YOUTUBE_TOKEN_FILE, "rb") as f:
            credentials = pickle.load(f)

    # Refresh or re-authenticate as needed
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_SECRETS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open(YOUTUBE_TOKEN_FILE, "wb") as f:
            pickle.dump(credentials, f)

    return build("youtube", "v3", credentials=credentials)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str | None = None,
) -> str:
    """
    Upload a video to YouTube and optionally set its thumbnail.
    Returns the YouTube video ID.
    """
    youtube = _get_authenticated_service()

    body = {
        "snippet": {
            "title":       title[:100],      # YouTube title limit
            "description": description[:5000],
            "tags":        tags[:500],        # tag list limit
            "categoryId":  YOUTUBE_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    print(f"  Uploading '{title}' to YouTube as {YOUTUBE_PRIVACY}...")
    try:
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"    Upload progress: {pct}%", end="\r")

        print()
        video_id = response["id"]
        print(f"  Upload complete! Video ID: {video_id}")

        # Set custom thumbnail (requires channel to be verified on YouTube)
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path),
                ).execute()
                print("  Thumbnail set.")
            except HttpError as e:
                print(f"  Note: could not set thumbnail ({e}). "
                      "Your channel may need to be verified first.")

        return video_id

    except HttpError as e:
        raise RuntimeError(f"YouTube upload failed: {e}")
