"""Design Review utilities: library management, cost tracking, local save, validation."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from logger_config import logger


# ─── Library Management ───

def load_figma_library() -> List[Dict]:
    """Load the Figma community file library."""
    library_path = Path(__file__).parent / "figma_library.json"
    if not library_path.exists():
        logger.warning(f"Figma library not found at {library_path}")
        return []
    return json.loads(library_path.read_text(encoding="utf-8"))


def get_library_entry(library_entry_id: str) -> Optional[Dict]:
    """Get a specific library entry by ID."""
    library = load_figma_library()
    for entry in library:
        if entry.get("id") == library_entry_id:
            return entry
    return None


def load_layer_tree(library_entry_id: str) -> Optional[Dict]:
    """Load the Figma layer tree for a library entry."""
    layer_tree_path = Path(__file__).parent / "layer_trees" / f"{library_entry_id}.json"
    if not layer_tree_path.exists():
        logger.warning(f"Layer tree not found at {layer_tree_path}")
        return None
    return json.loads(layer_tree_path.read_text(encoding="utf-8"))


def extract_layer_names(layer_tree: Dict, prefix: str = "") -> List[str]:
    """Recursively extract all layer names from a Figma layer tree.

    Figma REST API returns a tree with 'name' and 'children' fields.
    Returns flat list of full layer paths like 'Frame / Subframe / Button'.
    """
    names = []
    name = layer_tree.get("name", "")
    full_name = f"{prefix} / {name}".strip(" / ") if prefix else name

    if name:
        names.append(full_name)

    for child in layer_tree.get("children", []):
        names.extend(extract_layer_names(child, full_name))

    return names


def format_frames_for_prompt(frames: Dict) -> str:
    """Format the frames/key_elements from a library entry for prompt injection."""
    parts = []
    for screen_name, screen_data in frames.items():
        frame_name = screen_data.get("frame_name", screen_name)
        parts.append(f"Screen: {screen_name} (frame: {frame_name})")
        for element_name, layer_name in screen_data.get("key_elements", {}).items():
            parts.append(f"  - {element_name}: {layer_name}")
    return "\n".join(parts)


# ─── Validation ───

def validate_flaw_layers(flaws: List[Dict], layer_names: List[str]) -> List[str]:
    """Check that all flaw target_layers exist in the layer tree. Returns list of invalid layers."""
    invalid = []
    for flaw in flaws:
        target = flaw.get("target_layer", "")
        if target and target not in layer_names:
            invalid.append(f"Flaw {flaw.get('id', '?')}: layer '{target}' not found")
    return invalid


def validate_figma_link(link: str) -> bool:
    """Basic validation that the link is a Figma URL."""
    return link.startswith("https://figma.com/") or link.startswith("https://www.figma.com/")


def validate_spec_file(spec_data: Dict) -> List[str]:
    """Validate a generated spec file has all required fields."""
    errors = []
    required = ["flaw_spec", "candidate_brief", "evaluation_rubric", "library_entry"]
    for field in required:
        if field not in spec_data:
            errors.append(f"Missing required field: {field}")
    return errors


# ─── Token Usage & Cost ───

def extract_usage(response) -> Dict:
    """Extract token usage from an OpenAI Responses API response."""
    usage = getattr(response, "usage", None)
    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }
    return {"input_tokens": 0, "output_tokens": 0}


PRICING = {
    "gpt-5-nano-2025-08-07": {"input": 0.50, "output": 2.00},
    "gpt-5.1-2025-11-13": {"input": 2.00, "output": 8.00},
}


def calculate_cost(total_usage: Dict, model: str) -> float:
    """Calculate cost in USD from token usage."""
    prices = PRICING.get(model, {"input": 1.25, "output": 10.00})
    input_cost = (total_usage["input_tokens"] / 1_000_000) * prices["input"]
    output_cost = (total_usage["output_tokens"] / 1_000_000) * prices["output"]
    return input_cost + output_cost


def format_cost_summary(usage_by_model: Dict) -> str:
    """Format a cost summary string."""
    lines = ["Cost Breakdown:"]
    grand_total_cost = 0.0
    for model, usage in usage_by_model.items():
        cost = calculate_cost(usage, model)
        grand_total_cost += cost
        lines.append(f"  {model}: {usage['input_tokens']:,} in + {usage['output_tokens']:,} out = ${cost:.6f}")
    lines.append(f"  Total: ${grand_total_cost:.6f}")
    return "\n".join(lines)


# ─── Local Save ───

def save_design_task_locally(
    library_id: str,
    flaw_spec: Dict,
    candidate_brief: Dict,
    evaluation_rubric: Dict,
    library_entry: Dict,
    eval_info: Dict,
    competencies: List[Dict],
) -> Path:
    """Save generated design task spec locally for inspection.

    Returns path to the saved directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(__file__).parent.parent / "infra_assets" / "design_tasks" / f"{timestamp}_{library_id}"
    base_dir.mkdir(parents=True, exist_ok=True)

    spec_data = {
        "flaw_spec": flaw_spec,
        "candidate_brief": candidate_brief,
        "evaluation_rubric": evaluation_rubric,
        "library_entry": library_entry,
        "eval_info": eval_info,
        "competencies": competencies,
        "generated_at": datetime.now().isoformat(),
    }

    spec_path = base_dir / "design_task_spec.json"
    spec_path.write_text(
        json.dumps(spec_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Also save candidate brief separately for easy sharing
    brief_path = base_dir / "candidate_brief.json"
    brief_path.write_text(
        json.dumps(candidate_brief, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Save flaw spec separately for the Figma plugin
    plugin_spec_path = base_dir / "flaw_spec_for_plugin.json"
    plugin_spec_path.write_text(
        json.dumps(flaw_spec, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    logger.info(f"Saved design review task locally: {base_dir}")
    return base_dir
