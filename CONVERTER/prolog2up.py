import time
import re
from pyswip import Prolog
import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter

def extract_prolog_knowledge(prolog_file):
    """Extract knowledge from Prolog file using PySwip without making assumptions about names"""
    start_time = time.time()
    print(f"Starting extraction from Prolog file...")
    
    # Initialize Prolog engine
    prolog = Prolog()
    
    # Load the Prolog file
    prolog.consult(prolog_file)
    
    # Extract all predicates that could define types (unary predicates)
    type_predicates = {}
    
    # Extract types directly from the file content instead of querying all predicates
    # This avoids attempting to query system predicates that cause warnings
    
    # First, check for direct type declarations in the file (e.g., block(b1).)
    for predicate in ["block", "agent", "mela", "pos"]:  # Add known type predicates here
        try:
            instances = list(prolog.query(f"{predicate}(X)"))
            if instances:
                type_predicates[predicate] = [i['X'] for i in instances]
        except Exception as e:
            # Silently ignore errors for predicates that don't exist
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
                
                # Create action info dictionary
                action_info = {
                    'name': action_name,
                    'parameters': [f"Param{i+1}" for i in range(len(param_values))],
                    'param_values': param_values,
                    'preconditions': [str(p) for p in solution['Precond']],
                    'neg_preconditions': [str(p) for p in solution['NegPrecond']],
                    'resource_preconditions': [str(p) for p in solution['ResourcePrecond']],
                    'type_constraints': [str(c) for c in solution['TypeConstraints']],
                    'effects': [str(e) for e in solution['Effects']]
                }
                actions.append(action_info)
            else:
                print(f"Warning: Invalid action head format: {action_head}")
    except Exception as e:
        print(f"Warning: Could not extract actions directly: {e}")
        print("Attempting alternative action extraction method...")
        try:
            # Get all action heads first (more manual approach)
            with open(prolog_file, 'r') as f:
                content = f.read()
            
            # Look for action definitions in the file content
            action_pattern = r'action\(([^,]+)'
            action_heads = re.findall(action_pattern, content)
            
            for action_head in action_heads:
                action_head = action_head.strip()
                if '(' in action_head:
                    action_name = action_head.split('(')[0]
                    
                    # Try to query this specific action using its head
                    try:
                        query = f"action({action_head}, P, N, R, T, E)"
                        solutions = list(prolog.query(query))
                        
                        if solutions:
                            solution = solutions[0]
                            
                            # Extract parameters from head
                            params_match = re.match(r'[^(]+\((.*)\)', action_head)
                            param_values = []
                            if params_match:
                                params_str = params_match.group(1)
                                param_values = [p.strip() for p in params_str.split(',')]
                            
                            action_info = {
                                'name': action_name,
                                'parameters': [f"Param{i+1}" for i in range(len(param_values))],
                                'param_values': param_values,
                                'preconditions': [str(p) for p in solution['P']],
                                'neg_preconditions': [str(p) for p in solution['N']],
                                'resource_preconditions': [str(p) for p in solution['R']],
                                'type_constraints': [str(c) for c in solution['T']],
                                'effects': [str(e) for e in solution['E']]
                            }
                            actions.append(action_info)
                    except Exception as inner_e:
                        print(f"Warning: Failed to query action {action_head}: {inner_e}")
        except Exception as alt_e:
            print(f"Warning: Alternative action extraction failed: {alt_e}")
    
    # Also extract type information from type constraints in actions
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
    
    # Extract actions in a more flexible way
    actions = []
    # Find all action templates without assumptions about their names
    action_templates = list(prolog.query("clause(action(Template, _, _, _, _, _), _)"))
    
    for template in action_templates:
        action_template = template['Template']
        action_name = str(action_template).split('(')[0]
        
        # Count parameters by analyzing the template structure
        param_count = len(str(action_template).split(',')) if '(' in str(action_template) else 0
        
        # Create a general query structure with the right number of variables
        query_params = ", ".join([f"P{i}" for i in range(param_count)])
        action_query = f"action({action_name}({query_params}), Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"
        
        try:
            # Query for actions with this specific template
            for solution in prolog.query(action_query):
                param_values = [solution[f"P{i}"] for i in range(param_count)]
                
                action_info = {
                    'name': action_name,
                    'parameters': [f"Param{i+1}" for i in range(param_count)],  # Generic parameter names
                    'param_values': param_values,
                    'preconditions': [str(p) for p in solution['Precond']],
                    'neg_preconditions': [str(p) for p in solution['NegPrecond']],
                    'resource_preconditions': [str(p) for p in solution['ResourcePrecond']],
                    'type_constraints': [str(c) for c in solution['TypeConstraints']],
                    'effects': [str(e) for e in solution['Effects']]
                }
                actions.append(action_info)
        except Exception as e:
            print(f"Warning: Error querying action {action_name}: {e}")
    
    extraction_time = time.time() - start_time
    print(f"Extraction completed in {extraction_time:.4f} seconds")
    
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

