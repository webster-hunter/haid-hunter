import json
import logging
from backend.config import get_api_key

logger = logging.getLogger(__name__)

EMPTY_RESULT = {
    "skills": [],
    "technologies": [],
    "experience_keywords": [],
    "soft_skills": [],
}

EXTRACTION_PROMPT = """Analyze the following documents from a job seeker and extract structured information.

Return ONLY a JSON object with these keys:
- "skills": Technical skills mentioned (programming languages, frameworks, tools)
- "technologies": Infrastructure, platforms, databases, cloud services
- "experience_keywords": Key accomplishments, metrics, and experience highlights (short phrases)
- "soft_skills": Leadership, communication, teamwork, and other soft skills

Be specific and extract actual terms/phrases from the documents. Do not invent or generalize.

Documents:
{doc_contents}"""


def get_claude_client():
    import anthropic
    return anthropic.Anthropic(api_key=get_api_key())


def extract_from_documents(doc_contents: str) -> dict:
    if doc_contents == "No previewable documents found.":
        return dict(EMPTY_RESULT)

    client = get_claude_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT.format(doc_contents=doc_contents),
        }],
    )

    raw = response.content[0].text
    try:
        parsed = json.loads(raw)
        return {
            "skills": parsed.get("skills", []),
            "technologies": parsed.get("technologies", []),
            "experience_keywords": parsed.get("experience_keywords", []),
            "soft_skills": parsed.get("soft_skills", []),
        }
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Failed to parse extraction response: %s", raw[:200])
        return dict(EMPTY_RESULT)


def merge_suggestions(existing_profile: dict, suggestions: dict) -> dict:
    profile = dict(existing_profile)
    existing_skills = set(profile.get("skills", []))
    new_skills = (
        suggestions.get("skills", [])
        + suggestions.get("technologies", [])
        + suggestions.get("soft_skills", [])
    )
    merged = list(profile.get("skills", []))
    for skill in new_skills:
        if skill not in existing_skills:
            merged.append(skill)
            existing_skills.add(skill)
    profile["skills"] = merged
    return profile
