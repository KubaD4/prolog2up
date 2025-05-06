#!/usr/bin/env python3
import subprocess
import sys
import time
import re
import argparse
import os
import json
import csv
from datetime import datetime
from prettytable import PrettyTable
import shutil
import platform
import traceback


class PlannerRunner:
    """Base class for all planner runners"""
    
    def __init__(self, domain_file, problem_file, timeout=300, verbose=False):
        self.domain_file = os.path.abspath(domain_file)
        self.problem_file = os.path.abspath(problem_file)
        self.timeout = timeout
        self.verbose = verbose
    
    def run(self, search):
        """Run the planner and return results"""
        raise NotImplementedError("Subclasses must implement run()")


class FastDownwardRunner(PlannerRunner):
    """Runner for Fast Downward planner"""
    
    def __init__(self, domain_file, problem_file, timeout=300, verbose=False, fd_path=None):
        super().__init__(domain_file, problem_file, timeout, verbose)
        self.fd_path = self._find_fd_path(fd_path)
    
    def _find_fd_path(self, fd_path):
        """Find the Fast Downward executable"""
        if fd_path and os.path.exists(fd_path):
            return fd_path
            
        # Try to find Fast Downward in common locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "downward", "fast-downward.py"),
            os.path.expanduser("~/test_pddl/downward/fast-downward.py"),
            "./downward/fast-downward.py",
            "/Users/kuba/test_pddl/downward/fast-downward.py"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Could not find fast-downward.py script")
    
    def _map_search_name(self, search):
        """Map search algorithm names to Fast Downward search strings"""
        search_algorithms = {
            "astar_ff": "astar(ff())",
            "astar_blind": "astar(blind())",
            "astar_lmcount": "astar(lmcount(lm_factory=lm_rhw()))",
            "astar_lmcut": "astar(lmcut())",
            "wastar": "eager_wastar([ff()], w=2)",
            "eager_greedy": "eager_greedy([ff()])",
            "lazy_greedy": "lazy_greedy([ff()])",
            "lazy_wastar": "lazy_wastar([ff()], w=2)"
        }
        return search_algorithms.get(search, "lazy_greedy([ff()])")
    
    def _extract_plan(self):
        """Extract plan from sas_plan file"""
        plan_lines = []
        plan_files = ['sas_plan']
        
        # Check if there are numbered plan files
        for i in range(1, 10):
            if os.path.exists(f"sas_plan.{i}"):
                plan_files.append(f"sas_plan.{i}")
        
        # Try to read from each plan file
        for plan_file in plan_files:
            if os.path.exists(plan_file):
                with open(plan_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith(";"):
                            plan_lines.append(line)
                # Break after finding the first valid plan file
                if plan_lines:
                    break
        
        return plan_lines
    
    def _extract_stats(self, output):
        """Extract statistics from Fast Downward output"""
        stats = {}
        
        # Search time
        search_time_match = re.search(r'Search time: ([\d.]+)s', output)
        if search_time_match:
            stats['search_time'] = float(search_time_match.group(1))
        
        # Total time
        total_time_match = re.search(r'Total time: ([\d.]+)s', output)
        if total_time_match:
            stats['total_time'] = float(total_time_match.group(1))
        
        # Plan length
        plan_length_match = re.search(r'Plan length: (\d+)', output)
        if plan_length_match:
            stats['plan_length'] = int(plan_length_match.group(1))
        
        # Expanded states
        expanded_match = re.search(r'Expanded (\d+) state', output)
        if expanded_match:
            stats['expanded_states'] = int(expanded_match.group(1))
        
        # Generated states
        generated_match = re.search(r'Generated (\d+) state', output)
        if generated_match:
            stats['generated_states'] = int(generated_match.group(1))
        
        # Variables
        variables_match = re.search(r'Translator variables: (\d+)', output)
        if variables_match:
            stats['variables'] = int(variables_match.group(1))
        
        # Operators
        operators_match = re.search(r'Translator operators: (\d+)', output)
        if operators_match:
            stats['operators'] = int(operators_match.group(1))
        
        return stats
    
    def _clean_up_plan_files(self):
        """Remove existing plan files"""
        for plan_file in ['sas_plan'] + [f'sas_plan.{i}' for i in range(1, 10)]:
            if os.path.exists(plan_file):
                try:
                    os.remove(plan_file)
                except Exception as e:
                    if self.verbose:
                        print(f"Could not remove old plan file {plan_file}: {e}")
    
    def run(self, search):
        """Run Fast Downward and return results"""
        # Clean up any existing plan files
        self._clean_up_plan_files()
        
        # Map search algorithm name to Fast Downward search string
        search_command = self._map_search_name(search)
        
        # Build the command
        cmd = [sys.executable, self.fd_path, self.domain_file, self.problem_file, "--search", search_command]
        
        if self.verbose:
            print(f"Running Fast Downward command: {' '.join(cmd)}")
        
        # Mark timing points
        process_start_time = time.time()
        
        try:
            # Run Fast Downward
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            process_end_time = time.time()
            
            # Get the output
            output = result.stdout + result.stderr
            
            # If verbose, print output summary
            if self.verbose:
                print(f"Fast Downward finished with return code {result.returncode}")
                output_summary = output.split('\n')
                if len(output_summary) > 20:
                    print("Output summary (first 10 lines):")
                    for line in output_summary[:10]:
                        print(f"  {line}")
                    print("  ...")
                    print("Output summary (last 10 lines):")
                    for line in output_summary[-10:]:
                        print(f"  {line}")
                else:
                    print("Complete output:")
                    print(output)
            
            # Check if solution was found - either explicit success message or sas_plan file exists
            solution_found = "Solution found" in output or os.path.exists("sas_plan")
            
            # Extract plan
            plan = self._extract_plan() if solution_found else None
            
            # Extract statistics
            stats = self._extract_stats(output)
            
            # Add process timing
            stats['process_time'] = process_end_time - process_start_time
            stats['wall_time'] = process_end_time - process_start_time
            
            # If we have a plan but no explicit success message, confirm it's valid
            if plan and not solution_found:
                solution_found = True
            
            # Determine if there was an error
            error = None
            if result.returncode != 0 and not solution_found:
                # Extract meaningful error message
                error_lines = [line for line in output.split('\n') if "error" in line.lower() or "exception" in line.lower()]
                if error_lines:
                    error = error_lines[0]
                else:
                    # Look for other common error messages
                    if "unknown option" in output.lower():
                        error = "Unknown command-line option"
                    elif "could not find domain file" in output.lower():
                        error = "Could not find domain file"
                    elif "parser error" in output.lower():
                        error = "Parser error in PDDL file"
                    else:
                        error = f"Fast Downward exited with code {result.returncode}"
            
            return {
                'planner': 'fast_downward',
                'search': search,
                'success': solution_found,
                'plan': plan,
                'stats': stats,
                'output': output,
                'returncode': result.returncode,
                'error': error
            }
        except subprocess.TimeoutExpired:
            return {
                'planner': 'fast_downward',
                'search': search,
                'success': False,
                'error': f'Timeout after {self.timeout} seconds',
                'stats': {'wall_time': self.timeout}
            }
        except Exception as e:
            return {
                'planner': 'fast_downward',
                'search': search,
                'success': False,
                'error': str(e),
                'stats': {'wall_time': time.time() - process_start_time},
                'exception': traceback.format_exc() if self.verbose else None
            }


class PyPerplanRunner(PlannerRunner):
    """Runner for PyPerplan planner"""
    
    def __init__(self, domain_file, problem_file, timeout=300, verbose=False):
        super().__init__(domain_file, problem_file, timeout, verbose)
        # Check if pyperplan is installed and available
        self._check_pyperplan()
    
    def _check_pyperplan(self):
        """Check if pyperplan is available"""
        try:
            # Check if pyperplan is in PATH
            result = subprocess.run(["which", "pyperplan"] if platform.system() != "Windows" else ["where", "pyperplan"], 
                                   capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                # Try checking if it's installed as a Python module
                try:
                    import pyperplan
                    return True
                except ImportError:
                    raise FileNotFoundError("PyPerplan is not installed or not in PATH. Install with: pip install pyperplan")
            return True
        except Exception as e:
            raise FileNotFoundError(f"Error checking for PyPerplan: {e}")
    
    def _map_search_name(self, search):
        """Map search algorithm names to PyPerplan search strings"""
        search_algorithms = {
            "astar_ff": ("astar", "ff"),
            "astar_blind": ("astar", "blind"),
            "astar_goalcount": ("astar", "goalcount"),
            "astar_hadd": ("astar", "hadd"),
            "astar_lmcount": ("astar", "landmark"),  # Corrected mapping
            "wastar": ("wastar", "ff"),
            "eager_greedy": ("gbf", "ff"),
            "lazy_greedy": ("bfs", None),  # Using BFS as fallback since PyPerplan doesn't have lazy greedy
            "bfs": ("bfs", None)
        }
        return search_algorithms.get(search, ("astar", "ff"))
    
    def _extract_plan_from_output(self, output):
        """Extract plan from PyPerplan output"""
        # First method: Find the plan after "Plan:" tag
        if "Plan:" in output:
            plan_section = output.split("Plan:")[1].strip()
            lines = plan_section.split('\n')
            plan = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("Plan length:") and not line.startswith("Tried to find"):
                    plan.append(line)
            if plan:
                return plan
        
        # Second method: Look for actions, which typically include parentheses
        action_pattern = r'\([^)]+\)'
        actions = re.findall(action_pattern, output)
        if actions:
            # If actions contain "move", they're likely actual actions 
            if any("move" in action.lower() for action in actions):
                return actions
        
        # Third method: Look for lines that start with "move-" or similar keywords
        move_actions = []
        for line in output.split('\n'):
            if line.strip().startswith(("move", "lift", "pick", "place", "stack")):
                move_actions.append(line.strip())
        if move_actions:
            return move_actions
        
        return None
    
    def _extract_stats(self, output):
        """Extract statistics from PyPerplan output"""
        stats = {}
        
        # Search time
        search_time_match = re.search(r'Search time: ([\d.]+)s', output)
        if search_time_match:
            stats['search_time'] = float(search_time_match.group(1))
        
        # Nodes expanded
        nodes_expanded_match = re.search(r'(\d+) Nodes expanded', output)
        if nodes_expanded_match:
            stats['expanded_states'] = int(nodes_expanded_match.group(1))
        
        # Plan length
        plan_length_match = re.search(r'Plan length: (\d+)', output)
        if plan_length_match:
            stats['plan_length'] = int(plan_length_match.group(1))
        
        return stats
    
    def run(self, search):
        """Run PyPerplan and return results"""
        # Map search algorithm name
        search_algo, heuristic = self._map_search_name(search)
        
        # Build the command
        cmd = ["pyperplan"]
        
        if search_algo:
            cmd.extend(["-s", search_algo])
        
        if heuristic:
            cmd.extend(["-H", heuristic])
        
        cmd.extend([self.domain_file, self.problem_file])
        
        if self.verbose:
            print(f"Running PyPerplan command: {' '.join(cmd)}")
        
        # Mark timing points
        process_start_time = time.time()
        
        try:
            # Run PyPerplan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            process_end_time = time.time()
            
            # Get the output
            output = result.stdout + result.stderr
            
            # If verbose, print output summary
            if self.verbose:
                print(f"PyPerplan finished with return code {result.returncode}")
                output_summary = output.split('\n')
                if len(output_summary) > 20:
                    print("Output summary (first 10 lines):")
                    for line in output_summary[:10]:
                        print(f"  {line}")
                    print("  ...")
                    print("Output summary (last 10 lines):")
                    for line in output_summary[-10:]:
                        print(f"  {line}")
                else:
                    print("Complete output:")
                    print(output)
            
            # Extract plan
            plan = self._extract_plan_from_output(output)
            
            # Check if solution was found - either explicit "Plan found" message or we extracted a plan
            solution_found = "Plan found" in output or plan is not None
            
            # Extract statistics
            stats = self._extract_stats(output)
            
            # Add process timing
            stats['process_time'] = process_end_time - process_start_time
            stats['wall_time'] = process_end_time - process_start_time
            
            # Determine if there was an error
            error = None
            if result.returncode != 0 and not solution_found:
                # Extract meaningful error message
                error_lines = [line for line in output.split('\n') if "error" in line.lower() or "exception" in line.lower()]
                if error_lines:
                    error = error_lines[0]
                else:
                    error = f"PyPerplan exited with code {result.returncode}"
            elif not solution_found:
                if "Problem not solvable" in output:
                    error = "Problem not solvable"
                elif "No plan found" in output:
                    error = "No plan found"
                elif not output.strip():
                    error = "No output produced - PyPerplan may not be installed correctly"
                else:
                    # Extract last few lines for clues
                    last_lines = output.strip().split('\n')[-3:]
                    error = f"Failed to find solution. Last output: {' '.join(last_lines)}"
            
            return {
                'planner': 'pyperplan',
                'search': search,
                'success': solution_found,
                'plan': plan,
                'stats': stats,
                'output': output,
                'returncode': result.returncode,
                'error': error
            }
        except subprocess.TimeoutExpired:
            return {
                'planner': 'pyperplan',
                'search': search,
                'success': False,
                'error': f'Timeout after {self.timeout} seconds',
                'stats': {'wall_time': self.timeout}
            }
        except Exception as e:
            error_msg = str(e)
            if "No such file or directory" in error_msg and "pyperplan" in error_msg:
                error_msg = "PyPerplan command not found. Make sure it's installed (pip install pyperplan) and in your PATH."
            
            return {
                'planner': 'pyperplan',
                'search': search,
                'success': False,
                'error': error_msg,
                'stats': {'wall_time': time.time() - process_start_time},
                'exception': traceback.format_exc() if self.verbose else None
            }


class PlannerComparisonTool:
    """Tool for comparing different planners and search algorithms"""
    
    def __init__(self, domain_file, problem_file, output_dir=None, timeout=300, verbose=False):
        self.domain_file = os.path.abspath(domain_file)
        self.problem_file = os.path.abspath(problem_file)
        self.timeout = timeout
        self.verbose = verbose
        
        # Setup output directory
        if output_dir:
            self.output_dir = os.path.abspath(output_dir)
        else:
            timestamp = datetime.now().strftime("%m%d_%H%M")
            problem_name = os.path.splitext(os.path.basename(problem_file))[0]
            # Create path to RESULTS/PDDL directory
            results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(domain_file))), "RESULTS", "PDDL")
            # Create subfolder with problem name and timestamp
            self.output_dir = os.path.join(results_dir, f"{problem_name}_{timestamp}")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Setup planners
        self.planners = {}
        
        # Try to initialize Fast Downward
        try:
            self.planners['fd'] = FastDownwardRunner(domain_file, problem_file, timeout, verbose)
            if verbose:
                print("Fast Downward planner initialized successfully")
        except Exception as e:
            print(f"Fast Downward planner not available: {e}")
            if verbose:
                traceback.print_exc()
        
        # Try to initialize PyPerplan
        try:
            self.planners['pyperplan'] = PyPerplanRunner(domain_file, problem_file, timeout, verbose)
            if verbose:
                print("PyPerplan planner initialized successfully")
        except Exception as e:
            print(f"PyPerplan planner not available: {e}")
            if verbose:
                traceback.print_exc()
    
    def run_comparison(self, planners=['fd'], search_algorithms=['lazy_greedy', 'astar_ff']):
        """Run the comparison with specified planners and search algorithms"""
        results = []
        
        print(f"\n===== RUNNING COMPARISON =====")
        print(f"Domain: {self.domain_file}")
        print(f"Problem: {self.problem_file}")
        print(f"Output directory: {self.output_dir}")
        print(f"Planners: {', '.join(planners)}")
        print(f"Search algorithms: {', '.join(search_algorithms)}")
        print("==============================\n")
        
        for planner_name in planners:
            if planner_name not in self.planners:
                print(f"Planner '{planner_name}' not available, skipping")
                continue
            
            planner = self.planners[planner_name]
            print(f"\nRunning planner: {planner_name}")
            
            for search in search_algorithms:
                print(f"  - Testing search algorithm: {search}")
                
                # Run the planner with the search algorithm
                start_time = time.time()
                result = planner.run(search)
                end_time = time.time()
                
                # Add total time to stats
                if 'stats' not in result:
                    result['stats'] = {}
                result['stats']['total_time'] = end_time - start_time
                
                # Save the result
                results.append(result)
                
                # Display success/failure
                if result['success']:
                    plan_length = len(result['plan']) if result['plan'] else "N/A"
                    search_time = result['stats'].get('search_time', "N/A")
                    if isinstance(search_time, float):
                        search_time = f"{search_time:.4f}s"
                    print(f"    ✓ Success (Plan length: {plan_length}, Search time: {search_time})")
                else:
                    error = result.get('error', "Unknown error")
                    print(f"    ✗ Failed: {error}")
                
                # Save plan to file
                if result['success'] and result['plan']:
                    plan_file_path = os.path.join(self.output_dir, f"{planner_name}_{search}_plan.txt")
                    with open(plan_file_path, 'w') as f:
                        for action in result['plan']:
                            f.write(f"{action}\n")
                    if self.verbose:
                        print(f"    Plan saved to: {plan_file_path}")
                
                # Save full output
                output_file_path = os.path.join(self.output_dir, f"{planner_name}_{search}_output.txt")
                with open(output_file_path, 'w') as f:
                    if 'output' in result:
                        f.write(result['output'])
                    else:
                        f.write(f"No output available. Error: {result.get('error', 'Unknown error')}")
                
                if self.verbose:
                    print(f"    Full output saved to: {output_file_path}")
        
        # Generate comparison report
        self._generate_report(results)
        
        return results
    
    def _generate_report(self, results):
        """Generate comparison report"""
        # Create results table
        table = PrettyTable()
        table.field_names = ["Planner", "Search", "Success", "Plan Length", "Search Time (s)", "Total Time (s)", "Expanded States"]
        
        # Add results to table
        for result in results:
            planner = result['planner']
            search = result['search']
            success = "Yes" if result['success'] else "No"
            
            # Get statistics
            stats = result.get('stats', {})
            plan_length = len(result['plan']) if result['success'] and result['plan'] else "N/A"
            search_time = f"{stats.get('search_time', 'N/A')}" if isinstance(stats.get('search_time'), (int, float)) else "N/A"
            total_time = f"{stats.get('total_time', 'N/A')}" if isinstance(stats.get('total_time'), (int, float)) else "N/A"
            expanded = f"{stats.get('expanded_states', 'N/A')}" if isinstance(stats.get('expanded_states'), (int, float)) else "N/A"
            
            table.add_row([planner, search, success, plan_length, search_time, total_time, expanded])
        
        # Sort by success (Yes first), then by plan length, then by search time
        table.sortby = "Success"
        table.reversesort = True
        
        # Print table
        print("\n===== COMPARISON RESULTS =====")
        print(table)
        
        # Save table to file
        report_path = os.path.join(self.output_dir, "comparison_report.txt")
        with open(report_path, 'w') as f:
            f.write(f"Planner Comparison Report\n")
            f.write(f"Domain: {self.domain_file}\n")
            f.write(f"Problem: {self.problem_file}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"System: {platform.system()} {platform.release()}\n\n")
            f.write(str(table))
        
        print(f"\nComparison report saved to: {report_path}")
        
        # Save results to CSV
        csv_path = os.path.join(self.output_dir, "comparison_results.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Planner", "Search", "Success", "Plan Length", "Search Time", "Total Time", "Expanded States", "Error"])
            
            for result in results:
                planner = result['planner']
                search = result['search']
                success = "Yes" if result['success'] else "No"
                
                # Get statistics
                stats = result.get('stats', {})
                plan_length = len(result['plan']) if result['success'] and result['plan'] else "N/A"
                search_time = stats.get('search_time', "N/A")
                total_time = stats.get('total_time', "N/A")
                expanded = stats.get('expanded_states', "N/A")
                error = result.get('error', "")
                
                writer.writerow([planner, search, success, plan_length, search_time, total_time, expanded, error])
        
        print(f"Comparison results saved to CSV: {csv_path}")
        
        # Save detailed results as JSON
        json_path = os.path.join(self.output_dir, "detailed_results.json")
        with open(json_path, 'w') as f:
            # Create a simplified version of results for JSON serialization
            json_results = []
            for result in results:
                # Create a copy without 'output' which can be large
                r = result.copy()
                if 'output' in r:
                    del r['output']
                json_results.append(r)
            
            json.dump(json_results, f, indent=2)
        
        print(f"Detailed results saved to: {json_path}")
        
        # Copy domain and problem files for reference
        shutil.copy2(self.domain_file, os.path.join(self.output_dir, os.path.basename(self.domain_file)))
        shutil.copy2(self.problem_file, os.path.join(self.output_dir, os.path.basename(self.problem_file)))
        
        print(f"Domain and problem files copied to output directory")
        
        # Write summary of best solution
        successful_results = [r for r in results if r['success']]
        if successful_results:
            # Find the shortest plan
            best_result = min(successful_results, key=lambda r: len(r['plan']) if r['plan'] else float('inf'))
            
            best_summary_path = os.path.join(self.output_dir, "best_solution_summary.txt")
            with open(best_summary_path, 'w') as f:
                f.write(f"Best Solution Summary\n")
                f.write(f"Domain: {self.domain_file}\n")
                f.write(f"Problem: {self.problem_file}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Planner: {best_result['planner']}\n")
                f.write(f"Search algorithm: {best_result['search']}\n")
                f.write(f"Plan length: {len(best_result['plan'])}\n")
                f.write(f"Search time: {best_result['stats'].get('search_time', 'N/A')} seconds\n")
                f.write(f"Total time: {best_result['stats'].get('total_time', 'N/A')} seconds\n")
                f.write(f"Expanded states: {best_result['stats'].get('expanded_states', 'N/A')}\n\n")
                f.write(f"Plan:\n")
                for i, action in enumerate(best_result['plan']):
                    f.write(f"{i+1}. {action}\n")
            
            print(f"Best solution summary saved to: {best_summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Planning Comparison Tool")
    parser.add_argument("domain", help="PDDL domain file")
    parser.add_argument("problem", help="PDDL problem file")
    parser.add_argument("--planners", nargs='+', default=["fd"], 
                        choices=["fd", "pyperplan"], 
                        help="Planners to use (default: fd)")
    parser.add_argument("--searches", nargs='+', 
                        default=["lazy_greedy", "astar_ff"], 
                        help="Search algorithms to compare")
    parser.add_argument("--timeout", type=int, default=300, 
                        help="Timeout in seconds for each planning attempt (default: 300)")
    parser.add_argument("--output-dir", help="Directory to store results")
    parser.add_argument("--verbose", action="store_true", 
                        help="Show detailed output")
    
    args = parser.parse_args()
    
    # Verify files exist
    if not os.path.exists(args.domain):
        print(f"Error: Domain file '{args.domain}' does not exist")
        return 1
    
    if not os.path.exists(args.problem):
        print(f"Error: Problem file '{args.problem}' does not exist")
        return 1
    
    try:
        # Create comparison tool
        tool = PlannerComparisonTool(
            args.domain, 
            args.problem, 
            args.output_dir, 
            args.timeout, 
            args.verbose
        )
        
        # Run comparison
        tool.run_comparison(args.planners, args.searches)
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())