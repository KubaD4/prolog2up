import sys
import os
import json
import argparse
import subprocess
import time
from datetime import datetime

# Import functions from existing modules
from prolog_extractor import extract_prolog_knowledge, analyze_fluent_signatures, print_knowledge_summary
from kb_to_json import knwoledge_to_json


def main():
    """Main orchestrator function"""
    parser = argparse.ArgumentParser(description="Convert Prolog knowledge base to Unified Planning code")
    parser.add_argument("prolog_file", help="Path to the Prolog file to convert")
    parser.add_argument("--solve", action="store_true", help="Run PDDL solver after generating files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed progress information")
    
    args = parser.parse_args()
    
    # Check if Prolog file exists
    if not os.path.exists(args.prolog_file):
        print(f"Error: Prolog file '{args.prolog_file}' not found!")
        return 1
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%m%d_%H%M")
    filename = os.path.splitext(os.path.basename(args.prolog_file))[0]
    output_dir = f"RESULTS/CONVERTER/{filename}_{timestamp}"
    
    print(f"=== Prolog to UP Conversion Pipeline ===")
    print(f"Input file: {args.prolog_file}")
    print(f"Output directory: {output_dir}")
    if args.solve:
        print("Solver: ENABLED")
    print()
    
    # Start total timing
    total_start_time = time.time()
    
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Extract knowledge from Prolog file
        print("Step 1: Extracting knowledge from Prolog file...")
        step1_start = time.time()
        knowledge = extract_prolog_knowledge(args.prolog_file)
        step1_time = time.time() - step1_start
        
        if args.verbose:
            print(f"  - Found {len(knowledge['types'])} types")
            print(f"  - Found {len(knowledge['fluent_names'])} fluents") 
            print(f"  - Found {len(knowledge['actions'])} actions")
        print(f"  ⏱️  Extraction completed in {step1_time:.3f} seconds")
        
        # Step 2: Analyze fluent signatures
        print("\nStep 2: Analyzing fluent signatures...")
        step2_start = time.time()
        fluent_signatures = analyze_fluent_signatures(knowledge)
        knowledge['fluent_signatures'] = fluent_signatures
        step2_time = time.time() - step2_start
        
        if args.verbose:
            print(f"  - Analyzed signatures for {len(fluent_signatures)} fluents")
            print("\n  === ACTION TYPE CONSTRAINTS DEBUG ===")
            for action in knowledge['actions']:
                print(f"\n  Action: {action['name']}")
                print(f"    Parameters: {action['parameters']}")
                print(f"    Param values: {action.get('param_values', [])}")
                print(f"    Type constraints: {action.get('type_constraints', [])}")
                print(f"    Type dict: {action.get('_type_constraint_dict', {})}")
            print("  === END DEBUG ===\n")
            print_knowledge_summary(knowledge, fluent_signatures)
        print(f"  ⏱️  Signature analysis completed in {step2_time:.3f} seconds")
        
        # Step 3: Convert to JSON format
        print("\nStep 3: Converting knowledge to JSON format...")
        step3_start = time.time()
        structured_knowledge = knwoledge_to_json(knowledge)
        step3_time = time.time() - step3_start
        
        # Step 4: Save JSON to file
        print("Step 4: Saving extracted knowledge to JSON...")
        step4_start = time.time()
        json_output_path = os.path.join(output_dir, "extracted_knowledge.json")
        with open(json_output_path, "w") as json_file:
            json.dump(structured_knowledge, json_file, indent=4)
        step4_time = time.time() - step4_start
        
        print(f"  - Saved to: {json_output_path}")
        print(f"  ⏱️  JSON generation completed in {step3_time + step4_time:.3f} seconds")
        
        # Step 5: Generate UP code from JSON
        print("\nStep 5: Generating Unified Planning code...")
        step5_start = time.time()
        
        # Import and execute the code generation from prolog2up_V2.py
        from prolog2up_V2 import generate_up_code
        
        # Generate the UP code with the correct output directory
        up_code = generate_up_code(structured_knowledge, output_dir)
        
        # Save the generated code
        up_output_path = os.path.join(output_dir, "generated_up.py")
        with open(up_output_path, 'w') as f:
            f.write(up_code)
        step5_time = time.time() - step5_start
        
        print(f"  - Generated UP code: {up_output_path}")
        print(f"  ⏱️  UP code generation completed in {step5_time:.3f} seconds")
        
        # Step 6: Execute the generated UP code to create PDDL files
        print("\nStep 6: Executing generated UP code to create PDDL files...")
        step6_start = time.time()
        
        # Execute the generated UP code using subprocess
        try:
            # Change working directory to output directory and run the script
            result = subprocess.run([
                sys.executable, "generated_up.py"
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
                raise Exception("UP code execution failed")
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
                raise fallback_e
            finally:
                os.chdir(original_cwd)
        
        step6_time = time.time() - step6_start
        print(f"  ⏱️  PDDL generation completed in {step6_time:.3f} seconds")
        
        # Step 7: Optional - Run PDDL solver
        if args.solve:
            print("\nStep 7: Running PDDL solver...")
            step7_start = time.time()
            
            # Check if PDDL files were generated
            domain_file = os.path.join(output_dir, "generated_domain.pddl")
            problem_file = os.path.join(output_dir, "generated_problem.pddl")
            
            if not os.path.exists(domain_file) or not os.path.exists(problem_file):
                print(f"  - Error: PDDL files not found!")
                return 1
            
            # Run the planner using simplified run_plan.py
            try:
                run_plan_script = "PDDL/run_plan.py"
                if not os.path.exists(run_plan_script):
                    print(f"  - Error: Solver script '{run_plan_script}' not found!")
                    return 1
                
                # Build command for the planner
                planner_cmd = [
                    sys.executable, run_plan_script,
                    domain_file, problem_file,
                    "--output-dir", output_dir,
                    "--planners", "fd",
                    "--searches", "lazy_greedy", "astar_ff",
                    "--timeout", "300"
                ]
                
                # Execute the planner (capture output to avoid verbose printing)
                result = subprocess.run(
                    planner_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                step7_time = time.time() - step7_start
                
                if result.returncode == 0:
                    print("  - Planning successful! Results saved to planning_results.txt")
                else:
                    print(f"  - Planning failed")
                    if args.verbose and result.stderr:
                        print(f"    Error: {result.stderr.strip()}")
                
                print(f"  ⏱️  Planning completed in {step7_time:.3f} seconds")
                
            except subprocess.TimeoutExpired:
                step7_time = time.time() - step7_start
                print(f"  -  Planner timed out after {step7_time:.1f} seconds")
            except Exception as e:
                step7_time = time.time() - step7_start
                print(f"  - Error running planner: {e}")
                print(f"  -  Planning attempt took {step7_time:.3f} seconds")
        
        total_time = time.time() - total_start_time
        
        print()
        print("=== Conversion Pipeline Completed Successfully! ===")
        print(f"- Generated files in: {output_dir}")
        print(f"  - JSON knowledge: extracted_knowledge.json")
        print(f"  - UP Python code: generated_up.py")
        print(f"  - PDDL domain: generated_domain.pddl")
        print(f"  - PDDL problem: generated_problem.pddl")
        if args.solve:
            print(f"  - Planning results: planning_results.txt")
        
        print(f"\n-  Total execution time: {total_time:.5f} seconds")
        print(f"    Step 1 (Extraction): {step1_time:.5f}s")
        print(f"    Step 2 (Signatures): {step2_time:.5f}s") 
        print(f"    Step 3-4 (JSON): {step3_time + step4_time:.5f}s")
        print(f"    Step 5 (UP Code): {step5_time:.5f}s")
        print(f"    Step 6 (PDDL): {step6_time:.5f}s")
        if args.solve:
            print(f"    Step 7 (Planning): {step7_time:.5f}s")
        
        return 0
        
    except Exception as e:
        total_time = time.time() - total_start_time
        print(f"\n-  Error during conversion pipeline: {e}")
        print(f"-   Pipeline failed after {total_time:.5f} seconds")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())