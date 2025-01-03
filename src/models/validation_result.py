from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class ValidationResult:
    """Result of validating knowledge content"""
    is_valid: bool
    issues: List[str]
    confidence_score: float  # Score between 0 and 1 indicating confidence in the validation
    timestamp: datetime = datetime.now()  # When the validation was performed 