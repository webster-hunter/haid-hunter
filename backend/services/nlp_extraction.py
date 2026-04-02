"""
NLP-based extraction service.
Uses spaCy PhraseMatcher with a unified skill dictionary for offline
keyword extraction. Returns typed skill objects {name, type}.
"""

import logging

import spacy
from spacy.matcher import PhraseMatcher

from backend.services.skill_definitions import SKILLS

logger = logging.getLogger(__name__)

EMPTY_RESULT = {"skills": []}

# Build canonical-lowercase -> (canonical_name, type) lookup
_lower_map: dict[str, tuple[str, str]] = {
    name.lower(): (name, skill_type)
    for name, skill_type in SKILLS.items()
}

# ── SpaCy pipeline (lazy-loaded) ─────────────────────────────────────────────

_nlp = None
_matcher: PhraseMatcher | None = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner"])
    return _nlp


def _get_matcher() -> PhraseMatcher:
    global _matcher
    if _matcher is None:
        nlp = _get_nlp()
        _matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(term.lower()) for term in SKILLS]
        _matcher.add("SKILL", patterns)
    return _matcher


# ── Public API ────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> list[dict]:
    """Return typed skill objects found in text: [{"name": ..., "type": ...}, ...]"""
    if not text or not text.strip():
        return []
    nlp = _get_nlp()
    matcher = _get_matcher()
    doc = nlp(text)
    seen: set[str] = set()
    results: list[dict] = []
    for _match_id, start, end in matcher(doc):
        span_lower = doc[start:end].text.lower()
        entry = _lower_map.get(span_lower)
        if entry and entry[0] not in seen:
            seen.add(entry[0])
            results.append({"name": entry[0], "type": entry[1]})
    return sorted(results, key=lambda s: s["name"])


def extract_from_documents(doc_contents: str) -> dict:
    """
    Main entry point. Returns {"skills": [{"name": ..., "type": ...}, ...]}.
    Works completely offline via spaCy.
    """
    if doc_contents == "No previewable documents found.":
        return dict(EMPTY_RESULT)

    return {"skills": extract_skills(doc_contents)}
