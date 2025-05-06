(define (domain blocks-domain)
  (:requirements :strips :typing :negative-preconditions :equality :existential-preconditions)
  (:types
    block location agent
  )
  (:predicates
    (ontable ?b - block)
    (on ?b1 - block ?b2 - block)
    (at_ ?b - block ?l - location)
    (clear ?b - block)
    (available ?a - agent)
    (moving_table_to_table ?a - agent ?b - block ?l1 - location ?l2 - location)
    (moving_table_to_block ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    (moving_onblock_to_table ?a - agent ?b - block ?l1 - location ?l2 - location)
    (moving_onblock_to_block ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
  )
  (:action move_table_to_table_start
    :parameters ( ?a - agent ?b - block ?l1 - location ?l2 - location)
    :precondition (and (ontable ?b) (at_ ?b ?l1) (available ?a) (clear ?b) (not (exists
          (?block2 - block)
          (at_ ?block2 ?l2))) (not (exists
          (?block2 - block)
          (on ?b ?block2))) (not (exists
          (?other_agent - agent ?other_l2 - location ?other_l1 - location)
          (moving_table_to_table ?other_agent ?b ?other_l1 ?other_l2))) (not (exists
          (?other_agent - agent ?other_b - block ?other_l2 - location ?other_l1 - location)
          (moving_table_to_block ?other_agent ?b ?other_b ?other_l1 ?other_l2))))
    :effect (and (not (available ?a)) (not (clear ?b)) (not (ontable ?b)) (not (at_ ?b ?l1)) (moving_table_to_table ?a ?b ?l1 ?l2))
  )
  (:action move_table_to_table_end
    :parameters ( ?a - agent ?b - block ?l1 - location ?l2 - location)
    :precondition (and (moving_table_to_table ?a ?b ?l1 ?l2) (not (exists
          (?other_block - block)
          (at_ ?other_block ?l2))))
    :effect (and (not (moving_table_to_table ?a ?b ?l1 ?l2)) (ontable ?b) (at_ ?b ?l2) (clear ?b) (available ?a))
  )
  (:action move_table_to_block_start
    :parameters ( ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and (available ?a) (ontable ?b1) (at_ ?b1 ?l1) (at_ ?b2 ?l2) (clear ?b2) (clear ?b1) (not (= ?b1 ?b2)) (not (exists
          (?other_block - block)
          (on ?other_block ?b1))) (not (exists
          (?other_block - block)
          (on ?b1 ?other_block))) (not (exists
          (?other_agent - agent ?other_l2 - location ?other_l1 - location)
          (moving_table_to_table ?other_agent ?b1 ?other_l1 ?other_l2))) (not (exists
          (?other_b2 - block ?other_agent - agent ?other_l2 - location ?other_l1 - location)
          (moving_table_to_block ?other_agent ?b1 ?other_b2 ?other_l1 ?other_l2))))
    :effect (and (not (available ?a)) (not (clear ?b1)) (not (ontable ?b1)) (not (at_ ?b1 ?l1)) (moving_table_to_block ?a ?b1 ?b2 ?l1 ?l2))
  )
  (:action move_table_to_block_end
    :parameters ( ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and (moving_table_to_block ?a ?b1 ?b2 ?l1 ?l2) (clear ?b2))
    :effect (and (not (clear ?b2)) (not (moving_table_to_block ?a ?b1 ?b2 ?l1 ?l2)) (on ?b1 ?b2) (at_ ?b1 ?l2) (clear ?b1) (available ?a))
  )
  (:action move_onblock_to_table_start
    :parameters ( ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and (available ?a) (on ?b1 ?b2) (at_ ?b1 ?l1) (at_ ?b2 ?l1) (clear ?b1) (not (= ?b1 ?b2)) (not (ontable ?b1)) (not (exists
          (?other_a - agent ?other_l2 - location ?other_l1 - location)
          (moving_onblock_to_table ?other_a ?b1 ?other_l1 ?other_l2))) (not (exists
          (?other_b - block)
          (on ?other_b ?b1))) (not (exists
          (?other_b - block)
          (at_ ?other_b ?l2))))
    :effect (and (not (available ?a)) (not (clear ?b1)) (not (on ?b1 ?b2)) (not (at_ ?b1 ?l1)) (clear ?b2) (moving_onblock_to_table ?a ?b1 ?l1 ?l2))
  )
  (:action move_onblock_to_table_end
    :parameters ( ?a - agent ?b1 - block ?l1 - location ?l2 - location)
    :precondition (and (moving_onblock_to_table ?a ?b1 ?l1 ?l2) (not (exists
          (?other_block - block)
          (at_ ?other_block ?l2))))
    :effect (and (not (moving_onblock_to_table ?a ?b1 ?l1 ?l2)) (ontable ?b1) (at_ ?b1 ?l2) (clear ?b1) (available ?a))
  )
  (:action move_onblock_to_block_start
    :parameters ( ?a - agent ?b1 - block ?b2 - block ?b3 - block ?l1 - location ?l2 - location)
    :precondition (and (available ?a) (on ?b1 ?b3) (at_ ?b1 ?l1) (at_ ?b2 ?l2) (clear ?b2) (clear ?b1) (not (ontable ?b1)) (not (= ?b1 ?b2)) (not (= ?b2 ?b3)) (not (exists
          (?other_a - agent ?other_b - block ?other_l2 - location ?other_l1 - location)
          (moving_onblock_to_block ?other_a ?b1 ?other_b ?other_l1 ?other_l2))) (not (exists
          (?other_b - block)
          (on ?other_b ?b1))))
    :effect (and (not (available ?a)) (not (clear ?b1)) (not (on ?b1 ?b3)) (not (at_ ?b1 ?l1)) (moving_onblock_to_block ?a ?b1 ?b2 ?l1 ?l2) (clear ?b3))
  )
  (:action move_onblock_to_block_end
    :parameters ( ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
    :precondition (and (moving_onblock_to_block ?a ?b1 ?b2 ?l1 ?l2) (clear ?b2))
    :effect (and (not (clear ?b2)) (not (moving_onblock_to_block ?a ?b1 ?b2 ?l1 ?l2)) (on ?b1 ?b2) (at_ ?b1 ?l2) (clear ?b1) (available ?a))
  )
)