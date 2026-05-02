from duckduckgo_search import DDGS
from config import MAX_RESEARCH_RESULTS


def research_topic(topic: str) -> list[dict]:
    """
    Search DuckDuckGo for the topic and return a list of result dicts.
    Each dict has: title, href, body
    """
    print(f"  Searching the web for: {topic}")
    results = []

    try:
        with DDGS() as ddgs:
            raw = ddgs.text(topic, max_results=MAX_RESEARCH_RESULTS)
            results = list(raw)
    except Exception as e:
        print(f"  Warning: DuckDuckGo search failed ({e}). Continuing without web data.")

    print(f"  Found {len(results)} research results.")
    return results


def format_research_for_prompt(results: list[dict]) -> str:
    """Convert research results into a readable block for the LLM prompt."""
    if not results:
        return "No web research available. Use your own knowledge."

    lines = []
    for r in results:
        title = r.get("title", "")
        body  = r.get("body", "")
        lines.append(f"- {title}: {body}")

    return "\n".join(lines)
