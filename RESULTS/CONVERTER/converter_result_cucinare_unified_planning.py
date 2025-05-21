import time
start_time = time.time()

import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.model.operators import OperatorKind

up.shortcuts.get_environment().credits_stream = None

# Define types
cuoco = UserType("Cuoco")
cibo = UserType("Cibo")
strumento = UserType("Strumento")
Location = UserType("Location")
Generic = UserType("Generic")

# Define fluents
