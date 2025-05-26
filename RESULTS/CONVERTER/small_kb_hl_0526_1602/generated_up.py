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

Block = UserType('block')
Agent = UserType('agent')
Mela = UserType('mela')
Vegetale = UserType('vegetale')
Location = UserType('Location')

# Create position objects for coordinates
positions = []
pos_dict = {}  # (x,y) -> position object mapping
loc_1_1 = Object('loc_1_1', Location)
positions.append(loc_1_1)
pos_dict[(1,1)] = loc_1_1
loc_2_2 = Object('loc_2_2', Location)
positions.append(loc_2_2)
pos_dict[(2,2)] = loc_2_2

cotta = Fluent('cotta', BoolType(), p0=Vegetale)
clear = Fluent('clear', BoolType(), p0=Block)
moving_table_to_block = Fluent('moving_table_to_block', BoolType(), p0=Agent, p1=Block, p2=Block, p3=Location, p4=Location, p5=Location, p6=Location)
at = Fluent('at', BoolType(), p0=Block, p1=Location)
ontable = Fluent('ontable', BoolType(), p0=Block)
morsa = Fluent('morsa', BoolType(), p0=Mela)
intera = Fluent('intera', BoolType(), p0=Mela)
cruda = Fluent('cruda', BoolType(), p0=Vegetale)
available = Fluent('available', BoolType(), p0=Agent)
on = Fluent('on', BoolType(), p0=Block, p1=Block)

problem = Problem('from_prolog')
problem.add_fluent(cotta, default_initial_value=False)
problem.add_fluent(clear, default_initial_value=False)
problem.add_fluent(moving_table_to_block, default_initial_value=False)
problem.add_fluent(at, default_initial_value=False)
problem.add_fluent(ontable, default_initial_value=False)
problem.add_fluent(morsa, default_initial_value=False)
problem.add_fluent(intera, default_initial_value=False)
problem.add_fluent(cruda, default_initial_value=False)
problem.add_fluent(available, default_initial_value=False)
problem.add_fluent(on, default_initial_value=False)

# Add regular objects

# Add position objects
problem.add_objects(positions)

problem.add_objects([
])

# Set initial state
problem.set_initial_value(ontable(b1), True)
problem.set_initial_value(ontable(b2), True)
problem.set_initial_value(at(b1, loc_1_1), True)
problem.set_initial_value(at(b2, loc_2_2), True)
problem.set_initial_value(clear(b1), True)
problem.set_initial_value(clear(b2), True)
problem.set_initial_value(available(a1), True)
problem.set_initial_value(intera(m1), True)
problem.set_initial_value(cruda(carota1), True)

# Set goal state
problem.add_goal(ontable(b2))
problem.add_goal(on(b1, b2))
problem.add_goal(at(b1, loc_2_2))
problem.add_goal(at(b2, loc_2_2))
problem.add_goal(clear(b1))
problem.add_goal(available(a1))
problem.add_goal(morsa(m1))
problem.add_goal(cotta(carota1))

# --- action move_table_to_block_start
move_table_to_block_start = InstantaneousAction('move_table_to_block_start', Param1=Agent, Param2=Block, Param3=Block, Param4=Location, Param5=Location, Param6=Location, Param7=Location)
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
any_move_table_to_block_start_3 = Variable('any_move_table_to_block_start_3', Location)
any_move_table_to_block_start_4 = Variable('any_move_table_to_block_start_4', Location)
any_move_table_to_block_start_5 = Variable('any_move_table_to_block_start_5', Location)
any_move_table_to_block_start_6 = Variable('any_move_table_to_block_start_6', Location)
move_table_to_block_start.add_precondition(Not(Exists(moving_table_to_block(any_move_table_to_block_start_0, Param2, any_move_table_to_block_start_2, any_move_table_to_block_start_3, any_move_table_to_block_start_4, any_move_table_to_block_start_5, any_move_table_to_block_start_6), any_move_table_to_block_start_0, any_move_table_to_block_start_2, any_move_table_to_block_start_3, any_move_table_to_block_start_4, any_move_table_to_block_start_5, any_move_table_to_block_start_6)))
move_table_to_block_start.add_effect(available(Param1), False)
move_table_to_block_start.add_effect(clear(Param2), False)
move_table_to_block_start.add_effect(ontable(Param2), False)
move_table_to_block_start.add_effect(at(Param2, Param4, Param5), False)
move_table_to_block_start.add_effect(moving_table_to_block(Param1, Param2, Param3, Param4, Param5, Param6, Param7), True)
problem.add_action(move_table_to_block_start)

# --- action move_table_to_block_end
move_table_to_block_end = InstantaneousAction('move_table_to_block_end', Param1=Agent, Param2=Block, Param3=Block, Param4=Location, Param5=Location, Param6=Location, Param7=Location)
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