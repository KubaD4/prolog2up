#!/usr/bin/env python3

import sys
import os
import json
import argparse
import subprocess
import time
import threading
import time as time_module
from datetime import datetime
import contextlib
from io import StringIO

from prolog_extractor import extract_prolog_knowledge, analyze_fluent_signatures, print_knowledge_summary
from kb_to_json import knwoledge_to_json

try:
    from prolog2up_V2 import generate_up_code
except ImportError as e:
    print(f"Error importing prolog2up_V2: {e}")
    sys.exit(1)


class OutputFilter:
    """Utility class to filter debug output based on detailed flag"""
    
    def __init__(self, detailed=False):
        self.detailed = detailed
        self.buffer = StringIO()
    
    def filter_output(self, output_text):
        """Filter output text based on detailed flag"""
        if self.detailed:
            return output_text
        
        lines = output_text.split('\n')
        filtered_lines = []
        
        skip_section = False
        
        for line in lines:
            # Skip debug lines
            if line.strip().startswith("DEBUG:"):
                continue
            
            # Skip sections marked with === ... ===
            if "===" in line and any(keyword in line.upper() for keyword in [
                "DETECTING", "SYNCHRONIZING", "POLYMORPHIC", "DEBUG", "ANALYSIS"
            ]):
                skip_section = True
                continue
            
            if skip_section and "=== END" in line:
                skip_section = False
                continue
            
            if skip_section:
                continue
            
            # Skip detailed fluent analysis
            if line.strip().startswith("Analyzing fluent:") or \
               line.strip().startswith("Position ") or \
               line.strip().startswith("Updated signature:") or \
               line.strip().startswith("Created new supertype:"):
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)


def capture_function_output(func, *args, detailed=False, **kwargs):
    """Capture function output and filter based on detailed flag"""
    filter_obj = OutputFilter(detailed)
    
    # Capture stdout
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        result = func(*args, **kwargs)
        output = captured_output.getvalue()
        
        # Filter output if not detailed
        if not detailed:
            filtered_output = filter_obj.filter_output(output)
            if filtered_output.strip():
                print(filtered_output, file=old_stdout)
        else:
            print(output, file=old_stdout, end='')
        
        return result
    finally:
        sys.stdout = old_stdout


def read_and_display_detailed_planning_results(output_dir, show_full_plans=False, hide_plans=False):
    """
    Read and display detailed planning results with individual planner timings
    """
    results_file = os.path.join(output_dir, "planning_results.txt")
    
    if not os.path.exists(results_file):
        print("  - No planning results file found")
        return False, {}, {}
    
    try:
        with open(results_file, 'r') as f:
            content = f.read()
        
        # Parse the results file to extract individual planner results
        individual_times = {}
        plans_found = []
        
        # Extract comparison table data
        if "===== COMPARISON RESULTS =====" in content:
            lines = content.split("\n")
            in_table = False
            
            for line in lines:
                if "===== COMPARISON RESULTS =====" in line:
                    in_table = True
                    continue
                elif "===== PLANS =====" in line:
                    in_table = False
                    break
                elif in_table and "|" in line and "Planner" not in line and "----" not in line:
                    # Parse table row
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 6:
                        planner = parts[0]
                        search = parts[1]
                        success = parts[2] == "Yes"
                        plan_length = parts[3] if parts[3] != "N/A" else None
                        search_time = parts[4] if parts[4] != "N/A" else None
                        total_time = parts[5] if parts[5] != "N/A" else None
                        
                        key = f"{planner}_{search}"
                        individual_times[key] = {
                            'success': success,
                            'search_time': search_time,
                            'total_time': total_time,
                            'plan_length': plan_length
                        }
                        
                        if success:
                            plans_found.append(key)
        
        # Extract and display plans
        if "===== PLANS =====" in content:
            plans_section = content.split("===== PLANS =====")[1]
            
            for plan_key in plans_found:
                if f"{plan_key} plan:" in plans_section:
                    plan_start = plans_section.find(f"{plan_key} plan:")
                    plan_end = plans_section.find("\n\n", plan_start)
                    if plan_end == -1:
                        plan_content = plans_section[plan_start:]
                    else:
                        plan_content = plans_section[plan_start:plan_end]
                    
                    lines = plan_content.split('\n')[1:]  # Skip the header line
                    plan_steps = [line.strip() for line in lines if line.strip()]
                    
                    if plan_steps:
                        timing = individual_times.get(plan_key, {})
                        total_time = timing.get('total_time', 'N/A')
                        print(f"    * {plan_key}:")
                        print(f"      STATUS: Plan found ({len(plan_steps)} steps)")
                        if total_time != 'N/A':
                            print(f"      TIMING: {total_time}s total")
                        
                        # Check flags for plan display mode
                        if hide_plans:
                            # Hide plans mode: show ONLY status and timing
                            pass  # Don't show any plan steps
                        elif show_full_plans:
                            # Show complete plan
                            for i, step in enumerate(plan_steps):
                                print(f"      Step {i+1:2d}: {step}")
                        else:
                            # Default mode: show only first 2 steps
                            for i, step in enumerate(plan_steps[:2]):
                                print(f"      Step {i+1:2d}: {step}")
                            if len(plan_steps) > 2:
                                print(f"      ... and {len(plan_steps)-2} more steps")
                        print()
        
        # Check for failed planners
        failed_planners = [key for key, data in individual_times.items() if not data['success']]
        if failed_planners:
            print("    * Failed planners:")
            for planner in failed_planners:
                print(f"      - {planner}: No solution found")
            print()
        
        # Calculate detailed statistics
        successful_times = []
        for key, data in individual_times.items():
            if data['success'] and data.get('total_time') and data['total_time'] != 'N/A':
                try:
                    time_val = float(data['total_time'])
                    successful_times.append(time_val)
                except (ValueError, TypeError):
                    pass
        
        timing_stats = {}
        if successful_times:
            timing_stats = {
                'avg_time': sum(successful_times) / len(successful_times),
                'best_time': min(successful_times),
                'worst_time': max(successful_times),
                'total_time': sum(successful_times)
            }
        
        return len(plans_found) > 0, individual_times, timing_stats
        
    except Exception as e:
        print(f"  - Error reading planning results: {e}")
        return False, {}, {}



