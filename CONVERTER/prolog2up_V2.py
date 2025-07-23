import os
from unified_planning.shortcuts import *
from unified_planning.model import Problem, Object, Fluent, InstantaneousAction, Variable
from unified_planning.io import PDDLWriter
import json

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

                            inferred_type = _infer_type_from_structure(arg, knowledge)
                            types.append(inferred_type)
                            if inferred_type != "Unknown":
                                quality_score += 1
                    
                    if types:
                        combined_score = (quality_score / len(types)) * action_score
                        candidates_with_scores.append((types, combined_score, action["name"]))
    

    for state_section, section_name in [(knowledge["init_state"], "init"), (knowledge["goal_state"], "goal")]:
        for state_item in state_section:
            if state_item["name"] == fluent_name:
                types = []
                for arg in state_item["args"]:
                    inferred_type = _infer_type_from_structure(arg, knowledge)
                    types.append(inferred_type)
                
                if types:

                    candidates_with_scores.append((types, 1000, section_name))
    
    if not candidates_with_scores:
        return ["Unknown"]
    

    candidates_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    
    lengths = [len(c[0]) for c in candidates_with_scores]
    most_common_length = max(set(lengths), key=lengths.count)
    
    
    filtered = [c for c in candidates_with_scores if len(c[0]) == most_common_length]
    
    
    result = []
    for i in range(most_common_length):
        types_at_pos = [c[0][i] for c in filtered if i < len(c[0])]
        
        if types_at_pos:
            
            known_types = [t for t in types_at_pos if t != "Unknown"]
            if known_types:
                
                most_common = max(set(known_types), key=known_types.count)
                result.append(most_common)
            else:
                result.append("Unknown")
        else:
            result.append("Unknown")
    
    return result

def _infer_type_from_structure(arg, knowledge):
    """Inferisce il tipo di un argomento dalla sua struttura"""
    
    for type_name, instances in knowledge["types"].items():
        if arg in instances:
            return type_name
    
    
    if arg.isdigit() or (arg.replace('-', '').replace('.', '').isdigit()):
        return "pos"
    
    return "Unknown"


def _infer_wildcard_type_from_context(fluent_name, position, action, knowledge):
    """
    Inferisce il tipo di una wildcard anche i supertipi
    """

    for section in ("preconditions", "add_effects", "del_effects"):
        for item in action.get(section, []):
            if item["name"] == fluent_name and len(item["args"]) > position:
                arg_at_position = item["args"][position]
                if arg_at_position in action["type_constraints"]:
                    return action["type_constraints"][arg_at_position]
    
    if fluent_name in knowledge.get("fluent_signatures", {}):
        sig = knowledge["fluent_signatures"][fluent_name]
        if position < len(sig) and sig[position] != "Unknown":
            return sig[position]
    
    return "object"   # fallback 


def resolve_parameter_types_for_supertypes(knowledge, action):
    print(f"  Resolving supertypes for action {action['name']}")
    
    
    fluent_signatures = knowledge.get("fluent_signatures", {})
    supertypes = knowledge.get("supertypes", {})
    
    
    parameter_usage = {}  
    
    
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
    
    
    for section_name in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
        for pred in action.get(section_name, []):
            analyze_predicate_usage(pred)
    
    
    resolved_types = action["type_constraints"].copy()
    
    for param_name, required_types in parameter_usage.items():
        if len(required_types) > 1:
            
            for supertype_name, constituent_types in supertypes.items():
                
                if required_types.issubset(set(constituent_types)):
                    print(f"    Parameter {param_name}: {required_types} -> {supertype_name}")
                    resolved_types[param_name] = supertype_name
                    break
        elif len(required_types) == 1:
            required_type = list(required_types)[0]
            current_type = resolved_types.get(param_name, "Unknown")
            
            
            if required_type in supertypes:
                print(f"    Parameter {param_name}: {current_type} -> {required_type} (supertype)")
                resolved_types[param_name] = required_type
            
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
        
        
        fluent_sig = knowledge["fluent_signatures"].get(pname)
        if not fluent_sig:
            fluent_sig = infer_fluent_signature_from_usage(knowledge, pname)
        
        
        while len(fluent_sig) < len(pargs):
            fluent_sig.append("object")
        
        expr = []
        vars_for_exists = []
        
        for i, a in enumerate(pargs):
            if i in wilds or a.startswith("_"):
                var = f"any_{name}_{i}"
                
                
                if i < len(fluent_sig):
                    vtype = fluent_sig[i]
                    if vtype == "Unknown" or vtype is None:
                        vtype = _infer_wildcard_type_from_context(pname, i, act, knowledge)
                else:
                    vtype = _infer_wildcard_type_from_context(pname, i, act, knowledge)
                
                
                if vtype == "Unknown":
                    vtype = "object"
                
                
                if vtype in knowledge.get("supertypes", {}):
                    
                    type_name = vtype
                else:
                    
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
        
        if isinstance(value, str) and value.isdigit():
            return f"x{value}"
        elif isinstance(value, (int, float)):
            return f"x{int(value)}"
        return value
    
    def convert_predicate_args(pred):
        
        converted_pred = pred.copy()
        converted_pred["args"] = [convert_number_if_needed(arg) for arg in pred["args"]]
        return converted_pred
    
    def convert_action_args(action):
        
        converted_action = action.copy()
        
        for section in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
            if section in converted_action:
                converted_action[section] = [
                    convert_predicate_args(pred) for pred in converted_action[section]
                ]
        
        return converted_action
    
    # Converti init_state
    knowledge["init_state"] = [convert_predicate_args(pred) for pred in knowledge["init_state"]]
    
    # Converti goal_state  
    knowledge["goal_state"] = [convert_predicate_args(pred) for pred in knowledge["goal_state"]]
    
    # Converti azioni
    knowledge["actions"] = [convert_action_args(action) for action in knowledge["actions"]]
    
    return knowledge


