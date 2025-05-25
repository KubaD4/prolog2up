import time
import re
from pyswip import Prolog

def extract_prolog_knowledge(prolog_file):
    """Extract knowledge from Prolog file using PySwip without making assumptions about names"""
    start_time = time.time()
    print(f"Starting extraction from Prolog file...")
    
    # Initialize Prolog engine
    prolog = Prolog()
    
    # Load the Prolog file
    prolog.consult(prolog_file)
    type_predicates = {}

    # Metodo generale
    try:
        
        predicates_found = set()
        
        with open(prolog_file, 'r') as f:
            content = f.read()
            
        # Cerca nomeTipo(istanza).
        import re
        type_patterns = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\([^)]+\)\s*\.', content, re.MULTILINE)
        predicates_found.update(type_patterns)
        
        # Cerca anche nei type constraints delle azioni 
        action_patterns = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\([^)]+\)', content)
        predicates_found.update([p for p in action_patterns if p not in ['action', 'add', 'del']])
        
        
        for predicate in predicates_found:
            try:
                # Testa se questo predicato ha istanze unarie
                instances = list(prolog.query(f"{predicate}(X)"))
                if instances:
                    valid_instances = []
                    for instance in instances:
                        instance_value = instance['X']
                        if isinstance(instance_value, (str, int)) or (hasattr(instance_value, 'name') and not str(instance_value).startswith('_')):
                            valid_instances.append(instance_value)
                    
                    if valid_instances:
                        type_predicates[predicate] = valid_instances
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Warning: General type extraction failed: {e}")
        print("Falling back to manual type detection...")
        
        for predicate in ["block", "agent", "mela", "pos", "cuoco", "cibo", "strumento", "persona", "porta", "stanza", "vegetale", "piano"]:
            try:
                instances = list(prolog.query(f"{predicate}(X)"))
                if instances:
                    type_predicates[predicate] = [i['X'] for i in instances]
            except Exception:
                pass
    
    # Extract initial state
    init_state_query = list(prolog.query("init_state(X)"))
    if init_state_query:
        init_state_list = init_state_query[0]['X']
        init_state = []
        for item in init_state_list:
            # Convert Prolog term to string
            init_state.append(str(item))
    else:
        init_state = []
    
    # Extract goal state
    goal_state_query = list(prolog.query("goal_state(X)"))
    if goal_state_query:
        goal_state_list = goal_state_query[0]['X']
        goal_state = []
        for item in goal_state_list:
            # Convert Prolog term to string
            goal_state.append(str(item))
    else:
        goal_state = []
    
    # Extract actions (query directly for action predicates)
    actions = []
    try:
        # Direct query for actions without using clause/2
        for solution in prolog.query("action(Head, Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"):
            action_head = str(solution["Head"])
            
            # Extract action name from head
            if '(' in action_head:
                action_name = action_head.split('(')[0]
                
                # Extract parameters from head
                params_match = re.match(r'[^(]+\((.*)\)', action_head)
                param_values = []
                if params_match:
                    params_str = params_match.group(1)
                    # Split parameters, handling potential nested parentheses
                    param_values = []
                    current_param = ""
                    paren_count = 0
                    
                    for char in params_str:
                        if char == ',' and paren_count == 0:
                            param_values.append(current_param.strip())
                            current_param = ""
                        else:
                            if char == '(':
                                paren_count += 1
                            elif char == ')':
                                paren_count -= 1
                            current_param += char
                    
                    if current_param:
                        param_values.append(current_param.strip())
                
                # Create parameter names (Param1, Param2, ...)
                param_names = [f"Param{i+1}" for i in range(len(param_values))]
                
                # Create mapping from original parameter values to param names
                param_mapping = {str(val): name for val, name in zip(param_values, param_names)}
                
                # Function to replace parameter values with names in expressions
                def replace_params(expr, mapping):
                    # Convert expression to string if it's not already
                    expr_str = str(expr)
                    # For each parameter value, replace it with the corresponding name
                    for val, name in mapping.items():
                        # Replace parameters but be careful to only replace whole words
                        # and not parts of other words
                        expr_str = re.sub(r'\b' + re.escape(val) + r'\b', name, expr_str)
                    return expr_str
                
                # Process preconditions
                processed_preconditions = []
                for precond in solution['Precond']:
                    processed_preconditions.append(replace_params(precond, param_mapping))
                
                # Process negative preconditions
                processed_neg_preconditions = []
                for neg_precond in solution['NegPrecond']:
                    processed_neg_preconditions.append(replace_params(neg_precond, param_mapping))
                
                # Process resource preconditions
                processed_resource_preconditions = []
                for res_precond in solution['ResourcePrecond']:
                    processed_resource_preconditions.append(replace_params(res_precond, param_mapping))
                
                # Process type constraints
                processed_type_constraints = []
                for constraint in solution['TypeConstraints']:
                    processed_type_constraints.append(replace_params(constraint, param_mapping))
                
                # Process effects
                processed_effects = []
                for effect in solution['Effects']:
                    # Process both add and del effects
                    effect_str = str(effect)
                    
                    # Handle add effects
                    if 'add(' in effect_str:
                        match = re.search(r'add\((.*?)\)', effect_str)
                        if match:
                            inner = match.group(1)
                            replaced_inner = replace_params(inner, param_mapping)
                            effect_str = effect_str.replace(match.group(0), f"add({replaced_inner})")
                    
                    # Handle del effects
                    if 'del(' in effect_str:
                        match = re.search(r'del\((.*?)\)', effect_str)
                        if match:
                            inner = match.group(1)
                            replaced_inner = replace_params(inner, param_mapping)
                            effect_str = effect_str.replace(match.group(0), f"del({replaced_inner})")
                    
                    processed_effects.append(effect_str)
                
                # Create action info dictionary with processed data
                action_info = {
                    'name': action_name,
                    'parameters': param_names,
                    'param_values': param_values,
                    'preconditions': processed_preconditions,
                    'neg_preconditions': processed_neg_preconditions,
                    'resource_preconditions': processed_resource_preconditions,
                    'type_constraints': processed_type_constraints,
                    'effects': processed_effects
                }
                actions.append(action_info)
            else:
                print(f"Warning: Invalid action head format")
    except Exception as e:
        print(f"Warning: Could not extract actions directly: {e}")

    for action in actions:
        for constraint in action['type_constraints']:
            match = re.match(r'([a-zA-Z_]+)\((.*?)\)', constraint)
            if match and match.group(1) not in type_predicates:
                pred_name = match.group(1)
                try:
                    instances = list(prolog.query(f"{pred_name}(X)"))
                    if instances:
                        type_predicates[pred_name] = [i['X'] for i in instances]
                except Exception:
                    # Silently ignore errors
                    pass
    
    # Organize extracted knowledge
    knowledge = {
        'types': type_predicates,  # Now a dictionary of type_name -> list of instances
        'init_state': init_state,
        'goal_state': goal_state,
        'actions': actions
    }
    
    # Extract fluent names from actions, initial and goal states
    fluent_names = set()
    
    # From initial state
    for state in init_state:
        fluent_name = state.split('(')[0]
        fluent_names.add(fluent_name)
    
    # From goal state
    for state in goal_state:
        fluent_name = state.split('(')[0]
        fluent_names.add(fluent_name)
    
    # From action preconditions and effects
    for action in actions:
        for precond in action['preconditions']:
            if '(' in precond:
                fluent_name = precond.split('(')[0]
                fluent_names.add(fluent_name)
        
        for effect in action['effects']:
            if 'add(' in effect or 'del(' in effect:
                match = re.search(r'add\((.*?)\)', effect) or re.search(r'del\((.*?)\)', effect)
                if match:
                    inner_fluent = match.group(1)
                    fluent_name = inner_fluent.split('(')[0]
                    fluent_names.add(fluent_name)
    
    knowledge['fluent_names'] = list(fluent_names)
    
    extraction_time = time.time() - start_time
    print(f"Extraction completed in {extraction_time:.4f} seconds")
    
    return knowledge