def create_up_problem(knowledge, fluent_signatures):
    """Create a unified_planning Problem from extracted knowledge without name assumptions"""
    start_time = time.time()
    print(f"\nCreating Unified Planning problem...")
    
    # Create Problem
    problem = Problem('extracted_domain')
    
    # Define types dynamically based on extracted knowledge
    up_types = {}
    for type_name in knowledge['types'].keys():
        # Capitalize the type name for UP convention
        up_type_name = type_name.capitalize()
        up_types[type_name] = UserType(up_type_name)
    
    # Ensure we have at least these basic types
    if 'Location' not in up_types:
        up_types['Location'] = UserType('Location')
    if 'Generic' not in up_types:
        up_types['Generic'] = UserType('Generic')
    
    # Create fluents
    fluents = {}
    for fluent_name, param_types in fluent_signatures.items():
        # Map parameter types to UP types
        up_param_types = []
        param_names = []
        
        for i, param_type in enumerate(param_types):
            # Convert to proper UP type, use the extracted type if available
            if param_type in up_types:
                up_param_types.append(up_types[param_type])
                param_names.append(f'{param_type[0].lower()}{i+1}')  # e.g., b1 for block1
            elif param_type == 'Location' and 'Location' in up_types:
                up_param_types.append(up_types['Location'])
                param_names.append(f'l{i+1}')
            else:
                # Use a generic type if we can't determine it
                up_param_types.append(up_types['Generic'])
                param_names.append(f'x{i+1}')
        
        # Create fluent with appropriate parameters
        param_dict = {name: type for name, type in zip(param_names, up_param_types)}
        
        try:
            fluent = Fluent(fluent_name, BoolType(), **param_dict)
            fluents[fluent_name] = fluent
            problem.add_fluent(fluent, default_initial_value=False)
        except Exception as e:
            print(f"Warning: Could not create fluent {fluent_name} with parameters {param_dict}: {e}")
            # Try creating with a simplified signature
            if fluent_name.startswith('moving_'):
                try:
                    # Create a simplified version with generic parameters
                    simplified_params = {}
                    for i in range(len(param_types)):
                        simplified_params[f'p{i}'] = up_types.get('Generic', UserType('Generic'))
                    
                    fluent = Fluent(fluent_name, BoolType(), **simplified_params)
                    fluents[fluent_name] = fluent
                    problem.add_fluent(fluent, default_initial_value=False)
                    print(f"Created simplified fluent {fluent_name} instead")
                except Exception as inner_e:
                    print(f"Warning: Could not create simplified fluent {fluent_name}: {inner_e}")
    
    # Create objects for each type
    objects_by_type = {}
    for type_name, instances in knowledge['types'].items():
        if type_name in up_types:
            type_objects = [Object(str(instance), up_types[type_name]) for instance in instances]
            objects_by_type[type_name] = type_objects
            problem.add_objects(type_objects)
    
    # Create location objects (if needed)
    locations = set()
    location_objects = []
    
    # Extract location values from init_state and goal_state
    for state in knowledge['init_state'] + knowledge['goal_state']:
        if 'at' in state:
            # Attempt to extract location coordinates
            match = re.match(r'at\([^,]+,\s*(\d+),\s*(\d+)\)', state)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                locations.add((x, y))
    
    # Create location objects
    loc_dict = {}  # (x,y) -> loc_x_y object
    for x, y in locations:
        loc_name = f"loc_{x}_{y}"
        if 'Location' in up_types:
            l = Object(loc_name, up_types['Location'])
            location_objects.append(l)
            loc_dict[(x, y)] = l
    
    if location_objects:
        problem.add_objects(location_objects)
        if 'Location' not in objects_by_type:
            objects_by_type['Location'] = []
        objects_by_type['Location'].extend(location_objects)
    
    # Create a mapping for objects
    object_dict = {}
    for type_objs in objects_by_type.values():
        for obj in type_objs:
            object_dict[obj.name] = obj
    
    # Add location objects to object_dict
    for coord, obj in loc_dict.items():
        object_dict[coord] = obj
    
    # Set initial state
    for state in knowledge['init_state']:
        match = re.match(r'([a-zA-Z_]+)\((.*?)\)', state)
        if not match:
            continue
        
        fluent_name = match.group(1)
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(',')]
        
        if fluent_name not in fluents:
            continue
        
        # Handle different fluent types based on parameter count and name
        if fluent_name == 'at' and len(params) == 3:
            # Special case for at(object, x, y)
            obj_name = params[0]
            x, y = int(params[1]), int(params[2])
            
            if obj_name in object_dict and (x, y) in loc_dict:
                try:
                    problem.set_initial_value(fluents[fluent_name](object_dict[obj_name], loc_dict[(x, y)], loc_dict[(x, y)]), True)
                except Exception as e:
                    print(f"Warning: Could not set initial value for {fluent_name}({obj_name}, {x}, {y}): {e}")
        elif fluent_name in ['intera', 'morsa'] and len(params) == 1:
            # Special case for mela predicates
            mela_name = params[0]
            if mela_name in object_dict:
                try:
                    problem.set_initial_value(fluents[fluent_name](object_dict[mela_name]), True)
                except Exception as e:
                    print(f"Warning: Could not set initial value for {fluent_name}({mela_name}): {e}")
        elif all(p in object_dict for p in params):
            # Regular case where all parameters are objects
            try:
                problem.set_initial_value(fluents[fluent_name](*[object_dict[p] for p in params]), True)
            except Exception as e:
                print(f"Warning: Could not set initial value for {fluent_name}({', '.join(params)}): {e}")
    
    # Set goal state
    for state in knowledge['goal_state']:
        match = re.match(r'([a-zA-Z_]+)\((.*?)\)', state)
        if not match:
            continue
        
        fluent_name = match.group(1)
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(',')]
        
        if fluent_name not in fluents:
            continue
        
        # Handle different fluent types based on parameter count and name
        if fluent_name == 'at' and len(params) == 3:
            # Special case for at(object, x, y)
            obj_name = params[0]
            x, y = int(params[1]), int(params[2])
            
            if obj_name in object_dict and (x, y) in loc_dict:
                try:
                    problem.add_goal(fluents[fluent_name](object_dict[obj_name], loc_dict[(x, y)], loc_dict[(x, y)]))
                except Exception as e:
                    print(f"Warning: Could not add goal for {fluent_name}({obj_name}, {x}, {y}): {e}")
        elif fluent_name in ['intera', 'morsa'] and len(params) == 1:
            # Special case for mela predicates
            mela_name = params[0]
            if mela_name in object_dict:
                try:
                    problem.add_goal(fluents[fluent_name](object_dict[mela_name]))
                except Exception as e:
                    print(f"Warning: Could not add goal for {fluent_name}({mela_name}): {e}")
        elif all(p in object_dict for p in params):
            # Regular case where all parameters are objects
            try:
                problem.add_goal(fluents[fluent_name](*[object_dict[p] for p in params]))
            except Exception as e:
                print(f"Warning: Could not add goal for {fluent_name}({', '.join(params)}): {e}")
    
    # Process actions
    print(f"Number of actions to process: {len(knowledge['actions'])}")
    for action_info in knowledge['actions']:
        action_name = action_info['name']
        
        print(f"Processing action: {action_name}")
        
        # Extract parameter types from type constraints
        param_types = {}
        for constraint in action_info['type_constraints']:
            match = re.match(r'([a-zA-Z_]+)\((.*?)\)', constraint)
            if match:
                type_name = match.group(1)
                param_name = match.group(2)
                if type_name in up_types:
                    param_types[param_name] = up_types[type_name]
        
        # Create a map of parameter names to UP types
        action_params = {}
        for i, param_name in enumerate(action_info['param_values']):
            param_str = str(param_name)
            if param_str in param_types:
                action_params[f'p{i}'] = param_types[param_str]
            else:
                # If we can't determine the type, use generic
                action_params[f'p{i}'] = up_types['Generic']
        
        try:
            # Create the action with the determined parameter types
            action = InstantaneousAction(action_name, **action_params)
            
            # Get parameter objects for convenience
            param_objs = {name: action.parameter(name) for name in action_params.keys()}
            
            # Helper to find the parameter object for a given parameter name
            def get_param_obj(param_name):
                for i, orig_param in enumerate(action_info['param_values']):
                    if str(orig_param) == param_name:
                        return param_objs.get(f'p{i}')
                return None
            
            # Add preconditions
            for precond in action_info['preconditions']:
                match = re.match(r'([a-zA-Z_]+)\((.*?)\)', precond)
                if not match:
                    continue
                
                fluent_name = match.group(1)
                params = [p.strip() for p in match.group(2).split(',')]
                
                if fluent_name not in fluents:
                    print(f"Warning: Fluent {fluent_name} not found for precondition in action {action_name}")
                    continue
                
                # Map parameters from action to fluent parameters
                mapped_params = []
                for param in params:
                    param_obj = get_param_obj(param)
                    if param_obj:
                        mapped_params.append(param_obj)
                
                # Special case for moving_table_to_block fluent
                if fluent_name.startswith('moving_') and len(mapped_params) == len(params):
                    try:
                        action.add_precondition(fluents[fluent_name](*mapped_params))
                    except Exception as e:
                        print(f"Warning: Could not add precondition {fluent_name}({', '.join(params)}) to action {action_name}: {e}")
                elif fluent_name == 'at' and len(params) == 3:
                    # Special case for at(object, x, y)
                    obj_param = get_param_obj(params[0])
                    x_param, y_param = params[1], params[2]
                    
                    # Check if x, y are numeric or parameters
                    if x_param.isdigit() and y_param.isdigit():
                        # Fixed locations
                        x, y = int(x_param), int(y_param)
                        if (x, y) in loc_dict and obj_param:
                            try:
                                action.add_precondition(fluents[fluent_name](obj_param, loc_dict[(x, y)], loc_dict[(x, y)]))
                            except Exception as e:
                                print(f"Warning: Could not add at precondition with fixed location: {e}")
                    else:
                        # Parameters that refer to locations
                        x_obj = get_param_obj(x_param)
                        y_obj = get_param_obj(y_param)
                        
                        if obj_param and x_obj and y_obj:
                            try:
                                action.add_precondition(fluents[fluent_name](obj_param, x_obj, y_obj))
                            except Exception as e:
                                print(f"Warning: Could not add at precondition with param location: {e}")
                elif len(mapped_params) == len(params):
                    # Only add precondition if we have all parameters mapped
                    try:
                        action.add_precondition(fluents[fluent_name](*mapped_params))
                    except Exception as e:
                        print(f"Warning: Could not add standard precondition {fluent_name}({', '.join(params)}) to action {action_name}: {e}")
            
            # Add negative preconditions
            for neg_precond in action_info['neg_preconditions']:
                # If it's an explicit negation of a fluent
                match = re.match(r'([a-zA-Z_]+)\((.*?)\)', neg_precond)
                if match:
                    fluent_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(',')]
                    
                    if fluent_name not in fluents:
                        print(f"Warning: Fluent {fluent_name} not found for negative precondition in action {action_name}")
                        continue
                    
                    # Map parameters from action to fluent parameters
                    mapped_params = []
                    for param in params:
                        param_obj = get_param_obj(param)
                        if param_obj:
                            mapped_params.append(param_obj)
                    
                    # Add negated precondition if all parameters are mapped
                    if len(mapped_params) == len(params):
                        try:
                            action.add_precondition(Not(fluents[fluent_name](*mapped_params)))
                        except Exception as e:
                            print(f"Warning: Could not add negative precondition: {e}")
            
            # Add effects
            for effect in action_info['effects']:
                if 'add(' in effect:
                    # Add effect
                    match = re.search(r'add\((.*?)\)', effect)
                    if not match:
                        continue
                    
                    fluent_expr = match.group(1)
                    match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_expr)
                    if not match:
                        continue
                    
                    fluent_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(',')]
                    
                    if fluent_name not in fluents:
                        print(f"Warning: Fluent {fluent_name} not found for add effect in action {action_name}")
                        continue
                    
                    # Map parameters from action to fluent parameters
                    mapped_params = []
                    for param in params:
                        param_obj = get_param_obj(param)
                        if param_obj:
                            mapped_params.append(param_obj)
                    
                    # Special case for moving_table_to_block fluent
                    if fluent_name.startswith('moving_') and len(mapped_params) == len(params):
                        try:
                            action.add_effect(fluents[fluent_name](*mapped_params), True)
                        except Exception as e:
                            print(f"Warning: Could not add effect {fluent_name}: {e}")
                    elif fluent_name == 'at' and len(params) == 3:
                        # Special case for at(object, x, y)
                        obj_param = get_param_obj(params[0])
                        x_param, y_param = params[1], params[2]
                        
                        if x_param.isdigit() and y_param.isdigit():
                            # Fixed locations
                            x, y = int(x_param), int(y_param)
                            if (x, y) in loc_dict and obj_param:
                                try:
                                    action.add_effect(fluents[fluent_name](obj_param, loc_dict[(x, y)], loc_dict[(x, y)]), True)
                                except Exception as e:
                                    print(f"Warning: Could not add at effect with fixed location: {e}")
                        else:
                            # Parameters that refer to locations
                            x_obj = get_param_obj(x_param)
                            y_obj = get_param_obj(y_param)
                            
                            if obj_param and x_obj and y_obj:
                                try:
                                    action.add_effect(fluents[fluent_name](obj_param, x_obj, y_obj), True)
                                except Exception as e:
                                    print(f"Warning: Could not add at effect with param location: {e}")
                    elif len(mapped_params) == len(params):
                        # Add effect if all parameters are mapped
                        try:
                            action.add_effect(fluents[fluent_name](*mapped_params), True)
                        except Exception as e:
                            print(f"Warning: Could not add standard effect {fluent_name}: {e}")
                
                elif 'del(' in effect:
                    # Delete effect
                    match = re.search(r'del\((.*?)\)', effect)
                    if not match:
                        continue
                    
                    fluent_expr = match.group(1)
                    match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_expr)
                    if not match:
                        continue
                    
                    fluent_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(',')]
                    
                    if fluent_name not in fluents:
                        print(f"Warning: Fluent {fluent_name} not found for del effect in action {action_name}")
                        continue
                    
                    # Map parameters from action to fluent parameters
                    mapped_params = []
                    for param in params:
                        param_obj = get_param_obj(param)
                        if param_obj:
                            mapped_params.append(param_obj)
                    
                    # Special cases for specific fluents
                    if fluent_name.startswith('moving_') and len(mapped_params) == len(params):
                        try:
                            action.add_effect(fluents[fluent_name](*mapped_params), False)
                        except Exception as e:
                            print(f"Warning: Could not add delete effect {fluent_name}: {e}")
                    elif fluent_name == 'at' and len(params) == 3:
                        # Special case for at(object, x, y)
                        obj_param = get_param_obj(params[0])
                        x_param, y_param = params[1], params[2]
                        
                        if x_param.isdigit() and y_param.isdigit():
                            # Fixed locations
                            x, y = int(x_param), int(y_param)
                            if (x, y) in loc_dict and obj_param:
                                try:
                                    action.add_effect(fluents[fluent_name](obj_param, loc_dict[(x, y)], loc_dict[(x, y)]), False)
                                except Exception as e:
                                    print(f"Warning: Could not add at delete effect with fixed location: {e}")
                        else:
                            # Parameters that refer to locations
                            x_obj = get_param_obj(x_param)
                            y_obj = get_param_obj(y_param)
                            
                            if obj_param and x_obj and y_obj:
                                try:
                                    action.add_effect(fluents[fluent_name](obj_param, x_obj, y_obj), False)
                                except Exception as e:
                                    print(f"Warning: Could not add at delete effect with param location: {e}")
                    elif len(mapped_params) == len(params):
                        # Add delete effect if all parameters are mapped
                        try:
                            action.add_effect(fluents[fluent_name](*mapped_params), False)
                        except Exception as e:
                            print(f"Warning: Could not add standard delete effect {fluent_name}: {e}")
            
            # Add action to problem
            problem.add_action(action)
        except Exception as e:
            print(f"Warning: Failed to create action {action_name}: {e}")
    
    up_creation_time = time.time() - start_time
    print(f"Unified Planning problem created in {up_creation_time:.4f} seconds")
    
    return problem

