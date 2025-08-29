#!/usr/bin/env python3
"""
Prolog to Unified Planning Converter V2 - FIXED VERSION
Converts extracted Prolog knowledge (from JSON) into Unified Planning Python code
WITH BUG FIXES for type inference
"""

import os
import json
import sys
from unified_planning.shortcuts import *
from unified_planning.model import Problem, Object, Fluent, InstantaneousAction, Variable
from unified_planning.io import PDDLWriter


def infer_fluent_signature_from_usage(knowledge, fluent_name):
    """
    Inferisce la signature di un fluent analizzando il suo uso,
    completamente generalizzato senza assunzioni hard-coded.
    """
    candidates_with_scores = []
    
    for action in knowledge["actions"]:
        action_score = len(action["type_constraints"])
        
        sections = [
            ("preconditions", action.get("preconditions", [])),
            ("neg_preconditions", action.get("neg_preconditions", [])),
            ("add_effects", action.get("add_effects", [])),
            ("del_effects", action.get("del_effects", []))
        ]
        
        for section_name, items in sections:
            for item in items:
                if item["name"] == fluent_name:
                    types = []
                    quality_score = 0
                    
                    for arg in item["args"]:
                        if arg in action["type_constraints"]:
                            arg_type = action["type_constraints"][arg]
                            types.append(arg_type)
                            if arg_type != "Unknown":
                                quality_score += 1
                        elif arg.startswith("_"):
                            types.append("Unknown")
                        else:
                            # Infer type from structure
                            inferred_type = _infer_type_from_structure(arg, knowledge)
                            types.append(inferred_type)
                            if inferred_type != "Unknown":
                                quality_score += 1
                    
                    if types:
                        combined_score = (quality_score / len(types)) * action_score
                        candidates_with_scores.append((types, combined_score, action["name"]))

    # Check state sections with high priority
    for state_section, section_name in [(knowledge["init_state"], "init"), (knowledge["goal_state"], "goal")]:
        for state_item in state_section:
            if state_item["name"] == fluent_name:
                types = []
                for arg in state_item["args"]:
                    inferred_type = _infer_type_from_structure(arg, knowledge)
                    types.append(inferred_type)
                
                if types:
                    # High priority for state sections
                    candidates_with_scores.append((types, 1000, section_name))
    
    if not candidates_with_scores:
        return ["Unknown"]

    # Sort by score
    candidates_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Choose most common length
    lengths = [len(c[0]) for c in candidates_with_scores]
    most_common_length = max(set(lengths), key=lengths.count)
    
    # Filter by most common length
    filtered = [c for c in candidates_with_scores if len(c[0]) == most_common_length]
    
    # Generate final signature
    result = []
    for i in range(most_common_length):
        types_at_pos = [c[0][i] for c in filtered if i < len(c[0])]
        
        if types_at_pos:
            # Choose most common type at this position
            known_types = [t for t in types_at_pos if t != "Unknown"]
            if known_types:
                # Most frequent known type
                most_common = max(set(known_types), key=known_types.count)
                result.append(most_common)
            else:
                result.append("Unknown")
        else:
            result.append("Unknown")
    
    return result


def _infer_type_from_structure(arg, knowledge):
    """Inferisce il tipo di un argomento dalla sua struttura"""
    # Check if it's in known types
    for type_name, instances in knowledge["types"].items():
        if arg in instances:
            return type_name
    
    # Check if it's a number (coordinate)
    if arg.isdigit() or (arg.replace('-', '').replace('.', '').isdigit()):
        return "pos"
    
    return "Unknown"


