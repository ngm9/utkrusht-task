# Task Session Review Template v2

## Why This Template Exists

When a candidate completes a task on Utkrushta, our AI generates a report with scores, highlights, and a hiring recommendation. But the AI has blind spots — it might praise someone for "thorough review" when they just scrolled through AI-generated output, or give a "Strong Hire" to someone who never wrote a single line of code in a coding task.

Human reviews using this template serve two purposes:
1. **Right now**: Catch what the AI misses and provide accurate hiring signals
2. **Soon**: Train a DSPy pipeline that learns from your reviews to make the AI smarter over time

Every field in this template is designed to be machine-readable so DSPy can learn from it.

---

## The Template

```markdown
# Task Session Review

## Session Info

- tasksession_id:
- reviewer:
- review_date: YYYY-MM-DD
- video_duration_minutes:
- task_description: (one line — what were they asked to build/design?)
- proficiency_level: BEGINNER | BASIC | INTERMEDIATE | ADVANCED
- task_type: coding | design | pr-review | non-tech
- time_allocated_minutes:
- time_spent_minutes:
- ai_tools_used: [e.g. Claude Code, Cursor, ChatGPT, Copilot, None]

---

## AI Report Comparison

(What did the AI report say vs what you actually observed?)

| Field                  | AI Said        | You Observed   | Agree? |
|------------------------|----------------|----------------|--------|
| Skill Score            |    /5          |    /5          | Y/N    |
| AI Usage Score         |    /5          |    /5          | Y/N    |
| Problem Solving Score  |    /5          |    /5          | Y/N    |
| Recommendation         |                |                | Y/N    |

disagreement_notes: (If you disagreed, explain why in 1-2 lines per field)

---

## Overall Scores (0-5)

| Dimension        | Score | Notes (why this score, 1-2 lines) |
|------------------|-------|-----------------------------------|
| Overall          |       |                                   |
| Skill/Competency |       |                                   |
| Problem Solving  |       |                                   |

---

## AI Usage Breakdown (0-5 each)

Instead of a single "AI Usage" score, rate these four dimensions separately:

| Dimension            | Score | Notes |
|----------------------|-------|-------|
| Prompt Quality       |       | How specific, constrained, and well-structured were their prompts? |
| Iterative Steering   |       | Did they refine through back-and-forth, or dump-and-accept? |
| Critical Evaluation  |       | Did they question, modify, or reject AI output? |
| Independence         |       | Did they do any solo thinking/work before or alongside the AI? |

---

## Skill Breakdown

(Only the competencies being tested for this session)

| Competency   | Score (0-5) | One-liner |
|--------------|-------------|-----------|
| e.g. React   |             |           |
| e.g. Testing |             |           |

---

## Key Behaviors Observed

### Should be POSITIVE (model might miss or underweight)
-

### Should be NEGATIVE (model might miss or underweight)
-

### Should NOT be penalized (model might wrongly penalize)
-

### Should NOT be rewarded (model might wrongly reward)
-

---

## Insights Observed

(List only what you actually saw. Use the type tags. One line each.)

### Tags to use:
- `[prompt_quality]` — How they wrote prompts to AI tools
- `[agent_steering]` — How they directed/redirected AI suggestions
- `[verification]` — How they tested/checked their work or AI output
- `[debugging]` — How they found and fixed problems
- `[architecture]` — Design decisions and structural choices
- `[testing]` — Writing or running tests
- `[documentation]` — Comments, READMEs, commit messages
- `[independence]` — Solo thinking without AI assistance
- `[time_management]` — How they used their allocated time
- `[communication]` — How they explained their thinking (if applicable)

### Observations:
- [tag] observation
- [tag] observation

---

## Hiring Recommendation

recommendation: STRONG_HIRE | HIRE | LEAN_HIRE | LEAN_NO | NO | STRONG_NO
confidence: HIGH | MEDIUM | LOW

reasoning: (1-3 sentences. What would you tell the hiring manager?)

---

## Miscellaneous

(Anything notable that doesn't fit above)
```

---

## What Changed From v1 and Why

