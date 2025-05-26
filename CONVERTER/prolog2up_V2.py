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
                            # Prova a inferire il tipo dalla struttura
                            inferred_type = _infer_type_from_structure(arg, knowledge)
                            types.append(inferred_type)
                            if inferred_type != "Unknown":
                                quality_score += 1
                    
                    if types:
                        combined_score = (quality_score / len(types)) * action_score
                        candidates_with_scores.append((types, combined_score, action["name"]))
    
    # Aggiungi anche analisi da init_state e goal_state (alta priorità)
    for state_section, section_name in [(knowledge["init_state"], "init"), (knowledge["goal_state"], "goal")]:
        for state_item in state_section:
            if state_item["name"] == fluent_name:
                types = []
                for arg in state_item["args"]:
                    inferred_type = _infer_type_from_structure(arg, knowledge)
                    types.append(inferred_type)
                
                if types:
                    # Alto score per definizioni di stato
                    candidates_with_scores.append((types, 1000, section_name))
    
    if not candidates_with_scores:
        return ["Unknown"]
    
    # Ordina per score
    candidates_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Trova la lunghezza più comune
    lengths = [len(c[0]) for c in candidates_with_scores]
    most_common_length = max(set(lengths), key=lengths.count)
    
    # Filtra per lunghezza più comune
    filtered = [c for c in candidates_with_scores if len(c[0]) == most_common_length]
    
    # Per ogni posizione, trova il tipo migliore
    result = []
    for i in range(most_common_length):
        types_at_pos = [c[0][i] for c in filtered if i < len(c[0])]
        
        if types_at_pos:
            # Rimuovi Unknown se ci sono alternative
            known_types = [t for t in types_at_pos if t != "Unknown"]
            if known_types:
                # Tipo più comune tra quelli conosciuti
                most_common = max(set(known_types), key=known_types.count)
                result.append(most_common)
            else:
                result.append("Unknown")
        else:
            result.append("Unknown")
    
    return result

def _infer_type_from_structure(arg, knowledge):
    """Inferisce il tipo di un argomento dalla sua struttura, senza assunzioni"""
    
    # Controlla se è un oggetto conosciuto dai types estratti
    for type_name, instances in knowledge["types"].items():
        if arg in instances:
            return type_name
    
    # Controlla se sembra numerico (posizione/coordinata)
    if arg.isdigit() or (arg.replace('-', '').replace('.', '').isdigit()):
        return "pos"
    
    # Se non riusciamo a determinarlo
    return "Unknown"


def _infer_wildcard_type_from_context(fluent_name, position, action, knowledge):
    """
    Inferisce il tipo di una wildcard dal contesto, completamente generalizzato
    """
    # Cerca lo stesso fluent in altre parti dell'azione
    for section in ("preconditions", "add_effects", "del_effects"):
        for item in action.get(section, []):
            if item["name"] == fluent_name and len(item["args"]) > position:
                arg_at_position = item["args"][position]
                if arg_at_position in action["type_constraints"]:
                    return action["type_constraints"][arg_at_position]
    
    # Cerca nella signature del fluent se disponibile
    if fluent_name in knowledge.get("fluent_signatures", {}):
        sig = knowledge["fluent_signatures"][fluent_name]
        if position < len(sig) and sig[position] != "Unknown":
            return sig[position]
    
    # Analizza pattern dai types estratti
    available_types = list(knowledge["types"].keys())
    
    # Se abbiamo tipi disponibili, usa euristica basata sulla posizione
    if available_types:
        # Prima posizione spesso è agente o oggetto principale
        if position == 0 and "agent" in available_types:
            return "agent"
        # Posizioni numeriche spesso sono posizioni
        elif position >= 2 and "pos" in [t.lower() for t in available_types]:
            return "pos"
        # Altrimenti usa il tipo più comune
        else:
            # Trova il tipo con più istanze
            type_with_most_instances = max(knowledge["types"].items(), key=lambda x: len(x[1]))
            return type_with_most_instances[0]
    
    return "object"  # Fallback finale


