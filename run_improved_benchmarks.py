#!/usr/bin/env python3
"""
Improved Benchmark Runner - Versione migliorata che integra:
1. JSON Structure Analyzer (più preciso del parsing Prolog)
2. Advanced Benchmarks con grafici automatici
3. Compatibilità con il sistema esistente
"""

import sys
import os
import argparse
from datetime import datetime

# Import dei nuovi moduli migliorati
try:
    from json_structure_analyzer import JSONStructureAnalyzer
    from advanced_benchmarks_with_charts import AdvancedBenchmarksWithCharts
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("💡 Make sure json_structure_analyzer.py and advanced_benchmarks_with_charts.py are in the same directory")
    sys.exit(1)

def run_structure_analysis_only():
    """Esegue solo l'analisi strutturale JSON"""
    print("🔍 Running JSON-based Structure Analysis")
    print("="*60)
    
    analyzer = JSONStructureAnalyzer()
    analyzer.analyze_all_files()
    analyzer.print_summary()
    analyzer.save_analysis()
    
    print("\n✅ Structure analysis completed!")

def run_performance_benchmarks_only():
    """Esegue solo i benchmark di performance (senza analisi strutturale)"""
    print("⏱️  Running Performance Benchmarks Only")
    print("="*60)
    
    # Qui potresti importare il vecchio sistema se necessario
    # O usare una versione semplificata
    benchmarker = AdvancedBenchmarksWithCharts()
    
    # Modifica per eseguire solo performance
    print("💡 Running performance-only mode (structure analysis disabled)")
    
    for filename in benchmarker.test_files:
        print(f"\n🚀 Performance benchmark for {filename}")
        perf_result = benchmarker.run_performance_benchmark(filename)
        benchmarker.results[filename] = {'performance': perf_result}
    
    benchmarker.end_time = datetime.now()
    benchmarker.save_results()
    benchmarker.print_summary()

def run_full_analysis():
    """Esegue l'analisi completa: structure + performance + charts"""
    print("🚀 Running Full Advanced Benchmark Suite")
    print("="*60)
    print("📊 Includes: JSON structure analysis + Performance benchmarks + Charts")
    
    benchmarker = AdvancedBenchmarksWithCharts()
    benchmarker.run_all_benchmarks()
    
    print("\n✅ Full analysis completed!")

