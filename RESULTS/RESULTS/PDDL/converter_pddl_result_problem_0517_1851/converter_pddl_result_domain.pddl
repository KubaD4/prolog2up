(define (domain extracted_domain-domain)
  (:requirements :strips :typing)
  (:types
    generic agent block mela location vegetale
  )
  (:predicates
    (moving_table_to_block ?p0 - generic ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
    (available ?a1 - agent)
    (on ?b1 - block ?b2 - block)
    (clear ?b1 - block)
    (intera ?m1 - mela)
    (morsa ?m1 - mela)
    (ontable ?b1 - block)
    (at_ ?b - block ?l - location)
    (cotta ?v1 - vegetale)
    (cruda ?v1 - vegetale)
  )
  (:action move_table_to_block_start
    :parameters ( ?p0_0 - agent ?p1_0 - block ?p2_0 - block ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
    :precondition (and (available ?p0_0) (ontable ?p1_0) (clear ?p1_0) (clear ?p2_0))
    :effect (and (not (available ?p0_0)) (not (ontable ?p1_0)) (not (clear ?p1_0)))
  )
  (:action move_table_to_block_end
    :parameters ( ?p0_0 - agent ?p1 - generic ?p2 - generic ?p3 - generic ?p4 - generic ?p5 - generic ?p6 - generic)
    :effect (and (available ?p0_0))
  )
  (:action mangia_mela
    :parameters ( ?p0_0 - agent ?p1_1 - mela)
    :precondition (and (available ?p0_0) (intera ?p1_1))
    :effect (and (not (available ?p0_0)) (not (intera ?p1_1)) (morsa ?p1_1))
  )
  (:action cuoci
    :parameters ( ?p0_0 - agent ?p1_2 - vegetale)
    :precondition (and (available ?p0_0) (cruda ?p1_2))
    :effect (and (not (cruda ?p1_2)) (cotta ?p1_2))
  )
)