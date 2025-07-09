import json
import re
import os

def synchronize_fluent_usage_after_signature_resolution(knowledge):
    """
    Dopo aver risolto le signature, sincronizza TUTTI gli usi dei fluent
    per garantire consistenza tra neg_preconditions, preconditions, e effects.
    """
    fluent_signatures = knowledge.get("fluent_signatures", {})
    
    print("\n=== SYNCHRONIZING FLUENT USAGE ===")
    
    for action in knowledge["actions"]:
        action_name = action["name"]
        type_constraints = action.get("type_constraints", {})
        
        # Per ogni sezione, controlla e sincronizza l'uso dei fluent
        for section_name in ["neg_preconditions", "preconditions", "add_effects", "del_effects"]:
            section_data = action.get(section_name, [])
            
            for item_idx, item in enumerate(section_data):
                fluent_name = item["name"]
                current_args = item["args"]
                
                # Se questo fluent ha una signature risolta
                if fluent_name in fluent_signatures:
                    expected_length = len(fluent_signatures[fluent_name])
                    current_length = len(current_args)
                    
                    if current_length != expected_length:
                        print(f"  MISMATCH in {action_name}.{section_name}: {fluent_name}")
                        print(f"    Current: {current_length} args, Expected: {expected_length} args")
                        print(f"    Current args: {current_args}")
                        
                        # Prova a ricostruire gli argomenti corretti
                        corrected_args = _reconstruct_fluent_args(
                            fluent_name, 
                            current_args, 
                            expected_length,
                            action,
                            section_name
                        )
                        
                        if corrected_args:
                            print(f"    Corrected args: {corrected_args}")
                            
                            # Aggiorna gli argomenti
                            section_data[item_idx]["args"] = corrected_args
                            
                            # Se è una neg_precondition, aggiorna anche le wildcard_positions
                            if section_name == "neg_preconditions":
                                wildcard_positions = []
                                for pos, arg in enumerate(corrected_args):
                                    if arg.startswith("_") or arg.startswith("any_"):
                                        wildcard_positions.append(pos)
                                section_data[item_idx]["wildcard_positions"] = wildcard_positions
                                print(f"    Updated wildcard_positions: {wildcard_positions}")
                        else:
                            print(f"    Could not reconstruct args for {fluent_name}")
    
    print("=== END SYNCHRONIZATION ===\n")
    return knowledge


def _reconstruct_fluent_args(fluent_name, current_args, expected_length, action, section_name):
    """
    Ricostruisce gli argomenti corretti per un fluent basandosi sulla signature attesa
    e sul contesto dell'azione.
    """
    type_constraints = action.get("type_constraints", {})
    
    # Se la lunghezza è già corretta, non fare nulla
    if len(current_args) == expected_length:
        return current_args
    
    # Strategia 1: Cerca lo stesso fluent nell'add_effects (più autoritativo)
    if section_name != "add_effects":
        for add_eff in action.get("add_effects", []):
            if add_eff["name"] == fluent_name and len(add_eff["args"]) == expected_length:
                # Usa la struttura dall'add_effect come template
                template_args = add_eff["args"]
                corrected_args = []
                
                for i, template_arg in enumerate(template_args):
                    if i < len(current_args):
                        current_arg = current_args[i]
                        
                        # Se current_arg è un parametro valido, usalo
                        if current_arg.startswith("Param") and current_arg in type_constraints:
                            corrected_args.append(current_arg)
                        # Se current_arg è wildcard, mantienilo
                        elif current_arg.startswith("_"):
                            corrected_args.append(current_arg)
                        # Altrimenti usa il template
                        else:
                            if template_arg.startswith("Param") and template_arg in type_constraints:
                                # Se il template arg esiste nei constraints, usalo
                                corrected_args.append(template_arg)
                            else:
                                # Genera una wildcard
                                corrected_args.append(f"_{i}")
                    else:
                        # Argomento mancante - usa dal template o genera wildcard
                        if template_arg.startswith("Param") and template_arg in type_constraints:
                            corrected_args.append(template_arg)
                        else:
                            corrected_args.append(f"_{i}")
                
                return corrected_args
    
    # Strategia 2: Estendi con wildcard se troppo corto
    if len(current_args) < expected_length:
        corrected_args = current_args.copy()
        for i in range(len(current_args), expected_length):
            corrected_args.append(f"_{i}")
        return corrected_args
    
    # Strategia 3: Tronca se troppo lungo
    if len(current_args) > expected_length:
        return current_args[:expected_length]
    
    return None

