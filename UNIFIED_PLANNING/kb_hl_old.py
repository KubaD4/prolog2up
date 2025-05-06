import time 
start_time = time.time()  

import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.model import Variable, InstantaneousAction, Problem
from unified_planning.io import PDDLWriter
from unified_planning.model.operators import OperatorKind

up.shortcuts.get_environment().credits_stream = None

# Define types
Pos = UserType("Pos")
Block = UserType("Block")
Agent = UserType("Agent")



# Define fluents
ontable = Fluent("ontable", BoolType(), block=Block)
on = Fluent("on", BoolType(), block1=Block, block2=Block)
at = Fluent("at", BoolType(), block=Block, pos=Pos)
clear = Fluent("clear", BoolType(), block=Block)
available = Fluent("available", BoolType(), agent=Agent)
empty = Fluent("empty", BoolType(), pos=Pos)  # NEW: Added empty fluent

# Define movement state fluents
moving_table_to_table = Fluent("moving_table_to_table", BoolType(), 
                              agent=Agent, block=Block, 
                              from_pos=Pos, to_pos=Pos)

moving_table_to_block = Fluent("moving_table_to_block", BoolType(),
                               agent=Agent, block1=Block, block2=Block,
                               from_pos=Pos, to_pos=Pos)
                               
moving_onblock_to_table = Fluent("moving_onblock_to_table", BoolType(),
                                 agent=Agent, block=Block, 
                                 from_pos=Pos, to_pos=Pos)
                                 
moving_onblock_to_block = Fluent("moving_onblock_to_block", BoolType(),
                                agent=Agent, block1=Block, block2=Block,
                                from_pos=Pos, to_pos=Pos)

# Create positions
positions = []
pos_dict = {}  # (1,1) -> pos_1_1 object
for x, y in [(1,1), (2,2), (3,3), (10,10)]:
    pos_name = f"loc{x}_{y}"
    pos = Object(pos_name, Pos)
    positions.append(pos)
    pos_dict[(x,y)] = pos

# Create Problem
problem = Problem('blocks_world')

# Add fluents to problem
problem.add_fluent(ontable, default_initial_value=False)
problem.add_fluent(on, default_initial_value=False)
problem.add_fluent(at, default_initial_value=False)
problem.add_fluent(clear, default_initial_value=False)
problem.add_fluent(available, default_initial_value=False)
problem.add_fluent(empty, default_initial_value=True)  # NEW: All positions are initially empty
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

# ACTION 1: move_table_to_table_start
move_table_to_table_start = InstantaneousAction('move_table_to_table_start', 
                                               agent=Agent, 
                                               block=Block, 
                                               from_pos=Pos, 
                                               to_pos=Pos)
agent = move_table_to_table_start.parameter('agent')
block = move_table_to_table_start.parameter('block')
from_pos = move_table_to_table_start.parameter('from_pos')
to_pos = move_table_to_table_start.parameter('to_pos')

# Add positive preconditions
move_table_to_table_start.add_precondition(ontable(block))
move_table_to_table_start.add_precondition(at(block, from_pos))
move_table_to_table_start.add_precondition(available(agent))
move_table_to_table_start.add_precondition(clear(block))
move_table_to_table_start.add_precondition(empty(to_pos))  # NEW: Use the empty fluent

# Block is not being moved
any_block = Variable("any_block", Block)
any_pos = Variable("any_pos", Pos)

# Block is not on another block
move_table_to_table_start.add_precondition(Not(Exists([any_block], on(block, any_block))))  # CHANGED: Use Exists instead of Forall

# Block is not already being moved
move_table_to_table_start.add_precondition(Not(Exists([any_pos, any_pos], moving_table_to_table(agent, block, any_pos, any_pos))))  # CHANGED
move_table_to_table_start.add_precondition(Not(Exists([any_block, any_pos, any_pos], moving_table_to_block(agent, block, any_block, any_pos, any_pos))))  # CHANGED

# Add effects
move_table_to_table_start.add_effect(available(agent), False)
move_table_to_table_start.add_effect(clear(block), False)
move_table_to_table_start.add_effect(ontable(block), False)
move_table_to_table_start.add_effect(at(block, from_pos), False)
move_table_to_table_start.add_effect(empty(from_pos), True)  # NEW: from_pos becomes empty
move_table_to_table_start.add_effect(moving_table_to_table(agent, block, from_pos, to_pos), True)

problem.add_action(move_table_to_table_start)

# ACTION 2: move_table_to_table_end
move_table_to_table_end = InstantaneousAction('move_table_to_table_end', 
                                             agent=Agent, 
                                             block=Block, 
                                             from_pos=Pos, 
                                             to_pos=Pos)