| Change | Why |
|--------|-----|
| Added `proficiency_level` | A beginner using AI well is impressive. An advanced candidate who can't work without AI is a red flag. The AI needs to know the bar. |
| Added `task_type` | "No code written" is a dealbreaker for `coding` tasks but expected for `design` tasks. Scoring rules change by type. |
| Added `time_spent_minutes` | A perfect solution in 25 minutes is different from a perfect solution in 5 minutes. Efficiency matters. |
| Added `ai_tools_used` | Different tools have different capabilities. Using Claude Code vs ChatGPT copy-paste tells you different things about the candidate. |
| Split AI Usage into 4 dimensions | One score hides too much. Someone can write great prompts but never question the output. These are separate skills. |
| Added AI Report Comparison section | This is the most important section for DSPy — it directly tells the system where it was wrong. |
| Made recommendation categorical | "Strong Hire" as free text is hard to learn from. `STRONG_HIRE` as a category lets DSPy measure accuracy. |
| Added confidence level | A reviewer saying "HIRE with LOW confidence" tells us this is an edge case worth studying. |
| Added fixed insight tags | Free-form tags are hard to aggregate. Fixed tags let DSPy count patterns (e.g., "candidates who skip verification always get overscored"). |

---

## How DSPy Will Use This Template

### What is DSPy? (Simple Version)

Think of DSPy as **a way to teach an AI by showing it examples instead of writing long prompts**.

Right now, the Utkrushta AI uses a big hand-written prompt that says things like "evaluate the candidate's problem solving ability" and hopes the AI interprets that well. Sometimes it does, sometimes it doesn't (like giving "Strong Hire" to someone who wrote zero code).

DSPy flips this:
1. You show it 20-50 examples of **your** reviews (the filled-in templates)
2. It figures out the patterns — "oh, when a human reviewer sees no code in a coding task, they score lower"
3. It automatically writes better prompts that match how **you** would score

You never write a prompt. You just review candidates, and the AI learns from you.

### The Three Phases

```
Phase 1: Collect          Phase 2: Train           Phase 3: Assist
(You do reviews)          (DSPy learns)            (AI helps you)

You watch video    →      DSPy sees your     →     AI pre-fills the
You fill template         reviews + AI's            template for new
You note where AI         reports and learns        sessions. You just
was wrong                 the gaps                  correct what's wrong
                                                    ↓
                                                    Corrections feed
                                                    back into training
```

### Phase 1: Collect Reviews (Now → 20-50 reviews)

You fill out this template for each task session. The key section is **AI Report Comparison** — this tells DSPy exactly where the current AI is wrong.

Example:
```
| Field           | AI Said      | You Observed | Agree? |
|-----------------|-------------|--------------|--------|
| Skill Score     | 4/5         | 2/5          | N      |
| Recommendation  | Strong Hire | Lean No      | N      |

disagreement_notes: AI gave 4/5 for Java but candidate wrote zero Java code.
Recommendation should be much lower for a coding task with no coding.
```

This disagreement is gold for DSPy. It learns: "when task_type=coding and no code is committed, the AI overscores."

### Phase 2: Train DSPy (After ~20 reviews)

DSPy takes your reviews and does three things:

**a) Learns scoring patterns**
```
Your reviews show:
- "coding" tasks with no code → you score 1-2/5
- "design" tasks with good docs → you score 3-4/5
- Candidates who iterate with AI → you score AI Usage higher
- Candidates who dump-and-accept → you score AI Usage lower

DSPy encodes these patterns automatically.
```

**b) Finds where AI consistently disagrees with you**
```
Pattern found: AI overscores "verification" when candidate
only scrolls through output. Humans score this 1-2/5,
AI scores 4/5. Adjusting.
```

**c) Generates optimized evaluation prompts**
```
Instead of: "evaluate the candidate's AI usage"

DSPy generates: "evaluate the candidate's AI usage across four
dimensions: prompt quality (were prompts specific and constrained?),
iterative steering (did they refine through multiple rounds?),
critical evaluation (did they question or modify output?),
and independence (did they do solo work before using AI?).
Score 0-2 if they dumped requirements into AI and accepted output.
Score 3-4 if they iterated and modified. Score 5 only if they
demonstrated independent thinking alongside excellent AI collaboration."
```

You never write this prompt. DSPy generates it from your examples.

