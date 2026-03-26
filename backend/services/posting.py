import json
import logging
import re
from fastapi import HTTPException
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk import CLINotFoundError, CLIConnectionError, ProcessError, ClaudeSDKError
from backend.services.schema import generate_profile_schema

logger = logging.getLogger(__name__)

EMPTY_RESULT = {
    "key_requirements": [],
    "emphasis_areas": [],
    "keywords": [],
}

POSTING_SYSTEM_PROMPT = "You are a job posting analyst. Your job is to fetch and analyze job postings from the web and extract structured information that helps candidates tailor their applications."

POSTING_PROMPT = """Fetch and analyze the job posting at this URL: {url}

Use the WebFetch tool to retrieve the job posting content.

Current candidate profile for context:
{profile_json}

Profile schema reference:
{schema}

Analyze the posting and return ONLY a JSON object with these keys:
- "key_requirements": List of specific requirements, qualifications, and must-haves from the posting
- "emphasis_areas": Domains, responsibilities, or themes that are heavily emphasized
- "keywords": Important technical terms, tools, skills, and phrases to incorporate

Be specific and extract actual text/terms from the posting. Do not invent or generalize.
Return only valid JSON — no markdown fences, no extra text."""


def _parse_json_result(raw: str) -> dict:
    """Parse JSON from SDK result text, handling markdown code fences."""
    if not raw:
        return dict(EMPTY_RESULT)

    stripped = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", stripped)
    if fence_match:
        stripped = fence_match.group(1).strip()

    try:
        parsed = json.loads(stripped)
        return {
            "key_requirements": parsed.get("key_requirements", []),
            "emphasis_areas": parsed.get("emphasis_areas", []),
            "keywords": parsed.get("keywords", []),
        }
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Failed to parse posting analysis response: %s", raw[:200])
        return dict(EMPTY_RESULT)


async def analyze_posting(url: str, profile: dict) -> dict:
    schema = generate_profile_schema()
    profile_json = json.dumps(profile, indent=2)
    prompt = POSTING_PROMPT.format(url=url, profile_json=profile_json, schema=schema)

    options = ClaudeAgentOptions(
        allowed_tools=["WebFetch"],
        permission_mode="bypassPermissions",
        max_turns=5,
        system_prompt=POSTING_SYSTEM_PROMPT,
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
