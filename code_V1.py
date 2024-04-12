import copy
import heapq
from collections import deque
from itertools import product
from pddl.parser.domain import DomainParser
from pddl.parser.problem import ProblemParser
import pddl

class Pddl:
    def __init__(self, domain_file, problem_file):
        self.domain = DomainParser()(open(domain_file).read())
        self.problem = ProblemParser()(open(problem_file).read())
        self.init_state = copy.deepcopy(list(self.problem.init))
        self.goal_state = copy.deepcopy(list(self.problem.goal.__getstate__()['_operands']))

class ActionGenerator:
    @staticmethod
    def generate_klist(variables, k):
        return list(product(variables, repeat=k))

    @staticmethod
    def all_actions(domain, problem):
        actions = []
        for a in range(len(domain.actions)):
            action = copy.deepcopy(list(domain.actions)[a])
            possibility = ActionGenerator.generate_klist(copy.deepcopy(list(problem.objects)), len(list(action.parameters)))
            for klist in possibility:
                if len(set(klist)) == len(klist):
                    dict_action = ActionGenerator.action_dict(action, klist)
                    actions.append(dict_action) 
        return actions

    @staticmethod
    def action_dict(action, klist):
        dict_action = {'name': action.name.__str__() + '(' + ', '.join([v.__str__() for v in klist]) + ')'}
        dict_var = dict(zip(action.parameters, klist))
        dict_action['preconditions'], dict_action['positive effects'], dict_action['negative effects'] = [], [], []
        # Traite les préconditions
        for p in action.precondition.operands:
            terms = tuple([dict_var[v] for v in p.__getstate__()['_terms']])
            dict_action['preconditions'].append(terms)
        # Traite les effets
        for e in action.effect.operands:
            # Vérifie si l'effet est de type Not (négatif) ou non
            if isinstance(e, pddl.logic.base.Not):
                terms = tuple([dict_var[v] for v in e.__getstate__()['_arg'].__getstate__()['_terms']])
                dict_action['negative effects'].append(terms)
            else:
                terms = tuple([dict_var[v] for v in e.__getstate__()['_terms']])
                dict_action['positive effects'].append(terms)
        return dict_action


class AStarSearch:
    def __init__(self, init_state, goal_state, actions):
        self.init_state = tuple(init_state)
        self.goal_state = tuple(goal_state)
        self.actions = actions
        self.path_actions = self.astar_search()

    def applicable_actions(self, state):
        applicable = []
        for action in self.actions:
            if all(pre in state for pre in action['preconditions']):
                applicable.append(action)
        return applicable

    def apply_action(self, state, action):
        new_state = set(state)
        new_state.update(action['positive effects'])
        new_state.difference_update(action['negative effects'])
        return tuple(new_state)

    def astar_search(self):
        open_list = []
        heapq.heappush(open_list, (0, self.init_state))
        came_from = {self.init_state: None}
        cost_so_far = {self.init_state: 0}
        while open_list:
            _, current = heapq.heappop(open_list)
            if self.goal_state == current:
                return self.reconstruct_path(came_from)
            for action in self.applicable_actions(current):
                new_state = self.apply_action(current, action)
                new_cost = cost_so_far[current] + 1
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    priority = new_cost
                    heapq.heappush(open_list, (priority, new_state))
                    came_from[new_state] = (current, action)
        return None

    def reconstruct_path(self, came_from):
        current = self.goal_state
        path = []
        while current != self.init_state:
            current, action = came_from[current]
            path.append(action)
        path.reverse()
        return path

# Exemple d'utilisation
pddl_parser = Pddl("data/domain.pddl", "data/problem.pddl")
actions_generator = ActionGenerator()
all_actions = actions_generator.all_actions(pddl_parser.domain, pddl_parser.problem)
astar = AStarSearch(pddl_parser.init_state, pddl_parser.goal_state, all_actions)

print("Plan trouvé :", [action['name'] for action in astar.path_actions])
