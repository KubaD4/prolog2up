import time
import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter

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
    
    # Handle moving_* fluents first with simple parameter structure
    for fluent_name in knowledge['fluent_names']:
        if fluent_name.startswith('moving_'):
            # Always create moving fluents with generic parameters for flexibility
            try:
                param_count = 7  # Most moving fluents have 7 parameters
                if fluent_name == 'moving_table_to_table' or fluent_name == 'moving_onblock_to_table':
                    param_count = 6
                
                param_dict = {}
                for i in range(param_count):
                    param_dict[f'p{i}'] = up_types.get('Generic', UserType('Generic'))
                
                fluent = Fluent(fluent_name, BoolType(), **param_dict)
                fluents[fluent_name] = fluent
                problem.add_fluent(fluent, default_initial_value=False)
                print(f"Created generic fluent {fluent_name} with {param_count} parameters")
            except Exception as e:
                print(f"Warning: Could not create generic moving fluent {fluent_name}: {e}")
    
    # Create the rest of the fluents
    for fluent_name, param_types in fluent_signatures.items():
        # Skip fluents we've already created
        if fluent_name in fluents:
            continue
            
        # Handle at fluent specially due to its peculiar structure
        if fluent_name == 'at':
            try:
                # Create a simpler version with just block and location
                fluent = Fluent('at', BoolType(), b=up_types.get('block', UserType('Block')), l=up_types.get('Location', UserType('Location')))
                fluents[fluent_name] = fluent
                problem.add_fluent(fluent, default_initial_value=False)
                print(f"Created simplified at fluent")
                continue
            except Exception as e:
                print(f"Warning: Could not create simplified at fluent: {e}")
                # Fall through to normal creation
        
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
        
        try:
            # Create fluent with appropriate parameters
            param_dict = {name: type for name, type in zip(param_names, up_param_types)}
            fluent = Fluent(fluent_name, BoolType(), **param_dict)
            fluents[fluent_name] = fluent
            problem.add_fluent(fluent, default_initial_value=False)
        except Exception as e:
            print(f"Warning: Could not create fluent {fluent_name} with parameters {param_dict}: {e}")
            # Try creating a simplified version with generic parameters
            try:
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
    import re
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
                    # Try simplified at(block, location)
                    problem.set_initial_value(fluents[fluent_name](object_dict[obj_name], loc_dict[(x, y)]), True)
                except Exception as e:
                    print(f"Warning: Could not set initial value for {fluent_name}({obj_name}, {x}, {y}): {e}")
        elif len(params) == 1 and params[0] in object_dict:
            # Simple unary predicate like intera(m1)
            try:
                problem.set_initial_value(fluents[fluent_name](object_dict[params[0]]), True)
            except Exception as e:
                print(f"Warning: Could not set initial value for {fluent_name}({params[0]}): {e}")
        elif len(params) == 2 and all(p in object_dict for p in params):
            # Binary predicate like on(b1, b2)
            try:
                problem.set_initial_value(fluents[fluent_name](object_dict[params[0]], object_dict[params[1]]), True)
            except Exception as e:
                print(f"Warning: Could not set initial value for {fluent_name}({params[0]}, {params[1]}): {e}")
    
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
                    # Try simplified at(block, location)
                    problem.add_goal(fluents[fluent_name](object_dict[obj_name], loc_dict[(x, y)]))
                except Exception as e:
                    print(f"Warning: Could not add goal for {fluent_name}({obj_name}, {x}, {y}): {e}")
        elif len(params) == 1 and params[0] in object_dict:
            # Simple unary predicate like morsa(m1)
            try:
                problem.add_goal(fluents[fluent_name](object_dict[params[0]]))
            except Exception as e:
                print(f"Warning: Could not add goal for {fluent_name}({params[0]}): {e}")
        elif len(params) == 2 and all(p in object_dict for p in params):
            # Binary predicate like on(b1, b2)
            try:
                problem.add_goal(fluents[fluent_name](object_dict[params[0]], object_dict[params[1]]))
            except Exception as e:
                print(f"Warning: Could not add goal for {fluent_name}({params[0]}, {params[1]}): {e}")
    
    # Process actions
    print(f"Number of actions to process: {len(knowledge['actions'])}")
    for action_info in knowledge['actions']:
        action_name = action_info['name']
        
        print(f"\nProcessing action: {action_name}")
        print(f"  Parameters: {action_info['parameters']}")
        
        # Extract parameter types from type constraints
        param_types = {}
        for constraint in action_info['type_constraints']:
            match = re.match(r'([a-zA-Z_]+)\((.*?)\)', constraint)
            if match:
                type_name = match.group(1)
                param_name = match.group(2)
                if type_name in up_types:
                    param_types[param_name] = up_types[type_name]
        
        print(f"  Parameter types: {param_types}")
        
        # Create a map of parameter names to UP types
        action_params = {}
        for i, param_name in enumerate(action_info['parameters']):
            if param_name in param_types:
                action_params[f'p{i}'] = param_types[param_name]
            else:
                # If we can't determine the type, use generic
                action_params[f'p{i}'] = up_types['Generic']
        
        print(f"  Action parameters: {action_params}")
        
        try:
            # Create the action with the determined parameter types
            action = InstantaneousAction(action_name, **action_params)
            
            # Add preconditions
            for precond in action_info['preconditions']:
                match = re.match(r'([a-zA-Z_]+)\((.*?)\)', precond)
                if not match:
                    print(f"  Could not match precondition: {precond}")
                    continue
                
                fluent_name = match.group(1)
                params = [p.strip() for p in match.group(2).split(',')]
                
                if fluent_name not in fluents:
                    print(f"  Warning: Fluent {fluent_name} not found for precondition")
                    continue
                
                # Map 'Param1' to index 0, 'Param2' to index 1, etc.
                param_indices = []
                for param in params:
                    if param.startswith('Param'):
                        try:
                            idx = int(param[5:]) - 1  # Convert Param1 -> 0, Param2 -> 1, etc.
                            param_indices.append(idx)
                        except ValueError:
                            print(f"  Warning: Could not parse parameter index from {param}")
                    else:
                        print(f"  Warning: Parameter not in expected format: {param}")
                
                if len(param_indices) == 1:
                    print(f"  Adding precondition: {fluent_name}(p{param_indices[0]})")
                    action.add_precondition(fluents[fluent_name](action.parameter(f'p{param_indices[0]}')))
                elif len(param_indices) == 2:
                    print(f"  Adding precondition: {fluent_name}(p{param_indices[0]}, p{param_indices[1]})")
                    action.add_precondition(fluents[fluent_name](
                        action.parameter(f'p{param_indices[0]}'), 
                        action.parameter(f'p{param_indices[1]}')))
            
            # Add effects
            for effect in action_info['effects']:
                # Process add effects
                if 'add(' in effect:
                    add_match = re.search(r'add\((.*?)\)', effect)
                    if add_match:
                        add_expr = add_match.group(1)
                        inner_match = re.match(r'([a-zA-Z_]+)\((.*?)\)', add_expr)
                        if inner_match:
                            fluent_name = inner_match.group(1)
                            params = [p.strip() for p in inner_match.group(2).split(',')]
                            
                            if fluent_name not in fluents:
                                print(f"  Warning: Fluent {fluent_name} not found for add effect")
                                continue
                            
                            # Map 'Param1' to index 0, 'Param2' to index 1, etc.
                            param_indices = []
                            for param in params:
                                if param.startswith('Param'):
                                    try:
                                        idx = int(param[5:]) - 1  # Convert Param1 -> 0, Param2 -> 1, etc.
                                        param_indices.append(idx)
                                    except ValueError:
                                        print(f"  Warning: Could not parse parameter index from {param}")
                                else:
                                    print(f"  Warning: Parameter not in expected format: {param}")
                            
                            if len(param_indices) == 1:
                                print(f"  Adding add effect: {fluent_name}(p{param_indices[0]}) = True")
                                action.add_effect(fluents[fluent_name](action.parameter(f'p{param_indices[0]}')), True)
                            elif len(param_indices) == 2:
                                print(f"  Adding add effect: {fluent_name}(p{param_indices[0]}, p{param_indices[1]}) = True")
                                action.add_effect(fluents[fluent_name](
                                    action.parameter(f'p{param_indices[0]}'), 
                                    action.parameter(f'p{param_indices[1]}')), True)
                
                # Process del effects
                if 'del(' in effect:
                    del_match = re.search(r'del\((.*?)\)', effect)
                    if del_match:
                        del_expr = del_match.group(1)
                        inner_match = re.match(r'([a-zA-Z_]+)\((.*?)\)', del_expr)
                        if inner_match:
                            fluent_name = inner_match.group(1)
                            params = [p.strip() for p in inner_match.group(2).split(',')]
                            
                            if fluent_name not in fluents:
                                print(f"  Warning: Fluent {fluent_name} not found for del effect")
                                continue
                            
                            # Map 'Param1' to index 0, 'Param2' to index 1, etc.
                            param_indices = []
                            for param in params:
                                if param.startswith('Param'):
                                    try:
                                        idx = int(param[5:]) - 1  # Convert Param1 -> 0, Param2 -> 1, etc.
                                        param_indices.append(idx)
                                    except ValueError:
                                        print(f"  Warning: Could not parse parameter index from {param}")
                                else:
                                    print(f"  Warning: Parameter not in expected format: {param}")
                            
                            if len(param_indices) == 1:
                                print(f"  Adding del effect: {fluent_name}(p{param_indices[0]}) = False")
                                action.add_effect(fluents[fluent_name](action.parameter(f'p{param_indices[0]}')), False)
                            elif len(param_indices) == 2:
                                print(f"  Adding del effect: {fluent_name}(p{param_indices[0]}, p{param_indices[1]}) = False")
                                action.add_effect(fluents[fluent_name](
                                    action.parameter(f'p{param_indices[0]}'), 
                                    action.parameter(f'p{param_indices[1]}')), False)
            
            # Add the action to the problem
            problem.add_action(action)
            
        except Exception as e:
            print(f"  Error creating action {action_name}: {e}")
            import traceback
            traceback.print_exc()
    
    up_creation_time = time.time() - start_time
    print(f"Unified Planning problem created in {up_creation_time:.4f} seconds")
    
    return problem


