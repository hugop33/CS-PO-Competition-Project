# Projet de recherche de plan avec l'algorithme A* en PDDL

Ce projet consiste en l'implémentation de l'algorithme A* pour la recherche de plan dans un environnement défini en PDDL (Planning Domain Definition Language). Le but est de trouver une séquence d'actions qui mène d'un état initial à un état objectif en utilisant le domaine et le problème fournis.

## Fichiers

- `main.py` : Fichier principal qui exécute la recherche de plan et vérifie la validité du plan trouvé.
- `a_star.py` : Fichier contenant l'implémentation de l'algorithme A* pour la recherche de plan.

## Dépendances

- `pddl` : Bibliothèque pour parser les fichiers PDDL.

## Utilisation

1. Installez les dépendances nécessaires :

```
pip install -r requirements.txt
```

2. Exécutez le fichier `main.py` avec les arguments `--domain` et `--problem` :

```
python main.py --domain data/taquin_domain.pddl --problem data/taquin-size2x2-conf_0.pddl
```

Le programme affichera le nombre d'actions dans le plan trouvé, le temps d'exécution et si le plan est valide ou non.

## Fonctions

### Dans `main.py` :

- `valid_plan(plan)` : Vérifie la validité du plan en appliquant chaque action du plan à l'état initial et en vérifiant si l'état résultant est l'état objectif. Retourne `True` si le plan est valide, `False` sinon.

### Dans `a_star.py` :

- `astar_search(domain_file, problem_file)` : Implémente l'algorithme A* pour trouver une séquence d'actions qui mène d'un état initial à un état objectif. Retourne le plan trouvé sous forme de liste d'actions.
- `modified_predicates(domain)` : Retourne une liste de noms de prédicats qui sont modifiés par les actions du domaine.
- `is_possible_actions(dict_action, effects_name=modified_predicates(domain))` : Vérifie si une action est possible en fonction des préconditions et des effets des actions du domaine. Retourne `True` si l'action est possible, `False` sinon.
- `generate_klist(variables, k)` : Retourne une liste de toutes les permutations possibles de `k` variables.
- `all_actions(domain, problem)` : Retourne une liste de toutes les actions possibles en fonction du domaine et du problème.
- `applicable_actions(state, actions)` : Retourne une liste de toutes les actions applicables à un état donné.
- `apply_action(state, action)` : Applique une action à un état et retourne le nouvel état résultant.
- `relaxed_graphplan_heuristic(state, goal_state)` : Calcule l'heuristique de coût pour un état donné en utilisant l'algorithme de Graphplan relaxé (somme des actions pour satisfaire les sous-but).
- `reconstruct_path(came_from, start, goal)` : Reconstruit le chemin à partir d'un nœud objectif jusqu'au nœud de départ en utilisant le dictionnaire `came_from`.

## Résultats sur le taquin
| Config | Nombre d'actions dans le plan | Temps d'exécution (secondes) | Plan valide |
| --- | --- | --- | --- |
| taquin-size2x2-conf_0.pddl | 4 | 0.08 | Oui |
| taquin-size3x3-conf_0.pddl | 28 | 38.47 | Oui |
| taquin-size3x3-conf_1.pddl | 22 | 30.56 | Oui |
| taquin-size3x3-conf_2.pddl |  |  |  |
| taquin-size3x3-conf_3.pddl |  |  |  |
| taquin-size3x3-conf_4.pddl |  |  |  |
| taquin-size3x3-conf_5.pddl |  |  |  |
| taquin-size3x3-conf_6.pddl | 22 | 72.37 | Oui |
| taquin-size3x3-conf_7.pddl |  |  |  |
| taquin-size3x3-conf_8.pddl |  |  |  |
| taquin-size3x3-conf_9.pddl |  |  |  |
