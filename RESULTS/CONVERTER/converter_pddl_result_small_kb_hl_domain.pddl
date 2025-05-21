(define (domain extracted_domain-domain)
 (:requirements :strips :typing)
 (:types generic block mela agent location vegetale)
 (:predicates (moving_table_to_block ?p0 - generic ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic) (clear ?b1 - block) (intera ?m1 - mela) (morsa ?m1 - mela) (ontable ?b1 - block) (available ?a1 - agent) (on ?b1 - block ?b2 - block) (at_ ?b - block ?l - location) (cruda ?v1 - vegetale) (cotta ?v1 - vegetale))
 (:action mangia_mela
  :parameters ( ?p0_0 - agent ?p1_0 - mela)
  :precondition (and (intera ?p1_0) (available ?p0_0)))
 (:action cuoci
  :parameters ( ?p0_0 - agent ?p1_1 - vegetale)
  :precondition (and (available ?p0_0) (cruda ?p1_1)))
)
