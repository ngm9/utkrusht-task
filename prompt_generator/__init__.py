"""
Prompt Generator package.

Generates task generation prompt template files (.py) for coding assessments
based on technology stack, proficiency level, and deployment model.

Usage as CLI:
    python -m prompt_generator --techs "Java,Kafka" --proficiency BASIC --deployment docker-backend

Usage as module:
    from prompt_generator import generate_prompt, derive_registry_key, derive_tech_slug
"""

from prompt_generator.generator import (
    generate_prompt,
    create_openai_client,
    format_cost_summary,
    get_output_path,
)
from prompt_generator.deployment_models import (
    derive_registry_key,
    derive_tech_slug,
    canonicalize_tech_name,
    DEPLOYMENT_MODELS,
    CANONICAL_TECH_NAMES,
)

__all__ = [
    "generate_prompt",
    "create_openai_client",
    "format_cost_summary",
    "get_output_path",
    "derive_registry_key",
    "derive_tech_slug",
    "canonicalize_tech_name",
    "DEPLOYMENT_MODELS",
    "CANONICAL_TECH_NAMES",
]
