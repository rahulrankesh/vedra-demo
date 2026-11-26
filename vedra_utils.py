from urllib.parse import urlparse

def safe_https_url(value):
    """Return an HTTPS URL, or None for malformed/non-HTTPS input."""
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    try:
        parsed = urlparse(candidate)
    except ValueError:
        return None
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    return candidate

def normalise_video_result(value):
    """Normalize SerpAPI video results without assuming one response shape."""
    if isinstance(value, str):
        link = safe_https_url(value)
        return {"link": link, "title": "Watch video", "thumbnail": None, "channel": None} if link else None
    if not isinstance(value, dict):
        return None
    link = safe_https_url(value.get("link"))
    if not link:
        return None
    thumbnail = value.get("thumbnail")
    if isinstance(thumbnail, dict):
        thumbnail = thumbnail.get("static") or thumbnail.get("rich")
    thumbnail = safe_https_url(thumbnail)
    channel = value.get("channel")
    if isinstance(channel, dict):
        channel = channel.get("name")
    return {
        "link": link,
        "title": value.get("title") if isinstance(value.get("title"), str) else "Watch video",
        "thumbnail": thumbnail,
        "channel": channel if isinstance(channel, str) else None,
    }