def analyze_fluent_signatures(knowledge):
    """Analyze fluent signatures to determine their parameter types without making assumptions"""
    fluent_signatures = {}
    
    # Create a mapping from object to its type
    object_to_type = {}
    for type_name, instances in knowledge['types'].items():
        for instance in instances:
            object_to_type[str(instance)] = type_name
    
    # Define known fluent signatures
    known_fluents = {
        'intera': ['mela'],
        'morsa': ['mela'],
        'clear': ['block'],
        'available': ['agent'],
        'ontable': ['block'],
        'on': ['block', 'block'],
        'moving_table_to_block': ['agent', 'block', 'block', 'Location', 'Location', 'Location', 'Location'],
        'moving_table_to_table': ['agent', 'block', 'Location', 'Location', 'Location', 'Location'],
        'moving_onblock_to_table': ['agent', 'block', 'Location', 'Location', 'Location', 'Location'],
        'moving_onblock_to_block': ['agent', 'block', 'block', 'Location', 'Location', 'Location', 'Location']
    }
    
    # Apply known fluent signatures first
    for fluent_name in knowledge['fluent_names']:
        if fluent_name in known_fluents:
            fluent_signatures[fluent_name] = known_fluents[fluent_name]
    
    # Helper function to extract parameter types from a fluent instance
    def extract_param_types(fluent_str):
        # Extract the parameters from the fluent string
        match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_str)
        if not match:
            return []
        
        # Get parameter strings
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(',')]
        
        param_types = []
        for param in params:
            # Check if parameter is a known object
            if param in object_to_type:
                param_types.append(object_to_type[param])
            # Check if it might be a position/location parameter (numeric)
            elif param.isdigit() or (param.replace('-', '').replace('.', '').isdigit()):
                param_types.append('Location')
            else:
                # If can't determine, assume it's a variable of unknown type
                param_types.append('Unknown')
        
        return param_types
    
    # Analyze all fluent instances in initial state, goal state and actions to infer types
    for fluent_name in knowledge['fluent_names']:
        # Skip fluents we've already handled
        if fluent_name in fluent_signatures:
            continue
            
        param_types_instances = []
        
        # Check initial state
        for state in knowledge['init_state']:
            if state.startswith(fluent_name + '('):
                param_types = extract_param_types(state)
                if param_types:
                    param_types_instances.append(param_types)
        
        # Check goal state
        for state in knowledge['goal_state']:
            if state.startswith(fluent_name + '('):
                param_types = extract_param_types(state)
                if param_types:
                    param_types_instances.append(param_types)
        
        # Special case for 'at' fluent
        if fluent_name == 'at':
            # Look for pattern at(object, x, y) with 3 parameters
            three_param_instances = []
            for state in knowledge['init_state'] + knowledge['goal_state']:
                match = re.match(r'at\(([^,]+),\s*(\d+),\s*(\d+)\)', state)
                if match:
                    obj_name = match.group(1).strip()
                    x, y = match.group(2), match.group(3)
                    obj_type = object_to_type.get(obj_name, 'Unknown')
                    three_param_instances.append([obj_type, 'Location', 'Location'])
            
            if three_param_instances:
                fluent_signatures[fluent_name] = three_param_instances[0]
                continue
        
        # Check action preconditions and effects
        for action in knowledge['actions']:
            for precond in action['preconditions']:
                if precond.startswith(fluent_name + '('):
                    param_types = extract_param_types(precond)
                    if param_types:
                        param_types_instances.append(param_types)
            
            for effect in action['effects']:
                if 'add(' in effect or 'del(' in effect:
                    match = re.search(r'add\((.*?)\)', effect) or re.search(r'del\((.*?)\)', effect)
                    if match and match.group(1).startswith(fluent_name + '('):
                        param_types = extract_param_types(match.group(1))
                        if param_types:
                            param_types_instances.append(param_types)
        
        # Additional check: look for type constraints in actions
        for action in knowledge['actions']:
            for constraint in action['type_constraints']:
                if not any(f"{param_name}(" in constraint for param_name in knowledge['types']):
                    continue
                    
                # Extract type information from constraints
                match = re.match(r'([a-zA-Z_]+)\((.*?)\)', constraint)
                if match and match.group(1) in knowledge['types']:
                    # Found a type constraint, now find which parameter it refers to
                    type_name = match.group(1)
                    param_name = match.group(2)
                    
                    # Find where this parameter is used in fluents
                    for precond in action['preconditions']:
                        precond_match = re.match(r'([a-zA-Z_]+)\((.*?)\)', precond)
                        if not precond_match:
                            continue
                            
                        precond_fluent = precond_match.group(1)
                        precond_params = [p.strip() for p in precond_match.group(2).split(',')]
                        
                        if precond_fluent == fluent_name and param_name in precond_params:
                            # Found a parameter with known type
                            param_pos = precond_params.index(param_name)
                            
                            # Create type list with known type at this position
                            new_type_list = ['Unknown'] * len(precond_params)
                            new_type_list[param_pos] = type_name
                            param_types_instances.append(new_type_list)
        
        # If we have any instances of this fluent
        if param_types_instances:
            # Use the most common length
            common_length = max(set(len(pt) for pt in param_types_instances), key=lambda x: sum(1 for pt in param_types_instances if len(pt) == x))
            
            # Filter to instances with the common length
            filtered_instances = [pt for pt in param_types_instances if len(pt) == common_length]
            
            # For each parameter position, find the most common type
            final_param_types = []
            for i in range(common_length):
                types_at_position = [instance[i] for instance in filtered_instances]
                # Filter out 'Unknown' if there are known types
                known_types = [t for t in types_at_position if t != 'Unknown']
                if known_types:
                    common_type = max(set(known_types), key=known_types.count)
                else:
                    common_type = 'Unknown'
                final_param_types.append(common_type)
            
            fluent_signatures[fluent_name] = final_param_types
    
    return fluent_signatures


