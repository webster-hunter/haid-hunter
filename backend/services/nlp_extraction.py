"""
NLP-based extraction service.
Replaces Claude API calls for document analysis using offline keyword matching
and lightweight text processing — zero API cost, zero network dependency.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Curated keyword lists ──────────────────────────────────────────────────────

SKILLS_LIST = {
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Bash",
    "Shell", "PowerShell", "Lua", "Haskell", "Elixir", "Erlang", "Clojure",
    # Frontend frameworks/libs
    "React", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js", "Svelte",
    "Redux", "MobX", "jQuery", "HTML", "CSS", "Sass", "SCSS", "Tailwind",
    "Bootstrap", "Material UI", "Chakra UI", "Storybook", "Webpack", "Vite",
    # Backend frameworks/libs
    "FastAPI", "Django", "Flask", "Express", "NestJS", "Spring", "Spring Boot",
    "Rails", "Laravel", "Symfony", "ASP.NET", "Node.js", "Deno", "Bun",
    "GraphQL", "REST", "gRPC", "WebSockets",
    # Data / ML
    "NumPy", "Pandas", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
    "Hugging Face", "spaCy", "NLTK", "OpenCV", "Matplotlib", "Seaborn",
    "Spark", "Hadoop", "Airflow", "dbt", "SQLAlchemy",
    # Testing
    "pytest", "Jest", "Mocha", "Chai", "Cypress", "Playwright", "Selenium",
    "unittest", "JUnit",
    # Other
    "Git", "Linux", "Unix", "Agile", "Scrum", "CI/CD", "TDD", "BDD",
    "Microservices", "GraphQL", "OAuth", "JWT", "OpenAPI",
}

TECHNOLOGIES_LIST = {
    # Databases
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "Firestore", "CockroachDB", "MariaDB", "Oracle",
    "MS SQL", "SQL Server", "Neo4j", "InfluxDB", "Snowflake", "BigQuery",
    # Cloud / Infrastructure
    "AWS", "Azure", "GCP", "Google Cloud", "Cloudflare", "Vercel", "Netlify",
    "Heroku", "DigitalOcean", "Linode",
    # Containers / Orchestration
    "Docker", "Kubernetes", "Helm", "Podman", "Docker Compose", "ECS", "EKS",
    "AKS", "GKE", "OpenShift",
    # IaC / DevOps
    "Terraform", "Ansible", "Pulumi", "CloudFormation", "Packer",
    "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "Travis CI",
    "ArgoCD", "Flux", "Spinnaker",
    # Messaging / Streaming
    "Kafka", "RabbitMQ", "SQS", "SNS", "Pub/Sub", "NATS", "ZeroMQ",
    # Monitoring / Observability
    "Prometheus", "Grafana", "Datadog", "New Relic", "Splunk", "ELK",
    "Logstash", "Kibana", "Jaeger", "OpenTelemetry", "Sentry",
    # Storage / CDN
    "S3", "GCS", "Azure Blob", "CloudFront", "Fastly",
    # Misc platforms
    "Nginx", "Apache", "HAProxy", "Istio", "Envoy", "Consul", "Vault",
}

SOFT_SKILLS_LIST = {
    "communication", "leadership", "teamwork", "collaboration", "mentoring",
    "problem-solving", "problem solving", "critical thinking", "adaptability",
    "time management", "organization", "attention to detail", "detail-oriented",
    "creativity", "innovation", "initiative", "ownership", "accountability",
    "empathy", "emotional intelligence", "conflict resolution", "negotiation",
    "presentation", "public speaking", "writing", "documentation",
    "prioritization", "multitasking", "deadline-driven", "self-motivated",
    "analytical", "strategic thinking", "decision-making", "coaching",
    "facilitation", "stakeholder management", "cross-functional", "interpersonal",
}

# Phrases/patterns that signal measurable accomplishments
_METRIC_PATTERN = re.compile(
    r"(?:"
    r"\d+\s*%|"                          # percentages: 40%, 99.9%
    r"\$\s*[\d,]+(?:\s*[KMB])?|"         # dollar amounts: $200K, $1.2M
    r"\d+\s*[KMB]\b|"                    # magnitudes: 5K, 2M
    r"\d+x\b|"                           # multipliers: 3x, 10x
    r"(?:reduced|improved|increased|decreased|optimized|scaled|cut|saved|"
    r"grew|delivered|launched|built|designed|led|managed|mentored|shipped|"
    r"automated|migrated|refactored|deployed)\b"  # achievement verbs
    r")",
    re.IGNORECASE,
)

EMPTY_RESULT = {
    "skills": [],
    "technologies": [],
    "experience_keywords": [],
    "soft_skills": [],
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Split text into whitespace-separated tokens, stripping punctuation."""
    return re.findall(r"[A-Za-z][\w\.\+\#\-\/]*", text)


def _match_against_list(text: str, word_list: set[str]) -> list[str]:
    """
    Case-insensitive phrase matching against a list.
    Returns matched terms using the canonical casing from the list.
    """
    found: set[str] = set()
    lower_text = text.lower()

    for term in word_list:
        # Use word-boundary matching to avoid partial matches (e.g. "C" in "CI/CD")
        pattern = r"(?<![A-Za-z0-9])" + re.escape(term.lower()) + r"(?![A-Za-z0-9])"
        if re.search(pattern, lower_text):
            found.add(term)

    return sorted(found)


# ── Public API ─────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> list[str]:
    """Return programming languages, frameworks, and dev tools found in text."""
    if not text or not text.strip():
        return []
    return _match_against_list(text, SKILLS_LIST)


def extract_technologies(text: str) -> list[str]:
    """Return infrastructure, platforms, databases, and cloud services found in text."""
    if not text or not text.strip():
        return []
    return _match_against_list(text, TECHNOLOGIES_LIST)


def extract_soft_skills(text: str) -> list[str]:
    """Return soft skills found in text."""
    if not text or not text.strip():
        return []
    return _match_against_list(text, SOFT_SKILLS_LIST)


def extract_experience_keywords(text: str) -> list[str]:
    """
    Extract short achievement/accomplishment phrases from text.
    Looks for sentences containing metrics or action verbs and returns
    condensed noun-phrase-like fragments (≤ 10 words).
    """
    if not text or not text.strip():
        return []

    phrases: list[str] = []
    # Split into sentences on period, newline, or semicolon
    sentences = re.split(r"[.\n;]+", text)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence.split()) < 3:
            continue
        if _METRIC_PATTERN.search(sentence):
            # Trim to ≤ 10 words
            words = sentence.split()
            phrase = " ".join(words[:10])
            phrases.append(phrase)

    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for p in phrases:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            result.append(p)

    return result


def extract_from_documents(doc_contents: str) -> dict:
    """
    Main entry point — same interface as the Claude-based extraction.
    Returns {"skills", "technologies", "experience_keywords", "soft_skills"}.
    Works completely offline; no API calls made.
    """
    if doc_contents == "No previewable documents found.":
        return dict(EMPTY_RESULT)

    return {
        "skills": extract_skills(doc_contents),
        "technologies": extract_technologies(doc_contents),
        "experience_keywords": extract_experience_keywords(doc_contents),
        "soft_skills": extract_soft_skills(doc_contents),
    }
