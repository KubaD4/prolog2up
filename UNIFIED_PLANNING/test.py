import time 
start_time = time.time()  

import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.model.operators import OperatorKind

up.shortcuts.get_environment().credits_stream = None

# Define types
Location = UserType("Location")
Block = UserType("Block")
Agent = UserType("Agent")

# Define fluents
ontable = Fluent("ontable", BoolType(), b=Block)
on = Fluent("on", BoolType(), b1=Block, b2=Block)
at = Fluent("at", BoolType(), b=Block, l=Location)
clear = Fluent("clear", BoolType(), b=Block)
available = Fluent("available", BoolType(), a=Agent)
empty = Fluent("empty", BoolType(), l=Location) 

# Define movement state fluents
moving_table_to_table = Fluent("moving_table_to_table", BoolType(), 
                              a=Agent, b=Block, 
                              l1=Location, l2=Location)

moving_table_to_block = Fluent("moving_table_to_block", BoolType(),
                               a=Agent, b1=Block, b2=Block,
                               l1=Location, l2=Location)
                               
moving_onblock_to_table = Fluent("moving_onblock_to_table", BoolType(),
                                 a=Agent, b=Block, 
                                 l1=Location, l2=Location)
                                 
moving_onblock_to_block = Fluent("moving_onblock_to_block", BoolType(),
                                a=Agent, b1=Block, b2=Block,
                                l1=Location, l2=Location)

# Create positions
positions = []
pos_dict = {}  # (1,1) -> pos_1_1 object
for x, y in [(1,1), (2,2), (3,3), (10,10)]:
    pos_name = f"loc_{x}_{y}"
    l = Object(pos_name, Location)
    positions.append(l)
    pos_dict[(x,y)] = l

# Create Problem
problem = Problem('blocks')

# Add fluents to problem
problem.add_fluent(ontable, default_initial_value=False)
problem.add_fluent(on, default_initial_value=False)
problem.add_fluent(at, default_initial_value=False)
problem.add_fluent(clear, default_initial_value=False)
problem.add_fluent(available, default_initial_value=False)
problem.add_fluent(empty, default_initial_value=True) 
problem.add_fluent(moving_table_to_table, default_initial_value=False)
problem.add_fluent(moving_table_to_block, default_initial_value=False)
problem.add_fluent(moving_onblock_to_table, default_initial_value=False)
problem.add_fluent(moving_onblock_to_block, default_initial_value=False)

# Create blocks and agents
N_BLOCKS = 6
blocks = [Object(f'b{i+1}', Block) for i in range(N_BLOCKS)]
problem.add_objects(blocks)

N_AGENTS = 2
agents = [Object(f'a{i+1}', Agent) for i in range(N_AGENTS)]
problem.add_objects(agents)
problem.add_objects(positions)

print(f"\n======== Time until ACTIONS: {time.time() - start_time:.4f} seconds ========")
actions_timer = time.time()

# =================================================================
# ======= ACTION 1: move_table_to_table_start =====================
# =================================================================
move_table_to_table_start = InstantaneousAction('move_table_to_table_start', 
                                               a=Agent, 
                                               b=Block, 
                                               l1=Location, 
                                               l2=Location)
a = move_table_to_table_start.parameter('a')
b = move_table_to_table_start.parameter('b')
l1 = move_table_to_table_start.parameter('l1')
l2 = move_table_to_table_start.parameter('l2')

# Add positive preconditions
move_table_to_table_start.add_precondition(ontable(b))
move_table_to_table_start.add_precondition(at(b, l1))
move_table_to_table_start.add_precondition(available(a))
move_table_to_table_start.add_precondition(clear(b))

# TODO: NON SERVE A NIENTE EMPTY
move_table_to_table_start.add_precondition(empty(l2))

