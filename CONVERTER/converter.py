from prolog2up import main

# Path al file Prolog
prolog_file = "PROLOG/small_kb_hl.pl"

# Nome del file di output PDDL
pddl_output = "converter_pddl_result"

# Esegui la conversione
problem = main(prolog_file, pddl_output)