def parse_predicate(pred_str):
    """
    Parse a predicate string of the form 'name(arg1,arg2,...)'
    and return a dict: {'name': name, 'args': [arg1, arg2, ...]}.
    """
    m = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*(.*?)\s*\)\s*$', pred_str)
    if not m:
        # zero‐arity
        return {"name": pred_str.strip(), "args": []}
    name, args_str = m.group(1), m.group(2).strip()
    args = [a.strip() for a in args_str.split(',')] if args_str else []
    return {"name": name, "args": args}

def infer_missing_types(acts, fluent_sigs):
    """
    Inferisce i tipi mancanti in modo completamente generalizzato,
    senza assunzioni hard-coded sui domini specifici.
    """
    
    # Prima passata: raccogli tutte le informazioni sui tipi già disponibili
    all_param_type_info = {}  # param_name -> set of possible types
    
    for act in acts:
        tdict = act["type_constraints"]
        
        # Raccogli tutti i tipi già noti
        for param, ptype in tdict.items():
            if param not in all_param_type_info:
                all_param_type_info[param] = set()
            if ptype != "Unknown":
                all_param_type_info[param].add(ptype)
    
    # Seconda passata: analizza l'uso dei parametri nei fluent
    for act in acts:
        tdict = act["type_constraints"]
        
        for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
            for pred in act.get(section, []):
                fname = pred["name"]
                sig = fluent_sigs.get(fname, [])
                
                for idx, arg in enumerate(pred["args"]):
                    if not arg.startswith("Param"):
                        continue
                    
                    # Se la firma ha informazioni per questa posizione
                    if idx < len(sig) and sig[idx] != "Unknown":
                        if arg not in all_param_type_info:
                            all_param_type_info[arg] = set()
                        all_param_type_info[arg].add(sig[idx])
    
    # Terza passata: propaga le informazioni raccolte
    for act in acts:
        tdict = act["type_constraints"]
        
        for param in act["parameters"]:
            if param in tdict and tdict[param] != "Unknown":
                continue
            
            # Usa le informazioni raccolte
            if param in all_param_type_info and all_param_type_info[param]:
                type_candidates = list(all_param_type_info[param])
                if len(type_candidates) == 1:
                    tdict[param] = type_candidates[0]
                else:
                    # Scegli il tipo più appropriato basandosi sul contesto
                    best_type = _select_best_type_for_param(param, act, fluent_sigs, type_candidates)
                    tdict[param] = best_type
            else:
                # Analisi del contesto locale
                inferred_type = _infer_type_from_local_context(param, act, fluent_sigs)
                tdict[param] = inferred_type if inferred_type != "Unknown" else "object"
    
    # Quarta passata: sincronizzazione cross-action
    _propagate_types_across_related_actions(acts, fluent_sigs)
    
    return acts
    
def _select_best_type_for_param(param, action, fluent_sigs, candidates):
    """Seleziona il tipo migliore tra i candidati basandosi sul contesto"""
    if len(candidates) == 1:
        return candidates[0]
    
    # Conta la frequenza di ogni tipo nel contesto dell'azione
    type_scores = {ctype: 0 for ctype in candidates}
    
    for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
        for pred in action.get(section, []):
            fname = pred["name"]
            sig = fluent_sigs.get(fname, [])
            
            for idx, arg in enumerate(pred["args"]):
                if arg == param and idx < len(sig):
                    expected_type = sig[idx]
                    if expected_type in type_scores:
                        type_scores[expected_type] += 1
    
    # Restituisci il tipo con score più alto
    if any(score > 0 for score in type_scores.values()):
        return max(type_scores.items(), key=lambda x: x[1])[0]
    else:
        return candidates[0]  # Fallback al primo candidato


def _infer_type_from_local_context(param, action, fluent_sigs):
    """Inferisce il tipo basandosi solo sul contesto locale dell'azione"""
    possible_types = set()
    
    # Analizza tutti gli usi del parametro in questa azione
    for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
        for pred in action.get(section, []):
            fname = pred["name"]
            sig = fluent_sigs.get(fname, [])
            
            for idx, arg in enumerate(pred["args"]):
                if arg == param and idx < len(sig) and sig[idx] != "Unknown":
                    possible_types.add(sig[idx])
    
    if len(possible_types) == 1:
        return list(possible_types)[0]
    elif possible_types:
        # Se ci sono più opzioni, restituisci la più comune o la prima
        return list(possible_types)[0]
    
    return "Unknown"