# Block is not being moved from other a
move_table_to_table_start.add_precondition(Not(moving_table_to_table(a, b, l1, l2)))
move_table_to_table_start.add_precondition(Not(moving_table_to_block(a, b, l1, l2)))

# TODO: manca:

# Prima parte: non ci deve essere alcuna azione moving_table_to_table in corso
""" move_table_to_table_start.add_precondition(
    Not(Exists(
        moving_table_to_table(a, b, x1, y1, x2, y2),
        b, x1, y1, x2, y2
    ))
)

# Seconda parte: non ci deve essere alcuna azione moving_table_to_block in corso
move_table_to_table_start.add_precondition(
    Not(Exists(
        moving_table_to_block(a, b, b2, x1, y1, x2, y2),
        b, b2, x1, y1, x2, y2
    ))
) """

# TODO: guarda risposta Claude per come riscriverlo bene. Poi fallo rifare a per tutti


# 3) no other b is being moved *from* or *to* here
b2 = Variable("b2", Block)
b3 = Variable("b3", Block)

move_table_to_table_start.add_precondition(
    Not(Exists(
        moving_onblock_to_table(a, b2, l1, l2),
        b2 
    ))
)
move_table_to_table_start.add_precondition(
    Not(Exists(
        moving_onblock_to_block(a, b2, b3, l1, l2),
        b2, b3
        ))
)
move_table_to_table_start.add_precondition(
    Not(Exists(
        moving_table_to_block(a, b2, b3, l1, l2),
        b2, b3
    ))
)

# Add effects
move_table_to_table_start.add_effect(available(a), False)
move_table_to_table_start.add_effect(clear(b), False)
move_table_to_table_start.add_effect(ontable(b), False)
move_table_to_table_start.add_effect(at(b, l1), False)
move_table_to_table_start.add_effect(empty(l1), True)  
move_table_to_table_start.add_effect(moving_table_to_table(a, b, l1, l2), True)

problem.add_action(move_table_to_table_start)

# =================================================================
# ======= ACTION 2: move_table_to_table_end =======================
# =================================================================
move_table_to_table_end = InstantaneousAction('move_table_to_table_end', 
                                             a=Agent, 
                                             b=Block, 
                                             l1=Location, 
                                             l2=Location)
a = move_table_to_table_end.parameter('a')
b = move_table_to_table_end.parameter('b')
l1 = move_table_to_table_end.parameter('l1')
l2 = move_table_to_table_end.parameter('l2')

# Add preconditions
move_table_to_table_end.add_precondition(moving_table_to_table(a, b, l1, l2))
move_table_to_table_end.add_precondition(empty(l2))

# Add effects
move_table_to_table_end.add_effect(moving_table_to_table(a, b, l1, l2), False)
move_table_to_table_end.add_effect(ontable(b), True)
move_table_to_table_end.add_effect(at(b, l2), True)
move_table_to_table_end.add_effect(clear(b), True)
move_table_to_table_end.add_effect(available(a), True)
move_table_to_table_end.add_effect(empty(l2), False)

problem.add_action(move_table_to_table_end)

# =================================================================
# ======= ACTION 3: move_table_to_block_start ====================
# =================================================================
move_table_to_block_start = InstantaneousAction('move_table_to_block_start', 
                                               a=Agent, 
                                               b1=Block, 
                                               b2=Block, 
                                               l1=Location, 
                                               l2=Location)
a = move_table_to_block_start.parameter('a')
b1 = move_table_to_block_start.parameter('b1')
b2 = move_table_to_block_start.parameter('b2')
l1 = move_table_to_block_start.parameter('l1')
l2 = move_table_to_block_start.parameter('l2')

# Add positive preconditions
move_table_to_block_start.add_precondition(available(a))
move_table_to_block_start.add_precondition(ontable(b1))
move_table_to_block_start.add_precondition(at(b1, l1))
move_table_to_block_start.add_precondition(at(b2, l2))
move_table_to_block_start.add_precondition(clear(b2))
move_table_to_block_start.add_precondition(clear(b1))
move_table_to_block_start.add_precondition(Not(Equals(b1, b2)))

