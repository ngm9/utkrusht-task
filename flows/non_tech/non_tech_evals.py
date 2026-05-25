import json
from typing import Dict
from infra.logger_config import logger

def clean_llm_json_response(response: str) -> str:
    """Clean LLM response to extract valid JSON"""
    try:
        response = response.strip()
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        return response
    except Exception as e:
        logger.error(f"Error cleaning LLM response: {str(e)}")
        return response

MAX_EVAL_RETRIES = 2

TASK_EVAL_PROMPT = """
You are an expert AI product manager and technical assessment reviewer specializing in Prompt Engineering and contact-center AI applications. Your role is to evaluate whether generated assessment tasks effectively measure candidates' ability to design, optimize, analyze, and maintain production-grade AI solutions.

Given the following task JSON, proficiency level, years of experience, and time constraint, evaluate the following CRITICAL criteria:

## 1. TIME CONSTRAINT EVALUATION
Can this task be realistically completed within {time_constraint} minutes? Consider the full workflow:
   - **Reading and understanding time**: Reviewing data files (CSV, JSON, logs, configs), understanding the business context and AI system challenges
   - **Analysis and diagnosis time**: Identifying patterns, root causes, AI system issues (flaws, bias, bottlenecks, inconsistencies)
   - **Solution design time**: Designing/redesigning AI flows, prompts, and guardrails; creating evaluation frameworks
   - **Documentation time**: Writing problem diagnosis, solution architecture, prompt redesigns with reasoning, metrics analysis, safety considerations, and executive summary
   - **Total time should NOT exceed {time_constraint} minutes**

## 2. TASK LENGTH AND COMPLEXITY
Is the task appropriately sized for the time constraint? Check:
   - **Number and size of data files**: Should be manageable (typically 20-60 rows/entries for CSVs, small configs/logs that can be read in a few minutes)
   - **Scope of analysis required**: Should match proficiency level expectations
   - **Deliverables expected**: Should be achievable within time (problem diagnosis, prompt redesigns, basic metrics, executive summary)
   - **Complexity of requirements**: Should not require extensive statistical analysis or multi-model orchestration unless proficiency level is ADVANCED/EXPERT
   - The task should be concise, focused, and scoped appropriately

## 3. PROFICIENCY LEVEL ALIGNMENT
Does the task complexity align with the {proficiency} proficiency level while assuming candidates will use AI tools?
   - **BEGINNER/BASIC**: Should require single-file analysis, obvious issues, straightforward fixes, basic metrics, simple documentation
   - **INTERMEDIATE**: Should require multi-file systems, pattern identification, comparative analysis, root cause diagnosis, CPTO-level summaries
   - **ADVANCED**: Should require complex multi-step flows, statistical analysis, comprehensive remediation strategies, scalability considerations
   - **EXPERT**: Should require multi-model orchestration, production optimization at scale, organizational governance frameworks, strategic architecture

## 4. TASK NATURE AND REALISM
Does the task meet the expected assessment criteria?
   - **Presents a realistic business problem** with actual operational data files (not templates or examples)
   - **Requires AI tinkering and diagnostic thinking** - candidates must analyze, diagnose, test different approaches
   - **Assesses key competencies**: AI literacy, flow design, prompt engineering, evaluation frameworks, safety & governance, high agency/AI tinkering, executive communication
   - **Encourages AI tool usage** - task should be designed assuming candidates use ChatGPT, Claude, LLM playgrounds
   - **Focuses on quality of reasoning** rather than memorization - evaluates diagnostic thinking, systematic analysis, strategic thinking

## 5. DELIVERABLES FEASIBILITY
Can candidates realistically produce the expected deliverables within {time_constraint} minutes?
   - Problem diagnosis and root cause analysis
   - AI solution architecture and flow improvements
   - Prompt redesigns with reasoning and iterations
   - Evaluation framework or data analysis with metrics
   - Safety/bias considerations and remediation plans
   - Executive summary suitable for CPTO presentation

**CRITICAL**: If the task requires more than {time_constraint} minutes OR is too long/complex for the proficiency level OR doesn't align with the expected assessment nature, it MUST FAIL.

If the task PASSES all criteria, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["list of specific criteria that were met, e.g., 'Completable within {time_constraint} minutes', 'Appropriate task length and file sizes', 'Appropriate complexity for {proficiency} level', 'Realistic AI/Prompt Engineering scenario', 'Feasible deliverables scope', 'Well-balanced for {yoe} years experience', 'Assesses key AI competencies']
}}

If the task FAILS any criteria, respond in JSON:
{{
  "pass": false,
  "issues": ["list of specific issues found - MUST include if task is too long or takes more than {time_constraint} minutes, or if complexity doesn't match proficiency level"],
  "feedback": "detailed explanation of what needs to be fixed - specifically mention how to make it shorter, simpler, reduce file sizes, narrow scope, or adjust complexity to fit {time_constraint} minutes and {proficiency} proficiency level"
}}

TASK JSON:
{task_json}
"""

