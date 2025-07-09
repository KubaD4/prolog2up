import time
import re
from pyswip import Prolog

def improve_type_constraints_inference(knowledge):
    """
    Post-process actions to infer missing type constraints based on parameter names
    and their usage in fluents.
    """
    print("\nImproving type constraint inference...")
    
    # Build a mapping of parameter patterns to likely types
    param_patterns = {
        'agent': ['agent', 'a'],
        'block': ['block', 'b'],
        'pos': ['x', 'y', 'pos', 'loc'],
        'location': ['location', 'loc'],
        'container': ['container', 'c'],
        'robot': ['robot', 'r']
    }
    
    for action in knowledge['actions']:
        action_name = action['name']
        parameters = action['parameters']
        param_values = action.get('param_values', [])
        type_constraints = action.get('_type_constraint_dict', {})
        
        # For each parameter without a type constraint
        for idx, (param_name, param_value) in enumerate(zip(parameters, param_values)):
            if param_name not in type_constraints or type_constraints.get(param_name) == 'Unknown':
                # Try to infer type from parameter value/name
                inferred_type = None
                param_value_lower = str(param_value).lower()
                
                # Check against patterns
                for type_name, patterns in param_patterns.items():
                    for pattern in patterns:
                        if pattern in param_value_lower:
                            inferred_type = type_name
                            break
                    if inferred_type:
                        break
                
                # Special case for numeric coordinates
                if not inferred_type and param_value_lower in ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']:
                    inferred_type = 'pos'
                
                # If still no type, look at how the parameter is used in fluents
                if not inferred_type:
                    # Check in preconditions and effects
                    for section in ['preconditions', 'add_effects', 'del_effects']:
                        for item_str in action.get(section, []):
                            if param_name in item_str:
                                # Try to infer from fluent usage
                                if 'at(' in item_str and param_name in item_str.split('at(')[1]:
                                    # If used in at() fluent, likely a position or block
                                    # Check position in the fluent
                                    import re
                                    at_match = re.search(r'at\(([^,]+),([^,]+),([^)]+)\)', item_str)
                                    if at_match:
                                        args = [at_match.group(1).strip(), at_match.group(2).strip(), at_match.group(3).strip()]
                                        if param_name in args[1:]:  # positions 2 and 3 are coordinates
                                            inferred_type = 'pos'
                                        elif param_name == args[0]:  # position 1 is the object
                                            inferred_type = 'block'
                                
                                elif 'available(' in item_str and param_name in item_str:
                                    inferred_type = 'agent'
                                elif 'on(' in item_str and param_name in item_str:
                                    inferred_type = 'block'
                                elif 'clear(' in item_str and param_name in item_str:
                                    inferred_type = 'block'
                                elif 'ontable(' in item_str and param_name in item_str:
                                    inferred_type = 'block'
                
                if inferred_type:
                    print(f"  Inferred type for {action_name}.{param_name} ({param_value}): {inferred_type}")
                    type_constraints[param_name] = inferred_type
                    
                    # Also update the string type constraints
                    constraint_str = f"{inferred_type}({param_name})"
                    if constraint_str not in action['type_constraints']:
                        action['type_constraints'].append(constraint_str)
        
        # Update the action's type constraint dict
        action['_type_constraint_dict'] = type_constraints
    
    return knowledge