agent = move_table_to_table_end.parameter('agent')
block = move_table_to_table_end.parameter('block')
from_pos = move_table_to_table_end.parameter('from_pos')
to_pos = move_table_to_table_end.parameter('to_pos')

# Add preconditions
move_table_to_table_end.add_precondition(moving_table_to_table(agent, block, from_pos, to_pos))
move_table_to_table_end.add_precondition(empty(to_pos))  # NEW: Destination must be empty

# Add effects
move_table_to_table_end.add_effect(moving_table_to_table(agent, block, from_pos, to_pos), False)
move_table_to_table_end.add_effect(ontable(block), True)
move_table_to_table_end.add_effect(at(block, to_pos), True)
move_table_to_table_end.add_effect(clear(block), True)
move_table_to_table_end.add_effect(available(agent), True)
move_table_to_table_end.add_effect(empty(to_pos), False)  # NEW: to_pos is no longer empty

problem.add_action(move_table_to_table_end)

# ACTION 3: move_table_to_block_start
move_table_to_block_start = InstantaneousAction('move_table_to_block_start', 
                                               agent=Agent, 
                                               block1=Block, 
                                               block2=Block, 
                                               from_pos=Pos, 
                                               to_pos=Pos)
agent = move_table_to_block_start.parameter('agent')
block1 = move_table_to_block_start.parameter('block1')
block2 = move_table_to_block_start.parameter('block2')
from_pos = move_table_to_block_start.parameter('from_pos')
to_pos = move_table_to_block_start.parameter('to_pos')

# Add positive preconditions
move_table_to_block_start.add_precondition(available(agent))
move_table_to_block_start.add_precondition(ontable(block1))
move_table_to_block_start.add_precondition(at(block1, from_pos))
move_table_to_block_start.add_precondition(at(block2, to_pos))
move_table_to_block_start.add_precondition(clear(block2))
move_table_to_block_start.add_precondition(clear(block1))
move_table_to_block_start.add_precondition(Not(Equals(block1, block2)))

# Block1 is not on any block
move_table_to_block_start.add_precondition(Not(Exists([any_block], on(block1, any_block))))  # CHANGED

# Block1 is not being moved by any action
move_table_to_block_start.add_precondition(Not(Exists([any_pos, any_pos], moving_table_to_table(agent, block1, any_pos, any_pos))))  # CHANGED
move_table_to_block_start.add_precondition(Not(Exists([any_block, any_pos, any_pos], moving_table_to_block(agent, block1, any_block, any_pos, any_pos))))  # CHANGED

# Add effects
move_table_to_block_start.add_effect(available(agent), False)
move_table_to_block_start.add_effect(clear(block1), False)
move_table_to_block_start.add_effect(ontable(block1), False)
move_table_to_block_start.add_effect(at(block1, from_pos), False)
move_table_to_block_start.add_effect(empty(from_pos), True)  # NEW: from_pos becomes empty
move_table_to_block_start.add_effect(moving_table_to_block(agent, block1, block2, from_pos, to_pos), True)

problem.add_action(move_table_to_block_start)

# ACTION 4: move_table_to_block_end
move_table_to_block_end = InstantaneousAction('move_table_to_block_end', 
                                             agent=Agent, 
                                             block1=Block, 
                                             block2=Block, 
                                             from_pos=Pos, 
                                             to_pos=Pos)
agent = move_table_to_block_end.parameter('agent')
block1 = move_table_to_block_end.parameter('block1')
block2 = move_table_to_block_end.parameter('block2')
from_pos = move_table_to_block_end.parameter('from_pos')
to_pos = move_table_to_block_end.parameter('to_pos')

# Add positive preconditions
move_table_to_block_end.add_precondition(moving_table_to_block(agent, block1, block2, from_pos, to_pos))
move_table_to_block_end.add_precondition(clear(block2))

# Add effects
move_table_to_block_end.add_effect(clear(block2), False)
move_table_to_block_end.add_effect(moving_table_to_block(agent, block1, block2, from_pos, to_pos), False)
move_table_to_block_end.add_effect(on(block1, block2), True)
move_table_to_block_end.add_effect(at(block1, to_pos), True)
move_table_to_block_end.add_effect(clear(block1), True)
move_table_to_block_end.add_effect(available(agent), True)

problem.add_action(move_table_to_block_end)

# ACTION 5: move_onblock_to_table_start
move_onblock_to_table_start = InstantaneousAction('move_onblock_to_table_start', 
                                                 agent=Agent, 
                                                 block1=Block, 
                                                 block2=Block,
                                                 from_pos=Pos, 
                                                 to_pos=Pos)
