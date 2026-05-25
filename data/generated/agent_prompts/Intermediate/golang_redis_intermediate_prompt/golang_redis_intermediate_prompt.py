PROMPT_GOLANG_REDIS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company, the role expectations, and how Golang and Redis are likely used together in this environment.
"""

PROMPT_GOLANG_REDIS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Golang + Redis assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- The task should assess practical implementation, debugging, optimization, and tradeoff reasoning rather than trivia.
- The task must stay within a script-and-db setup: Docker + Redis + Go script, with no web framework and no REST API requirement.

Before proceeding to the detailed task generation instructions, briefly confirm your understanding by answering:

1. What will the task be about? Describe the business workflow, Redis usage pattern, and the production-style issue the candidate will solve.
2. What will the task look like? Describe the expected repository shape, the kind of Go changes required, the Redis behaviors involved, and why this fits INTERMEDIATE Golang + Redis proficiency.

Keep the summary brief and concrete.
"""

PROMPT_GOLANG_REDIS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a senior backend architect experienced in Go and Redis, generate a realistic intermediate-level assessment task for a candidate with Golang and Redis proficiency. The task must present a working Go codebase and Redis-backed workflow with intentional correctness, performance, and resilience issues that the candidate must diagnose and improve.

The generated task must evaluate practical skill in:
- idiomatic Go structure, packages, interfaces, error handling, and tests
- concurrency-safe Go implementation using goroutines, channels, context cancellation, or worker coordination where appropriate
- Redis key-space design, TTL strategy, and suitable data structure selection
- reducing Redis round trips using pipelining or batched access
- preserving correctness under concurrent execution and partial Redis failures
- cache invalidation or refresh behavior aligned with the business workflow
- basic observability and measurable verification of improvement

## HARD SCOPE BOUNDARIES
Stay strictly within the competency scope for INTERMEDIATE Golang and INTERMEDIATE Redis.

Allowed and encouraged:
- Go core syntax, structs, interfaces, pointers, packages, modules
- goroutines, channels, worker pools, context usage, race-condition prevention
- custom errors, wrapped errors, logging, tests with the testing package
- Redis Strings, Hashes, Sets, Sorted Sets, Lists, Streams when naturally relevant
- Redis key naming, TTLs, pipelining, MULTI/EXEC, WATCH, Lua only if naturally needed for a focused intermediate task
- cache-aside, lazy invalidation, simple distributed coordination, rate limiting, queue-like workflows
- Redis performance reasoning such as hot keys, command count, latency, and memory-conscious design
- Docker-based local environment and a reproducible run flow

Do not make the task primarily about:
- Redis Sentinel, Redis Cluster resharding, multi-node failover orchestration, or topology administration
- TLS, ACL, secret rotation, or deep security hardening as the main challenge
- full microservices architecture, REST/gRPC service design, or web framework implementation
- advanced infrastructure automation, Kubernetes, Terraform, Helm, or CI/CD setup
- major persistence tuning, backup/restore drills, or zero-data-loss migration exercises
- broad system design essays instead of a concrete coding task

If operational concepts are mentioned, they must remain secondary and lightweight, not the main implementation burden.

## TASK CATEGORY REQUIREMENT
This task MUST match SCRIPT_AND_DB exactly:
- include Docker infrastructure
- include a Redis service
- include a Go script or CLI-style program
- do NOT include a web framework
- do NOT generate API endpoints as the primary interface
- do NOT generate app-and-db or microservices structure

## NATURE OF THE TASK
Generate a task where the candidate receives a fully runnable repository with:
- a Go program that processes or synchronizes business data using Redis
- a Redis instance preloaded with realistic seed data
- intentionally flawed Redis access patterns and/or concurrency behavior
- tests that currently fail or are incomplete in ways that require intermediate-level fixes
- clear candidate-facing requirements that ask them to improve correctness, performance, and maintainability without rebuilding the project from scratch

