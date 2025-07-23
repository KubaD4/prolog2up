import time
import re
from pyswip import Prolog

def improve_type_constraints_inference(knowledge):
    print("\nImproving type constraints inference...")
    
    for action in knowledge['actions']:
        action_name = action['name']
        parameters = action['parameters']
        param_values = action.get('param_values', [])
        type_constraints = action.get('_type_constraint_dict', {})
        
        
        for idx, (param_name, param_value) in enumerate(zip(parameters, param_values)):
            if param_name not in type_constraints or type_constraints.get(param_name) == 'Unknown':
                
                inferred_type = None
                
                
                for section in ['preconditions', 'add_effects', 'del_effects']:
                    for item_str in action.get(section, []):
                        if param_name in item_str:
                            
                            fluent_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)', item_str)
                            if fluent_match:
                                fluent_name = fluent_match.group(1)
                                fluent_args = [arg.strip() for arg in fluent_match.group(2).split(',')]
                                
                                
                                if param_name in fluent_args:
                                    param_position = fluent_args.index(param_name)
                                    
                                    
                                    fluent_signatures = knowledge.get('fluent_signatures', {})
                                    if fluent_name in fluent_signatures:
                                        sig = fluent_signatures[fluent_name]
                                        if param_position < len(sig) and sig[param_position] != 'Unknown':
                                            inferred_type = sig[param_position]
                                            break
                                    
                                    
                                    for i, arg in enumerate(fluent_args):
                                        if arg in type_constraints and i != param_position:
                                            
                                            
                                            pass
                    
                    if inferred_type:
                        break
                
                
                if not inferred_type:
                    param_value_str = str(param_value).lower()
                    for type_name, instances in knowledge['types'].items():
                        for instance in instances:
                            if str(instance).lower() == param_value_str:
                                inferred_type = type_name
                                break
                        if inferred_type:
                            break
                
                
                if not inferred_type:
                    if (param_value_str.isdigit() or 
                        (param_value_str.replace('-', '').replace('.', '').isdigit())):
                        inferred_type = 'pos'
                
                if inferred_type:
                    print(f"  Inferred type for {action_name}.{param_name} ({param_value}): {inferred_type}")
                    type_constraints[param_name] = inferred_type
                    
                    
                    constraint_str = f"{inferred_type}({param_name})"
                    if constraint_str not in action['type_constraints']:
                        action['type_constraints'].append(constraint_str)
        
        
        action['_type_constraint_dict'] = type_constraints
    
    return knowledge


