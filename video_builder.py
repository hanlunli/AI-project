import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SCENE_FADE_SECS


# ── Font helpers ─────────────────────────────────────────────────

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try Windows system fonts, fall back to PIL default."""
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
        "arialbd.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    # Last resort: PIL's built-in bitmap font (no size param)
    return ImageFont.load_default()


# ── Text overlay ─────────────────────────────────────────────────

def add_text_overlay(image_path: str, title_text: str, output_path: str) -> None:
    """
    Open an image, resize it to 1280×720, add a semi-transparent bar at the
    bottom with the scene title, and save the result.
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)

    # Dark translucent strip along the bottom 80px
    overlay = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle(
        [(0, VIDEO_HEIGHT - 80), (VIDEO_WIDTH, VIDEO_HEIGHT)],
        fill=(0, 0, 0, 180)
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Draw title text centred in the strip
    draw = ImageDraw.Draw(img)
    font = _load_font(36)

    # Measure text width for centering
    bbox = draw.textbbox((0, 0), title_text, font=font)
    text_w = bbox[2] - bbox[0]
    x = max((VIDEO_WIDTH - text_w) // 2, 20)
    y = VIDEO_HEIGHT - 50

    # Drop shadow for readability
    draw.text((x + 2, y + 2), title_text, font=font, fill=(0, 0, 0))
    draw.text((x, y), title_text, font=font, fill=(255, 255, 255))

    img.save(output_path)


# ── Thumbnail ────────────────────────────────────────────────────

def generate_thumbnail(topic: str, first_image_path: str, output_path: str) -> None:
    """
    Create a YouTube thumbnail from the first scene image with the topic
    overlaid as large bold text.
    """
    img = Image.open(first_image_path).convert("RGB")
    img = img.resize((1280, 720), Image.LANCZOS)

    # Darken the image slightly for text contrast
    darkener = Image.new("RGBA", (1280, 720), (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), darkener).convert("RGB")

    draw = ImageDraw.Draw(img)
    font_big  = _load_font(72)
    font_small = _load_font(36)

    # Wrap topic text
    words = topic.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        test_line = " ".join(current)
        bbox = draw.textbbox((0, 0), test_line, font=font_big)
        if (bbox[2] - bbox[0]) > 1100:
            lines.append(" ".join(current[:-1]))
            current = [word]
    lines.append(" ".join(current))

    total_h = len(lines) * 90
    start_y = (720 - total_h) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_big)
        x = max((1280 - (bbox[2] - bbox[0])) // 2, 20)
        y = start_y + i * 90
        # Shadow
        draw.text((x + 3, y + 3), line, font=font_big, fill=(0, 0, 0))
        draw.text((x, y), line, font=font_big, fill=(255, 220, 50))

    img.save(output_path)
    print(f"  Thumbnail saved: {output_path}")


# ── Video assembly ───────────────────────────────────────────────

def build_video(scenes: list[dict], output_path: str) -> None:
    """
    Combine per-scene images and audio into a final MP4 video.
    Each scene's duration is driven by its audio length.
    """
    clips = []
    temp_images = []

    for scene in scenes:
        scene_num = scene["scene_number"]
        print(f"  Compositing scene {scene_num}...")

        # Add text overlay to a temp copy of the image
        overlaid = scene["image_path"].replace(".png", "_text.png")
        add_text_overlay(scene["image_path"], scene["title"], overlaid)
        temp_images.append(overlaid)

        # Load audio and measure duration
        audio_clip = AudioFileClip(scene["audio_path"])
        duration = audio_clip.duration + 0.3   # tiny buffer after speech ends

        # Build image clip
        img_clip = (
            ImageClip(overlaid)
            .set_duration(duration)
            .set_audio(audio_clip)
            .fadein(SCENE_FADE_SECS)
            .fadeout(SCENE_FADE_SECS)
        )
        clips.append(img_clip)

    print("  Concatenating clips and rendering video (this may take a few minutes)...")
    final = concatenate_videoclips(clips, method="compose")

    final.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        logger=None,         # suppress verbose MoviePy bar
    )

    # Cleanup
    final.close()
    for c in clips:
        c.close()
    for path in temp_images:
        try:
            os.remove(path)
        except OSError:
            pass

    print(f"  Video saved: {output_path}")
