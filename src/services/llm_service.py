from typing import Dict, List
import json
import openai
import os

class LLMService:
    def __init__(self):
        """Initialize the LLM service"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        
    def answer_query(self, query: str, use_case: str, knowledge_map: Dict) -> str:
        """Answer a query using the RAG knowledge base"""
        # Extract relevant knowledge items based on the query
        knowledge_items = knowledge_map.get("knowledge_items", [])
        
        # Format knowledge items for better context
        formatted_knowledge = []
        for item in knowledge_items:
            formatted_knowledge.append(f"""
Topic: {item.get('type', 'concept')}
Content: {item.get('content', '')}
Validation Rules: {', '.join(item.get('validation_criteria', []))}
Related Topics: {', '.join(item.get('relationships', []))}
""")
        
        prompt = f"""Given the following knowledge base and query, provide a detailed and accurate answer.
Use only the information from the knowledge base to inform your response.

Use Case: {use_case}

Knowledge Base:
{chr(10).join(formatted_knowledge)}

Query: {query}

Please provide a comprehensive answer based on the knowledge base. If the knowledge base does not contain relevant information to answer the query, please state that explicitly."""
        
        response = self._query_llm(prompt, require_json=False)
        return response

    def analyze_bug_report(self, bug_description: str, use_case: str, knowledge_map: Dict, test_cases: Dict) -> Dict:
        """Analyze a bug report to identify knowledge gaps and improvement opportunities"""
        prompt = f"""Analyze the following bug report in the context of the existing knowledge map and test cases.
        Identify any knowledge gaps, missing validations, or areas for improvement.
        
        Use Case: {use_case}
        
        Bug Report:
        {bug_description}
        
        Knowledge Map:
        {json.dumps(knowledge_map, indent=2)}
        
        Test Cases:
        {json.dumps(test_cases, indent=2)}
        
        Please provide:
        1. Analysis of the root cause
        2. Identified knowledge gaps
        3. Suggested improvements to the knowledge map
        4. Recommendations for new validation rules
        
        Format your response as a JSON object with these keys:
        {{
            "root_cause": "string",
            "knowledge_gaps": ["string"],
            "improvements": ["string"],
            "validation_rules": ["string"]
        }}"""
        
        try:
            response = self._query_llm(prompt, require_json=True)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {response}")
            return {
                "root_cause": "Error analyzing bug report",
                "knowledge_gaps": [],
                "improvements": [],
                "validation_rules": []
            }

    def generate_test_cases_from_bug(self, bug_description: str, use_case: str, domain: str, existing_test_cases: Dict) -> List[Dict]:
        """Generate new test cases based on a bug report"""
        prompt = f"""Given the following bug report and existing test cases, generate new test cases to prevent similar issues.
        The test cases should validate that the bug scenario is properly handled and prevent regression.
        
        Use Case: {use_case}
        Domain: {domain}
        
        Bug Report:
        {bug_description}
        
        Existing Test Cases:
        {json.dumps(existing_test_cases, indent=2)}
        
        Generate new test cases that:
        1. Verify the bug scenario is handled correctly
        2. Test edge cases related to the bug
        3. Validate any new knowledge or rules added
        
        Format each test case as a JSON object with:
        - id: string (format: "TC-{{number}}")
        - title: string
        - description: string
        - complexity: string (low, medium, high)
        - validation_rules: array of strings
        
        Return an array of test case objects in this format:
        [
            {{
                "id": "TC-001",
                "title": "Example Test Case",
                "description": "Description of what is being tested",
                "complexity": "medium",
                "validation_rules": ["Rule 1", "Rule 2"]
            }}
        ]"""
        
        try:
            response = self._query_llm(prompt, require_json=True)
            test_cases = json.loads(response)
            if not isinstance(test_cases, list):
                raise ValueError("Response is not a list of test cases")
            return test_cases
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error generating test cases: {str(e)}")
            print(f"Response was: {response}")
            return []
        
    def _query_llm(self, prompt: str, require_json: bool = False) -> str:
        """Query the LLM with a prompt"""
        system_prompt = """You are a helpful assistant that provides accurate and relevant information."""
        if require_json:
            system_prompt += """
