from typing import List, Dict, Set, Tuple
from datetime import datetime
from collections import defaultdict
from src.models.validation_result import ValidationResult

class KnowledgeMapValidator:
    """Validates knowledge maps for structural integrity, completeness, and content quality."""
    
    def __init__(self):
        """Initialize the validator."""
        self.min_description_length = 50
        self.max_description_length = 1000
        self.max_path_length = 10
        self.max_branching_factor = 3
        self.max_prerequisites_per_node = 4
        self.valid_technical_levels = ["beginner", "intermediate", "advanced", "expert"]

    def _check_duplicate_ids(self, nodes):
        """Check for duplicate node IDs."""
        seen_ids = set()
        issues = []
        for node in nodes:
            if node["id"] in seen_ids:
                issues.append("Duplicate node IDs found")
            seen_ids.add(node["id"])
        return issues

    def _check_missing_fields(self, nodes):
        """Check for missing required fields."""
        required_fields = ["id", "topic", "description", "required_prerequisites", "technical_level"]
        issues = []
        for node in nodes:
            missing = [field for field in required_fields if field not in node]
            if missing:
                issues.append("missing required fields")
        return issues

    def _check_undefined_prerequisites(self, nodes):
        """Check for prerequisites that don't exist."""
        node_ids = {node["id"] for node in nodes}
        issues = []
        for node in nodes:
            undefined = [prereq for prereq in node.get("required_prerequisites", []) if prereq not in node_ids]
            if undefined:
                issues.append("undefined prerequisites")
        return issues

    def _check_circular_dependencies(self, nodes):
        """Check for circular dependencies."""
        def has_cycle(node_id, visited, path):
            if node_id in path:
                return True
            if node_id in visited:
                return False
            if not any(n["id"] == node_id for n in nodes):
                return False
            visited.add(node_id)
            path.add(node_id)
            node = next(n for n in nodes if n["id"] == node_id)
            for prereq in node.get("required_prerequisites", []):
                if has_cycle(prereq, visited, path):
                    return True
            path.remove(node_id)
            return False

        issues = []
        for node in nodes:
            if has_cycle(node["id"], set(), set()):
                issues.append("Circular dependencies detected")
                break
        return issues

    def _check_description_length(self, nodes):
        """Check description length requirements."""
        issues = []
        for node in nodes:
            if "description" not in node:
                continue
            desc_len = len(node["description"])
            if desc_len < self.min_description_length:
                issues.append("description too short")
            elif desc_len > self.max_description_length:
                issues.append("description too long")
        return issues

    def _check_technical_level_validation(self, nodes):
        """Check if technical levels are valid."""
        issues = []
        for node in nodes:
            if "technical_level" not in node:
                continue
            level = node.get("technical_level", "").lower()
            if level not in self.valid_technical_levels:
                issues.append("invalid technical level")
            else:
                # Check if any prerequisites have higher technical level
                current_level_idx = self.valid_technical_levels.index(level)
                for prereq_id in node.get("required_prerequisites", []):
                    prereq_node = next((n for n in nodes if n["id"] == prereq_id), None)
                    if prereq_node and "technical_level" in prereq_node:
                        prereq_level = prereq_node["technical_level"].lower()
                        if prereq_level in self.valid_technical_levels:
                            prereq_level_idx = self.valid_technical_levels.index(prereq_level)
                            if prereq_level_idx > current_level_idx:
                                issues.append("higher technical level prerequisite")
        return issues

    def _check_isolated_nodes(self, nodes):
        """Check for isolated nodes (no incoming or outgoing connections)."""
        connected_nodes = set()
        for node in nodes:
            for prereq in node.get("required_prerequisites", []):
                connected_nodes.add(prereq)
                connected_nodes.add(node["id"])
        
        issues = []
        for node in nodes:
            if node["id"] not in connected_nodes:
                issues.append(f"Node {node['id']} is isolated")
        return issues

    def _check_learning_path_length(self, nodes):
        """Check for overly long learning paths."""
        def get_path_length(node_id, visited=None):
            if visited is None:
                visited = set()
            if node_id in visited:
                return 0
            visited.add(node_id)
            try:
                node = next(n for n in nodes if n["id"] == node_id)
                if not node.get("required_prerequisites"):
                    return 1
                prereq_lengths = [get_path_length(prereq, visited.copy()) for prereq in node["required_prerequisites"]]
                return 1 + max(prereq_lengths) if prereq_lengths else 1
            except StopIteration:
                return 0

        try:
            max_length = max(get_path_length(node["id"]) for node in nodes)
            if max_length > self.max_path_length:
                return [f"Learning path too long: {max_length} nodes (maximum {self.max_path_length})"]
        except ValueError:
            pass
        return []

    def _check_non_progressive_paths(self, nodes):
        """Check for non-progressive technical levels in learning paths."""
        technical_level_order = {level: idx for idx, level in enumerate(self.valid_technical_levels)}
        issues = []
        
        for node in nodes:
            if "technical_level" not in node:
                continue
            level = node.get("technical_level", "").lower()
            if level not in technical_level_order:
                continue
            current_level = technical_level_order[level]
            for prereq_id in node.get("required_prerequisites", []):
                prereq_node = next((n for n in nodes if n["id"] == prereq_id), None)
                if prereq_node and "technical_level" in prereq_node:
                    prereq_level = prereq_node["technical_level"].lower()
                    if prereq_level in technical_level_order:
                        prereq_level_idx = technical_level_order[prereq_level]
                        if prereq_level_idx > current_level:
                            issues.append("Non-progressive technical levels detected")
                            break
        return issues

    def _check_excessive_branching(self, nodes):
        """Check for excessive branching (too many alternative paths)."""
        issues = []
        for node in nodes:
            dependents = sum(1 for n in nodes if node["id"] in n.get("required_prerequisites", []))
            if dependents > self.max_branching_factor:
                issues.append("too many dependent nodes")
        return issues

    def _check_excessive_prerequisites(self, nodes):
        """Check for nodes with too many prerequisites."""
        issues = []
        for node in nodes:
            prereq_count = len(node.get("required_prerequisites", []))
            if prereq_count > self.max_prerequisites_per_node:
                issues.append("too many prerequisites")
        return issues

    def _check_imbalanced_technical_levels(self, nodes):
        """Check for imbalanced distribution of technical levels."""
        level_counts = {level: 0 for level in self.valid_technical_levels}
        total_nodes = len(nodes)
        
        for node in nodes:
            if "technical_level" in node:
                level = node["technical_level"].lower()
                if level in level_counts:
                    level_counts[level] += 1
        
        # Check if any level has more than 50% of nodes
        threshold = total_nodes * 0.5
        for level, count in level_counts.items():
            if count > threshold:
                issues = [f"Imbalanced technical level distribution: too many {level} nodes ({count}/{total_nodes})"]
                return issues
        return []

    def _check_missing_technical_levels(self, nodes):
        """Check for missing technical levels in the knowledge map."""
        required_levels = {"beginner", "intermediate", "advanced", "expert"}
        present_levels = {node.get("technical_level", "").lower() for node in nodes}
        missing_levels = required_levels - present_levels
        
        # Only report missing levels if there are higher levels present
        issues = []
        if "expert" in present_levels and ("intermediate" not in present_levels or "advanced" not in present_levels):
            missing = []
            if "intermediate" not in present_levels:
                missing.append("intermediate")
            if "advanced" not in present_levels:
                missing.append("advanced")
            if missing:
                issues.append(f"Missing technical levels: {', '.join(missing)}")
        elif "advanced" in present_levels and "intermediate" not in present_levels:
            issues.append("Missing technical levels: intermediate")
            
        return issues

    def _check_bottlenecks(self, nodes):
        """Check for bottleneck nodes (required by many paths)."""
        def count_dependencies(node_id, visited=None):
            if visited is None:
                visited = set()
            if node_id in visited:
                return 0
            visited.add(node_id)
            count = 0
            for node in nodes:
                if node_id in node.get("required_prerequisites", []):
                    count += 1 + count_dependencies(node["id"], visited.copy())
            return count

        issues = []
        total_nodes = len(nodes)
        bottleneck_nodes = []
        
        for node in nodes:
            dep_count = count_dependencies(node["id"])
            if dep_count > total_nodes * 0.35:  # Adjust threshold for bottleneck detection
                bottleneck_nodes.append(node["id"])
        
        if len(bottleneck_nodes) > 2:
            issues.append("Multiple bottleneck nodes detected")
        return issues

    def validate_map(self, nodes):
        """Validate the knowledge map."""
        if not nodes:
            return ValidationResult(False, ["Empty knowledge map"], 1.0)
            
        # Check for critical issues first
        critical_issues = []
        critical_issues.extend(self._check_missing_fields(nodes))
        critical_issues.extend(self._check_duplicate_ids(nodes))
        critical_issues.extend(self._check_undefined_prerequisites(nodes))
        critical_issues.extend(self._check_circular_dependencies(nodes))
        critical_issues.extend(self._check_technical_level_validation(nodes))
        critical_issues.extend(self._check_description_length(nodes))
        critical_issues.extend(self._check_non_progressive_paths(nodes))
        critical_issues.extend(self._check_isolated_nodes(nodes))
        critical_issues.extend(self._check_learning_path_length(nodes))
        critical_issues.extend(self._check_excessive_branching(nodes))
        critical_issues.extend(self._check_excessive_prerequisites(nodes))
        critical_issues.extend(self._check_imbalanced_technical_levels(nodes))
        critical_issues.extend(self._check_missing_technical_levels(nodes))
        critical_issues.extend(self._check_bottlenecks(nodes))
        
        # Calculate confidence score based on number and severity of issues
        confidence_score = self._calculate_confidence_score(critical_issues)
        
        # A map is valid only if there are no critical issues
        is_valid = len(critical_issues) == 0
        
        return ValidationResult(is_valid, critical_issues, confidence_score)

    def _calculate_confidence_score(self, issues):
        """Calculate confidence score based on number and severity of issues."""
        if not issues:
            return 1.0
        return max(0.0, 1.0 - (len(issues) * 0.1)) 