def _propagate_types_across_related_actions(acts, fluent_sigs):
    """Propaga i tipi tra azioni che condividono fluent simili"""
    
    # Raggruppa azioni per fluent condivisi
    fluent_action_map = {}
    
    for act_idx, act in enumerate(acts):
        for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
            for pred in act.get(section, []):
                fname = pred["name"]
                if fname not in fluent_action_map:
                    fluent_action_map[fname] = []
                fluent_action_map[fname].append(act_idx)
    
    # Per ogni fluent, propaga informazioni sui tipi
    for fname, action_indices in fluent_action_map.items():
        sig = fluent_sigs.get(fname, [])
        if not sig:
            continue
        
        # Raccogli tutti i parametri usati per questo fluent
        param_info_by_position = {}  # position -> {param_name: type}
        
        for act_idx in action_indices:
            act = acts[act_idx]
            tdict = act["type_constraints"]
            
            for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
                for pred in act.get(section, []):
                    if pred["name"] == fname:
                        for pos, arg in enumerate(pred["args"]):
                            if arg.startswith("Param") and arg in tdict:
                                if pos not in param_info_by_position:
                                    param_info_by_position[pos] = {}
                                if tdict[arg] != "Unknown":
                                    param_info_by_position[pos][arg] = tdict[arg]
        
        # Propaga le informazioni raccolte
        for act_idx in action_indices:
            act = acts[act_idx]
            tdict = act["type_constraints"]
            
            for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
                for pred in act.get(section, []):
                    if pred["name"] == fname:
                        for pos, arg in enumerate(pred["args"]):
                            if (arg.startswith("Param") and 
                                arg in tdict and 
                                tdict[arg] == "Unknown" and 
                                pos in param_info_by_position):
                                
                                # Usa un tipo noto per questa posizione
                                if param_info_by_position[pos]:
                                    known_type = next(iter(param_info_by_position[pos].values()))
                                    tdict[arg] = known_type

def parse_type_constraints(type_constraints_list, type_constraint_dict=None):
    """
    Convert type constraints handling both string constraints and direct type mapping.
    Now also accepts an optional type_constraint_dict for more accurate mapping.
    """
    type_dict = {}
    
    # If we have a direct type constraint dict (from improved extractor), use it first
    if type_constraint_dict:
        type_dict.update(type_constraint_dict)
    
    # Then parse string constraints as fallback/addition
    for constraint in type_constraints_list:
        match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)', constraint.strip())
        if match:
            type_name = match.group(1)
            param_names = match.group(2)
            
            # Gestisci tutti i parametri individualmente
            for param in param_names.split(','):
                param = param.strip()
                if param and param.startswith('Param'):  # Ignora stringhe vuote e non-Param
                    # Only add if not already in type_dict (direct mapping takes precedence)
                    if param not in type_dict:
                        type_dict[param] = type_name
                
    return type_dict

def knwoledge_to_json(knowledge):
    """
    Convert a 'knowledge' dict into a fully structured JSON‐serializable dict,
    including fluent signatures and wildcard positions for negated preconditions.
    VERSIONE MIGLIORATA che risolve le signature Unknown.
    """
    result = {}
    result["types"] = knowledge.get("types", {})
    result["fluents"] = knowledge.get("fluent_names", [])
    result["fluent_signatures"] = knowledge.get("fluent_signatures", {})

    result["init_state"] = [parse_predicate(f) for f in knowledge.get("init_state", [])]
    result["goal_state"] = [parse_predicate(f) for f in knowledge.get("goal_state", [])]

    # Actions processing
    acts = []
    for act in knowledge.get("actions", []):
        a = {
            "name": act["name"],
            "parameters": act.get("parameters", []),
            "type_constraints": parse_type_constraints(
                act.get("type_constraints", []), 
                act.get("_type_constraint_dict", {})
            ),
            "preconditions": [parse_predicate(p) for p in act.get("preconditions", [])],
            "neg_preconditions": [],
            "add_effects": [],
            "del_effects": []
        }
        
        for raw in act.get("neg_preconditions", []):
            pred = parse_predicate(raw)
            wc = []
            for idx, arg in enumerate(pred["args"]):
                if arg == "_" or arg.startswith("_"):
                    wc.append(idx)
            pred["wildcard_positions"] = wc
            a["neg_preconditions"].append(pred)

        for eff in act.get("effects", []):
            eff = eff.strip()
            if eff.startswith("add(") and eff.endswith(")"):
                inner = eff[4:-1]
                a["add_effects"].append(parse_predicate(inner))
            elif eff.startswith("del(") and eff.endswith(")"):
                inner = eff[4:-1]
                a["del_effects"].append(parse_predicate(inner))
            else:
                a["add_effects"].append(parse_predicate(eff))

        acts.append(a)

    acts = infer_missing_types(acts, result["fluent_signatures"])
    result["actions"] = acts

    # Risoluzione signature
    result = resolve_fluent_signatures_from_actions(result)
    
    # *** NUOVA SINCRONIZZAZIONE COMPLETA ***
    result = synchronize_fluent_usage_after_signature_resolution(result)
    
    return result


