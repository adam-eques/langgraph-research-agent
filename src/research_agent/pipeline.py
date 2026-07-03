from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PipelineStep:
    """Represents a single step in a research pipeline."""

    def __init__(self, name: str, fn) -> None:
        self.name = name
        self._fn = fn
        self.enabled = True

    def run(self, data: Any) -> Any:
        if not self.enabled:
            logger.debug("Skipping disabled step: %s", self.name)
            return data
        logger.debug("Running step: %s", self.name)
        return self._fn(data)


class ResearchPipeline:
    """Sequential pipeline of processing steps with enable/disable support."""

    def __init__(self) -> None:
        self._steps: list[PipelineStep] = []

    def add(self, name: str, fn) -> ResearchPipeline:
        self._steps.append(PipelineStep(name, fn))
        return self

    def disable(self, name: str) -> None:
        for step in self._steps:
            if step.name == name:
                step.enabled = False

    def run(self, data: Any) -> Any:
        for step in self._steps:
            data = step.run(data)
        return data

    @property
    def step_names(self) -> list[str]:
        return [s.name for s in self._steps]
