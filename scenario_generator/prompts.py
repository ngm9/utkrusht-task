"""
Prompt templates for the Task Scenario Generator.

All prompts used by scenario_generator.py for generating and evaluating
task scenarios across different technology categories and proficiency levels.
"""

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SCENARIO_SYSTEM_PROMPT = """You are a senior technical architect with 15+ years of experience designing practical assessments for hiring, mostly tech roles but not limited to software. It could be tech or tech allied roles like data scientists, data analysts, product managers etc. You create realistic, workplace-derived task scenarios that test specific competencies at precise proficiency levels.

CRITICAL RULE: You MUST calibrate scenario complexity EXACTLY to the specified proficiency level. A BASIC-level scenario must be solvable by someone with 1 years of experience in 20 minutes. An INTERMEDIATE scenario must be solvable by someone with 3-5 years of experience in 20 minutes. If you generate a scenario that requires advanced knowledge or would take an experienced developer more than the time limit, you have FAILED.

Your scenarios read like real bug reports, incident tickets, or feature requests — but they are SMALL, FOCUSED, and SCOPED to the candidate's level.

ENSURE that you follow the questions_prompt and role description when creating tasks!
"""

SCENARIO_SYSTEM_PROMPT_NON_CODE = """You are a senior assessment designer with 15+ years of experience creating work-simulation assessments for business, product, and non-engineering roles. You create realistic, workplace-derived task scenarios that test specific competencies at precise proficiency levels.

CRITICAL RULE: You MUST calibrate scenario complexity EXACTLY to the specified proficiency level and role. Scenarios must represent realistic decisions, analyses, plans, or critiques that the role would actually own or contribute to. If you generate a scenario that requires deep software engineering knowledge or would be more suited to a developer than the target role, you have FAILED.

Your scenarios read like real work items — an evaluation plan to critique, a set of metrics to review, a launch recommendation to draft, a rubric to improve, or a tradeoff to reason through — but they are SMALL, FOCUSED, and SCOPED to the candidate's level.

IMPORTANT: Do NOT generate coding tasks, debugging exercises, or software implementation challenges. The candidate is NOT a software engineer. Scenarios should test judgment, analysis, planning, communication, and domain reasoning appropriate to the role.

ENSURE that you follow the questions_prompt and role description when creating tasks!
"""


# ============================================================================
# NON-CODE CLASSIFICATION PROMPT
# ============================================================================

NON_CODE_CLASSIFICATION_PROMPT = """You are classifying whether an assessment should generate code-based or non-code-based task scenarios.

Return "non_code" if the role primarily involves judgment, analysis, planning, communication, or domain reasoning and would NOT be expected to write, debug, or review code as a primary job function.
Examples of non_code roles: Product Manager, Designer, Data Analyst, HR, Sales, Marketing, Legal, Operations Manager.

Return "code" if the role primarily involves writing, debugging, reviewing, or architecting software.
Examples of code roles: Software Engineer, Backend Developer, Data Engineer, DevOps Engineer, ML Engineer, Frontend Developer.

Role description: {role_description}
Competency name: {competency_name}
Proficiency: {proficiency}

Respond with only the word: "code" or "non_code"
"""


# ============================================================================
# PROFICIENCY GUARDRAILS — strict per-level complexity rules
# ============================================================================

