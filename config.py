import os

# ── Video settings ──────────────────────────────────────────────
VIDEO_WIDTH       = 1280
VIDEO_HEIGHT      = 720
VIDEO_FPS         = 24
SCENE_FADE_SECS   = 0.4      # fade in/out duration per scene

# ── Ollama / LLM ────────────────────────────────────────────────
OLLAMA_MODEL      = "llama3"  # swap to "mistral" if you prefer

# ── Text-to-speech ──────────────────────────────────────────────
# Full list: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support
TTS_VOICE         = "en-US-AriaNeural"

# ── Research ────────────────────────────────────────────────────
MAX_RESEARCH_RESULTS = 6

# ── Image search ────────────────────────────────────────────────
IMAGE_DOWNLOAD_TIMEOUT = 15   # seconds per image download attempt

# ── Output paths ────────────────────────────────────────────────
OUTPUT_DIR        = "output"
AUDIO_DIR         = os.path.join(OUTPUT_DIR, "audio")
IMAGES_DIR        = os.path.join(OUTPUT_DIR, "images")
VIDEO_DIR         = os.path.join(OUTPUT_DIR, "video")

# ── YouTube ─────────────────────────────────────────────────────
YOUTUBE_SECRETS_FILE  = "client_secrets.json"
YOUTUBE_TOKEN_FILE    = "token.pickle"
YOUTUBE_PRIVACY       = "private"   # "private", "unlisted", or "public"
YOUTUBE_CATEGORY_ID   = "27"        # 27 = Education
