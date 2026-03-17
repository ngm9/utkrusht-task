"""Evaluation prompts for PR Review generation gates."""

BASE_REPO_EVAL_PROMPT = """Evaluate this generated base repository for use in a PR review assessment.

COMPETENCIES BEING TESTED:
{competencies_text}

CODE FILES:
{code_files_text}

Evaluate STRICTLY against these criteria:

1. CODE QUALITY: Is the code clean, well-structured, and following best practices for the tech stack?
2. CONSISTENCY: Are patterns consistent throughout (naming, error handling, structure)?
3. REALISM: Does this look like a real project, not a tutorial or toy example?
4. MINIMUM SIZE: Are there at least 3 source code files (excluding README, .gitignore, config files)?
5. REVIEWABILITY: Is the codebase structured enough that a PR against it would be meaningful to review?

If the base repo PASSES all criteria, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["list of criteria met"],
  "feedback": ""
}}

If the base repo FAILS any criteria, respond in JSON:
{{
  "pass": false,
  "issues": ["specific issues found"],
  "validated_criteria": ["criteria that were met"],
  "feedback": "detailed explanation of what needs to be fixed"
}}"""

PR_EVAL_PROMPT = """Evaluate this generated PR and answer key for a code review assessment.

BASE REPOSITORY (the clean codebase the PR is against):
{base_repo_text}

PR FILES (modified/added by the PR):
{pr_files_text}

ANSWER KEY:
{answer_key_text}

CRITICAL CONTEXT: This PR is INTENTIONALLY flawed. It is part of a CODE REVIEW ASSESSMENT where candidates must FIND the flaws. The flaws are DELIBERATE. Do NOT fail the evaluation because the PR contains bugs, bad practices, or missing error handling. Those are FEATURES, not bugs.

Your job is ONLY to check these 3 things:

1. ANSWER KEY COMPLETENESS: Does the answer key capture all the intentional flaws visible in the code? Are there obvious issues in the PR code that the answer key does not mention?
2. MODIFIED FILES VALIDITY: Do all file paths in modified_files exist in the base repository?
3. PR COMPILES: Does the PR code look syntactically valid (ignoring the intentional logic/design flaws)?

PASS the evaluation if all 3 criteria are met. Do NOT evaluate code quality — the code is SUPPOSED to be flawed.

If the PR PASSES, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["answer key complete", "modified files valid", "code syntactically valid"],
  "feedback": ""
}}

If the PR FAILS, respond in JSON:
{{
  "pass": false,
  "issues": ["specific issue — e.g. answer key missing a flaw, or modified file not in base repo"],
  "validated_criteria": ["criteria that were met"],
  "feedback": "what specifically needs to change"
}}"""
