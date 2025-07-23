import json
import re
import os

def detect_polymorphic_fluents(knowledge):
    print("\n=== DETECTING POLYMORPHIC FLUENTS ===")
    
    
    fluent_usage_analysis = {}  
    
    
    def analyze_predicate_types(pred_dict, action_context=None):
        fluent_name = pred_dict["name"]
        args = pred_dict["args"]
        
        if fluent_name not in fluent_usage_analysis:
            fluent_usage_analysis[fluent_name] = {}
        
        for pos, arg in enumerate(args):
            if pos not in fluent_usage_analysis[fluent_name]:
                fluent_usage_analysis[fluent_name][pos] = set()
            
            
            arg_type = None
            
            
            if action_context and arg in action_context.get("type_constraints", {}):
                arg_type = action_context["type_constraints"][arg]
            elif not arg.startswith("_") and not arg.startswith("Param"):
                
                for type_name, instances in knowledge["types"].items():
                    if arg in instances:
                        arg_type = type_name
                        break
            
            if arg_type and arg_type != "Unknown":
                fluent_usage_analysis[fluent_name][pos].add(arg_type)
    
    
    for state_section in [knowledge["init_state"], knowledge["goal_state"]]:
        for pred in state_section:
            analyze_predicate_types(pred)
    
    
    for action in knowledge["actions"]:
        for section in ["preconditions", "neg_preconditions", "add_effects", "del_effects"]:
            for pred in action.get(section, []):
                analyze_predicate_types(pred, action)
    
    
    supertype_registry = {}  
    supertype_counter = 1
    fluent_signature_updates = {}  
    
    for fluent_name, position_types in fluent_usage_analysis.items():
        print(f"\nAnalyzing fluent: {fluent_name}")
        
        needs_supertype = False
        new_signature = []
        
        
        max_position = max(position_types.keys()) if position_types else -1
        
        for pos in range(max_position + 1):
            types_at_position = position_types.get(pos, set())
            
            print(f"  Position {pos}: {types_at_position}")
            
            if len(types_at_position) > 1:
                
                needs_supertype = True
                
                
                sorted_types = sorted(types_at_position)
                supertype_signature = "_".join(sorted_types)
                
                
                existing_supertype = None
                for st_name, st_types in supertype_registry.items():
                    if st_types == types_at_position:
                        existing_supertype = st_name
                        break
                
                if existing_supertype:
                    new_signature.append(existing_supertype)
                    print(f"    -> Using existing supertype: {existing_supertype}")
                else:
                    
                    supertype_name = f"SuperType{supertype_counter}"
                    supertype_counter += 1
                    supertype_registry[supertype_name] = types_at_position
                    new_signature.append(supertype_name)
                    print(f"    -> Created new supertype: {supertype_name} = {types_at_position}")
                    
            elif len(types_at_position) == 1:
                
                new_signature.append(list(types_at_position)[0])
            else:
                
                new_signature.append("Unknown")
        
        if needs_supertype:
            fluent_signature_updates[fluent_name] = new_signature
            print(f"  Updated signature: {fluent_name}: {new_signature}")
    
    
    if supertype_registry:
        print(f"\nCreated {len(supertype_registry)} supertypes:")
        for st_name, st_types in supertype_registry.items():
            print(f"  {st_name}: {sorted(st_types)}")
            
        
        knowledge["supertypes"] = {
            st_name: sorted(list(st_types)) for st_name, st_types in supertype_registry.items()
        }
        
        
        for fluent_name, new_sig in fluent_signature_updates.items():
            knowledge["fluent_signatures"][fluent_name] = new_sig
    
    print("=== END POLYMORPHIC FLUENT DETECTION ===\n")
    return knowledge