def export_to_pddl(problem, output_file_prefix, output_dir="RESULTS/CONVERTER"):
    """Export problem to PDDL files"""
    import os
    
    try:
        writer = PDDLWriter(problem)
        
        # Ensure the directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        domain_path = f"{output_dir}/{output_file_prefix}_domain.pddl"
        problem_path = f"{output_dir}/{output_file_prefix}_problem.pddl"
        
        writer.write_domain(domain_path)
        writer.write_problem(problem_path)
        
        print(f"\nPDDL files written to:")
        print(f"  Domain: {domain_path}")
        print(f"  Problem: {problem_path}")
        
        return domain_path, problem_path
        
    except Exception as e:
        print(f"Error writing PDDL files: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def solve_problem(problem):
    """Try to solve the problem using available planners"""
    print("\n===== TRYING TO SOLVE THE PROBLEM =====")
    
    try:
        with OneshotPlanner(problem_kind=problem.kind) as planner:
            print(f"Selected planner: {planner.name}")
            
            solve_start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - solve_start_time
            
            print(f"Plan status: {result.status}")
            
            if result.status in [up.engines.results.PlanGenerationResultStatus.SOLVED_SATISFICING,
                                up.engines.results.PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
                print(f"\nPlan found in {solve_time:.2f} seconds:")
                for action in result.plan.actions:
                    print(f"  {action}")
                return result
            else:
                print(f"No plan found. Solving attempted for {solve_time:.2f} seconds.")
                return None
                
    except Exception as e:
        print(f"Error while trying to solve the problem: {e}")
        import traceback
        traceback.print_exc()
        return None$