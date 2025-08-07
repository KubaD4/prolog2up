# Crea questo file come: CONVERTER/planner_config.py

"""
Configurazione per i planner e algoritmi di ricerca
Questo file permette di gestire facilmente quali algoritmi usare
"""

# Configurazioni predefinite di algoritmi
ALGORITHM_SETS = {
    "basic": [
        "lazy_greedy",
        "astar_ff"
    ],
    
    "fast": [
        "lazy_greedy", 
        "eager_greedy",
        "astar_ff",
        "wastar"
    ],
    
    "comprehensive": [
        "lazy_greedy",
        "eager_greedy", 
        "astar_ff",
        "astar_blind",
        "astar_lmcut",
        "astar_lmcount", 
        "wastar",
        "lazy_wastar",
        "ehc_ff",
        "lazy_greedy_multi"
    ],
    
    "research": [
        "lazy_greedy",
        "eager_greedy",
        "astar_ff", 
        "astar_add",
        "astar_lmcut",
        "astar_lmcount",
        "astar_goalcount",
        "wastar",
        "wastar_ff_w3",
        "wastar_ff_w5", 
        "lazy_wastar",
        "lazy_wastar_w3",
        "ehc_ff",
        "iterated",
        "lazy_greedy_multi",
        "eager_greedy_multi", 
        "lazy_best_first",
        "astar_merge_shrink"
    ],
    
    "debug": [
        "lazy_greedy",
        "astar_ff", 
        "astar_blind"
    ]
}

# Descrizioni degli algoritmi per documentazione
ALGORITHM_DESCRIPTIONS = {
    "lazy_greedy": "Lazy Greedy Best-First Search con FF heuristic - Veloce e efficace",
    "eager_greedy": "Eager Greedy Best-First Search con FF heuristic - Simile a lazy ma più memoria",
    "astar_ff": "A* con FF heuristic - Ottimale con euristica ammissibile",
    "astar_blind": "A* cieco - Lento ma garantito ottimale",
    "astar_lmcut": "A* con LM-Cut heuristic - Molto forte ma costoso",
    "astar_lmcount": "A* con Landmark Count heuristic - Bilanciato",
    "astar_goalcount": "A* con Goal Count heuristic - Semplice ma efficace", 
    "astar_add": "A* con Additive heuristic - Classico",
    "astar_max": "A* con Maximum heuristic - Combina FF e Goal Count",
    "wastar": "Weighted A* (w=2) - Compromesso qualità/velocità",
    "wastar_ff_w3": "Weighted A* (w=3) - Più veloce, meno ottimale", 
    "wastar_ff_w5": "Weighted A* (w=5) - Molto veloce",
    "lazy_wastar": "Lazy Weighted A* - Veloce con buona qualità",
    "lazy_wastar_w3": "Lazy Weighted A* (w=3) - Bilanciato",
    "lazy_wastar_w5": "Lazy Weighted A* (w=5) - Priorità velocità",
    "ehc_ff": "Enforced Hill-Climbing con FF - Molto veloce ma incompleto",
    "iterated": "Iterative search - Combina diversi algoritmi",
    "lazy_greedy_multi": "Lazy Greedy multi-heuristic - Usa FF+Add",
    "eager_greedy_multi": "Eager Greedy multi-heuristic - Usa FF+Add", 
    "lazy_greedy_ff_goalcount": "Lazy Greedy FF+GoalCount - Doppia euristica",
    "lazy_best_first": "Lazy Best-First con preferred operators",
    "eager_best_first": "Eager Best-First con preferred operators",
    "astar_merge_shrink": "A* con Merge&Shrink - Molto avanzato"
}

# Caratteristiche degli algoritmi
ALGORITHM_PROPERTIES = {
    "lazy_greedy": {"speed": "fast", "memory": "low", "optimality": "no", "completeness": "no"},
    "eager_greedy": {"speed": "fast", "memory": "high", "optimality": "no", "completeness": "no"},
    "astar_ff": {"speed": "medium", "memory": "medium", "optimality": "no", "completeness": "yes"},
    "astar_blind": {"speed": "very_slow", "memory": "high", "optimality": "yes", "completeness": "yes"},
    "astar_lmcut": {"speed": "slow", "memory": "high", "optimality": "yes", "completeness": "yes"},
    "astar_lmcount": {"speed": "medium", "memory": "medium", "optimality": "no", "completeness": "yes"},
    "wastar": {"speed": "fast", "memory": "medium", "optimality": "bounded", "completeness": "yes"},
    "lazy_wastar": {"speed": "very_fast", "memory": "low", "optimality": "bounded", "completeness": "yes"},
    "ehc_ff": {"speed": "very_fast", "memory": "very_low", "optimality": "no", "completeness": "no"},
}