def _reconstruct_fluent_args(fluent_name, current_args, expected_length, action, section_name):
    """
    Ricostruisce gli argomenti corretti per un fluent basandosi sulla signature attesa
    e sul contesto dell'azione.
    VERSIONE CORRETTA che mantiene la struttura wildcard/parametri originale.
    """
    type_constraints = action.get("type_constraints", {})
    
    # Se la lunghezza è già corretta, non fare nulla
    if len(current_args) == expected_length:
        return current_args
    
    print(f"    Reconstructing {fluent_name}: {len(current_args)} -> {expected_length}")
    print(f"    Original args: {current_args}")
    
    # Per neg_preconditions, mantieni la struttura originale di wildcard/parametri
    if section_name == "neg_preconditions":
        corrected_args = []
        
        # Mantieni gli argomenti originali preservando la loro natura (wildcard vs param)
        for i in range(expected_length):
            if i < len(current_args):
                current_arg = current_args[i]
                
                # Se era un parametro fisso, mantienilo (solo se è valido)
                if current_arg.startswith("Param") and current_arg in type_constraints:
                    corrected_args.append(current_arg)
                # Se era una wildcard, mantienila
                elif current_arg.startswith("_"):
                    corrected_args.append(current_arg)
                # Se era qualcos'altro, mantienilo come wildcard
                else:
                    corrected_args.append(f"_{i}")
            else:
                # Argomenti mancanti: genera wildcard
                corrected_args.append(f"_{i}")
        
        print(f"    Corrected args (neg_precondition): {corrected_args}")
        return corrected_args
    
    # Per altri tipi di sezioni, usa strategia diversa
    else:
        # Strategia 1: Cerca lo stesso fluent nell'add_effects come riferimento
        for add_eff in action.get("add_effects", []):
            if add_eff["name"] == fluent_name and len(add_eff["args"]) == expected_length:
                template_args = add_eff["args"]
                corrected_args = []
                
                for i, template_arg in enumerate(template_args):
                    if i < len(current_args):
                        current_arg = current_args[i]
                        
                        # Se current_arg è un parametro valido, usalo
                        if current_arg.startswith("Param") and current_arg in type_constraints:
                            corrected_args.append(current_arg)
                        # Se current_arg è wildcard, mantienilo
                        elif current_arg.startswith("_"):
                            corrected_args.append(current_arg)
                        # Altrimenti usa il template
                        else:
                            corrected_args.append(template_arg)
                    else:
                        # Argomento mancante - usa dal template
                        corrected_args.append(template_arg)
                
                print(f"    Corrected args (from template): {corrected_args}")
                return corrected_args
    
    # Strategia di fallback: estendi con wildcard
    if len(current_args) < expected_length:
        corrected_args = current_args.copy()
        for i in range(len(current_args), expected_length):
            corrected_args.append(f"_{i}")
        print(f"    Corrected args (extended): {corrected_args}")
        return corrected_args
    
    # Se troppo lungo, tronca
    if len(current_args) > expected_length:
        corrected_args = current_args[:expected_length]
        print(f"    Corrected args (truncated): {corrected_args}")
        return corrected_args
    
    return None


