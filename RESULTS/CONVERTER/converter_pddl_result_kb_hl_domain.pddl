(define (domain extracted_domain-domain)
 (:requirements :strips :typing)
 (:types generic block agent location)
 (:predicates (moving_table_to_table ?p0 - generic ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic) (moving_onblock_to_table ?p0 - generic ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic) (moving_table_to_block ?p0 - generic ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic) (moving_onblock_to_block ?p0 - generic ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic) (clear ?b1 - block) (ontable ?b1 - block) (on ?b1 - block ?b2 - block) (available ?a1 - agent) (at_ ?b - block ?l - location))
 (:action move_table_to_table_start
  :parameters ( ?p0_0 - agent ?p1_0 - block ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic)
  :precondition (and (ontable ?p1_0) (available ?p0_0) (clear ?p1_0)))
 (:action move_table_to_table_end
  :parameters ( ?p0_0 - agent ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic))
 (:action move_table_to_block_start
  :parameters ( ?p0_0 - agent ?p1_0 - block ?p2_0 - block ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
  :precondition (and (available ?p0_0) (ontable ?p1_0) (clear ?p1_0) (clear ?p2_0))
  :effect (and (not (available ?p0_0)) (not (ontable ?p1_0)) (not (clear ?p1_0))))
 (:action move_table_to_block_end
  :parameters ( ?p0_0 - agent ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
  :effect (and (available ?p0_0)))
 (:action move_onblock_to_table_start
  :parameters ( ?p0_0 - agent ?p1_0 - block ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic)
  :precondition (and (available ?p0_0) (clear ?p1_0)))
 (:action move_onblock_to_table_end
  :parameters ( ?p0_0 - agent ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic))
 (:action move_onblock_to_block_start
  :parameters ( ?p0_0 - agent ?p1_0 - block ?p2_0 - block ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
  :precondition (and (available ?p0_0) (clear ?p2_0) (clear ?p1_0)))
 (:action move_onblock_to_block_end
  :parameters ( ?p0_0 - agent ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic))
)