PROFICIENCY_GUARDRAILS = {
    "BEGINNER": """PROFICIENCY LEVEL: BEGINNER (0-1 years of experience)
TIME LIMIT: 20-30 minutes

WHAT TO GENERATE:
- ONE clear bug fix OR ONE simple feature addition
- Test exactly 1 concept (e.g., fix a loop, add a function, correct a query)
- The scenario should feel like a junior developer's first real task at work
- Max 2 bullet points in the "Your Task" section
- Keep the entire scenario under 100 words

ALLOWED CONCEPTS (pick only 1 per scenario):
- Basic syntax fixes, variable/type errors, simple logic bugs
- Writing a single function or method
- Basic CRUD operations (one at a time, not all four)
- Simple conditional logic or loop fixes
- Basic string/array/list manipulation
- Reading from or writing to a file
- Simple SELECT/INSERT/UPDATE queries (one operation)

FORBIDDEN — DO NOT include any of these:
- Multiple endpoints or API routes
- Authentication, authorization, JWT, OAuth
- Caching, middleware, interceptors
- Async/await, promises, concurrency
- Database joins, transactions, indexes, migrations
- Design patterns (factory, singleton, observer, etc.)
- Testing frameworks or writing tests
- Deployment, CI/CD, Docker, containers
- Performance optimization or profiling
- Connection pooling, message queues
- State management libraries (Redux, Zustand, Context API)
- Third-party library configuration
- Error handling beyond basic try/catch

EXAMPLE OF A WELL-CALIBRATED BEGINNER SCENARIO:
**Current Implementation:** A Python script in a logistics company reads package weights from a list and calculates shipping costs, but the calculate_cost() function always returns 0 because it uses = instead of == in the weight-tier comparison and never enters the correct branch.
**Your Task:** Fix the comparison operators in calculate_cost() so each weight tier (0-5kg, 5-20kg, 20+kg) returns the correct price.
**Success Criteria:** calculate_cost(3) returns 5.99, calculate_cost(12) returns 12.99, and calculate_cost(25) returns 24.99.""",

    "BASIC": """PROFICIENCY LEVEL: BASIC (1-2 years of experience)
TIME LIMIT: 20-30 minutes

WHAT TO GENERATE:
- ONE focused feature implementation OR ONE multi-symptom bug (2-3 related issues)
- Test 2-3 concepts combined (e.g., class + error handling, API endpoint + validation)
- The scenario should feel like a ticket assigned to a junior-mid developer
- Max 3 bullet points in the "Your Task" section
- Keep the entire scenario under 150 words

ALLOWED CONCEPTS (combine 2-3 per scenario):
- Functions, modules, classes with basic OOP (init, methods, simple inheritance)
- Error handling with try/except, raising custom exceptions
- File I/O with context managers
- List comprehensions, dict operations, standard library usage
- Basic REST endpoint (single endpoint, not multiple)
- Simple database queries (single table, basic joins)
- Basic unit test writing (1-2 test cases)
- Reading/writing JSON or CSV
- Simple data validation
- Basic HTTP client usage (requests, fetch)

FORBIDDEN — DO NOT include any of these:
- System design or architecture decisions
- Microservices, service mesh, API gateway patterns
- Caching layers (Redis, Memcached, in-memory caching)
- CI/CD pipelines, deployment strategies, Docker configuration
- Advanced concurrency (thread pools, async workers, race conditions)
- Distributed systems concepts (eventual consistency, CAP theorem)
- Performance profiling, load testing, benchmarking
- Security hardening (CORS, CSP, rate limiting, input sanitization)
- Infrastructure (connection pooling, health checks, monitoring)
- Message queues or event streaming (unless the competency IS Kafka)
- GraphQL, WebSockets, Server-Sent Events
- Advanced state management (Redux, Zustand, MobX)
- Advanced ORM patterns (eager loading, N+1, query optimization)
- Background tasks, job queues, cron scheduling
- Multiple interacting services or components
- Comprehensive test suites (just 1-2 simple tests if testing is needed)

EXAMPLE OF A WELL-CALIBRATED BASIC SCENARIO:
**Current Implementation:** An e-commerce order service has an Order class with public fields and a process_order() function that silently returns None when the order amount is negative or the customer_id is missing, making it hard to debug failed orders.
**Your Task:** Encapsulate Order fields with proper getters/setters, add validation in __init__ that raises ValueError for invalid data, and wrap the database call in process_order() with try/except that logs the error and re-raises.
**Success Criteria:** Invalid orders raise ValueError with descriptive messages, database errors are logged and propagated instead of silently swallowed, and Order fields cannot be set to invalid values directly.""",

    "INTERMEDIATE": """PROFICIENCY LEVEL: INTERMEDIATE (3-5 years of experience)
TIME LIMIT: 30-40 minutes

WHAT TO GENERATE:
- System optimization, performance tuning, or architectural improvement
- Test 4-5 concepts combined
- The scenario should feel like a task for a mid-senior developer
- Max 5 bullet points in the "Your Task" section
- Keep the entire scenario under 250 words

ALLOWED CONCEPTS:
- All concepts from BASIC level, plus:
- API design with multiple endpoints
- Database optimization (indexes, query plans, connection pooling)
- Caching strategies and implementation
- Async/await patterns, concurrency handling
- Design patterns applied to real problems
- Comprehensive error handling and resilience
- Integration between multiple components
- Performance optimization with measurable targets
- Advanced ORM usage, query optimization
- Middleware, interceptors, decorators
- Comprehensive testing strategies

EXAMPLE OF A WELL-CALIBRATED INTERMEDIATE SCENARIO:
**Current Implementation:** A SaaS analytics dashboard's GET /api/reports/daily endpoint takes 8 seconds because it runs 3 sequential queries against a PostgreSQL events table (50M rows) with no indexes on event_type or created_at, uses synchronous psycopg2 with a new connection per request, and returns uncompressed JSON payloads averaging 2MB.
**Your Task:** Add composite indexes on (event_type, created_at) and (created_at) columns. Refactor the 3 sequential queries into a single CTE-based query. Switch to asyncpg with a connection pool (min=5, max=20). Add a 5-minute TTL cache for the report data. Implement response compression.
**Success Criteria:** Response time drops from 8s to under 800ms, connection pool eliminates per-request connection overhead, and cache hit rate exceeds 80% for repeated queries within the TTL window.""",
}