agent = move_onblock_to_table_start.parameter('agent')
block1 = move_onblock_to_table_start.parameter('block1')
block2 = move_onblock_to_table_start.parameter('block2')
from_pos = move_onblock_to_table_start.parameter('from_pos')
to_pos = move_onblock_to_table_start.parameter('to_pos')

# Add positive preconditions
move_onblock_to_table_start.add_precondition(available(agent))
move_onblock_to_table_start.add_precondition(on(block1, block2))  # Block1 is on Block2
move_onblock_to_table_start.add_precondition(at(block1, from_pos))
move_onblock_to_table_start.add_precondition(at(block2, from_pos))
move_onblock_to_table_start.add_precondition(clear(block1))
move_onblock_to_table_start.add_precondition(Not(Equals(block1, block2)))
move_onblock_to_table_start.add_precondition(Not(ontable(block1)))
move_onblock_to_table_start.add_precondition(empty(to_pos))  # NEW: Destination must be empty

# No block is on block1
any_block = Variable("any_block", Block)
move_onblock_to_table_start.add_precondition(Not(Exists([any_block], on(any_block, block1))))  # CHANGED

# Block1 is not being moved already
move_onblock_to_table_start.add_precondition(Not(Exists([any_pos, any_pos], moving_table_to_table(agent, block1, any_pos, any_pos))))  # CHANGED
move_onblock_to_table_start.add_precondition(Not(Exists([any_block, any_pos, any_pos], moving_table_to_block(agent, block1, any_block, any_pos, any_pos))))  # CHANGED
move_onblock_to_table_start.add_precondition(Not(Exists([any_pos, any_pos], moving_onblock_to_table(agent, block1, any_pos, any_pos))))  # CHANGED
move_onblock_to_table_start.add_precondition(Not(Exists([any_block, any_pos, any_pos], moving_onblock_to_block(agent, block1, any_block, any_pos, any_pos))))  # CHANGED

# Add effects
move_onblock_to_table_start.add_effect(available(agent), False)
move_onblock_to_table_start.add_effect(clear(block1), False)
move_onblock_to_table_start.add_effect(on(block1, block2), False)
move_onblock_to_table_start.add_effect(at(block1, from_pos), False)
move_onblock_to_table_start.add_effect(moving_onblock_to_table(agent, block1, from_pos, to_pos), True)
move_onblock_to_table_start.add_effect(clear(block2), True)

problem.add_action(move_onblock_to_table_start)

# ACTION 6: move_onblock_to_table_end
move_onblock_to_table_end = InstantaneousAction('move_onblock_to_table_end', 
                                               agent=Agent, 
                                               block1=Block, 
                                               from_pos=Pos, 
                                               to_pos=Pos)
agent = move_onblock_to_table_end.parameter('agent')
block1 = move_onblock_to_table_end.parameter('block1')
from_pos = move_onblock_to_table_end.parameter('from_pos')
to_pos = move_onblock_to_table_end.parameter('to_pos')

# Add positive preconditions
move_onblock_to_table_end.add_precondition(moving_onblock_to_table(agent, block1, from_pos, to_pos))
move_onblock_to_table_end.add_precondition(empty(to_pos))  # NEW: Destination must be empty

# Add effects
move_onblock_to_table_end.add_effect(moving_onblock_to_table(agent, block1, from_pos, to_pos), False)
move_onblock_to_table_end.add_effect(ontable(block1), True)
move_onblock_to_table_end.add_effect(at(block1, to_pos), True)
move_onblock_to_table_end.add_effect(clear(block1), True)
move_onblock_to_table_end.add_effect(available(agent), True)
move_onblock_to_table_end.add_effect(empty(to_pos), False)  # NEW: to_pos is no longer empty

problem.add_action(move_onblock_to_table_end)

# ACTION 7: move_onblock_to_block_start
move_onblock_to_block_start = InstantaneousAction('move_onblock_to_block_start', 
                                                 agent=Agent, 
                                                 block1=Block, 
                                                 block2=Block, 
                                                 block3=Block,  # The block that block1 is currently on
                                                 from_pos=Pos, 
                                                 to_pos=Pos)
agent = move_onblock_to_block_start.parameter('agent')
block1 = move_onblock_to_block_start.parameter('block1')
block2 = move_onblock_to_block_start.parameter('block2')
block3 = move_onblock_to_block_start.parameter('block3')
from_pos = move_onblock_to_block_start.parameter('from_pos')
to_pos = move_onblock_to_block_start.parameter('to_pos')

