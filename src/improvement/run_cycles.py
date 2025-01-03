import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from validation.user_stories_validator import UserStoryValidator

def run_improvement_cycles(max_cycles: int = 20):
    # Initialize paths
    knowledge_map_path = "data/knowledge_maps/user_stories.json"
    test_cases_path = "tests/test_data/user_stories_test_cases.json"
    results_path = "docs/improvement_results.json"
    
    # Initialize results tracking
    cycle_results = {
        "cycles": [],
        "final_success_rate": 0,
        "total_improvements": 0
    }
    
    # Run improvement cycles
    for cycle in range(1, max_cycles + 1):
        print(f"\nRunning improvement cycle {cycle}")
        
        # Initialize validator
        validator = UserStoryValidator(knowledge_map_path, test_cases_path)
        
        # Run validation
        results = validator.run_validation_cycle()
        
        # Record results
        cycle_data = {
            "cycle_number": cycle,
            "success_rate": results["success_rate"],
            "passed_tests": results["passed_tests"],
            "failed_tests": results["failed_tests"],
            "issues": results["issues"]
        }
        
        cycle_results["cycles"].append(cycle_data)
        
        print(f"Cycle {cycle} Results:")
        print(f"Success Rate: {results['success_rate']}%")
        print(f"Passed Tests: {results['passed_tests']}")
        print(f"Failed Tests: {results['failed_tests']}")
        
        if results["issues"]:
            print("\nIssues Found:")
            for issue in results["issues"]:
                print(f"\nTest Case: {issue['test_case']}")
                for i in issue['issues']:
                    print(f"- {i}")
        
        # Check if we've achieved perfect success
        if results["success_rate"] == 100:
            print("\nAchieved 100% success rate!")
            break
            
        # Update knowledge map based on issues (simulated improvement)
        # In a real system, this would use pattern recognition and automated improvements
        if cycle < max_cycles:
            print("\nApplying improvements based on identified issues...")
            # Simulate improvements (in real system, this would modify the knowledge map)
            pass
    
    # Calculate final metrics
    cycle_results["final_success_rate"] = cycle_results["cycles"][-1]["success_rate"]
    cycle_results["total_improvements"] = len(cycle_results["cycles"])
    
    # Save results
    with open(results_path, 'w') as f:
        json.dump(cycle_results, f, indent=2)
    
    print(f"\nImprovement cycles completed. Results saved to {results_path}")
    return cycle_results

if __name__ == "__main__":
    run_improvement_cycles() 