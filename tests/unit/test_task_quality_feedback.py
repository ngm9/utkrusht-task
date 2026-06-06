"""Public-API smoke tests for the task_quality package.

The retry-loop ``build_retry_feedback`` extension was removed when the
content-quality layer switched from gate-and-retry to autofix-and-forward
— there is no quality_feedback kwarg anymore. These tests just verify
that the documented exports load cleanly from the package root.
"""


class TestPublicAPI:
    def test_documented_exports_are_importable_from_package_root(self):
        from task_quality import (  # noqa: F401
            QualityReport,
            Violation,
            evaluate_and_patch_task,
            run_quality_for_attempt,
        )

    def test_legacy_symbols_no_longer_exported(self):
        """The deterministic-rules-era symbols are gone — importing them
        from the package root must raise ImportError so we catch any
        accidental reintroduction."""
        import task_quality

        for legacy in ("RULES", "Rule", "QualityOutcome"):
            assert not hasattr(task_quality, legacy), (
                f"{legacy} should no longer be exported from task_quality"
            )