# Block b1 is not being moved in any other action
move_table_to_block_start.add_precondition(Not(moving_table_to_block(a, b1, b2, l1, l2)))

# No other blocks are being moved to or from these locations
b3 = Variable("b3", Block)
b4 = Variable("b4", Block)

move_table_to_block_start.add_precondition(
    Not(Exists(
        moving_table_to_table(a, b3, l1, l2),
        b3
    ))
)
move_table_to_block_start.add_precondition(
    Not(Exists(
        moving_onblock_to_table(a, b3, l1, l2),
        b3
    ))
)
move_table_to_block_start.add_precondition(
    Not(Exists(
        moving_onblock_to_block(a, b3, b4, l1, l2),
        b3, b4
    ))
)

# Add effects
move_table_to_block_start.add_effect(available(a), False)
move_table_to_block_start.add_effect(clear(b1), False)
move_table_to_block_start.add_effect(ontable(b1), False)
move_table_to_block_start.add_effect(at(b1, l1), False)
move_table_to_block_start.add_effect(empty(l1), True)
move_table_to_block_start.add_effect(moving_table_to_block(a, b1, b2, l1, l2), True)

problem.add_action(move_table_to_block_start)

# =================================================================
# ======= ACTION 4: move_table_to_block_end ======================
# =================================================================
move_table_to_block_end = InstantaneousAction('move_table_to_block_end', 
                                             a=Agent, 
                                             b1=Block, 
                                             b2=Block, 
                                             l1=Location, 
                                             l2=Location)
a = move_table_to_block_end.parameter('a')
b1 = move_table_to_block_end.parameter('b1')
b2 = move_table_to_block_end.parameter('b2')
l1 = move_table_to_block_end.parameter('l1')
l2 = move_table_to_block_end.parameter('l2')

# Add positive preconditions
move_table_to_block_end.add_precondition(moving_table_to_block(a, b1, b2, l1, l2))
move_table_to_block_end.add_precondition(clear(b2))

# Add effects
move_table_to_block_end.add_effect(clear(b2), False)
move_table_to_block_end.add_effect(moving_table_to_block(a, b1, b2, l1, l2), False)
move_table_to_block_end.add_effect(on(b1, b2), True)
move_table_to_block_end.add_effect(at(b1, l2), True)
move_table_to_block_end.add_effect(clear(b1), True)
move_table_to_block_end.add_effect(available(a), True)

problem.add_action(move_table_to_block_end)

# =================================================================
# ======= ACTION 5: move_onblock_to_table_start ==================
# =================================================================
move_onblock_to_table_start = InstantaneousAction('move_onblock_to_table_start', 
                                                 a=Agent, 
                                                 b1=Block, 
                                                 b2=Block,
                                                 l1=Location, 
                                                 l2=Location)
a = move_onblock_to_table_start.parameter('a')
b1 = move_onblock_to_table_start.parameter('b1')
b2 = move_onblock_to_table_start.parameter('b2')
l1 = move_onblock_to_table_start.parameter('l1')
l2 = move_onblock_to_table_start.parameter('l2')

# Add positive preconditions
move_onblock_to_table_start.add_precondition(available(a))
move_onblock_to_table_start.add_precondition(on(b1, b2))  # Block1 is on Block2
move_onblock_to_table_start.add_precondition(at(b1, l1))
move_onblock_to_table_start.add_precondition(at(b2, l1))
move_onblock_to_table_start.add_precondition(clear(b1))
move_onblock_to_table_start.add_precondition(Not(Equals(b1, b2)))
move_onblock_to_table_start.add_precondition(Not(ontable(b1)))
move_onblock_to_table_start.add_precondition(empty(l2))