# Raccomandazioni per diversi scenari
SCENARIO_RECOMMENDATIONS = {
    "small_problems": ["lazy_greedy", "astar_ff", "ehc_ff"],
    "large_problems": ["lazy_greedy", "lazy_wastar", "ehc_ff"], 
    "optimal_solution_needed": ["astar_lmcut", "astar_ff", "astar_blind"],
    "time_critical": ["lazy_greedy", "ehc_ff", "lazy_wastar"],
    "memory_limited": ["lazy_greedy", "ehc_ff", "lazy_wastar"],
    "research_benchmark": ["lazy_greedy", "astar_ff", "astar_lmcut", "wastar", "ehc_ff"],
    "first_time_user": ["lazy_greedy", "astar_ff"],
    "debugging": ["lazy_greedy", "astar_blind"]
}

def get_algorithms_for_scenario(scenario):
    """Ritorna gli algoritmi raccomandati per uno scenario specifico"""
    return SCENARIO_RECOMMENDATIONS.get(scenario, ALGORITHM_SETS["basic"])

def get_algorithm_set(set_name):
    """Ritorna un set predefinito di algoritmi"""
    return ALGORITHM_SETS.get(set_name, ALGORITHM_SETS["basic"])

def describe_algorithm(algorithm):
    """Ritorna la descrizione di un algoritmo"""
    return ALGORITHM_DESCRIPTIONS.get(algorithm, "Algoritmo non documentato")

def get_algorithm_properties(algorithm):
    """Ritorna le proprietà di un algoritmo"""
    return ALGORITHM_PROPERTIES.get(algorithm, {})

def filter_algorithms_by_speed(algorithms, max_speed="medium"):
    """Filtra algoritmi per velocità massima"""
    speed_order = ["very_fast", "fast", "medium", "slow", "very_slow"]
    max_index = speed_order.index(max_speed) if max_speed in speed_order else len(speed_order)
    
    filtered = []
    for alg in algorithms:
        props = get_algorithm_properties(alg)
        speed = props.get("speed", "medium")
        if speed in speed_order[:max_index + 1]:
            filtered.append(alg)
    
    return filtered

def recommend_algorithms(problem_size="medium", time_limit="medium", memory_limit="medium", need_optimal=False):
    """Raccomanda algoritmi basati sui vincoli del problema"""
    
    if need_optimal:
        candidates = ["astar_lmcut", "astar_ff", "astar_blind"]
    elif problem_size == "large" or time_limit == "low":
        candidates = get_algorithm_set("fast")
    elif time_limit == "high":
        candidates = get_algorithm_set("comprehensive")
    else:
        candidates = get_algorithm_set("basic")
    
    # Filtra per memoria se necessario
    if memory_limit == "low":
        candidates = [alg for alg in candidates 
                     if get_algorithm_properties(alg).get("memory", "medium") in ["low", "very_low"]]
    
    # Filtra per velocità se necessario  
    if time_limit == "low":
        candidates = filter_algorithms_by_speed(candidates, "fast")
    
    return candidates or ["lazy_greedy"]  # Fallback

# Configurazioni per orchestrator.py
DEFAULT_CONFIG = {
    "algorithm_set": "basic",
    "timeout_per_algorithm": 300,
    "max_algorithms": 10,
    "skip_slow_on_large_problems": True,
    "show_individual_timings": True,
    "continue_on_error": True
}

def get_orchestrator_config():
    """Ritorna la configurazione per l'orchestrator"""
    return DEFAULT_CONFIG

# Esempio di utilizzo nel codice:
if __name__ == "__main__":
    print("=== Configurazione Planner ===")
    print(f"Algoritmi basic: {get_algorithm_set('basic')}")
    print(f"Algoritmi comprehensive: {get_algorithm_set('comprehensive')}")
    print(f"\nRaccomandazioni per problemi grandi: {get_algorithms_for_scenario('large_problems')}")
    print(f"Raccomandazioni per soluzioni ottime: {get_algorithms_for_scenario('optimal_solution_needed')}")
    
    print(f"\nDescrizione lazy_greedy: {describe_algorithm('lazy_greedy')}")
    print(f"Proprietà astar_ff: {get_algorithm_properties('astar_ff')}")
    
    print(f"\nRaccomandazione automatica: {recommend_algorithms('large', 'low', 'medium', False)}")

