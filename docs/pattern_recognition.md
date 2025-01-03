# Pattern Recognition System

The Pattern Recognition System is a core component of the Self-Improving RAG System that analyzes validation history to identify recurring patterns in validation issues. This helps the system learn from past validation results and improve its performance over time.

## Overview

The system identifies two types of patterns:

1. **Semantic Patterns**: Groups of semantically similar validation issues that occur frequently. These patterns help identify common themes in validation failures.

2. **Temporal Patterns**: Sequences of validation issues that occur repeatedly over time. These patterns help identify potential causal relationships between issues.

## Components

### Pattern Class

The `Pattern` class represents a detected pattern with the following attributes:

- `pattern_type`: Either "semantic" or "temporal"
- `description`: Human-readable description of the pattern
- `significance`: Float between 0 and 1 indicating pattern importance
- `occurrences`: Number of times the pattern was observed
- `first_seen`: Timestamp of first occurrence
- `last_seen`: Timestamp of last occurrence
- `related_issues`: List of validation issues involved in the pattern
- `metadata`: Additional pattern-specific information

### Pattern Recognition Service

The `PatternRecognitionService` class provides the following functionality:

1. **Semantic Pattern Detection**:
   - Uses DBSCAN clustering to group similar validation issues
   - Employs semantic embeddings to measure issue similarity
   - Calculates pattern significance based on cluster size and cohesion

2. **Temporal Pattern Detection**:
   - Identifies repeating sequences of validation issues
   - Considers temporal density and sequence length
   - Handles variations in issue ordering within sequences

## Usage

```python
from src.services.pattern_recognition import PatternRecognitionService

# Initialize with an embedding model
service = PatternRecognitionService(embedding_model)

# Analyze validation history
patterns = service.analyze_validation_history(validation_results)

# Filter patterns by significance
significant_patterns = service.analyze_validation_history(
    validation_results,
    min_significance=0.8
)
```

## Configuration

The service can be configured with the following parameters:

- `min_sequence_length`: Minimum length of temporal patterns (default: 2)
- `min_sequence_occurrences`: Minimum occurrences for temporal patterns (default: 3)
- `eps`: DBSCAN clustering distance threshold (default: 0.5)
- `min_samples`: DBSCAN minimum cluster size (default: 2)

## Integration

The Pattern Recognition System integrates with other components:

1. **Validation History**: Provides the input data for pattern analysis
2. **Knowledge Map Management**: Uses pattern insights to suggest improvements
3. **Recovery Management**: Helps identify systematic issues requiring recovery

## Example Patterns

### Semantic Pattern Example
```python
Pattern(
    pattern_type="semantic",
    description="Similar issues: Technical level mismatch, Technical level too advanced",
    significance=0.85,
    occurrences=5,
    first_seen=timestamp1,
    last_seen=timestamp2,
    related_issues=["Technical level mismatch", "Technical level too advanced"],
    metadata={
        "cluster_size": 2,
        "average_similarity": 0.92
    }
)
```

### Temporal Pattern Example
```python
Pattern(
    pattern_type="temporal",
    description="Repeating sequence: Missing prerequisites -> Technical level mismatch",
    significance=0.75,
    occurrences=3,
    first_seen=timestamp1,
    last_seen=timestamp2,
    related_issues=["Missing prerequisites", "Technical level mismatch"],
    metadata={
        "sequence_length": 2,
        "temporal_density": 0.8
    }
)
```

## Future Improvements

1. **Advanced Pattern Types**:
   - Structural patterns in knowledge maps
   - Multi-dimensional patterns combining different aspects

2. **Pattern Evolution**:
   - Tracking pattern changes over time
   - Identifying emerging and declining patterns

3. **Pattern Recommendations**:
   - Automated suggestions for knowledge map improvements
   - Predictive pattern detection 