def synchronize_fluent_usage_after_signature_resolution(knowledge):
    fluent_signatures = knowledge.get("fluent_signatures", {})
    
    print("\n=== SYNCHRONIZING FLUENT USAGE ===")
    
    for action in knowledge["actions"]:
        action_name = action["name"]
        type_constraints = action.get("type_constraints", {})
        
        
        for section_name in ["neg_preconditions", "preconditions", "add_effects", "del_effects"]:
            section_data = action.get(section_name, [])
            
            for item_idx, item in enumerate(section_data):
                fluent_name = item["name"]
                current_args = item["args"]
                
                
                if fluent_name in fluent_signatures:
                    expected_length = len(fluent_signatures[fluent_name])
                    current_length = len(current_args)
                    
                    if current_length != expected_length:
                        print(f"  MISMATCH in {action_name}.{section_name}: {fluent_name}")
                        print(f"    Current: {current_length} args, Expected: {expected_length} args")
                        print(f"    Current args: {current_args}")
                        
                        
                        corrected_args = _reconstruct_fluent_args(
                            fluent_name, 
                            current_args, 
                            expected_length,
                            action,
                            section_name
                        )
                        
                        if corrected_args:
                            print(f"    Corrected args: {corrected_args}")
                            
                            
                            section_data[item_idx]["args"] = corrected_args
                            
                            
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
    type_constraints = action.get("type_constraints", {})
    
    
    if len(current_args) == expected_length:
        return current_args
    
    
    if section_name != "add_effects":
        for add_eff in action.get("add_effects", []):
            if add_eff["name"] == fluent_name and len(add_eff["args"]) == expected_length:
                
                template_args = add_eff["args"]
                corrected_args = []
                
                for i, template_arg in enumerate(template_args):
                    if i < len(current_args):
                        current_arg = current_args[i]
                        
                        
                        if current_arg.startswith("Param") and current_arg in type_constraints:
                            corrected_args.append(current_arg)
                        
                        elif current_arg.startswith("_"):
                            corrected_args.append(current_arg)
                        
                        else:
                            if template_arg.startswith("Param") and template_arg in type_constraints:
                                
                                corrected_args.append(template_arg)
                            else:
                                
                                corrected_args.append(f"_{i}")
                    else:
                        
                        if template_arg.startswith("Param") and template_arg in type_constraints:
                            corrected_args.append(template_arg)
                        else:
                            corrected_args.append(f"_{i}")
                
                return corrected_args
    
    
    if len(current_args) < expected_length:
        corrected_args = current_args.copy()
        for i in range(len(current_args), expected_length):
            corrected_args.append(f"_{i}")
        return corrected_args
    
    
    if len(current_args) > expected_length:
        return current_args[:expected_length]
    
    return None

def parse_predicate(pred_str):
    m = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*(.*?)\s*\)\s*$', pred_str)
    if not m:
        
        return {"name": pred_str.strip(), "args": []}
    name, args_str = m.group(1), m.group(2).strip()
    args = [a.strip() for a in args_str.split(',')] if args_str else []
    return {"name": name, "args": args}

def infer_missing_types(acts, fluent_sigs):
    
    
    all_param_type_info = {}  
    
    for act in acts:
        tdict = act["type_constraints"]
        
        
        for param, ptype in tdict.items():
            if param not in all_param_type_info:
                all_param_type_info[param] = set()
            if ptype != "Unknown":
                all_param_type_info[param].add(ptype)
    
    
    for act in acts:
        tdict = act["type_constraints"]
        
        for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
            for pred in act.get(section, []):
                fname = pred["name"]
                sig = fluent_sigs.get(fname, [])
                
                for idx, arg in enumerate(pred["args"]):
                    if not arg.startswith("Param"):
                        continue
                    
                    
                    if idx < len(sig) and sig[idx] != "Unknown":
                        if arg not in all_param_type_info:
                            all_param_type_info[arg] = set()
                        all_param_type_info[arg].add(sig[idx])
    
    
    for act in acts:
        tdict = act["type_constraints"]
        
        for param in act["parameters"]:
            if param in tdict and tdict[param] != "Unknown":
                continue
            
            
            if param in all_param_type_info and all_param_type_info[param]:
                type_candidates = list(all_param_type_info[param])
                if len(type_candidates) == 1:
                    tdict[param] = type_candidates[0]
                else:
                    
                    best_type = _select_best_type_for_param(param, act, fluent_sigs, type_candidates)
                    tdict[param] = best_type
            else:
                
                inferred_type = _infer_type_from_local_context(param, act, fluent_sigs)
                tdict[param] = inferred_type if inferred_type != "Unknown" else "object"
    
    
    _propagate_types_across_related_actions(acts, fluent_sigs)
    
    return acts
    
