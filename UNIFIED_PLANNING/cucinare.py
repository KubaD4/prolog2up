import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.model.operators import OperatorKind
# 1) Tipi (corrispondono ai predicati cuoco/1, cibo/1, strumento/1, piano/1, luce/1)
Cuoco      = UserType('Cuoco')
Cibo       = UserType('Cibo')
Strumento  = UserType('Strumento')
Piano      = UserType('Piano')
Luce       = UserType('Luce')

# 2) Fluents (corrispondono ai fatti Prolog)
crudo         = Fluent('crudo', BoolType(), c=Cibo)
disponibile   = Fluent('disponibile', BoolType(), s=Strumento)
ha_fame       = Fluent('ha_fame', BoolType(), p=Cuoco)
vuoto         = Fluent('vuoto', BoolType(), loc=Piano)
cotto         = Fluent('cotto', BoolType(), c=Cibo)
soddisfatto   = Fluent('soddisfatto', BoolType(), p=Cuoco)
pieno         = Fluent('pieno', BoolType(), loc=Piano)
su            = Fluent('su', BoolType(), dest=Piano, s=Strumento)

# 3) Creo il problema
problem = Problem('cucinare')

# 4) Aggiungo i fluent al problema, con valore di default False
for f in (crudo, disponibile, ha_fame, vuoto, cotto, soddisfatto, pieno, su):
    problem.add_fluent(f, default_initial_value=False)

# 5) Creo gli oggetti (da cuoco/1, cibo/1, strumento/1, piano/1, luce/1)
mario   = Object('mario',   Cuoco)
pasta   = Object('pasta',   Cibo)
pentola = Object('pentola', Strumento)
tavolo  = Object('tavolo',  Piano)
led     = Object('led',     Luce)

problem.add_objects([mario, pasta, pentola, tavolo, led])

# 6) Stato iniziale (init_state/1)
problem.set_initial_value(crudo(pasta),       True)
problem.set_initial_value(disponibile(pentola), True)
problem.set_initial_value(ha_fame(mario),     True)
problem.set_initial_value(vuoto(tavolo),      True)

# 7) Stato goal (goal_state/1)
problem.add_goal(cotto(pasta))
problem.add_goal(soddisfatto(mario))
problem.add_goal(pieno(tavolo))

# 8) Azioni

# 8.1) cucina(Persona, Cibo, Strumento, Tavolo)
cucina = InstantaneousAction('cucina', persona=Cuoco, cibo=Cibo, strumento=Strumento, tavolo=Piano)
p = cucina.parameter('persona')
c = cucina.parameter('cibo')
s = cucina.parameter('strumento')
t = cucina.parameter('tavolo')

# precondizioni positive
cucina.add_precondition(crudo(c))
cucina.add_precondition(disponibile(s))
cucina.add_precondition(vuoto(t))
# non ce ne sono di negative

# effetti (del/add)
cucina.add_effect(crudo(c),       False)
cucina.add_effect(vuoto(t),       False)
cucina.add_effect(cotto(c),       True)
cucina.add_effect(pieno(t),       True)

problem.add_action(cucina)


# 8.2) mangia(Persona, Cibo)
mangia = InstantaneousAction('mangia', persona=Cuoco, cibo=Cibo)
p = mangia.parameter('persona')
c = mangia.parameter('cibo')

# precondizioni positive
mangia.add_precondition(cotto(c))
mangia.add_precondition(ha_fame(p))
# no negative

# effetti
mangia.add_effect(ha_fame(p),       False)
mangia.add_effect(soddisfatto(p),   True)

problem.add_action(mangia)


# 8.3) sposta_qualsiasi(Persona, Strumento, Destinazione)
sposta = InstantaneousAction('sposta_qualsiasi',
                             persona=Cuoco,
                             strumento=Strumento,
                             destinazione=Piano)
p = sposta.parameter('persona')
s = sposta.parameter('strumento')
d = sposta.parameter('destinazione')

# precondizioni positive
sposta.add_precondition(disponibile(s))
sposta.add_precondition(vuoto(d))

# precondizione negativa: non esista già su(_, Strumento)
other_d = Variable('other_d', Piano)
sposta.add_precondition(
    Not(Exists(su(other_d, s), other_d))
)

# effetti
sposta.add_effect(disponibile(s),    False)
sposta.add_effect(vuoto(d),          False)
sposta.add_effect(su(d, s),          True)

problem.add_action(sposta)


# 9) export & solve (come in kb_hl.py)
def export_to_pddl():
    writer = PDDLWriter(problem)
    writer.write_domain('RESULTS/cucina_converter_pddl_result_domain.pddl')
    writer.write_problem('RESULTS/cucina_converter_pddl_result_problem.pddl')

# Scommenta a piacere:
export_to_pddl()
