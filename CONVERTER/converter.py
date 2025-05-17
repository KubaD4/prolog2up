import argparse
from prolog2up import main

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Specify the Prolog file name.")
parser.add_argument("filename", help="Name of the Prolog file")
args = parser.parse_args()

# Path al file Prolog
prolog_file = "PROLOG/" + args.filename

# Nome del file di output PDDL
pddl_output = "converter_pddl_result"

# Esegui la conversione
problem = main(prolog_file, pddl_output)

