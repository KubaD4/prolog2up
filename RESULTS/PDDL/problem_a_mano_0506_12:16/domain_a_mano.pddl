(define (domain blocks-world)
  (:requirements :strips :negative-preconditions :typing :existential-preconditions)
  
  (:types
    agent block location - object
  )
  
  (:predicates
    (ontable ?b - block)                           ; block is on the table
    (on ?b1 - block ?b2 - block)                   ; block1 is on block2
    (at ?b - block ?l - location)                  ; block is at location
    (clear ?b - block)                             ; block has nothing on top
    (available ?a - agent)                         ; agent is available
    (empty ?l - location)                          ; location has no block
    
    (moving-onblock-to-table ?a - agent ?b - block ?l1 - location ?l2 - location)
    (moving-onblock-to-block ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    (moving-table-to-table ?a - agent ?b - block ?l1 - location ?l2 - location)
    (moving-table-to-block ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
  )

  (:action move-onblock-to-table-start
    :parameters (?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and
      (available ?a)
      (on ?b1 ?b2)
      (at ?b1 ?l1)
      (at ?b2 ?l1)
      (clear ?b1)
      (empty ?l2)

      (not (exists (?b - block) (moving-onblock-to-table ?a ?b ?l1 ?l2)))
      ;(not (exists (?b3 - block) (moving-onblock-to-block ?a ?b1 ?b3 ?l1 ?l2)))
      ;(not (exists (?b3 - block) (moving-table-to-table ?a ?b3 ?l1 ?l2)))
      ;(not (exists (?b3 - block ?b4 - block) (moving-table-to-block ?a ?b3 ?b4 ?l1 ?l2)))
    )
    :effect (and
      (not (available ?a))
      (not (clear ?b1))
      (not (on ?b1 ?b2))
      (not (at ?b1 ?l1))
      (clear ?b2)
      (moving-onblock-to-table ?a ?b1 ?l1 ?l2)
    )
  )
  
  (:action move-onblock-to-table-end
    :parameters (?a - agent ?b1 - block ?l1 - location ?l2 - location)
    :precondition (and
      (moving-onblock-to-table ?a ?b1 ?l1 ?l2)
      (empty ?l2)
    )
    :effect (and
      (not (moving-onblock-to-table ?a ?b1 ?l1 ?l2))
      (ontable ?b1)
      (at ?b1 ?l2)
      (clear ?b1)
      (available ?a)
      (not (empty ?l2))
    )
  )

  (:action move-onblock-to-block-start
    ; b3 -> blocco su cui poggia b1
    :parameters (?a - agent ?b1 - block ?b2 - block ?b3 - block ?l1 - location ?l2 - location)
    :precondition (and
      (available ?a)
      (on ?b1 ?b3)
      (at ?b1 ?l1)
      (at ?b2 ?l2)
      (clear ?b2)
      (clear ?b1)

      (not (exists (?b - block) (moving-onblock-to-table ?a ?b ?l1 ?l2)))
      (not (exists (?b4 - block) (moving-onblock-to-block ?a ?b1 ?b4 ?l1 ?l2)))
      (not (exists (?b4 - block) (moving-onblock-to-block ?a ?b4 ?b2 ?l1 ?l2)))
      (not (exists (?b4 - block) (moving-table-to-table ?a ?b4 ?l1 ?l2)))
      (not (exists (?b4 - block ?b5 - block) (moving-table-to-block ?a ?b4 ?b5 ?l1 ?l2)))
    )
    :effect (and
      (not (available ?a))
      (not (clear ?b1))
      (not (on ?b1 ?b3))
      (not (at ?b1 ?l1))
      (moving-onblock-to-block ?a ?b1 ?b2 ?l1 ?l2)
      (clear ?b3)
    )
  )
  
  (:action move-onblock-to-block-end
    :parameters (?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and
      (moving-onblock-to-block ?a ?b1 ?b2 ?l1 ?l2)
      (clear ?b2)
      (at ?b2 ?l2)
    )
    :effect (and
      (not (clear ?b2))
      (not (moving-onblock-to-block ?a ?b1 ?b2 ?l1 ?l2))
      (on ?b1 ?b2)
      (at ?b1 ?l2)
      (clear ?b1)
      (available ?a)
    )
  )

  (:action move-table-to-table-start
    :parameters (?a - agent ?b - block ?l1 - location ?l2 - location)
    :precondition (and 
      (ontable ?b)
      (at ?b ?l1) 
      (available ?a) 
      (clear ?b)
      (empty ?l2)

      (not (exists (?b2 - block) (moving-onblock-to-table ?a ?b2 ?l1 ?l2)))
      (not (exists (?b2 - block ?b3 - block) (moving-onblock-to-block ?a ?b2 ?b3 ?l1 ?l2)))
      (not (moving-table-to-table ?a ?b ?l1 ?l2))
      (not (exists (?b2 - block ?b3 - block) (moving-table-to-block ?a ?b2 ?b3 ?l1 ?l2)))
    )
    :effect (and 
      (not (available ?a))
      (not (clear ?b))
      (not (ontable ?b))
      (not (at ?b ?l1))
      (empty ?l1)
      (moving-table-to-table ?a ?b ?l1 ?l2)
    )
  )

  (:action move-table-to-table-end
    :parameters (?a - agent ?b - block ?l1 - location ?l2 - location)
    :precondition (and 
      (moving-table-to-table ?a ?b ?l1 ?l2)
      (empty ?l2)
    )
    :effect (and 
      (not (moving-table-to-table ?a ?b ?l1 ?l2))
      (ontable ?b)
      (at ?b ?l2)
      (not (empty ?l2))
      (clear ?b)
      (available ?a)
    )
  )

  (:action move-table-to-block-start
    :parameters (?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and 
      (available ?a)
      (ontable ?b1)
      (at ?b1 ?l1) 
      (at ?b2 ?l2)
      (clear ?b2) 
      (clear ?b1)

      (not (exists (?b3 - block) (moving-onblock-to-table ?a ?b3 ?l1 ?l2)))
      (not (exists (?b3 - block ?b4 - block) (moving-onblock-to-block ?a ?b3 ?b4 ?l1 ?l2)))
      (not (exists (?b3 - block) (moving-table-to-table ?a ?b3 ?l1 ?l2)))
      (not (moving-table-to-block ?a ?b1 ?b2 ?l1 ?l2))
      (not (exists (?b3 - block) (moving-table-to-block ?a ?b3 ?b2 ?l1 ?l2)))
    )
    :effect (and 
      (not (available ?a))
      (not (clear ?b1))
      (not (ontable ?b1))
      (not (at ?b1 ?l1))
      (empty ?l1)
      (moving-table-to-block ?a ?b1 ?b2 ?l1 ?l2)
    )
  )

  (:action move-table-to-block-end
    :parameters (?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and 
      (moving-table-to-block ?a ?b1 ?b2 ?l1 ?l2)
      (clear ?b2)
    )
    :effect (and 
      (not (clear ?b2))
      (not (moving-table-to-block ?a ?b1 ?b2 ?l1 ?l2))
      (on ?b1 ?b2)
      (at ?b1 ?l2)
      (clear ?b1)
      (available ?a)
    )
  )
)