def generate_up_code_negative_preconditions_section(knowledge, name, act):
    """
    Genera la sezione delle precondizioni negative in modo generalizzato
    """
    lines = []
    
    for neg in act.get("neg_preconditions", []):
        pname = neg["name"]
        pargs = neg["args"]
        wilds = set(neg.get("wildcard_positions", []))
        
        # Ottieni la signature del fluent
        fluent_sig = knowledge["fluent_signatures"].get(pname)
        if not fluent_sig:
            fluent_sig = infer_fluent_signature_from_usage(knowledge, pname)
        
        # Estendi la signature se necessario
        while len(fluent_sig) < len(pargs):
            fluent_sig.append("object")
        
        expr = []
        vars_for_exists = []
        
        for i, a in enumerate(pargs):
            if i in wilds or a.startswith("_"):
                var = f"any_{name}_{i}"
                
                # Determina il tipo per la wildcard
                if i < len(fluent_sig):
                    vtype = fluent_sig[i]
                    if vtype == "Unknown" or vtype is None:
                        vtype = _infer_wildcard_type_from_context(pname, i, act, knowledge)
                else:
                    vtype = _infer_wildcard_type_from_context(pname, i, act, knowledge)
                
                # Assicurati che il tipo sia valido
                if vtype == "Unknown":
                    vtype = "object"
                
                lines.append(f"{var} = Variable('{var}', {vtype.capitalize()})")
                expr.append(var)
                vars_for_exists.append(var)
            else:
                expr.append(a)
        
        if vars_for_exists:
            lines.append(f"{name}.add_precondition(Not(Exists({pname}({', '.join(expr)}), {', '.join(vars_for_exists)})))")
        else:
            lines.append(f"{name}.add_precondition(Not({pname}({', '.join(expr)})))")
    
    return lines


def generate_up_code(knowledge, out_dir):
    """Generate UP code with proper output directory handling and improved wildcard management"""
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
    
    # Creazione del set per valori unici dalle firme dei fluent
    unique_types = set()
    for fluent_name, type_list in knowledge['fluent_signatures'].items():
        unique_types.update(type_list)

    # Rimuovi "Unknown" dai tipi e aggiungi tipi mancanti comuni
    unique_types.discard("Unknown")
    unique_types.add("pos")  # Assicurati che 'pos' sia incluso
    unique_types_list = list(unique_types)

    print(f"Tipi unici trovati: {unique_types_list}")

    for UT in unique_types_list:
        if UT not in knowledge["types"]:  # Non ridefinire tipi già esistenti
            wp(f"{UT.capitalize()} = UserType('{UT}')")
    wp("")

    # 3) Fluents con firme migliorate
    for f in knowledge["fluents"]:
        sig = knowledge["fluent_signatures"].get(f, [])
        
        # Se signature non trovata, prova a inferirla
        if not sig:
            sig = infer_fluent_signature_from_usage(knowledge, f)
            print(f"  Warning: Inferred signature for fluent '{f}': {sig}")
        
        # Pulisci la signature da tipi Unknown
        cleaned_sig = []
        for typ in sig:
            if typ == "Unknown":
                cleaned_sig.append("object")  # Fallback a object per Unknown
            else:
                cleaned_sig.append(typ)
        
        params = []
        for i, typ in enumerate(cleaned_sig):
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

    # 5) Estrai e crea oggetti per le posizioni
    coordinates = extract_position_coordinates(knowledge)
    pos_objects, pos_creation_lines = create_position_objects(coordinates)
    
    print(f"Found coordinates: {coordinates}")
    print(f"Created position objects: {pos_objects}")

    # 6) Oggetti (inclusi quelli delle posizioni)
    for t, instances in knowledge["types"].items():
        for inst in instances:
            # Evita oggetti con nomi problematici
            if isinstance(inst, str) and not any(char in str(inst) for char in ['(', ')', '_', ' ']):
                wp(f"{inst} = Object('{inst}', {t.capitalize()})")
    
    # Aggiungi oggetti posizione
    for line in pos_creation_lines:
        wp(line)
    
    wp("problem.add_objects([")
    for t, instances in knowledge["types"].items():
        for inst in instances:
            if isinstance(inst, str) and not any(char in str(inst) for char in ['(', ')', '_', ' ']):
                wp(f"    {inst},")
    
    # Aggiungi oggetti posizione alla lista
    for coord in coordinates:
        wp(f"    pos_{coord},")
    
    wp("])")
    wp("")

    # 7) Stato iniziale con sostituzione coordinate
    for pred in knowledge["init_state"]:
        # Sostituisci coordinate con oggetti Pos se necessario
        updated_pred = replace_coordinates_in_predicate(pred, pos_objects)
        name = updated_pred["name"]
        args = ", ".join(updated_pred["args"])
        wp(f"problem.set_initial_value({name}({args}), True)")
    wp("")

    # 8) Goal state con sostituzione coordinate
    for pred in knowledge["goal_state"]:
        # Sostituisci coordinate con oggetti Pos se necessario
        updated_pred = replace_coordinates_in_predicate(pred, pos_objects)
        name = updated_pred["name"]
        args = ", ".join(updated_pred["args"])
        wp(f"problem.add_goal({name}({args}))")
    wp("")

    # 9) Azioni (resta invariato)
    for act in knowledge["actions"]:
        name = act["name"]
        params = act["parameters"]
        types = act["type_constraints"]
        
        wp(f"# --- action {name}")
        
        # Firma InstantaneousAction
        sig = ", ".join(f"{p}={types[p].capitalize()}" for p in params)
        wp(f"{name} = InstantaneousAction('{name}', {sig})")
        
        # Binding parametri
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

    # 10) Export PDDL
    wp("writer = PDDLWriter(problem)")
    wp("writer.write_domain('generated_domain.pddl')")
    wp("writer.write_problem('generated_problem.pddl')")
    wp("print('Generated PDDL files in current directory')")

    return "\n".join(lines)

