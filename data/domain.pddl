(define (domain hanoi)
    (:requirements :strips)
    (:predicates (clear ?x)  (on ?x ?y)  (smaller ?x ?y))
    (:action move
        :parameters (?x ?y ?z)
        :precondition (and (smaller ?x ?z) (on ?x ?y) (clear ?x) (clear ?z))
        :effect (and (clear ?y) (on ?x ?z) (not (on ?x ?y)) (not (clear ?z)))
    )
)