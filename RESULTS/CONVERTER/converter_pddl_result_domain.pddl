(define (domain extracted_domain-domain)
 (:requirements :strips :typing)
 (:types block mela agent location vegetale generic)
 (:predicates (clear ?b1 - block) (on ?b1 - block ?b2 - block) (morsa ?m1 - mela) (ontable ?b1 - block) (moving_table_to_block ?a1 - agent ?b2 - block ?b3 - block ?l4 - location ?l5 - location ?l6 - location ?l7 - location) (available ?a1 - agent) (intera ?m1 - mela) (cotta ?v1 - vegetale) (at_ ?b1 - block ?l2 - location ?l3 - location) (cruda ?v1 - vegetale))
 (:action move_table_to_block_start
  :parameters ( ?p0 - agent ?p1 - block ?p2 - block ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
  :precondition (and (available ?p0) (ontable ?p1) (clear ?p2) (clear ?p1)))
 (:action move_table_to_block_end
  :parameters ( ?p0 - agent ?p1_0 - generic ?p2_0 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic))
 (:action mangia_mela
  :parameters ( ?p0 - agent ?p1_1 - mela)
  :precondition (and (intera ?p1_1) (available ?p0)))
 (:action cuoci
  :parameters ( ?p0 - agent ?p1_2 - vegetale)
  :precondition (and (available ?p0) (cruda ?p1_2)))
)
