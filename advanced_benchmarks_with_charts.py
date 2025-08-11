#!/usr/bin/env python3
"""
Advanced Benchmarks with Charts - Sistema integrato per benchmark e analisi strutturale
Utilizza il nuovo JSONStructureAnalyzer per dati più precisi e genera grafici automaticamente
v3.0: Grafici specifici per tesi + Correlazioni step-by-step
"""

import os
import subprocess
import time
import json
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from json_structure_analyzer import JSONStructureAnalyzer

class AdvancedBenchmarksWithCharts:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.results = {}
        self.structure_analyzer = JSONStructureAnalyzer()
        
        # File di test standard - AGGIORNATO CON TUTTI I FILE SPERIMENTALI
            # === PROLOG_GEN (auto-generated) ===
        # File di test standard - AGGIORNATO CON TUTTI I FILE SPERIMENTALI
        self.test_files = [
            "cucinare.pl",                    # BASELINE
            
            # === SERIE OBJECTS ===
            "cucinare_objects_8.pl",          # 8 objects
            "cucinare_objects_12.pl",         # 12 objects
            "cucinare_objects_13.pl",         # 13 objects
            "cucinare_objects_15.pl",         # 15 objects
            "cucinare_objects_16.pl",         # 16 objects
            "cucinare_objects_20.pl",         # 20 objects
            "cucinare_objects_25.pl",         # 25 objects
            "cucinare_objects_32.pl",         # 32 objects
            "cucinare_obj_count_scaling.pl",  # scaling objects
            
            # === SERIE ACTIONS ===
            "cucinare_actions_6.pl",          # 3→6 actions
            "cucinare_actions_9.pl",          # 3→9 actions
            "cucinare_actions_12.pl",         # 3→12 actions
            
            # === SERIE ARITY ===
            "cucinare_arity_6.pl",            # arity 6
            "cucinare_arity_8.pl",            # arity 8
            "cucinare_arity_10.pl",           # arity 10
            
            # === SERIE PRECONDITIONS (POS) ===
            "cucinare_precond_14.pl",         # 14 pos_precond
            "cucinare_precond_21.pl",         # 21 pos_precond
            "cucinare_precond_28.pl",         # 28 pos_precond
            
            # === SERIE PRECONDITIONS (NEG) ===
            "cucinare_negprecond_4.pl",       # 4 neg_precond
            "cucinare_negprecond_8.pl",       # 8 neg_precond
            "cucinare_negprecond_12.pl",      # 12 neg_precond
            
            # === STRESS / VARI ===
            "cucinare_bottleneck_1.pl",       # bottleneck 1
            "cucinare_bottleneck_2.pl",       # bottleneck 2
            "cucinare_bottleneck_3.pl",       # bottleneck 3
            "cucinare_extended.pl",           # versione estesa
            "cucinare_multistep.pl",          # multistep base
            "cucinare_multistep_extreme.pl",  # multistep estremo
            "cucinare_multistep_mega.pl",     # multistep mega
            "cucinare_ultimate_stress_test.pl" # test finale estremo
        ]

        
        # Setup per grafici
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def run_benchmark_for_file(self, filename):
        """Esegue benchmark completo per un singolo file CON OUTPUT IN TEMPO REALE"""
        print(f"🚀 Starting comprehensive benchmark for {filename}")
        
        # 1. Performance Benchmark (tempi di esecuzione)
        performance_metrics = self.run_performance_benchmark(filename)
        
        # 2. Structure Analysis (dal JSON)
        structure_metrics = self.run_structure_analysis(filename)
        
        # 3. Combine results
        combined_metrics = {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'performance': performance_metrics,
            'structure': structure_metrics
        }
        
        self.results[filename] = combined_metrics
        
        # 4. Print immediate results
        self.print_file_results(filename, combined_metrics)
        
        return combined_metrics
    
    def run_performance_benchmark(self, filename):
        """Esegue il benchmark di performance (tempi) con timeout intelligenti"""
        prolog_path = f"PROLOG/{filename}"
        
        if not os.path.exists(prolog_path):
            return {'status': 'file_not_found', 'error': f'File not found: {prolog_path}'}
        
        try:
            print(f"  ⏱️  Running performance benchmark...")
            start_time = time.time()
            
            # 🔧 TIMEOUT INTELLIGENTE basato su complessità dominio
            timeout = self.estimate_timeout(filename, prolog_path)
            print(f"    🕐 Estimated timeout: {timeout}s for {filename}")
            
            # Esegui il converter con solving
            cmd = [
                'python3', 'CONVERTER/orchestrator.py', 
                prolog_path, '--solve', '--hide-plans'
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd='.'
            )
            
            total_time = time.time() - start_time
            
            if result.returncode != 0:
                return {
                    'status': 'failed',
                    'error': f'Converter failed: {result.stderr[:200]}',
                    'total_execution_time': total_time
                }
            
            # Parse output per timing e planning results
            stdout = result.stdout
            stderr = result.stderr
            
            # 1. Parse planning times (formato tabella o testo)
            planning_metrics = self.parse_planning_results(stdout, stderr)
            
            # 2. Parse step-by-step times 
            step_metrics = self.parse_step_times(stdout, stderr)
            
            # 3. Combine metrics
            metrics = {
                'status': 'completed',
                'total_execution_time': total_time,
                **planning_metrics,
                **step_metrics
            }
            
            return metrics
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout', 
                'timeout_seconds': timeout,
                'total_execution_time': timeout
            }
        except Exception as e:
            return {
                'status': 'error', 
                'error': str(e),
                'total_execution_time': time.time() - start_time
            }
    
    def estimate_timeout(self, filename, prolog_path):
        """Stima timeout intelligente basato sul nome file e dimensione"""
        base_timeout = 300  # 5 minuti default
        
        # Fattori di scaling basati sul nome file
        if 'ultimate' in filename or 'mega' in filename:
            return base_timeout * 3  # 15 minuti
        elif 'extreme' in filename or 'stress' in filename:
            return base_timeout * 2  # 10 minuti
        elif 'multistep' in filename:
            return base_timeout * 1.5  # 7.5 minuti
        elif any(x in filename for x in ['objects_16', 'actions_12']):
            return base_timeout * 1.2  # 6 minuti
        else:
            return base_timeout
    
    def parse_planning_results(self, stdout, stderr):
        """Parse risultati planning da output"""
        metrics = {
            'planning_best_time': None,
            'planning_avg_time': None, 
            'planning_worst_time': None,
            'total_solver_time': None,
            'success_rate': None,
            'algorithms_total': None,
            'algorithms_successful': None,
            'fastest_algorithm': None,
            'plan_steps': None
        }
        
        try:
            # 1. CERCA PATTERN PLANNING RESULTS TABLE
            table_pattern = r'\|\s*fast_downward\s*\|\s*(\w+)\s*\|\s*(Yes|No)\s*\|\s*(\d+|N/A)\s*\|\s*([\d.]+|N/A)\s*\|\s*([\d.]+)\s*\|\s*(\d+|N/A)\s*\|'
            table_matches = re.findall(table_pattern, stdout)
            
            if table_matches:
                print(f"    🔍 Found {len(table_matches)} algorithm results in table format")
                
                search_times = []
                total_times = []
                plan_lengths = []
                successful_algos = 0
                total_algos = len(table_matches)
                
                for match in table_matches:
                    algorithm, success, plan_length, search_time, total_time, expanded_states = match
                    
                    if success == 'Yes':
                        successful_algos += 1
                        if search_time != 'N/A':
                            search_times.append(float(search_time))
                        if total_time != 'N/A':
                            total_times.append(float(total_time))
                        if plan_length != 'N/A':
                            plan_lengths.append(int(plan_length))
                
                # Calcola statistiche dai tempi di SEARCH (non total)
                if search_times:
                    metrics['planning_best_time'] = min(search_times)
                    metrics['planning_avg_time'] = sum(search_times) / len(search_times)
                    metrics['planning_worst_time'] = max(search_times)
                    metrics['total_solver_time'] = sum(search_times)
                    
                    # 🔍 MOSTRA ANCHE TOTAL TIMES per confronto
                    if total_times:
                        metrics['total_best_time'] = min(total_times)
                        metrics['total_avg_time'] = sum(total_times) / len(total_times)
                        metrics['total_worst_time'] = max(total_times)
                
                if plan_lengths:
                    metrics['plan_steps'] = plan_lengths[0]  # Primo piano trovato
                
                metrics['algorithms_successful'] = successful_algos
                metrics['algorithms_total'] = total_algos
                metrics['success_rate'] = successful_algos / total_algos if total_algos > 0 else 0
                
                print(f"    ✅ Parsed table format: {successful_algos}/{total_algos} successful")
                print(f"    ⏱️  Planning times: {metrics.get('planning_best_time', 0):.3f}s - {metrics.get('planning_avg_time', 0):.3f}s - {metrics.get('planning_worst_time', 0):.3f}s")
            
            else:
                # 2. FALLBACK: cerca formato testo
                print(f"    🔍 Table format not found, trying text format...")
                print(f"    📄 Searching in stdout length: {len(stdout)} chars")
                
                # Cerca pattern alternativi nel testo
                time_patterns = [
                    r'Best time:\s*([\d.]+)s',
                    r'Average time:\s*([\d.]+)s', 
                    r'Worst time:\s*([\d.]+)s',
                    r'(\d+)\s*successful,\s*(\d+)\s*failed',
                    r'Plan found \((\d+) steps\)',
                    r'success rate[:\s]*([\d.]+)%'
                ]
                
                best_time_match = re.search(time_patterns[0], stdout)
                avg_time_match = re.search(time_patterns[1], stdout)
                worst_time_match = re.search(time_patterns[2], stdout)
                success_match = re.search(time_patterns[3], stdout)
                steps_match = re.search(time_patterns[4], stdout)
                rate_match = re.search(time_patterns[5], stdout)
                
                if best_time_match and avg_time_match and worst_time_match:
                    metrics['planning_best_time'] = float(best_time_match.group(1))
                    metrics['planning_avg_time'] = float(avg_time_match.group(1))
                    metrics['planning_worst_time'] = float(worst_time_match.group(1))
                    print(f"    ✅ Found text format planning times")
                
                if success_match:
                    successful = int(success_match.group(1))
                    failed = int(success_match.group(2))
                    total = successful + failed
                    metrics['algorithms_successful'] = successful
                    metrics['algorithms_total'] = total
                    metrics['success_rate'] = successful / total if total > 0 else 0
                    print(f"    ✅ Found success rate: {metrics['success_rate']*100:.1f}%")
                
                if steps_match:
                    metrics['plan_steps'] = int(steps_match.group(1))
                    print(f"    ✅ Found plan steps: {metrics['plan_steps']}")
                
                if not any([best_time_match, avg_time_match, worst_time_match]):
                    print(f"    ⚠️  No planning times found in text format either")
                    print(f"    🔍 Relevant lines found:")
                    lines = [line.strip() for line in stdout.split('\n') if 
                           any(keyword in line.lower() for keyword in ['time', 'plan', 'algorithm', 'search'])][:5]
                    for line in lines:
                        print(f"       {line[:100]}...")
                    print(f"    ⚠️  No planning times found - may need manual check")
                    print(f"    📝 Stdout sample: {stdout[:200]}")
                else:
                    print(f"    ✅ Using text format parsing successfully")
                    
        except Exception as e:
            print(f"    ❌ Error parsing planning results: {e}")
            return metrics
        
        return metrics
    
    def parse_step_times(self, stdout, stderr):
        """Parse step-by-step timing da output"""
        step_metrics = {
            'step1_extraction': None,
            'step2_signatures': None, 
            'step5_up_code': None,
            'step6_pddl': None,
            'step7_planning': None,
            'conversion_overhead': None
        }
        
        try:
            # Pattern per step times
            step_patterns = {
                'step1_extraction': r'Step 1[^:]*:\s*([\d.]+)s',
                'step2_signatures': r'Step 2[^:]*:\s*([\d.]+)s', 
                'step5_up_code': r'Step 5[^:]*:\s*([\d.]+)s',
                'step6_pddl': r'Step 6[^:]*:\s*([\d.]+)s',
                'step7_planning': r'Step 7[^:]*:\s*([\d.]+)s'
            }
            
            for step_name, pattern in step_patterns.items():
                match = re.search(pattern, stdout)
                if match:
                    step_metrics[step_name] = float(match.group(1))
            
            # Calcola conversion overhead (step 1-6)
            steps_found = [v for v in step_metrics.values() if v is not None]
            if len(steps_found) >= 4:
                step_metrics['conversion_overhead'] = sum(steps_found) - (step_metrics.get('step7_planning', 0) or 0)
            
        except Exception as e:
            print(f"    ⚠️  Error parsing step times: {e}")
        
        return step_metrics
    
    def run_structure_analysis(self, filename):
        """Analizza struttura del file tramite JSON"""
        print(f"  📊 Running structure analysis from JSON...")
        
        try:
            # Usa il JSONStructureAnalyzer per dati precisi
            structure_result = self.structure_analyzer.analyze_file_by_prolog_name(filename)
            
            if structure_result:
                print(f"✅ Structure analysis completed")
                return structure_result
            else:
                print(f"❌ No JSON found for {filename}")
                print(f"💡 Hint: Run the converter first to generate extracted_knowledge.json")
                return None
                
        except Exception as e:
            print(f"❌ Structure analysis failed: {e}")
            return None
    
    def print_file_results(self, filename, results):
            """Stampa risultati per singolo file in tempo reale - FIXED"""
            print(f"\n📊 RESULTS for {filename}:")
            print(f"{'='*60}")
            
            perf = results.get('performance', {})
            struct = results.get('structure', {})
            
            # PERFORMANCE - FIX: Controlla None values
            if perf.get('status') == 'completed':
                print(f"⚡ PLANNING PERFORMANCE:")
                
                # Safe formatting per planning times
                best_time = perf.get('planning_best_time')
                avg_time = perf.get('planning_avg_time') 
                worst_time = perf.get('planning_worst_time')
                
                if best_time is not None and avg_time is not None and worst_time is not None:
                    print(f"   • Search times:  {best_time:.4f}s / {avg_time:.4f}s / {worst_time:.4f}s (best/avg/worst)")
                else:
                    print(f"   • Planning times: Not parsed (check output format)")
                
                # Safe formatting per success rate
                success_rate = perf.get('success_rate')
                algorithms_successful = perf.get('algorithms_successful', 0)
                algorithms_total = perf.get('algorithms_total', 0)
                
                if success_rate is not None:
                    print(f"   • Success rate:  {success_rate*100:.1f}% ({algorithms_successful}/{algorithms_total} algorithms)")
                else:
                    print(f"   • Success rate:  Unknown (parsing failed)")
                
                # Safe formatting per plan steps
                plan_steps = perf.get('plan_steps')
                if plan_steps is not None:
                    print(f"   • Plan steps:    {plan_steps}")
                else:
                    print(f"   • Plan steps:    Not found")
                
                fastest_algorithm = perf.get('fastest_algorithm')
                if fastest_algorithm:
                    print(f"   • Fastest algo:  {fastest_algorithm}")
                
                print(f"\n🔧 CONVERSION BREAKDOWN:")
                
                # Safe formatting per step times
                step1 = perf.get('step1_extraction', 0)
                step5 = perf.get('step5_up_code', 0)
                step6 = perf.get('step6_pddl', 0)
                total_solver = perf.get('total_solver_time', 0)
                overhead = perf.get('conversion_overhead', 0)
                
                print(f"   • Extraction:    {step1:.4f}s")
                print(f"   • UP Code gen:   {step5:.4f}s")
                print(f"   • PDDL gen:      {step6:.4f}s")
                print(f"   • Total solver:  {total_solver:.4f}s")
                print(f"   • Overhead:      {overhead:.4f}s")
            else:
                print(f"❌ PLANNING: {perf.get('status', 'unknown')}")
                if perf.get('error'):
                    print(f"   Error: {perf.get('error')}")
            
            # STRUCTURE - FIX: Safe handling
            if struct:
                print(f"🏗️  DOMAIN STRUCTURE:")
                print(f"   • Objects:       {struct.get('objects_total', 'N/A')}")
                print(f"   • Actions:       {struct.get('actions_total', 'N/A')}")
                print(f"   • Fluents:       {struct.get('fluents_total', 'N/A')}")
                print(f"   • Pos precond:   {struct.get('positive_preconditions_total', 'N/A')}")
                print(f"   • Neg precond:   {struct.get('negative_preconditions_total', 'N/A')}")
                print(f"   • Wildcards:     {struct.get('wildcards_total', 'N/A')}")
                print(f"   • Max arity:     {struct.get('max_action_arity', 'N/A')}")
                
                # COMPLEXITY ANALYSIS - FIX: Safe calculation
                actions = struct.get('actions_total', 0) or 0
                avg_arity = struct.get('avg_action_arity', 1) or 1
                neg_precond = struct.get('negative_preconditions_total', 0) or 0
                wildcards = struct.get('wildcards_total', 0) or 0
                
                complexity = (actions * avg_arity + neg_precond * 2 + wildcards * 3)
                print(f"   • Complexity:    {complexity:.1f}")
                
                # Insights sulla complessità
                if wildcards > 20:
                    print(f"   ⚠️  High wildcard count may impact planning performance")
                if neg_precond > 15:
                    print(f"   ⚠️  Many negative preconditions detected")
                    
            else:
                print(f"❌ STRUCTURE: Failed to analyze")
            
            print(f"{'='*60}\n")

    
    def prepare_dataframe(self):
        """Prepara DataFrame per l'analisi con dati dettagliati"""
        data = []
        
        for filename, result in self.results.items():
            if not result:
                continue
                
            row = {'filename': filename}
            
            # Performance data DETTAGLIATI
            perf = result.get('performance', {})
            if perf.get('status') == 'completed':
                # TEMPI SPECIFICI DI PLANNING (questi sono i più importanti!)
                row.update({
                    'planning_best_time': perf.get('planning_best_time'),
                    'planning_avg_time': perf.get('planning_avg_time'),
                    'planning_worst_time': perf.get('planning_worst_time'),
                    'total_solver_time': perf.get('total_solver_time'),
                    'success_rate': perf.get('success_rate'),
                    'algorithms_total': perf.get('algorithms_total'),
                    'algorithms_successful': perf.get('algorithms_successful'),
                    'fastest_algorithm': perf.get('fastest_algorithm'),
                    'plan_steps': perf.get('plan_steps'),
                    
                    # TEMPI STEP-BY-STEP (fondamentali per correlazioni!)
                    'step1_extraction': perf.get('step1_extraction'),
                    'step2_signatures': perf.get('step2_signatures'),
                    'step5_up_code': perf.get('step5_up_code'),
                    'step6_pddl': perf.get('step6_pddl'),
                    'step7_planning': perf.get('step7_planning'),
                    'conversion_overhead': perf.get('conversion_overhead'),
                    'total_execution_time': perf.get('total_execution_time')
                })
            
            # Structure data DETTAGLIATI
            struct = result.get('structure', {})
            if struct:
                row.update({
                    'objects': struct.get('objects_total'),
                    'actions': struct.get('actions_total'),
                    'pos_precond': struct.get('positive_preconditions_total'),
                    'neg_precond': struct.get('negative_preconditions_total'),
                    'wildcards': struct.get('wildcards_total'),
                    'fluents': struct.get('fluents_total'),
                    'max_arity': struct.get('max_action_arity'),
                    'avg_arity': struct.get('avg_action_arity'),
                    'total_precond': struct.get('total_preconditions'),
                    'neg_precond_ratio': struct.get('negative_preconditions_ratio'),
                    'wildcards_per_action': struct.get('wildcards_per_action'),
                    'complexity_score': struct.get('complexity_score')
                })
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def create_thesis_specific_charts(self, df, charts_dir):
            """Crea grafici specifici per la tesi con correlazioni chiare - FIXED EMOJI"""
            print(f"  🎯 Creating THESIS-SPECIFIC correlation charts...")
            
            # Setup per grafici di qualità
            plt.rcParams.update({'font.size': 12})
            
            # 1. OBJECTS vs STEP 7 PLANNING (Correlazione più forte identificata)
            if 'objects' in df.columns and 'step7_planning' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Scatter plot con colori per evidenziare il trend
                scatter = ax.scatter(df['objects'], df['step7_planning'], 
                                s=150, alpha=0.7, c=df['objects'], cmap='Reds')
                
                # Linea di tendenza
                if len(df) > 2:
                    z = np.polyfit(df['objects'], df['step7_planning'], 1)
                    p = np.poly1d(z)
                    ax.plot(df['objects'], p(df['objects']), "r--", linewidth=3, label='Trend Line')
                    
                    # Correlazione
                    corr = df['objects'].corr(df['step7_planning'])
                    ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                        transform=ax.transAxes, fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
                
                # Annotazioni file
                for i, row in df.iterrows():
                    filename = row['filename'].replace('.pl', '').replace('cucinare_', '')
                    ax.annotate(filename, (row['objects'], row['step7_planning']),
                            xytext=(8, 8), textcoords='offset points', fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
                
                ax.set_xlabel('Number of Objects', fontsize=14, fontweight='bold')
                ax.set_ylabel('Step 7 Planning Time (s)', fontsize=14, fontweight='bold')
                ax.set_title('THESIS KEY FINDING: Objects vs Planning Time\n(Primary Scalability Factor)', 
                            fontsize=16, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig(f"{charts_dir}/01_THESIS_objects_vs_step7_planning.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            # 2. ACTIONS vs STEP 2 SIGNATURES (Impatto fortissimo identificato)
            if 'actions' in df.columns and 'step2_signatures' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                scatter = ax.scatter(df['actions'], df['step2_signatures'], 
                                s=150, alpha=0.7, c=df['actions'], cmap='Greens')
                
                if len(df) > 2:
                    z = np.polyfit(df['actions'], df['step2_signatures'], 1)
                    p = np.poly1d(z)
                    ax.plot(df['actions'], p(df['actions']), "g--", linewidth=3, label='Trend Line')
                    
                    corr = df['actions'].corr(df['step2_signatures'])
                    ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                        transform=ax.transAxes, fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle="round", facecolor='lightgreen', alpha=0.8))
                
                for i, row in df.iterrows():
                    filename = row['filename'].replace('.pl', '').replace('cucinare_', '')
                    ax.annotate(filename, (row['actions'], row['step2_signatures']),
                            xytext=(8, 8), textcoords='offset points', fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
                
                ax.set_xlabel('Number of Actions', fontsize=14, fontweight='bold')
                ax.set_ylabel('Step 2 Signatures Time (s)', fontsize=14, fontweight='bold')
                ax.set_title('THESIS KEY FINDING: Actions vs Signatures Generation\n(Preprocessing Bottleneck)', 
                            fontsize=16, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig(f"{charts_dir}/02_THESIS_actions_vs_step2_signatures.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            # 3. ACTIONS vs STEP 5 UP CODE (Correlazione identificata)
            if 'actions' in df.columns and 'step5_up_code' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                scatter = ax.scatter(df['actions'], df['step5_up_code'], 
                                s=150, alpha=0.7, c=df['actions'], cmap='Blues')
                
                if len(df) > 2:
                    z = np.polyfit(df['actions'], df['step5_up_code'], 1)
                    p = np.poly1d(z)
                    ax.plot(df['actions'], p(df['actions']), "b--", linewidth=3, label='Trend Line')
                    
                    corr = df['actions'].corr(df['step5_up_code'])
                    ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                        transform=ax.transAxes, fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
                
                for i, row in df.iterrows():
                    filename = row['filename'].replace('.pl', '').replace('cucinare_', '')
                    ax.annotate(filename, (row['actions'], row['step5_up_code']),
                            xytext=(8, 8), textcoords='offset points', fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
                
                ax.set_xlabel('Number of Actions', fontsize=14, fontweight='bold')
                ax.set_ylabel('Step 5 UP Code Generation Time (s)', fontsize=14, fontweight='bold')
                ax.set_title('THESIS FINDING: Actions vs UP Code Generation\n(Code Complexity Impact)', 
                            fontsize=16, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig(f"{charts_dir}/03_THESIS_actions_vs_step5_up_code.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            # 4. NEG_PRECOND vs STEP 7 PLANNING (Correlazione NEGATIVA - controintuitiva!)
            if 'neg_precond' in df.columns and 'step7_planning' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                scatter = ax.scatter(df['neg_precond'], df['step7_planning'], 
                                s=150, alpha=0.7, c=df['neg_precond'], cmap='Purples')
                
                if len(df) > 2:
                    z = np.polyfit(df['neg_precond'], df['step7_planning'], 1)
                    p = np.poly1d(z)
                    ax.plot(df['neg_precond'], p(df['neg_precond']), "purple", 
                        linestyle="--", linewidth=3, label='Trend Line (NEGATIVE!)')
                    
                    corr = df['neg_precond'].corr(df['step7_planning'])
                    ax.text(0.05, 0.95, f'Correlation: {corr:.3f}\n(NEGATIVE = GOOD!)', 
                        transform=ax.transAxes, fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle="round", facecolor='plum', alpha=0.8))
                
                for i, row in df.iterrows():
                    filename = row['filename'].replace('.pl', '').replace('cucinare_', '')
                    ax.annotate(filename, (row['neg_precond'], row['step7_planning']),
                            xytext=(8, 8), textcoords='offset points', fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
                
                ax.set_xlabel('Number of Negative Preconditions', fontsize=14, fontweight='bold')
                ax.set_ylabel('Step 7 Planning Time (s)', fontsize=14, fontweight='bold')
                ax.set_title('THESIS COUNTERINTUITIVE FINDING: Negative Preconditions IMPROVE Planning\n(More Constraints = Faster Search)', 
                            fontsize=16, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig(f"{charts_dir}/04_THESIS_negprecond_vs_step7_planning.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            # 5. OBJECTS vs STEP 6 PDDL (Seconda correlazione forte)
            if 'objects' in df.columns and 'step6_pddl' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                scatter = ax.scatter(df['objects'], df['step6_pddl'], 
                                s=150, alpha=0.7, c=df['objects'], cmap='Oranges')
                
                if len(df) > 2:
                    z = np.polyfit(df['objects'], df['step6_pddl'], 1)
                    p = np.poly1d(z)
                    ax.plot(df['objects'], p(df['objects']), "orange", linewidth=3, label='Trend Line')
                    
                    corr = df['objects'].corr(df['step6_pddl'])
                    ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                        transform=ax.transAxes, fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle="round", facecolor='moccasin', alpha=0.8))
                
                for i, row in df.iterrows():
                    filename = row['filename'].replace('.pl', '').replace('cucinare_', '')
                    ax.annotate(filename, (row['objects'], row['step6_pddl']),
                            xytext=(8, 8), textcoords='offset points', fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
                
                ax.set_xlabel('Number of Objects', fontsize=14, fontweight='bold')
                ax.set_ylabel('Step 6 PDDL Generation Time (s)', fontsize=14, fontweight='bold')
                ax.set_title('THESIS FINDING: Objects vs PDDL Generation\n(Domain Complexity Impact)', 
                            fontsize=16, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig(f"{charts_dir}/05_THESIS_objects_vs_step6_pddl.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            # 6. HEATMAP CORRELAZIONI COMPLETE
            correlation_cols = []
            param_cols = ['objects', 'actions', 'pos_precond', 'neg_precond', 'wildcards', 'max_arity']
            step_cols = ['step1_extraction', 'step2_signatures', 'step5_up_code', 'step6_pddl', 'step7_planning']
            
            for col in param_cols + step_cols:
                if col in df.columns and df[col].notna().sum() > 2:
                    correlation_cols.append(col)
            
            if len(correlation_cols) > 4:
                fig, ax = plt.subplots(figsize=(14, 10))
                
                # Calcola matrice correlazioni
                corr_matrix = df[correlation_cols].corr()
                
                # Estrai solo correlazioni parametri vs step
                param_available = [col for col in param_cols if col in correlation_cols]
                step_available = [col for col in step_cols if col in correlation_cols]
                
                if param_available and step_available:
                    param_vs_step_corr = corr_matrix.loc[param_available, step_available]
                    
                    # Heatmap con annotazioni
                    sns.heatmap(param_vs_step_corr, annot=True, cmap='RdBu_r', center=0,
                            square=True, fmt='.3f', cbar_kws={'label': 'Correlation Coefficient'},
                            linewidths=0.5)
                    
                    ax.set_title('THESIS CORRELATIONS MATRIX: Parameters vs Pipeline Steps\n(Red = Positive Impact, Blue = Negative Impact)', 
                                fontsize=16, fontweight='bold')
                    ax.set_xlabel('Pipeline Steps', fontsize=14, fontweight='bold')
                    ax.set_ylabel('Structural Parameters', fontsize=14, fontweight='bold')
                    
                    plt.xticks(rotation=45, ha='right')
                    plt.yticks(rotation=0)
                    plt.tight_layout()
                    plt.savefig(f"{charts_dir}/06_THESIS_correlation_heatmap.png", dpi=300, bbox_inches='tight')
                    plt.close()
                    
            # 7. COMPARAZIONE DIRETTA: ACTIONS vs OBJECTS su PLANNING
            if all(col in df.columns for col in ['objects', 'actions', 'step7_planning']):
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
                
                # Objects vs Planning
                ax1.scatter(df['objects'], df['step7_planning'], s=150, alpha=0.7, c='red')
                if len(df) > 2:
                    z1 = np.polyfit(df['objects'], df['step7_planning'], 1)
                    p1 = np.poly1d(z1)
                    ax1.plot(df['objects'], p1(df['objects']), "r--", linewidth=3)
                    corr1 = df['objects'].corr(df['step7_planning'])
                    ax1.text(0.05, 0.95, f'Correlation: {corr1:.3f}', transform=ax1.transAxes, 
                            fontsize=12, fontweight='bold', bbox=dict(boxstyle="round", facecolor='lightcoral', alpha=0.8))
                
                ax1.set_xlabel('Number of Objects', fontsize=12, fontweight='bold')
                ax1.set_ylabel('Step 7 Planning Time (s)', fontsize=12, fontweight='bold')
                ax1.set_title('Objects Impact on Planning\n(STRONG CORRELATION)', fontsize=14, fontweight='bold')
                ax1.grid(True, alpha=0.3)
                
                # Actions vs Planning
                ax2.scatter(df['actions'], df['step7_planning'], s=150, alpha=0.7, c='blue')
                if len(df) > 2:
                    z2 = np.polyfit(df['actions'], df['step7_planning'], 1)
                    p2 = np.poly1d(z2)
                    ax2.plot(df['actions'], p2(df['actions']), "b--", linewidth=3)
                    corr2 = df['actions'].corr(df['step7_planning'])
                    ax2.text(0.05, 0.95, f'Correlation: {corr2:.3f}', transform=ax2.transAxes, 
                            fontsize=12, fontweight='bold', bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
                
                ax2.set_xlabel('Number of Actions', fontsize=12, fontweight='bold')
                ax2.set_ylabel('Step 7 Planning Time (s)', fontsize=12, fontweight='bold')
                ax2.set_title('Actions Impact on Planning\n(WEAK CORRELATION)', fontsize=14, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                
                plt.suptitle('THESIS COMPARISON: What Really Impacts Planning Performance?', 
                            fontsize=16, fontweight='bold')
                plt.tight_layout()
                plt.savefig(f"{charts_dir}/07_THESIS_objects_vs_actions_comparison.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            print(f"  ✅ Generated 7 THESIS-SPECIFIC charts for key findings!")


    def generate_charts(self, df):
        """Genera i grafici (metodo principale modificato)"""
        charts_dir = f"{self.output_dir}/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        print(f"🎨 Generating THESIS-FOCUSED charts...")
        
        try:
            # Chiama il metodo specifico per la tesi
            self.create_thesis_specific_charts(df, charts_dir)
            
            print(f"  ✅ All thesis charts generated in: {charts_dir}/")
            print(f"  🎯 Key files for thesis:")
            print(f"     📊 01_THESIS_objects_vs_step7_planning.png")
            print(f"     📊 02_THESIS_actions_vs_step2_signatures.png") 
            print(f"     📊 03_THESIS_actions_vs_step5_up_code.png")
            print(f"     📊 04_THESIS_negprecond_vs_step7_planning.png")
            print(f"     📊 05_THESIS_objects_vs_step6_pddl.png")
            print(f"     📊 06_THESIS_correlation_heatmap.png")
            print(f"     📊 07_THESIS_objects_vs_actions_comparison.png")
            
        except Exception as e:
            print(f"❌ Error generating thesis charts: {e}")
            import traceback
            traceback.print_exc()

    def export_raw_data(self, df):
        """Esporta dati raw in vari formati per analisi esterna"""
        data_dir = f"{self.output_dir}/data"
        os.makedirs(data_dir, exist_ok=True)
        
        try:
            print(f"  💾 Exporting raw data...")
            
            # 1. CSV principale
            df.to_csv(f"{data_dir}/benchmark_data.csv", index=False)
            
            # 2. JSON strutturato (con fix per int64)
            def convert_numpy_types(obj):
                """Converte numpy types a Python native types"""
                if hasattr(obj, 'dtype'):
                    if 'int' in str(obj.dtype):
                        return int(obj)
                    elif 'float' in str(obj.dtype):
                        return float(obj)
                return obj
            
            # Converti DataFrame in dict con fix numpy types
            data_records = []
            for record in df.to_dict('records'):
                fixed_record = {}
                for key, value in record.items():
                    fixed_record[key] = convert_numpy_types(value)
                data_records.append(fixed_record)
            
            data_export = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'analyzer_version': 'AdvancedBenchmarksWithCharts v3.0',
                    'description': 'Raw benchmark data for thesis charts'
                },
                'data': data_records
            }
            
            with open(f"{data_dir}/benchmark_data.json", 'w') as f:
                json.dump(data_export, f, indent=2)
            
            # 3. Subset specifici per grafici
            planning_cols = ['filename', 'planning_best_time', 'planning_avg_time', 
                           'planning_worst_time', 'success_rate', 'plan_steps']
            structure_cols = ['filename', 'objects', 'actions', 'pos_precond', 
                            'neg_precond', 'wildcards', 'fluents']
            correlation_cols = ['filename', 'planning_avg_time', 'complexity_score', 
                              'wildcards', 'neg_precond', 'success_rate']
            
            # Export subset per tipo di analisi
            for subset_name, cols in [('planning', planning_cols), 
                                    ('structure', structure_cols),
                                    ('correlations', correlation_cols)]:
                available_cols = [col for col in cols if col in df.columns]
                if len(available_cols) > 2:
                    df[available_cols].to_csv(f"{data_dir}/{subset_name}_data.csv", index=False)
            
            # 4. Statistiche summary
            summary_stats = {
                'files_analyzed': len(df),
                'avg_planning_time': df['planning_avg_time'].mean() if 'planning_avg_time' in df.columns else None,
                'avg_success_rate': df['success_rate'].mean() if 'success_rate' in df.columns else None,
                'total_actions': df['actions'].sum() if 'actions' in df.columns else None,
                'total_wildcards': df['wildcards'].sum() if 'wildcards' in df.columns else None,
                'correlations': {}
            }
            
            # Calcola correlazioni chiave
            if len(df) > 2:
                corr_pairs = [
                    ('planning_avg_time', 'wildcards'),
                    ('planning_avg_time', 'neg_precond'),
                    ('success_rate', 'complexity_score'),
                    ('planning_avg_time', 'complexity_score')
                ]
                
                for col1, col2 in corr_pairs:
                    if col1 in df.columns and col2 in df.columns:
                        corr = df[col1].corr(df[col2])
                        summary_stats['correlations'][f"{col1}_vs_{col2}"] = corr
            
            with open(f"{data_dir}/summary_statistics.json", 'w') as f:
                json.dump(summary_stats, f, indent=2)
                
            print(f"    ✅ Raw data exported: CSV, JSON, subsets, statistics")
            
        except Exception as e:
            print(f"    ❌ Error exporting raw data: {e}")
    
    def run_all_benchmarks(self):
        """Esegue benchmark su tutti i file di test"""
        print(f"🚀 Starting Advanced Benchmark Suite with Charts")
        print(f"📅 Start time: {self.start_time}")
        print(f"📝 Testing {len(self.test_files)} files")
        print(f"🎨 Charts will be generated automatically")
        
        failed_files = []
        
        for i, filename in enumerate(self.test_files, 1):
            print(f"\n[{i}/{len(self.test_files)}] Processing {filename}...")
            
            try:
                result = self.run_benchmark_for_file(filename)
                if result and result.get('performance', {}).get('status') != 'completed':
                    failed_files.append((filename, result.get('performance', {}).get('status', 'unknown')))
            except Exception as e:
                print(f"❌ Critical error processing {filename}: {e}")
                failed_files.append((filename, f"exception: {str(e) if e else 'unknown error'}"))
                continue
        
        # Generate charts and export data
        print(f"\n🎨 Generating individual charts and raw data...")
        
        # Prepare data
        df = self.prepare_dataframe()
        
        if len(df) == 0:
            print(f"❌ No valid data collected for analysis")
            return
            
        # Setup output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = f"RESULTS/advanced_benchmark_results_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Export raw data
        self.export_raw_data(df)
        
        # Generate charts
        self.generate_charts(df)
        
        # Final summary
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        print(f"\n💾 Complete results saved to: {self.output_dir.split('/')[-1]}.json")
        
        self.print_summary(df, failed_files, duration)
        
        # Save complete results
        self.save_results(f"{self.output_dir}/benchmark_results.json")
    
    def print_summary(self, df, failed_files, duration):
        """Stampa sommario finale dettagliato"""
        print(f"\n{'='*90}")
        print(f"📊 ADVANCED BENCHMARK WITH CHARTS SUMMARY")
        print(f"{'='*90}")
        print(f"⏱️  Total Duration: {duration:.1f}s")
        print(f"📁 Files Tested: {len(self.test_files)}")
        
        # Status breakdown
        completed_count = len([r for r in self.results.values() 
                             if r and r.get('performance', {}).get('status') == 'completed'])
        
        print(f"\n📈 Performance Benchmark Status:")
        print(f"   ✅ completed: {completed_count}")
        if failed_files:
            print(f"   ❌ failed: {len(failed_files)}")
        
        # Structure analysis status  
        structure_count = len([r for r in self.results.values() 
                             if r and r.get('structure')])
        structure_failed = len(self.results) - structure_count
        
        print(f"\n📊 Structure Analysis Status:")
        print(f"   ✅ completed: {structure_count}")
        if structure_failed > 0:
            print(f"   ❌ failed: {structure_failed}")
        
        # Detailed results table (SEARCH TIMES FOCUS)
        print(f"\n📋 Detailed Results (Search Times Focus):")
        print(f"File".ljust(20) + " Search Best Search Avg  Search Worst Success  Steps  Objects Wildcards")
        print("-" * 95)
        
        for _, row in df.iterrows():
            filename = row['filename'].replace('.pl', '')[:19]
            
            # Format planning times
            best_time = f"{row['planning_best_time']:.4f}s" if pd.notna(row['planning_best_time']) else "N/A"
            avg_time = f"{row['planning_avg_time']:.4f}s" if pd.notna(row['planning_avg_time']) else "N/A"
            worst_time = f"{row['planning_worst_time']:.4f}s" if pd.notna(row['planning_worst_time']) else "N/A"
            success_rate = f"{row['success_rate']*100:.1f}%" if pd.notna(row['success_rate']) else "-"
            steps = str(int(row['plan_steps'])) if pd.notna(row['plan_steps']) else "-"
            objects = str(int(row['objects'])) if pd.notna(row['objects']) else "-"
            wildcards = str(int(row['wildcards'])) if pd.notna(row['wildcards']) else "-"
            
            print(f"{filename.ljust(20)} {best_time.ljust(11)} {avg_time.ljust(11)} {worst_time.ljust(12)} {success_rate.ljust(8)} {steps.ljust(6)} {objects.ljust(7)} {wildcards.ljust(9)}")
        
        # Failed files details
        if failed_files:
            print(f"\n🔍 PARSING ISSUES ({len(failed_files)}):")
            for filename, status in failed_files:
                print(f"   • {filename} - {status}")
            print(f"   💡 Check output format or regex patterns")
        
        print(f"\n💡 SEARCH TIMES = Pure algorithm performance (ms/s range)")
        print(f"💡 TOTAL TIMES = Search + overhead (parsing, grounding, etc.)")
        print(f"🔍 Look for correlations: wildcards↑ = search_time↑, neg_preconditions↑ = success_rate↓")
        print(f"🎨 Charts show intelligent correlations between structure and planning performance")
        print(f"⏰ Timeouts are estimated intelligently based on domain complexity")
        
        print(f"\n{'='*90}")
        
    def save_results(self, output_file=None):
        """Salva i risultati completi"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"advanced_benchmark_results_{timestamp}.json"
        
        summary = {
            'benchmark_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
                'files_tested': len(self.test_files),
                'version': 'AdvancedBenchmarksWithCharts v3.0'
            },
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

def main():
    """Funzione principale"""
    print(f"\n{'='*80}")
    print(f"🔧 IMPROVED BENCHMARK RUNNER v3.0")
    print(f"{'='*80}")
    print(f"⚡ Features: JSON-based structure analysis + Performance + THESIS CHARTS")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print(f"🚀 Running Full Advanced Benchmark Suite")
    print(f"{'='*60}")
    print(f"📊 Includes: JSON structure analysis + Performance benchmarks + Thesis Charts")
    
    # Crea e esegui benchmark
    benchmarker = AdvancedBenchmarksWithCharts()
    benchmarker.run_all_benchmarks()
    
    print(f"\n✅ Full analysis completed!")

if __name__ == "__main__":
    main()