def read_and_display_planning_results(output_dir):
    """
    Read and display planning results from planning_results.txt (legacy function)
    """
    results_file = os.path.join(output_dir, "planning_results.txt")
    
    if not os.path.exists(results_file):
        print("  - No planning results file found")
        return False
    
    try:
        with open(results_file, 'r') as f:
            content = f.read()
        
        # Extract plans section
        if "===== PLANS =====" in content:
            plans_section = content.split("===== PLANS =====")[1]
            
            # Parse plans
            plans_found = []
            current_plan = None
            plan_actions = []
            
            for line in plans_section.split('\n'):
                line = line.strip()
                if not line:
                    if current_plan and plan_actions:
                        plans_found.append((current_plan, plan_actions))
                        plan_actions = []
                    current_plan = None
                elif line.endswith("plan:"):
                    if current_plan and plan_actions:
                        plans_found.append((current_plan, plan_actions))
                    current_plan = line.replace(" plan:", "")
                    plan_actions = []
                elif line and current_plan:
                    plan_actions.append(line)
            
            # Add last plan if exists
            if current_plan and plan_actions:
                plans_found.append((current_plan, plan_actions))
            
            if plans_found:
                print("  - Planning results:")
                for plan_name, plan_actions in plans_found:
                    print(f"    * {plan_name}:")
                    if any("FAILED" in action for action in plan_actions):
                        for action in plan_actions:
                            if "FAILED" in action:
                                print(f"      ERROR: {action}")
                    else:
                        print(f"      STATUS: Plan found ({len(plan_actions)} steps)")
                        for i, action in enumerate(plan_actions, 1):
                            print(f"      Step {i:2d}: {action}")
                    print()
                return True
            else:
                print("  - No valid plans found in results file")
                return False
        else:
            print("  - Planning results file exists but no plans section found")
            return False
            
    except Exception as e:
        print(f"  - Error reading planning results: {e}")
        return False


