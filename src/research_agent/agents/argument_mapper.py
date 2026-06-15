from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Argument:
    premise: str
    conclusion: str
    strength: float = 0.7
    supporting_facts: list[str] = field(default_factory=list)


@dataclass
class ArgumentMap:
    topic: str
    arguments: list[Argument] = field(default_factory=list)
    counter_arguments: list[Argument] = field(default_factory=list)

    def add_argument(self, arg: Argument) -> None:
        self.arguments.append(arg)

    def add_counter(self, arg: Argument) -> None:
        self.counter_arguments.append(arg)

    def balance_score(self) -> float:
        a = len(self.arguments)
        c = len(self.counter_arguments)
        total = a + c
        if total == 0:
            return 0.5
        return a / total


_PRO_PATTERNS = [
    r"\bsupports?\b", r"\bdemonstrates?\b", r"\bshows?\b", r"\bproves?\b", r"\bconfirms?\b",
    r"\bevidence\s+for\b", r"\badvantage\b", r"\bbenefit\b",
]
_CON_PATTERNS = [
    r"\bhowever\b", r"\bcontra\w*\b", r"\boppose[sd]?\b", r"\bcritici[sz]\w*\b",
    r"\blimitation\b", r"\bdisadvantage\b", r"\bweakness\b", r"\bchallenge\b",
]


def extract_argument_structure(text: str, topic: str = "") -> ArgumentMap:
    arg_map = ArgumentMap(topic=topic)
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    for sent in sentences:
        is_pro = any(re.search(p, sent, re.I) for p in _PRO_PATTERNS)
        is_con = any(re.search(p, sent, re.I) for p in _CON_PATTERNS)
        if is_pro:
            arg_map.add_argument(Argument(premise=sent, conclusion=f"supports {topic}"))
        elif is_con:
            arg_map.add_counter(Argument(premise=sent, conclusion=f"challenges {topic}"))

    return arg_map