# ============================================================================
# PROFICIENCY GUARDRAILS — NON-CODE roles
# ============================================================================

PROFICIENCY_GUARDRAILS_NON_CODE = {
    "BEGINNER": """PROFICIENCY LEVEL: BEGINNER (0-1 years of experience)
TIME LIMIT: 10-15 minutes

WHAT TO GENERATE:
- ONE focused task: identify a single obvious gap, define 1-2 success metrics, or spot one clear risk
- The scenario should feel like a junior PM or analyst's first scoped work item
- Max 2 bullet points in the "Your Task" section
- Keep the entire scenario under 100 words

ALLOWED TASK TYPES (pick only 1 per scenario):
- Identify one obvious missing metric or evaluation gap in a given plan
- Name 1-2 success criteria for a described AI feature
- Flag one clear risk or blind spot in a simple launch plan
- Choose between two clearly described approaches and state why
- Describe what a good vs bad output looks like for a simple AI task

FORBIDDEN — DO NOT include any of these:
- Multi-step evaluation framework design
- Statistical concepts (confidence intervals, significance testing)
- A/B test design or analysis
- Complex tradeoff reasoning across more than 2 dimensions
- Writing rubrics or rating scales from scratch
- Defining human evaluation processes
- Anything requiring knowledge of specific ML models or architectures
- Coding, scripting, or tool configuration of any kind

EXAMPLE OF A WELL-CALIBRATED BEGINNER SCENARIO:
**Current Implementation:** A PM at a B2B SaaS company is launching an AI email-draft assistant. The current success plan only tracks open rate.
**Your Task:** Identify one additional metric the PM should track to know if the AI drafts are actually useful to users, and explain in one sentence why it matters more than open rate.
**Success Criteria:** The candidate names a user-outcome metric (e.g. reply rate, edit distance, time-to-send) and gives a brief, sensible rationale tied to actual user value.""",

    "BASIC": """PROFICIENCY LEVEL: BASIC (1-2 years of experience)
TIME LIMIT: 15 minutes

WHAT TO GENERATE:
- ONE focused work item: critique a flawed plan, choose between approaches with rationale, or draft a simple recommendation
- The scenario should feel like a ticket assigned to a junior PM or analyst with some context
- Max 3 bullet points in the "Your Task" section
- Keep the entire scenario under 150 words

ALLOWED TASK TYPES (combine 1-2 per scenario):
- Critique a flawed evaluation plan and identify 1-2 specific gaps
- Choose between two evaluation approaches and justify the choice
- Draft a simple launch recommendation based on provided eval results
- Identify what is missing from a test dataset or scenario coverage
- Flag a metric that is a weak proxy and suggest a better one
- Describe what should be in a basic human eval rubric for a given task

FORBIDDEN — DO NOT include any of these:
- Designing a full end-to-end evaluation framework from scratch
- Statistical analysis or A/B test power calculations
- Defining monitoring strategies post-launch
- Complex multi-stakeholder prioritization
- Anything requiring ML engineering knowledge
- Coding, scripting, or API usage of any kind

EXAMPLE OF A WELL-CALIBRATED BASIC SCENARIO:
**Current Implementation:** A food-delivery company's PM is reviewing eval results for an AI that suggests reorder items. The eval only measures click-through rate on suggestions. The team is ready to ship based on 72% CTR.
**Your Task:** Identify why CTR alone is a weak signal for this use case, name one product metric that would better reflect whether the AI is genuinely helping users, and state what threshold you'd want to see before recommending launch.
**Success Criteria:** The candidate explains the proxy-metric risk (CTR doesn't confirm a reorder happened), names a stronger metric (e.g. reorder completion rate, basket add rate), and proposes a reasonable threshold with a short rationale.""",

    "INTERMEDIATE": """PROFICIENCY LEVEL: INTERMEDIATE (3-5 years of experience)
TIME LIMIT: 20 minutes

WHAT TO GENERATE:
- A realistic work item requiring applied judgment across multiple dimensions
- The scenario should feel like a task for a mid-level PM or analyst with real product ownership
- Max 4 bullet points in the "Your Task" section
- Keep the entire scenario under 200 words
- IMPORTANT: There should be multiple valid approaches — the goal is to see the candidate's reasoning and prioritisation, not a single correct answer

ALLOWED TASK TYPES:
- Design a lightweight evaluation framework for a new AI feature (offline + online + human)
- Review a flawed eval plan and recommend specific improvements with justification
- Reason through a launch decision with conflicting signals (quality up, latency borderline, safety concern)
- Define a minimal but meaningful pre-launch eval set for a described AI use case
- Propose a post-launch monitoring strategy with specific metrics and alert thresholds
- Compare two evaluation strategies and recommend one, explaining the tradeoffs

WHAT MAKES AN INTERMEDIATE SCENARIO GOOD:
- Multiple valid paths to a correct outcome — reward the quality of reasoning
- Grounded in realistic product constraints (cost, time, data availability, team capacity)
- Requires the candidate to prioritise under uncertainty, not just list everything possible
- Subjective yet specific: the expected outcome is clear even if the path isn't

FORBIDDEN — DO NOT include any of these:
- Anything requiring ML engineering or model training knowledge
- Coding, scripting, or API usage of any kind
- Pure trivia about tool names, framework versions, or configuration syntax

EXAMPLE OF A WELL-CALIBRATED INTERMEDIATE SCENARIO:
**Current Implementation:** A logistics company is preparing to launch an AI that generates ETA explanations for delayed deliveries. Offline eval shows 89% accuracy on a 200-case test set. Latency is 1.4 seconds (budget: 1.2 seconds). The safety team has flagged 3 cases where the explanation blamed the customer incorrectly.
**Your Task:** Decide whether to launch, hold, or launch with guardrails. Specify (a) what you'd tell the team to fix before or after launch, (b) what one post-launch metric you'd monitor most closely in the first two weeks, and (c) what threshold would trigger a rollback.
**Success Criteria:** The candidate makes a clear, justified launch decision, addresses the latency and safety issues with proportionate actions, and names a specific post-launch metric with a sensible rollback threshold.""",
}