def main(prolog_file, pddl_output_file=None):
    """Main function to convert Prolog KB to UP and then to PDDL"""
    total_start_time = time.time()
    
    # Extract knowledge from Prolog
    knowledge = extract_prolog_knowledge(prolog_file)
    
    # Print extracted knowledge summary
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
    
    # Analyze fluent signatures
    fluent_signatures = analyze_fluent_signatures(knowledge)
    print(f"\nFluent signatures:")
    for fluent_name, param_types in fluent_signatures.items():
        print(f"  {fluent_name}: {param_types}")
    
    # Create UP problem
    problem = create_up_problem(knowledge, fluent_signatures)
    
    print(f"\nUnified Planning problem details:")
    print(problem)
    
    # Generate PDDL if output file specified
    if pddl_output_file:
        try:
            writer = PDDLWriter(problem)
            
            # Ensure the directory exists
            import os
            os.makedirs("RESULTS/CONVERTER", exist_ok=True)
            
            domain_path = "RESULTS/CONVERTER/" + pddl_output_file + "_domain.pddl"
            problem_path = "RESULTS/CONVERTER/" + pddl_output_file + "_problem.pddl"
            
            writer.write_domain(domain_path)
            writer.write_problem(problem_path)
            
            print(f"\nPDDL files written to {pddl_output_file}_domain.pddl and {pddl_output_file}_problem.pddl")
            
            # Print PDDL content for verification
            print("\nGenerated PDDL Domain File Content:")
            with open(domain_path, 'r') as f:
                domain_content = f.read()
                print(domain_content[:500] + "..." if len(domain_content) > 500 else domain_content)
            
            print("\nGenerated PDDL Problem File Content:")
            with open(problem_path, 'r') as f:
                problem_content = f.read()
                print(problem_content[:500] + "..." if len(problem_content) > 500 else problem_content)
        except Exception as e:
            print(f"Error writing PDDL files: {e}")
    
    total_time = time.time() - total_start_time
    print(f"\nTotal conversion time: {total_time:.4f} seconds")
    
    return problem

if __name__ == "__main__":
    # Example usage
    prolog_file = "simple_blocks.pl"
    pddl_output = "simple_blocks"
    
    # Run conversion
    problem = main(prolog_file, pddl_output)
    print("\nConversion completed successfully!")