The task should feel like a production issue in a backend job, such as:
- a booking or inventory sync worker doing too many Redis calls
- a rate-limited batch processor with stale or inconsistent Redis state
- a queue or reservation processor with race conditions and weak invalidation
- a leaderboard, slot allocator, or job dispatcher using the wrong Redis structure or inefficient access pattern

The task must require 4-5 intermediate concepts combined, for example:
- Go concurrency + context/error handling
- Redis key redesign + TTL strategy
- pipelining or batched reads/writes
- correctness under concurrent updates
- unit/integration testing of the improved behavior

## SCENARIO CALIBRATION
Use exactly one of the provided real-world scenarios as inspiration.
The generated task should resemble a realistic production maintenance task, not a greenfield build.
Prefer scenarios where:
- there is an existing implementation with measurable inefficiency or stale data behavior
- Redis is part of the core workflow, not an incidental dependency
- the candidate can improve both Go code quality and Redis usage patterns
- there are multiple valid solution paths with clear tradeoffs

## REPOSITORY REQUIREMENTS
The output JSON must define a complete repository with at least these files:

- README.md
- .gitignore
- docker-compose.yml
- run.sh
- kill.sh
- init_redis.sh
- redis/redis.conf
- service-go/Dockerfile
- service-go/go.mod
- service-go/go.sum
- service-go/cmd/syncer/main.go
- service-go/internal/app/app.go
- service-go/internal/config/config.go
- service-go/internal/domain/models.go
- service-go/internal/redisstore/store.go
- service-go/internal/worker/processor.go
- service-go/internal/worker/processor_test.go
- service-go/internal/worker/integration_test.go

You may add a few more files if needed, but keep the repository focused and completable.

## INFRASTRUCTURE REQUIREMENTS
- The in-container environment uses docker-compose to run all services.
- Do NOT include a version field in docker-compose.yml.
- Services must include:
  - one Redis service
  - one Go service
- Redis port must be bound to localhost only using "127.0.0.1:6379:6379".
- The Go service must depend_on Redis and wait until Redis is healthy.
- Redis data should persist via a mounted volume.
- Seed data must be loaded automatically during startup through init_redis.sh or equivalent startup logic.
- The environment must come up with a single run.sh execution.
- kill.sh must fully clean up containers, volumes, networks, images for this task, and remove /root/task with || true where appropriate.

## REDIS TASK DESIGN REQUIREMENTS
The Redis portion should test intermediate judgment without requiring advanced topology administration.
Good task ingredients include:
- poor key naming or fragmented key-space that should be consolidated
- missing or unsuitable TTLs causing stale or wasteful cache behavior
- repeated GET/SET loops that should be replaced by pipelining or batched operations
- a correctness issue under concurrent processing that needs WATCH/MULTI/EXEC, Lua, or safer application logic
- use of an unsuitable Redis data structure that the candidate should improve
- fallback behavior when Redis is unavailable or partially failing
- measurable reduction in command count or latency after improvement

Do not require all Redis features at once. Pick a focused subset that fits one coherent task.

## GO TASK DESIGN REQUIREMENTS
The Go portion should test intermediate engineering skill through:
- package organization and interface-based design
- context-aware operations
- wrapped errors with useful function context
- concurrency safety and avoidance of race conditions or goroutine leaks
- tests using the testing package
- maintainable code structure and idiomatic naming
- simple logging that helps diagnose failures without revealing the solution

The candidate should modify existing code, not build the whole architecture from scratch.

## TESTING REQUIREMENTS
Include tests that align with the scenario and expected fixes.
Tests should cover a focused set such as:
- cache hit or batched read behavior
- invalidation or refresh after a state change
- concurrent processing correctness
- fallback behavior when Redis is unavailable
- no duplicate processing or stale reservation under contention

Tests must be runnable and meaningful, but the starter code should not already contain the final solution.

## README REQUIREMENTS
README.md must contain these sections in this exact order:
1. Task Overview
2. Helpful Tips
3. Database Access
4. Objectives
5. How to Verify

Content rules:
- fully populated, specific, and relevant to the generated scenario
- no empty placeholders
- no direct solution steps
- no code snippets that reveal the answer
- no setup tutorial beyond concise verification-oriented guidance