def analyze_original_structure(knowledge):
    """
    Analizza la struttura originale delle neg_preconditions per capire 
    i pattern di wildcard vs parametri fissi
    """
    print("\n=== ANALYZING ORIGINAL NEG_PRECONDITION PATTERNS ===")
    
    for action in knowledge["actions"]:
        action_name = action["name"]
        
        for neg_precond in action.get("neg_preconditions", []):
            fluent_name = neg_precond["name"]
            args = neg_precond["args"]
            
            if fluent_name.startswith("moving_"):
                print(f"\n{action_name}: {fluent_name}")
                print(f"  Args: {args}")
                
                pattern = []
                for i, arg in enumerate(args):
                    if arg.startswith("Param"):
                        pattern.append(f"PARAM({arg})")
                    elif arg.startswith("_"):
                        pattern.append("WILDCARD")
                    else:
                        pattern.append(f"OTHER({arg})")
                
                print(f"  Pattern: {pattern}")
                print(f"  Wildcard positions: {neg_precond.get('wildcard_positions', [])}")
    
    print("=== END ANALYSIS ===\n")

def debug_fluent_consistency(knowledge):
    """
    Debug function per verificare la consistenza dei fluent
    """
    print("\n=== FLUENT CONSISTENCY CHECK ===")
    
    fluent_signatures = knowledge.get("fluent_signatures", {})
    
    for fluent_name, signature in fluent_signatures.items():
        print(f"\nFluent: {fluent_name}")
        print(f"  Signature: {signature} (length: {len(signature)})")
        
        # Trova tutti gli usi di questo fluent
        usages = []
        
        for action in knowledge["actions"]:
            for section_name in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
                for item in action.get(section_name, []):
                    if item["name"] == fluent_name:
                        usages.append({
                            "action": action["name"],
                            "section": section_name,
                            "args": item["args"],
                            "length": len(item["args"])
                        })
        
        # Raggruppa per lunghezza
        length_groups = {}
        for usage in usages:
            length = usage["length"]
            if length not in length_groups:
                length_groups[length] = []
            length_groups[length].append(usage)
        
        print(f"  Usages by length:")
        for length, group in sorted(length_groups.items()):
            print(f"    Length {length}: {len(group)} occurrences")
            for usage in group[:3]:  # Mostra solo i primi 3
                print(f"      {usage['action']}.{usage['section']}: {usage['args']}")
    
    print("=== END CONSISTENCY CHECK ===\n")

