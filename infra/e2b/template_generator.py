"""Auto-generate an E2B template definition when none exists locally.

Called by ``build_if_missing`` (template_builder.py) when a template_id
has been matched by the classifier but has no ``template.py`` under
``infra/e2b/templates/``.

Flow:
  1. Scan ``infra/e2b/templates/`` for all dirs that already have a
     ``template.py`` (excluding the target dir itself).
  2. Randomly pick up to 2 of them as structural reference examples.
  3. Call the LLM (via Portkey) to produce a new ``template.py`` for the
     new runtime, using those references as examples.
  4. Write ``template.py`` + ``start.sh`` to ``infra/e2b/templates/<dir>/``.

After this function returns True, ``build_if_missing`` re-loads the
definition and continues with the normal E2B build → Supabase registration
→ combo_key hydration flow.
"""
from __future__ import annotations

import os
import random
import re
import shutil
import textwrap
from pathlib import Path

from infra.logger_config import logger

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _infer_runtime(template_id: str) -> str:
    """Strip the utkrusht- prefix and normalise to a lowercase slug."""
    slug = template_id.lower()
    if slug.startswith("utkrusht-"):
        slug = slug[len("utkrusht-"):]
    return slug.replace("-", "_")


def _available_reference_dirs(exclude_dir: str) -> list[str]:
    """Return all template dirs (excluding target) that have a template.py."""
    dirs = []
    for p in _TEMPLATES_DIR.iterdir():
        if not p.is_dir():
            continue
        if p.name.startswith("_"):
            continue
        if p.name == exclude_dir:
            continue
        if (p / "template.py").exists():
            dirs.append(p.name)
    return sorted(dirs)


def _pick_references(exclude_dir: str, count: int = 2) -> list[str]:
    """Randomly pick up to ``count`` reference template dirs."""
    available = _available_reference_dirs(exclude_dir)
    if not available:
        return []
    return random.sample(available, min(count, len(available)))


