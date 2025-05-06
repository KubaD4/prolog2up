import time
import re
from pyswip import Prolog
import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter

def extract_prolog_knowledge(prolog_file):
    """Extract knowledge from Prolog file using PySwip"""
    start_time = time.time()
    print(f"Starting extraction from Prolog file...")
    
    # Initialize Prolog engine
    prolog = Prolog()
    
    # Load the Prolog file
    prolog.consult(prolog_file)
    
    # Extract basic facts
    blocks = list(prolog.query("block(X)"))
    positions = list(prolog.query("pos(X, Y)"))
    agents = list(prolog.query("agent(X)"))
    
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
    
    # Extract actions
    actions = []
    # First, find all action names
    action_names = set()
    for solution in prolog.query("action(Action, _, _, _, _, _)"):
        functor = str(solution['Action']).split('(')[0]
        action_names.add(functor)
    
    # Then extract details for each action
    for action_name in action_names:
        # Use regular parameter names instead of Prolog variables
        standard_param_names = {
            'move_table_to_block_start': ['Agent', 'Block1', 'Block2', 'X1', 'Y1', 'X2', 'Y2'],
            'move_table_to_block_end': ['Agent', 'Block1', 'Block2', 'X1', 'Y1', 'X2', 'Y2'],
            'move_table_to_table_start': ['Agent', 'Block', 'X1', 'Y1', 'X2', 'Y2'],
            'move_table_to_table_end': ['Agent', 'Block', 'X1', 'Y1', 'X2', 'Y2'],
            'move_onblock_to_table_start': ['Agent', 'Block1', 'Block2', 'X1', 'Y1', 'X2', 'Y2'],
            'move_onblock_to_table_end': ['Agent', 'Block1', 'Block2', 'X1', 'Y1', 'X2', 'Y2'],
            'move_onblock_to_block_start': ['Agent', 'Block1', 'Block2', 'Block3', 'X1', 'Y1', 'X2', 'Y2'],
            'move_onblock_to_block_end': ['Agent', 'Block1', 'Block2', 'Block3', 'X1', 'Y1', 'X2', 'Y2'],
        }
        
        param_names = standard_param_names.get(action_name, ['Param1', 'Param2', 'Param3', 'Param4', 'Param5', 'Param6', 'Param7'])
        
        # Try with different parameter counts
        action_found = False
        
        # For actions with 7 parameters
        for solution in prolog.query(f"action({action_name}(A, B, C, D, E, F, G), Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"):
            action_info = {
                'name': action_name,
                'parameters': param_names[:7],  # Use standard param names
                'param_values': [solution['A'], solution['B'], solution['C'], solution['D'], solution['E'], solution['F'], solution['G']],
                'preconditions': [str(p) for p in solution['Precond']],
                'neg_preconditions': [str(p) for p in solution['NegPrecond']],
                'resource_preconditions': [str(p) for p in solution['ResourcePrecond']],
                'type_constraints': [str(c) for c in solution['TypeConstraints']],
                'effects': [str(e) for e in solution['Effects']]
            }
            actions.append(action_info)
            action_found = True
        
        # Try with 6 parameters if not found yet
        if not action_found:
            for solution in prolog.query(f"action({action_name}(A, B, C, D, E, F), Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"):
                action_info = {
                    'name': action_name,
                    'parameters': param_names[:6],  # Use standard param names
                    'param_values': [solution['A'], solution['B'], solution['C'], solution['D'], solution['E'], solution['F']],
                    'preconditions': [str(p) for p in solution['Precond']],
                    'neg_preconditions': [str(p) for p in solution['NegPrecond']],
                    'resource_preconditions': [str(p) for p in solution['ResourcePrecond']],
                    'type_constraints': [str(c) for c in solution['TypeConstraints']],
                    'effects': [str(e) for e in solution['Effects']]
                }
                actions.append(action_info)
                action_found = True
        
        # Try with 8 parameters if needed
        if not action_found:
            for solution in prolog.query(f"action({action_name}(A, B, C, D, E, F, G, H), Precond, NegPrecond, ResourcePrecond, TypeConstraints, Effects)"):
                action_info = {
                    'name': action_name,
                    'parameters': param_names[:8] if len(param_names) >= 8 else param_names + ['Param' + str(i) for i in range(len(param_names)+1, 9)],
                    'param_values': [solution['A'], solution['B'], solution['C'], solution['D'], solution['E'], solution['F'], solution['G'], solution['H']],
                    'preconditions': [str(p) for p in solution['Precond']],
                    'neg_preconditions': [str(p) for p in solution['NegPrecond']],
                    'resource_preconditions': [str(p) for p in solution['ResourcePrecond']],
                    'type_constraints': [str(c) for c in solution['TypeConstraints']],
                    'effects': [str(e) for e in solution['Effects']]
                }
                actions.append(action_info)
                action_found = True
    
    extraction_time = time.time() - start_time
    print(f"Extraction completed in {extraction_time:.4f} seconds")
    
    # Organize extracted knowledge
    knowledge = {
        'blocks': [b['X'] for b in blocks],
        'positions': [(p['X'], p['Y']) for p in positions],
        'agents': [a['X'] for a in agents],
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
    """Analyze fluent signatures to determine their parameter types"""
    fluent_signatures = {}
    
    # Helper function to extract parameter types from a fluent instance
    def extract_param_types(fluent_str):
        # Extract the parameters from the fluent string
        match = re.match(r'([a-zA-Z_]+)\((.*?)\)', fluent_str)
        if not match:
            return []
        
        fluent_name = match.group(1) #nome del Fluent
        params_str = match.group(2) #parametri del Fluent
        params = [p.strip() for p in params_str.split(',')]
        
        param_types = []
        for param in params:
            # Check if parameter is a block
            if param in knowledge['blocks']:
                param_types.append('Block')
            # Check if parameter is an agent
            elif param in knowledge['agents']:
                param_types.append('Agent')
            # Check if parameter is a position coordinate
            elif any(param == str(pos[0]) or param == str(pos[1]) for pos in knowledge['positions']):
                param_types.append('Location')
            else:
                # If can't determine, assume it's a variable
                param_types.append('Unknown')
        
        return param_types
    
    # Analyze all fluent instances in initial state, goal state and actions
    for fluent_name in knowledge['fluent_names']:
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
                common_type = max(set(types_at_position), key=types_at_position.count)
                final_param_types.append(common_type)
            
            fluent_signatures[fluent_name] = final_param_types
    
    return fluent_signatures

def create_up_problem(knowledge, fluent_signatures):
    """Create a unified_planning Problem from extracted knowledge"""
    start_time = time.time()
    print(f"\nCreating Unified Planning problem...")
    
    # Define types
    Location = UserType("Location")
    Block = UserType("Block")
    Agent = UserType("Agent")
    
    # Create Problem
    problem = Problem('blocks')
    
    # Create fluents
    fluents = {}
    for fluent_name, param_types in fluent_signatures.items():
        # Skip the "moving_" fluents initially - we'll add them later
        if fluent_name.startswith('moving_'):
            continue
        
        # Map parameter types to UP types
        up_param_types = []
        param_names = []
        
        for i, param_type in enumerate(param_types):
            if param_type == 'Block':
                up_param_types.append(Block)
                param_names.append(f'b{i+1}')
            elif param_type == 'Agent':
                up_param_types.append(Agent)
                param_names.append(f'a')
            elif param_type == 'Location':
                up_param_types.append(Location)
                param_names.append(f'l{i+1}')
            else:
                # Default to Block if unknown
                up_param_types.append(Block)
                param_names.append(f'x{i+1}')
        
        # Create fluent with appropriate parameters
        param_dict = {name: type for name, type in zip(param_names, up_param_types)}
        fluent = Fluent(fluent_name, BoolType(), **param_dict)
        fluents[fluent_name] = fluent
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Now add the "moving_" fluents
    for fluent_name, param_types in fluent_signatures.items():
        if not fluent_name.startswith('moving_'):
            continue
        
        # For "moving_" fluents, we need specific parameter mapping
        if fluent_name == 'moving_table_to_block':
            # moving_table_to_block(Agent, Block1, Block2, X1, Y1, X2, Y2)
            fluent = Fluent(fluent_name, BoolType(),
                           a=Agent, b1=Block, b2=Block,
                           l1=Location, l2=Location)
        elif fluent_name == 'moving_table_to_table':
            # moving_table_to_table(Agent, Block, X1, Y1, X2, Y2)
            fluent = Fluent(fluent_name, BoolType(),
                           a=Agent, b=Block,
                           l1=Location, l2=Location)
        elif fluent_name == 'moving_onblock_to_table':
            # moving_onblock_to_table(Agent, Block, X1, Y1, X2, Y2)
            fluent = Fluent(fluent_name, BoolType(),
                           a=Agent, b=Block,
                           l1=Location, l2=Location)
        elif fluent_name == 'moving_onblock_to_block':
            # moving_onblock_to_block(Agent, Block1, Block2, X1, Y1, X2, Y2)
            fluent = Fluent(fluent_name, BoolType(),
                           a=Agent, b1=Block, b2=Block,
                           l1=Location, l2=Location)
        else:
            # Skip if we don't know how to handle this fluent
            continue
        
        fluents[fluent_name] = fluent
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Create positions
    positions = []
    pos_dict = {}  # (x,y) -> pos_x_y object
    for x, y in knowledge['positions']:
        pos_name = f"loc_{x}_{y}"
        l = Object(pos_name, Location)
        positions.append(l)
        pos_dict[(x, y)] = l
    
    # Create blocks
    blocks = [Object(str(b), Block) for b in knowledge['blocks']]
    problem.add_objects(blocks)
    
    # Create agents
    agents = [Object(str(a), Agent) for a in knowledge['agents']]
    problem.add_objects(agents)
    problem.add_objects(positions)
    
    # Create a mapping for objects
    object_dict = {}
    for block in blocks:
        object_dict[block.name] = block
    for agent in agents:
        object_dict[agent.name] = agent
    for pos in positions:
        # Extract coordinates from position name
        x, y = pos.name.replace('loc_', '').split('_')
        object_dict[(int(x), int(y))] = pos
    
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
        
        # Set the fluent to True in the initial state
        if fluent_name == 'ontable':
            problem.set_initial_value(fluents[fluent_name](object_dict[params[0]]), True)
        elif fluent_name == 'on':
            problem.set_initial_value(fluents[fluent_name](object_dict[params[0]], object_dict[params[1]]), True)
        elif fluent_name == 'at':
            block = object_dict[params[0]]
            x, y = int(params[1]), int(params[2])
            location = pos_dict.get((x, y))
            if location:
                # Fix: Use both x and y as separate location parameters
                problem.set_initial_value(fluents[fluent_name](block, pos_dict[(x, y)], pos_dict[(x, y)]), True)
        elif fluent_name == 'clear':
            problem.set_initial_value(fluents[fluent_name](object_dict[params[0]]), True)
        elif fluent_name == 'available':
            problem.set_initial_value(fluents[fluent_name](object_dict[params[0]]), True)
    
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
        
        # Set the fluent to True in the goal state
        if fluent_name == 'ontable':
            problem.add_goal(fluents[fluent_name](object_dict[params[0]]))
        elif fluent_name == 'on':
            problem.add_goal(fluents[fluent_name](object_dict[params[0]], object_dict[params[1]]))
        elif fluent_name == 'at':
            block = object_dict[params[0]]
            x, y = int(params[1]), int(params[2])
            location = pos_dict.get((x, y))
            if location:
                # Fix: Use both x and y as separate location parameters
                problem.add_goal(fluents[fluent_name](block, pos_dict[(x, y)], pos_dict[(x, y)]))
        elif fluent_name == 'clear':
            problem.add_goal(fluents[fluent_name](object_dict[params[0]]))
        elif fluent_name == 'available':
            problem.add_goal(fluents[fluent_name](object_dict[params[0]]))
    
    # Create actions
    print(f"Number of actions to process: {len(knowledge['actions'])}")
    for action_info in knowledge['actions']:
        action_name = action_info['name']
        
        print(f"Processing action: {action_name}")
        
        # Determine action parameters
        if action_name == 'move_table_to_block_start' or action_name == 'move_table_to_block_end':
            # move_table_to_block(Agent, Block1, Block2, X1, Y1, X2, Y2)
            action = InstantaneousAction(action_name, a=Agent, b1=Block, b2=Block, l1=Location, l2=Location)
            a = action.parameter('a')
            b1 = action.parameter('b1')
            b2 = action.parameter('b2')
            l1 = action.parameter('l1')
            l2 = action.parameter('l2')
            
            # Add preconditions
            for precond in action_info['preconditions']:
                match = re.match(r'([a-zA-Z_]+)\((.*?)\)', precond)
                if not match:
                    continue
                
                fluent_name = match.group(1)
                params_str = match.group(2)
                params = [p.strip() for p in params_str.split(',')]
                
                if fluent_name not in fluents:
                    continue
                
                # Add precondition based on fluent type
                if fluent_name == 'available':
                    action.add_precondition(fluents[fluent_name](a))
                elif fluent_name == 'ontable':
                    action.add_precondition(fluents[fluent_name](b1))
                elif fluent_name == 'at' and params[0] == 'Block1':
                    # Fix: Use the same parameter twice for locations
                    action.add_precondition(fluents[fluent_name](b1, l1, l1))
                elif fluent_name == 'at' and params[0] == 'Block2':
                    # Fix: Use the same parameter twice for locations
                    action.add_precondition(fluents[fluent_name](b2, l2, l2))
                elif fluent_name == 'clear' and params[0] == 'Block1':
                    action.add_precondition(fluents[fluent_name](b1))
                elif fluent_name == 'clear' and params[0] == 'Block2':
                    action.add_precondition(fluents[fluent_name](b2))
                elif fluent_name == 'moving_table_to_block':
                    action.add_precondition(fluents[fluent_name](a, b1, b2, l1, l2))
            
            # Add negative preconditions using Exists for universally quantified variables
            if action_name == 'move_table_to_block_start':
                any_b = Variable("other_b", Block)
                
                # No block on b1
                action.add_precondition(
                    Not(Exists(
                        fluents['on'](any_b, b1),
                        any_b
                    ))
                )
                
                # b1 is not on any block
                action.add_precondition(
                    Not(Exists(
                        fluents['on'](b1, any_b),
                        any_b
                    ))
                )
                
                # No ongoing move involving b1
                other_agent = Variable("other_agent", Agent)
                other_block = Variable("other_block", Block)
                other_l1 = Variable("other_l1", Location)
                other_l2 = Variable("other_l2", Location)
                
                action.add_precondition(
                    Not(Exists(
                        fluents['moving_table_to_block'](other_agent, b1, other_block, other_l1, other_l2),
                        other_agent, other_block, other_l1, other_l2
                    ))
                )
            
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
                    params_str = match.group(2)
                    params = [p.strip() for p in params_str.split(',')]
                    
                    if fluent_name not in fluents:
                        continue
                    
                    # Add effect based on fluent type
                    if fluent_name == 'available':
                        action.add_effect(fluents[fluent_name](a), True)
                    elif fluent_name == 'on':
                        action.add_effect(fluents[fluent_name](b1, b2), True)
                    elif fluent_name == 'at':
                        # Fix: Use the same parameter twice for locations
                        action.add_effect(fluents[fluent_name](b1, l2, l2), True)
                    elif fluent_name == 'clear':
                        if params[0] == 'Block1':
                            action.add_effect(fluents[fluent_name](b1), True)
                        elif params[0] == 'Block2':
                            action.add_effect(fluents[fluent_name](b2), True)
                    elif fluent_name == 'moving_table_to_block':
                        action.add_effect(fluents[fluent_name](a, b1, b2, l1, l2), True)
                
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
                    params_str = match.group(2)
                    params = [p.strip() for p in params_str.split(',')]
                    
                    if fluent_name not in fluents:
                        continue
                    
                    # Delete effect based on fluent type
                    if fluent_name == 'available':
                        action.add_effect(fluents[fluent_name](a), False)
                    elif fluent_name == 'ontable':
                        action.add_effect(fluents[fluent_name](b1), False)
                    elif fluent_name == 'at':
                        # Fix: Use the same parameter twice for locations
                        action.add_effect(fluents[fluent_name](b1, l1, l1), False)
                    elif fluent_name == 'clear':
                        if params[0] == 'Block1':
                            action.add_effect(fluents[fluent_name](b1), False)
                        elif params[0] == 'Block2':
                            action.add_effect(fluents[fluent_name](b2), False)
                    elif fluent_name == 'moving_table_to_block':
                        action.add_effect(fluents[fluent_name](a, b1, b2, l1, l2), False)
            
            problem.add_action(action)
    
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
    print(f"  Blocks: {knowledge['blocks']}")
    print(f"  Positions: {knowledge['positions']}")
    print(f"  Agents: {knowledge['agents']}")
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
    
    print(f"\n\n\nUnified Planning problem details:")
    print(problem)
    print(f"\n\n\n")

    # Generate PDDL if output file specified
    if pddl_output_file:
        writer = PDDLWriter(problem)
        writer.write_domain("RESULTS/CONVERTER/" + pddl_output_file + "_domain.pddl")
        writer.write_problem("RESULTS/CONVERTER/" + pddl_output_file + "_problem.pddl")
        print(f"\nPDDL files written to {pddl_output_file}.domain.pddl and {pddl_output_file}.problem.pddl")
    
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