# Block1 is not being moved in any other action
move_onblock_to_table_start.add_precondition(Not(moving_onblock_to_table(a, b1, l1, l2)))

# No other blocks are being moved to or from these locations
b3 = Variable("b3", Block)
b4 = Variable("b4", Block)

move_onblock_to_table_start.add_precondition(
    Not(Exists(
        moving_table_to_table(a, b3, l1, l2),
        b3
    ))
)
move_onblock_to_table_start.add_precondition(
    Not(Exists(
        moving_table_to_block(a, b3, b4, l1, l2),
        b3, b4
    ))
)
move_onblock_to_table_start.add_precondition(
    Not(Exists(
        moving_onblock_to_block(a, b3, b4, l1, l2),
        b3, b4
    ))
)

# Add effects
move_onblock_to_table_start.add_effect(available(a), False)
move_onblock_to_table_start.add_effect(clear(b1), False)
move_onblock_to_table_start.add_effect(on(b1, b2), False)
move_onblock_to_table_start.add_effect(at(b1, l1), False)
move_onblock_to_table_start.add_effect(moving_onblock_to_table(a, b1, l1, l2), True)
move_onblock_to_table_start.add_effect(clear(b2), True)

problem.add_action(move_onblock_to_table_start)

# =================================================================
# ======= ACTION 6: move_onblock_to_table_end ====================
# =================================================================
move_onblock_to_table_end = InstantaneousAction('move_onblock_to_table_end', 
                                               a=Agent, 
                                               b1=Block, 
                                               l1=Location, 
                                               l2=Location)
a = move_onblock_to_table_end.parameter('a')
b1 = move_onblock_to_table_end.parameter('b1')
l1 = move_onblock_to_table_end.parameter('l1')
l2 = move_onblock_to_table_end.parameter('l2')

# Add positive preconditions
move_onblock_to_table_end.add_precondition(moving_onblock_to_table(a, b1, l1, l2))
move_onblock_to_table_end.add_precondition(empty(l2))

# Add effects
move_onblock_to_table_end.add_effect(moving_onblock_to_table(a, b1, l1, l2), False)
move_onblock_to_table_end.add_effect(ontable(b1), True)
move_onblock_to_table_end.add_effect(at(b1, l2), True)
move_onblock_to_table_end.add_effect(clear(b1), True)
move_onblock_to_table_end.add_effect(available(a), True)
move_onblock_to_table_end.add_effect(empty(l2), False)

problem.add_action(move_onblock_to_table_end)

# =================================================================
# ======= ACTION 7: move_onblock_to_block_start =================
# =================================================================
move_onblock_to_block_start = InstantaneousAction('move_onblock_to_block_start', 
                                                 a=Agent, 
                                                 b1=Block, 
                                                 b2=Block, 
                                                 b3=Block,  # The block that b1 is currently on
                                                 l1=Location, 
                                                 l2=Location)
a = move_onblock_to_block_start.parameter('a')
b1 = move_onblock_to_block_start.parameter('b1')
b2 = move_onblock_to_block_start.parameter('b2')
b3 = move_onblock_to_block_start.parameter('b3')
l1 = move_onblock_to_block_start.parameter('l1')
l2 = move_onblock_to_block_start.parameter('l2')

# Add positive preconditions
move_onblock_to_block_start.add_precondition(available(a))
move_onblock_to_block_start.add_precondition(on(b1, b3))  # b1 is on b3
move_onblock_to_block_start.add_precondition(at(b1, l1))
move_onblock_to_block_start.add_precondition(at(b3, l1))
move_onblock_to_block_start.add_precondition(at(b2, l2))
move_onblock_to_block_start.add_precondition(clear(b2))
move_onblock_to_block_start.add_precondition(clear(b1))
# Questi sono specificati in PROLOG
move_onblock_to_block_start.add_precondition(Not(Equals(b1, b2)))
move_onblock_to_block_start.add_precondition(Not(Equals(b1, b3)))
move_onblock_to_block_start.add_precondition(Not(Equals(b2, b3)))
move_onblock_to_block_start.add_precondition(Not(ontable(b1)))
move_onblock_to_block_start.add_precondition(Not(moving_onblock_to_block(a, b1, b2, l1, l2))) # b1 is not being moved in any other action

