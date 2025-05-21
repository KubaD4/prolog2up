import argparse
import os
from prolog2up import main
from prolog_extractor import extract_prolog_knowledge, analyze_fluent_signatures, print_knowledge_summary

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Convert Prolog knowledge base to PDDL using Unified Planning.")
    parser.add_argument("filename", help="Name of the Prolog file")
    parser.add_argument("--extract-only", action="store_true", 
                        help="Only extract Prolog knowledge without generating UP or PDDL")
    parser.add_argument("--solve", action="store_true", help="Try to solve the problem after conversion")
    parser.add_argument("--output-dir", default="RESULTS/CONVERTER", 
                       help="Directory to store output files (default: RESULTS/CONVERTER)")
    return parser.parse_args()

def extract_and_print_prolog(prolog_file):
    """Extract knowledge from Prolog file and print it"""
    print(f"\n=== EXTRACTING KNOWLEDGE FROM {prolog_file} ===\n")
    
    # Extract knowledge
    knowledge = extract_prolog_knowledge(prolog_file)
    
    # Analyze fluent signatures
    fluent_signatures = analyze_fluent_signatures(knowledge)
    
    # Print summary
    print_knowledge_summary(knowledge, fluent_signatures)
    
    return knowledge, fluent_signatures

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Make sure the Prolog file exists
    prolog_file = f"PROLOG/{args.filename}"
    if not os.path.exists(prolog_file):
        print(f"Error: File {prolog_file} not found")
        exit(1)

    if args.extract_only:
        # Only extract and print Prolog knowledge
        extract_and_print_prolog(prolog_file)
    else:
        # Full conversion process
        # Output file prefix for PDDL files
        pddl_output = f"converter_result_{args.filename.split('.')[0]}"
        
        print(f"Converting {prolog_file} to PDDL...")
        print(f"Output will be stored in {args.output_dir} with prefix {pddl_output}")
        
        # Execute the conversion
        problem = main(prolog_file, pddl_output)
        
        # If solve flag is set, try to solve the problem
        if args.solve and problem:
            from up_generator import solve_problem
            solve_problem(problem)