def extract_string_objects_from_knowledge(knowledge):
    """
    Estrae tutti gli oggetti stringa (inclusi quelli convertiti da numeri)
    dal knowledge per creare gli oggetti UP necessari.
    """
    string_objects = set()
    
    
    for state_section in [knowledge["init_state"], knowledge["goal_state"]]:
        for pred in state_section:
            for arg in pred["args"]:
                if (isinstance(arg, str) and 
                    not arg.startswith("Param") and
                    not arg.startswith("_")):
                    string_objects.add(arg)
    
    
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
        
        supertype_lines.append(f"{supertype_name} = UserType('{supertype_name.lower()}')")
        print(f"Created supertype: {supertype_name} = {constituent_types}")
        
        # Raccogli tutti gli oggetti che appartengono a questo supertipo
        supertype_instances = []
        
        
        for constituent_type in constituent_types:
            if constituent_type in knowledge["types"]:
                for instance in knowledge["types"][constituent_type]:
                    if isinstance(instance, str):
                        supertype_instances.append(instance)
        
        supertype_objects[supertype_name] = supertype_instances
        print(f"  Instances: {supertype_instances}")
    
    print("=== END SUPERTYPE GENERATION ===\n")
    
    return supertype_lines, supertype_objects


#TODO  ricontrolla
def get_effective_type_for_object(obj_name, knowledge, supertype_objects):
    """
    Determina il tipo effettivo di un oggetto, considerando i supertipi.
    """
    
    for supertype_name, instances in supertype_objects.items():
        if obj_name in instances:
            return supertype_name
    
    
    for type_name, instances in knowledge["types"].items():
        if obj_name in instances:
            return type_name.capitalize()
    
    
    if obj_name.startswith("x") and obj_name[1:].isdigit():
        return "Pos"
    
    # Fallback ad "Object" se non trovato
    available_types = list(knowledge["types"].keys())
    if available_types:
        return available_types[0].capitalize()
    
    return "Object"


