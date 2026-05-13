"""
Task category classification — determines the infrastructure category of a task
from its competency mix.

Categories drive what Docker/file structure the generated prompt should specify:
  - PURE_CODE         : language only, no infrastructure (e.g. Python BASIC, React)
  - DB_ONLY           : SQL/database tasks with no app code (e.g. SQL BASIC)
  - SCRIPT_AND_DB     : Python/Node script that talks to a DB (e.g. Python+SQL)
  - APP_AND_DB        : web framework + database (e.g. Node+Postgres, FastAPI+DB)
  - FRONTEND          : browser-side only (React, Next, Vue)
  - LLM_FRAMEWORK     : Python + LLM ecosystem (Langchain, Llamaindex, RAG)
  - VECTOR_DB         : Python + vector store (Milvus, Chroma, Pinecone)
  - MESSAGING         : Kafka/queue tasks paired with a backend
  - MICROSERVICES     : multi-service architecture
  - CONTAINERIZED_APP : language/framework packaged into Docker/Kubernetes,
                        no DB (e.g. Java+Docker, Python+FastAPI+Docker)
  - NON_CODE          : evaluation/PM tasks with no executable code
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class TaskCategory(str, Enum):
    PURE_CODE = "pure_code"
    DB_ONLY = "db_only"
    SCRIPT_AND_DB = "script_and_db"
    APP_AND_DB = "app_and_db"
    FRONTEND = "frontend"
    LLM_FRAMEWORK = "llm_framework"
    VECTOR_DB = "vector_db"
    MESSAGING = "messaging"
    MICROSERVICES = "microservices"
    CONTAINERIZED_APP = "containerized_app"
    NON_CODE = "non_code"


# Competency name fragments grouped by what they imply about infrastructure.
# Lowercased; matched as substring against competency names.
# "redis" intentionally added alongside legacy "redis_cache" so a plain "Redis"
# competency name is recognised as a data store.
_DB_TOKENS = (
    "sql", "postgres", "postgresql", "mongo", "mongodb", "mysql",
    "redis", "redis_cache",
)
_WEB_FRAMEWORK_TOKENS = (
    "fastapi", "flask", "django", "express", "nest", "spring boot", "spring mvc",
    "spring webservices", "rails", "laravel",
)
_FRONTEND_TOKENS = ("react", "next", "vue", "angular", "svelte", "html and css", "javascript", "typescript")
_BACKEND_LANG_TOKENS = ("python", "java", "go", "golang", "node", "nodejs", "ruby", "rust", "kotlin", "php")

# Languages that almost always imply a web app when combined with a DB,
# even without an explicit framework competency. Python is flexible (script or app),
# so it's NOT in this set — Python + DB defaults to SCRIPT_AND_DB.
_WEB_APP_LANG_TOKENS = ("node", "nodejs", "java", "ruby", "php", "kotlin")
_LLM_TOKENS = ("langchain", "llamaindex", "llama-index", "rag", "rags")
_VECTOR_DB_TOKENS = ("vector database", "vector db", "pinecone", "milvus", "chroma", "weaviate", "qdrant", "faiss")
_MESSAGING_TOKENS = ("kafka", "rabbitmq", "pubsub", "sqs", "sns")
_MICROSERVICES_TOKENS = ("microservices",)
# Containerization signals — Docker/Kubernetes change task structure even when
# no DB is present. Without this, Java+Docker fell through to PURE_CODE and the
# generated prompt lost all infrastructure context.
_CONTAINER_TOKENS = ("docker", "kubernetes", "k8s", "podman", "containerization")
_NON_CODE_TOKENS = (
    "ai evals for product managers",
    "voice agent evaluation",
    "prompt engineering",
)


@dataclass(frozen=True)
class Competency:
    """A normalized competency for classification."""
    name: str
    proficiency: str

    @property
    def name_lower(self) -> str:
        return self.name.lower()


def _matches_any(name_lower: str, tokens: Iterable[str]) -> bool:
    return any(tok in name_lower for tok in tokens)


def _has_db(comps: list[Competency]) -> bool:
    return any(_matches_any(c.name_lower, _DB_TOKENS) for c in comps)


def _has_web_framework(comps: list[Competency]) -> bool:
    return any(_matches_any(c.name_lower, _WEB_FRAMEWORK_TOKENS) for c in comps)


def _has_backend_language(comps: list[Competency]) -> bool:
    # Backend language without a web framework attached
    return any(
        _matches_any(c.name_lower, _BACKEND_LANG_TOKENS)
        and not _matches_any(c.name_lower, _WEB_FRAMEWORK_TOKENS)
        for c in comps
    )


def _has_frontend_only(comps: list[Competency]) -> bool:
    # Pure frontend — no backend lang, no DB, no framework
    return all(
        _matches_any(c.name_lower, _FRONTEND_TOKENS)
        and not _matches_any(c.name_lower, _BACKEND_LANG_TOKENS)
        for c in comps
    )


def _has_container(comps: list[Competency]) -> bool:
    return any(_matches_any(c.name_lower, _CONTAINER_TOKENS) for c in comps)


def classify_task_category(competencies: list[Competency]) -> TaskCategory:
    """Classify a task's infrastructure category from its competency mix.

    Order matters — most-specific categories are checked first.
    """
    if not competencies:
        raise ValueError("classify_task_category requires at least one competency")

    names_lower = [c.name_lower for c in competencies]
    joined = " ".join(names_lower)

    # NON_CODE first — it's a hard rule-out for everything else
    if any(_matches_any(n, _NON_CODE_TOKENS) for n in names_lower):
        return TaskCategory.NON_CODE

    # MICROSERVICES — explicit microservices competency
    if _matches_any(joined, _MICROSERVICES_TOKENS):
        return TaskCategory.MICROSERVICES

    # MESSAGING — Kafka/queues paired with backend
    if _matches_any(joined, _MESSAGING_TOKENS):
        return TaskCategory.MESSAGING

    # LLM_FRAMEWORK — Langchain, Llamaindex, RAG (always Python-based)
    if _matches_any(joined, _LLM_TOKENS):
        return TaskCategory.LLM_FRAMEWORK

    # VECTOR_DB — vector stores (always paired with Python in practice)
    if _matches_any(joined, _VECTOR_DB_TOKENS):
        return TaskCategory.VECTOR_DB

    # FRONTEND — purely frontend competencies
    if _has_frontend_only(competencies):
        return TaskCategory.FRONTEND

    has_db = _has_db(competencies)
    has_framework = _has_web_framework(competencies)
    has_backend = _has_backend_language(competencies)
    has_web_app_lang = any(_matches_any(c.name_lower, _WEB_APP_LANG_TOKENS) for c in competencies)
    has_container = _has_container(competencies)

    # APP_AND_DB — explicit web framework + database, OR a web-app-defaulting language + DB.
    # Node.js/Java/Ruby + DB conventionally means a web app, even without an explicit framework.
    # Checked before CONTAINERIZED_APP because a DB is the stronger infrastructure signal —
    # an app+DB task that also uses Docker is still primarily app+DB.
    if has_db and (has_framework or has_web_app_lang):
        return TaskCategory.APP_AND_DB

    # SCRIPT_AND_DB — flexible-language backend + database, NO web framework
    # (Python + SQL falls here; Python is a script unless FastAPI/Flask is named.)
    if has_db and has_backend:
        return TaskCategory.SCRIPT_AND_DB

    # DB_ONLY — only a DB competency, nothing else (e.g. SQL BASIC alone)
    if has_db:
        return TaskCategory.DB_ONLY

    # CONTAINERIZED_APP — Docker/Kubernetes paired with a language or framework,
    # no DB. Catches Java+Docker, Python+Docker, Go+Docker, Python+FastAPI+Docker.
    if has_container and (has_backend or has_framework):
        return TaskCategory.CONTAINERIZED_APP

    # Default — pure code (language-only or framework-only without DB)
    return TaskCategory.PURE_CODE


def to_competencies(items: list[dict]) -> list[Competency]:
    """Convert dicts (e.g. from competency JSON files) into Competency objects."""
    return [
        Competency(name=item["name"], proficiency=item.get("proficiency", "BASIC"))
        for item in items
    ]