def extract_prolog_knowledge(prolog_file):
    """Extract knowledge from Prolog file using PySwip without making assumptions about names"""
    start_time = time.time()
    print(f"Starting extraction from Prolog file...")
    
    prolog = Prolog()
    # Load the Prolog file
    prolog.consult(prolog_file)
    type_predicates = {}

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
                
                # Extract parameters from head - IMPROVED VERSION
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
                
                # CRITICAL FIX: Create a more robust parameter mapping
                # that preserves the original parameter order and avoids confusion
                param_mapping = {}
                param_order_map = {}  # Track the order of parameters
                
                for idx, val in enumerate(param_values):
                    param_name = param_names[idx]
                    param_mapping[str(val)] = param_name
                    param_order_map[param_name] = idx
                
                # Function to replace parameter values with names in expressions
                def replace_params(expr, mapping, param_values_list):
                    """
                    Enhanced parameter replacement that handles ambiguous cases better
                    """
                    expr_str = str(expr)
                    
                    # Sort parameter values by length (descending) to avoid partial replacements
                    sorted_params = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)
                    
                    # Create a temporary expression for processing
                    temp_expr = expr_str
                    replacements = []
                    
                    # First pass: identify all replacements needed
                    for val, name in sorted_params:
                        # Use word boundaries and context to ensure accurate replacement
                        # Look for the value as a complete parameter (not part of another string)
                        pattern = r'\b' + re.escape(val) + r'\b'
                        matches = list(re.finditer(pattern, temp_expr))
                        
                        for match in matches:
                            replacements.append((match.start(), match.end(), val, name))
                    
                    # Sort replacements by position (reverse order to maintain indices)
                    replacements.sort(key=lambda x: x[0], reverse=True)
                    
                    # Apply replacements
                    result = temp_expr
                    for start, end, val, name in replacements:
                        result = result[:start] + name + result[end:]
                    
                    return result
                
                # Process preconditions
                processed_preconditions = []
                for precond in solution['Precond']:
                    processed_preconditions.append(replace_params(precond, param_mapping, param_values))
                
                # Process negative preconditions
                processed_neg_preconditions = []
                for neg_precond in solution['NegPrecond']:
                    processed_neg_preconditions.append(replace_params(neg_precond, param_mapping, param_values))
                
                # Process resource preconditions
                processed_resource_preconditions = []
                for res_precond in solution['ResourcePrecond']:
                    processed_resource_preconditions.append(replace_params(res_precond, param_mapping, param_values))
                
                # CRITICAL FIX: Process type constraints more carefully
                processed_type_constraints = []
                type_constraint_dict = {}  # Store the actual type mapping
                
                for constraint in solution['TypeConstraints']:
                    constraint_str = str(constraint)
                    
                    # Parse the constraint to extract type and parameters
                    constraint_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)', constraint_str)
                    if constraint_match:
                        type_name = constraint_match.group(1)
                        params_in_constraint = constraint_match.group(2)
                        
                        # Split parameters in the constraint
                        constraint_params = []
                        current = ""
                        paren_count = 0
                        
                        for char in params_in_constraint:
                            if char == ',' and paren_count == 0:
                                constraint_params.append(current.strip())
                                current = ""
                            else:
                                if char == '(':
                                    paren_count += 1
                                elif char == ')':
                                    paren_count -= 1
                                current += char
                        
                        if current:
                            constraint_params.append(current.strip())
                        
                        # Map each parameter in the constraint to its Param name
                        for cp in constraint_params:
                            cp_str = str(cp).strip()
                            if cp_str in param_mapping:
                                param_name = param_mapping[cp_str]
                                type_constraint_dict[param_name] = type_name
                        
                        # Create the processed constraint string
                        processed_params = []
                        for cp in constraint_params:
                            cp_str = str(cp).strip()
                            if cp_str in param_mapping:
                                processed_params.append(param_mapping[cp_str])
                            else:
                                processed_params.append(cp_str)
                        
                        if processed_params:
                            processed_constraint = f"{type_name}({', '.join(processed_params)})"
                            processed_type_constraints.append(processed_constraint)
                
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
                            replaced_inner = replace_params(inner, param_mapping, param_values)
                            effect_str = effect_str.replace(match.group(0), f"add({replaced_inner})")
                    
                    # Handle del effects
                    if 'del(' in effect_str:
                        match = re.search(r'del\((.*?)\)', effect_str)
                        if match:
                            inner = match.group(1)
                            replaced_inner = replace_params(inner, param_mapping, param_values)
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
                    'effects': processed_effects,
                    # Add the actual type mapping for debugging
                    '_type_constraint_dict': type_constraint_dict
                }
                actions.append(action_info)
            else:
                print(f"Warning: Invalid action head format")
    except Exception as e:
        print(f"Warning: Could not extract actions directly: {e}")
        import traceback
        traceback.print_exc()

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
    
    knowledge = improve_type_constraints_inference(knowledge)
    
    extraction_time = time.time() - start_time
    print(f"Extraction completed in {extraction_time:.4f} seconds")
        
    return knowledge