def extract_prolog_knowledge(prolog_file):
    start_time = time.time()
    print(f"Starting extraction from Prolog file...")
    
    prolog = Prolog()
    
    prolog.consult(prolog_file)
    type_predicates = {}

    try:
        predicates_found = set()
        
        with open(prolog_file, 'r') as f:
            content = f.read()
        
        
        import re
        type_patterns = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\([^)]+\)\s*\.', content, re.MULTILINE)
        predicates_found.update(type_patterns)
        
        
        action_patterns = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\([^)]+\)', content)
        predicates_found.update([p for p in action_patterns if p not in ['action', 'add', 'del']])
        
        print(f"DEBUG: Found potential type predicates: {predicates_found}")
        
        for predicate in predicates_found:
            try:
                query_str = f"{predicate}(X)"
                print(f"DEBUG: Querying {query_str}")
                instances = list(prolog.query(query_str))
                print(f"DEBUG: Query {query_str} returned: {instances}")
                
                if instances:
                    valid_instances = []
                    for instance in instances:
                        instance_value = instance['X']
                        print(f"DEBUG: Processing instance {instance_value} of type {type(instance_value)}")
                        
                        
                        processed_value = None
                        
                        if hasattr(instance_value, 'name'):
                            
                            processed_value = str(instance_value.name)
                        elif hasattr(instance_value, 'value'):
                            
                            processed_value = str(instance_value.value)
                        elif isinstance(instance_value, str):
                            
                            processed_value = instance_value
                        elif isinstance(instance_value, (int, float)):
                            
                            processed_value = str(instance_value)
                        else:
                            
                            processed_value = str(instance_value)
                        
                        
                        if processed_value and not processed_value.startswith('_'):
                            valid_instances.append(processed_value)
                            print(f"DEBUG: Added valid instance: {processed_value}")
                    
                    if valid_instances:
                        
                        unique_instances = []
                        seen = set()
                        for item in valid_instances:
                            if item not in seen:
                                unique_instances.append(item)
                                seen.add(item)
                        
                        type_predicates[predicate] = unique_instances
                        print(f"DEBUG: Type {predicate} has instances: {unique_instances}")
                    else:
                        print(f"DEBUG: No valid instances found for {predicate}")
                else:
                    print(f"DEBUG: No instances found for {predicate}")
            except Exception as e:
                print(f"DEBUG: Error querying {predicate}: {e}")
                continue
        
        print(f"DEBUG: Final type_predicates: {type_predicates}")
                
    except Exception as e:
        print(f"Warning: General type extraction failed: {e}")
        print("Falling back to manual type detection...")
    
    
    print("DEBUG: Extracting additional types from action constraints...")
    
    try:
        
        for solution in prolog.query("action(Head, Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"):
            type_constraints = solution['TypeConstraints']
            print(f"DEBUG: Processing type constraints: {type_constraints}")
            
            for constraint in type_constraints:
                constraint_str = str(constraint)
                print(f"DEBUG: Processing constraint: {constraint_str}")
                
                
                match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\([^)]+\)', constraint_str)
                if match:
                    type_name = match.group(1)
                    print(f"DEBUG: Found type from constraint: {type_name}")
                    
                    
                    if type_name not in type_predicates:
                        try:
                            query_str = f"{type_name}(X)"
                            instances = list(prolog.query(query_str))
                            if instances:
                                valid_instances = []
                                for instance in instances:
                                    instance_value = instance['X']
                                    
                                    
                                    processed_value = None
                                    if hasattr(instance_value, 'name'):
                                        processed_value = str(instance_value.name)
                                    elif hasattr(instance_value, 'value'):
                                        processed_value = str(instance_value.value)
                                    elif isinstance(instance_value, str):
                                        processed_value = instance_value
                                    elif isinstance(instance_value, (int, float)):
                                        processed_value = str(instance_value)
                                    else:
                                        processed_value = str(instance_value)
                                    
                                    if processed_value and not processed_value.startswith('_'):
                                        valid_instances.append(processed_value)
                                
                                if valid_instances:
                                    
                                    unique_instances = []
                                    seen = set()
                                    for item in valid_instances:
                                        if item not in seen:
                                            unique_instances.append(item)
                                            seen.add(item)
                                    
                                    type_predicates[type_name] = unique_instances
                                    print(f"DEBUG: Added type {type_name} with instances: {unique_instances}")
                        except Exception as e:
                            print(f"DEBUG: Could not query type {type_name}: {e}")
                            continue
    except Exception as e:
        print(f"DEBUG: Error in additional type extraction: {e}")

    
    init_state_query = list(prolog.query("init_state(X)"))
    if init_state_query:
        init_state_list = init_state_query[0]['X']
        init_state = []
        for item in init_state_list:
            
            init_state.append(str(item))
    else:
        init_state = []
    
    
    goal_state_query = list(prolog.query("goal_state(X)"))
    if goal_state_query:
        goal_state_list = goal_state_query[0]['X']
        goal_state = []
        for item in goal_state_list:
            
            goal_state.append(str(item))
    else:
        goal_state = []
    
    
    actions = []
    try:
        
        for solution in prolog.query("action(Head, Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"):
            action_head = str(solution["Head"])
            
            
            if '(' in action_head:
                action_name = action_head.split('(')[0]
                
                
                params_match = re.match(r'[^(]+\((.*)\)', action_head)
                param_values = []
                if params_match:
                    params_str = params_match.group(1)
                    
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
                
                
                param_names = [f"Param{i+1}" for i in range(len(param_values))]
                
                
                
                param_mapping = {}
                param_order_map = {}  
                
                for idx, val in enumerate(param_values):
                    param_name = param_names[idx]
                    param_mapping[str(val)] = param_name
                    param_order_map[param_name] = idx
                
                
                def replace_params(expr, mapping, param_values_list):
                    expr_str = str(expr)
                    
                    
                    sorted_params = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)
                    
                    
                    temp_expr = expr_str
                    replacements = []
                    
                    
                    for val, name in sorted_params:
                        
                        
                        pattern = r'\b' + re.escape(val) + r'\b'
                        matches = list(re.finditer(pattern, temp_expr))
                        
                        for match in matches:
                            replacements.append((match.start(), match.end(), val, name))
                    
                    
                    replacements.sort(key=lambda x: x[0], reverse=True)
                    
                    
                    result = temp_expr
                    for start, end, val, name in replacements:
                        result = result[:start] + name + result[end:]
                    
                    return result
                
                
                processed_preconditions = []
                for precond in solution['Precond']:
                    processed_preconditions.append(replace_params(precond, param_mapping, param_values))
                
                
                processed_neg_preconditions = []
                for neg_precond in solution['NegPrecond']:
                    processed_neg_preconditions.append(replace_params(neg_precond, param_mapping, param_values))
                
                
                processed_resource_preconditions = []
                for res_precond in solution['ResourcePrecond']:
                    processed_resource_preconditions.append(replace_params(res_precond, param_mapping, param_values))
                
                
                processed_type_constraints = []
                type_constraint_dict = {}  
                
                for constraint in solution['TypeConstraints']:
                    constraint_str = str(constraint)
                    
                    
                    constraint_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)', constraint_str)
                    if constraint_match:
                        type_name = constraint_match.group(1)
                        params_in_constraint = constraint_match.group(2)
                        
                        
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
                        
                        
                        for cp in constraint_params:
                            cp_str = str(cp).strip()
                            if cp_str in param_mapping:
                                param_name = param_mapping[cp_str]
                                type_constraint_dict[param_name] = type_name
                        
                        
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
                
                
                processed_effects = []
                for effect in solution['Effects']:
                    
                    effect_str = str(effect)
                    
                    
                    if 'add(' in effect_str:
                        match = re.search(r'add\((.*?)\)', effect_str)
                        if match:
                            inner = match.group(1)
                            replaced_inner = replace_params(inner, param_mapping, param_values)
                            effect_str = effect_str.replace(match.group(0), f"add({replaced_inner})")
                    
                    
                    if 'del(' in effect_str:
                        match = re.search(r'del\((.*?)\)', effect_str)
                        if match:
                            inner = match.group(1)
                            replaced_inner = replace_params(inner, param_mapping, param_values)
                            effect_str = effect_str.replace(match.group(0), f"del({replaced_inner})")
                    
                    processed_effects.append(effect_str)
                
                
                action_info = {
                    'name': action_name,
                    'parameters': param_names,
                    'param_values': param_values,
                    'preconditions': processed_preconditions,
                    'neg_preconditions': processed_neg_preconditions,
                    'resource_preconditions': processed_resource_preconditions,
                    'type_constraints': processed_type_constraints,
                    'effects': processed_effects,
                    
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
                        valid_instances = []
                        for instance in instances:
                            instance_value = instance['X']
                            
                            
                            processed_value = None
                            if hasattr(instance_value, 'name'):
                                processed_value = str(instance_value.name)
                            elif hasattr(instance_value, 'value'):
                                processed_value = str(instance_value.value)
                            elif isinstance(instance_value, str):
                                processed_value = instance_value
                            elif isinstance(instance_value, (int, float)):
                                processed_value = str(instance_value)
                            else:
                                processed_value = str(instance_value)
                            
                            if processed_value and not processed_value.startswith('_'):
                                valid_instances.append(processed_value)
                        
                        if valid_instances:
                            
                            unique_instances = []
                            seen = set()
                            for item in valid_instances:
                                if item not in seen:
                                    unique_instances.append(item)
                                    seen.add(item)
                            
                            type_predicates[pred_name] = unique_instances
                            print(f"DEBUG: Added type {pred_name} from action constraints: {unique_instances}")
                except Exception:
                    
                    pass
    
    
    knowledge = {
        'types': type_predicates,  
        'init_state': init_state,
        'goal_state': goal_state,
        'actions': actions
    }
    
    
    fluent_names = set()
    
    
    for state in init_state:
        fluent_name = state.split('(')[0]
        fluent_names.add(fluent_name)
    
    
    for state in goal_state:
        fluent_name = state.split('(')[0]
        fluent_names.add(fluent_name)
    
    
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
    fluent_signatures = {}
    
    
    object_to_type = {}
    for type_name, instances in knowledge['types'].items():
        for instance in instances:
            object_to_type[str(instance)] = type_name
    
    
    
    fluent_usage = {}  
    
    def extract_param_types_from_action(fluent_str, action):
        match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_str)
        if not match:
            return []
        
        fluent_name = match.group(1)
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(',')]
        
        param_types = []
        
        
        type_constraint_dict = action.get('_type_constraint_dict', {})
        
        
        action_type_constraints = action.get('type_constraints', [])
        param_to_type = {}
        
        for constraint in action_type_constraints:
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
        
        for param in params:
            
            if param in type_constraint_dict:
                param_types.append(type_constraint_dict[param])
            
            elif param in param_to_type:
                param_types.append(param_to_type[param])
            
            elif param in object_to_type:
                param_types.append(object_to_type[param])
            
            elif param.isdigit() or (param.replace('-', '').replace('.', '').isdigit()):
                param_types.append('pos')
            
            elif param.startswith('_'):
                param_types.append('wildcard')
            else:
                param_types.append('Unknown')
        
        return param_types
    
    
    for fluent_name in knowledge['fluent_names']:
        if fluent_name not in fluent_usage:
            fluent_usage[fluent_name] = []
        
        
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
                        
                        fluent_usage[fluent_name].append((param_types, 100, state_name))
        
        
        for action in knowledge['actions']:
            action_score = len(action.get('type_constraints', []))
            
            
            for precond in action['preconditions']:
                if precond.startswith(fluent_name + '('):
                    param_types = extract_param_types_from_action(precond, action)
                    if param_types:
                        fluent_usage[fluent_name].append((param_types, action_score, action['name']))
            
            
            for effect in action['effects']:
                if 'add(' in effect or 'del(' in effect:
                    match = re.search(r'add\((.*?)\)', effect) or re.search(r'del\((.*?)\)', effect)
                    if match and match.group(1).startswith(fluent_name + '('):
                        param_types = extract_param_types_from_action(match.group(1), action)
                        if param_types:
                            fluent_usage[fluent_name].append((param_types, action_score, action['name']))
    
    
    for fluent_name, usage_list in fluent_usage.items():
        if not usage_list:
            continue
        
        
        usage_list.sort(key=lambda x: x[1], reverse=True)
        
        
        lengths = [len(usage[0]) for usage in usage_list]
        if not lengths:
            continue
            
        most_common_length = max(set(lengths), key=lengths.count)
        
        
        filtered_usage = [usage for usage in usage_list if len(usage[0]) == most_common_length]
        
        
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
            
            
            if types_at_position:
                
                known_types = [t for t in types_at_position if t not in ['wildcard', 'Unknown']]
                
                if known_types:
                    
                    best_type = max(known_types, key=lambda t: scores_for_types.get(t, 0))
                    final_signature.append(best_type)
                else:
                    final_signature.append('Unknown')
            else:
                final_signature.append('Unknown')
        
        fluent_signatures[fluent_name] = final_signature
    
    
    fluent_signatures = _resolve_unknowns_across_actions(fluent_signatures, knowledge)
    
    return fluent_signatures

