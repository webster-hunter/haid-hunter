import json
import logging
import re
from fastapi import HTTPException
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError
from backend.services.schema import generate_profile_schema

logger = logging.getLogger(__name__)

EMPTY_RESULT = {
    "skills": [],
    "technologies": [],
    "experience_keywords": [],
    "soft_skills": [],
}

EXTRACTION_PROMPT = """Analyze the documents in this directory and extract structured profile information.

Use the Read and Glob tools to read documents in the current working directory.

{schema}

Return ONLY a JSON object with these keys:
- "skills": Technical skills mentioned (programming languages, frameworks, tools)
- "technologies": Infrastructure, platforms, databases, cloud services
- "experience_keywords": Key accomplishments, metrics, and experience highlights (short phrases)
- "soft_skills": Leadership, communication, teamwork, and other soft skills

Be specific and extract actual terms/phrases from the documents. Do not invent or generalize.
Return only valid JSON — no markdown fences, no extra text."""


def _parse_json_result(raw: str) -> dict:
    """Parse JSON from SDK result text, handling markdown code fences."""
    if not raw:
        return dict(EMPTY_RESULT)

    # Strip markdown code fences if present
    stripped = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", stripped)
    if fence_match:
        stripped = fence_match.group(1).strip()

    try:
        parsed = json.loads(stripped)
        return {
            "skills": parsed.get("skills", []),
            "technologies": parsed.get("technologies", []),
            "experience_keywords": parsed.get("experience_keywords", []),
            "soft_skills": parsed.get("soft_skills", []),
        }
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Failed to parse extraction response: %s", raw[:200])
        return dict(EMPTY_RESULT)


async def extract_from_documents(documents_dir: str) -> dict:
    schema = generate_profile_schema()
    prompt = EXTRACTION_PROMPT.format(schema=schema)

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        cwd=documents_dir,
        permission_mode="bypassPermissions",
        max_turns=5,
    )

    try:
        result_text = None
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, "result") and message.result is not None:
                result_text = message.result
        return _parse_json_result(result_text or "")
    except CLINotFoundError as exc:
        logger.error("Claude CLI not found: %s", exc)
        raise HTTPException(status_code=503, detail="Claude CLI not found") from exc
    except CLIConnectionError as exc:
        logger.error("Claude CLI connection error: %s", exc)
        raise HTTPException(status_code=503, detail="Claude CLI connection error") from exc
    except ProcessError as exc:
        logger.error("Claude process error: %s", exc)
        raise HTTPException(status_code=502, detail="Claude process error") from exc
    except ClaudeSDKError as exc:
        logger.error("Claude SDK error: %s", exc)
        raise HTTPException(status_code=500, detail="Claude SDK error") from exc


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
