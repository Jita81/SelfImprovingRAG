from dataclasses import dataclass
from typing import List

@dataclass
class UseCase:
    """Definition of a knowledge use case"""
    name: str
    description: str
    technical_level: str
    success_criteria: List[str]
    dependencies: List[str]
    domain: str 