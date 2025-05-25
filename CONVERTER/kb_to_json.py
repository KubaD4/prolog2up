import json
import re

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
    Per ogni azione completa il dict 'type_constraints' usando
    la firma del fluent in cui compare un parametro ancora tipato.
    """
    for act in acts:
        tdict = act["type_constraints"]          # alias
        # Scorri tutte le espressioni dove appaiono parametri
        for section in ("preconditions",
                        "neg_preconditions",
                        "add_effects",
                        "del_effects"):
            for pred in act.get(section, []):
                fname   = pred["name"]
                sig     = fluent_sigs.get(fname, [])
                for idx, arg in enumerate(pred["args"]):
                    # Considera solo i ParamX, salta wildcard "_" e costanti
                    if not arg.startswith("Param"):
                        continue
                    if arg in tdict:              # già noto
                        continue
                    # Se la firma ha abbastanza posizioni deduci il tipo
                    if idx < len(sig):
                        tdict[arg] = sig[idx]
                    else:
                        # altrimenti usa un fallback generico
                        tdict[arg] = "object"     # o "Any"
    return acts

def parse_type_constraints(type_constraints_list):
    """
    Convert type constraints handling both single and multiple parameters
    """
    type_dict = {}
    for constraint in type_constraints_list:
        match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)', constraint.strip())
        if match:
            type_name = match.group(1)
            param_names = match.group(2)
            
            # Se ci sono più parametri (separati da virgola)
            if ',' in param_names:
                # Gestisci la coppia originale
                type_dict[param_names.strip()] = type_name
                
                # Gestisci i singoli parametri
                for param in param_names.split(','):
                    param = param.strip()
                    if param:  # Ignora stringhe vuote
                        type_dict[param] = type_name
            else:
                # Gestione parametro singolo
                type_dict[param_names.strip()] = type_name
                
    return type_dict

def knwoledge_to_json(knowledge):
    """
    Convert a 'knowledge' dict into a fully structured JSON‐serializable dict,
    including fluent signatures and wildcard positions for negated preconditions.
    """
    result = {}
    # 1) Types and instances
    result["types"] = knowledge.get("types", {})
    # 2) Fluent names
    result["fluents"] = knowledge.get("fluent_names", [])
    # 2b) Fluent signatures (optional)
    #    expected format: { fluent_name: [type1, type2, ...], ... }
    result["fluent_signatures"] = knowledge.get("fluent_signatures", {})

    # 3) Initial state
    result["init_state"] = [parse_predicate(f) for f in knowledge.get("init_state", [])]
    # 4) Goal state
    result["goal_state"] = [parse_predicate(f) for f in knowledge.get("goal_state", [])]

    # 5) Actions
    acts = []
    for act in knowledge.get("actions", []):
        a = {
            "name": act["name"],
            "parameters": act.get("parameters", []),
            "type_constraints": parse_type_constraints(act.get("type_constraints", [])),  # Convert to dict
            "preconditions": [parse_predicate(p) for p in act.get("preconditions", [])],
            # we will fill neg_preconditions with extra wildcard info
            "neg_preconditions": [],
            "add_effects": [],
            "del_effects": []
        }
        # negative preconditions, with wildcard_positions
        for raw in act.get("neg_preconditions", []):
            pred = parse_predicate(raw)
            wc = []
            for idx, arg in enumerate(pred["args"]):
                # treat any "_" or leading "_" as wildcard
                if arg == "_" or arg.startswith("_"):
                    wc.append(idx)
            pred["wildcard_positions"] = wc
            a["neg_preconditions"].append(pred)

        # split effects into add/del
        for eff in act.get("effects", []):
            eff = eff.strip()
            if eff.startswith("add(") and eff.endswith(")"):
                inner = eff[4:-1]
                a["add_effects"].append(parse_predicate(inner))
            elif eff.startswith("del(") and eff.endswith(")"):
                inner = eff[4:-1]
                a["del_effects"].append(parse_predicate(inner))
            else:
                # fallback: assume add
                a["add_effects"].append(parse_predicate(eff))

        acts.append(a)

    # Sostituisci le wildcards ("_") con l'effettivo tipo di fluent signature 
    # trovandolo in fluent_signatures così da capire a chi associare "any" in UP
    

    acts = infer_missing_types(acts, result["fluent_signatures"])


    result["actions"] = acts

    return result

if __name__ == "__main__":
    # your existing `knowledge` dict
    knowledge = {
        "types": {
            "piano": ["tavolo"],
            "luce": ["led"],
            "strumento": ["pentola"],
            "cibo": ["pasta"],
            "cuoco": ["mario"]
        },
        "fluent_names": ["pieno", "disponibile", "cotto", "su", "ha_fame", "vuoto", "soddisfatto", "crudo"],
        "fluent_signatures": {
            "pieno": ["piano"],
            "disponibile": ["strumento"],
            "cotto": ["cibo"],
            "su": ["piano", "strumento"],
            "ha_fame": ["cuoco"],
            "vuoto": ["piano"],
            "soddisfatto": ["cuoco"],
            "crudo": ["cibo"]
        },
        "init_state": [
            "crudo(pasta)",
            "disponibile(pentola)",
            "ha_fame(mario)",
            "vuoto(tavolo)"
        ],
        "goal_state": [
            "cotto(pasta)",
            "soddisfatto(mario)",
            "pieno(tavolo)"
        ],
        "actions": [
            {
                "name": "cucina",
                "parameters": ["Param1", "Param2", "Param3", "Param4"],
                "type_constraints": [
                    "cuoco(Param1)",
                    "cibo(Param2)",
                    "strumento(Param3)",
                    "piano(Param4)"
                ],
                "preconditions": [
                    "crudo(Param2)",
                    "disponibile(Param3)",
                    "vuoto(Param4)"
                ],
                "neg_preconditions": [],
                "effects": [
                    "add(cotto(Param2))",
                    "add(pieno(Param4))",
                    "del(crudo(Param2))",
                    "del(vuoto(Param4))"
                ]
            },
            {
                "name": "mangia",
                "parameters": ["Param1", "Param2"],
                "type_constraints": [
                    "cuoco(Param1)",
                    "cibo(Param2)"
                ],
                "preconditions": [
                    "cotto(Param2)",
                    "ha_fame(Param1)"
                ],
                "neg_preconditions": [],
                "effects": [
                    "add(soddisfatto(Param1))",
                    "del(ha_fame(Param1))"
                ]
            },
            {
                "name": "sposta_qualsiasi",
                "parameters": ["Param1", "Param2", "Param3"],
                "type_constraints": [
                    "cuoco(Param1)",
                    "strumento(Param2)",
                    "piano(Param3)"
                ],
                "preconditions": [
                    "disponibile(Param2)",
                    "vuoto(Param3)"
                ],
                "neg_preconditions": [
                    "su(_982, Param2)"
                ],
                "effects": [
                    "add(su(Param3, Param2))",
                    "del(disponibile(Param2))",
                    "del(vuoto(Param3))"
                ]
            }
        ]
    }

    result = knwoledge_to_json(knowledge)
    print(json.dumps(result, indent=4))
    with open("CONVERTER/extracted_knowledge.json", "w") as json_file:
        json.dump(result, json_file, indent=4)