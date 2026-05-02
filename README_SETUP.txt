════════════════════════════════════════════════════════
  AI YouTube Video Pipeline — Windows Setup Guide
════════════════════════════════════════════════════════

STEP 1: Install Python 3.11
───────────────────────────
1. Go to https://www.python.org/downloads/
2. Download Python 3.11.x (recommended — most stable with MoviePy)
3. Run the installer
   !! Check "Add Python to PATH" before clicking Install !!
4. Verify:  Open Command Prompt and type:
   python --version


STEP 2: Install FFmpeg
──────────────────────
FFmpeg is used by MoviePy to render the final video.

Option A — Using winget (built into Windows 10/11):
  Open Command Prompt as Administrator and run:
  winget install -e --id Gyan.FFmpeg

Option B — Manual install:
  1. Go to https://www.gyan.dev/ffmpeg/builds/
  2. Download "ffmpeg-release-essentials.zip"
  3. Extract it to C:\ffmpeg
  4. Add C:\ffmpeg\bin to your system PATH:
     - Search "Environment Variables" in Start Menu
     - Click "Environment Variables"
     - Under "System variables", find "Path" → Edit
     - Click "New" → type C:\ffmpeg\bin → OK

Verify FFmpeg: open a new Command Prompt and run:
  ffmpeg -version


STEP 3: Install Ollama (free local LLM)
────────────────────────────────────────
1. Go to https://ollama.com and download the Windows installer
2. Run the installer — it adds Ollama as a background service
3. Open Command Prompt and pull the Llama 3 model:
   ollama pull llama3

   (This downloads ~4.7 GB. Only needed once.)

4. Verify Ollama is running:
   ollama list
   You should see "llama3" in the list.

   If you have less than 8 GB RAM, use the smaller model instead:
   ollama pull llama3:8b
   Then open config.py and change:
   OLLAMA_MODEL = "llama3:8b"


STEP 4: Install Python packages
────────────────────────────────
Open Command Prompt in the project folder (where requirements.txt is) and run:

  pip install -r requirements.txt

This installs:
  - duckduckgo-search   (free web search)
  - ollama              (Python client for Ollama)
  - edge-tts            (free Microsoft text-to-speech)
  - requests            (HTTP for image generation)
  - moviepy==1.0.3      (video assembly)
  - imageio / imageio-ffmpeg (MoviePy helpers)
  - pillow              (image processing)
  - google-api-python-client  (YouTube API)
  - google-auth-oauthlib      (YouTube OAuth)
  - google-auth-httplib2      (YouTube auth transport)


STEP 5: Set up YouTube Data API (for uploading)
─────────────────────────────────────────────────
You only need this if you want to auto-upload to YouTube.
You can skip it and just use --no-upload flag to generate the video locally.

5a. Create a Google Cloud project:
  1. Go to https://console.cloud.google.com/
  2. Click "Select a project" → "New Project"
  3. Name it anything (e.g. "YT Pipeline") → Create

5b. Enable the YouTube Data API:
  1. In the Cloud Console, go to "APIs & Services" → "Library"
  2. Search "YouTube Data API v3"
  3. Click it → "Enable"

5c. Create OAuth credentials:
  1. Go to "APIs & Services" → "Credentials"
  2. Click "Create Credentials" → "OAuth client ID"
  3. If prompted, configure the consent screen:
     - Choose "External" → fill in app name → Save
  4. Application type: "Desktop app"
  5. Name it anything → "Create"
  6. Click "Download JSON" on the credential that appears
  7. Rename the downloaded file to:  client_secrets.json
  8. Place it in the project folder (same folder as main.py)


════════════════════════════════════════════════════════
  Running the pipeline
════════════════════════════════════════════════════════

To generate AND upload:
  python main.py

To generate without uploading (no YouTube setup needed):
  python main.py --no-upload

When prompted, type your topic, e.g.:
  The history of the Roman Empire
  How black holes form
  The science of sleep


════════════════════════════════════════════════════════
  Troubleshooting
════════════════════════════════════════════════════════

"ollama is not recognized"
  → Restart Command Prompt after installing Ollama.

"ffmpeg is not recognized"
  → Make sure C:\ffmpeg\bin is in your PATH (see Step 2).
    Open a NEW Command Prompt after adding it.

"ModuleNotFoundError"
  → Run:  pip install -r requirements.txt
    Make sure you're in the correct project folder.

"client_secrets.json not found"
  → Either follow Step 5 to set up YouTube API,
    or run with the --no-upload flag.

Pollinations.ai image times out
  → Pollinations is a free public service and can be slow.
    Increase IMAGE_TIMEOUT in config.py (default: 90 seconds).

Video render is very slow
  → This is normal. A 6-scene video takes 2–5 minutes to render
    depending on your CPU. Grab a coffee.

════════════════════════════════════════════════════════