Section guidance:
- Task Overview: 2-4 sentences describing the business workflow, the current issue, and why it matters.
- Helpful Tips: 4-6 bullets starting with Consider, Think about, Explore, Review, or Analyze. Guide discovery without prescribing exact commands or code changes.
- Database Access: explain Redis is reachable on 127.0.0.1:6379 after SSH into the droplet; mention redis-cli or a GUI client can be used.
- Objectives: measurable outcomes focused on correctness, reduced Redis round trips, safer concurrent behavior, and maintainable Go code.
- How to Verify: concrete observable checks such as improved behavior under repeated runs, passing tests, reduced stale data, fewer duplicate operations, or graceful handling of Redis issues.

## RUN.SH REQUIREMENTS
run.sh must:
- use set -e
- start docker-compose up -d --build
- wait for Redis health
- verify the Go container can run the program or tests successfully enough to confirm deployment
- print useful logs on failure
- be idempotent enough for repeated execution in a task environment

## KILL.SH REQUIREMENTS
kill.sh must:
- use set -e
- run docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true
- remove task-related images if applicable || true
- run docker system prune -a --volumes -f || true
- rm -rf /root/task || true
- print progress messages
- be safe to run multiple times

## DOCKERFILE REQUIREMENTS
- Use a current Go base image such as golang:1.22-alpine
- Set WORKDIR to /root/task/service-go
- Copy module files first, then source
- Build and run the Go program in a simple, reproducible way
- Do not rely on environment variables or .env files

## OUTPUT JSON SCHEMA
Your output must be valid JSON only and must use exactly these top-level keys:

{{
  "name": "short-kebab-case-repo-name",
  "question": "candidate-facing task description",
  "code_files": {{
    "README.md": "file contents",
    ".gitignore": "file contents"
  }},
  "answer": {{
    "summary": "high-level evaluator solution summary",
    "key_points": [
      "point 1",
      "point 2"
    ]
  }},
  "definitions": {{
    "term": "definition"
  }},
  "hints": "single-line hint",
  "outcomes": [
    "outcome 1",
    "outcome 2"
  ],
  "pre_requisites": [
    "item 1",
    "item 2"
  ],
  "short_overview": [
    "item 1",
    "item 2"
  ]
}}

Use exactly those canonical keys:
- name
- question
- code_files
- answer
- definitions
- hints
- outcomes
- pre_requisites
- short_overview

Do not use synonyms such as title, task_title, files, repository_structure, context, or acceptance_criteria.

## CONTENT REQUIREMENTS FOR JSON FIELDS
- "name": short kebab-case repository name
- "question": a clear candidate-facing description of the business problem, current behavior, constraints, and expected improvements
- "code_files": every filepath mapped to full file contents
- "answer": evaluator-facing high-level solution summary only, not a full patch
- "definitions": relevant Go and Redis terms used in the task
- "hints": exactly one line, subtle and non-revealing
- "outcomes": bullet-style list of expected end-state outcomes
- "pre_requisites": bullet-style list in simple language
- "short_overview": bullet-style list in simple language

## QUALITY BAR
The generated task should:
- be realistic for an intermediate backend engineer
- be solvable in a focused assessment window
- require meaningful reasoning and implementation, not boilerplate
- have more than one viable approach
- avoid giving away the exact fix in the README or question
- remain tightly aligned to Golang + Redis, script-and-db, and the provided scenario inspiration

## BRACE ESCAPING REMINDER
Any literal braces in JSON examples or code-like snippets inside this prompt must remain escaped with double braces so downstream formatting does not break.
"""

PROMPT_REGISTRY = {
    "Golang (INTERMEDIATE), Redis (INTERMEDIATE)": [
        PROMPT_GOLANG_REDIS_INTERMEDIATE_CONTEXT,
        PROMPT_GOLANG_REDIS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_GOLANG_REDIS_INTERMEDIATE_INSTRUCTIONS,
    ]
}