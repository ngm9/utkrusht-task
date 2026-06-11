"""Guard: the prompt generator must emit E2B-correct connection details.

The generator used to instruct the 'Database Access' README section to use the
droplet-era ``<DROPLET_IP>`` host placeholder, which is never substituted on
E2B (services run at localhost inside the sandbox). This locks in the fix so
the obsolete convention can't creep back into the generator instructions.
"""
import inspect

from generators.prompts.agent import GeneratePromptSignature


def _instructions() -> str:
    return (
        getattr(GeneratePromptSignature, "instructions", None)
        or inspect.getdoc(GeneratePromptSignature)
        or ""
    )


def test_generator_prescribes_localhost_for_db_access():
    text = _instructions()
    assert "must use `localhost`" in text, (
        "generator should prescribe localhost (E2B sandbox) for the Database Access host"
    )


def test_generator_does_not_prescribe_droplet_ip():
    text = _instructions()
    # The old prescriptive instruction must be gone. An explicit *forbid*
    # ("Do NOT use `<DROPLET_IP>`") is allowed — that steers the LLM away from it.
    assert "must use `<DROPLET_IP>`" not in text, (
        "generator must not prescribe the droplet-era <DROPLET_IP> host placeholder — "
        "tasks run in an E2B sandbox, not on a droplet"
    )
