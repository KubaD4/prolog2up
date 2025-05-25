import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.model.operators import OperatorKind

up.shortcuts.get_environment().credits_stream = None

Piano = UserType('piano')
Luce = UserType('luce')
Strumento = UserType('strumento')
Cibo = UserType('cibo')
Cuoco = UserType('cuoco')

crudo = Fluent('crudo', BoolType(), p0=Cibo)
disponibile = Fluent('disponibile', BoolType(), p0=Strumento)
ha_fame = Fluent('ha_fame', BoolType(), p0=Cuoco)
vuoto = Fluent('vuoto', BoolType(), p0=Piano)
cotto = Fluent('cotto', BoolType(), p0=Cibo)
soddisfatto = Fluent('soddisfatto', BoolType(), p0=Cuoco)
pieno = Fluent('pieno', BoolType(), p0=Piano)
su = Fluent('su', BoolType(), p0=Piano, p1=Strumento)

problem = Problem('from_prolog')
problem.add_fluent(crudo, default_initial_value=False)
problem.add_fluent(disponibile, default_initial_value=False)
problem.add_fluent(ha_fame, default_initial_value=False)
problem.add_fluent(vuoto, default_initial_value=False)
problem.add_fluent(cotto, default_initial_value=False)
problem.add_fluent(soddisfatto, default_initial_value=False)
problem.add_fluent(pieno, default_initial_value=False)
problem.add_fluent(su, default_initial_value=False)

tavolo = Object('tavolo', Piano)
led = Object('led', Luce)
pentola = Object('pentola', Strumento)
pasta = Object('pasta', Cibo)
mario = Object('mario', Cuoco)
problem.add_objects([
    tavolo,
    led,
    pentola,
    pasta,
    mario,
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
any_0 = Variable('any_0', Piano)
sposta_qualsiasi.add_precondition(
    Not(Exists(
        su(any_0, Param2),
          any_0))
    )   
sposta_qualsiasi.add_effect(disponibile(Param2), False)
sposta_qualsiasi.add_effect(vuoto(Param3), False)
sposta_qualsiasi.add_effect(su(Param3, Param2), True)
problem.add_action(sposta_qualsiasi)


def export_to_pddl():
    """Export the problem to PDDL files and print the contents."""
    print("\nSTART PDDL Exporting...")
    writer = PDDLWriter(problem)
    
    # Write to files
    domain_filename = "V2_UP_generated_domain.pddl"
    problem_filename = "V2_UP_generated_problem.pddl"
    
    writer.write_domain("RESULTS/UP/" + domain_filename)
    writer.write_problem("RESULTS/UP/" + problem_filename)
    
    print(f"Domain written to: {domain_filename}")
    print(f"Problem written to: {problem_filename}")
    
    print("\nDOMAIN PDDL:")
    domain_str = writer.get_domain()
    #print(domain_str[:1000] + "..." if len(domain_str) > 1000 else domain_str)
    
    print("\nPROBLEM PDDL:")
    problem_str = writer.get_problem()
    #print(problem_str[:1000] + "..." if len(problem_str) > 1000 else problem_str)
    


export_to_pddl()