def _select_best_type_for_param(param, action, fluent_sigs, candidates):

    if len(candidates) == 1:
        return candidates[0]
    
    
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
    
    
    if any(score > 0 for score in type_scores.values()):
        return max(type_scores.items(), key=lambda x: x[1])[0]
    else:
        return candidates[0]  


def _infer_type_from_local_context(param, action, fluent_sigs):

    possible_types = set()
    
    
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
        
        return list(possible_types)[0]
    
    return "Unknown"


def _propagate_types_across_related_actions(acts, fluent_sigs):

    
    
    fluent_action_map = {}
    
    for act_idx, act in enumerate(acts):
        for section in ("preconditions", "neg_preconditions", "add_effects", "del_effects"):
            for pred in act.get(section, []):
                fname = pred["name"]
                if fname not in fluent_action_map:
                    fluent_action_map[fname] = []
                fluent_action_map[fname].append(act_idx)
    
    
    for fname, action_indices in fluent_action_map.items():
        sig = fluent_sigs.get(fname, [])
        if not sig:
            continue
        
        
        param_info_by_position = {}  
        
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
                                
                                
                                if param_info_by_position[pos]:
                                    known_type = next(iter(param_info_by_position[pos].values()))
                                    tdict[arg] = known_type

def parse_type_constraints(type_constraints_list, type_constraint_dict=None):
    type_dict = {}
    
    
    if type_constraint_dict:
        type_dict.update(type_constraint_dict)
    
    
    for constraint in type_constraints_list:
        match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)', constraint.strip())
        if match:
            type_name = match.group(1)
            param_names = match.group(2)
            
            
            for param in param_names.split(','):
                param = param.strip()
                if param and param.startswith('Param'):  
                    
                    if param not in type_dict:
                        type_dict[param] = type_name
                
    return type_dict

def knwoledge_to_json(knowledge):
    result = {}
    result["types"] = knowledge.get("types", {})
    result["fluents"] = knowledge.get("fluent_names", [])
    result["fluent_signatures"] = knowledge.get("fluent_signatures", {})

    result["init_state"] = [parse_predicate(f) for f in knowledge.get("init_state", [])]
    result["goal_state"] = [parse_predicate(f) for f in knowledge.get("goal_state", [])]

    
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

    
    result = resolve_fluent_signatures_from_actions(result)
    
    
    result = detect_polymorphic_fluents(result)
    
    
    result = synchronize_fluent_usage_after_signature_resolution(result)
    
    return result


