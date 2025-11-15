# rules.py
from dataclasses import dataclass
from typing import List, Protocol
from app.services.accessibility.analytics.json_parser.models import DocumentModel, ElementNode


@dataclass
class RuleViolation:
    rule_id: str
    message: str
    node_path: str


class WCAGRule(Protocol):
    id: str
    description: str

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        ...


