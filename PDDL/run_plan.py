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


class SimplifiedPlannerTool:
    """Simplified tool for running planners with minimal output"""
    
    def __init__(self, domain_file, problem_file, output_dir=None, timeout=300, verbose=False):
        self.domain_file = os.path.abspath(domain_file)
        self.problem_file = os.path.abspath(problem_file)
        self.timeout = timeout
        self.verbose = verbose
        self.output_dir = output_dir or os.path.dirname(problem_file)
        
        # Setup planners
        self.planners = {}
        
        # Try to initialize Fast Downward
        try:
            self.planners['fd'] = FastDownwardRunner(domain_file, problem_file, timeout, verbose)
        except Exception as e:
            if verbose:
                print(f"Fast Downward planner not available: {e}")
    
    def run_comparison(self, planners=['fd'], search_algorithms=['lazy_greedy', 'astar_ff']):
        """Run the comparison with specified planners and search algorithms"""
        results = []
        
        for planner_name in planners:
            if planner_name not in self.planners:
                continue
            
            planner = self.planners[planner_name]
            
            for search in search_algorithms:
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
        
        # Generate unified results file
        self._generate_unified_results(results)
        
        # Return success if any planner found a solution
        return any(r['success'] for r in results)
    
    def _generate_unified_results(self, results):
        """Generate a single unified results file"""
        
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
        
        # Create unified results file
        results_path = os.path.join(self.output_dir, "planning_results.txt")
        with open(results_path, 'w') as f:
            f.write(f"Planning Results\n")
            f.write(f"Domain: {self.domain_file}\n")
            f.write(f"Problem: {self.problem_file}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("===== COMPARISON RESULTS =====\n")
            f.write(str(table))
            f.write("\n\n")
            
            # Add plans section
            f.write("===== PLANS =====\n\n")
            
            for result in results:
                if result['success'] and result['plan']:
                    planner_name = result['planner']
                    search_name = result['search']
                    f.write(f"{planner_name}_{search_name} plan:\n")
                    for action in result['plan']:
                        f.write(f"{action}\n")
                    f.write("\n")
                elif not result['success']:
                    planner_name = result['planner']
                    search_name = result['search']
                    error = result.get('error', 'Unknown error')
                    f.write(f"{planner_name}_{search_name}: FAILED - {error}\n\n")
        
        return results_path


def main():
    parser = argparse.ArgumentParser(description="Simplified Planning Tool")
    parser.add_argument("domain", help="PDDL domain file")
    parser.add_argument("problem", help="PDDL problem file")
    parser.add_argument("--planners", nargs='+', default=["fd"], 
                        choices=["fd"], 
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
        # Create simplified tool
        tool = SimplifiedPlannerTool(
            args.domain, 
            args.problem, 
            args.output_dir, 
            args.timeout, 
            args.verbose
        )
        
        # Run comparison
        success = tool.run_comparison(args.planners, args.searches)
        
        if success:
            print("Planning completed successfully")
            return 0
        else:
            print("Planning failed")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())