Your responses should be properly formatted JSON objects that can be parsed by json.loads().
Make sure to escape any special characters and format the JSON correctly.
Do not include any explanatory text outside the JSON object."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def extract_knowledge_structure(self, use_case: str) -> Dict:
        """Extract knowledge structure from a use case description"""
        prompt = f"""Given the following use case, create a comprehensive knowledge map.
        The knowledge map should include core concepts, relationships, validation rules, and best practices.
        
        Use Case:
        {use_case}
        
        Create a knowledge map with:
        1. Core concepts and their definitions
        2. Relationships between concepts
        3. Validation rules for each concept
        4. Best practices and guidelines
        5. Common pitfalls to avoid
        
        Format the response as a JSON object with:
        - knowledge_items: array of objects with id, type, content, relationships, and validation_criteria
        - validation_rules: array of objects with id and description
        
        Each knowledge item should have:
        - id: string (format: "KI-{{number}}")
        - type: string (concept, rule, best_practice, pitfall)
        - content: string
        - relationships: array of strings (other KI ids)
        - validation_criteria: array of strings (validation rule ids)"""
        
        try:
            response = self._query_llm(prompt, require_json=True)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {response}")
            return {
                "knowledge_items": [],
                "validation_rules": []
            }

    def generate_test_cases(self, use_case: str, domain: str) -> Dict:
        """Generate comprehensive test cases for a use case"""
        prompt = f"""Given the following use case, generate comprehensive test cases.
        The test cases should validate all aspects of the use case and cover edge cases.
        
        Use Case:
        {use_case}
        Domain: {domain}
        
        Generate test cases that:
        1. Validate core functionality
        2. Test edge cases and error conditions
        3. Verify best practices are followed
        4. Check for common pitfalls
        
        Format the response as a JSON object with:
        - test_cases: array of objects with id, title, description, complexity, and validation_rules
        
        Each test case should have:
        - id: string (format: "TC-{{number}}")
        - title: string
        - description: string
        - complexity: string (low, medium, high)
        - validation_rules: array of strings"""
        
        try:
            response = self._query_llm(prompt, require_json=True)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {response}")
            return {
                "test_cases": []
            }

    def validate_knowledge(self, use_case: str, domain: str, knowledge_map: Dict, test_cases: Dict) -> Dict:
        """Validate the current knowledge against test cases"""
        prompt = f"""Validate the current knowledge map against the test cases for this use case.
        Identify any issues, gaps, or inconsistencies that need to be addressed.
        
        Use Case: {use_case}
        Domain: {domain}
        
        Knowledge Map:
        {json.dumps(knowledge_map, indent=2)}
        
        Test Cases:
        {json.dumps(test_cases, indent=2)}
        
        Analyze the knowledge map and test cases to:
        1. Calculate a success rate (0.0 to 1.0)
        2. Identify any issues that need to be addressed
        3. Suggest areas for improvement
        
        Format the response as a JSON object with:
        - success_rate: float
        - issues: array of objects with type and description
        - recommendations: array of strings"""
        
        try:
            response = self._query_llm(prompt, require_json=True)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {response}")
            return {
                "success_rate": 0.0,
                "issues": [],
                "recommendations": []
            }

    def analyze_improvements(self, issues: List[Dict], knowledge_map: Dict, test_cases: Dict, domain: str) -> Dict:
        """Analyze issues and recommend improvements"""
        prompt = f"""Given the following validation issues, recommend improvements to the knowledge map.
        
        Issues:
        {json.dumps(issues, indent=2)}
        
        Current Knowledge Map:
        {json.dumps(knowledge_map, indent=2)}
        
        Test Cases:
        {json.dumps(test_cases, indent=2)}
        
        Analyze the issues and recommend improvements:
        1. Identify patterns in the issues
        2. Suggest specific updates to the knowledge map
        3. Recommend new knowledge items if needed
        
        Format the response as a JSON object with:
        - explanation: string (detailed explanation of the improvement plan)
        - knowledge_updates: array of objects with:
          - type: string (add or update)
          - id: string (for updates)
          - content: object or string"""
        
        try:
            response = self._query_llm(prompt, require_json=True)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {response}")
            return {
                "explanation": "Error analyzing improvements",
                "knowledge_updates": []
            } 