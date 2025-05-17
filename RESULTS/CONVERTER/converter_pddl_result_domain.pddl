(define (domain extracted_domain-domain)
 (:requirements :strips :typing)
 (:types mela block agent location vegetale generic)
 (:predicates (morsa ?m1 - mela) (ontable ?b1 - block) (moving_table_to_block ?a1 - agent ?b2 - block ?b3 - block ?l4 - location ?l5 - location ?l6 - location ?l7 - location) (available ?a1 - agent) (clear ?b1 - block) (on ?b1 - block ?b2 - block) (intera ?m1 - mela) (cotta ?v1 - vegetale) (at_ ?b1 - block ?l2 - location ?l3 - location) (cruda ?v1 - vegetale))
 (:action move_table_to_block_start
  :parameters ( ?p0_0 - agent ?p1_0 - block ?p2_0 - block ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
  :precondition (and (available ?p0_0) (ontable ?p1_0) (clear ?p1_0) (clear ?p2_0))
  :effect (and (not (available ?p0_0)) (not (ontable ?p1_0)) (not (clear ?p1_0))))
 (:action move_table_to_block_end
  :parameters ( ?p0_0 - agent ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
  :effect (and (available ?p0_0)))
 (:action mangia_mela
  :parameters ( ?p0_0 - agent ?p1_1 - mela)
  :precondition (and (available ?p0_0) (intera ?p1_1))
  :effect (and (not (available ?p0_0)) (not (intera ?p1_1)) (morsa ?p1_1)))
 (:action cuoci
  :parameters ( ?p0_0 - agent ?p1_2 - vegetale)
  :precondition (and (available ?p0_0) (cruda ?p1_2))
  :effect (and (not (cruda ?p1_2)) (cotta ?p1_2)))
)
