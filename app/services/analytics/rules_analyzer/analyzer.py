# rules.py
from dataclasses import dataclass
from typing import List, Protocol
from app.services.analytics.json_parser.models import DocumentModel, ElementNode


@dataclass
class RuleViolation:
    rule_id: str
    element_id: str
    message: str


class WCAGRule(Protocol):
    id: str
    description: str

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        ...


