import os
from unified_planning.shortcuts import *
from unified_planning.model import Problem, Object, Fluent, InstantaneousAction, Variable
from unified_planning.io import PDDLWriter
import json

def infer_fluent_signature_from_usage(knowledge, fluent_name):
    """
    Infer fluent signature by looking at how it's used in actions.
    Returns a list of types for the fluent parameters.
    """
    # Look through all actions for usage of this fluent
    param_type_candidates = []
    
    for action in knowledge["actions"]:
        # Check preconditions
        for precond in action.get("preconditions", []):
            if precond["name"] == fluent_name:
                # Try to infer types from the arguments used
                types = []
                for arg in precond["args"]:
                    # If arg is a parameter name, look up its type
                    if arg in action["type_constraints"]:
                        types.append(action["type_constraints"][arg])
                    else:
                        types.append("Unknown")
                if types:
                    param_type_candidates.append(types)
        
        # Check negative preconditions
        for neg_precond in action.get("neg_preconditions", []):
            if neg_precond["name"] == fluent_name:
                types = []
                for arg in neg_precond["args"]:
                    if arg in action["type_constraints"]:
                        types.append(action["type_constraints"][arg])
                    else:
                        types.append("Unknown")
                if types:
                    param_type_candidates.append(types)
        
        # Check add effects
        for effect in action.get("add_effects", []):
            if effect["name"] == fluent_name:
                types = []
                for arg in effect["args"]:
                    if arg in action["type_constraints"]:
                        types.append(action["type_constraints"][arg])
                    else:
                        types.append("Unknown")
                if types:
                    param_type_candidates.append(types)
        
        # Check del effects
        for effect in action.get("del_effects", []):
            if effect["name"] == fluent_name:
                types = []
                for arg in effect["args"]:
                    if arg in action["type_constraints"]:
                        types.append(action["type_constraints"][arg])
                    else:
                        types.append("Unknown")
                if types:
                    param_type_candidates.append(types)
    
    # Return the most common signature found
    if param_type_candidates:
        # Find most common length
        lengths = [len(sig) for sig in param_type_candidates]
        if lengths:
            most_common_length = max(set(lengths), key=lengths.count)
            # Filter to signatures with most common length
            filtered = [sig for sig in param_type_candidates if len(sig) == most_common_length]
            
            # For each position, find most common type
            result = []
            for i in range(most_common_length):
                types_at_pos = [sig[i] for sig in filtered if i < len(sig)]
                if types_at_pos:
                    # Remove "Unknown" types if there are known types
                    known_types = [t for t in types_at_pos if t != "Unknown"]
                    if known_types:
                        most_common = max(set(known_types), key=known_types.count)
                    else:
                        most_common = "Unknown"
                    result.append(most_common)
            
            return result
    
    # Default fallback
    return ["Unknown"]

