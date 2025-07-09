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

Patient = UserType('patient')
Staff = UserType('staff')
Procedure = UserType('procedure')
Resource = UserType('resource')

Pos = UserType('pos')

needs_procedure = Fluent('needs_procedure', BoolType(), p0=Patient, p1=Procedure)
procedure_done = Fluent('procedure_done', BoolType(), p0=Patient, p1=Procedure)
available = Fluent('available', BoolType(), p0=Staff)

problem = Problem('from_prolog')
problem.add_fluent(needs_procedure, default_initial_value=False)
problem.add_fluent(procedure_done, default_initial_value=False)
problem.add_fluent(available, default_initial_value=False)

p1 = Object('p1', Patient)
p2 = Object('p2', Patient)
doctor1 = Object('doctor1', Staff)
nurse1 = Object('nurse1', Staff)
technician1 = Object('technician1', Staff)
electrocardiogram = Object('electrocardiogram', Procedure)
problem.add_objects([
    p1,
    p2,
    doctor1,
    nurse1,
    technician1,
    electrocardiogram,
])

problem.set_initial_value(needs_procedure(p1, electrocardiogram), True)
problem.set_initial_value(needs_procedure(p1, blood_test), True)
problem.set_initial_value(needs_procedure(p2, x_ray), True)
problem.set_initial_value(available(doctor1), True)
problem.set_initial_value(available(nurse1), True)
problem.set_initial_value(available(technician1), True)
problem.set_initial_value(available(equipment_ecg), True)
problem.set_initial_value(available(equipment_xray), True)
problem.set_initial_value(available(lab_blood_test), True)

problem.add_goal(procedure_done(p1, electrocardiogram))
problem.add_goal(procedure_done(p1, blood_test))
problem.add_goal(procedure_done(p2, x_ray))
problem.add_goal(available(doctor1))
problem.add_goal(available(nurse1))
problem.add_goal(available(technician1))
problem.add_goal(available(equipment_ecg))
problem.add_goal(available(equipment_xray))
problem.add_goal(available(lab_blood_test))

# --- action perform_ecg
perform_ecg = InstantaneousAction('perform_ecg', Param1=Staff, Param2=Patient)
Param1 = perform_ecg.parameter('Param1')
Param2 = perform_ecg.parameter('Param2')
perform_ecg.add_precondition(needs_procedure(Param2, electrocardiogram))
perform_ecg.add_precondition(available(Param1))
perform_ecg.add_precondition(available(equipment_ecg))
perform_ecg.add_effect(needs_procedure(Param2, electrocardiogram), False)
perform_ecg.add_effect(available(Param1), False)
perform_ecg.add_effect(available(equipment_ecg), False)
perform_ecg.add_effect(procedure_done(Param2, electrocardiogram), True)
perform_ecg.add_effect(available(Param1), True)
perform_ecg.add_effect(available(equipment_ecg), True)
problem.add_action(perform_ecg)

# --- action perform_blood_test
perform_blood_test = InstantaneousAction('perform_blood_test', Param1=Staff, Param2=Patient)
Param1 = perform_blood_test.parameter('Param1')
Param2 = perform_blood_test.parameter('Param2')
perform_blood_test.add_precondition(needs_procedure(Param2, blood_test))
perform_blood_test.add_precondition(available(Param1))
perform_blood_test.add_precondition(available(lab_blood_test))
perform_blood_test.add_effect(needs_procedure(Param2, blood_test), False)
perform_blood_test.add_effect(available(Param1), False)
perform_blood_test.add_effect(available(lab_blood_test), False)
perform_blood_test.add_effect(procedure_done(Param2, blood_test), True)
perform_blood_test.add_effect(available(Param1), True)
perform_blood_test.add_effect(available(lab_blood_test), True)
problem.add_action(perform_blood_test)

# --- action perform_xray
perform_xray = InstantaneousAction('perform_xray', Param1=Staff, Param2=Patient)
Param1 = perform_xray.parameter('Param1')
Param2 = perform_xray.parameter('Param2')
perform_xray.add_precondition(needs_procedure(Param2, x_ray))
perform_xray.add_precondition(available(Param1))
perform_xray.add_precondition(available(equipment_xray))
perform_xray.add_effect(needs_procedure(Param2, x_ray), False)
perform_xray.add_effect(available(Param1), False)
perform_xray.add_effect(available(equipment_xray), False)
perform_xray.add_effect(procedure_done(Param2, x_ray), True)
perform_xray.add_effect(available(Param1), True)
perform_xray.add_effect(available(equipment_xray), True)
problem.add_action(perform_xray)

writer = PDDLWriter(problem)
writer.write_domain('generated_domain.pddl')
writer.write_problem('generated_problem.pddl')
print('Generated PDDL files in current directory')