def analyze_fluent_signatures(knowledge):
    """Analyze fluent signatures to determine their parameter types - COMPLETELY GENERALIZED"""
    fluent_signatures = {}
    
    # Create a mapping from object to its type
    object_to_type = {}
    for type_name, instances in knowledge['types'].items():
        for instance in instances:
            object_to_type[str(instance)] = type_name
    
    
    # Collect fluent usage information with action context and scores
    fluent_usage = {}  # fluent_name -> list of (param_types, action_score, action_name)
    
    def extract_param_types_from_action(fluent_str, action):
        """Extract parameter types from a fluent string using action context"""
        match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_str)
        if not match:
            return []
        
        fluent_name = match.group(1)
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(',')]
        
        param_types = []
        
        # Use the _type_constraint_dict if available (from our fixed extractor)
        type_constraint_dict = action.get('_type_constraint_dict', {})
        
        # Also parse the string-based constraints as fallback
        action_type_constraints = action.get('type_constraints', [])
        param_to_type = {}
        
        for constraint in action_type_constraints:
            constraint_match = re.match(r'([a-zA-Z_]+)\((.*?)\)', constraint)
            if constraint_match:
                type_name = constraint_match.group(1)
                param_names = constraint_match.group(2)
                
                # Handle both single and multiple parameters
                if ',' in param_names:
                    for param in param_names.split(','):
                        param = param.strip()
                        if param:
                            param_to_type[param] = type_name
                else:
                    param_to_type[param_names.strip()] = type_name
        
        for param in params:
            # First try the direct type constraint dict
            if param in type_constraint_dict:
                param_types.append(type_constraint_dict[param])
            # Then try the parsed constraints
            elif param in param_to_type:
                param_types.append(param_to_type[param])
            # Check if parameter is a known object from extracted types
            elif param in object_to_type:
                param_types.append(object_to_type[param])
            # Check if it's numeric (likely position/coordinate)
            elif param.isdigit() or (param.replace('-', '').replace('.', '').isdigit()):
                param_types.append('pos')
            # Check if it starts with underscore (wildcard)
            elif param.startswith('_'):
                param_types.append('wildcard')
            else:
                param_types.append('Unknown')
        
        return param_types
    
    # Analyze fluent usage in ALL contexts
    for fluent_name in knowledge['fluent_names']:
        if fluent_name not in fluent_usage:
            fluent_usage[fluent_name] = []
        
        # From initial and goal states (highest priority - concrete instances)
        for state_list, state_name in [(knowledge['init_state'], 'init'), (knowledge['goal_state'], 'goal')]:
            for state in state_list:
                if state.startswith(fluent_name + '('):
                    param_types = []
                    match = re.match(r'([a-zA-Z_]+)\((.*?)\)', state)
                    if match:
                        params = [p.strip() for p in match.group(2).split(',')]
                        for param in params:
                            if param in object_to_type:
                                param_types.append(object_to_type[param])
                            elif param.isdigit():
                                param_types.append('pos')
                            else:
                                param_types.append('Unknown')
                    
                    if param_types:
                        # High score for state definitions
                        fluent_usage[fluent_name].append((param_types, 100, state_name))
        
        # From actions (analyze based on type constraint richness)
        for action in knowledge['actions']:
            action_score = len(action.get('type_constraints', []))
            
            # Check preconditions
            for precond in action['preconditions']:
                if precond.startswith(fluent_name + '('):
                    param_types = extract_param_types_from_action(precond, action)
                    if param_types:
                        fluent_usage[fluent_name].append((param_types, action_score, action['name']))
            
            # Check effects
            for effect in action['effects']:
                if 'add(' in effect or 'del(' in effect:
                    match = re.search(r'add\((.*?)\)', effect) or re.search(r'del\((.*?)\)', effect)
                    if match and match.group(1).startswith(fluent_name + '('):
                        param_types = extract_param_types_from_action(match.group(1), action)
                        if param_types:
                            fluent_usage[fluent_name].append((param_types, action_score, action['name']))
    
    # Process collected usage to determine best signatures
    for fluent_name, usage_list in fluent_usage.items():
        if not usage_list:
            continue
        
        # Sort by score (descending) to prioritize more informative sources
        usage_list.sort(key=lambda x: x[1], reverse=True)
        
        # Find most common signature length
        lengths = [len(usage[0]) for usage in usage_list]
        if not lengths:
            continue
            
        most_common_length = max(set(lengths), key=lengths.count)
        
        # Filter to most common length
        filtered_usage = [usage for usage in usage_list if len(usage[0]) == most_common_length]
        
        # For each parameter position, find the best type
        final_signature = []
        for pos in range(most_common_length):
            types_at_position = []
            scores_for_types = {}
            
            for param_types, score, source in filtered_usage:
                if pos < len(param_types):
                    ptype = param_types[pos]
                    types_at_position.append(ptype)
                    if ptype not in scores_for_types:
                        scores_for_types[ptype] = 0
                    scores_for_types[ptype] += score
            
            # Choose best type for this position
            if types_at_position:
                # Filter out wildcards and unknowns if we have better options
                known_types = [t for t in types_at_position if t not in ['wildcard', 'Unknown']]
                
                if known_types:
                    # Choose type with highest combined score
                    best_type = max(known_types, key=lambda t: scores_for_types.get(t, 0))
                    final_signature.append(best_type)
                else:
                    final_signature.append('Unknown')
            else:
                final_signature.append('Unknown')
        
        fluent_signatures[fluent_name] = final_signature
    
    # Post-process to resolve remaining unknowns based on cross-action analysis
    fluent_signatures = _resolve_unknowns_across_actions(fluent_signatures, knowledge)
    
    return fluent_signatures

