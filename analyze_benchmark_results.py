#!/usr/bin/env python3
"""
Analizzatore Avanzato dei Risultati Benchmark
Genera grafici, tabelle comparative e analisi statistiche dei benchmark
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import argparse
import os
import glob

class BenchmarkResultsAnalyzer:
    def __init__(self, results_file=None):
        self.results_file = results_file
        self.results_data = None
        self.df = None
        
        # Configurazione stile grafici
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Carica i dati
        self.load_results()
        self.prepare_dataframe()

    def load_results(self):
        """Carica i risultati dal file JSON"""
        if self.results_file is None:
            # Cerca il file più recente
            pattern = "advanced_benchmark_results_*.json"
            files = glob.glob(pattern)
            if not files:
                raise FileNotFoundError("No benchmark results files found. Run benchmarks first.")
            self.results_file = max(files, key=os.path.getctime)
            print(f"📁 Using most recent results: {self.results_file}")
        
        with open(self.results_file, 'r') as f:
            self.results_data = json.load(f)
        
        print(f"✅ Loaded results from {self.results_file}")

    def prepare_dataframe(self):
        """Prepara DataFrame pandas per l'analisi"""
        records = []
        
        for filename, result in self.results_data['results'].items():
            if result.get('status') == 'completed':
                record = {
                    'filename': filename,
                    'file_type': self.categorize_file(filename),
                    'complexity_level': self.get_complexity_level(filename),
                    'total_execution_time': result.get('total_execution_time', 0),
                    'plan_steps': result.get('plan_steps', 0),
                    'avg_time': result.get('avg_time', 0),
                    'best_time': result.get('best_time', 0),
                    'worst_time': result.get('worst_time', 0),
                    'successful_planners': result.get('successful_planners', 0),
                    'failed_planners': result.get('failed_planners', 0),
                    'total_conversion_time': result.get('total_conversion_time', 0),
                    'planning_overhead': result.get('planning_overhead', 0)
                }
                
                # Aggiungi step times se disponibili
                if 'step_times' in result:
                    for step, time_val in result['step_times'].items():
                        record[f'step_{step}_time'] = time_val
                
                records.append(record)
        
        self.df = pd.DataFrame(records)
        print(f"📊 Prepared DataFrame with {len(self.df)} completed benchmarks")

    def categorize_file(self, filename):
        """Categorizza i file per tipo di benchmark"""
        if 'multistep_mega' in filename:
            return 'Multi-step MEGA'
        elif 'multistep_extreme' in filename:
            return 'Multi-step Extreme'
        elif 'multistep' in filename:
            return 'Multi-step'
        elif 'object_scaling_extreme' in filename:
            return 'Object Scaling Extreme'
        elif 'obj_count_scaling' in filename:
            return 'Object Scaling'
        elif 'ultimate_stress_test' in filename:
            return 'Ultimate Stress Test'
        elif 'bottleneck_3' in filename:
            return 'Complex Negatives'
        elif 'bottleneck_2' in filename:
            return 'Split Actions'
        elif 'bottleneck_1' in filename:
            return 'Coordinates'
        elif 'extended' in filename:
            return 'Extended'
        elif filename == 'cucinare.pl':
            return 'Baseline'
        else:
            return 'Other'

    def get_complexity_level(self, filename):
        """Assegna livello di complessità numerico"""
        complexity_map = {
            'cucinare.pl': 1,
            'cucinare_bottleneck_1.pl': 2,
            'cucinare_bottleneck_2.pl': 3,
            'cucinare_extended.pl': 3,
            'cucinare_bottleneck_3.pl': 4,
            'cucinare_multistep.pl': 5,
            'cucinare_obj_count_scaling.pl': 6,
            'cucinare_multistep_extreme.pl': 7,
            'cucinare_multistep_mega.pl': 8,
            'cucinare_object_scaling_extreme.pl': 9,
            'cucinare_ultimate_stress_test.pl': 10
        }
        return complexity_map.get(filename, 5)

    def create_performance_comparison_chart(self):
        """Crea grafico comparativo delle performance"""
        if self.df.empty:
            print("⚠️ No data available for performance chart")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Benchmark Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Average Planning Time vs Complexity
        ax1.scatter(self.df['complexity_level'], self.df['avg_time'], 
                   s=self.df['plan_steps']*10, alpha=0.7, c=self.df['complexity_level'], cmap='viridis')
        ax1.set_xlabel('Complexity Level')
        ax1.set_ylabel('Average Planning Time (s)')
        ax1.set_title('Planning Time vs Complexity\n(Bubble size = Plan Steps)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Plan Steps vs Execution Time
        ax2.scatter(self.df['plan_steps'], self.df['total_execution_time'], 
                   c=self.df['complexity_level'], cmap='plasma', alpha=0.7)
        ax2.set_xlabel('Plan Steps')
        ax2.set_ylabel('Total Execution Time (s)')
        ax2.set_title('Execution Time vs Plan Length')
        ax2.grid(True, alpha=0.3)
        
        # 3. Success Rate by File Type
        success_rate = self.df.groupby('file_type').agg({
            'successful_planners': 'mean',
            'failed_planners': 'mean'
        })
        success_rate['total'] = success_rate['successful_planners'] + success_rate['failed_planners']
        success_rate['success_rate'] = success_rate['successful_planners'] / success_rate['total'] * 100
        
        bars = ax3.bar(range(len(success_rate)), success_rate['success_rate'], 
                      color=plt.cm.RdYlGn(success_rate['success_rate']/100))
        ax3.set_xlabel('File Type')
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_title('Planner Success Rate by File Type')
        ax3.set_xticks(range(len(success_rate)))
        ax3.set_xticklabels(success_rate.index, rotation=45, ha='right')
        ax3.grid(True, alpha=0.3)
        
        # 4. Conversion vs Planning Time
        ax4.scatter(self.df['total_conversion_time'], self.df['avg_time'], 
                   s=60, alpha=0.7, c=self.df['complexity_level'], cmap='coolwarm')
        ax4.set_xlabel('Conversion Time (s)')
        ax4.set_ylabel('Average Planning Time (s)')
        ax4.set_title('Conversion Time vs Planning Time')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salva il grafico
        chart_filename = f"performance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        print(f"💾 Performance chart saved as: {chart_filename}")
        
        plt.show()

    def create_scaling_analysis(self):
        """Analizza il comportamento di scaling"""
        if self.df.empty:
            print("⚠️ No data available for scaling analysis")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Scaling Behavior Analysis', fontsize=16, fontweight='bold')
        
        # 1. Time Growth by Complexity
        complexity_groups = self.df.groupby('complexity_level').agg({
            'avg_time': ['mean', 'std', 'min', 'max'],
            'plan_steps': 'mean'
        }).round(3)
        
        x = complexity_groups.index
        y_mean = complexity_groups[('avg_time', 'mean')]
        y_std = complexity_groups[('avg_time', 'std')].fillna(0)
        
        ax1.errorbar(x, y_mean, yerr=y_std, marker='o', capsize=5, capthick=2)
        ax1.set_xlabel('Complexity Level')
        ax1.set_ylabel('Average Planning Time (s)')
        ax1.set_title('Time Growth with Complexity\n(Error bars = Std Dev)')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3)
        
        # 2. Step Growth Analysis
        ax2.plot(x, complexity_groups[('plan_steps', 'mean')], 'o-', linewidth=2, markersize=8)
        ax2.set_xlabel('Complexity Level')
        ax2.set_ylabel('Average Plan Steps')
        ax2.set_title('Plan Length Growth')
        ax2.grid(True, alpha=0.3)
        
        # 3. Efficiency Analysis (Time per Step)
        self.df['time_per_step'] = self.df['avg_time'] / self.df['plan_steps'].replace(0, 1)
        efficiency = self.df.groupby('complexity_level')['time_per_step'].mean()
        
        ax3.bar(efficiency.index, efficiency.values, alpha=0.7, 
               color=plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(efficiency))))
        ax3.set_xlabel('Complexity Level')
        ax3.set_ylabel('Time per Step (s/step)')
        ax3.set_title('Planning Efficiency (Lower = Better)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Variance Analysis
        variance_data = self.df.groupby('file_type').agg({
            'avg_time': 'mean',
            'best_time': 'mean', 
            'worst_time': 'mean'
        })
        variance_data['variance'] = variance_data['worst_time'] - variance_data['best_time']
        
        bars = ax4.bar(range(len(variance_data)), variance_data['variance'], alpha=0.7)
        ax4.set_xlabel('File Type')
        ax4.set_ylabel('Time Variance (Worst - Best)')
        ax4.set_title('Algorithm Variance by File Type')
        ax4.set_xticks(range(len(variance_data)))
        ax4.set_xticklabels(variance_data.index, rotation=45, ha='right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salva il grafico
        scaling_filename = f"scaling_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(scaling_filename, dpi=300, bbox_inches='tight')
        print(f"💾 Scaling analysis saved as: {scaling_filename}")
        
        plt.show()

    def generate_detailed_report(self):
        """Genera report dettagliato in formato testo"""
        if self.df.empty:
            print("⚠️ No data available for detailed report")
            return
        
        report_filename = f"benchmark_detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w') as f:
            f.write("ADVANCED BENCHMARK DETAILED REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total benchmarks completed: {len(self.df)}\n")
            f.write(f"Average planning time: {self.df['avg_time'].mean():.3f}s\n")
            f.write(f"Average plan length: {self.df['plan_steps'].mean():.1f} steps\n")
            f.write(f"Average success rate: {(self.df['successful_planners'] / (self.df['successful_planners'] + self.df['failed_planners'])).mean() * 100:.1f}%\n\n")
            
            # Performance rankings
            f.write("PERFORMANCE RANKINGS\n")
            f.write("-" * 20 + "\n")
            
            # By speed
            fastest = self.df.nsmallest(3, 'avg_time')[['filename', 'avg_time', 'plan_steps']]
            f.write("Fastest (by avg planning time):\n")
            for i, (_, row) in enumerate(fastest.iterrows(), 1):
                f.write(f"  {i}. {row['filename']}: {row['avg_time']:.3f}s ({row['plan_steps']} steps)\n")
            f.write("\n")
            
            # By plan efficiency
            self.df['efficiency'] = self.df['avg_time'] / self.df['plan_steps'].replace(0, 1)
            most_efficient = self.df.nsmallest(3, 'efficiency')[['filename', 'efficiency', 'plan_steps']]
            f.write("Most efficient (time per step):\n")
            for i, (_, row) in enumerate(most_efficient.iterrows(), 1):
                f.write(f"  {i}. {row['filename']}: {row['efficiency']:.4f}s/step ({row['plan_steps']} steps)\n")
            f.write("\n")
            
            # Scaling analysis
            f.write("SCALING ANALYSIS\n")
            f.write("-" * 15 + "\n")
            
            # Correlation analysis
            corr_steps = self.df['plan_steps'].corr(self.df['avg_time'])
            corr_complexity = self.df['complexity_level'].corr(self.df['avg_time'])
            
            f.write(f"Correlation plan_steps vs avg_time: {corr_steps:.3f}\n")
            f.write(f"Correlation complexity vs avg_time: {corr_complexity:.3f}\n\n")
            
            # Growth rates
            baseline_time = self.df[self.df['filename'] == 'cucinare.pl']['avg_time'].iloc[0] if 'cucinare.pl' in self.df['filename'].values else None
            if baseline_time:
                f.write("Growth vs baseline (cucinare.pl):\n")
                growth_data = self.df[['filename', 'avg_time']].copy()
                growth_data['growth_factor'] = growth_data['avg_time'] / baseline_time
                growth_data = growth_data.sort_values('growth_factor', ascending=False)
                
                for _, row in growth_data.head(5).iterrows():
                    if row['filename'] != 'cucinare.pl':
                        f.write(f"  {row['filename']}: {row['growth_factor']:.1f}x slower\n")
                f.write("\n")
            
            # Detailed table
            f.write("DETAILED RESULTS TABLE\n")
            f.write("-" * 22 + "\n")
            f.write(f"{'Filename':<35} {'Time':<8} {'Steps':<6} {'Success%':<8} {'Efficiency':<11}\n")
            f.write("-" * 70 + "\n")
            
            for _, row in self.df.sort_values('complexity_level').iterrows():
                success_rate = row['successful_planners'] / (row['successful_planners'] + row['failed_planners']) * 100
                efficiency = row['avg_time'] / row['plan_steps'] if row['plan_steps'] > 0 else 0
                
                f.write(f"{row['filename'][:34]:<35} {row['avg_time']:<8.3f} {row['plan_steps']:<6.0f} {success_rate:<8.1f} {efficiency:<11.4f}\n")
            
            f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 15 + "\n")
            
            max_time = self.df['avg_time'].max()
            if max_time > 10:
                f.write("⚠️  Some benchmarks take >10s - consider timeout optimizations\n")
            
            min_success = (self.df['successful_planners'] / (self.df['successful_planners'] + self.df['failed_planners'])).min() * 100
            if min_success < 50:
                f.write("⚠️  Some benchmarks have <50% success rate - investigate algorithm robustness\n")
            
            if self.df['time_per_step'].max() > self.df['time_per_step'].min() * 10:
                f.write("⚠️  Large efficiency variation detected - analyze complexity factors\n")
            
            f.write("\nEnd of report.\n")
        
        print(f"📄 Detailed report saved as: {report_filename}")

    def run_full_analysis(self):
        """Esegue l'analisi completa"""
        print("🔍 Starting comprehensive benchmark analysis...")
        
        if self.df.empty:
            print("❌ No completed benchmarks found for analysis")
            return
        
        print(f"📊 Analyzing {len(self.df)} completed benchmarks")
        
        # Genera tutti gli output
        self.create_performance_comparison_chart()
        self.create_scaling_analysis()
        self.generate_detailed_report()
        
        print("\n✅ Analysis complete! Generated:")
        print("   📈 Performance comparison charts")
        print("   📉 Scaling analysis charts") 
        print("   📄 Detailed text report")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze advanced benchmark results')
    parser.add_argument('--file', help='JSON results file to analyze (auto-detects if not specified)')
    parser.add_argument('--charts-only', action='store_true', help='Generate only charts, skip detailed report')
    parser.add_argument('--report-only', action='store_true', help='Generate only text report, skip charts')
    
    args = parser.parse_args()
    
    try:
        analyzer = BenchmarkResultsAnalyzer(args.file)
        
        if args.charts_only:
            analyzer.create_performance_comparison_chart()
            analyzer.create_scaling_analysis()
        elif args.report_only:
            analyzer.generate_detailed_report()
        else:
            analyzer.run_full_analysis()
            
    except Exception as e:
        print(f"💥 Error during analysis: {e}")
        print("Make sure you have run the benchmarks first and have the required packages installed:")
        print("pip install matplotlib pandas seaborn numpy")