def extract_position_coordinates(knowledge):
    """
    Estrae tutte le coordinate numeriche uniche da init_state e goal_state
    per creare gli oggetti Pos necessari.
    """
    coordinates = set()
    
    # Analizza init_state e goal_state per trovare coordinate in fluent 'at'
    for state_section in [knowledge["init_state"], knowledge["goal_state"]]:
        for pred in state_section:
            if pred["name"] == "at" and len(pred["args"]) >= 3:
                # Estrai le coordinate (assumendo che siano nelle posizioni 1 e 2)
                for coord in pred["args"][1:]:  # Salta il primo argomento (object)
                    if coord.isdigit() or (coord.replace('-', '').replace('.', '').isdigit()):
                        coordinates.add(coord)
    
    return sorted(coordinates, key=lambda x: int(x))


def create_position_objects(coordinates):
    """
    Crea gli oggetti Pos per ogni coordinata unica
    """
    pos_objects = {}
    pos_creation_lines = []
    
    for coord in coordinates:
        pos_name = f"pos_{coord}"
        pos_objects[coord] = pos_name
        pos_creation_lines.append(f"{pos_name} = Object('{pos_name}', Pos)")
    
    return pos_objects, pos_creation_lines


def replace_coordinates_in_predicate(pred, pos_objects):
    """
    Sostituisce le coordinate numeriche con oggetti Pos in un predicato
    """
    if pred["name"] == "at" and len(pred["args"]) >= 3:
        # Sostituisci solo le coordinate (posizioni 1 e successive)
        new_args = [pred["args"][0]]  # Mantieni il primo argomento (object)
        
        for coord in pred["args"][1:]:
            if coord in pos_objects:
                new_args.append(pos_objects[coord])
            else:
                new_args.append(coord)  # Mantieni come era se non è una coordinata
        
        return {
            "name": pred["name"],
            "args": new_args
        }
    
    return pred 

if __name__ == "__main__":
        # For standalone execution - look for JSON in current directory
        json_file = "extracted_knowledge.json"
        if not os.path.exists(json_file):
            print(f"Error: {json_file} not found in current directory")
            sys.exit(1)
            
        # Load knowledge from the extracted JSON
        with open(json_file) as f:
            knowledge = json.load(f)
        
        # Generate and save the UP code in current directory
        code = generate_up_code(knowledge, ".")
        with open('generated_up.py', 'w') as f:
            f.write(code)
        print("Generated generated_up.py")