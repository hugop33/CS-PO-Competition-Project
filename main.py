import time
import argparse
from pddl.parser.domain import DomainParser
from pddl.parser.problem import ProblemParser
from a_star import astar_search

# Ajoutez un parseur d'arguments
parser = argparse.ArgumentParser()
parser.add_argument("--domain", help="Domain PDDL file")
parser.add_argument("--problem", help="Problem PDDL file")
args = parser.parse_args()

start_time = time.time()

# Utilisez les arguments passés en ligne de commande
DOMAIN = args.domain
PROBLEM = args.problem

plan = astar_search(DOMAIN, PROBLEM)

print("Nombre d'actions dans le plan :", len(plan))
print("Temps d'exécution : %s secondes" % (time.time() - start_time))

# Vérification de la validité du plan
import copy
def valid_plan(plan):

    def apply_action(state, action): # return new state after applying an action
        new_state = list(copy.deepcopy(state))
        for e in action['positive effects']:
            new_state.append(e)
        for e in action['negative effects']:
            new_state.remove(e.__getstate__()['_arg'])
        return tuple(new_state)

    problem = ProblemParser()(open(PROBLEM).read())
    state = list(problem.init)
    goal_state = list(problem.goal.__getstate__()['_operands'])

    try:
        for a in plan:
            print(a['name'])
            state = apply_action(state, a)
        return set(goal_state).issubset(set(state))
    except:
        return False

print("Plan valide :", valid_plan(plan))