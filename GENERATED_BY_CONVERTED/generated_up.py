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

Luce = UserType('luce')
Cibo = UserType('cibo')
Piano = UserType('piano')
Cuoco = UserType('cuoco')
Strumento = UserType('strumento')

Cuoco = UserType('cuoco')
Strumento = UserType('strumento')
Piano = UserType('piano')
Cibo = UserType('cibo')

su = Fluent('su', BoolType(), p0=Piano, p1=Strumento)
pieno = Fluent('pieno', BoolType(), p0=Piano)
ha_fame = Fluent('ha_fame', BoolType(), p0=Cuoco)
crudo = Fluent('crudo', BoolType(), p0=Cibo)
cotto = Fluent('cotto', BoolType(), p0=Cibo)
vuoto = Fluent('vuoto', BoolType(), p0=Piano)
soddisfatto = Fluent('soddisfatto', BoolType(), p0=Cuoco)
disponibile = Fluent('disponibile', BoolType(), p0=Strumento)

problem = Problem('from_prolog')
problem.add_fluent(su, default_initial_value=False)
problem.add_fluent(pieno, default_initial_value=False)
problem.add_fluent(ha_fame, default_initial_value=False)
problem.add_fluent(crudo, default_initial_value=False)
problem.add_fluent(cotto, default_initial_value=False)
problem.add_fluent(vuoto, default_initial_value=False)
problem.add_fluent(soddisfatto, default_initial_value=False)
problem.add_fluent(disponibile, default_initial_value=False)

led = Object('led', Luce)
pasta = Object('pasta', Cibo)
tavolo = Object('tavolo', Piano)
mario = Object('mario', Cuoco)
pentola = Object('pentola', Strumento)
problem.add_objects([
    led,
    pasta,
    tavolo,
    mario,
    pentola,
])

problem.set_initial_value(crudo(pasta), True)
problem.set_initial_value(disponibile(pentola), True)
problem.set_initial_value(ha_fame(mario), True)
problem.set_initial_value(vuoto(tavolo), True)

problem.add_goal(cotto(pasta))
problem.add_goal(soddisfatto(mario))
problem.add_goal(pieno(tavolo))

# --- action cucina
cucina = InstantaneousAction('cucina', Param1=Cuoco, Param2=Cibo, Param3=Strumento, Param4=Piano)
Param1 = cucina.parameter('Param1')
Param2 = cucina.parameter('Param2')
Param3 = cucina.parameter('Param3')
Param4 = cucina.parameter('Param4')
cucina.add_precondition(crudo(Param2))
cucina.add_precondition(disponibile(Param3))
cucina.add_precondition(vuoto(Param4))
cucina.add_effect(crudo(Param2), False)
cucina.add_effect(vuoto(Param4), False)
cucina.add_effect(cotto(Param2), True)
cucina.add_effect(pieno(Param4), True)
problem.add_action(cucina)

# --- action mangia
mangia = InstantaneousAction('mangia', Param1=Cuoco, Param2=Cibo)
Param1 = mangia.parameter('Param1')
Param2 = mangia.parameter('Param2')
mangia.add_precondition(cotto(Param2))
mangia.add_precondition(ha_fame(Param1))
mangia.add_effect(ha_fame(Param1), False)
mangia.add_effect(soddisfatto(Param1), True)
problem.add_action(mangia)

# --- action sposta_qualsiasi
sposta_qualsiasi = InstantaneousAction('sposta_qualsiasi', Param1=Cuoco, Param2=Strumento, Param3=Piano)
Param1 = sposta_qualsiasi.parameter('Param1')
Param2 = sposta_qualsiasi.parameter('Param2')
Param3 = sposta_qualsiasi.parameter('Param3')
sposta_qualsiasi.add_precondition(disponibile(Param2))
sposta_qualsiasi.add_precondition(vuoto(Param3))
any_sposta_qualsiasi_0 = Variable('any_sposta_qualsiasi_0', Piano)
sposta_qualsiasi.add_precondition(Not(Exists(su(any_sposta_qualsiasi_0, Param2), any_sposta_qualsiasi_0)))
sposta_qualsiasi.add_effect(disponibile(Param2), False)
sposta_qualsiasi.add_effect(vuoto(Param3), False)
sposta_qualsiasi.add_effect(su(Param3, Param2), True)
problem.add_action(sposta_qualsiasi)

writer = PDDLWriter(problem)
writer.write_domain(os.path.join('CONVERTER/GENERATED_BY_CONVERTED/generated_domain.pddl'))
writer.write_problem(os.path.join('CONVERTER/GENERATED_BY_CONVERTED/generated_problem.pddl'))
print('Generated PDDL files in', 'GENERATED_BY_CONVERTED')