def _extract_python_block(text: str) -> str:
    """Extract the first ```python…``` fenced block, or return raw text."""
    m = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _call_llm(prompt: str) -> str | None:
    """Single LLM call via the shared Portkey client. Returns text or None."""
    try:
        from generators.task._clients import openai_client
        model = os.getenv("TEMPLATE_GEN_MODEL", "claude-sonnet-4-6")
        response = openai_client.chat.completions.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:
        logger.warning(f"template_generator: LLM call failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def auto_generate_template(template_id: str) -> bool:
    """Generate and write template.py + start.sh for a new template_id.

    Randomly picks 2 existing templates as structural examples and asks the
    LLM to produce a new template.py adapted for the new runtime. Writes
    both files under ``infra/e2b/templates/<dir>/``.

    Returns True on success, False on any failure. Never raises.
    """
    try:
        return _auto_generate_template_inner(template_id)
    except Exception as exc:
        logger.warning(
            f"template_generator: unexpected error generating {template_id!r}: {exc}"
        )
        return False


def _auto_generate_template_inner(template_id: str) -> bool:
    runtime = _infer_runtime(template_id)

    # Determine target dir name (strip utkrusht- prefix)
    dir_name = template_id
    if dir_name.startswith("utkrusht-"):
        dir_name = dir_name[len("utkrusht-"):]

    # Pick 2 random existing templates as references
    ref_dirs = _pick_references(exclude_dir=dir_name, count=2)
    if not ref_dirs:
        logger.warning(
            f"template_generator: no existing templates to use as reference "
            f"for {template_id!r} — cannot auto-generate"
        )
        return False

    logger.info(
        f"template_generator: generating {template_id!r} "
        f"(runtime={runtime!r}) using references={ref_dirs}"
    )

    # Build the reference section for the prompt
    ref_sections = ""
    for ref_dir in ref_dirs:
        ref_content = (_TEMPLATES_DIR / ref_dir / "template.py").read_text(encoding="utf-8")
        ref_sections += textwrap.dedent(f"""
            ── REFERENCE: {ref_dir}/template.py ──────────────────────────────
            ```python
            {ref_content}
            ```
        """)

    prompt = textwrap.dedent(f"""
        You are generating an E2B v2 sandbox template definition for a new
        technical assessment environment.

        ────────────────────────────────────────────────────────────────────
        TARGET
        ────────────────────────────────────────────────────────────────────
        template_id    : {template_id}
        primary_runtime: {runtime}

        ────────────────────────────────────────────────────────────────────
        REFERENCE EXAMPLES  (study both — follow the same structure)
        ────────────────────────────────────────────────────────────────────
        {ref_sections}

        ────────────────────────────────────────────────────────────────────
        INSTRUCTIONS
        ────────────────────────────────────────────────────────────────────
        Generate a NEW ``template.py`` for ``{template_id}`` that:

        1. Follows the EXACT same module structure as the references:
             - Module docstring describing the template
             - ``manifest`` dict
             - ``template`` object (AsyncTemplate chain)

        2. ``manifest`` dict MUST contain these keys with correct values
           for ``{runtime}``:
             template_id      : "{template_id}"
             status           : "built"
             primary_runtime  : "{runtime}"
             personas         : list of relevant personas e.g. ["backend_engineer"]
             eval_methods     : ["test_suite"]
             capabilities     : dict with keys:
               language_versions : e.g. {{"dotnet": "8"}} for the runtime
               frameworks        : most common test + web frameworks for {runtime}
               datastores        : list relevant datastores this runtime typically uses
               protocols         : ["rest"] at minimum
               tools             : all CLI tools installed in the image
               requires          : {{"browser": false, "gpu": false}}
               tags              : relevant tags
             build_cmd    : the command to build/compile the project
             test_cmd     : the command to run tests
             compile_cmd  : the compile-only command (no tests)
             install_cmd  : the apt/package-manager install command for the runtime
             install_verify : command that verifies the runtime is installed
             install_seconds : estimated seconds for install
             description  : one-sentence description of what this template provides

        3. ``template`` object MUST:
             - Use the correct official base Docker image for {runtime}
               (e.g. mcr.microsoft.com/dotnet/sdk:8.0 for .NET,
               eclipse-temurin:21 for Java, golang:1.22 for Go, etc.)
             - Use ``AsyncTemplate()`` chaining exactly as the references show
             - Install git + curl + ca-certificates via apt at the start
             - Install Docker (docker-ce, docker-ce-cli, containerd.io,
               docker-compose-plugin) following the same pattern as whichever
               reference includes it — ALL runtimes need Docker so tasks can
               spin up datastores (SQL Server, PostgreSQL, Redis, etc.)
             - Install the runtime's standard SDK, build tool, and test framework
             - Install ttyd (browser terminal :7681) — copy the EXACT curl/chmod
               block from the reference verbatim
             - Install code-server (browser IDE :8443) — copy the EXACT
               curl/dpkg block from the reference verbatim
             - End with .copy("start.sh", "/usr/local/bin/start.sh")
               + .run_cmd("chmod +x /usr/local/bin/start.sh")
               + .set_workdir("/home/user")
               + .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 5")

        4. IMPORTANT: Every template MUST include Docker regardless of runtime.
           Assessment tasks for any language may require spinning up a database
           or other service via docker-compose. Follow the Docker install steps
           exactly as shown in the reference that includes them.

        5. Output ONLY the Python file content inside ```python ... ``` fences.
           No explanation text before or after the code block.
    """).strip()

    raw = _call_llm(prompt)
    if not raw:
        logger.warning(
            f"template_generator: LLM returned empty response for {template_id!r}"
        )
        return False

    code = _extract_python_block(raw)
    if len(code) < 200:
        logger.warning(
            f"template_generator: LLM output too short ({len(code)} chars) "
            f"for {template_id!r} — discarding"
        )
        return False

    target_dir = _TEMPLATES_DIR / dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Write template.py
    target_py = target_dir / "template.py"
    target_py.write_text(code, encoding="utf-8")
    logger.info(f"template_generator: wrote {target_py} ({len(code)} chars)")

    # Copy start.sh from first reference that has one
    target_sh = target_dir / "start.sh"
    if not target_sh.exists():
        copied = False
        for ref_dir in ref_dirs:
            ref_sh = _TEMPLATES_DIR / ref_dir / "start.sh"
            if ref_sh.exists():
                shutil.copy2(ref_sh, target_sh)
                logger.info(
                    f"template_generator: copied start.sh from {ref_dir!r} → {target_sh}"
                )
                copied = True
                break
        if not copied:
            target_sh.write_text(
                "#!/usr/bin/env bash\nset -e\nmkdir -p /var/log\n"
                "nohup ttyd -W -p 7681 bash > /var/log/ttyd.log 2>&1 &\n"
                "mkdir -p /root/.config/code-server\n"
                "nohup code-server --bind-addr 0.0.0.0:8443 --auth none "
                "--disable-telemetry /home/user > /var/log/code-server.log 2>&1 &\n"
                "exec tail -f /dev/null\n",
                encoding="utf-8",
            )
            logger.info(f"template_generator: wrote fallback start.sh to {target_sh}")

    return True
