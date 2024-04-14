from pddl.parser.domain import DomainParser
from pddl.parser.problem import ProblemParser
import pddl
from itertools import product, permutations
import copy
import heapq
import time
        
def astar_search(domain_file, problem_file):
    with open(domain_file, 'r') as f:
        domain_str = f.read()

    with open(problem_file, 'r') as f:
        problem_str = f.read()

    domain = DomainParser()(domain_str)
    problem = ProblemParser()(problem_str)

    init_state = copy.deepcopy(list(problem.init))
    goal_state = copy.deepcopy(list(problem.goal.__getstate__()['_operands']))

    def modified_predicates(domain):
        effects_name = []
        for action in domain.actions:
            # Vérifie si l'effet contient des opérandes et les traite en conséquence
            if hasattr(action.effect, 'operands'):
                effects = action.effect.operands
            else:
                effects = [action.effect]  # Traite l'effet comme un seul élément s'il n'est pas dans un 'and'

            for effect in effects:
                if isinstance(effect, pddl.logic.predicates.Predicate):
                    effects_name.append(effect.name)
                elif isinstance(effect, pddl.logic.base.Not) and isinstance(effect.argument, pddl.logic.predicates.Predicate):
                    effects_name.append(effect.argument.name)
        return list(set(effects_name))


    def is_possible_actions(dict_action, effects_name=modified_predicates(domain)):
        for precondition in dict_action['preconditions']:
            # Extraire le nom en fonction du type de précondition
            if isinstance(precondition, pddl.logic.predicates.Predicate):
                name = precondition.name
            elif isinstance(precondition, pddl.logic.base.Not) and isinstance(precondition.argument, pddl.logic.predicates.Predicate):
                name = precondition.argument.name

            # Vérifier si le nom de la précondition est dans les effets des actions
            if name not in effects_name:  # Si le nom n'est pas dans les effets, donc il ne sera jamais modifié
                if precondition not in init_state:  # Si la précondition n'est pas dans l'état initial, donc l'action n'est pas possible
                    return False
        return True

    def generate_klist(variables, k):
        return list(permutations(variables, k))

    def all_actions(domain, problem):
        actions = []
        domain_actions_list = list(domain.actions)  # Convert to list once to avoid repeated conversions
        dict_possibility = {}
        for action in domain_actions_list:

            action_copy = copy.deepcopy(action)
            # Optimization: Generate possibilities once and use len(action_copy.parameters) directly
            if len(action_copy.parameters) not in dict_possibility:
                dict_possibility[len(action_copy.parameters)] = generate_klist(copy.deepcopy(list(problem.objects)), len(action_copy.parameters))
            
            possiblity = dict_possibility[len(action_copy.parameters)]

            
            for klist in possiblity:
                dict_action = {'name': '', 'preconditions': [], 'positive effects': [], 'negative effects': []}
                
                # Construct action name
                dict_action['name'] = action_copy.name.__str__() + '(' + ', '.join(v.__str__() for v in klist) + ')'
                # print('"parameters"', list(action_copy.parameters)[0].__getstate__())   
                # print('"klist"', list(klist)[0].__getstate__())
                dict_var = dict(zip(action_copy.parameters, klist))

                if all(action_copy.parameters[i].__getstate__()['_type_tags'] == klist[i].__getstate__()['_type_tags'] for i in range(len(action_copy.parameters))):

                    # list(precondition._terms)[0].__getstate__()['_type_tags']


                    # Process preconditions
                    preconditions = copy.deepcopy(action_copy.precondition.operands) if hasattr(action_copy.precondition, 'operands') else [action_copy.precondition]
                    for precondition in preconditions:
                        if hasattr(precondition, '_terms'):
                            terms = tuple(dict_var.get(v, v) for v in precondition._terms)
                            precondition._terms = terms
                        dict_action['preconditions'].append(precondition)

                    # Process effects
                    effects = copy.deepcopy(action_copy.effect.operands) if hasattr(action_copy.effect, 'operands') else [action_copy.effect]
                    for effect in effects:
                        if isinstance(effect, pddl.logic.predicates.Predicate):
                            terms = tuple(dict_var.get(v, v) for v in effect._terms)
                            effect._terms = terms
                            dict_action['positive effects'].append(effect)
                        elif isinstance(effect, pddl.logic.base.Not):
                            terms = tuple(dict_var.get(v, v) for v in effect._arg._terms)
                            effect._arg._terms = terms
                            dict_action['negative effects'].append(effect)
                    
                    # Check if action is possible
                    if is_possible_actions(dict_action):
                        actions.append(dict_action) 
        return actions
    
    All_actions = all_actions(domain, problem)

    # print("Nombre d'actions possibles :",len(All_actions))

    # buffer_actions={}
    # def applicable_actions(state, actions): # return applicable actions for a state
    #     if tuple(state) not in buffer_actions:
    #         buffer_actions[tuple(state)]= [a for a in actions if all(p in state for p in a['preconditions'])]
    #     return buffer_actions[tuple(state)]
    def applicable_actions(state, actions): # return applicable actions for a state
        return [a for a in actions if all(p in state for p in a['preconditions'])]
   


    def apply_action(state, action): # return new state after applying an action
        new_state = list(copy.deepcopy(state))
        for e in action['positive effects']:
            new_state.append(e)
        for e in action['negative effects']:
            new_state.remove(e.__getstate__()['_arg'])
        return tuple(new_state)

    # print(apply_action(init_state, applicable_actions(init_state, All_actions)[0]))
        
    def relaxed_graphplan_heuristic(state, goal_state):
        # Initialisation de l'ensemble de tous les faits connus (états actuels, objectifs, et tous les effets possibles).
        all_facts = set(list(goal_state) + list(state))
        for action in All_actions:
            for effect in action['positive effects']:
                all_facts.add(effect)

        # Initialisation du dictionnaire des coûts des faits.
        fact_costs = {fact: float('inf') for fact in all_facts}
        for fact in state:
            fact_costs[fact] = 0  # Coût nul pour les faits dans l'état actuel.
        
        # Boucle jusqu'à stabilisation : pas de mise à jour des coûts.
        updated = True
        while updated:
            updated = False
            for action in All_actions:
                # Vérifier si toutes les préconditions sont satisfaites.
                if all(fact_costs.get(pre, float('inf')) < float('inf') for pre in action['preconditions']):
                    cost = max(fact_costs.get(pre, 0) for pre in action['preconditions']) + 1  # Coût de l'action.
                    for effect in action['positive effects']:
                        if fact_costs[effect] > cost:
                            fact_costs[effect] = cost
                            updated = True
        
        # Calculer et retourner la somme des coûts pour atteindre chaque fait de l'état objectif.
        heuristic_value = sum(fact_costs.get(goal, float('inf')) for goal in goal_state)
        return heuristic_value if heuristic_value < float('inf') else float('inf')


    def reconstruct_path(came_from, start, goal):
        current = goal
        plan = []

        while current != start:
            found = False  # Indicateur pour vérifier si l'état courant est trouvé dans les clés
            for key in came_from.keys():
                if set(current).issubset(set(key)):
                    prev_state, action = came_from[key]  # Récupère l'état précédent et l'action
                    plan.append(action)  # Ajoute le nom de l'action au plan
                    current = prev_state  # Met à jour l'état courant pour continuer à remonter
                    found = True  # Met à jour l'indicateur pour montrer que nous avons trouvé un match
                    break  # Sort de la boucle car nous avons trouvé l'état courant dans les clés

            if not found:  # Si après avoir vérifié toutes les clés, aucun match n'est trouvé
                return None  # Retourne None car un chemin complet ne peut pas être reconstruit

        plan.reverse()  # Inverse le plan pour qu'il commence par l'état initial
        return plan

    def astar_search(init_state, goal_state, actions):
        init_state_tuple = tuple(copy.deepcopy(init_state))
        goal_state_tuple = tuple(copy.deepcopy(goal_state))    
        open_list = []
        heapq.heappush(open_list, (relaxed_graphplan_heuristic(init_state_tuple, copy.deepcopy(goal_state)), 0, init_state_tuple))
        
        came_from = {}
        cost_so_far = {init_state_tuple: 0}

        iteration = 0  # Ajout pour suivre le nombre d'itérations
        while open_list:
            _, current_cost, current_state = heapq.heappop(open_list)
            iteration += 1

            if set(goal_state).issubset(set(current_state)):
                print("Objectif atteint !")
                return reconstruct_path(came_from, init_state_tuple, goal_state_tuple)
            
            for action in applicable_actions(list(current_state), actions):
                new_state = tuple(apply_action(list(current_state), action))
                if set(goal_state).issubset(set(new_state)):
                    print("Objectif atteint !")
                    came_from[new_state] = (current_state, action)
                    return reconstruct_path(came_from, init_state_tuple, goal_state_tuple)
                    
                new_cost = current_cost + 1  
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    h = relaxed_graphplan_heuristic(new_state, copy.deepcopy(goal_state))
                    priority = new_cost + h
                    heapq.heappush(open_list, (priority, new_cost, new_state))
                    came_from[new_state] = (current_state, action)
            
            if iteration > 100000:  # Condition de sortie pour éviter la boucle infinie pendant le débogage
                print("Arrêt")
                return None
                    
        print("Aucun chemin trouvé.")
        return None

    return astar_search(init_state, goal_state, All_actions)