# No other blocks are being moved to or from these locations
b4 = Variable("b4", Block)
b5 = Variable("b5", Block)

move_onblock_to_block_start.add_precondition(
    Not(Exists(
        moving_table_to_table(a, b4, l1, l2),
        b4
    ))
)
move_onblock_to_block_start.add_precondition(
    Not(Exists(
        moving_table_to_block(a, b4, b5, l1, l2),
        b4, b5
    ))
)
move_onblock_to_block_start.add_precondition(
    Not(Exists(
        moving_onblock_to_table(a, b4, l1, l2),
        b4
    ))
)

# Add effects
move_onblock_to_block_start.add_effect(available(a), False)
move_onblock_to_block_start.add_effect(clear(b1), False)
move_onblock_to_block_start.add_effect(on(b1, b3), False)
move_onblock_to_block_start.add_effect(at(b1, l1), False)
move_onblock_to_block_start.add_effect(moving_onblock_to_block(a, b1, b2, l1, l2), True)
move_onblock_to_block_start.add_effect(clear(b3), True)

problem.add_action(move_onblock_to_block_start)

# =================================================================
# ======= ACTION 8: move_onblock_to_block_end ===================
# =================================================================
move_onblock_to_block_end = InstantaneousAction('move_onblock_to_block_end', 
                                               a=Agent, 
                                               b1=Block, 
                                               b2=Block, 
                                               l1=Location, 
                                               l2=Location)
a = move_onblock_to_block_end.parameter('a')
b1 = move_onblock_to_block_end.parameter('b1')
b2 = move_onblock_to_block_end.parameter('b2')
l1 = move_onblock_to_block_end.parameter('l1')
l2 = move_onblock_to_block_end.parameter('l2')

# Add positive preconditions
move_onblock_to_block_end.add_precondition(moving_onblock_to_block(a, b1, b2, l1, l2))
move_onblock_to_block_end.add_precondition(clear(b2))

# Add effects
move_onblock_to_block_end.add_effect(clear(b2), False)
move_onblock_to_block_end.add_effect(moving_onblock_to_block(a, b1, b2, l1, l2), False)
move_onblock_to_block_end.add_effect(on(b1, b2), True)
move_onblock_to_block_end.add_effect(at(b1, l2), True)
move_onblock_to_block_end.add_effect(clear(b1), True)
move_onblock_to_block_end.add_effect(available(a), True)

problem.add_action(move_onblock_to_block_end)


print(f"\n======== Total time for ACTIONS: {time.time() - actions_timer:.4f} seconds ========")
goal_timer = time.time()
# Set initial state
for i in range(3):
    problem.set_initial_value(ontable(blocks[i]), True)  # b1, b2, b3 on table
    problem.set_initial_value(on(blocks[i+3], blocks[i]), True)  # b4 on b1, b5 on b2, b6 on b3
    
    problem.set_initial_value(at(blocks[i], pos_dict[(i+1, i+1)]), True)  # b1 at (1,1), b2 at (2,2), b3 at (3,3)
    problem.set_initial_value(at(blocks[i+3], pos_dict[(i+1, i+1)]), True)  # b4 at (1,1), b5 at (2,2), b6 at (3,3)
    
    problem.set_initial_value(clear(blocks[i+3]), True)  # b4, b5, b6 are clear
    
    # Set positions as not empty where blocks are located
    problem.set_initial_value(empty(pos_dict[(i+1, i+1)]), False)  # NEW: Positions with blocks are not empty

# Positions without blocks are empty
problem.set_initial_value(empty(pos_dict[(10,10)]), True)  # NEW: Position (10,10) is empty