# ============================================================================
# GENERATION PROMPT — NON-CODE SCENARIOS
# ============================================================================

SCENARIO_GENERATION_PROMPT_NON_CODE = """Generate exactly {count} work-item style scenarios for a non-code assessment platform.

COMPETENCIES TO TEST:
{competencies_with_scopes}

{proficiency_guardrails}

COMPETENCY/ROLE: {competency_names}
Generate scenarios specifically relevant to the competency and role listed above. Use the competency scope descriptions to understand what areas of judgment, analysis, and decision-making are appropriate.

FORMAT RULES (apply to ALL proficiency levels):
Each scenario MUST follow this exact three-section structure with bold markdown headers:

**Current Implementation:** [1-2 sentences describing the current situation — a plan, a metric set, a decision in progress, an eval result, or a process that has a gap or needs a judgment call]

**Your Task:** [Clear deliverables describing what to critique/decide/recommend/design. Use bullet points ONLY if multiple items. Keep bullet count within the limit for this proficiency level]

**Success Criteria:** [1-2 sentences describing what a good response looks like — what reasoning or output demonstrates applied competence]

CRITICAL FORMAT CONSTRAINTS:
- Each scenario MUST be compact — respect the word limit for this proficiency level
- Each scenario MUST be a SEPARATE string in the JSON array — NEVER concatenate multiple scenarios into one string
- Include specific context: feature names, metric values, team constraints, product stage
- Use the exact bold headers: **Current Implementation:**, **Your Task:**, **Success Criteria:**
- Do NOT pad scenarios with extra requirements to fill space

{assessment_scope_block}

QUALITY RULES:
- Each scenario MUST use a DIFFERENT business domain (fintech, healthcare, logistics, e-commerce, SaaS, edtech, travel, food delivery, media/streaming, HR/recruiting, real estate)
- Each scenario MUST test a DIFFERENT area from the competency scope above
- Scenarios must feel like real product or business decisions, NOT academic exercises or trivia
- Do NOT ask the candidate to write, debug, fix, or review code
- Do NOT ask about tool installation, framework configuration, or API syntax
- MOST IMPORTANTLY: Every scenario must be completable by someone in the target role at the specified proficiency level within the time limit

{deduplication_block}

{eval_feedback_block}

OUTPUT FORMAT:
Return ONLY a JSON object with a single key "scenarios" containing an array of exactly {count} scenario strings. No other text, no markdown, no explanation.
"""


