#!/usr/bin/env python3
"""
Advanced Benchmark Suite per il Converter Prolog→PDDL
Esegue i nuovi benchmark estremi e raccoglie metriche dettagliate
"""

import subprocess
import time
import json
import re
import os
from datetime import datetime

class AdvancedBenchmarkSuite:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
        # File da testare in ordine di difficoltà crescente
        self.test_files = [
            # Baseline per confronto
            "cucinare.pl",
            "cucinare_multistep.pl", 
            "cucinare_obj_count_scaling.pl",
            
            # Nuovi benchmark estremi
            "cucinare_multistep_extreme.pl",
            "cucinare_multistep_mega.pl",
            "cucinare_object_scaling_extreme.pl", 
            "cucinare_ultimate_stress_test.pl"
        ]
        
        # Timeout per file (in secondi)
        self.timeouts = {
            "cucinare.pl": 60,
            "cucinare_multistep.pl": 120,
            "cucinare_obj_count_scaling.pl": 300,
            "cucinare_multistep_extreme.pl": 300,
            "cucinare_multistep_mega.pl": 600,
            "cucinare_object_scaling_extreme.pl": 900,
            "cucinare_ultimate_stress_test.pl": 1200  # 20 minuti max
        }

    def run_single_benchmark(self, filename):
        """Esegue un singolo benchmark e raccoglie le metriche"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {filename}")
        print(f"⏰ Timeout: {self.timeouts.get(filename, 300)}s")
        print(f"{'='*60}")
        
        start_time = time.time()
        timeout = self.timeouts.get(filename, 300)
        
        # Comando da eseguire
        cmd = [
            "python3", 
            "CONVERTER/orchestrator.py", 
            f"PROLOG/{filename}",
            "--solve", 
            "--hide-plans"
        ]
        
        try:
            # Esegui con timeout
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd="."
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Parsing dell'output
            metrics = self.parse_output(result.stdout, result.stderr, execution_time)
            metrics['status'] = 'completed'
            metrics['return_code'] = result.returncode
            
            if result.returncode != 0:
                metrics['status'] = 'failed'
                print(f"❌ FAILED with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")
            else:
                print(f"✅ SUCCESS in {execution_time:.2f}s")
                
        except subprocess.TimeoutExpired:
            execution_time = timeout
            metrics = {
                'status': 'timeout',
                'execution_time': execution_time,
                'timeout_limit': timeout
            }
            print(f"⏰ TIMEOUT after {timeout}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            metrics = {
                'status': 'error',
                'execution_time': execution_time,
                'error': str(e)
            }
            print(f"💥 ERROR: {e}")
        
        # Aggiungi metadati
        metrics['filename'] = filename
        metrics['timestamp'] = datetime.now().isoformat()
        metrics['total_execution_time'] = execution_time
        
        self.results[filename] = metrics
        return metrics

    def parse_output(self, stdout, stderr, execution_time):
        """Estrae metriche dall'output del converter"""
        metrics = {}
        
        # Regex patterns per estrarre informazioni
        patterns = {
            'plan_steps': r'Plan found \((\d+) steps\)',
            'best_time': r'Best time:\s+([\d.]+)s',
            'avg_time': r'Average time:\s+([\d.]+)s', 
            'worst_time': r'Worst time:\s+([\d.]+)s',
            'successful_planners': r'(\d+) successful, (\d+) failed planners',
            'total_solver_time': r'Total solver time:\s+([\d.]+)s',
            'step_times': {
                'extraction': r'Step 1 \(Extraction\):\s+([\d.]+)s',
                'signatures': r'Step 2 \(Signatures\):\s+([\d.]+)s', 
                'json': r'Step 3-4 \(JSON\):\s+([\d.]+)s',
                'up_code': r'Step 5 \(UP Code\):\s+([\d.]+)s',
                'pddl': r'Step 6 \(PDDL\):\s+([\d.]+)s',
                'planning': r'Step 7 \(Planning\):\s+([\d.]+)s'
            }
        }
        
        # Estrai plan steps
        plan_match = re.search(patterns['plan_steps'], stdout)
        if plan_match:
            metrics['plan_steps'] = int(plan_match.group(1))
        
        # Estrai timing planning
        for key, pattern in patterns.items():
            if key == 'step_times':
                continue
            if key == 'successful_planners':
                match = re.search(pattern, stdout)
                if match:
                    metrics['successful_planners'] = int(match.group(1))
                    metrics['failed_planners'] = int(match.group(2))
                continue
                
            match = re.search(pattern, stdout)
            if match:
                metrics[key] = float(match.group(1))
        
        # Estrai step times
        step_times = {}
        for step, pattern in patterns['step_times'].items():
            match = re.search(pattern, stdout)
            if match:
                step_times[step] = float(match.group(1))
        
        if step_times:
            metrics['step_times'] = step_times
            metrics['total_conversion_time'] = sum(step_times.values())
        
        # Calcola overhead
        if 'total_solver_time' in metrics and 'total_conversion_time' in metrics:
            metrics['planning_overhead'] = metrics['total_solver_time'] - metrics.get('total_conversion_time', 0)
        
        return metrics

    def run_all_benchmarks(self):
        """Esegue tutti i benchmark nella sequenza"""
        print(f"🚀 Starting Advanced Benchmark Suite")
        print(f"📅 Start time: {self.start_time}")
        print(f"📝 Testing {len(self.test_files)} files")
        
        for i, filename in enumerate(self.test_files, 1):
            print(f"\n[{i}/{len(self.test_files)}] Processing {filename}...")
            
            # Controlla se il file esiste
            if not os.path.exists(f"PROLOG/{filename}"):
                print(f"⚠️  SKIP: File PROLOG/{filename} not found")
                self.results[filename] = {
                    'status': 'file_not_found',
                    'filename': filename,
                    'timestamp': datetime.now().isoformat()
                }
                continue
            
            try:
                self.run_single_benchmark(filename)
            except KeyboardInterrupt:
                print(f"\n🛑 Benchmark interrupted by user")
                self.results[filename] = {
                    'status': 'interrupted',
                    'filename': filename, 
                    'timestamp': datetime.now().isoformat()
                }
                break
            except Exception as e:
                print(f"💥 Unexpected error testing {filename}: {e}")
                self.results[filename] = {
                    'status': 'unexpected_error',
                    'error': str(e),
                    'filename': filename,
                    'timestamp': datetime.now().isoformat()
                }
        
        # Finalizza
        self.end_time = datetime.now()
        self.save_results()
        self.print_summary()

    def save_results(self):
        """Salva i risultati in formato JSON"""
        output_file = f"advanced_benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = {
            'benchmark_info': {
                'suite': 'Advanced Benchmark Suite',
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'total_duration': (self.end_time - self.start_time).total_seconds(),
                'files_tested': len(self.test_files)
            },
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

    def print_summary(self):
        """Stampa un riassunto dei risultati"""
        print(f"\n{'='*80}")
        print(f"📊 ADVANCED BENCHMARK SUMMARY")
        print(f"{'='*80}")
        
        print(f"⏱️  Total Duration: {(self.end_time - self.start_time).total_seconds():.1f}s")
        print(f"📁 Files Tested: {len(self.test_files)}")
        
        # Conta status
        status_counts = {}
        for result in self.results.values():
            status = result.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 Status Summary:")
        for status, count in status_counts.items():
            emoji = {'completed': '✅', 'timeout': '⏰', 'failed': '❌', 'error': '💥', 'file_not_found': '📂'}.get(status, '❓')
            print(f"   {emoji} {status}: {count}")
        
        # Tabella risultati
        print(f"\n📋 Detailed Results:")
        print(f"{'File':<35} {'Status':<12} {'Time':<8} {'Steps':<6} {'Avg Plan':<10}")
        print(f"{'-'*75}")
        
        for filename, result in self.results.items():
            status = result.get('status', 'unknown')[:11]
            time_str = f"{result.get('total_execution_time', 0):.1f}s"[:7]
            steps = str(result.get('plan_steps', '-'))[:5]
            avg_plan = f"{result.get('avg_time', 0):.3f}s"[:9] if result.get('avg_time') else '-'
            
            print(f"{filename[:34]:<35} {status:<12} {time_str:<8} {steps:<6} {avg_plan:<10}")
        
        # Performance analysis
        completed_results = [(f, r) for f, r in self.results.items() if r.get('status') == 'completed']
        
        if completed_results:
            print(f"\n🎯 Performance Analysis:")
            
            # Ordina per tempo di esecuzione
            completed_results.sort(key=lambda x: x[1].get('avg_time', float('inf')))
            
            print(f"   🏆 Fastest: {completed_results[0][0]} ({completed_results[0][1].get('avg_time', 0):.3f}s avg)")
            print(f"   🐌 Slowest: {completed_results[-1][0]} ({completed_results[-1][1].get('avg_time', 0):.3f}s avg)")
            
            # Media dei tempi
            avg_times = [r.get('avg_time', 0) for _, r in completed_results if r.get('avg_time')]
            if avg_times:
                print(f"   📊 Average planning time across all: {sum(avg_times)/len(avg_times):.3f}s")
            
            # Plan steps analysis
            steps = [r.get('plan_steps', 0) for _, r in completed_results if r.get('plan_steps')]
            if steps:
                print(f"   📏 Plan steps range: {min(steps)}-{max(steps)} (avg: {sum(steps)/len(steps):.1f})")

        print(f"\n{'='*80}")

if __name__ == "__main__":
    suite = AdvancedBenchmarkSuite()
    
    try:
        suite.run_all_benchmarks()
    except KeyboardInterrupt:
        print(f"\n🛑 Benchmark suite interrupted by user")
        suite.end_time = datetime.now()
        suite.save_results()
        suite.print_summary()
    except Exception as e:
        print(f"\n💥 Fatal error in benchmark suite: {e}")
        suite.end_time = datetime.now()
        suite.save_results()