# Agents are available
for a in agents:
    problem.set_initial_value(available(a), True)

# Set goal state
for i in range(4):
    problem.add_goal(ontable(blocks[i]))  # b1, b2, b3, b4 on table

# b5 on b4, b6 on b3
problem.add_goal(on(blocks[4], blocks[3]))  # b5 on b4
problem.add_goal(on(blocks[5], blocks[2]))  # b6 on b3

problem.add_goal(at(blocks[0], pos_dict[(1,1)]))   # b1 at (1,1)
problem.add_goal(at(blocks[1], pos_dict[(2,2)]))   # b2 at (2,2)
problem.add_goal(at(blocks[2], pos_dict[(3,3)]))   # b3 at (3,3)
problem.add_goal(at(blocks[3], pos_dict[(10,10)])) # b4 at (10,10)
problem.add_goal(at(blocks[4], pos_dict[(10,10)])) # b5 at (10,10)
problem.add_goal(at(blocks[5], pos_dict[(3,3)]))   # b6 at (3,3)

problem.add_goal(clear(blocks[0]))  # b1 is clear
problem.add_goal(clear(blocks[1]))  # b2 is clear
problem.add_goal(clear(blocks[4]))  # b5 is clear
problem.add_goal(clear(blocks[5]))  # b6 is clear

for a in agents:
    problem.add_goal(available(a))

print(f"\n======== Total TIme to add goals: {time.time() - goal_timer:.4f} seconds ========")

def export_to_pddl():
    """Export the problem to PDDL files and print the contents."""
    function_start_time = time.time()
    print("\nSTART PDDL Exporting...")
    writer = PDDLWriter(problem)
    
    # Write to files
    domain_filename = "test_domain.pddl"
    problem_filename = "test_problem.pddl"
    
    writer.write_domain(domain_filename)
    writer.write_problem(problem_filename)
    
    print(f"Domain written to: {domain_filename}")
    print(f"Problem written to: {problem_filename}")
    
    print("\nDOMAIN PDDL:")
    domain_str = writer.get_domain()
    #print(domain_str[:1000] + "..." if len(domain_str) > 1000 else domain_str)
    
    print("\nPROBLEM PDDL:")
    problem_str = writer.get_problem()
    #print(problem_str[:1000] + "..." if len(problem_str) > 1000 else problem_str)
    
    function_end_time = time.time()
    print(f"\nPDDL EXPORT COMPLETED in {function_end_time - function_start_time:.4f} seconds")

def solve_problem():
    print("\n===== PROBLEM DETAILS =====")
    print(f"Problem kind: {problem.kind}")
    
    print("\n===== TRYING AUTOMATIC ENGINE SELECTION =====")
    function_start_time = time.time()
    try:
        with OneshotPlanner(problem_kind=problem.kind) as planner:
        #with OneshotPlanner(name='fast-downward') as planner:
            print(f"Selected planner: {planner.name}")
            result = planner.solve(problem)
            print(f"Plan status: {result.status}")
            if result.status in [unified_planning.engines.results.PlanGenerationResultStatus.SOLVED_SATISFICING,
                                unified_planning.engines.results.PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
                print("\nPlan found:")
                for action in result.plan.actions:
                    print(f"  {action}")
                function_end_time = time.time()
                print(f"\nProblem solving completed in {function_end_time - function_start_time:.4f} seconds")
            else:
                print("No plan found with automatic engine selection.\n")
                function_end_time = time.time()
                print(f"\nProblem solving failed: {function_end_time - function_start_time:.4f} seconds")
    except Exception as e:
        print(f"Error with automatic engine selection: {e}")


# Solving
print(f"\nTime until function calls: {time.time() - start_time:.4f} seconds")

export_to_pddl()
# solve_problem()

print(f"\nTotal execution time: {time.time() - start_time:.4f} seconds")