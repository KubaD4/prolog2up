# Generated UP code from Prolog knowledge
# This code is automatically generated.
import unified_planning as up
import os
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.model.operators import OperatorKind
from unified_planning.shortcuts import *
up.shortcuts.get_environment().credits_stream = None

Cibo = UserType('cibo')
Strumento = UserType('strumento')
Cuoco = UserType('cuoco')
Piano = UserType('piano')
Luce = UserType('luce')

Location = UserType('Location')
Unknown = UserType('Unknown')
Strumento = UserType('strumento')
Cuoco = UserType('cuoco')
Piano = UserType('piano')
Cibo = UserType('cibo')

crudo = Fluent('crudo', BoolType(), p0=Cibo)
pieno = Fluent('pieno', BoolType(), p0=Piano)
disponibile = Fluent('disponibile', BoolType(), p0=Strumento)
cotto = Fluent('cotto', BoolType(), p0=Cibo)
ha_fame = Fluent('ha_fame', BoolType(), p0=Cuoco)
vuoto = Fluent('vuoto', BoolType(), p0=Piano)
pos_attuale = Fluent('pos_attuale', BoolType(), p0=Strumento, p1=Piano, p2=Unknown)
temperatura = Fluent('temperatura', BoolType(), p0=Cibo, p1=Unknown, p2=Location)
soddisfatto = Fluent('soddisfatto', BoolType(), p0=Cuoco)

problem = Problem('from_prolog')
problem.add_fluent(crudo, default_initial_value=False)
problem.add_fluent(pieno, default_initial_value=False)
problem.add_fluent(disponibile, default_initial_value=False)
problem.add_fluent(cotto, default_initial_value=False)
problem.add_fluent(ha_fame, default_initial_value=False)
problem.add_fluent(vuoto, default_initial_value=False)
problem.add_fluent(pos_attuale, default_initial_value=False)
problem.add_fluent(temperatura, default_initial_value=False)
problem.add_fluent(soddisfatto, default_initial_value=False)

pasta = Object('pasta', Cibo)
pentola = Object('pentola', Strumento)
mario = Object('mario', Cuoco)
tavolo = Object('tavolo', Piano)
led = Object('led', Luce)
problem.add_objects([
    pasta,
    pentola,
    mario,
    tavolo,
    led,
])

problem.set_initial_value(crudo(pasta), True)
problem.set_initial_value(disponibile(pentola), True)
problem.set_initial_value(ha_fame(mario), True)
problem.set_initial_value(vuoto(tavolo), True)
problem.set_initial_value(pos_attuale(pentola, fornelli, alto), True)
problem.set_initial_value(temperatura(pasta, freddo, 0), True)

problem.add_goal(cotto(pasta))
problem.add_goal(soddisfatto(mario))
problem.add_goal(pieno(tavolo))
problem.add_goal(pos_attuale(pentola, tavolo, basso))
problem.add_goal(temperatura(pasta, caldo, 100))

# --- action cucina
cucina = InstantaneousAction('cucina', Param1=Cuoco, Param2=Cibo, Param3=Strumento, Param4=Pos_cucina, Param5=Pos_cucina)
Param1 = cucina.parameter('Param1')
Param2 = cucina.parameter('Param2')
Param3 = cucina.parameter('Param3')
Param4 = cucina.parameter('Param4')
Param5 = cucina.parameter('Param5')
cucina.add_precondition(crudo(Param2))
cucina.add_precondition(disponibile(Param3))
cucina.add_precondition(pos_attuale(Param3, Param4, Param5))
cucina.add_effect(crudo(Param2), False)
cucina.add_effect(temperatura(Param2, freddo, 0), False)
cucina.add_effect(cotto(Param2), True)
cucina.add_effect(temperatura(Param2, caldo, 100), True)
problem.add_action(cucina)

# --- action sposta
sposta = InstantaneousAction('sposta', Param1=Strumento, Param2=Pos_cucina, Param3=Pos_cucina, Param4=Pos_cucina, Param5=Pos_cucina)
Param1 = sposta.parameter('Param1')
Param2 = sposta.parameter('Param2')
Param3 = sposta.parameter('Param3')
Param4 = sposta.parameter('Param4')
Param5 = sposta.parameter('Param5')
sposta.add_precondition(pos_attuale(Param1, Param2, Param3))
sposta.add_effect(pos_attuale(Param1, Param2, Param3), False)
sposta.add_effect(pos_attuale(Param1, Param4, Param5), True)
problem.add_action(sposta)

# --- action mangia
mangia = InstantaneousAction('mangia', Param1=Cuoco, Param2=Cibo, Param3=Pos_cucina, Param4=Pos_cucina)
Param1 = mangia.parameter('Param1')
Param2 = mangia.parameter('Param2')
Param3 = mangia.parameter('Param3')
Param4 = mangia.parameter('Param4')
mangia.add_precondition(cotto(Param2))
mangia.add_precondition(ha_fame(Param1))
mangia.add_precondition(pos_attuale(Param2, Param3, Param4))
mangia.add_precondition(temperatura(Param2, caldo, 100))
mangia.add_effect(ha_fame(Param1), False)
mangia.add_effect(soddisfatto(Param1), True)
problem.add_action(mangia)

writer = PDDLWriter(problem)
writer.write_domain('generated_domain.pddl')
writer.write_problem('generated_problem.pddl')
print('Generated PDDL files in current directory')