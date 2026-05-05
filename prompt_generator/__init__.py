"""
Prompt Generator package — agent that synthesizes new task generation prompt files.

Uses existing prompt files (in task_generation_prompts/) and successful tasks in
Supabase as a knowledge base. A Generator → Verifier → Refiner DSPy loop produces
a new .py file that registers a PROMPT_REGISTRY entry for the given (competencies,
proficiency) combination.

Usage as CLI:
    python -m prompt_generator --name "Python, SQL" --proficiency BASIC

Usage as module:
    from prompt_generator.classifier import classify_task_category, Competency
    from prompt_generator.retriever import retrieve_references

See docs/research/prompt-generator-agent.md for design.
"""
