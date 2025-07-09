# Generated UP code from Prolog knowledge
# This code is automatically generated.
import unified_planning as up
import os
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.shortcuts import *

Block = UserType('block')
Mela = UserType('mela')
Vegetale = UserType('vegetale')
Agent = UserType('agent')

Pos = UserType('pos')

at = Fluent('at', BoolType(), p0=Block, p1=Pos, p2=Pos)
intera = Fluent('intera', BoolType(), p0=Mela)
moving_table_to_block = Fluent('moving_table_to_block', BoolType(), p0=Agent, p1=Block, p2=Block, p3=Pos, p4=Pos, p5=Pos, p6=Pos)
ontable = Fluent('ontable', BoolType(), p0=Block)
on = Fluent('on', BoolType(), p0=Block, p1=Block)
available = Fluent('available', BoolType(), p0=Agent)
cotta = Fluent('cotta', BoolType(), p0=Vegetale)
clear = Fluent('clear', BoolType(), p0=Block)
cruda = Fluent('cruda', BoolType(), p0=Vegetale)
morsa = Fluent('morsa', BoolType(), p0=Mela)

problem = Problem('from_prolog')
problem.add_fluent(at, default_initial_value=False)
problem.add_fluent(intera, default_initial_value=False)
problem.add_fluent(moving_table_to_block, default_initial_value=False)
problem.add_fluent(ontable, default_initial_value=False)
problem.add_fluent(on, default_initial_value=False)
problem.add_fluent(available, default_initial_value=False)
problem.add_fluent(cotta, default_initial_value=False)
problem.add_fluent(clear, default_initial_value=False)
problem.add_fluent(cruda, default_initial_value=False)
problem.add_fluent(morsa, default_initial_value=False)

b1 = Object('b1', Block)
b2 = Object('b2', Block)
m1 = Object('m1', Mela)
carota1 = Object('carota1', Vegetale)
a1 = Object('a1', Agent)
x1 = Object('x1', Pos)
x2 = Object('x2', Pos)
problem.add_objects([
    b1,
    b2,
    m1,
    carota1,
    a1,
    x1,
    x2,
])

problem.set_initial_value(ontable(b1), True)
problem.set_initial_value(ontable(b2), True)
problem.set_initial_value(at(b1, x1, x1), True)
problem.set_initial_value(at(b2, x2, x2), True)
problem.set_initial_value(clear(b1), True)
problem.set_initial_value(clear(b2), True)
problem.set_initial_value(available(a1), True)
problem.set_initial_value(intera(m1), True)
problem.set_initial_value(cruda(carota1), True)

problem.add_goal(ontable(b2))
problem.add_goal(on(b1, b2))
problem.add_goal(at(b1, x2, x2))
problem.add_goal(at(b2, x2, x2))
problem.add_goal(clear(b1))
problem.add_goal(available(a1))
problem.add_goal(morsa(m1))
problem.add_goal(cotta(carota1))