# Add positive preconditions
move_onblock_to_block_start.add_precondition(available(agent))
move_onblock_to_block_start.add_precondition(on(block1, block3))  # Block1 is on Block3
move_onblock_to_block_start.add_precondition(at(block1, from_pos))
move_onblock_to_block_start.add_precondition(at(block3, from_pos))
move_onblock_to_block_start.add_precondition(at(block2, to_pos))
move_onblock_to_block_start.add_precondition(clear(block2))
move_onblock_to_block_start.add_precondition(clear(block1))
move_onblock_to_block_start.add_precondition(Not(Equals(block1, block2)))
move_onblock_to_block_start.add_precondition(Not(Equals(block1, block3)))
move_onblock_to_block_start.add_precondition(Not(Equals(block2, block3)))
move_onblock_to_block_start.add_precondition(Not(ontable(block1)))

# No block is on block1
move_onblock_to_block_start.add_precondition(Not(Exists([any_block], on(any_block, block1))))  # CHANGED

# Block1 is not being moved already
move_onblock_to_block_start.add_precondition(Not(Exists([any_pos, any_pos], moving_table_to_table(agent, block1, any_pos, any_pos))))  # CHANGED
move_onblock_to_block_start.add_precondition(Not(Exists([any_block, any_pos, any_pos], moving_table_to_block(agent, block1, any_block, any_pos, any_pos))))  # CHANGED
move_onblock_to_block_start.add_precondition(Not(Exists([any_pos, any_pos], moving_onblock_to_table(agent, block1, any_pos, any_pos))))  # CHANGED
move_onblock_to_block_start.add_precondition(Not(Exists([any_block, any_pos, any_pos], moving_onblock_to_block(agent, block1, any_block, any_pos, any_pos))))  # CHANGED

# Add effects
move_onblock_to_block_start.add_effect(available(agent), False)
move_onblock_to_block_start.add_effect(clear(block1), False)
move_onblock_to_block_start.add_effect(on(block1, block3), False)
move_onblock_to_block_start.add_effect(at(block1, from_pos), False)
move_onblock_to_block_start.add_effect(moving_onblock_to_block(agent, block1, block2, from_pos, to_pos), True)
move_onblock_to_block_start.add_effect(clear(block3), True)

problem.add_action(move_onblock_to_block_start)

# ACTION 8: move_onblock_to_block_end
move_onblock_to_block_end = InstantaneousAction('move_onblock_to_block_end', 
                                               agent=Agent, 
                                               block1=Block, 
                                               block2=Block, 
                                               from_pos=Pos, 
                                               to_pos=Pos)
agent = move_onblock_to_block_end.parameter('agent')
block1 = move_onblock_to_block_end.parameter('block1')
block2 = move_onblock_to_block_end.parameter('block2')
from_pos = move_onblock_to_block_end.parameter('from_pos')
to_pos = move_onblock_to_block_end.parameter('to_pos')

# Add positive preconditions
move_onblock_to_block_end.add_precondition(moving_onblock_to_block(agent, block1, block2, from_pos, to_pos))
move_onblock_to_block_end.add_precondition(clear(block2))

# Add effects
move_onblock_to_block_end.add_effect(clear(block2), False)
move_onblock_to_block_end.add_effect(moving_onblock_to_block(agent, block1, block2, from_pos, to_pos), False)
move_onblock_to_block_end.add_effect(on(block1, block2), True)
move_onblock_to_block_end.add_effect(at(block1, to_pos), True)
move_onblock_to_block_end.add_effect(clear(block1), True)
move_onblock_to_block_end.add_effect(available(agent), True)

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
for agent in agents:
    problem.set_initial_value(available(agent), True)

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

# Set empty/non-empty goals for positions
problem.add_goal(Not(empty(pos_dict[(1,1)])))  # NEW: Position (1,1) is not empty
problem.add_goal(Not(empty(pos_dict[(2,2)])))  # NEW: Position (2,2) is not empty
problem.add_goal(Not(empty(pos_dict[(3,3)])))  # NEW: Position (3,3) is not empty
problem.add_goal(Not(empty(pos_dict[(10,10)])))  # NEW: Position (10,10) is not empty

for agent in agents:
    problem.add_goal(available(agent))

print(f"\n======== Total TIme to add goals: {time.time() - goal_timer:.4f} seconds ========")

def export_to_pddl():
    """Export the problem to PDDL files and print the contents."""
    function_start_time = time.time()
    print("\nSTART PDDL Exporting...")
    writer = PDDLWriter(problem)
    
    # Write to files
    domain_filename = "blocks_domain.pddl"
    problem_filename = "blocks_problem.pddl"
    
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
solve_problem()

print(f"\nTotal execution time: {time.time() - start_time:.4f} seconds")