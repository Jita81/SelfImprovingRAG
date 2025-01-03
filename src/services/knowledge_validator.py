from typing import List, Dict, Any, Optional
from datetime import timedelta
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from src.models.use_case import UseCase
from src.models.validation_result import ValidationResult
from src.models.validation_history import ValidationHistory

class KnowledgeValidator:
    """Service for validating knowledge content against use case requirements"""
    
    def __init__(self, model_name: str, timeout: float = 30.0):
        """Initialize the validator with model name and timeout"""
        self.model_name = model_name
        self.timeout = timeout
        self.chain = self._setup_chain()
        self.history = ValidationHistory()
    
    def _setup_chain(self):
        """Set up the validation chain"""
        prompt = PromptTemplate.from_template(
            """You are a knowledge content validator. Your task is to validate content against use case requirements.

Use Case:
Name: {name}
Description: {description}
Technical Level: {technical_level}
Success Criteria: {success_criteria}

Content to validate:
{content}

Dependencies:
{dependencies}

Validate the content and provide a detailed assessment. Consider:

1. Technical Level Appropriateness
- For expert level: Content must cover advanced topics, internal details, and edge cases
- For intermediate level: Content should balance theory and practical examples
- For beginner level: Content should focus on fundamentals with simple examples

2. Success Criteria Coverage
- Check if each criterion is adequately covered
- Look for specific explanations and examples
- Consider depth and accuracy of coverage

3. Content Quality
- Clarity and accuracy of explanations
- Presence and quality of examples
- Appropriate level of detail

4. Dependencies and Prerequisites
- Check if prerequisites are properly referenced
- Verify dependency relationships are valid

Return your assessment in the following JSON format:

{{
    "technical_level_appropriate": true/false,
    "criteria_coverage": {{
        "criterion1": "covered/partial/not_covered",
        "criterion2": "covered/partial/not_covered"
    }},
    "improvement_suggestions": [
        "suggestion1",
        "suggestion2"
    ]
}}

Be strict about technical level requirements but lenient about content coverage if the explanations are clear and accurate."""
        )
        
        return prompt | ChatOpenAI(
            model_name=self.model_name,
            temperature=0,
            request_timeout=self.timeout
        ) | JsonOutputParser()
    
    def validate_content(self, content: str, use_case: UseCase) -> ValidationResult:
        """Validate content against use case requirements"""
        try:
            result = self.chain.invoke({
                "name": use_case.name,
                "description": use_case.description,
                "technical_level": use_case.technical_level,
                "success_criteria": use_case.success_criteria,
                "content": content,
                "dependencies": use_case.dependencies
            })

            issues = []
            covered_criteria = 0
            total_criteria = 0
            
            # Check technical level
            if not result.get("technical_level_appropriate", True):
                issues.append(f"Content is not appropriate for {use_case.technical_level} technical level")
                
            # Check criteria coverage
            coverage = result.get("criteria_coverage", {})
            for criterion, status in coverage.items():
                total_criteria += 1
                if status == "covered":
                    covered_criteria += 1
                elif status == "partial":
                    covered_criteria += 0.5
                if status != "covered":
                    issues.append(f"Incomplete coverage of criterion: {criterion}")
                    
            # Add improvement suggestions
            for suggestion in result.get("improvement_suggestions", []):
                issues.append(suggestion)

            # Calculate confidence score based on criteria coverage and technical level appropriateness
            coverage_score = covered_criteria / max(1, total_criteria)
            technical_level_score = 1.0 if result.get("technical_level_appropriate", True) else 0.5
            
            # Adjust confidence based on number of issues
            issue_penalty = len(issues) * 0.1  # Each issue reduces confidence by 10%
            confidence_score = max(0.0, min(1.0, (coverage_score + technical_level_score) / 2 - issue_penalty))

            validation_result = ValidationResult(
                is_valid=len(issues) == 0,
                issues=issues,
                confidence_score=confidence_score
            )
            
            # Add result to history
            self.history.add_result(validation_result)
            return validation_result

        except TimeoutError:
            result = ValidationResult(
                is_valid=False, 
                issues=["Validation timed out"],
                confidence_score=0.0
            )
            self.history.add_result(result)
            return result
            
        except Exception as e:
            result = ValidationResult(
                is_valid=False,
                issues=[f"Validation error: {str(e)}"],
                confidence_score=0.0
            )
            self.history.add_result(result)
            return result
            
    def get_validation_trends(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get validation trends from history"""
        return {
            "average_confidence": self.history.get_average_confidence(time_window),
            "common_issues": self.history.get_common_issues()
        } 