def _infer_wildcard_type_from_context(fluent_name, position, action, knowledge):
    """
    Inferisce il tipo di una wildcard anche considerando i supertipi
    """
    # First check direct usage in this action
    for section in ("preconditions", "add_effects", "del_effects"):
        for item in action.get(section, []):
            if item["name"] == fluent_name and len(item["args"]) > position:
                arg_at_position = item["args"][position]
                if arg_at_position in action["type_constraints"]:
                    return action["type_constraints"][arg_at_position]
    
    # Check fluent signatures
    if fluent_name in knowledge.get("fluent_signatures", {}):
        sig = knowledge["fluent_signatures"][fluent_name]
        if position < len(sig) and sig[position] != "Unknown":
            return sig[position]
    
    return "object"   # fallback


def resolve_parameter_types_for_supertypes(knowledge, action):
    print(f"  Resolving supertypes for action {action['name']}")
    
    # Get relevant data
    fluent_signatures = knowledge.get("fluent_signatures", {})
    supertypes = knowledge.get("supertypes", {})
    
    # Track parameter usage across different fluents
    parameter_usage = {}  # param_name -> set of required types
    
    # Helper function to analyze predicate usage
    def analyze_predicate_usage(pred):
        fluent_name = pred["name"]
        args = pred["args"]
        
        if fluent_name in fluent_signatures:
            sig = fluent_signatures[fluent_name]
            
            for i, arg in enumerate(args):
                if arg.startswith("Param") and i < len(sig):
                    required_type = sig[i]
                    
                    if arg not in parameter_usage:
                        parameter_usage[arg] = set()
                    parameter_usage[arg].add(required_type)
    
    # Analyze usage in all sections
    for section_name in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
        for pred in action.get(section_name, []):
            analyze_predicate_usage(pred)
    
    # Resolve types using supertypes
    resolved_types = action["type_constraints"].copy()
    
    for param_name, required_types in parameter_usage.items():
        if len(required_types) > 1:
            # Look for a supertype that encompasses all required types
            for supertype_name, constituent_types in supertypes.items():
                # Check if this supertype covers all required types
                if required_types.issubset(set(constituent_types)):
                    print(f"    Parameter {param_name}: {required_types} -> {supertype_name}")
                    resolved_types[param_name] = supertype_name
                    break
        elif len(required_types) == 1:
            required_type = list(required_types)[0]
            current_type = resolved_types.get(param_name, "Unknown")
            
            # If the required type is already a supertype, use it
            if required_type in supertypes:
                print(f"    Parameter {param_name}: {current_type} -> {required_type} (supertype)")
                resolved_types[param_name] = required_type
            # If current type should be promoted to supertype
            elif current_type != required_type:
                for supertype_name, constituent_types in supertypes.items():
                    if current_type in constituent_types and required_type == supertype_name:
                        print(f"    Parameter {param_name}: {current_type} -> {supertype_name} (promoted to supertype)")
                        resolved_types[param_name] = supertype_name
                        break
    
    return resolved_types


def generate_up_code_negative_preconditions_section(knowledge, name, act):
    lines = []
    
    for neg in act.get("neg_preconditions", []):
        pname = neg["name"]
        pargs = neg["args"]
        wilds = set(neg.get("wildcard_positions", []))
        
        # Get fluent signature for this predicate
        fluent_sig = knowledge["fluent_signatures"].get(pname)
        if not fluent_sig:
            fluent_sig = infer_fluent_signature_from_usage(knowledge, pname)
        
        # Extend signature if needed
        while len(fluent_sig) < len(pargs):
            fluent_sig.append("object")
        
        expr = []
        vars_for_exists = []
        
        for i, a in enumerate(pargs):
            if i in wilds or a.startswith("_"):
                var = f"any_{name}_{i}"
                
                # Get type for this position
                if i < len(fluent_sig):
                    vtype = fluent_sig[i]
                    if vtype == "Unknown" or vtype is None:
                        vtype = _infer_wildcard_type_from_context(pname, i, act, knowledge)
                else:
                    vtype = _infer_wildcard_type_from_context(pname, i, act, knowledge)
                
                # Handle Unknown types
                if vtype == "Unknown":
                    vtype = "object"
                
                # Use appropriate type name
                if vtype in knowledge.get("supertypes", {}):
                    # It's a supertype
                    type_name = vtype
                else:
                    # It's a regular type - capitalize
                    type_name = vtype.capitalize()
                
                lines.append(f"{var} = Variable('{var}', {type_name})")
                expr.append(var)
                vars_for_exists.append(var)
            else:
                expr.append(a)
        
        if vars_for_exists:
            lines.append(f"{name}.add_precondition(Not(Exists({pname}({', '.join(expr)}), {', '.join(vars_for_exists)})))")
        else:
            lines.append(f"{name}.add_precondition(Not({pname}({', '.join(expr)})))")
    
    return lines


