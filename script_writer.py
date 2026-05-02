import json
import re
import ollama
from config import OLLAMA_MODEL
from research import format_research_for_prompt


# ── Helpers ─────────────────────────────────────────────────────

def _clean_json(text: str) -> str:
    """Strip markdown code fences that LLMs sometimes wrap around JSON."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the response text."""
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


# ── Script generation ────────────────────────────────────────────

SCRIPT_PROMPT = """You are a YouTube video script writer. Create an engaging educational video script about:

TOPIC: {topic}

RESEARCH:
{research}

Write a script with exactly 6 scenes. Return ONLY a valid JSON array — no explanation, no markdown, just raw JSON.

Each scene object must have these exact keys:
- "scene_number": integer (1 through 6)
- "title": string (3–6 word scene title shown on screen)
- "narration": string (what the narrator speaks — 2 to 4 sentences, conversational tone)
- "image_search_query": string (a short, specific search query to find a real photograph or image that fits this scene, e.g. "ancient Roman Colosseum aerial view" or "DNA double helix microscope photo")

Example of the required format:
[
  {{
    "scene_number": 1,
    "title": "Introduction to the Topic",
    "narration": "Welcome to our exploration of ...",
    "image_search_query": "specific descriptive search query for a real photo"
  }}
]
"""


def generate_script(topic: str, research_results: list) -> list[dict]:
    """Use Ollama to generate a structured video script."""
    research_text = format_research_for_prompt(research_results)
    prompt = SCRIPT_PROMPT.format(
        topic=topic,
        research=research_text,
    )

    for attempt in range(3):
        try:
            raw = _call_ollama(prompt)
            cleaned = _clean_json(raw)
            scenes = json.loads(cleaned)
            if isinstance(scenes, list) and len(scenes) > 0:
                print(f"  Script generated: {len(scenes)} scenes.")
                return scenes
        except json.JSONDecodeError as e:
            print(f"  Attempt {attempt + 1}: JSON parse error — {e}. Retrying...")

    raise RuntimeError("Failed to generate a valid script after 3 attempts. "
                       "Try running Ollama manually to check the model is loaded.")


# ── Metadata generation ──────────────────────────────────────────

METADATA_PROMPT = """Generate YouTube upload metadata for a video about: {topic}

Script summary:
{summary}

Return ONLY valid JSON with these exact keys — no markdown, no explanation:
{{
  "title": "engaging YouTube title, under 70 characters",
  "description": "3 paragraph YouTube description with keywords and a call to action",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"]
}}
"""


def generate_metadata(topic: str, scenes: list[dict]) -> dict:
    """Use Ollama to generate YouTube title, description, and tags."""
    summary = " ".join(s["narration"] for s in scenes)[:1500]
    prompt = METADATA_PROMPT.format(topic=topic, summary=summary)

    for attempt in range(3):
        try:
            raw = _call_ollama(prompt)
            cleaned = _clean_json(raw)
            metadata = json.loads(cleaned)
            if "title" in metadata and "description" in metadata:
                return metadata
        except json.JSONDecodeError as e:
            print(f"  Attempt {attempt + 1}: metadata JSON parse error — {e}. Retrying...")

    # Fallback metadata if LLM keeps failing
    print("  Warning: could not generate metadata via LLM. Using fallback.")
    return {
        "title": f"{topic} | Full Explainer",
        "description": f"An educational video covering {topic}.",
        "tags": [topic, "education", "explainer", "learn", "AI generated"]
    }