### Phase 3: AI-Assisted Review (After training)

For new task sessions:
1. AI pre-fills the template using the DSPy-optimized pipeline
2. You watch the video and check if the pre-filled scores match your judgment
3. You correct any mistakes
4. Corrections feed back into DSPy (the AI keeps getting better)

Over time, you spend less time reviewing because the AI aligns with your judgment. But you always have the final say.

### What This Looks Like in Code (Simplified)

```python
import dspy

# Step 1: Define what a review looks like
class TaskReview(dspy.Signature):
    """Review a candidate's task session."""
    task_description: str = dspy.InputField()
    task_type: str = dspy.InputField()          # coding, design, pr-review
    proficiency_level: str = dspy.InputField()   # BEGINNER to ADVANCED
    code_diff: str = dspy.InputField()           # what they committed
    video_summary: str = dspy.InputField()       # chapter summaries
    ai_tool_used: str = dspy.InputField()

    overall_score: int = dspy.OutputField(desc="0-5")
    skill_score: int = dspy.OutputField(desc="0-5")
    problem_solving_score: int = dspy.OutputField(desc="0-5")
    prompt_quality_score: int = dspy.OutputField(desc="0-5")
    iterative_steering_score: int = dspy.OutputField(desc="0-5")
    critical_evaluation_score: int = dspy.OutputField(desc="0-5")
    independence_score: int = dspy.OutputField(desc="0-5")
    positive_behaviors: list[str] = dspy.OutputField()
    negative_behaviors: list[str] = dspy.OutputField()
    recommendation: str = dspy.OutputField(desc="STRONG_HIRE|HIRE|LEAN_HIRE|LEAN_NO|NO|STRONG_NO")
    reasoning: str = dspy.OutputField()


# Step 2: Build a reviewer that thinks step-by-step
class TaskReviewer(dspy.Module):
    def __init__(self):
        self.review = dspy.ChainOfThought(TaskReview)

    def forward(self, **inputs):
        return self.review(**inputs)


# Step 3: Load your human reviews as training data
trainset = load_human_reviews("reviews/*.md")  # your filled templates


# Step 4: Define "good" = close to human scores
def matches_human(example, prediction, trace=None):
    score_diffs = [
        abs(example.overall_score - prediction.overall_score),
        abs(example.skill_score - prediction.skill_score),
        abs(example.problem_solving_score - prediction.problem_solving_score),
    ]
    avg_diff = sum(score_diffs) / len(score_diffs)
    rec_match = example.recommendation == prediction.recommendation
    return (avg_diff <= 1) and rec_match


# Step 5: Let DSPy optimize (this is the magic)
optimizer = dspy.MIPROv2(metric=matches_human, num_threads=4)
optimized_reviewer = optimizer.compile(
    TaskReviewer(),
    trainset=trainset,
)

# Step 6: Save and use
optimized_reviewer.save("trained_reviewer.json")

# Now for any new session:
result = optimized_reviewer(
    task_description="Design grading architecture",
    task_type="design",
    proficiency_level="INTERMEDIATE",
    code_diff="...",
    video_summary="...",
    ai_tool_used="Claude Code"
)
# result.overall_score → 3
# result.recommendation → "LEAN_HIRE"
# result.reasoning → "Produced design doc via AI but showed no independent..."
```

### The Key Insight

The current system writes one big prompt and hopes it works. DSPy instead:

```
Big hand-written prompt     →    You review 20 candidates
that sometimes works              DSPy learns YOUR judgment
                                   AI gets better automatically
                                   You never touch a prompt
```

Your reviews ARE the training data. The template IS the schema. DSPy IS the optimizer.

---

## Getting Started Checklist

- [ ] Use this template for next 20 task session reviews
- [ ] Always fill the "AI Report Comparison" section (most important for training)
- [ ] Use the fixed insight tags (don't invent new ones without adding to the tag list)
- [ ] Use categorical recommendation (STRONG_HIRE, not "I think they're pretty good")
- [ ] Store completed reviews in `reviews/` directory as `{tasksession_id}.md`
- [ ] After 20 reviews: build the DSPy pipeline and run first optimization
- [ ] After 50 reviews: deploy AI-assisted pre-filling for new sessions