def convert_numbers_to_strings(knowledge):
    """
    Converte tutti i numeri in stringhe valide per UP.
    Es: 1 -> x1, 2 -> x2, 10 -> x10, etc.
    """
    
    def convert_number_if_needed(value):
        # Convert digit strings and numbers to x-prefixed format
        if isinstance(value, str) and value.isdigit():
            return f"x{value}"
        elif isinstance(value, (int, float)):
            return f"x{int(value)}"
        return value
    
    def convert_predicate_args(pred):
        # Convert args in predicates
        converted_pred = pred.copy()
        converted_pred["args"] = [convert_number_if_needed(arg) for arg in pred["args"]]
        return converted_pred
    
    def convert_action_args(action):
        # Convert args in action sections
        converted_action = action.copy()
        
        for section in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
            if section in converted_action:
                converted_action[section] = [
                    convert_predicate_args(pred) for pred in converted_action[section]
                ]
        
        return converted_action
    
    # Convert init_state
    knowledge["init_state"] = [convert_predicate_args(pred) for pred in knowledge["init_state"]]
    
    # Convert goal_state  
    knowledge["goal_state"] = [convert_predicate_args(pred) for pred in knowledge["goal_state"]]
    
    # Convert actions
    knowledge["actions"] = [convert_action_args(action) for action in knowledge["actions"]]
    
    return knowledge


def extract_string_objects_from_knowledge(knowledge):
    """
    Estrae tutti gli oggetti stringa (inclusi quelli convertiti da numeri)
    dal knowledge per creare gli oggetti UP necessari.
    """
    string_objects = set()
    
    # Extract from state sections
    for state_section in [knowledge["init_state"], knowledge["goal_state"]]:
        for pred in state_section:
            for arg in pred["args"]:
                if (isinstance(arg, str) and 
                    not arg.startswith("Param") and
                    not arg.startswith("_")):
                    string_objects.add(arg)
    
    # Extract from actions
    for action in knowledge["actions"]:
        for section in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
            for pred in action.get(section, []):
                for arg in pred["args"]:
                    if (isinstance(arg, str) and 
                        not arg.startswith("Param") and 
                        not arg.startswith("_")):
                        string_objects.add(arg)
    
    return sorted(string_objects)


def generate_supertype_definitions(knowledge):
    """
    Genera le definizioni dei supertipi e crea oggetti che appartengono a questi supertipi.
    """
    supertype_lines = []
    supertype_objects = {}  # supertype_name -> list of object instances
    
    if "supertypes" not in knowledge:
        return supertype_lines, supertype_objects
    
    print("\n=== GENERATING SUPERTYPE DEFINITIONS ===")
    
    for supertype_name, constituent_types in knowledge["supertypes"].items():
        # Generate UserType definition
        supertype_lines.append(f"{supertype_name} = UserType('{supertype_name.lower()}')")
        print(f"Created supertype: {supertype_name} = {constituent_types}")
        
        # Raccogli tutti gli oggetti che appartengono a questo supertipo
        supertype_instances = []
        
        # Collect all instances from constituent types
        for constituent_type in constituent_types:
            if constituent_type in knowledge["types"]:
                for instance in knowledge["types"][constituent_type]:
                    if isinstance(instance, str):
                        supertype_instances.append(instance)
        
        supertype_objects[supertype_name] = supertype_instances
        print(f"  Instances: {supertype_instances}")
    
    print("=== END SUPERTYPE GENERATION ===\n")
    
    return supertype_lines, supertype_objects