def generate_up_code(knowledge, out_dir):
    """Generate UP code with polymorphic fluent support"""
    
    
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

    # 2) Tipi originali (UserType)
    for t, instances in knowledge["types"].items():
        wp(f"{t.capitalize()} = UserType('{t}')")
    wp("")
    
    # 3) Genera supertipi se presenti
    supertype_lines, supertype_objects = generate_supertype_definitions(knowledge)
    for line in supertype_lines:
        wp(line)
    if supertype_lines:
        wp("")
    
    # 4) Tipi aggiuntivi dai fluent signatures
    unique_types = set()
    for fluent_name, type_list in knowledge['fluent_signatures'].items():
        unique_types.update(type_list)

    # Rimuovi "Unknown" dai tipi e aggiungi tipi mancanti comuni
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
        
        
        supertype_names = set(knowledge.get("supertypes", {}).keys())
        if ut_lower not in existing_types and UT not in supertype_names:
            wp(f"{UT.capitalize()} = UserType('{ut_lower}')")
    wp("")

    # 5) Fluents con firme che supportano supertipi
    for f in knowledge["fluents"]:
        sig = knowledge["fluent_signatures"].get(f, [])
        
        # Se signature non trovata, prova a inferirla
        if not sig:
            sig = infer_fluent_signature_from_usage(knowledge, f)
            print(f"  Warning: Inferred signature for fluent '{f}': {sig}")
        

        cleaned_sig = []
        for typ in sig:
            if typ == "Unknown":
                cleaned_sig.append("object")  # Fallback a object per Unknown
            else:
                cleaned_sig.append(typ)
        
        params = []
        for i, typ in enumerate(cleaned_sig):
            var = f"p{i}"
            if typ in knowledge.get("supertypes", {}):
                params.append(f"{var}={typ}")  
            else:
                params.append(f"{var}={typ.capitalize()}") 
        
        params_str = ", ".join(params)
        wp(f"{f} = Fluent('{f}', BoolType(){', ' + params_str if params_str else ''})")
    wp("")

    # 6) Problem e fluents iniziali
    wp("problem = Problem('from_prolog')")
    for f in knowledge["fluents"]:
        wp(f"problem.add_fluent({f}, default_initial_value=False)")
    wp("")

    # 7) Oggetti
    all_objects_to_create = set()
    
    
    string_objects = extract_string_objects_from_knowledge(knowledge)
    all_objects_to_create.update(string_objects)
    
    
    objects_created = []
    for obj in sorted(all_objects_to_create):
        
        effective_type = get_effective_type_for_object(obj, knowledge, supertype_objects)
        
        wp(f"{obj} = Object('{obj}', {effective_type})")
        objects_created.append(obj)
    
    
    wp("problem.add_objects([")
    for obj in objects_created:
        wp(f"    {obj},")
    wp("])")
    wp("")

    # 8) Stato iniziale (numeri già convertiti)
    for pred in knowledge["init_state"]:
        name = pred["name"]
        args = ", ".join(pred["args"])
        wp(f"problem.set_initial_value({name}({args}), True)")
    wp("")

    # 9) Goal state (numeri già convertiti)
    for pred in knowledge["goal_state"]:
        name = pred["name"]
        args = ", ".join(pred["args"])
        wp(f"problem.add_goal({name}({args}))")
    wp("")

    # 10) Azioni (numeri già convertiti)
    for act in knowledge["actions"]:
        name = act["name"]
        params = act["parameters"]
        types = act["type_constraints"]
        
        
        print(f"\nDEBUG: Processing action {name}")
        print(f"  Parameters: {params}")
        print(f"  Type constraints: {types}")
        
        
        missing_types = []
        for p in params:
            if p not in types or types[p] == "Unknown":
                missing_types.append(p)
                print(f"  WARNING: Parameter {p} has no type constraint or Unknown type!")
        
        
        if missing_types:
            print(f"  Attempting to infer types for: {missing_types}")
            for missing_param in missing_types:
                
                inferred_type = None
                
                
                for pre in act.get("preconditions", []):
                    if missing_param in pre["args"]:
                        idx = pre["args"].index(missing_param)
                        fluent_name = pre["name"]
                        if fluent_name in knowledge["fluent_signatures"]:
                            sig = knowledge["fluent_signatures"][fluent_name]
                            if idx < len(sig) and sig[idx] != "Unknown":
                                inferred_type = sig[idx]
                                break
                
                
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
        
        
        types = resolve_parameter_types_for_supertypes(knowledge, act)
        
        wp(f"# --- action {name}")
        
        
        sig_parts = []
        for p in params:
            param_type = types.get(p, 'object')
            if param_type == "Unknown":
                param_type = "object"
            
            
            
            if param_type in knowledge.get("supertypes", {}):
                sig_parts.append(f"{p}={param_type}")  
            else:
                sig_parts.append(f"{p}={param_type.capitalize()}")  
        
        sig = ", ".join(sig_parts)
        wp(f"{name} = InstantaneousAction('{name}', {sig})")
        
        
        for p in params:
            wp(f"{p} = {name}.parameter('{p}')")
        
        # Precondizioni positive
        for pre in act.get("preconditions", []):
            pname = pre["name"]
            pargs = ", ".join(pre["args"])
            wp(f"{name}.add_precondition({pname}({pargs}))")
        
        # Precondizioni negative con gestione generalizzata
        neg_precond_lines = generate_up_code_negative_preconditions_section(knowledge, name, act)
        for line in neg_precond_lines:
            wp(line)
        
        
        
        type_to_params = {}
        for p in params:
            param_type = types.get(p, 'object')
            if param_type == "Unknown":
                param_type = "object"
            
            if param_type not in type_to_params:
                type_to_params[param_type] = []
            type_to_params[param_type].append(p)
        
        
        for param_type, param_list in type_to_params.items():
            if len(param_list) > 1:
                
                for i in range(len(param_list)):
                    for j in range(i + 1, len(param_list)):
                        wp(f"{name}.add_precondition(Not(Equals({param_list[i]}, {param_list[j]})))")
        
        # Effetti delete
        for eff in act.get("del_effects", []):
            ename = eff["name"]
            eargs = ", ".join(eff["args"])
            wp(f"{name}.add_effect({ename}({eargs}), False)")
        
        # Effetti add
        for eff in act.get("add_effects", []):
            ename = eff["name"]
            eargs = ", ".join(eff["args"])
            wp(f"{name}.add_effect({ename}({eargs}), True)")
        
        # Aggiungi azione al problema
        wp(f"problem.add_action({name})")
        wp("")

    # 11) Export PDDL
    wp("writer = PDDLWriter(problem)")
    wp("writer.write_domain('generated_domain.pddl')")
    wp("writer.write_problem('generated_problem.pddl')")
    wp("print('Generated PDDL files in current directory')")

    return "\n".join(lines)


if __name__ == "__main__":
        
        json_file = "extracted_knowledge.json"
        if not os.path.exists(json_file):
            print(f"Error: {json_file} not found in current directory")
            sys.exit(1)
            
        
        with open(json_file) as f:
            knowledge = json.load(f)
        
        
        code = generate_up_code(knowledge, ".")
        with open('generated_up.py', 'w') as f:
            f.write(code)
        print("Generated generated_up.py")