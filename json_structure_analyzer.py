#!/usr/bin/env python3
"""
JSON Structure Analyzer - Legge metriche strutturali direttamente dal JSON del converter
Molto più preciso e affidabile del parsing Prolog con regex
"""

import os
import json
import glob
from collections import defaultdict, Counter
from datetime import datetime

class JSONStructureAnalyzer:
    def __init__(self):
        self.metrics = {}
        self.knowledge_cache = {}
        
    def find_json_file(self, prolog_filename):
        """Trova il file JSON corrispondente al file Prolog"""
        # Rimuovi estensione .pl
        base_name = os.path.splitext(prolog_filename)[0]
        
        # Pattern di ricerca per trovare il JSON
        patterns = [
            f"extracted_knowledge.json",  # Nome standard
            f"{base_name}_knowledge.json",
            f"RESULTS/CONVERTER/{base_name}_*/extracted_knowledge.json",
            f"CONVERTER/extracted_knowledge.json"
        ]
        
        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                # Prendi il più recente se ce ne sono più di uno
                return max(matches, key=os.path.getmtime)
        
        return None
    
    def load_knowledge_json(self, json_path):
        """Carica il JSON della knowledge base"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
            print(f"✅ Loaded knowledge from: {json_path}")
            return knowledge
        except Exception as e:
            print(f"❌ Error loading {json_path}: {e}")
            return None
    
    def analyze_from_json(self, json_path, prolog_filename=None):
        """Analizza la struttura dal JSON invece che dal Prolog"""
        knowledge = self.load_knowledge_json(json_path)
        if not knowledge:
            return None
        
        filename = prolog_filename or os.path.basename(json_path)
        
        print(f"🔍 Analyzing structure from JSON for {filename}")
        
        metrics = {
            'filename': filename,
            'json_source': json_path,
            'analysis_method': 'JSON_based',
            'timestamp': datetime.now().isoformat()
        }
        
        # Analisi strutturale dal JSON
        metrics.update(self.analyze_objects_from_json(knowledge))
        metrics.update(self.analyze_actions_from_json(knowledge))
        metrics.update(self.analyze_states_from_json(knowledge))
        metrics.update(self.analyze_fluents_from_json(knowledge))
        
        self.metrics[filename] = metrics
        self.knowledge_cache[filename] = knowledge
        return metrics
    
    def analyze_objects_from_json(self, knowledge):
        """Analizza oggetti dai tipi nel JSON"""
        metrics = {}
        
        types = knowledge.get('types', {})
        objects_by_type = knowledge.get('objects_by_type', {})
        
        # BUGFIX: Se objects_by_type è vuoto, prova a contare da altri posti
        total_objects = 0
        type_distribution = {}
        
        # Metodo principale: objects_by_type
        for obj_type, obj_list in objects_by_type.items():
            count = len(obj_list)
            total_objects += count
            type_distribution[obj_type] = count
        
        # FALLBACK: Se non trova oggetti, conta da init_state e azioni
        if total_objects == 0:
            print("⚠️  WARNING: objects_by_type is empty, counting from other sources...")
            object_names = set()
            
            # Conta oggetti dall'init_state
            for pred in knowledge.get('init_state', []):
                for arg in pred.get('args', []):
                    if not arg.startswith('Param') and not arg.startswith('_'):
                        object_names.add(arg)
            
            # Conta oggetti dalle azioni (parametri non-Param)
            for action in knowledge.get('actions', []):
                for param in action.get('parameters', []):
                    if not param.startswith('Param'):
                        object_names.add(param)
            
            total_objects = len(object_names)
            print(f"   Found {total_objects} objects from fallback method")
        
        metrics.update({
            'objects_total': total_objects,
            'object_types_count': len(types),
            'objects_by_type': type_distribution,
            'types_defined': list(types.keys()),
            'max_objects_per_type': max(type_distribution.values()) if type_distribution else 0,
            'avg_objects_per_type': total_objects / len(types) if types else 0
        })
        
        return metrics
    
    def analyze_actions_from_json(self, knowledge):
        """Analizza azioni dal JSON - QUESTA È LA PARTE IMPORTANTE!"""
        metrics = {}
        
        actions = knowledge.get('actions', [])
        
        # Contatori totali
        total_actions = len(actions)
        total_positive_precond = 0
        total_negative_precond = 0
        total_wildcards = 0
        total_add_effects = 0
        total_del_effects = 0
        
        # Statistiche dettagliate
        action_arities = []
        precond_stats = []
        wildcard_stats = []
        
        for action in actions:
            # Parametri azione
            params = action.get('parameters', [])
            action_arities.append(len(params))
            
            # PRECONDIZIONI POSITIVE - Direttamente dal JSON!
            pos_precond = action.get('preconditions', [])
            pos_count = len(pos_precond)
            total_positive_precond += pos_count
            
            # PRECONDIZIONI NEGATIVE - Direttamente dal JSON!
            neg_precond = action.get('neg_preconditions', [])
            neg_count = len(neg_precond)
            total_negative_precond += neg_count
            
            # WILDCARDS - Già identificati nel JSON!
            wildcards_in_action = 0
            for neg_pred in neg_precond:
                wildcard_positions = neg_pred.get('wildcard_positions', [])
                wildcards_in_action += len(wildcard_positions)
            total_wildcards += wildcards_in_action
            
            # EFFETTI
            add_effects = action.get('add_effects', [])
            del_effects = action.get('del_effects', [])
            total_add_effects += len(add_effects)
            total_del_effects += len(del_effects)
            
            # Statistiche per azione
            precond_stats.append({
                'action': action.get('name', 'unknown'),
                'positive': pos_count,
                'negative': neg_count,
                'wildcards': wildcards_in_action,
                'add_effects': len(add_effects),
                'del_effects': len(del_effects)
            })
        
        # Calcola metriche aggregate
        metrics.update({
            'actions_total': total_actions,
            'positive_preconditions_total': total_positive_precond,
            'negative_preconditions_total': total_negative_precond,
            'wildcards_total': total_wildcards,
            'add_effects_total': total_add_effects,
            'del_effects_total': total_del_effects,
            
            # Statistiche per azione
            'max_action_arity': max(action_arities) if action_arities else 0,
            'avg_action_arity': sum(action_arities) / len(action_arities) if action_arities else 0,
            
            # Medie
            'avg_positive_precond_per_action': total_positive_precond / total_actions if total_actions else 0,
            'avg_negative_precond_per_action': total_negative_precond / total_actions if total_actions else 0,
            'avg_wildcards_per_action': total_wildcards / total_actions if total_actions else 0,
            'avg_effects_per_action': (total_add_effects + total_del_effects) / total_actions if total_actions else 0,
            
            # Ratio
            'negative_to_positive_ratio': total_negative_precond / total_positive_precond if total_positive_precond else 0,
            'effects_to_precond_ratio': (total_add_effects + total_del_effects) / (total_positive_precond + total_negative_precond) if (total_positive_precond + total_negative_precond) else 0,
            
            # Dettagli per azione
            'action_breakdown': precond_stats
        })
        
        return metrics
    
    def analyze_states_from_json(self, knowledge):
        """Analizza stati iniziali e goal dal JSON"""
        metrics = {}
        
        init_state = knowledge.get('init_state', [])
        goal_state = knowledge.get('goal_state', [])
        
        metrics.update({
            'init_state_predicates': len(init_state),
            'goal_state_predicates': len(goal_state),
            'state_complexity': len(init_state) + len(goal_state)
        })
        
        return metrics
    
    def analyze_fluents_from_json(self, knowledge):
        """Analizza fluenti e loro signature dal JSON"""
        metrics = {}
        
        fluent_signatures = knowledge.get('fluent_signatures', {})
        fluent_names = knowledge.get('fluent_names', [])
        
        # Analisi arità fluenti
        fluent_arities = []
        for fluent_name, signature in fluent_signatures.items():
            fluent_arities.append(len(signature))
        
        metrics.update({
            'fluents_total': len(fluent_names),
            'fluent_signatures_count': len(fluent_signatures),
            'max_fluent_arity': max(fluent_arities) if fluent_arities else 0,
            'avg_fluent_arity': sum(fluent_arities) / len(fluent_arities) if fluent_arities else 0,
            'fluent_names': fluent_names
        })
        
        return metrics
    
    def analyze_file_by_prolog_name(self, prolog_filename):
        """Analizza cercando automaticamente il JSON corrispondente"""
        json_path = self.find_json_file(prolog_filename)
        
        if not json_path:
            print(f"❌ No JSON found for {prolog_filename}")
            print("💡 Hint: Run the converter first to generate extracted_knowledge.json")
            return None
        
        return self.analyze_from_json(json_path, prolog_filename)
    
    def analyze_all_files(self, prolog_directory="PROLOG"):
        """Analizza tutti i file Prolog trovando i JSON corrispondenti"""
        print(f"🔍 Analyzing all Prolog files in {prolog_directory}/ using JSON data")
        
        prolog_files = []
        if os.path.exists(prolog_directory):
            for filename in os.listdir(prolog_directory):
                if filename.endswith('.pl'):
                    prolog_files.append(filename)
        
        if not prolog_files:
            print(f"❌ No .pl files found in {prolog_directory}/")
            return
        
        print(f"📁 Found {len(prolog_files)} Prolog files")
        
        successful_analyses = 0
        for filename in sorted(prolog_files):
            print(f"\n--- Processing {filename} ---")
            result = self.analyze_file_by_prolog_name(filename)
            if result:
                successful_analyses += 1
            else:
                print(f"⚠️  Skipped {filename} (no JSON found)")
        
        print(f"\n✅ Analysis complete: {successful_analyses}/{len(prolog_files)} files successfully analyzed")
    
    def save_analysis(self, output_file=None):
        """Salva l'analisi in un file JSON"""
        if output_file is None:
            output_file = f"json_structure_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        analysis_data = {
            'analysis_info': {
                'analyzer': 'JSONStructureAnalyzer',
                'version': '2.0',
                'method': 'JSON-based (more accurate than Prolog parsing)',
                'timestamp': datetime.now().isoformat(),
                'files_analyzed': len(self.metrics)
            },
            'file_metrics': self.metrics
        }
        
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"💾 JSON Structure analysis saved to: {output_file}")
        return output_file
    
    def print_summary(self):
        """Stampa un riassunto dell'analisi con dati precisi dal JSON"""
        if not self.metrics:
            print("❌ No analysis data available")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 JSON-BASED STRUCTURE ANALYSIS SUMMARY")
        print(f"{'='*80}")
        print(f"🎯 Method: JSON parsing (more accurate than Prolog regex)")
        print(f"📁 Files analyzed: {len(self.metrics)}")
        
        # Statistiche aggregate
        total_objects = sum(m.get('objects_total', 0) for m in self.metrics.values())
        total_actions = sum(m.get('actions_total', 0) for m in self.metrics.values())
        total_pos_precond = sum(m.get('positive_preconditions_total', 0) for m in self.metrics.values())
        total_neg_precond = sum(m.get('negative_preconditions_total', 0) for m in self.metrics.values())
        total_wildcards = sum(m.get('wildcards_total', 0) for m in self.metrics.values())
        total_fluents = sum(m.get('fluents_total', 0) for m in self.metrics.values())
        
        print(f"\n📈 Aggregate Statistics (ACCURATE FROM JSON):")
        print(f"   🎯 Total Objects: {total_objects}")
        print(f"   ⚡ Total Actions: {total_actions}")
        print(f"   ✅ Total Positive Preconditions: {total_pos_precond}")
        print(f"   ❌ Total Negative Preconditions: {total_neg_precond}")
        print(f"   🃏 Total Wildcards: {total_wildcards}")
        print(f"   🔧 Total Fluents: {total_fluents}")
        
        # Tabella per file
        print(f"\n📋 Per-File Breakdown:")
        print(f"{'File':<35} {'Obj':<4} {'Act':<4} {'Pos+':<5} {'Neg-':<5} {'Wild':<5} {'Fluent':<7} {'Arity':<6}")
        print(f"{'-'*80}")
        
        for filename, metrics in sorted(self.metrics.items()):
            obj_count = metrics.get('objects_total', 0)
            act_count = metrics.get('actions_total', 0)
            pos_count = metrics.get('positive_preconditions_total', 0)
            neg_count = metrics.get('negative_preconditions_total', 0)
            wild_count = metrics.get('wildcards_total', 0)
            fluent_count = metrics.get('fluents_total', 0)
            max_arity = metrics.get('max_action_arity', 0)
            
            print(f"{filename[:34]:<35} {obj_count:<4} {act_count:<4} {pos_count:<5} {neg_count:<5} {wild_count:<5} {fluent_count:<7} {max_arity:<6}")
        
        print(f"\n💡 This analysis is based on JSON data from the converter")
        print(f"   Much more accurate than Prolog parsing with regex!")
        print(f"\n{'='*80}")

if __name__ == "__main__":
    analyzer = JSONStructureAnalyzer()
    
    # Analizza tutti i file nella directory PROLOG/
    analyzer.analyze_all_files()
    
    # Stampa sommario
    analyzer.print_summary()
    
    # Salva risultati
    analyzer.save_analysis()