def print_knowledge_summary(knowledge, fluent_signatures):
    """Print a summary of the extracted knowledge"""
    print(f"\nExtracted knowledge summary:")
    print(f"  Types and objects:")
    for type_name, instances in knowledge['types'].items():
        print(f"    {type_name}: {instances}")
    print(f"  Fluents: {knowledge['fluent_names']}")
    print(f"  Initial state has {len(knowledge['init_state'])} assertions")
    print(f"  Goal state has {len(knowledge['goal_state'])} assertions")
    print(f"  Found {len(knowledge['actions'])} actions")
    
    # Print Initial State and Goal State
    print(f"\nInitial State:")
    for state in knowledge['init_state']:
        print(f"  {state}")
    
    print(f"\nGoal State:")
    for state in knowledge['goal_state']:
        print(f"  {state}")
    
    # Print fluent signatures
    print(f"\nFluent signatures:")
    for fluent_name, param_types in fluent_signatures.items():
        print(f"  {fluent_name}: {param_types}")
    
    # Print actions in a complete, ordered and clean way
    print(f"\nActions details:")
    # Sort actions by name for better readability
    sorted_actions = sorted(knowledge['actions'], key=lambda x: x['name'])
    
    for i, action in enumerate(sorted_actions, 1):
        print(f"\n  Action {i}: {action['name']}")
        
        # Print parameter names with their Prolog variable values
        params = []
        for param_name, param_value in zip(action['parameters'], action['param_values']):
            # Skip parameters that are unnamed (underscores)
            if param_name.startswith('_'):
                continue
            # Only show the Prolog value if it's not an underscore
            if str(param_value) != '_':
                params.append(f"{param_name} ({param_value})")
            else:
                params.append(param_name)
        
        print(f"    Parameters: {', '.join(params)}")
        
        # Replace Prolog variables with the parameter names in preconditions and effects
        param_mapping = {}
        for param_name, param_value in zip(action['parameters'], action['param_values']):
            param_mapping[str(param_value)] = param_name
        
        def replace_vars(text):
            # Replace variables with their parameter names
            for var, name in param_mapping.items():
                # Replace entire variables
                text = text.replace(var + ')', name + ')')
                text = text.replace(var + ',', name + ',')
                
                # Handle when variable is at the end of a list
                text = text.replace(', ' + var, ', ' + name)
                
                # Handle when variable is standalone
                if text == var:
                    text = name
            return text
        
        if action['preconditions']:
            print(f"    Preconditions:")
            for precond in action['preconditions']:
                print(f"      + {replace_vars(precond)}")
        
        if action['neg_preconditions']:
            print(f"    Negative Preconditions:")
            for neg_precond in action['neg_preconditions']:
                print(f"      - {replace_vars(neg_precond)}")
        
        if action['resource_preconditions']:
            print(f"    Resource Preconditions:")
            for res_precond in action['resource_preconditions']:
                print(f"      * {replace_vars(res_precond)}")
        
        if action['type_constraints']:
            print(f"    Type Constraints:")
            for constraint in action['type_constraints']:
                print(f"      = {replace_vars(constraint)}")
        
        effects_add = [e for e in action['effects'] if 'add(' in e]
        effects_del = [e for e in action['effects'] if 'del(' in e]
        
        if effects_add:
            print(f"    Add Effects:")
            for effect in effects_add:
                # Extract the inner part of add(...)
                inner = effect.split('add(')[1].rsplit(')', 1)[0]
                print(f"      + {replace_vars(inner)}")
        
        if effects_del:
            print(f"    Delete Effects:")
            for effect in effects_del:
                # Extract the inner part of del(...)
                inner = effect.split('del(')[1].rsplit(')', 1)[0]
                print(f"      - {replace_vars(inner)}")