def generate_up_code(knowledge, out_dir="RESULTS"):
    os.makedirs(out_dir, exist_ok=True)
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
    wp("from unified_planning.model.operators import OperatorKind")
    wp("from unified_planning.shortcuts import *")
    wp("up.shortcuts.get_environment().credits_stream = None")
    wp("")

    # 2) Tipi (UserType)
    for t, instances in knowledge["types"].items():
        wp(f"{t.capitalize()} = UserType('{t}')")
    wp("")
    
    # Creazione del set per valori unici
    # Creazione del set per valori unici
    unique_types = set()

    # Accesso ai fluent_signatures
    for fluent_name, type_list in knowledge['fluent_signatures'].items():
        # Aggiungi ogni tipo al set
        unique_types.update(type_list)

    # Conversione finale in lista
    unique_types_list = list(unique_types)

    print(f"Tipi unici trovati: {unique_types_list}")

    for UT in unique_types_list:
        wp(f"{UT.capitalize()} = UserType('{UT}')")
    wp("")

    # 3) Fluents
    #    (uso fluent_signatures per i parametri)
    for f in knowledge["fluents"]:
        sig = knowledge["fluent_signatures"].get(f, [])
        
        # If signature not found, try to infer it
        if not sig:
            sig = infer_fluent_signature_from_usage(knowledge, f)
            print(f"  Warning: Inferred signature for fluent '{f}': {sig}")
        
        params = []
        for i, typ in enumerate(sig):
            var = f"p{i}"
            params.append(f"{var}={typ.capitalize()}")
        params_str = ", ".join(params)
        wp(f"{f} = Fluent('{f}', BoolType(){', ' + params_str if params_str else ''})")
    wp("")

    # 4) Problem e fluents iniziali
    wp("problem = Problem('from_prolog')")
    for f in knowledge["fluents"]:
        wp(f"problem.add_fluent({f}, default_initial_value=False)")
    wp("")

    # 5) Oggetti
    for t, instances in knowledge["types"].items():
        for inst in instances:
            wp(f"{inst} = Object('{inst}', {t.capitalize()})")
    wp("problem.add_objects([")
    for t, instances in knowledge["types"].items():
        for inst in instances:
            wp(f"    {inst},")
    wp("])")
    wp("")

    # 6) Stato iniziale
    for pred in knowledge["init_state"]:
        name = pred["name"]
        args = ", ".join(pred["args"])
        wp(f"problem.set_initial_value({name}({args}), True)")
    wp("")

    # 7) Goal state
    for pred in knowledge["goal_state"]:
        name = pred["name"]
        args = ", ".join(pred["args"])
        wp(f"problem.add_goal({name}({args}))")
    wp("")

    # 8) Azioni
    for act in knowledge["actions"]:
        name   = act["name"]
        params = act["parameters"]
        types  = act["type_constraints"]
        wp(f"# --- action {name}")
        # firma InstantaneousAction
        sig   = ", ".join(f"{p}={types[p].capitalize()}" for p in params)
        wp(f"{name} = InstantaneousAction('{name}', {sig})")
        # binding parametri
        for p in params:
            wp(f"{p} = {name}.parameter('{p}')")
        # precondizioni positive
        for pre in act.get("preconditions", []):
            pname = pre["name"]
            pargs = ", ".join(pre["args"])
            wp(f"{name}.add_precondition({pname}({pargs}))")
        # precondizioni negative
        for neg in act.get("neg_preconditions", []):
            pname   = neg["name"]
            pargs   = neg["args"]
            wilds   = set(neg.get("wildcard_positions", []))
            expr    = []
            vars_for_exists = []
            
            # Get fluent signature, with fallback
            fluent_sig = knowledge["fluent_signatures"].get(pname)
            if not fluent_sig:
                fluent_sig = infer_fluent_signature_from_usage(knowledge, pname)
                print(f"  Warning: Using inferred signature for negative precondition fluent '{pname}': {fluent_sig}")
            
            for i, a in enumerate(pargs):
                if i in wilds or a.startswith("_"):
                    var = f"any_{name}_{i}"
                    # Use inferred signature with bounds checking
                    if i < len(fluent_sig):
                        vtype = fluent_sig[i]
                    else:
                        vtype = "Unknown"
                        print(f"  Warning: No type info for position {i} in fluent '{pname}', using Unknown")
                    
                    wp(f"{var} = Variable('{var}', {vtype.capitalize()})")
                    expr.append(var)
                    vars_for_exists.append(var)
                else:
                    expr.append(a)
            wp(f"{name}.add_precondition(Not(Exists({pname}({', '.join(expr)}), {', '.join(vars_for_exists)})))")
        # effetti delete
        for eff in act.get("del_effects", []):
            ename = eff["name"]
            eargs = ", ".join(eff["args"])
            wp(f"{name}.add_effect({ename}({eargs}), False)")
        # effetti add
        for eff in act.get("add_effects", []):
            ename = eff["name"]
            eargs = ", ".join(eff["args"])
            wp(f"{name}.add_effect({ename}({eargs}), True)")
        # aggiungo azione al problema
        wp(f"problem.add_action({name})")
        wp("")

    # 9) Export PDDL
    wp("writer = PDDLWriter(problem)")
    wp(f"writer.write_domain(os.path.join('CONVERTER/GENERATED_BY_CONVERTED/generated_domain.pddl'))")
    wp(f"writer.write_problem(os.path.join('CONVERTER/GENERATED_BY_CONVERTED/generated_problem.pddl'))")
    wp("print('Generated PDDL files in', '" + out_dir + "')")

    return "\n".join(lines)

if __name__ == "__main__":
        # Ensure the /GENERATED directory exists
        os.makedirs('GENERATED_BY_CONVERTED', exist_ok=True)
        
        # Load knowledge from the extracted JSON
        with open('extracted_knowledge.json') as f:
            knowledge = json.load(f)
        
        # Generate and save the UP code
        code = generate_up_code(knowledge)
        with open('GENERATED_BY_CONVERTED/generated_up.py', 'w') as f:
            f.write(code)
        print("Generated generated_up.py")