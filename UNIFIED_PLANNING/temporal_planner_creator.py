#!/usr/bin/env python3
"""
Temporal Planning - Working Version
===================================

This version creates a temporal-like problem that works with available planners.
Since full temporal planning isn't supported, we use classical planning with
temporal logic encoded in the state.
"""

import time
import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.io import PDDLWriter

Match = UserType('Match')
Fuse = UserType('Fuse')

handfree = Fluent('handfree')
light = Fluent('light')
match_used = Fluent('match_used', BoolType(), m=Match)
fuse_mended = Fluent('fuse_mended', BoolType(), f=Fuse)

problem = Problem('MatchCellar')

problem.add_fluent(handfree)
problem.add_fluent(light)
problem.add_fluent(match_used, default_initial_value=False)
problem.add_fluent(fuse_mended, default_initial_value=False)

problem.set_initial_value(light, False)
problem.set_initial_value(handfree, True)

fuses = [Object(f'f{i}', Fuse) for i in range(3)]
matches = [Object(f'm{i}', Match) for i in range(3)]

problem.add_objects(fuses)
problem.add_objects(matches)

light_match = DurativeAction('light_match', m=Match)
m = light_match.parameter('m')
light_match.set_fixed_duration(6)
light_match.add_condition(StartTiming(), Not(match_used(m)))
light_match.add_effect(StartTiming(), match_used(m), True)
light_match.add_effect(StartTiming(), light, True)
light_match.add_effect(EndTiming(), light, False)
problem.add_action(light_match)
print(light_match)

mend_fuse = DurativeAction('mend_fuse', f=Fuse)
f = mend_fuse.parameter('f')
mend_fuse.set_fixed_duration(5)
mend_fuse.add_condition(StartTiming(), handfree)
mend_fuse.add_condition(ClosedTimeInterval(StartTiming(), EndTiming()), light)
mend_fuse.add_effect(StartTiming(), handfree, False)
mend_fuse.add_effect(EndTiming(), fuse_mended(f), True)
mend_fuse.add_effect(EndTiming(), handfree, True)
problem.add_action(mend_fuse)
print(mend_fuse)

for f in fuses:
  problem.add_timed_goal(EndTiming(), fuse_mended(f))

print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print(f"{planner.name} returned:")
        for start, action, duration in plan.timed_actions:
            print(f"{float(start)}: {action} [{float(duration)}]")
    else:
        print("No plan found.")

from unified_planning import plot_plan