# ============================================================================
# GENERATION PROMPT — CODING SCENARIOS
# ============================================================================

SCENARIO_GENERATION_PROMPT = """Generate exactly {count} task scenarios for a coding assessment platform.

COMPETENCIES TO TEST:
{competencies_with_scopes}

{proficiency_guardrails}

TECHNOLOGY/COMPETENCY: {competency_names}
Generate scenarios that are specifically relevant to the competency names listed above. Use the competency scope descriptions to understand what technical concepts are appropriate.

{integration_rule_block}

FORMAT RULES (apply to ALL proficiency levels):
Each scenario MUST follow this exact three-section structure with bold markdown headers:

**Current Implementation:** [1-2 sentences describing the existing system and what is currently broken/slow/missing with specific technical details]

**Your Task:** [Clear deliverables describing what to fix/build/optimize. Use bullet points ONLY if multiple items. Keep bullet count within the limit for this proficiency level]

**Success Criteria:** [1-2 sentences describing the expected outcome with measurable targets where applicable]

CRITICAL FORMAT CONSTRAINTS:
- Each scenario MUST be compact — respect the word limit for this proficiency level
- Each scenario MUST be a SEPARATE string in the JSON array — NEVER concatenate multiple scenarios into one string
- Include specific technical details: endpoint paths, error messages, function names, table names
- Use the exact bold headers: **Current Implementation:**, **Your Task:**, **Success Criteria:**
- Do NOT pad scenarios with extra requirements to fill space — shorter is better than over-scoped

{assessment_scope_block}

QUALITY RULES:
- Each scenario MUST use a DIFFERENT business domain (fintech, healthcare, logistics, e-commerce, SaaS, edtech, travel, food delivery, IoT, media/streaming, HR/recruiting, real estate)
- Each scenario MUST test a DIFFERENT primary skill from the competency scope above
- Include realistic details: endpoint paths, function names, error messages, table names
- Every scenario must have a clear "current broken state" → "target fixed state"
- Do NOT create toy examples or tutorial-style exercises
- MOST IMPORTANTLY: Every scenario must be completable by a developer at the specified proficiency level within the time limit. If in doubt, make it simpler.

{deduplication_block}

{eval_feedback_block}

OUTPUT FORMAT:
Return ONLY a JSON object with a single key "scenarios" containing an array of exactly {count} scenario strings. No other text, no markdown, no explanation.
"""

# ============================================================================
# EVAL FEEDBACK BLOCK — passed to retry generation with failure reasons
# ============================================================================

