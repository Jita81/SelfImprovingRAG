from typing import Dict, List
import os
import json
from src.services.llm_service import LLMService
from src.models.domain import UseCaseDefinition

class RAGOrchestrator:
    def __init__(self):
        """Initialize the RAG orchestrator"""
        self.llm_service = LLMService()
        self.max_cycles = 3

    def process_bug_report(self, bug_description: str, use_case: str, domain: str) -> Dict:
        """Process a bug report and improve the RAG system"""
        print(f"\n{'='*80}")
        print(f"Processing bug report for {domain} domain")
        print(f"Use case: {use_case}")
        print(f"{'='*80}\n")
        
        # Load existing knowledge map and test cases
        domain_dir = f"data/knowledge_bases/{domain}"
        knowledge_map_path = os.path.join(domain_dir, "knowledge_map.json")
        test_cases_path = os.path.join(domain_dir, "test_cases.json")
        
        with open(knowledge_map_path, "r") as f:
            knowledge_map = json.load(f)
        with open(test_cases_path, "r") as f:
            test_cases = json.load(f)
            
        print(f"Loaded knowledge map with {len(knowledge_map.get('knowledge_items', []))} items")
        print(f"Loaded {len(test_cases.get('test_cases', []))} test cases\n")
        
        # Create a temporary use case from the bug report
        use_case_def = UseCaseDefinition(
            name=use_case,
            description=bug_description,
            domain=domain,
            technical_level="intermediate",
            success_criteria=[
                "System should handle the reported bug scenario correctly",
                "System should prevent similar issues in the future"
            ],
            output_requirements={
                "format": "text",
                "structure": {"type": "explanation"},
                "validation_rules": ["Must handle bug scenario"],
                "examples": []
            },
            knowledge_prerequisites=[],
            example_queries=[]
        )
        
        # Generate new test cases from the bug
        print("\nGenerating new test cases from bug report...")
        new_test_cases = self.llm_service.generate_test_cases_from_bug(
            bug_description=bug_description,
            use_case=use_case,
            domain=domain,
            existing_test_cases=test_cases
        )
        
        # Add new test cases
        if new_test_cases:
            test_cases["test_cases"].extend(new_test_cases)
            with open(test_cases_path, "w") as f:
                json.dump(test_cases, f, indent=2)
            print(f"Added {len(new_test_cases)} new test cases")
        
        # Run the improvement process with the updated test cases
        print("\nRunning improvement process...")
        results = self.run_improvement_process(use_case_def)
        
        return {
            "new_test_cases": len(new_test_cases),
            "improvement_results": results
        }

    def process_use_case(self, use_case: UseCaseDefinition) -> Dict:
        """Process a use case and generate its RAG knowledge base"""
        print(f"\n{'='*80}")
        print(f"Processing use case: {use_case.name}")
        print(f"Domain: {use_case.domain}")
        print(f"{'='*80}\n")
        
        # Create domain directory if it doesn't exist
        domain_dir = f"data/knowledge_bases/{use_case.domain}"
        os.makedirs(domain_dir, exist_ok=True)
        
        # Create knowledge map
        print("Creating knowledge map...")
        knowledge_map = self.create_knowledge_map(use_case)
        
        # Create test cases
        print("\nCreating test cases...")
        test_cases = self.create_test_cases(use_case)
        
        # Run improvement process
        print("\nRunning improvement process...")
        results = self.run_improvement_process(use_case)
        
        return {
            "knowledge_map": knowledge_map,
            "test_cases": test_cases,
            "improvement_results": results
        }

    def create_knowledge_map(self, use_case: UseCaseDefinition) -> Dict:
        """Create a knowledge map for the use case"""
        print("Extracting knowledge structure using LLM...")
        knowledge_map = self.llm_service.extract_knowledge_structure(use_case.description)
        
        # Save knowledge map
        knowledge_map_path = os.path.join(f"data/knowledge_bases/{use_case.domain}", "knowledge_map.json")
        with open(knowledge_map_path, "w") as f:
            json.dump(knowledge_map, f, indent=2)
        
        return knowledge_map

    def create_test_cases(self, use_case: UseCaseDefinition) -> Dict:
        """Create test cases for the use case"""
        print("Generating comprehensive test cases using LLM...")
        test_cases = self.llm_service.generate_test_cases(use_case.description, use_case.domain)
        
        # Save test cases
        test_cases_path = os.path.join(f"data/knowledge_bases/{use_case.domain}", "test_cases.json")
        with open(test_cases_path, "w") as f:
            json.dump(test_cases, f, indent=2)
        
        return test_cases

    def run_improvement_process(self, use_case: UseCaseDefinition) -> Dict:
        """Run the improvement process for the given use case and domain."""
        print(f"\n{'='*80}")
        print(f"Starting improvement process for {use_case.domain} domain")
        print(f"Use case: {use_case.name}")
        print(f"{'='*80}\n")
        
        # Initialize paths
        domain_dir = f"data/knowledge_bases/{use_case.domain}"
        knowledge_map_path = os.path.join(domain_dir, "knowledge_map.json")
        test_cases_path = os.path.join(domain_dir, "test_cases.json")
        
        # Load knowledge map and test cases
        with open(knowledge_map_path, "r") as f:
            knowledge_map = json.load(f)
        with open(test_cases_path, "r") as f:
            test_cases = json.load(f)
        
        print(f"Loaded knowledge map with {len(knowledge_map.get('knowledge_items', []))} items")
        print(f"Loaded {len(test_cases.get('test_cases', []))} test cases\n")
        
        # Initialize results
        results = {
            "use_case": use_case.name,
            "domain": use_case.domain,
            "initial_success_rate": 0.0,
            "final_success_rate": 0.0,
            "total_cycles": 0,
            "improvements_made": 0,
            "status": "needs_improvement",
            "cycle_details": []
        }
        
        # Run improvement cycles
        for cycle in range(1, self.max_cycles + 1):
            print(f"\n{'-'*80}")
            print(f"Running improvement cycle {cycle}")
            print(f"{'-'*80}")
            
            print("\nValidating current knowledge...")
            # Get validation results from LLM
            validation_results = self.llm_service.validate_knowledge(
                use_case=use_case.description,
                domain=use_case.domain,
                knowledge_map=knowledge_map,
                test_cases=test_cases
            )
            
            # Record initial success rate
            if cycle == 1:
                results["initial_success_rate"] = validation_results["success_rate"]
                print(f"\nInitial validation success rate: {validation_results['success_rate']:.1%}")
            else:
                print(f"\nCurrent success rate: {validation_results['success_rate']:.1%}")
                
            # If validation failed, get improvement recommendations
            if validation_results["issues"]:
                print("\nIssues found:")
                for i, issue in enumerate(validation_results["issues"], 1):
                    print(f"{i}. {issue}")
                    
                print("\nAnalyzing improvements...")
                improvements = self.llm_service.analyze_improvements(
                    validation_results["issues"],
                    knowledge_map,
                    test_cases,
                    use_case.domain
                )
                
                print(f"\nImprovement plan: {improvements.get('explanation', 'No explanation provided')}")
                
                # Update knowledge map with improvements
                if improvements.get("knowledge_updates"):
                    print("\nApplying improvements:")
                    for i, update in enumerate(improvements["knowledge_updates"], 1):
                        print(f"\n{i}. {'Adding new' if update['type'] == 'add' else 'Updating'} knowledge:")
                        print(f"   {json.dumps(update['content'], indent=2)}")
                        
                        # Add new knowledge
                        if update["type"] == "add":
                            if isinstance(update["content"], dict):
                                knowledge_map["knowledge_items"].append(update["content"])
                            else:
                                # Create a new knowledge item
                                next_id = len(knowledge_map["knowledge_items"]) + 1
                                knowledge_map["knowledge_items"].append({
                                    "id": f"KI-{next_id:03d}",
                                    "type": "concept",
                                    "content": update["content"],
                                    "relationships": [],
                                    "validation_criteria": []
                                })
                        # Update existing knowledge
                        elif update["type"] == "update":
                            for item in knowledge_map["knowledge_items"]:
                                if item["id"] == update["id"]:
                                    if isinstance(update["content"], dict):
                                        item.update(update["content"])
                                    else:
                                        item["content"] = update["content"]
                                    break
                    
                    # Save updated knowledge map
                    with open(knowledge_map_path, "w") as f:
                        json.dump(knowledge_map, f, indent=2)
                        
                    results["improvements_made"] += len(improvements.get("knowledge_updates", []))
                    print(f"\nSaved {len(improvements['knowledge_updates'])} improvements to knowledge base")
            else:
                print("\nNo issues found in this cycle")
                
            # Record cycle results
            cycle_data = {
                "cycle": cycle,
                "success_rate": validation_results["success_rate"],
                "issues": validation_results["issues"]
            }
            results["cycle_details"].append(cycle_data)
            
            # Update metrics
            results["final_success_rate"] = validation_results["success_rate"]
            results["total_cycles"] = cycle
            
            # Check if we've achieved success
            if validation_results["success_rate"] >= 0.95:
                print(f"\nSuccess achieved after {cycle} cycles!")
                results["status"] = "success"
                break
                
        print(f"\n{'='*80}")
        print(f"Improvement process completed")
        print(f"Initial success rate: {results['initial_success_rate']:.1%}")
        print(f"Final success rate: {results['final_success_rate']:.1%}")
        print(f"Total improvements made: {results['improvements_made']}")
        
        return results 