def _resolve_unknowns_across_actions(fluent_signatures, knowledge):
    
    
    param_usage_patterns = {}  
    
    for action in knowledge['actions']:
        
        type_constraint_dict = action.get('_type_constraint_dict', {})
        
        
        if not type_constraint_dict:
            type_constraints = action.get('type_constraints', [])
            
            
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
    
    
    for fluent_name, signature in fluent_signatures.items():
        for pos, param_type in enumerate(signature):
            if param_type == 'Unknown':
                
                candidate_types = set()
                
                for param_name, usage_pattern in param_usage_patterns.items():
                    if fluent_name in usage_pattern and pos in usage_pattern[fluent_name]:
                        candidate_types.add(usage_pattern[fluent_name][pos])
                
                if len(candidate_types) == 1:
                    signature[pos] = list(candidate_types)[0]
                elif candidate_types:
                    
                    type_counts = {}
                    for ctype in candidate_types:
                        type_counts[ctype] = type_counts.get(ctype, 0) + 1
                    signature[pos] = max(type_counts.items(), key=lambda x: x[1])[0]
    
    return fluent_signatures


def print_knowledge_summary(knowledge, fluent_signatures):
    print(f"\nExtracted knowledge summary:")
    print(f"  Types and objects:")
    for type_name, instances in knowledge['types'].items():
        print(f"    {type_name}: {instances}")
    print(f"  Fluents: {knowledge['fluent_names']}")
    print(f"  Initial state has {len(knowledge['init_state'])} assertions")
    print(f"  Goal state has {len(knowledge['goal_state'])} assertions")
    print(f"  Found {len(knowledge['actions'])} actions")
    
    
    print(f"\nInitial State:")
    for state in knowledge['init_state']:
        print(f"  {state}")
    
    print(f"\nGoal State:")
    for state in knowledge['goal_state']:
        print(f"  {state}")
    
    
    print(f"\nFluent signatures:")
    for fluent_name, param_types in fluent_signatures.items():
        print(f"  {fluent_name}: {param_types}")
    
    
    print(f"\nActions details:")
    
    sorted_actions = sorted(knowledge['actions'], key=lambda x: x['name'])
    
    for i, action in enumerate(sorted_actions, 1):
        print(f"\n  Action {i}: {action['name']}")
        
        
        params = []
        for param_name, param_value in zip(action['parameters'], action['param_values']):
            
            if param_name.startswith('_'):
                continue
            
            if str(param_value) != '_':
                params.append(f"{param_name} ({param_value})")
            else:
                params.append(param_name)
        
        print(f"    Parameters: {', '.join(params)}")
        
        
        if '_type_constraint_dict' in action:
            print(f"    Type mapping: {action['_type_constraint_dict']}")
        
        
        param_mapping = {}
        for param_name, param_value in zip(action['parameters'], action['param_values']):
            param_mapping[str(param_value)] = param_name
        
        def replace_vars(text):
            
            for var, name in param_mapping.items():
                
                text = text.replace(var + ')', name + ')')
                text = text.replace(var + ',', name + ',')
                
                
                text = text.replace(', ' + var, ', ' + name)
                
                
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
                
                inner = effect.split('add(')[1].rsplit(')', 1)[0]
                print(f"      + {replace_vars(inner)}")
        
        if effects_del:
            print(f"    Delete Effects:")
            for effect in effects_del:
                
                inner = effect.split('del(')[1].rsplit(')', 1)[0]
                print(f"      - {replace_vars(inner)}")