def get_effective_type_for_object(obj_name, knowledge, supertype_objects):
    """
    Determina il tipo effettivo di un oggetto, considerando i supertipi.
    FIXED: Returns proper type strings instead of Python Object class
    """
    # First check if object belongs to a supertype
    for supertype_name, instances in supertype_objects.items():
        if obj_name in instances:
            return supertype_name
    
    # Then check standard types
    for type_name, instances in knowledge["types"].items():
        if obj_name in instances:
            return type_name.capitalize()
    
    # Check if it's a numeric coordinate (x1, x2, etc.)
    if obj_name.startswith("x") and obj_name[1:].isdigit():
        return "Pos"
    
    # FIXED: Better fallback logic
    available_types = list(knowledge["types"].keys())
    if available_types:
        return available_types[0].capitalize()
    
    # FIXED: Return "object" string instead of Object class
    return "object"


def collect_all_fluents_from_knowledge(knowledge):
    all_fluents = set()
    
    print("🔍 Collecting fluents from all knowledge sections...")
    
    # 1. Fluents from init_state
    for pred in knowledge.get("init_state", []):
        fluent_name = pred["name"]
        all_fluents.add(fluent_name)
        print(f"  Found fluent in init_state: {fluent_name}")
    
    # 2. Fluents from goal_state  
    for pred in knowledge.get("goal_state", []):
        fluent_name = pred["name"]
        all_fluents.add(fluent_name)
        print(f"  Found fluent in goal_state: {fluent_name}")
    
    # 3. Fluents from actions
    for action in knowledge.get("actions", []):
        action_name = action["name"]
        
        # Positive preconditions
        for pred in action.get("preconditions", []):
            fluent_name = pred["name"]
            all_fluents.add(fluent_name)
            print(f"  Found fluent in {action_name}.preconditions: {fluent_name}")
        
        # NEGATIVE PRECONDITIONS 
        for pred in action.get("neg_preconditions", []):
            fluent_name = pred["name"]
            all_fluents.add(fluent_name)
            print(f"  Found fluent in {action_name}.neg_preconditions: {fluent_name}")
        
        # Add effects
        for pred in action.get("add_effects", []):
            fluent_name = pred["name"]
            all_fluents.add(fluent_name)
            print(f"  Found fluent in {action_name}.add_effects: {fluent_name}")
        
        # Delete effects
        for pred in action.get("del_effects", []):
            fluent_name = pred["name"]
            all_fluents.add(fluent_name)
            print(f"  Found fluent in {action_name}.del_effects: {fluent_name}")
    
    print(f" Total unique fluents found: {len(all_fluents)}")
    print(f"   Fluents: {sorted(all_fluents)}")
    
    return sorted(all_fluents)


def generate_wildcard_variable(fluent_name, arg_position, knowledge, action_name):
    """Generate appropriate wildcard variable for fluent argument
    FIXED: Returns proper type strings instead of Python Object class
    """
    
    # Get fluent signature
    fluent_sig = knowledge["fluent_signatures"].get(fluent_name, [])
    
    if arg_position < len(fluent_sig):
        arg_type = fluent_sig[arg_position]
        if arg_type != "Unknown":
            # Create unique variable name
            var_name = f"any_{fluent_name}_{arg_position}_{action_name}"
            return var_name, arg_type  # FIXED: don't capitalize here
    
    # FIXED: Fallback to object type (string, not class)
    var_name = f"any_{fluent_name}_{arg_position}_{action_name}"
    return var_name, "object"  # FIXED: "object" string instead of Object class