# --- action move_table_to_block_start
move_table_to_block_start = InstantaneousAction('move_table_to_block_start', Param1=Agent, Param2=Block, Param3=Block, Param4=Pos, Param5=Pos, Param6=Pos, Param7=Pos)
Param1 = move_table_to_block_start.parameter('Param1')
Param2 = move_table_to_block_start.parameter('Param2')
Param3 = move_table_to_block_start.parameter('Param3')
Param4 = move_table_to_block_start.parameter('Param4')
Param5 = move_table_to_block_start.parameter('Param5')
Param6 = move_table_to_block_start.parameter('Param6')
Param7 = move_table_to_block_start.parameter('Param7')
move_table_to_block_start.add_precondition(available(Param1))
move_table_to_block_start.add_precondition(ontable(Param2))
move_table_to_block_start.add_precondition(at(Param2, Param4, Param5))
move_table_to_block_start.add_precondition(at(Param3, Param6, Param7))
move_table_to_block_start.add_precondition(clear(Param3))
move_table_to_block_start.add_precondition(clear(Param2))
any_move_table_to_block_start_0 = Variable('any_move_table_to_block_start_0', Block)
move_table_to_block_start.add_precondition(Not(Exists(on(any_move_table_to_block_start_0, Param2), any_move_table_to_block_start_0)))
any_move_table_to_block_start_1 = Variable('any_move_table_to_block_start_1', Block)
move_table_to_block_start.add_precondition(Not(Exists(on(Param2, any_move_table_to_block_start_1), any_move_table_to_block_start_1)))
any_move_table_to_block_start_0 = Variable('any_move_table_to_block_start_0', Agent)
any_move_table_to_block_start_2 = Variable('any_move_table_to_block_start_2', Block)
any_move_table_to_block_start_3 = Variable('any_move_table_to_block_start_3', Pos)
any_move_table_to_block_start_4 = Variable('any_move_table_to_block_start_4', Pos)
any_move_table_to_block_start_5 = Variable('any_move_table_to_block_start_5', Pos)
any_move_table_to_block_start_6 = Variable('any_move_table_to_block_start_6', Pos)
move_table_to_block_start.add_precondition(Not(Exists(moving_table_to_block(any_move_table_to_block_start_0, Param2, any_move_table_to_block_start_2, any_move_table_to_block_start_3, any_move_table_to_block_start_4, any_move_table_to_block_start_5, any_move_table_to_block_start_6), any_move_table_to_block_start_0, any_move_table_to_block_start_2, any_move_table_to_block_start_3, any_move_table_to_block_start_4, any_move_table_to_block_start_5, any_move_table_to_block_start_6)))
move_table_to_block_start.add_effect(available(Param1), False)
move_table_to_block_start.add_effect(clear(Param2), False)
move_table_to_block_start.add_effect(ontable(Param2), False)
move_table_to_block_start.add_effect(at(Param2, Param4, Param5), False)
move_table_to_block_start.add_effect(moving_table_to_block(Param1, Param2, Param3, Param4, Param5, Param6, Param7), True)
problem.add_action(move_table_to_block_start)

# --- action move_table_to_block_end
move_table_to_block_end = InstantaneousAction('move_table_to_block_end', Param1=Agent, Param2=Block, Param3=Block, Param4=Pos, Param5=Pos, Param6=Pos, Param7=Pos)
Param1 = move_table_to_block_end.parameter('Param1')
Param2 = move_table_to_block_end.parameter('Param2')
Param3 = move_table_to_block_end.parameter('Param3')
Param4 = move_table_to_block_end.parameter('Param4')
Param5 = move_table_to_block_end.parameter('Param5')
Param6 = move_table_to_block_end.parameter('Param6')
Param7 = move_table_to_block_end.parameter('Param7')
move_table_to_block_end.add_precondition(moving_table_to_block(Param1, Param2, Param3, Param4, Param5, Param6, Param7))
move_table_to_block_end.add_precondition(clear(Param3))
move_table_to_block_end.add_effect(clear(Param3), False)
move_table_to_block_end.add_effect(moving_table_to_block(Param1, Param2, Param3, Param4, Param5, Param6, Param7), False)
move_table_to_block_end.add_effect(on(Param2, Param3), True)
move_table_to_block_end.add_effect(at(Param2, Param6, Param7), True)
move_table_to_block_end.add_effect(clear(Param2), True)
move_table_to_block_end.add_effect(available(Param1), True)
problem.add_action(move_table_to_block_end)

# --- action mangia_mela
mangia_mela = InstantaneousAction('mangia_mela', Param1=Agent, Param2=Mela)
Param1 = mangia_mela.parameter('Param1')
Param2 = mangia_mela.parameter('Param2')
mangia_mela.add_precondition(intera(Param2))
mangia_mela.add_precondition(available(Param1))
mangia_mela.add_effect(intera(Param2), False)
mangia_mela.add_effect(available(Param1), False)
mangia_mela.add_effect(morsa(Param2), True)
problem.add_action(mangia_mela)

# --- action cuoci
cuoci = InstantaneousAction('cuoci', Param1=Agent, Param2=Vegetale)
Param1 = cuoci.parameter('Param1')
Param2 = cuoci.parameter('Param2')
cuoci.add_precondition(available(Param1))
cuoci.add_precondition(cruda(Param2))
cuoci.add_effect(cruda(Param2), False)
cuoci.add_effect(cotta(Param2), True)
problem.add_action(cuoci)

writer = PDDLWriter(problem)
writer.write_domain('generated_domain.pddl')
writer.write_problem('generated_problem.pddl')
print('Generated PDDL files in current directory')