def run_single_file_analysis(filename):
    """Analizza un singolo file"""
    print(f"🎯 Running analysis for single file: {filename}")
    print("="*60)
    
    # Structure analysis
    print("1. Structure Analysis (JSON-based)")
    analyzer = JSONStructureAnalyzer()
    struct_result = analyzer.analyze_file_by_prolog_name(filename)
    
    if struct_result:
        print("✅ Structure analysis completed")
        print(f"   Objects: {struct_result.get('objects_total', 'N/A')}")
        print(f"   Actions: {struct_result.get('actions_total', 'N/A')}")
        print(f"   Pos Preconditions: {struct_result.get('positive_preconditions_total', 'N/A')}")
        print(f"   Neg Preconditions: {struct_result.get('negative_preconditions_total', 'N/A')}")
        print(f"   Wildcards: {struct_result.get('wildcards_total', 'N/A')}")
    else:
        print("❌ Structure analysis failed")
    
    # Performance analysis
    print("\n2. Performance Benchmark")
    benchmarker = AdvancedBenchmarksWithCharts()
    perf_result = benchmarker.run_performance_benchmark(filename)
    
    if perf_result.get('status') == 'completed':
        print("✅ Performance benchmark completed")
        print(f"   Total time: {perf_result.get('total_execution_time', 'N/A'):.2f}s")
        print(f"   Plan steps: {perf_result.get('plan_steps', 'N/A')}")
        print(f"   Algorithms tested: {perf_result.get('algorithms_tested', 'N/A')}")
    else:
        print(f"❌ Performance benchmark failed: {perf_result.get('status')}")
    
    print(f"\n✅ Single file analysis completed for {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Improved Benchmark Runner - JSON-based structure analysis + performance benchmarks",
        epilog="""
Examples:
  python3 run_improved_benchmarks.py                          # Full analysis (default)
  python3 run_improved_benchmarks.py --structure-only         # Only structure analysis
  python3 run_improved_benchmarks.py --performance-only       # Only performance benchmarks  
  python3 run_improved_benchmarks.py --file cucinare.pl       # Single file analysis
  python3 run_improved_benchmarks.py --compare-old            # Compare with old analyzer
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--structure-only', action='store_true',
                       help='Run only JSON-based structure analysis')
    parser.add_argument('--performance-only', action='store_true', 
                       help='Run only performance benchmarks')
    parser.add_argument('--file', type=str,
                       help='Analyze a single file (e.g., cucinare.pl)')
    parser.add_argument('--compare-old', action='store_true',
                       help='Compare new JSON analyzer with old Prolog parser')
    
    args = parser.parse_args()
    
    # Header
    print(f"\n{'='*80}")
    print(f"🔧 IMPROVED BENCHMARK RUNNER v2.0")
    print(f"{'='*80}")
    print(f"⚡ Features: JSON-based structure analysis (accurate!) + Performance + Charts")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Dispatch to appropriate function
    if args.structure_only:
        run_structure_analysis_only()
    elif args.performance_only:
        run_performance_benchmarks_only()
    elif args.file:
        run_single_file_analysis(args.file)
    elif args.compare_old:
        run_comparison_analysis()
    else:
        # Default: full analysis
        run_full_analysis()

def run_comparison_analysis():
    """Confronta il nuovo JSON analyzer con il vecchio Prolog parser"""
    print("🔍 Comparing JSON Analyzer vs Old Prolog Parser")
    print("="*60)
    
    # Nuovo JSON analyzer
    print("1. Running NEW JSON-based analyzer...")
    json_analyzer = JSONStructureAnalyzer()
    json_analyzer.analyze_all_files()
    
    # Vecchio Prolog analyzer (se disponibile)
    print("\n2. Running OLD Prolog-based analyzer...")
    try:
        from advanced_thesis_analyzer import PrologStructureAnalyzer
        old_analyzer = PrologStructureAnalyzer()
        old_analyzer.analyze_all_files()
        
        # Confronto risultati
        print("\n📊 COMPARISON RESULTS:")
        print("="*60)
        
        for filename in json_analyzer.metrics.keys():
            if filename in old_analyzer.metrics:
                json_metrics = json_analyzer.metrics[filename]
                old_metrics = old_analyzer.metrics[filename]
                
                print(f"\n📁 {filename}:")
                print(f"{'Metric':<25} {'JSON':<10} {'Prolog':<10} {'Diff':<10}")
                print("-" * 55)
                
                comparisons = [
                    ('Objects', 'objects_total', 'objects_total'),
                    ('Actions', 'actions_total', 'actions_total'),
                    ('Pos Preconditions', 'positive_preconditions_total', 'positive_preconditions_total'),
                    ('Neg Preconditions', 'negative_preconditions_total', 'negative_preconditions_total'),
                    ('Wildcards', 'wildcards_total', 'wildcards_total')
                ]
                
                for label, json_key, old_key in comparisons:
                    json_val = json_metrics.get(json_key, 0)
                    old_val = old_metrics.get(old_key, 0)
                    diff = json_val - old_val
                    diff_str = f"+{diff}" if diff > 0 else str(diff)
                    
                    print(f"{label:<25} {json_val:<10} {old_val:<10} {diff_str:<10}")
        
        print(f"\n💡 The JSON-based analyzer should be more accurate!")
        print(f"   It reads directly from converter output instead of parsing Prolog with regex.")
        
    except ImportError:
        print("⚠️  Old Prolog analyzer not found, skipping comparison")
        json_analyzer.print_summary()
    
    # Salva risultati
    json_analyzer.save_analysis("comparison_json_analysis.json")

if __name__ == "__main__":
    main()