def _resolve_unknowns_across_actions(fluent_signatures, knowledge):
    """Resolve Unknown types by analyzing cross-action parameter usage"""
    
    # Build parameter usage patterns across actions
    param_usage_patterns = {}  # param_name -> {fluent_name: {position: type}}
    
    for action in knowledge['actions']:
        # Use the _type_constraint_dict if available
        type_constraint_dict = action.get('_type_constraint_dict', {})
        
        # Fallback to parsing string constraints
        if not type_constraint_dict:
            type_constraints = action.get('type_constraints', [])
            
            # Build param-to-type mapping for this action
            param_to_type = {}
            for constraint in type_constraints:
                constraint_match = re.match(r'([a-zA-Z_]+)\((.*?)\)', constraint)
                if constraint_match:
                    type_name = constraint_match.group(1)
                    param_names = constraint_match.group(2)
                    
                    if ',' in param_names:
                        for param in param_names.split(','):
                            param = param.strip()
                            if param:
                                param_to_type[param] = type_name
                    else:
                        param_to_type[param_names.strip()] = type_name
        else:
            param_to_type = type_constraint_dict
        
        # Analyze all fluent usages in this action
        all_fluent_uses = []
        all_fluent_uses.extend(action['preconditions'])
        
        for effect in action['effects']:
            if 'add(' in effect:
                match = re.search(r'add\((.*?)\)', effect)
                if match:
                    all_fluent_uses.append(match.group(1))
            elif 'del(' in effect:
                match = re.search(r'del\((.*?)\)', effect)
                if match:
                    all_fluent_uses.append(match.group(1))
        
        for fluent_use in all_fluent_uses:
            match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_use)
            if not match:
                continue
                
            fluent_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',')]
            
            for pos, param in enumerate(params):
                if param in param_to_type:
                    if param not in param_usage_patterns:
                        param_usage_patterns[param] = {}
                    if fluent_name not in param_usage_patterns[param]:
                        param_usage_patterns[param][fluent_name] = {}
                    param_usage_patterns[param][fluent_name][pos] = param_to_type[param]
    
    # Apply cross-action resolution
    for fluent_name, signature in fluent_signatures.items():
        for pos, param_type in enumerate(signature):
            if param_type == 'Unknown':
                # Look for patterns in parameter usage
                candidate_types = set()
                
                for param_name, usage_pattern in param_usage_patterns.items():
                    if fluent_name in usage_pattern and pos in usage_pattern[fluent_name]:
                        candidate_types.add(usage_pattern[fluent_name][pos])
                
                if len(candidate_types) == 1:
                    signature[pos] = list(candidate_types)[0]
                elif candidate_types:
                    # Choose most common
                    type_counts = {}
                    for ctype in candidate_types:
                        type_counts[ctype] = type_counts.get(ctype, 0) + 1
                    signature[pos] = max(type_counts.items(), key=lambda x: x[1])[0]
    
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
        
        # Print type constraints from _type_constraint_dict if available
        if '_type_constraint_dict' in action:
            print(f"    Type mapping: {action['_type_constraint_dict']}")
        
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