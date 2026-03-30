"""
Deployment model definitions and tech name utilities for the prompt generator.
"""

import re
from typing import List


# ============================================================================
# CANONICAL TECH NAMES — CLI input → Display name for PROMPT_REGISTRY key
# ============================================================================

CANONICAL_TECH_NAMES = {
    "react": "ReactJs",
    "reactjs": "ReactJs",
    "node": "NodeJs",
    "nodejs": "NodeJs",
    "node.js": "NodeJs",
    "express": "ExpressJS",
    "expressjs": "ExpressJS",
    "fastapi": "FastAPI",
    "python-fastapi": "FastAPI",
    "python": "Python",
    "springboot": "SpringBoot",
    "java-springboot": "SpringBoot",
    "spring-boot": "SpringBoot",
    "spring-mvc": "Spring MVC",
    "spring-webservices": "Spring Web Services",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "typescript": "TypeScript",
    "nextjs": "NextJs",
    "next.js": "NextJs",
    "docker": "Docker",
    "kafka": "Kafka",
    "redis": "Redis",
    "go": "Golang",
    "golang": "Golang",
    "sql": "SQL",
    "java": "Java",
    "shell": "Shell Script",
    "shell-script": "Shell Script",
    "apache-camel": "Apache Camel",
    "langchain": "LangChain",
    "rag": "RAG",
    "microservices": "Microservices",
    "system-design": "System Design",
    "pandas": "Pandas",
    "numpy": "Numpy",
    "vector-databases": "Vector Databases",
}


def canonicalize_tech_name(raw: str) -> str:
    """Map a raw CLI tech name to its canonical display name.

    Lookup is case-insensitive. Falls back to raw.title() if not found.
    """
    return CANONICAL_TECH_NAMES.get(raw.strip().lower(), raw.strip().title())


def derive_registry_key(techs: List[str], proficiency: str) -> str:
    """Build the PROMPT_REGISTRY key from tech names + proficiency.

    Each tech gets its own (PROFICIENCY) suffix, sorted alphabetically.
    Example: ["Java", "Kafka"], "BASIC" -> "Java (BASIC), Kafka (BASIC)"
    """
    proficiency = proficiency.upper()
    entries = []
    for t in techs:
        canonical = canonicalize_tech_name(t)
        entries.append(f"{canonical} ({proficiency})")
    return ", ".join(sorted(entries))


def derive_tech_slug(techs: List[str]) -> str:
    """Derive a snake_case slug from tech names for file/variable naming.

    Example: ["Java", "Kafka"] -> "java_kafka"
             ["Node.js", "MongoDB"] -> "nodejs_mongodb"
    """
    joined = "_".join(techs)
    slug = joined.lower()
    slug = re.sub(r"[.\-\s]+", "_", slug)
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    slug = re.sub(r"_+", "_", slug)
    slug = slug.strip("_")
    return slug


# ============================================================================
# DEPLOYMENT MODELS — evaluation criteria for each deployment type
# ============================================================================

DEPLOYMENT_MODELS = {
    "no-docker": {
        "description": "No Docker infrastructure. Pure source code + README.",
        "when_used": "React, pure Python, Express, basic Java, TypeScript",
        "required_mentions": ["README.md", ".gitignore"],
        "forbidden_mentions": ["docker-compose", "Dockerfile", "run.sh", "kill.sh", "init_database.sql"],
        "eval_criteria": (
            "The generated prompt MUST NOT include any Docker, container, or docker-compose "
            "instructions. No run.sh or kill.sh scripts. The task should be a pure source code "
            "project with README.md and .gitignore only. The candidate runs the project locally "
            "with standard tooling (npm start, python main.py, mvn spring-boot:run, etc.)."
        ),
    },
    "docker-backend": {
        "description": "Single app service + database in Docker Compose.",
        "when_used": "SQL, FastAPI+DB, Node+DB, Java+DB, Python+Redis",
        "required_mentions": ["docker-compose", "Dockerfile", "run.sh", "kill.sh", "README.md", ".gitignore"],
        "forbidden_mentions": [],
        "eval_criteria": (
            "The generated prompt MUST instruct the task LLM to create:\n"
            "- docker-compose.yml: NO version field, hardcoded env vars (no .env file), "
            "depends_on with health checks, volume mounts for DB initialization\n"
            "- run.sh: docker-compose up -d --build, health check loops for database first then "
            "app service, print success message with service URLs, exit with error if any service fails\n"
            "- kill.sh: docker-compose down -v, docker image prune -a -f, docker system prune -f, "
            "rm -rf /root/task, all commands with || true for idempotency\n"
            "- init_database.sql (if applicable): single file that creates schema and seeds data, "
            "no solution hints in comments\n"
            "The prompt must emphasize that all infrastructure files must produce a working "
            "deployment that starts without manual intervention."
        ),
    },
    "docker-multi-service": {
        "description": "Multiple services (2-4) with Docker Compose orchestration.",
        "when_used": "Microservices, Kafka, distributed systems, event-driven architectures",
        "required_mentions": ["docker-compose", "Dockerfile", "run.sh", "kill.sh", "README.md", ".gitignore"],
        "forbidden_mentions": [],
        "eval_criteria": (
            "The generated prompt MUST instruct the task LLM to create:\n"
            "- docker-compose.yml: NO version field, 2-4 independent services each with own "
            "Dockerfile, proper inter-service networking, depends_on with health checks for "
            "startup ordering, hardcoded env vars, named volumes for persistence\n"
            "- run.sh: docker-compose up -d --build, sequential health check loops for each "
            "service (databases first, then app services), print all service URLs on success, "
            "exit with error code if any service fails to become healthy\n"
            "- kill.sh: docker-compose down -v, docker image prune -a -f, docker system prune -f, "
            "rm -rf /root/task, all commands with || true\n"
            "- Multiple Dockerfiles: one per service, each self-contained\n"
            "- init_database.sql (if applicable): single file for schema + seed data\n"
            "The prompt must emphasize per-service health checks, startup ordering, and "
            "inter-service communication patterns (REST, async, message queues)."
        ),
    },
    "design-only": {
        "description": "Design document only. No source code or Docker.",
        "when_used": "System Design tasks",
        "required_mentions": ["README.md", "DESIGN_TEMPLATE.md"],
        "forbidden_mentions": ["docker-compose", "Dockerfile", "run.sh", "kill.sh", "source code", "package.json", "requirements.txt", "pom.xml", "go.mod"],
        "eval_criteria": (
            "The generated prompt MUST instruct the task LLM to create ONLY documentation files: "
            "README.md with the design problem description and DESIGN_TEMPLATE.md with guiding "
            "sections for the candidate to fill in. NO source code files, NO Docker files, NO "
            "build files. The candidate produces a design document evaluating their architectural "
            "thinking, trade-off reasoning, and communication clarity."
        ),
    },
}


# ============================================================================
# PROFICIENCY TIME RANGES
# ============================================================================

PROFICIENCY_TIME_RANGES = {
    "BEGINNER": "20-30",
    "BASIC": "30-45",
    "INTERMEDIATE": "45-60",
}
