import json
import os
import re
from typing import Any, Dict, List, Optional

import openai
from dotenv import load_dotenv


def _strip_json_fences(text: str) -> str:
    t = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", t)
    if m:
        return m.group(1).strip()
    return t


def parse_llm_json(text: str) -> Any:
    """Parse JSON from model output; tolerate markdown fences and leading junk."""
    t = _strip_json_fences(text)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(t[start : end + 1])
        start = t.find("[")
        end = t.rfind("]")
        if start != -1 and end != -1 and end > start:
            return json.loads(t[start : end + 1])
        raise


class LLMService:
    def __init__(self):
        """Initialize the LLM service"""
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        openai.api_key = api_key
        self.client = openai.OpenAI()
        self.chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    def answer_query(
        self,
        query: str,
        use_case: str,
        knowledge_map: Dict,
        retrieved_items: Optional[List[Dict]] = None,
        retrieval_scores: Optional[List[float]] = None,
    ) -> str:
        """Answer using retrieved knowledge items; cite item ids when relevant."""
        if retrieved_items is not None:
            items = retrieved_items
            scores = retrieval_scores or [0.0] * len(items)
        else:
            items = list(knowledge_map.get("knowledge_items", []) or [])
            scores = [0.0] * len(items)

        formatted_blocks = []
        for idx, item in enumerate(items):
            score_note = ""
            if idx < len(scores) and scores[idx] > 0:
                score_note = f"\nRelevance score: {scores[idx]:.3f}"
            formatted_blocks.append(
                f"""
[Knowledge item id: {item.get("id", "unknown")}]{score_note}
Topic: {item.get("type", "concept")}
Content: {item.get("content", "")}
Validation Rules: {", ".join(item.get("validation_criteria", []) or [])}
Related Topics: {", ".join(item.get("relationships", []) or [])}
"""
            )

        context = "\n".join(formatted_blocks).strip()
        if not context:
            context = "(No knowledge items available.)"

        prompt = f"""You are answering using ONLY the knowledge excerpts below (each labeled with a knowledge item id).
If the excerpts do not contain enough information, say so clearly.

Use Case: {use_case}

Knowledge excerpts:
{context}

Question: {query}

Instructions:
- Ground your answer in the excerpts; when you use a fact from an excerpt, mention its knowledge item id in parentheses, e.g. (KI-001).
- If nothing applies, state that the knowledge base does not cover this question."""

        return self._query_llm(prompt, require_json=False)

    def analyze_bug_report(
        self, bug_description: str, use_case: str, knowledge_map: Dict, test_cases: Dict
    ) -> Dict:
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

        Respond with a JSON object (and only that) with these keys:
        "root_cause" (string),
        "knowledge_gaps" (array of strings),
        "improvements" (array of strings),
        "validation_rules" (array of strings)."""

        raw = ""
        try:
            raw = self._query_llm(prompt, require_json=True)
            data = parse_llm_json(raw)
            if isinstance(data, dict):
                return {
                    "root_cause": str(data.get("root_cause", "")),
                    "knowledge_gaps": list(data.get("knowledge_gaps", []) or []),
                    "improvements": list(data.get("improvements", []) or []),
                    "validation_rules": list(data.get("validation_rules", []) or []),
                }
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {raw!r}")
        return {
            "root_cause": "Error analyzing bug report",
            "knowledge_gaps": [],
            "improvements": [],
            "validation_rules": [],
        }

    def generate_test_cases_from_bug(
        self,
        bug_description: str,
        use_case: str,
        domain: str,
        existing_test_cases: Dict,
    ) -> List[Dict]:
        """Generate new test cases based on a bug report"""
        prompt = f"""Given the following bug report and existing test cases, generate new test cases to prevent similar issues.

        Use Case: {use_case}
        Domain: {domain}

        Bug Report:
        {bug_description}

        Existing Test Cases:
        {json.dumps(existing_test_cases, indent=2)}

        Respond with a JSON object (and only that) with key "new_test_cases" whose value is an array of objects.
        Each object must have: id (string, format TC-{{number}}), title, description, complexity (low|medium|high), validation_rules (array of strings)."""

        raw = ""
        try:
            raw = self._query_llm(prompt, require_json=True)
            data = parse_llm_json(raw)
            if isinstance(data, dict):
                test_cases = data.get("new_test_cases")
                if isinstance(test_cases, list):
                    return test_cases
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error generating test cases: {str(e)}")
            print(f"Response was: {raw!r}")
        return []

    def _query_llm(self, prompt: str, require_json: bool = False) -> str:
        """Query the LLM with a prompt"""
        system_prompt = """You are a helpful assistant that provides accurate and relevant information."""
        if require_json:
            system_prompt += (
                " Always respond with a single valid JSON value matching the user instructions. "
                "No markdown, no commentary outside JSON."
            )

        kwargs: Dict[str, Any] = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }
        if require_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return content if content is not None else ""

    def extract_knowledge_structure(self, use_case: str) -> Dict:
        """Extract knowledge structure from a use case description"""
        prompt = f"""Given the following use case, create a comprehensive knowledge map.

        Use Case:
        {use_case}

        Respond with a JSON object (and only that) with:
        "knowledge_items": array of objects with id, type, content, relationships, validation_criteria
        "validation_rules": array of objects with id and description

        Each knowledge item: id (string KI-{{number}}), type (concept|rule|best_practice|pitfall), content (string),
        relationships (array of KI id strings), validation_criteria (array of validation rule id strings)."""

        raw = ""
        try:
            raw = self._query_llm(prompt, require_json=True)
            data = parse_llm_json(raw)
            if isinstance(data, dict):
                return {
                    "knowledge_items": list(data.get("knowledge_items", []) or []),
                    "validation_rules": list(data.get("validation_rules", []) or []),
                }
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {raw!r}")
        return {"knowledge_items": [], "validation_rules": []}

    def generate_test_cases(self, use_case: str, domain: str) -> Dict:
        """Generate comprehensive test cases for a use case"""
        prompt = f"""Given the following use case, generate comprehensive test cases.

        Use Case:
        {use_case}
        Domain: {domain}

        Respond with a JSON object (and only that) with key "test_cases": array of objects with
        id (TC-{{number}}), title, description, complexity (low|medium|high), validation_rules (array of strings)."""

        raw = ""
        try:
            raw = self._query_llm(prompt, require_json=True)
            data = parse_llm_json(raw)
            if isinstance(data, dict):
                return {"test_cases": list(data.get("test_cases", []) or [])}
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {raw!r}")
        return {"test_cases": []}

    def validate_knowledge(
        self, use_case: str, domain: str, knowledge_map: Dict, test_cases: Dict
    ) -> Dict:
        """Validate the current knowledge against test cases"""
        prompt = f"""Validate the current knowledge map against the test cases.

        Use Case: {use_case}
        Domain: {domain}

        Knowledge Map:
        {json.dumps(knowledge_map, indent=2)}

        Test Cases:
        {json.dumps(test_cases, indent=2)}

        Respond with JSON only: success_rate (number 0-1), issues (array of objects with type and description), recommendations (array of strings)."""

        raw = ""
        try:
            raw = self._query_llm(prompt, require_json=True)
            data = parse_llm_json(raw)
            if isinstance(data, dict):
                sr = data.get("success_rate", 0.0)
                try:
                    sr_f = float(sr)
                except (TypeError, ValueError):
                    sr_f = 0.0
                return {
                    "success_rate": max(0.0, min(1.0, sr_f)),
                    "issues": list(data.get("issues", []) or []),
                    "recommendations": list(data.get("recommendations", []) or []),
                }
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {raw!r}")
        return {"success_rate": 0.0, "issues": [], "recommendations": []}

    def analyze_improvements(
        self, issues: List[Dict], knowledge_map: Dict, test_cases: Dict, domain: str
    ) -> Dict:
        """Analyze issues and recommend improvements"""
        prompt = f"""Given the following validation issues, recommend improvements to the knowledge map.

        Issues:
        {json.dumps(issues, indent=2)}

        Current Knowledge Map:
        {json.dumps(knowledge_map, indent=2)}

        Test Cases:
        {json.dumps(test_cases, indent=2)}

        Respond with JSON only: explanation (string), knowledge_updates (array of objects with type add|update, id optional, content object or string)."""

        raw = ""
        try:
            raw = self._query_llm(prompt, require_json=True)
            data = parse_llm_json(raw)
            if isinstance(data, dict):
                return {
                    "explanation": str(data.get("explanation", "")),
                    "knowledge_updates": list(data.get("knowledge_updates", []) or []),
                }
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error decoding JSON response: {str(e)}")
            print(f"Response was: {raw!r}")
        return {"explanation": "Error analyzing improvements", "knowledge_updates": []}
