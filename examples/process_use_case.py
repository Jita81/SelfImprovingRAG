from src.orchestration.rag_orchestrator import RAGOrchestrator

def main():
    # Initialize orchestrator
    orchestrator = RAGOrchestrator()
    
    # Define epic breakdown use case
    use_case = """Break down epics into well-defined features that can be implemented by development teams.
    An epic should be decomposed into features that:
    - Are independently valuable and deliverable
    - Have clear scope and boundaries
    - Can be estimated and prioritized
    - Support the epic's overall goals
    - Consider technical dependencies
    - Account for non-functional requirements
    """
    
    domain = "epic_breakdown"
    
    print(f"\nProcessing {domain} use case")
    results = orchestrator.process_use_case(use_case, domain)
    print(f"\nResults Summary:")
    print(f"Initial success rate: {results['initial_success_rate']:.1%}")
    print(f"Final success rate: {results['final_success_rate']:.1%}")
    print(f"Total improvements made: {results['improvements_made']}")

if __name__ == "__main__":
    main() 