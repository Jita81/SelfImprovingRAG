import json
import re
from typing import Dict, List, Tuple
from collections import Counter

class UserStoryValidator:
    def __init__(self, knowledge_map_path: str, test_cases_path: str):
        with open(knowledge_map_path, 'r') as f:
            self.knowledge_map = json.load(f)
        with open(test_cases_path, 'r') as f:
            self.test_cases = json.load(f)
        self.knowledge_map_path = knowledge_map_path
        self.test_cases_path = test_cases_path
        self.improvement_history = []
        
    def validate_basic_format(self, story: str) -> Tuple[bool, List[str]]:
        pattern = r"As an? (.+), I want (.+) so that (.+)"
        match = re.match(pattern, story)
        issues = []
        
        if not match:
            issues.append("Story does not follow 'As a/I want/so that' format")
            return False, issues
            
        role, goal, benefit = match.groups()
        
        if not role.strip():
            issues.append("Role is missing or empty")
        if not goal.strip():
            issues.append("Goal is missing or empty")
        if not benefit.strip():
            issues.append("Benefit is missing or empty")
            
        return len(issues) == 0, issues
        
    def validate_invest_criteria(self, story: str) -> Tuple[bool, List[str]]:
        """Validate INVEST criteria with enhanced testability checks."""
        issues = []
        words = story.lower().split()
        
        # Independence check (improved)
        dependency_indicators = ["depends", "after", "before", "requires", "following"]
        if any(ind in words for ind in dependency_indicators):
            issues.append("Story may have dependencies")
            
        # Negotiable check (improved)
        implementation_indicators = ["using", "via", "through", "must", "should", "shall"]
        if any(ind in words for ind in implementation_indicators):
            issues.append("Story contains implementation details")
            
        # Valuable check (improved)
        if "so that" not in story.lower() or len(story.split("so that")[1].strip()) < 10:
            issues.append("Story does not clearly state its value")
            
        # Estimable check (improved)
        if len(words) > 50:
            issues.append("Story may be too complex to estimate")
        elif len(words) < 10:
            issues.append("Story may lack sufficient detail to estimate")
            
        # Small check (improved)
        conjunction_count = sum(1 for word in words if word in ["and", "or", "also", "additionally"])
        if conjunction_count > 1:
            issues.append("Story may be too large or contain multiple stories")
            
        # Testable check (improved with specific actions and outcomes)
        testable_words = {
            # User interface actions
            "click": "user action",
            "select": "user action",
            "choose": "user action",
            "enter": "user action",
            "submit": "user action",
            "upload": "user action",
            "download": "user action",
            "view": "user action",
            "search": "user action",
            
            # System actions
            "display": "system action",
            "show": "system action",
            "create": "system action",
            "update": "system action",
            "delete": "system action",
            "process": "system action",
            "calculate": "system action",
            "validate": "system action",
            "verify": "system action",
            
            # Measurable outcomes
            "within": "measurable",
            "equals": "measurable",
            "greater": "measurable",
            "less": "measurable",
            "minimum": "measurable",
            "maximum": "measurable",
            "seconds": "measurable",
            "minutes": "measurable",
            "percentage": "measurable",
            "successfully": "measurable",
            "complete": "measurable"
        }
        
        # Check for different types of testable elements
        has_user_action = any(word in words and testable_words[word] == "user action" 
                            for word in testable_words if word in words)
        has_system_action = any(word in words and testable_words[word] == "system action" 
                              for word in testable_words if word in words)
        has_measurable = any(word in words and testable_words[word] == "measurable" 
                           for word in testable_words if word in words)
        
        # Context-aware testability check
        if not (has_user_action or has_system_action):
            issues.append("Story needs specific user or system actions")
        if not has_measurable:
            issues.append("Story needs measurable outcomes")
            
        return len(issues) == 0, issues
        
    def validate_acceptance_criteria(self, criteria: List[str]) -> Tuple[bool, List[str]]:
        """Validate acceptance criteria format and content."""
        issues = []
        pattern = r"Given (.+) When (.+) Then (.+)"
        
        if not criteria:
            issues.append("No acceptance criteria provided")
            return False, issues
            
        if len(criteria) < 2:
            issues.append("Too few acceptance criteria (minimum 2)")
        elif len(criteria) > 5:
            issues.append("Too many acceptance criteria (maximum 5)")
            
        # Track coverage of different scenarios
        has_happy_path = False
        has_error_case = False
        has_measurable_outcome = False
        
        error_indicators = ["invalid", "error", "fail", "missing", "incorrect", "not found", "unauthorized"]
        measurable_indicators = ["within", "equals", "greater than", "less than", "maximum", "minimum", 
                               "seconds", "minutes", "hours", "percentage", "count", "size", "length"]
        
        for criterion in criteria:
            if not re.match(pattern, criterion):
                issues.append(f"Criterion does not follow Given-When-Then format: {criterion}")
                continue
                
            # Extract sections
            given, when, then = re.match(pattern, criterion).groups()
            
            # Check section lengths
            if len(given.strip()) < 5:
                issues.append(f"Given section too brief: {given}")
            if len(when.strip()) < 5:
                issues.append(f"When section too brief: {when}")
            if len(then.strip()) < 5:
                issues.append(f"Then section too brief: {then}")
                
            # Check for error cases
            if any(indicator in criterion.lower() for indicator in error_indicators):
                has_error_case = True
                
            # Check for measurable outcomes
            if any(indicator in criterion.lower() for indicator in measurable_indicators):
                has_measurable_outcome = True
                
            # Check for happy path (criteria without error indicators)
            if not any(indicator in criterion.lower() for indicator in error_indicators):
                has_happy_path = True
                
            # Check for ambiguous language
            ambiguous_terms = ["appropriate", "correct", "proper", "valid", "normal", "good", "bad"]
            found_ambiguous = [term for term in ambiguous_terms if term in criterion.lower()]
            if found_ambiguous:
                issues.append(f"Criterion contains ambiguous terms: {', '.join(found_ambiguous)}")
                
            # Check for testability
            if not has_measurable_outcome and not any(indicator in criterion.lower() for indicator in measurable_indicators):
                issues.append(f"Criterion may not be testable - needs measurable outcomes: {criterion}")
                
        # Validate scenario coverage
        if not has_happy_path:
            issues.append("Missing happy path scenario in acceptance criteria")
        if not has_error_case:
            issues.append("Missing error case scenario in acceptance criteria")
        if not has_measurable_outcome:
            issues.append("No measurable outcomes in acceptance criteria")
            
        return len(issues) == 0, issues
        
    def validate_story_splitting(self, original: str, split_stories: List[str]) -> Tuple[bool, List[str]]:
        """Validate story splitting and generate split stories if needed."""
        issues = []
        
        # If no split stories provided, generate them
        if not split_stories:
            split_stories = self._generate_split_stories(original)
            
        if len(split_stories) < 2:
            issues.append("Not enough split stories (minimum 2)")
        elif len(split_stories) > 5:
            issues.append("Too many split stories (maximum 5)")
            
        # Extract key components from original story
        original_match = re.match(r"As an? (.+), I want (.+) so that (.+)", original)
        if not original_match:
            issues.append("Original story does not follow proper format")
            return False, issues
            
        original_role, original_goal, original_benefit = original_match.groups()
        original_components = {
            "role": set(original_role.lower().split()),
            "goal": set(original_goal.lower().split()),
            "benefit": set(original_benefit.lower().split())
        }
        
        for story in split_stories:
            # Extract components from split story
            split_match = re.match(r"As an? (.+), I want (.+) so that (.+)", story)
            if not split_match:
                issues.append(f"Split story does not follow proper format: {story}")
                continue
                
            split_role, split_goal, split_benefit = split_match.groups()
            split_components = {
                "role": set(split_role.lower().split()),
                "goal": set(split_goal.lower().split()),
                "benefit": set(split_benefit.lower().split())
            }
            
            # Check role consistency
            if not split_components["role"].intersection(original_components["role"]):
                issues.append(f"Split story role may not match original: {story}")
            
            # Check goal relationship
            goal_relation = len(split_components["goal"].intersection(original_components["goal"]))
            if goal_relation == 0:
                issues.append(f"Split story goal may not be related to original: {story}")
            
            # Check benefit alignment
            benefit_relation = len(split_components["benefit"].intersection(original_components["benefit"]))
            if benefit_relation == 0:
                issues.append(f"Split story benefit may not align with original: {story}")
            
            # Size check based on goal component
            if len(split_goal.split()) >= len(original_goal.split()):
                issues.append(f"Split story goal is not smaller than original: {story}")
                
        return len(issues) == 0, issues
        
    def _generate_split_stories(self, original: str) -> List[str]:
        """Generate split stories from a large story."""
        # Extract components
        match = re.match(r"As an? (.+), I want (.+) so that (.+)", original)
        if not match:
            return []
            
        role, goal, benefit = match.groups()
        
        # Find conjunctions and split points
        goal_parts = re.split(r",\s*(?:and|or)\s+|\s+and\s+|\s*,\s*", goal)
        
        # Generate individual stories
        split_stories = []
        for part in goal_parts:
            if part.strip():
                # Create a focused benefit for each part
                focused_benefit = self._generate_focused_benefit(part, benefit)
                split_story = f"As {role}, I want {part.strip()} so that {focused_benefit}"
                split_stories.append(split_story)
                
        return split_stories
        
    def _generate_focused_benefit(self, goal_part: str, original_benefit: str) -> str:
        """Generate a focused benefit for a split story based on the goal part."""
        # Extract key terms from goal part
        goal_terms = set(goal_part.lower().split())
        benefit_terms = set(original_benefit.lower().split())
        
        # Find common terms
        common_terms = goal_terms.intersection(benefit_terms)
        
        if common_terms:
            # Use the original benefit if there are common terms
            return original_benefit
        else:
            # Generate a specific benefit based on the goal
            action_words = ["manage", "view", "create", "update", "delete", "process", "handle"]
            for word in action_words:
                if word in goal_part.lower():
                    return f"I can effectively {word} this specific aspect"
            
            # Default benefit
            return f"I can achieve this specific functionality"
            
    def validate_refinement(self, original: str, refined: str, details: List[str]) -> Tuple[bool, List[str]]:
        issues = []
        
        # Check basic format for both
        valid_original, original_issues = self.validate_basic_format(original)
        valid_refined, refined_issues = self.validate_basic_format(refined)
        
        if not valid_original:
            issues.extend(["Original story: " + i for i in original_issues])
        if not valid_refined:
            issues.extend(["Refined story: " + i for i in refined_issues])
            
        # Check that refinement adds detail
        if len(refined.split()) <= len(original.split()):
            issues.append("Refined story should add more detail")
            
        # Check that details are meaningful
        for detail in details:
            if len(detail.strip()) < 10:
                issues.append(f"Detail lacks sufficient information: {detail}")
                
        return len(issues) == 0, issues
        
    def validate_advanced_organization(self, epic: str, theme: str, stories: List[str]) -> Tuple[bool, List[str]]:
        issues = []
        
        # Check epic and theme
        if len(epic.strip()) < 5:
            issues.append("Epic name too brief")
        if len(theme.strip()) < 5:
            issues.append("Theme name too brief")
            
        # Validate each story
        for story in stories:
            valid, story_issues = self.validate_basic_format(story)
            if not valid:
                issues.extend(story_issues)
                
        # Check relationships
        story_words = [set(story.lower().split()) for story in stories]
        epic_words = set(epic.lower().split())
        theme_words = set(theme.lower().split())
        
        for words in story_words:
            if not (words.intersection(epic_words) or words.intersection(theme_words)):
                issues.append("Story not clearly related to epic or theme")
                
        return len(issues) == 0, issues
        
    def validate_prerequisites(self, story: str, prerequisites: List[str], dependencies: List[str]) -> Tuple[bool, List[str]]:
        """Validate prerequisites and dependencies of a user story."""
        issues = []
        
        # Check if prerequisites are well-defined
        if not prerequisites:
            issues.append("No prerequisites specified")
        else:
            for prereq in prerequisites:
                if len(prereq.strip()) < 10:
                    issues.append(f"Prerequisite lacks detail: {prereq}")
                    
        # Check if dependencies are well-defined
        if not dependencies:
            issues.append("No dependencies specified")
        else:
            for dep in dependencies:
                if len(dep.strip()) < 10:
                    issues.append(f"Dependency lacks detail: {dep}")
                    
        # Check story format
        valid, format_issues = self.validate_basic_format(story)
        if not valid:
            issues.extend(format_issues)
            
        # Check for explicit dependency indicators
        words = story.lower().split()
        dependency_indicators = ["after", "before", "depends", "requires", "following", "once"]
        found_indicators = [ind for ind in dependency_indicators if ind in words]
        
        if found_indicators:
            # Verify that mentioned dependencies are in the dependencies list
            story_dependencies = set()
            for indicator in found_indicators:
                # Find words after the indicator
                try:
                    idx = words.index(indicator)
                    if idx + 1 < len(words):
                        story_dependencies.add(words[idx + 1])
                except ValueError:
                    continue
                    
            # Check if story dependencies are documented
            dependencies_lower = [dep.lower() for dep in dependencies]
            for dep in story_dependencies:
                if not any(dep in d for d in dependencies_lower):
                    issues.append(f"Story mentions undocumented dependency: {dep}")
                    
        return len(issues) == 0, issues
        
    def run_validation_cycle(self) -> Dict:
        """Run a validation cycle and return results."""
        results = {
            "total_tests": len(self.test_cases["test_cases"]),
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0.0,
            "issues": []
        }
        
        print("\nRunning validation tests:")
        for test_case in self.test_cases["test_cases"]:
            test_passed = False
            test_issues = []
            
            print(f"\nTest Case: {test_case['title']}")
            print(f"Input: {test_case.get('input', 'No input provided')}")
            
            # Get test type from test case title
            test_type = test_case["title"].lower().replace(" ", "_")
            print(f"Test Type: {test_type}")
            
            # Run appropriate validation based on test case type
            if any(keyword in test_type for keyword in ["basic", "format", "verify_basic"]):
                input_data = test_case.get("input", {})
                story = input_data.get("user_story", "") if isinstance(input_data, dict) else input_data
                test_passed, test_issues = self.validate_basic_format(story)
            elif any(keyword in test_type for keyword in ["invest", "criteria", "vague", "technical", "non-functional"]):
                input_data = test_case.get("input", {})
                story = input_data.get("user_story", "") if isinstance(input_data, dict) else input_data
                test_passed, test_issues = self.validate_invest_criteria(story)
            elif "acceptance" in test_type:
                input_data = test_case.get("input", {})
                criteria = input_data.get("acceptance_criteria", []) if isinstance(input_data, dict) else []
                test_passed, test_issues = self.validate_acceptance_criteria(criteria)
            elif any(keyword in test_type for keyword in ["prerequisite", "dependency"]):
                input_data = test_case.get("input", {})
                if isinstance(input_data, dict):
                    test_passed, test_issues = self.validate_prerequisites(
                        input_data.get("user_story", ""),
                        input_data.get("prerequisites", []),
                        input_data.get("dependencies", [])
                    )
                else:
                    test_issues = ["Invalid input format for prerequisite validation"]
            elif any(keyword in test_type for keyword in ["split", "vertical"]):
                input_data = test_case.get("input", {})
                if isinstance(input_data, dict):
                    test_passed, test_issues = self.validate_story_splitting(
                        input_data.get("large_user_story", input_data.get("user_story", "")),
                        input_data.get("split_stories", [])
                    )
                else:
                    test_issues = ["Invalid input format for story splitting"]
            elif "refinement" in test_type:
                input_data = test_case.get("input", {})
                if isinstance(input_data, dict):
                    test_passed, test_issues = self.validate_refinement(
                        input_data.get("user_story", ""),  # Use as original
                        input_data.get("refined_story", input_data.get("user_story", "")),  # Use same if no refined version
                        input_data.get("details", [])
                    )
                else:
                    test_issues = ["Invalid input format for refinement"]
            elif any(keyword in test_type for keyword in ["advanced", "epic", "theme", "mapping", "complex"]):
                input_data = test_case.get("input", {})
                if isinstance(input_data, dict):
                    # Handle user story map format
                    if "user_story_map" in input_data:
                        map_data = input_data["user_story_map"]
                        test_passed, test_issues = self.validate_advanced_organization(
                            map_data.get("epic", ""),
                            map_data.get("theme", "User Story Theme"),  # Default theme if not provided
                            map_data.get("stories", [])
                        )
                    else:
                        test_passed, test_issues = self.validate_advanced_organization(
                            input_data.get("epic", ""),
                            input_data.get("theme", ""),
                            input_data.get("stories", [])
                        )
                else:
                    test_issues = ["Invalid input format for advanced organization"]
            else:
                test_issues = [f"Unknown test type: {test_type}"]
                test_passed = False
                
            print(f"Test Passed: {test_passed}")
            if test_issues:
                print(f"Issues: {test_issues}")
                
            # Update results
            if test_passed:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                results["issues"].append({
                    "test_case": test_case["id"],
                    "test_type": test_type,
                    "issues": test_issues
                })
                
        # Calculate success rate
        results["success_rate"] = (results["passed_tests"] / results["total_tests"]) * 100
        print(f"\nValidation Results:")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed Tests: {results['passed_tests']}")
        print(f"Failed Tests: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']}%")
        
        # Record results for pattern analysis
        self.improvement_history.append(results)
        
        return results
        
    def analyze_patterns(self) -> Dict:
        """Analyze patterns in validation issues to guide improvements."""
        if not self.improvement_history:
            return {"patterns": [], "trends": []}
            
        all_issues = []
        for result in self.improvement_history:
            for issue in result["issues"]:
                all_issues.extend(issue["issues"])
                
        # Count issue frequencies
        issue_counts = Counter(all_issues)
        
        # Identify patterns
        patterns = []
        for issue, count in issue_counts.most_common(5):
            pattern = {
                "issue": issue,
                "frequency": count,
                "test_types": set()
            }
            
            # Find which test types this issue appears in
            for result in self.improvement_history:
                for issue_data in result["issues"]:
                    if issue in issue_data["issues"]:
                        pattern["test_types"].add(issue_data["test_type"])
                        
            pattern["test_types"] = list(pattern["test_types"])
            patterns.append(pattern)
            
        # Analyze trends
        trends = []
        if len(self.improvement_history) >= 3:
            recent_results = self.improvement_history[-3:]
            for i, result in enumerate(recent_results):
                trends.append({
                    "cycle": len(self.improvement_history) - 3 + i + 1,
                    "success_rate": result["success_rate"],
                    "issue_count": len(result["issues"])
                })
                
        return {
            "patterns": patterns,
            "trends": trends
        }
        
    def apply_improvements(self, patterns: Dict) -> None:
        """Apply improvements based on identified patterns."""
        if not patterns:
            return
            
        # Load current files
        with open(self.knowledge_map_path, 'r') as f:
            knowledge_map = json.load(f)
        with open(self.test_cases_path, 'r') as f:
            test_cases = json.load(f)
            
        # Apply improvements based on pattern types
        for pattern in patterns.get('patterns', []):
            issue = pattern.get('issue', '')
            test_types = pattern.get('test_types', set())
            
            if 'format' in issue.lower():
                self._strengthen_format_rules(test_cases, list(test_types))
            elif 'criteria' in issue.lower():
                self._enhance_criteria_guidelines(test_cases, list(test_types))
            elif 'size' in issue.lower() or 'length' in issue.lower():
                self._refine_size_guidelines(test_cases, list(test_types))
            elif 'test' in issue.lower():
                self._improve_testability_guidelines(test_cases, list(test_types))
                
        # Save updated files
        with open(self.test_cases_path, 'w') as f:
            json.dump(test_cases, f, indent=2)
            
    def _strengthen_format_rules(self, test_cases: Dict, test_types: List[str]) -> None:
        """Strengthen format validation rules."""
        rules = test_cases.get('validation_rules', {})
        basic_format = rules.get('basic_format', {})
        
        # Add more required elements if needed
        current_elements = set(basic_format.get('required_elements', []))
        additional_elements = {'role', 'goal', 'benefit', 'acceptance_criteria'}
        basic_format['required_elements'] = list(current_elements.union(additional_elements))
        
        # Update format pattern to be more strict
        basic_format['format_pattern'] = r"As an? (.+), I want (.+) so that (.+)"
        
        test_cases['validation_rules']['basic_format'] = basic_format
        
    def _enhance_criteria_guidelines(self, test_cases: Dict, test_types: List[str]) -> None:
        """Enhance acceptance criteria guidelines."""
        rules = test_cases.get('validation_rules', {})
        criteria_rules = rules.get('acceptance_criteria', {})
        
        # Strengthen criteria requirements
        criteria_rules.update({
            'format_pattern': r"Given (.+) When (.+) Then (.+)",
            'min_criteria': max(criteria_rules.get('min_criteria', 2), 2),
            'max_criteria': min(criteria_rules.get('max_criteria', 5), 5),
            'min_section_length': max(criteria_rules.get('min_section_length', 5), 5)
        })
        
        test_cases['validation_rules']['acceptance_criteria'] = criteria_rules
        
    def _refine_size_guidelines(self, test_cases: Dict, test_types: List[str]) -> None:
        """Refine size and complexity guidelines."""
        rules = test_cases.get('validation_rules', {})
        invest_rules = rules.get('invest_criteria', {})
        
        # Update size limits
        size_limits = invest_rules.get('size_limits', {})
        size_limits.update({
            'min_words': max(size_limits.get('min_words', 10), 10),
            'max_words': min(size_limits.get('max_words', 50), 50)
        })
        
        invest_rules['size_limits'] = size_limits
        test_cases['validation_rules']['invest_criteria'] = invest_rules
        
    def _improve_testability_guidelines(self, test_cases: Dict, test_types: List[str]) -> None:
        """Improve testability guidelines."""
        rules = test_cases.get('validation_rules', {})
        invest_rules = rules.get('invest_criteria', {})
        
        # Add testability keywords
        testable_words = [
            'view', 'create', 'update', 'delete',
            'select', 'choose', 'enter', 'submit',
            'receive', 'download', 'upload', 'search'
        ]
        
        # Update value keywords
        value_keywords = set(invest_rules.get('value_keywords', []))
        value_keywords.add('so that')
        invest_rules['value_keywords'] = list(value_keywords)
        
        # Add testability section if not exists
        if 'testability' not in rules:
            rules['testability'] = {
                'action_words': testable_words,
                'min_criteria': 2,
                'require_measurable_outcome': True
            }
            
        test_cases['validation_rules']['invest_criteria'] = invest_rules
        test_cases['validation_rules']['testability'] = rules.get('testability', {}) 