def resolve_fluent_parameter_type(arg_type, knowledge, created_additional_types, wp):
    """Risolve il tipo di un parametro fluent gestendo supertypes correttamente
    FIXED: Added to handle mixed types properly
    """
    
    if arg_type == "Unknown" or arg_type is None:
        arg_type = "object"
    
    # Se è un supertipo esistente
    if arg_type in knowledge.get("supertypes", {}):
        return arg_type
    
    # Se è un tipo standard esistente  
    standard_types = [t.lower() for t in knowledge["types"].keys()]
    if arg_type.lower() in standard_types:
        return arg_type.capitalize()
    
    # Se è "object", crea un UserType generico se necessario
    if arg_type.lower() == "object":
        if "object" not in created_additional_types:
            wp("ObjectType = UserType('object')")
            created_additional_types.add("object")
        return "ObjectType"
    
    # Altrimenti crea un nuovo UserType
    if arg_type not in created_additional_types:
        wp(f"{arg_type.capitalize()} = UserType('{arg_type.lower()}')")
        created_additional_types.add(arg_type)
    
    return arg_type.capitalize()


def generate_up_code(knowledge, out_dir):
    """Generate UP code with polymorphic fluent support
    FIXED: Better type handling throughout
    """
    
    # Convert numeric values to valid UP strings
    knowledge = convert_numbers_to_strings(knowledge)
    
    lines = []
    wp = lines.append

    # 1) Header
    wp("# Generated UP code from Prolog knowledge")
    wp("# This code is automatically generated.")
    wp("import unified_planning as up")
    wp("import os")
    wp("from unified_planning.shortcuts import *")
    wp("from unified_planning.model import Variable, InstantaneousAction, Problem")
    wp("from unified_planning.io import PDDLWriter")
    wp("from unified_planning.shortcuts import *")
    wp("")
    wp("# Suppress credits output if available")
    wp("try:")
    wp("    up.shortcuts.get_environment().credits_stream = None")
    wp("except AttributeError:")
    wp("    pass  # get_environment() not available in this UP version")
    wp("")

    # 2) Original types (UserType)
    for t, instances in knowledge["types"].items():
        wp(f"{t.capitalize()} = UserType('{t}')")
    wp("")
    
    # 3) Generate supertypes if present
    supertype_lines, supertype_objects = generate_supertype_definitions(knowledge)
    for line in supertype_lines:
        wp(line)
    if supertype_lines:
        wp("")
    
    # 4) Additional types from fluent signatures
    unique_types = set()
    for fluent_name, type_list in knowledge['fluent_signatures'].items():
        unique_types.update(type_list)

    # Remove "Unknown" from types and add common missing types
    unique_types.discard("Unknown")
    unique_types.add("pos") 
    unique_types_list = list(unique_types)

    print(f"Tipi unici trovati: {unique_types_list}")

    existing_types = set([t.lower() for t in knowledge["types"].keys()])
    existing_supertypes = set()
    if "supertypes" in knowledge:
        existing_supertypes = set([st.lower() for st in knowledge["supertypes"].keys()])
    
    for UT in unique_types_list:
        ut_lower = UT.lower()
        
        # Don't create if it already exists as a type or supertype
        supertype_names = set(knowledge.get("supertypes", {}).keys())
        if ut_lower not in existing_types and UT not in supertype_names:
            wp(f"{UT.capitalize()} = UserType('{ut_lower}')")
    wp("")

    all_fluents = collect_all_fluents_from_knowledge(knowledge)
    
    # 5) Fluents with signatures that support supertypes
    # FIXED: Better type resolution
    created_additional_types = set()
    
    for f in all_fluents:
        sig = knowledge["fluent_signatures"].get(f, [])
        
        # If signature not found, try to infer it
        if not sig:
            sig = infer_fluent_signature_from_usage(knowledge, f)
            print(f"  Warning: Inferred signature for fluent '{f}': {sig}")
        
        # Clean signature - replace Unknown with object
        cleaned_sig = []
        for typ in sig:
            if typ == "Unknown":
                cleaned_sig.append("object")  # Fallback to object for Unknown
            else:
                cleaned_sig.append(typ)
        
        # FIXED: Use the new resolve function
        params = []
        for i, typ in enumerate(cleaned_sig):
            var = f"p{i}"
            resolved_type = resolve_fluent_parameter_type(typ, knowledge, created_additional_types, wp)
            params.append(f"{var}={resolved_type}")
        
        params_str = ", ".join(params)
        wp(f"{f} = Fluent('{f}', BoolType(){', ' + params_str if params_str else ''})")
    wp("")

    # 6) Problem and initial fluents
    wp("problem = Problem('from_prolog')")
    for f in all_fluents:
        wp(f"problem.add_fluent({f}, default_initial_value=False)")
    wp("")

    # 7) Objects
    all_objects_to_create = set()
    
    # Get string objects from knowledge
    string_objects = extract_string_objects_from_knowledge(knowledge)
    all_objects_to_create.update(string_objects)
    
    # Create objects
    objects_created = []
    for obj in sorted(all_objects_to_create):
        # FIXED: Get effective type with better fallback
        effective_type = get_effective_type_for_object(obj, knowledge, supertype_objects)
        
        # FIXED: Handle the case where effective_type is "object"
        if effective_type == "object":
            if "object" not in created_additional_types:
                wp("ObjectType = UserType('object')")
                created_additional_types.add("object")
            effective_type = "ObjectType"
        
        wp(f"{obj} = Object('{obj}', {effective_type})")
        objects_created.append(obj)
    
    # Add objects to problem
    wp("problem.add_objects([")
    for obj in objects_created:
        wp(f"    {obj},")
    wp("])")
    wp("")

    # 8) Initial state (numbers already converted)
    for pred in knowledge["init_state"]:
        name = pred["name"]
        args = ", ".join(pred["args"])
        wp(f"problem.set_initial_value({name}({args}), True)")
    wp("")

    # 9) Goal state (numbers already converted)
    for pred in knowledge["goal_state"]:
        name = pred["name"]
        args = ", ".join(pred["args"])
        wp(f"problem.add_goal({name}({args}))")
    wp("")

    # 10) Actions (numbers already converted)
    for act in knowledge["actions"]:
        name = act["name"]
        params = act["parameters"]
        types = act["type_constraints"]
        
        # Debug information
        print(f"\nDEBUG: Processing action {name}")
        print(f"  Parameters: {params}")
        print(f"  Type constraints: {types}")
        
        # Check for missing types and try to infer them
        missing_types = []
        for p in params:
            if p not in types or types[p] == "Unknown":
                missing_types.append(p)
                print(f"  WARNING: Parameter {p} has no type constraint or Unknown type!")
        
        # Try to infer missing types
        if missing_types:
            print(f"  Attempting to infer types for: {missing_types}")
            for missing_param in missing_types:
                # Try to infer from preconditions
                inferred_type = None
                
                # Check preconditions
                for pre in act.get("preconditions", []):
                    if missing_param in pre["args"]:
                        idx = pre["args"].index(missing_param)
                        fluent_name = pre["name"]
                        if fluent_name in knowledge["fluent_signatures"]:
                            sig = knowledge["fluent_signatures"][fluent_name]
                            if idx < len(sig) and sig[idx] != "Unknown":
                                inferred_type = sig[idx]
                                break
                
                # Check add effects
                if not inferred_type:
                    for eff in act.get("add_effects", []):
                        if missing_param in eff["args"]:
                            idx = eff["args"].index(missing_param)
                            fluent_name = eff["name"]
                            if fluent_name in knowledge["fluent_signatures"]:
                                sig = knowledge["fluent_signatures"][fluent_name]
                                if idx < len(sig) and sig[idx] != "Unknown":
                                    inferred_type = sig[idx]
                                    break
                
                # Check delete effects
                if not inferred_type:
                    for eff in act.get("del_effects", []):
                        if missing_param in eff["args"]:
                            idx = eff["args"].index(missing_param)
                            fluent_name = eff["name"]
                            if fluent_name in knowledge["fluent_signatures"]:
                                sig = knowledge["fluent_signatures"][fluent_name]
                                if idx < len(sig) and sig[idx] != "Unknown":
                                    inferred_type = sig[idx]
                                    break
                
                if inferred_type:
                    print(f"    Inferred type for {missing_param}: {inferred_type}")
                    types[missing_param] = inferred_type
                else:
                    print(f"    Could not infer type for {missing_param}, using 'object'")
                    types[missing_param] = "object"
        
        # Resolve types using supertypes
        types = resolve_parameter_types_for_supertypes(knowledge, act)
        
        wp(f"# --- action {name}")
        
        # Generate action signature
        sig_parts = []
        for p in params:
            param_type = types.get(p, 'object')
            if param_type == "Unknown":
                param_type = "object"
            
            # FIXED: Handle supertypes correctly
            if param_type in knowledge.get("supertypes", {}):
                sig_parts.append(f"{p}={param_type}")  # Supertype name as-is
            else:
                sig_parts.append(f"{p}={param_type.capitalize()}")  # Capitalize regular types
        
        sig = ", ".join(sig_parts)
        wp(f"{name} = InstantaneousAction('{name}', {sig})")
        
        # Generate parameter references
        for p in params:
            wp(f"{p} = {name}.parameter('{p}')")
        
        # Positive preconditions
        for pre in act.get("preconditions", []):
            pname = pre["name"]
            pargs = ", ".join(pre["args"])
            wp(f"{name}.add_precondition({pname}({pargs}))")
        
        # Negative preconditions with generalized handling
        neg_precond_lines = generate_up_code_negative_preconditions_section(knowledge, name, act)
        for line in neg_precond_lines:
            wp(line)
        
        # Add constraint for parameters of same type
        type_to_params = {}
        for p in params:
            param_type = types.get(p, 'object')
            if param_type == "Unknown":
                param_type = "object"
            
            if param_type not in type_to_params:
                type_to_params[param_type] = []
            type_to_params[param_type].append(p)
        
        # Add inequality constraints for same-type parameters
        for param_type, param_list in type_to_params.items():
            if len(param_list) > 1:
                # Add inequality constraints
                for i in range(len(param_list)):
                    for j in range(i + 1, len(param_list)):
                        wp(f"{name}.add_precondition(Not(Equals({param_list[i]}, {param_list[j]})))")
        
        # Delete effects
        for eff in act.get("del_effects", []):
            ename = eff["name"]
            eargs = ", ".join(eff["args"])
            wp(f"{name}.add_effect({ename}({eargs}), False)")
        
        # Add effects
        for eff in act.get("add_effects", []):
            ename = eff["name"]
            eargs = ", ".join(eff["args"])
            wp(f"{name}.add_effect({ename}({eargs}), True)")
        
        # Add action to problem
        wp(f"problem.add_action({name})")
        wp("")

    # 11) Export PDDL
    # wp("writer = PDDLWriter(problem)")
    # wp("writer.write_domain('generated_domain.pddl')")
    # wp("writer.write_problem('generated_problem.pddl')")
    # wp("print('Generated PDDL files in current directory')")

    return "\n".join(lines)


if __name__ == "__main__":
    # Handle standalone execution
    json_file = "extracted_knowledge.json"
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found in current directory")
        sys.exit(1)
        
    # Load knowledge from JSON
    with open(json_file) as f:
        knowledge = json.load(f)
    
    # Generate UP code
    code = generate_up_code(knowledge, ".")
    with open('generated_up.py', 'w') as f:
        f.write(code)
    print("Generated generated_up.py")