def resolve_fluent_signatures_from_actions(knowledge):
    """
    Risolve definitivamente le signature dei fluent dando priorità agli add_effects
    che sono più affidabili per determinare la vera signature.
    """
    fluent_signatures = knowledge.get("fluent_signatures", {})
    
    # Prima passata: raccogli signature SOLO da add_effects 
    fluent_signature_candidates = {}  # fluent_name -> [(signature, action_score, action_name)]

    for action in knowledge["actions"]:
        type_constraints = action.get("type_constraints", {})
        action_score = len(type_constraints)  # Score basato su ricchezza di type info
        
        # Analizza add_effects per signature autoritativa
        for add_eff in action.get("add_effects", []):
            fluent_name = add_eff["name"]
            args = add_eff["args"]
            
            signature = []
            valid_signature = True
            
            for arg in args:
                if arg in type_constraints:
                    signature.append(type_constraints[arg])
                elif arg.startswith("_"):
                    valid_signature = False
                    break
                else:
                    inferred_type = _infer_type_from_constant_value(arg, knowledge)
                    if inferred_type != "Unknown":
                        signature.append(inferred_type)
                    else:
                        valid_signature = False
                        break
            
            # Se abbiamo una signature valida, aggiungila ai candidati
            if valid_signature and signature:
                if fluent_name not in fluent_signature_candidates:
                    fluent_signature_candidates[fluent_name] = []
                
                fluent_signature_candidates[fluent_name].append((
                    signature, action_score, action["name"]
                ))
    
    # Seconda passata: per fluent senza add_effects, usa precondizioni e del_effects
    for action in knowledge["actions"]:
        type_constraints = action.get("type_constraints", {})
        action_score = len(type_constraints)
        
        # Solo per fluent che non hanno signature dai add_effects
        for section_name, section_data in [("preconditions", action.get("preconditions", [])), 
                                          ("del_effects", action.get("del_effects", []))]:
            
            for item in section_data:
                fluent_name = item["name"]
                
                # Salta se abbiamo già buone signature da add_effects
                if fluent_name in fluent_signature_candidates:
                    continue
                
                args = item["args"]
                signature = []
                valid_signature = True
                
                for arg in args:
                    if arg in type_constraints:
                        signature.append(type_constraints[arg])
                    elif arg.startswith("_"):
                        valid_signature = False
                        break
                    else:
                        inferred_type = _infer_type_from_constant_value(arg, knowledge)
                        if inferred_type != "Unknown":
                            signature.append(inferred_type)
                        else:
                            valid_signature = False
                            break
                
                if valid_signature and signature:
                    if fluent_name not in fluent_signature_candidates:
                        fluent_signature_candidates[fluent_name] = []
                    
                    # Score più basso per non-add_effects
                    fluent_signature_candidates[fluent_name].append((
                        signature, action_score * 0.5, f"{action['name']}__{section_name}"
                    ))
    
    # Terza passata: seleziona la signature migliore per ogni fluent
    for fluent_name, candidates in fluent_signature_candidates.items():
        if not candidates:
            continue
        
        # Ordina per score (priorità a add_effects e azioni con più type info)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Prendi la signature con score più alto
        best_signature, best_score, source_action = candidates[0]
        
        # Verifica consistenza se ci sono più candidati con score alto
        if len(candidates) > 1:
            high_score_candidates = [c for c in candidates if c[1] >= best_score * 0.8]
            
            # Se ci sono più candidati simili, controlla che abbiano la stessa lunghezza
            lengths = [len(c[0]) for c in high_score_candidates]
            most_common_length = max(set(lengths), key=lengths.count)
            
            # Filtra per lunghezza più comune
            consistent_candidates = [c for c in high_score_candidates if len(c[0]) == most_common_length]
            
            if consistent_candidates:
                # Per ogni posizione, trova il tipo più comune
                final_signature = []
                for pos in range(most_common_length):
                    types_at_pos = [c[0][pos] for c in consistent_candidates if pos < len(c[0])]
                    
                    if types_at_pos:
                        # Trova tipo più comune
                        type_counts = {}
                        for t in types_at_pos:
                            type_counts[t] = type_counts.get(t, 0) + 1
                        
                        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0]
                        final_signature.append(most_common_type)
                    else:
                        final_signature.append("Unknown")
                
                fluent_signatures[fluent_name] = final_signature
                print(f"  Resolved signature for {fluent_name}: {final_signature} (from {len(consistent_candidates)} consistent sources)")
            else:
                fluent_signatures[fluent_name] = best_signature
                print(f"  Used best signature for {fluent_name}: {best_signature} (from {source_action})")
        else:
            fluent_signatures[fluent_name] = best_signature
            print(f"  Single signature for {fluent_name}: {best_signature} (from {source_action})")
    
    # Aggiorna il knowledge con le nuove signature
    knowledge["fluent_signatures"] = fluent_signatures
    return knowledge



def _infer_type_from_constant_value(value, knowledge):
    """Inferisce il tipo di un valore costante"""
    # Controlla se è un oggetto conosciuto
    for type_name, instances in knowledge.get("types", {}).items():
        if value in instances:
            return type_name
    
    # Controlla se è numerico (posizione)
    if str(value).isdigit() or (str(value).replace('-', '').replace('.', '').isdigit()):
        return "pos"
    
    return "Unknown"

def debug_fluent_usage_in_actions(knowledge):
    """
    Funzione di debug per capire come vengono usati i fluent nelle azioni
    """
    print("\n=== DEBUG: FLUENT USAGE ANALYSIS ===")
    
    for action in knowledge["actions"]:
        print(f"\nAction: {action['name']}")
        print(f"Type constraints: {action.get('type_constraints', {})}")
        
        # Add effects
        for add_eff in action.get("add_effects", []):
            if add_eff["name"].startswith("moving_"):
                print(f"  ADD: {add_eff['name']}({', '.join(add_eff['args'])})")
                
        # Del effects  
        for del_eff in action.get("del_effects", []):
            if del_eff["name"].startswith("moving_"):
                print(f"  DEL: {del_eff['name']}({', '.join(del_eff['args'])})")
                
        # Preconditions
        for precond in action.get("preconditions", []):
            if precond["name"].startswith("moving_"):
                print(f"  PRECOND: {precond['name']}({', '.join(precond['args'])})")
    
    print("=== END DEBUG ===\n")


if __name__ == "__main__":
    # your existing `knowledge` dict
    knowledge = {
    }

    result = knwoledge_to_json(knowledge)
    print(json.dumps(result, indent=4))
    
    # Ensure the output directory exists
    os.makedirs("RESULTS/CONVERTER", exist_ok=True)
    with open("RESULTS/CONVERTER/extracted_knowledge.json", "w") as json_file:
        json.dump(result, json_file, indent=4)