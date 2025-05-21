import time
from prolog_extractor import extract_prolog_knowledge, analyze_fluent_signatures, print_knowledge_summary
from up_generator import create_up_problem, export_to_pddl, solve_problem

def main(prolog_file, pddl_output_file=None, output_dir="RESULTS/CONVERTER"):
    """Main function to convert Prolog KB to UP and then to PDDL"""
    total_start_time = time.time()
    
    # Step 1: Extract knowledge from Prolog
    knowledge = extract_prolog_knowledge(prolog_file)
    
    # Step 2: Analyze fluent signatures
    fluent_signatures = analyze_fluent_signatures(knowledge)
    
    # Step 3: Print knowledge summary
    print_knowledge_summary(knowledge, fluent_signatures)
    
    # Step 4: Create UP problem
    problem = create_up_problem(knowledge, fluent_signatures)
    
    print(f"\nUnified Planning problem details:")
    print(problem)
    
    # Step 5: Generate PDDL if output file specified
    if pddl_output_file:
        domain_path, problem_path = export_to_pddl(problem, pddl_output_file, output_dir)
    
    total_time = time.time() - total_start_time
    print(f"\nTotal conversion time: {total_time:.4f} seconds")
    
    return problem

if __name__ == "__main__":
    # Example usage
    prolog_file = "small_kb_hl.pl"  # Default file
    pddl_output = "small_blocks"    # Default output prefix
    
    # Run conversion
    problem = main(prolog_file, pddl_output)
    print("\nConversion completed successfully!")