import unified_planning as up
import unified_planning.model.fluent
from unified_planning.shortcuts import *


#   ------------    USER TYPES     -----------
#   - built-in types: bool, real and intergers types 
#   - we can also define new ones by using UserType('name_of_type')
Location = UserType('Location')


#   ------------    FLUENTS     -----------
# Fluents --> basic variables of a planning problem --> changes over time --> can have various types but now we'll use boolean
#   - example: a boolean fluent `connected` that takes two locations as parameters
# define a Fluent:
robot_at = Fluent('robot_at', BoolType(), l=Location)    # robot_at(l) is true if roboti is in location l 
connected = Fluent('connected', BoolType(), l_from=Location, l_to=Location)
robot_occupied_at = Fluent("occupied", BoolType(), l=Location)


#   ------------    ACTIONS     -----------     (InstantaneousActions)
#   - lets create `move` --> two parameters Location (l_from, l_to). The action move(a,b) can be applied only if robot_at(a) and if connected(a,b)
#   - the effect will be robot_at(b) and no longer robot_at(a)
#   - Preconditions and Effects added by
#       - add_precondition
#       - add_effect    -->     specify if condition is now False or True
move = InstantaneousAction('move', l_from=Location, l_to=Location)
#   why isn't the following done automatically??
l_from = move.parameter('l_from')
l_to = move.parameter('l_to')

move.add_precondition(robot_at(l_from))
move.add_precondition(connected(l_from, l_to))
move.add_effect(robot_at(l_from), False)
move.add_effect(robot_at(l_to), True)


#   ------------    PROBLEM     -----------
#   Problem is the class that represents the planning problem
#   - add FLUENTS and ACTIONS to the problem
#   - Note: entities are not bound to one problem --> can create multiple problems using the same actions and fluents 
problem = Problem('robot')
#   - lets set all the 'robot_at` and `connected` FLUENTS False 
problem.add_fluent(robot_at, default_initial_value=False)
problem.add_fluent(connected, default_initial_value=False)
problem.add_fluent(robot_occupied_at, default_initial_value=False)
problem.add_action(move)

#   ------------    set of Objects
#   - it is possible to create multiple instances with one line 
NLOC = 10 # number of lcoations = 10
locations = [Object('l%s' % i, Location) for i in range(NLOC)]  # --> we create NLOC (set to 10) locations named l0 to l9
problem.add_objects(locations)

#   ------------    Initial State
#   - everything was set to False --> only True ones specified
problem.set_initial_value(robot_at(locations[0]), True)
for i in range(NLOC - 1):
    problem.set_initial_value(connected(locations[i], locations[i+1]), True)

#   ------------    Goal
problem.add_goal(robot_at(locations[-1]))


#   ------------    SOLVING PLANNING PROBLEMS     ------------
#   - select a planning engine by name and use it to solve the problem
#       - Download planning engines: 
#           - ONE --> pip install unified-planning[NAME]
#           - ALL --> pip install unified-planning[engines]

#   Unified_planning can automatically select among available planners 
def planning(engine_name):
    try:
        # Specifying the planner explicitly by name
        print("SPECIFIED ENGINE ---------")
        with OneshotPlanner(name=engine_name) as planner:
            result = planner.solve(problem)
            if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                print("%s returned: %s" % (engine_name, result.plan))
            else:
                print("No plan found with %s\n" % engine_name)
    except Exception as e:
        print(f"Failed using %s due to: {e}\n" % engine_name)
        print("AUTO ENGINE ---------")
        # Attempt to solve with an automatic solver based on the problem kind
        try:
            with OneshotPlanner(problem_kind=problem.kind) as planner:
                result = planner.solve(problem)
                if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                    print("%s returned: %s" % (planner.name, result.plan))
                else:
                    print("No plan found with automatic solver.\n")
        except Exception as e:
            print(f"Automatic solver failed due to: {e}")


#   ------------    PARALLEL PLANNING     ------------
""" def parallel_planning():
    with OneshotPlanner(names=['tamer', 'tamer', 'pyperplan'],
                        params=[{'heuristic': 'hadd'}, {'heuristic': 'hmax'}, {}]) as planner:
        plan = planner.solve(problem).plan
        print("%s returned: %s" % (planner.name, plan)) """


if __name__ == "__main__":
    import sys
    
    engine_name = "pyperplan"
    
    if len(sys.argv) > 1:
        engine_name = sys.argv[1]
    
    planning(engine_name)




#   ---------   Test with Objects and other things  ---------

Person = UserType('Person')

# For a specific person p, destination(p) would tell you which Location is that person's destination
#   - "destination" is the name of the fluent
#   - Location is the return type (meaning this fluent will return a Location)
#   - for any Person, you can determine their destination location
destination = Fluent("destination", Location, Person=Person)

# Create location objects
trieste = Object("Trieste", Location)
rome = Object("Rome", Location)
milan = Object("Milan", Location)

# Create person objects
gigi = Object("Gigi", Person)
mario = Object("Mario", Person)

# Add all objects to the problem
problem.add_objects([trieste, rome, milan, gigi, mario])

# Add the destination fluent to the problem
problem.add_fluent(destination)

# Set initial values for destinations
problem.set_initial_value(destination(gigi), trieste)
problem.set_initial_value(destination(mario), rome)