EVAL_FEEDBACK_BLOCK = """PREVIOUS EVALUATION FEEDBACK — AVOID THESE ISSUES:
The following scenarios were rejected in the previous attempt. Learn from these failure reasons and ensure your new scenarios do NOT have the same problems:

{eval_feedback_text}

Fix these specific issues in your new scenarios."""

EVAL_FEEDBACK_BLOCK_EMPTY = ""


# ============================================================================
# ASSESSMENT SCOPE BLOCK — from background file's questions_prompt
# ============================================================================

ASSESSMENT_SCOPE_BLOCK = """ASSESSMENT SCOPE — ONLY test skills from this list:
Role Context: {role_context}

Skills to assess:
{questions_prompt}

IMPORTANT: Do NOT generate scenarios that require skills OUTSIDE this scope. If a concept is not listed above, the candidate is NOT expected to know it at this level."""

ASSESSMENT_SCOPE_BLOCK_EMPTY = ""


# ============================================================================
# MULTI-COMPETENCY INTEGRATION BLOCK
# ============================================================================

INTEGRATION_RULE_BLOCK = """MULTI-COMPETENCY INTEGRATION RULE:
You are given multiple competencies: {competency_list}.
Every scenario MUST test these competencies TOGETHER as one integrated problem.
Do NOT create a scenario that only uses one of the listed technologies.
The scenario should represent a real-world task where a developer uses ALL listed
technologies as part of one cohesive solution.
Example: "{example_pair}" = a {first_tech} service that uses {second_tech} for caching/sessions/queues/streaming —
NOT a standalone {first_tech} bug with no {second_tech} involvement."""

INTEGRATION_RULE_BLOCK_EMPTY = ""




# ============================================================================
# DEDUPLICATION BLOCK TEMPLATE
# ============================================================================

DEDUPLICATION_BLOCK = """EXISTING SCENARIOS — DO NOT DUPLICATE OR CLOSELY RESEMBLE THESE:
{existing_scenarios_text}

Each generated scenario must be substantially different from ALL of the above in terms of:
- Business domain (use a different industry/company type)
- Primary technical problem (address a different bug/feature/optimization)
- Technical approach (don't repeat the same fix pattern)"""

DEDUPLICATION_BLOCK_EMPTY = """No existing scenarios found for this competency combination. Generate fresh, diverse scenarios."""


# ============================================================================
# SCENARIO EVALUATION PROMPTS — coding and non-code variants
# ============================================================================

SCENARIO_EVAL_PROMPT_NON_CODE = """Evaluate these generated work-item scenarios for a {proficiency}-level {tech_stack} non-code assessment.

SCENARIOS:
{scenarios_numbered}

COMPETENCY SCOPE (what the candidate should know at this level):
{scope_text}

{proficiency_guardrails}

Evaluate EACH scenario STRICTLY against these criteria:

1. REALISM: Does it describe a plausible, grounded workplace situation — a real decision, plan, eval result, or process gap a PM or analyst would actually face? Reject toy examples or academic exercises.

2. PROFICIENCY FIT (MOST IMPORTANT): Is the complexity EXACTLY right for {proficiency} level?
   - FAIL if the task requires deep ML/engineering knowledge not expected at this role/level
   - FAIL if the scenario is so open-ended it has no clear expected outcome
   - FAIL if it would take significantly longer than the time limit to reason through
   - FAIL if the scenario is actually suited for a more senior level
   - When in doubt, FAIL — over-scoped is worse than under-scoped

3. NO CODE: Does the scenario require ZERO coding, scripting, debugging, or software implementation?
   - FAIL if the candidate needs to write, fix, or review any code to complete the task

4. SPECIFICITY: Does it include enough concrete context — metric values, feature names, product stage, team constraints — for the candidate to act on it without needing to ask clarifying questions?

5. CLARITY OF OUTCOME: Is it clear what a good response looks like, even if multiple valid approaches exist? The Success Criteria should describe the reasoning or output expected, not just restate the task.

For each scenario, return pass or fail with a brief reason if failing. Be STRICT on proficiency fit and the no-code rule."""