def main():
    """Main orchestrator function"""
    parser = argparse.ArgumentParser(description="Convert Prolog knowledge base to Unified Planning code")
    parser.add_argument("prolog_file", help="Path to the Prolog file to convert")
    parser.add_argument("--solve", action="store_true", help="Run PDDL solver after generating files")
    parser.add_argument("--detailed", action="store_true", help="Show detailed debug information during processing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed progress information (deprecated, use --detailed)")
    
    # Plan display options (mutually exclusive)
    plan_group = parser.add_mutually_exclusive_group()
    plan_group.add_argument("--show-full-plans", action="store_true", 
                           help="Show complete plans instead of just first 2 steps")
    plan_group.add_argument("--hide-plans", action="store_true", 
                           help="Hide plan steps, show only status and timing")
    
    args = parser.parse_args()
    
    # Handle legacy --verbose flag
    if args.verbose:
        args.detailed = True
    
    # Verify Prolog file exists
    if not os.path.exists(args.prolog_file):
        print(f"Error: Prolog file '{args.prolog_file}' not found!")
        return 1
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%m%d_%H%M")
    filename = os.path.splitext(os.path.basename(args.prolog_file))[0]
    output_dir = f"RESULTS/CONVERTER/{filename}_{timestamp}"
    
    print(f"=== Prolog to Unified Planning Conversion Pipeline ===")
    print(f"Input file: {args.prolog_file}")
    print(f"Output directory: {output_dir}")
    print(f"SOLVER: {'enabled' if args.solve else 'disabled, use --solve to enable'}")
    print(f"DETAILS: {'enabled' if args.detailed else 'disabled, use --detailed to enable'}")
    
    # Show plan display mode
    if args.solve:
        if args.show_full_plans:
            plan_mode = "full plans enabled"
        elif args.hide_plans:
            plan_mode = "plans hidden (status only)"
        else:
            plan_mode = "abbreviated plans (default)"
        print(f"PLAN MODE: {plan_mode}")
    print()
    
    # Global timer
    total_start_time = time.time()
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Extract knowledge from Prolog
        print("Step 1: Extracting knowledge from Prolog file...")
        step1_start = time.time()
        knowledge = capture_function_output(extract_prolog_knowledge, args.prolog_file, detailed=args.detailed)
        step1_time = time.time() - step1_start
        
        if args.detailed:
            print(f"  - Found {len(knowledge['types'])} types")
            print(f"  - Found {len(knowledge['fluent_names'])} fluents") 
            print(f"  - Found {len(knowledge['actions'])} actions")
        print(f"  Completed in {step1_time:.3f} seconds")
        
        # Step 2: Analyze fluent signatures
        print("\nStep 2: Analyzing fluent signatures...")
        step2_start = time.time()
        fluent_signatures = capture_function_output(analyze_fluent_signatures, knowledge, detailed=args.detailed)
        knowledge['fluent_signatures'] = fluent_signatures
        step2_time = time.time() - step2_start
        
        if args.detailed:
            print(f"  - Analyzed signatures for {len(fluent_signatures)} fluents")
        print(f"  Completed in {step2_time:.3f} seconds")
        
        # Step 3: Convert to structured JSON
        print("\nStep 3: Converting knowledge to structured JSON...")
        step3_start = time.time()
        structured_knowledge = capture_function_output(knwoledge_to_json, knowledge, detailed=args.detailed)
        step3_time = time.time() - step3_start
        print(f"  Completed in {step3_time:.3f} seconds")
        
        # Step 4: Save JSON
        print("\nStep 4: Saving structured knowledge to JSON file...")
        step4_start = time.time()
        json_output_path = os.path.join(output_dir, "extracted_knowledge.json")
        with open(json_output_path, 'w') as f:
            json.dump(structured_knowledge, f, indent=2)
        step4_time = time.time() - step4_start
        
        print(f"  - Saved structured knowledge: {json_output_path}")
        print(f"  Completed in {step4_time:.3f} seconds")
        
        # Step 5: Generate UP code
        print("\nStep 5: Generating Unified Planning code...")
        step5_start = time.time()
        
        # Capture output from UP code generation
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            up_code = generate_up_code(structured_knowledge, output_dir)
            output = captured_output.getvalue()
            
            # Filter output if not detailed
            if not args.detailed:
                filter_obj = OutputFilter(args.detailed)
                filtered_output = filter_obj.filter_output(output)
                if filtered_output.strip():
                    print(filtered_output, file=old_stdout)
            else:
                print(output, file=old_stdout, end='')
        finally:
            sys.stdout = old_stdout
        
        # Save UP code
        up_output_path = os.path.join(output_dir, "generated_up.py")
        with open(up_output_path, 'w') as f:
            f.write(up_code)
        step5_time = time.time() - step5_start
        
        print(f"  - Generated UP code: {up_output_path}")
        print(f"  Completed in {step5_time:.3f} seconds")
        
        # Step 6: Execute generated UP code to create PDDL files
        print("\nStep 6: Executing generated UP code to create PDDL files...")
        
        # step6_start = time.time()
        
        # # Try normal execution
        # try:
        #     # Execute generated file
        #     result = subprocess.run([
        #         sys.executable, "generated_up.py"
        #     ], capture_output=True, text=True, cwd=output_dir)
            
        #     if result.returncode == 0:
        #         print("  - Successfully executed generated UP code")
        #         if args.detailed and result.stdout:
        #             print(f"  - Output: {result.stdout.strip()}")
        #     else:
        #         print(f"  - Error executing generated UP code:")
        #         if result.stderr:
        #             print(f"    {result.stderr.strip()}")
        #         if result.stdout:
        #             print(f"    {result.stdout.strip()}")
        #         raise Exception("UP code execution failed")
        # except Exception as e:
        #     print(f"  - Exception while executing generated UP code: {e}")
            
        #     print("  - Trying fallback execution method...")
        #     try:
        #         original_cwd = os.getcwd()
        #         os.chdir(output_dir)
                
        #         # Dynamic import and execution
        #         import importlib.util
        #         spec = importlib.util.spec_from_file_location("generated_up", "generated_up.py")
        #         generated_module = importlib.util.module_from_spec(spec)
        #         spec.loader.exec_module(generated_module)
                
        #         print("  - Fallback execution successful")
        #     except Exception as fallback_e:
        #         print(f"  - Fallback execution also failed: {fallback_e}")
        #         raise fallback_e
        #     finally:
        #         os.chdir(original_cwd)
        
        # step6_time = time.time() - step6_start
        # print(f"  Completed in {step6_time:.3f} seconds")
        print("\nStep 6: Skipping PDDL generation (commented for benchmarks)")
        step6_time = 0.0
        
        # Step 7: Planning (if requested)
        if args.solve:
            print("\nStep 7: Running PDDL solver...")
            step7_start = time.time()
            
            # Verify PDDL files exist
            domain_file = os.path.join(output_dir, "generated_domain.pddl")
            problem_file = os.path.join(output_dir, "generated_problem.pddl")
            
            if not os.path.exists(domain_file) or not os.path.exists(problem_file):
                print(f"  - Error: PDDL files not found!")
                return 1
            
            # Run planner with extended configuration
            try:
                run_plan_script = "PDDL/run_plan.py"
                if not os.path.exists(run_plan_script):
                    print(f"  - Error: Solver script '{run_plan_script}' not found!")
                    return 1
                
                # Extended list of search algorithms with smart timeouts
                search_algorithms = [
                    "lazy_greedy", "astar_ff", "astar_blind", "eager_greedy", 
                    "astar_lmcut", "wastar", "lazy_wastar", "astar_lmcount"
                ]
                
                print(f"  - Testing {len(search_algorithms)} algorithms: {', '.join(search_algorithms)}")
                print("  - Algorithms will have smart timeouts (30-90s each based on complexity)")
                print()
                
                # Planner command with smart timeout (reduced from 120 to 60 default)
                planner_cmd = [
                    sys.executable, run_plan_script,
                    domain_file, problem_file,
                    "--output-dir", output_dir,
                    "--planners", "fd",
                    "--searches"] + search_algorithms + [
                    "--timeout", "60",  # Default timeout, but algorithms use smart timeouts
                    "--verbose"  # Enable verbose output for real-time feedback
                ]
                
                # Execute command with REAL-TIME output streaming
                print(f"  - Starting planning process with real-time feedback...")
                print()
                
                # Use Popen for real-time output
                process = subprocess.Popen(
                    planner_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True
                )
                
                # Read output in real-time and display with prefix
                output_lines = []
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    # Remove trailing newline and add prefix for clarity
                    clean_line = line.rstrip()
                    if clean_line:
                        # Add prefix to distinguish planner output from orchestrator output
                        prefixed_line = f"    {clean_line}"
                        print(prefixed_line)
                        output_lines.append(clean_line)
                        sys.stdout.flush()  # Force immediate output
                
                # Wait for process to complete
                return_code = process.wait()
                
                step7_time = time.time() - step7_start
                
                print()  # Add spacing after real-time output
                
                if return_code == 0:
                    print("  - Planning successful! Results saved to planning_results.txt")
                    print("  - Planning results:")
                    # Read and display detailed results with individual timings
                    plan_found, individual_times, timing_stats = read_and_display_detailed_planning_results(output_dir, args.show_full_plans, args.hide_plans)

                    
                    # Show IMPROVED summary with timing statistics  
                    if individual_times:
                        successful_planners = [(k, v) for k, v in individual_times.items() if v['success']]
                        failed_planners = [(k, v) for k, v in individual_times.items() if not v['success']]
                        
                        print(f"  - Summary: {len(successful_planners)} successful, {len(failed_planners)} failed planners")
                        
                        if timing_stats:
                            print(f"  - Timing Analysis:")
                            print(f"    • Best time:    {timing_stats['best_time']:.4f}s")
                            print(f"    • Average time: {timing_stats['avg_time']:.4f}s") 
                            print(f"    • Worst time:   {timing_stats['worst_time']:.4f}s")
                            print(f"    • Total solver time: {timing_stats['total_time']:.4f}s")
                            print(f"    • Overhead time:     {step7_time - timing_stats['total_time']:.4f}s")
                            
                        if failed_planners:
                            print(f"  - Failed planners handled gracefully: {', '.join([k for k, v in failed_planners])}")
                else:
                    print(f"  - Planning failed with return code {return_code}")
                    
                    # Try to read partial results anyway
                    print("  - Checking for partial results...")
                    plan_found, individual_times, timing_stats = read_and_display_detailed_planning_results(output_dir, args.show_full_plans, args.hide_plans)

                    
                    if individual_times:
                        successful_count = len([k for k, v in individual_times.items() if v['success']])
                        failed_count = len(individual_times) - successful_count
                        print(f"  - Partial results: {successful_count} successful, {failed_count} failed planners")
                        
                        if timing_stats:
                            print(f"  - Total solver time: {timing_stats['total_time']:.4f}s")
                            print(f"  - Overhead time:     {step7_time - timing_stats['total_time']:.4f}s")
                
                print(f"  Completed in {step7_time:.3f} seconds")
                
            except subprocess.TimeoutExpired:
                step7_time = time.time() - step7_start
                print(f"  - Planning process timed out after {step7_time:.1f} seconds")
                print(f"  - This usually means the problem is very complex")
                print(f"  - Try reducing the number of algorithms or increasing timeout")
            except Exception as e:
                step7_time = time.time() - step7_start
                print(f"  - Error running planner: {e}")
                print(f"  - Planning attempt took {step7_time:.3f} seconds")
                if args.detailed:
                    import traceback
                    traceback.print_exc()

        
        # IMPROVED final summary with correct timing
        total_time = time.time() - total_start_time
        
        print()
        print("=== Conversion Pipeline Completed Successfully ===")
        print(f"Generated files in: {output_dir}")
        print(f"  - JSON knowledge: extracted_knowledge.json")
        print(f"  - UP Python code: generated_up.py")
        print(f"  - PDDL domain: generated_domain.pddl")
        print(f"  - PDDL problem: generated_problem.pddl")
        if args.solve:
            print(f"  - Planning results: planning_results.txt")
        
        print(f"\nTotal execution time: {total_time:.5f} seconds")
        print(f"  Step 1 (Extraction): {step1_time:.5f}s")
        print(f"  Step 2 (Signatures): {step2_time:.5f}s") 
        print(f"  Step 3-4 (JSON): {step3_time + step4_time:.5f}s")
        print(f"  Step 5 (UP Code): {step5_time:.5f}s")
        print(f"  Step 6 (PDDL): {step6_time:.5f}s")
        if args.solve:
            print(f"  Step 7 (Planning): {step7_time:.5f}s ← Total planning overhead")
            print(f"    └─ Actual solver time: varies by algorithm (see timing analysis above)")
        
        return 0
        
    except Exception as e:
        total_time = time.time() - total_start_time
        print(f"\nError during conversion pipeline: {e}")
        print(f"Pipeline failed after {total_time:.5f} seconds")
        if args.detailed:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())