"""Session Bridge — DeepSeek API summarizer."""
import os
import json
import urllib.request
import urllib.error

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"

SUMMARY_PROMPT = """You are a session context summarizer for Claude Code. Analyze the conversation transcript below and produce a structured summary in JSON format.

Return ONLY a valid JSON object with these fields:
{
  "summary": "A concise 2-3 sentence summary of what this session was about",
  "decisions": "Key decisions made, one per line (use '-' prefix)",
  "current_tasks": "Tasks in progress and their status, one per line (use '-' prefix)",
  "key_files": "Important file paths discussed or modified, one per line",
  "tags": "3-5 keywords or tags for this session, comma-separated"
}

Focus on extracting actionable information that will help restore context after compaction. Be specific — mention actual file paths, function names, and concrete decisions.

TRANSCRIPT:
{transcript}
"""


def get_api_key() -> str:
    """Try to get DeepSeek API key from environment or Claude config."""
    # Check common env vars
    for var in ["DEEPSEEK_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
        key = os.environ.get(var, "")
        if key and key.startswith("sk-"):
            return key
    # Try reading from settings.json
    settings_paths = [
        os.path.expandvars(r"%USERPROFILE%\.claude\settings.json"),
        os.path.expandvars(r"%HOME%\.claude\settings.json"),
    ]
    for sp in settings_paths:
        try:
            with open(sp, "r", encoding="utf-8") as f:
                settings = json.load(f)
            key = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
            if key and key.startswith("sk-"):
                return key
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    return ""


def summarize(transcript: str, api_key: str = "") -> dict:
    """Generate a structured summary of the conversation transcript."""
    if not api_key:
        api_key = get_api_key()
    if not api_key:
        return {"error": "No DeepSeek API key found. Set DEEPSEEK_API_KEY or ANTHROPIC_AUTH_TOKEN."}

    prompt = SUMMARY_PROMPT.replace("{transcript}", transcript[-8000:])

    payload = json.dumps({
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }).encode("utf-8")

    req = urllib.request.Request(DEEPSEEK_API_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        # Try to parse JSON from response
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
        return json.loads(content)
    except urllib.error.HTTPError as e:
        return {"error": f"API error: {e.code} — {e.reason}"}
    except (json.JSONDecodeError, KeyError) as e:
        return {"error": f"Failed to parse response: {e}"}