SCENARIO_EVAL_PROMPT = """Evaluate these generated task scenarios for a {proficiency}-level {tech_stack} coding assessment.

SCENARIOS:
{scenarios_numbered}

COMPETENCY SCOPE (what the candidate should know at this level):
{scope_text}

{proficiency_guardrails}

Evaluate EACH scenario STRICTLY against these criteria:

1. REALISM: Does it describe a plausible workplace problem? (not a toy/tutorial example)

2. PROFICIENCY FIT (MOST IMPORTANT): Is the complexity EXACTLY right for {proficiency} level?
   - FAIL if the scenario requires concepts from the FORBIDDEN list for this proficiency level
   - FAIL if it has more bullet points in "Your Task" than allowed for this level
   - FAIL if a developer at this level would need more than the time limit to complete it
   - FAIL if the scenario is actually suited for a higher proficiency level
   - When in doubt, FAIL — it is better to reject an over-scoped scenario than to accept one

3. DETAIL: Does it include specific technical details (endpoint paths, function names, error messages)?

4. COMPLETENESS: Does it clearly describe both the current broken state AND the target fixed state?

5. SCOPE: Can a competent {proficiency}-level developer REALISTICALLY complete this within the time limit?
   - BEGINNER/BASIC: 20-30 minutes
   - INTERMEDIATE: 30-40 minutes
   - Count the number of distinct changes required. If there are more than the bullet-point limit allows, FAIL.

For each scenario, return pass or fail with a brief reason if failing. Be STRICT — reject any scenario that is even slightly over-scoped for the proficiency level."""


# ============================================================================
# STRUCTURED OUTPUT SCHEMAS
# ============================================================================

SCENARIO_GENERATION_SCHEMA = {
    "name": "scenario_generation_response",
    "schema": {
        "type": "object",
        "properties": {
            "scenarios": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of generated task scenario strings"
            }
        },
        "required": ["scenarios"],
        "additionalProperties": False
    },
    "strict": True
}

SCENARIO_EVAL_SCHEMA = {
    "name": "scenario_eval_response",
    "schema": {
        "type": "object",
        "properties": {
            "evaluations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scenario_index": {
                            "type": "number",
                            "description": "0-based index of the scenario being evaluated"
                        },
                        "pass": {
                            "type": "boolean",
                            "description": "Whether the scenario passed all criteria"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief reason if the scenario failed, empty string if passed"
                        }
                    },
                    "required": ["scenario_index", "pass", "reason"],
                    "additionalProperties": False
                },
                "description": "Evaluation result for each scenario"
            }
        },
        "required": ["evaluations"],
        "additionalProperties": False
    },
    "strict": True
}


# ============================================================================
# HELPER — per-proficiency limits for structural validation
# ============================================================================

PROFICIENCY_LIMITS = {
    "BEGINNER": {"max_words": 150, "max_bullets": 2, "max_chars": 1200},
    "BASIC":    {"max_words": 200, "max_bullets": 3, "max_chars": 1800},
    "INTERMEDIATE": {"max_words": 300, "max_bullets": 5, "max_chars": 3000},
}


def get_proficiency_guardrails(proficiency: str) -> str:
    """Return the guardrails block for the given proficiency level."""
    return PROFICIENCY_GUARDRAILS.get(proficiency, PROFICIENCY_GUARDRAILS["BASIC"])


def build_assessment_scope_block(background: dict = None) -> str:
    """Build the assessment scope block from background file data."""
    if not background:
        return ASSESSMENT_SCOPE_BLOCK_EMPTY

    role_context = background.get("role_context", "")
    questions_prompt = background.get("questions_prompt", "")

    if not role_context and not questions_prompt:
        return ASSESSMENT_SCOPE_BLOCK_EMPTY

    return ASSESSMENT_SCOPE_BLOCK.format(
        role_context=role_context,
        questions_prompt=questions_prompt,
    )


def build_integration_rule_block(competency_names_list: list) -> str:
    """Build the multi-competency integration rule block.

    Returns an empty string if only 1 competency is present.
    Returns an explicit integration instruction if 2+ competencies.
    """
    if not competency_names_list or len(competency_names_list) < 2:
        return INTEGRATION_RULE_BLOCK_EMPTY

    competency_list = ", ".join(competency_names_list)
    first_tech = competency_names_list[0]
    second_tech = competency_names_list[1]
    example_pair = " + ".join(competency_names_list)

    return INTEGRATION_RULE_BLOCK.format(
        competency_list=competency_list,
        example_pair=example_pair,
        first_tech=first_tech,
        second_tech=second_tech,
    )