def llm_task_eval(task_json: Dict, proficiency: str, yoe: str, time_constraint: int, openai_client, model: str) -> Dict:
    """Evaluate if task can be completed within time constraint and is appropriately sized."""
    task_json_str = json.dumps(task_json, indent=2)
    prompt = TASK_EVAL_PROMPT.format(
        task_json=task_json_str,
        proficiency=proficiency,
        yoe=yoe,
        time_constraint=time_constraint
    )

    last_error = None
    raw_response = None

    for attempt in range(1, MAX_EVAL_RETRIES + 1):
        try:
            response = openai_client.chat.completions.create(
                model=model,
                # JSON mode – model will try to return strict JSON
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert AI product manager and technical assessment reviewer specializing in Prompt Engineering "
                            "and contact-center AI applications. You evaluate whether assessment tasks effectively measure candidates' "
                            "ability to design, optimize, analyze, and maintain production-grade AI solutions. "
                            "You MUST respond with a single valid JSON object only. "
                            "No markdown, no code fences, no extra text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            raw_response = response.choices[0].message.content
            logger.info(f"Raw LLM task eval response (attempt {attempt}): {raw_response[:200]}...")

            cleaned_response = clean_llm_json_response(raw_response)
            return json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            last_error = e
            logger.error(f"Failed to parse task eval JSON response on attempt {attempt}: {str(e)}")
            if raw_response is not None:
                logger.error(f"Raw response: {raw_response}")
        except Exception as e:
            last_error = e
            logger.error(f"Unexpected error in task evaluation on attempt {attempt}: {str(e)}")

    # All retries failed – default failure
    logger.error(f"Task evaluation failed after {MAX_EVAL_RETRIES} attempts")
    return {
        "pass": False,
        "issues": [
            f"Failed to parse evaluation response after {MAX_EVAL_RETRIES} attempts"
            if last_error
            else "Unknown evaluation error"
        ],
        "validated_criteria": []
    }


def run_evaluations(task_data: Dict, openai_client, model: str) -> Dict:
    """Run LLM-based evaluation on the task to check if it's too long or can be completed in 20 minutes."""
    # Get highest proficiency level (current behavior: last one in list)
    prof_levels = [criteria.get("proficiency", "").upper() for criteria in task_data.get("criterias", [])]
    yoe = task_data.get("background", {}).get("yoe", "") if isinstance(task_data.get("background"), dict) else ""
    time_constraint = 20  # Fixed to 20 minutes for test tasks
    
    proficiency = prof_levels[-1] if prof_levels else "BASIC"
    
    # Task evaluation - check if task is too long or can be completed in 20 minutes
    task_eval_result = llm_task_eval(
        task_data, 
        proficiency,
        yoe,
        time_constraint,
        openai_client,
        model
    )
    
    # Final output: only pass + validated_criteria (as you requested)
    eval_info = {
        "task_eval": {
            "pass": task_eval_result.get("pass", False),
            "validated_criteria": task_eval_result.get("validated_criteria", [])
        }
    }
    
    return eval_info
