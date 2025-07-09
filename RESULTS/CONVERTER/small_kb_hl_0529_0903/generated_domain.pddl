(define (domain from_prolog-domain)
  (:requirements :strips :typing :negative-preconditions :existential-preconditions)
  (:types
    agent block pos mela vegetale
  )
  (:predicates
    (moving_table_to_block ?p0 - agent ?p1 - block ?p2 - block ?p3 - pos ?p4 - pos ?p5 - pos ?p6 - pos)
    (ontable ?p0_0 - block)
    (clear ?p0_0 - block)
    (on ?p0_0 - block ?p1 - block)
    (available ?p0 - agent)
    (intera ?p0_1 - mela)
    (at_ ?p0_0 - block ?p1_0 - pos ?p2_0 - pos)
    (morsa ?p0_1 - mela)
    (cruda ?p0_2 - vegetale)
    (cotta ?p0_2 - vegetale)
  )
  (:action move_table_to_block_start
    :parameters ( ?param1 - agent ?param2 - block ?param3 - block ?param4 - pos ?param5 - pos ?param6 - pos ?param7 - pos)
    :precondition (and (available ?param1) (ontable ?param2) (at_ ?param2 ?param4 ?param5) (at_ ?param3 ?param6 ?param7) (clear ?param3) (clear ?param2) (not (exists
          (?any_move_table_to_block_start_0 - block)
          (on ?any_move_table_to_block_start_0 ?param2))) (not (exists
          (?any_move_table_to_block_start_1 - block)
          (on ?param2 ?any_move_table_to_block_start_1))) (not (exists
          (?any_move_table_to_block_start_5 - pos ?any_move_table_to_block_start_6 - pos ?any_move_table_to_block_start_0_0 - agent ?any_move_table_to_block_start_4 - pos ?any_move_table_to_block_start_3 - pos ?any_move_table_to_block_start_2 - block)
          (moving_table_to_block ?any_move_table_to_block_start_0_0 ?param2 ?any_move_table_to_block_start_2 ?any_move_table_to_block_start_3 ?any_move_table_to_block_start_4 ?any_move_table_to_block_start_5 ?any_move_table_to_block_start_6))))
    :effect (and (not (available ?param1)) (not (clear ?param2)) (not (ontable ?param2)) (not (at_ ?param2 ?param4 ?param5)) (moving_table_to_block ?param1 ?param2 ?param3 ?param4 ?param5 ?param6 ?param7))
  )
  (:action move_table_to_block_end
    :parameters ( ?param1 - agent ?param2 - block ?param3 - block ?param4 - pos ?param5 - pos ?param6 - pos ?param7 - pos)
    :precondition (and (moving_table_to_block ?param1 ?param2 ?param3 ?param4 ?param5 ?param6 ?param7) (clear ?param3))
    :effect (and (not (clear ?param3)) (not (moving_table_to_block ?param1 ?param2 ?param3 ?param4 ?param5 ?param6 ?param7)) (on ?param2 ?param3) (at_ ?param2 ?param6 ?param7) (clear ?param2) (available ?param1))
  )
  (:action mangia_mela
    :parameters ( ?param1 - agent ?param2_0 - mela)
    :precondition (and (intera ?param2_0) (available ?param1))
    :effect (and (not (intera ?param2_0)) (not (available ?param1)) (morsa ?param2_0))
  )
  (:action cuoci
    :parameters ( ?param1 - agent ?param2_1 - vegetale)
    :precondition (and (available ?param1) (cruda ?param2_1))
    :effect (and (not (cruda ?param2_1)) (cotta ?param2_1))
  )
)