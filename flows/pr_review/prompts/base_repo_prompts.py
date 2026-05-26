"""Prompts for Phase 1: generating clean, well-structured base repositories."""

BASE_REPO_SYSTEM_PROMPT = """You are a senior software engineer writing clean, production-quality code for a real project. Your code should:
- Follow industry best practices and idiomatic patterns for the tech stack
- Have consistent naming, error handling, and structure throughout
- Be realistic -- not a tutorial or toy example
- Include a clear README.md describing the project
- Have proper configuration files (.gitignore, dependency files, etc.)"""

BASE_REPO_GENERATION_PROMPT = """Generate a complete, well-structured codebase for the following project.

COMPETENCIES:
{competencies_with_scopes}

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
- Generate a realistic project with at least 4-5 source code files (excluding README, .gitignore, config files)
- Code must follow consistent patterns throughout (naming conventions, error handling, project structure)
- Include proper dependency/config files for the tech stack
- The codebase should be substantial enough that a PR against it is meaningful to review
- README.md should describe what the project does, its structure, and how to run it
- Do NOT include any intentional bugs or issues -- this is the "good" baseline code

OUTPUT FORMAT:
Return ONLY a JSON object with a single key "code_files" containing file paths as keys and file contents as values. No markdown, no explanation.

{eval_feedback_block}"""

EVAL_FEEDBACK_BLOCK = """PREVIOUS EVALUATION FEEDBACK -- FIX THESE ISSUES:
{feedback_text}"""

EVAL_FEEDBACK_BLOCK_EMPTY = ""
