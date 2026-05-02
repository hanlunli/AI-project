import io
import time
import requests
from PIL import Image
from duckduckgo_search import DDGS
from config import VIDEO_WIDTH, VIDEO_HEIGHT


def search_and_download_image(query: str, output_path: str) -> None:
    """
    Search DuckDuckGo for images, try to download the full-size image,
    and fall back to DDG's own thumbnail CDN (always accessible) if the
    image host blocks the request.
    """
    print(f"    Searching images for: \"{query}\"")
    results = _search_images(query)

    if not results:
        print(f"    No results found. Using placeholder.")
        _make_placeholder(output_path, query)
        return

    session = _make_session()

    # Pass 1 — try full-size image URLs (some hosts block, hence pass 2)
    for r in results:
        url = r.get("image", "")
        if not url:
            continue
        img = _try_download(session, url, min_w=400, min_h=300)
        if img:
            _save(img, output_path)
            print(f"    Full image saved.")
            return

    # Pass 2 — fall back to DuckDuckGo-hosted thumbnails (their own CDN,
    #           never blocked). We upscale with LANCZOS so quality is decent.
    print(f"    Full images blocked by hosts. Falling back to DDG thumbnails...")
    for r in results:
        url = r.get("thumbnail", "")
        if not url:
            continue
        img = _try_download(session, url, min_w=1, min_h=1)
        if img:
            _save(img, output_path)
            print(f"    Thumbnail saved (upscaled).")
            return

    print(f"    Warning: all downloads failed. Using placeholder.")
    _make_placeholder(output_path, query)


# ── Search ───────────────────────────────────────────────────────

def _search_images(query: str, max_results: int = 20) -> list[dict]:
    """Return raw DuckDuckGo image result dicts (image + thumbnail URLs)."""
    all_results = []
    queries = [query, f"{query} photograph", f"{query} high resolution"]

    with DDGS() as ddgs:
        for q in queries:
            try:
                batch = list(ddgs.images(q, max_results=max_results))
                for r in batch:
                    if r not in all_results:
                        all_results.append(r)
                if len(all_results) >= max_results:
                    break
                time.sleep(0.4)
            except Exception:
                continue

    return all_results


# ── Downloading ──────────────────────────────────────────────────

def _make_session() -> requests.Session:
    """Session that looks like a real browser to avoid hotlink blocks."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept":          "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer":         "https://duckduckgo.com/",
        "DNT":             "1",
    })
    return s


def _try_download(
    session: requests.Session,
    url: str,
    min_w: int,
    min_h: int,
) -> Image.Image | None:
    """
    Attempt to download url and return a PIL Image.
    Returns None on any failure or if image is too small.
    """
    try:
        resp = session.get(url, timeout=15, allow_redirects=True, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and "octet-stream" not in content_type:
            return None

        data = b"".join(resp.iter_content(chunk_size=65536))
        img = Image.open(io.BytesIO(data)).convert("RGB")

        if img.width < min_w or img.height < min_h:
            return None

        return img

    except Exception:
        return None


# ── Image processing ─────────────────────────────────────────────

def _save(img: Image.Image, path: str) -> None:
    """Resize + crop to 1280×720 and save."""
    img = _resize_and_crop(img, VIDEO_WIDTH, VIDEO_HEIGHT)
    img.save(path)


def _resize_and_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Scale to fill target dimensions then centre-crop — no black bars."""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(int(src_w * scale), target_w)
    new_h = max(int(src_h * scale), target_h)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top  = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _make_placeholder(output_path: str, label: str) -> None:
    from PIL import ImageDraw
    img  = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (35, 35, 35))
    draw = ImageDraw.Draw(img)
    words = label.split()
    lines, line = [], []
    for word in words:
        line.append(word)
        if len(" ".join(line)) > 55:
            lines.append(" ".join(line[:-1]))
            line = [word]
    lines.append(" ".join(line))
    y = VIDEO_HEIGHT // 2 - len(lines) * 18
    for text_line in lines:
        draw.text((VIDEO_WIDTH // 2, y), text_line, fill=(180, 180, 180), anchor="mm")
        y += 36
    img.save(output_path)


if __name__ == "__main__":
    search_and_download_image("fossil record illustration", "test_image.png")
    print("Saved test_image.png")