def _reconstruct_fluent_args(fluent_name, current_args, expected_length, action, section_name):
    type_constraints = action.get("type_constraints", {})
    
    
    if len(current_args) == expected_length:
        return current_args
    
    print(f"    Reconstructing {fluent_name}: {len(current_args)} -> {expected_length}")
    print(f"    Original args: {current_args}")
    
    
    if section_name == "neg_preconditions":
        corrected_args = []
        
        
        for i in range(expected_length):
            if i < len(current_args):
                current_arg = current_args[i]
                
                
                if current_arg.startswith("Param") and current_arg in type_constraints:
                    corrected_args.append(current_arg)
                
                elif current_arg.startswith("_"):
                    corrected_args.append(current_arg)
                
                else:
                    corrected_args.append(f"_{i}")
            else:
                
                corrected_args.append(f"_{i}")
        
        print(f"    Corrected args (neg_precondition): {corrected_args}")
        return corrected_args
    
    
    else:
        
        for add_eff in action.get("add_effects", []):
            if add_eff["name"] == fluent_name and len(add_eff["args"]) == expected_length:
                template_args = add_eff["args"]
                corrected_args = []
                
                for i, template_arg in enumerate(template_args):
                    if i < len(current_args):
                        current_arg = current_args[i]
                        
                        
                        if current_arg.startswith("Param") and current_arg in type_constraints:
                            corrected_args.append(current_arg)
                        
                        elif current_arg.startswith("_"):
                            corrected_args.append(current_arg)
                        
                        else:
                            corrected_args.append(template_arg)
                    else:
                        
                        corrected_args.append(template_arg)
                
                print(f"    Corrected args (from template): {corrected_args}")
                return corrected_args
    
    
    if len(current_args) < expected_length:
        corrected_args = current_args.copy()
        for i in range(len(current_args), expected_length):
            corrected_args.append(f"_{i}")
        print(f"    Corrected args (extended): {corrected_args}")
        return corrected_args
    
    
    if len(current_args) > expected_length:
        corrected_args = current_args[:expected_length]
        print(f"    Corrected args (truncated): {corrected_args}")
        return corrected_args
    
    return None


def resolve_fluent_signatures_from_actions(knowledge):
    fluent_signatures = knowledge.get("fluent_signatures", {})
    
    
    fluent_signature_candidates = {}  

    for action in knowledge["actions"]:
        type_constraints = action.get("type_constraints", {})
        action_score = len(type_constraints)  
        
        
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
            
            
            if valid_signature and signature:
                if fluent_name not in fluent_signature_candidates:
                    fluent_signature_candidates[fluent_name] = []
                
                fluent_signature_candidates[fluent_name].append((
                    signature, action_score, action["name"]
                ))
    
    
    for action in knowledge["actions"]:
        type_constraints = action.get("type_constraints", {})
        action_score = len(type_constraints)
        
        
        for section_name, section_data in [("preconditions", action.get("preconditions", [])), 
                                          ("del_effects", action.get("del_effects", []))]:
            
            for item in section_data:
                fluent_name = item["name"]
                
                
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
                    
                    
                    fluent_signature_candidates[fluent_name].append((
                        signature, action_score * 0.5, f"{action['name']}__{section_name}"
                    ))
    
    
    for fluent_name, candidates in fluent_signature_candidates.items():
        if not candidates:
            continue
        
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        
        best_signature, best_score, source_action = candidates[0]
        
        
        if len(candidates) > 1:
            high_score_candidates = [c for c in candidates if c[1] >= best_score * 0.8]
            
            
            lengths = [len(c[0]) for c in high_score_candidates]
            most_common_length = max(set(lengths), key=lengths.count)
            
            
            consistent_candidates = [c for c in high_score_candidates if len(c[0]) == most_common_length]
            
            if consistent_candidates:
                
                final_signature = []
                for pos in range(most_common_length):
                    types_at_pos = [c[0][pos] for c in consistent_candidates if pos < len(c[0])]
                    
                    if types_at_pos:
                        
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
    
    
    knowledge["fluent_signatures"] = fluent_signatures
    return knowledge



def _infer_type_from_constant_value(value, knowledge):
    
    for type_name, instances in knowledge.get("types", {}).items():
        if value in instances:
            return type_name
    
    
    if str(value).isdigit() or (str(value).replace('-', '').replace('.', '').isdigit()):
        return "pos"
    
    return "Unknown"


if __name__ == "__main__":
    
    knowledge = {
    }

    result = knwoledge_to_json(knowledge)
    print(json.dumps(result, indent=4))
    
    
    os.makedirs("RESULTS/CONVERTER", exist_ok=True)
    with open("RESULTS/CONVERTER/extracted_knowledge.json", "w") as json_file:
        json.dump(result, json_file, indent=4)