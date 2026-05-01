# Task Session Review

tasksession_id:
reviewer:
review_date:
video_duration_minutes:
task_description:

<!-- One-line summary of what the candidate was asked to build -->

---

## Scores (0-5)

<!-- Score each dimension as an integer 0-5.
     Notes: 1-2 lines explaining WHY this score, not describing what happened. -->

| Dimension        | Score | Notes |
|------------------|-------|-------|
| Overall          |       |       |
| Skill/Competency |       |       |
| Problem Solving  |       |       |
| AI Usage         |       |       |

## Skill Breakdown

<!-- Only include the competencies being tested for this session.
     Score: 0-5. One-liner: why this score, not what happened. 
     Add or remove rows as needed. -->

| Competency | Score (0-5) | One-liner |
|------------|-------------|-----------|
|            |             |           |
|            |             |           |
|            |             |           |

## Key Behaviors

<!-- This is the MOST IMPORTANT section. Each entry should be a specific 
     observed behavior, not a general statement.
     
     BAD:  "Good debugging skills"
     GOOD: "Fixed auth bug on first attempt after reading the stack trace"
     
     These entries become direct test cases for prompt optimization:
     if the model disagrees with your classification here, that's a signal. -->

### Should be POSITIVE (model might miss or underweight)

<!-- Behaviors you'd credit in a review that the model tends to ignore.
     Examples:
     - Spent 2 min reading AI-generated code before accepting
     - Fixed compilation error on first retry after reading error message
     - Gave specific architectural constraints in prompt to Cursor -->

-

### Should be NEGATIVE (model might miss or underweight)

<!-- Behaviors you'd flag as concerns that the model tends to overlook.
     Examples:
     - Accepted AI output without reading it for the auth module
     - Skipped testing entirely after completing feature, moved to next task
     - Never verified the app runs end-to-end -->

-

### Should NOT be penalized (model might wrongly penalize)

<!-- Behaviors the model tends to mark as weaknesses but you consider fine.
     Examples:
     - 3 terminal errors, but none repeated — each fixed on first retry
     - Used AI to generate boilerplate CSS
     - Took 5 min to understand the codebase before starting -->

-

### Should NOT be rewarded (model might wrongly reward)

<!-- Behaviors the model tends to credit but you don't consider meaningful.
     Examples:
     - Wrote long prompts but they were copy-pasted task descriptions
     - Made many commits but they were all "fix" with no meaningful messages
     - Ran tests but only the ones AI suggested, no independent test thinking -->

-

## Insights Observed

<!-- List ONLY what you actually saw. One line each. Use type tags.
     Don't list things that didn't happen.

     Type tags:
       problem_decomposition  — Broke the problem into sub-tasks or outlined 
                                an approach before jumping into code
       ai_output_evaluation   — Evaluated AI output for correctness, performance,
                                or security rather than accepting blindly
       git_commit_hygiene     — Atomic commits with meaningful messages derived 
                                from good planning
       prompt_quality         — Specified behavior in detail: guardrails, 
                                constraints, performance parameters in prompts
       verification           — Tested functionality: ran code, manual testing, 
                                edge cases, end-to-end checks
       agent_steering         — Actively rejected or corrected AI suggestion 
                                based on own judgment. NOT just using AI to debug
                                — only when candidate pushes back or redirects
       ai_brainstorming       — Used AI to understand the problem, research 
                                solutions, explore edge cases before implementing
       planning_with_ai       — Asked AI to make a plan, reviewed and refined it.
                                Iterating on the plan by rejecting/refining is 
                                strong evidence -->

-

## Hiring Recommendation

<!-- 1-3 sentences. What would you tell the hiring manager? -->


## Miscellaneous

<!-- Anything notable that doesn't fit above. 
     E.g., "Ran out of time on last subtask", "Audio was muted for first 3 min" -->

