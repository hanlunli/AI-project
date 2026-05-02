"""
AI YouTube Video Pipeline
─────────────────────────
Run:  python main.py
"""

import os
import sys

from config import AUDIO_DIR, IMAGES_DIR, VIDEO_DIR, OUTPUT_DIR
from research import research_topic
from script_writer import generate_script, generate_metadata
from tts_generator import generate_audio
from image_generator import search_and_download_image
from video_builder import build_video, generate_thumbnail
from youtube_uploader import upload_video


# ── Helpers ──────────────────────────────────────────────────────

def setup_directories():
    for d in [OUTPUT_DIR, AUDIO_DIR, IMAGES_DIR, VIDEO_DIR]:
        os.makedirs(d, exist_ok=True)


def print_banner():
    print("=" * 55)
    print("   AI YouTube Video Pipeline")
    print("=" * 55)


def print_phase(number: int, label: str):
    print(f"\n{'─'*55}")
    print(f"  Phase {number}: {label}")
    print(f"{'─'*55}")


# ── Main pipeline ─────────────────────────────────────────────────

def run_pipeline(topic: str, skip_upload: bool = False):
    setup_directories()

    # ── Phase 1: Research + Script ───────────────────────────────
    print_phase(1, "Research & Script Writing")

    print("Researching topic online...")
    research_results = research_topic(topic)

    print("Writing video script with Ollama (this may take 30-60 seconds)...")
    scenes = generate_script(topic, research_results)

    print(f"\nScript preview:")
    for scene in scenes:
        print(f"  Scene {scene['scene_number']}: {scene['title']}")

    # ── Phase 2: Asset Generation ────────────────────────────────
    print_phase(2, "Asset Generation")

    for i, scene in enumerate(scenes, 1):
        num = scene["scene_number"]
        print(f"\nScene {i}/{len(scenes)}: {scene['title']}")

        # Audio
        audio_path = os.path.join(AUDIO_DIR, f"scene_{num}.mp3")
        print(f"  Generating audio...")
        generate_audio(scene["narration"], audio_path)
        scene["audio_path"] = audio_path

        # Image
        image_path = os.path.join(IMAGES_DIR, f"scene_{num}.png")
        print(f"  Searching for image...")
        search_and_download_image(scene["image_search_query"], image_path)
        scene["image_path"] = image_path

    # ── Phase 3: Video Assembly ──────────────────────────────────
    print_phase(3, "Video Assembly")

    video_path     = os.path.join(VIDEO_DIR, "final_video.mp4")
    thumbnail_path = os.path.join(VIDEO_DIR, "thumbnail.png")

    print("Assembling video...")
    build_video(scenes, video_path)

    print("Generating thumbnail...")
    generate_thumbnail(topic, scenes[0]["image_path"], thumbnail_path)

    print(f"\nVideo ready: {os.path.abspath(video_path)}")

    # ── Phase 4: YouTube Upload ──────────────────────────────────
    print_phase(4, "YouTube Upload")

    if skip_upload:
        print("Skipping upload (--no-upload flag set).")
        print(f"Video file: {os.path.abspath(video_path)}")
        return

    print("Generating YouTube metadata...")
    metadata = generate_metadata(topic, scenes)
    print(f"  Title:  {metadata['title']}")
    print(f"  Tags:   {', '.join(metadata['tags'][:5])}...")

    answer = input("\nUpload to YouTube now? (y/n): ").strip().lower()
    if answer != "y":
        print("Upload skipped. Video saved locally.")
        print(f"  {os.path.abspath(video_path)}")
        return

    video_id = upload_video(
        video_path,
        metadata["title"],
        metadata["description"],
        metadata["tags"],
        thumbnail_path,
    )

    print(f"\n{'='*55}")
    print(f"  All done!")
    print(f"  Watch at: https://www.youtube.com/watch?v={video_id}")
    print(f"{'='*55}\n")


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    print_banner()

    # Check for --no-upload flag
    skip = "--no-upload" in sys.argv

    topic = input("\nEnter the topic for your video:\n> ").strip()
    if not topic:
        print("No topic entered. Exiting.")
        sys.exit(1)

    run_pipeline(topic, skip_upload=skip)
