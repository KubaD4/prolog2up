(define (domain blocks-domain)
 (:requirements :strips :typing :negative-preconditions :existential-preconditions)
 (:types block location agent)
 (:predicates (at_ ?b1 - block ?l2 - location ?l3 - location) (clear ?b1 - block) (ontable ?b1 - block) (on ?b1 - block ?b2 - block) (morsa ?x1 - block) (available ?a - agent) (intera ?x1 - block) (moving_table_to_block ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location))
 (:action move_table_to_block_start
  :parameters ( ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
  :precondition (and (available ?a) (ontable ?b1) (not (exists (?other_b - block)
 (on ?other_b ?b1))) (not (exists (?other_b - block)
 (on ?b1 ?other_b))) (not (exists (?other_agent - agent ?other_block - block ?other_l1 - location ?other_l2 - location)
 (moving_table_to_block ?other_agent ?b1 ?other_block ?other_l1 ?other_l2)))))
 (:action move_table_to_block_end
  :parameters ( ?a - agent ?b1 - block ?b2 - block ?l1 - location ?l2 - location)
  :precondition (and (moving_table_to_block ?a ?b1 ?b2 ?l1 ?l2)))
)
