#!/usr/bin/env python3
"""
Orchestrator script for the Prolog to Unified Planning conversion pipeline.

Usage: python orchestrator.py <prolog_file>

This script coordinates the entire flow:
1. prolog_extractor.py -> extracts knowledge from Prolog file
2. kb_to_json.py -> converts knowledge to JSON format  
3. extracted_knowledge.json -> intermediate JSON file
4. prolog2up_V2.py -> generates UP code from JSON
5. generated_up.py -> final Unified Planning file
"""

import sys
import os
import json
import argparse

# Import functions from existing modules
from prolog_extractor import extract_prolog_knowledge, analyze_fluent_signatures, print_knowledge_summary
from kb_to_json import knwoledge_to_json


def main():
    """Main orchestrator function"""
    parser = argparse.ArgumentParser(description="Convert Prolog knowledge base to Unified Planning code")
    parser.add_argument("prolog_file", help="Path to the Prolog file to convert")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed progress information")
    
    args = parser.parse_args()
    
    # Check if Prolog file exists
    if not os.path.exists(args.prolog_file):
        print(f"Error: Prolog file '{args.prolog_file}' not found!")
        return 1
    
    print(f"=== Prolog to UP Conversion Pipeline ===")
    print(f"Input file: {args.prolog_file}")
    print()
    
    try:
        # Step 1: Extract knowledge from Prolog file
        print("Step 1: Extracting knowledge from Prolog file...")
        knowledge = extract_prolog_knowledge(args.prolog_file)
        
        if args.verbose:
            print(f"  - Found {len(knowledge['types'])} types")
            print(f"  - Found {len(knowledge['fluent_names'])} fluents") 
            print(f"  - Found {len(knowledge['actions'])} actions")
        
        # Step 2: Analyze fluent signatures
        print("Step 2: Analyzing fluent signatures...")
        fluent_signatures = analyze_fluent_signatures(knowledge)
        knowledge['fluent_signatures'] = fluent_signatures
        
        if args.verbose:
            print(f"  - Analyzed signatures for {len(fluent_signatures)} fluents")
            print_knowledge_summary(knowledge, fluent_signatures)
        
        # Step 3: Convert to JSON format
        print("Step 3: Converting knowledge to JSON format...")
        structured_knowledge = knwoledge_to_json(knowledge)
        
        # Step 4: Save JSON to file
        print("Step 4: Saving extracted knowledge to JSON...")
        json_output_path = "extracted_knowledge.json"
        with open(json_output_path, "w") as json_file:
            json.dump(structured_knowledge, json_file, indent=4)
        
        print(f"  - Saved to: {json_output_path}")
        
        # Step 5: Generate UP code from JSON
        print("Step 5: Generating Unified Planning code...")
        
        # Import and execute the code generation from prolog2up_V2.py
        from prolog2up_V2 import generate_up_code
        
        # Ensure the output directory exists
        output_dir = "GENERATED_BY_CONVERTED"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate the UP code
        up_code = generate_up_code(structured_knowledge, output_dir)
        
        # Save the generated code
        up_output_path = os.path.join(output_dir, "generated_up.py")
        with open(up_output_path, 'w') as f:
            f.write(up_code)
        
        print(f"  - Generated UP code: {up_output_path}")
        
        # Step 6: Execute the generated UP code to create PDDL files
        print("Step 6: Executing generated UP code to create PDDL files...")
        
        import subprocess
        import sys
        
        # Execute the generated UP code using subprocess
        try:
            result = subprocess.run([
                sys.executable, up_output_path
            ], capture_output=True, text=True, cwd=output_dir)
            
            if result.returncode == 0:
                print("  - Successfully executed generated UP code")
                if result.stdout:
                    print(f"  - Output: {result.stdout.strip()}")
            else:
                print(f"  - Error executing generated UP code:")
                if result.stderr:
                    print(f"    {result.stderr.strip()}")
                if result.stdout:
                    print(f"    {result.stdout.strip()}")
        except Exception as e:
            print(f"  - Exception while executing generated UP code: {e}")
            # Try fallback method
            print("  - Trying fallback execution method...")
            try:
                original_cwd = os.getcwd()
                os.chdir(output_dir)
                
                # Import and execute the generated code
                import importlib.util
                spec = importlib.util.spec_from_file_location("generated_up", "generated_up.py")
                generated_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(generated_module)
                
                print("  - Fallback execution successful")
            except Exception as fallback_e:
                print(f"  - Fallback execution also failed: {fallback_e}")
            finally:
                os.chdir(original_cwd)
        
        print()
        print("=== Conversion Pipeline Completed Successfully! ===")
        print(f"Generated files:")
        print(f"  - JSON knowledge: {json_output_path}")
        print(f"  - UP Python code: {up_output_path}")
        print(f"  - PDDL domain: {output_dir}/generated_domain.pddl")
        print(f"  - PDDL problem: {output_dir}/generated_problem.pddl")
        
        return 0
        
    except Exception as e:
        print(f"Error during conversion pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())