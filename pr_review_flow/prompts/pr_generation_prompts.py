"""Prompts for Phase 2: generating flawed PRs with answer keys."""

PR_SYSTEM_PROMPT = """You are simulating a developer submitting a pull request. The PR should look like genuine work -- it implements real functionality but contains realistic mistakes that a code reviewer should catch. The flaws should NOT look planted or artificial. They should be the kind of mistakes a real developer makes under time pressure or from inexperience."""

PR_GENERATION_PROMPT = """Generate a pull request with intentional flaws against the following codebase.

BASE REPOSITORY FILES:
{base_repo_files}

PR INTENT:
{pr_intent}

INJECTED FLAWS (introduce ALL of these -- these are NOT shown to the candidate):
{injected_flaws}

REQUIREMENTS:
- The PR should implement the feature/fix described in PR Intent
- Introduce ALL the flaws listed above naturally -- they should look like real developer mistakes
- The PR title and description should be what a developer would actually write (the description itself may be vague/incomplete if that is one of the listed flaws)
- modified_files: provide the COMPLETE new content of each modified file (not a diff)
- added_files: provide complete content of any new files the PR introduces
- deleted_files: list any files the PR removes (empty array if none)
- Generate a complete answer_key listing every intentional flaw with file, line_range, category, severity, description, and correct_approach
- The overall_verdict should be "request_changes" if any flaw is critical/major, "approve_with_comments" if all flaws are minor/nitpick
- Include pr_description_issues if the PR description itself has problems

OUTPUT FORMAT:
Return ONLY a JSON object with keys: pr_title, pr_description, modified_files, added_files, deleted_files, answer_key. No markdown, no explanation.

{eval_feedback_block}"""

EVAL_FEEDBACK_BLOCK = """PREVIOUS EVALUATION FEEDBACK -- FIX THESE ISSUES:
{feedback_text}"""

EVAL_FEEDBACK_BLOCK_EMPTY = ""