def build_generation_prompt(
    competencies_with_scopes: str,
    proficiency: str,
    competency_names: str,
    count: int,
    existing_scenarios: list,
    eval_feedback: list = None,
    background: dict = None,
    competency_names_list: list = None,
    is_non_code: bool = False,
) -> str:
    """Build the complete generation prompt with all conditional sections filled in.

    Args:
        competency_names: Comma-separated competency names from the input files.
        eval_feedback: Optional list of dicts with 'scenario' and 'reason' keys from
                       previous evaluation failures, so the LLM can avoid the same mistakes.
        background: Optional background dict from background_forQuestions_*.json.
        competency_names_list: Optional list of individual competency name strings.
                               Used to generate multi-competency integration rules.
        is_non_code: If True, use the non-code generation prompt and guardrails.
    """
    if is_non_code:
        guardrails = PROFICIENCY_GUARDRAILS_NON_CODE.get(proficiency, PROFICIENCY_GUARDRAILS_NON_CODE["BASIC"])
    else:
        guardrails = get_proficiency_guardrails(proficiency)

    scope_block = build_assessment_scope_block(background)

    if existing_scenarios:
        numbered = "\n".join(
            f"{i+1}. {s[:300]}{'...' if len(s) > 300 else ''}"
            for i, s in enumerate(existing_scenarios)
        )
        dedup_block = DEDUPLICATION_BLOCK.format(existing_scenarios_text=numbered)
    else:
        dedup_block = DEDUPLICATION_BLOCK_EMPTY

    if eval_feedback:
        feedback_lines = []
        for i, fb in enumerate(eval_feedback, 1):
            feedback_lines.append(
                f"{i}. Rejected scenario: \"{fb['scenario'][:200]}...\"\n   Reason: {fb['reason']}"
            )
        feedback_block = EVAL_FEEDBACK_BLOCK.format(
            eval_feedback_text="\n\n".join(feedback_lines)
        )
    else:
        feedback_block = EVAL_FEEDBACK_BLOCK_EMPTY

    if is_non_code:
        return SCENARIO_GENERATION_PROMPT_NON_CODE.format(
            count=count,
            competencies_with_scopes=competencies_with_scopes,
            proficiency_guardrails=guardrails,
            competency_names=competency_names,
            assessment_scope_block=scope_block,
            deduplication_block=dedup_block,
            eval_feedback_block=feedback_block,
        )

    integration_block = build_integration_rule_block(competency_names_list or [])

    return SCENARIO_GENERATION_PROMPT.format(
        count=count,
        competencies_with_scopes=competencies_with_scopes,
        proficiency_guardrails=guardrails,
        competency_names=competency_names,
        integration_rule_block=integration_block,
        assessment_scope_block=scope_block,
        deduplication_block=dedup_block,
        eval_feedback_block=feedback_block,
    )


def build_eval_prompt(
    scenarios: list,
    proficiency: str,
    tech_stack: str,
    scope_text: str,
    is_non_code: bool = False,
) -> str:
    """Build the evaluation prompt for generated scenarios."""
    numbered = "\n".join(
        f"Scenario {i+1}:\n{s}\n"
        for i, s in enumerate(scenarios)
    )
    if is_non_code:
        guardrails = PROFICIENCY_GUARDRAILS_NON_CODE.get(proficiency, PROFICIENCY_GUARDRAILS_NON_CODE["BASIC"])
        return SCENARIO_EVAL_PROMPT_NON_CODE.format(
            proficiency=proficiency,
            tech_stack=tech_stack,
            scenarios_numbered=numbered,
            scope_text=scope_text,
            proficiency_guardrails=guardrails,
        )
    guardrails = get_proficiency_guardrails(proficiency)
    return SCENARIO_EVAL_PROMPT.format(
        proficiency=proficiency,
        tech_stack=tech_stack,
        scenarios_numbered=numbered,
        scope_text=scope_text,
        proficiency_guardrails=guardrails,
    )
