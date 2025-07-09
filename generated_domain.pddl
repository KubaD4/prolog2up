(define (domain from_prolog-domain)
  (:requirements :strips :typing :negative-preconditions :existential-preconditions)
  (:types
    block pos agent
  )
  (:predicates
    (at_ ?p0 - block ?p1 - pos ?p2 - pos)
    (available ?p0_0 - agent)
    (moving_onblock_to_block ?p0_0 - agent ?p1_0 - block ?p2_0 - block ?p3 - pos ?p4 - pos ?p5 - pos ?p6 - pos)
    (clear ?p0 - block)
    (ontable ?p0 - block)
    (moving_table_to_table ?p0_0 - agent ?p1_0 - block ?p2 - pos ?p3 - pos ?p4 - pos ?p5 - pos)
    (moving_onblock_to_table ?p0_0 - agent ?p1_0 - block ?p2 - pos ?p3 - pos ?p4 - pos ?p5 - pos)
    (on ?p0 - block ?p1_0 - block)
    (moving_table_to_block ?p0_0 - agent ?p1_0 - block ?p2_0 - block ?p3 - pos ?p4 - pos ?p5 - pos ?p6 - pos)
  )
  (:action move_table_to_table_start
    :parameters ( ?param1 - agent ?param2 - block ?param3 - pos ?param4 - pos ?param5 - pos ?param6 - pos)
    :precondition (and (ontable ?param2) (at_ ?param2 ?param3 ?param4) (available ?param1) (clear ?param2) (not (exists
          (?any_move_table_to_table_start_0 - block)
          (at_ ?any_move_table_to_table_start_0 ?param5 ?param6))) (not (exists
          (?any_move_table_to_table_start_1 - block)
          (on ?param2 ?any_move_table_to_table_start_1))) (not (exists
          (?any_move_table_to_table_start_3 - pos ?any_move_table_to_table_start_2 - pos ?any_move_table_to_table_start_5 - pos ?any_move_table_to_table_start_4 - pos ?any_move_table_to_table_start_0_0 - agent)
          (moving_table_to_table ?any_move_table_to_table_start_0_0 ?param2 ?any_move_table_to_table_start_2 ?any_move_table_to_table_start_3 ?any_move_table_to_table_start_4 ?any_move_table_to_table_start_5))) (not (exists
          (?any_move_table_to_table_start_3 - pos ?any_move_table_to_table_start_2_0 - block ?any_move_table_to_table_start_6 - pos ?any_move_table_to_table_start_5 - pos ?any_move_table_to_table_start_4 - pos ?any_move_table_to_table_start_0_0 - agent)
          (moving_table_to_block ?any_move_table_to_table_start_0_0 ?param2 ?any_move_table_to_table_start_2_0 ?any_move_table_to_table_start_3 ?any_move_table_to_table_start_4 ?any_move_table_to_table_start_5 ?any_move_table_to_table_start_6))))
    :effect (and (not (available ?param1)) (not (clear ?param2)) (not (ontable ?param2)) (not (at_ ?param2 ?param3 ?param4)) (moving_table_to_table ?param1 ?param2 ?param3 ?param4 ?param5 ?param6))
  )
  (:action move_table_to_table_end
    :parameters ( ?param1 - agent ?param2 - block ?param3 - pos ?param4 - pos ?param5 - pos ?param6 - pos)
    :precondition (and (moving_table_to_table ?param1 ?param2 ?param3 ?param4 ?param5 ?param6) (not (exists
          (?any_move_table_to_table_end_0 - block)
          (at_ ?any_move_table_to_table_end_0 ?param5 ?param6))))
    :effect (and (not (moving_table_to_table ?param1 ?param2 ?param3 ?param4 ?param5 ?param6)) (ontable ?param2) (at_ ?param2 ?param5 ?param6) (clear ?param2) (available ?param1))
  )
  (:action move_table_to_block_start
    :parameters ( ?param1 - agent ?param2 - block ?param3_0 - block ?param4 - pos ?param5 - pos ?param6 - pos ?param7 - pos)
    :precondition (and (available ?param1) (ontable ?param2) (at_ ?param2 ?param4 ?param5) (at_ ?param3_0 ?param6 ?param7) (clear ?param3_0) (clear ?param2) (not (exists
          (?any_move_table_to_block_start_0 - block)
          (on ?any_move_table_to_block_start_0 ?param2))) (not (exists
          (?any_move_table_to_block_start_1 - block)
          (on ?param2 ?any_move_table_to_block_start_1))) (not (exists
          (?any_move_table_to_block_start_5 - pos ?any_move_table_to_block_start_3 - pos ?any_move_table_to_block_start_4 - pos ?any_move_table_to_block_start_0_0 - agent ?any_move_table_to_block_start_2 - pos)
          (moving_table_to_table ?any_move_table_to_block_start_0_0 ?param2 ?any_move_table_to_block_start_2 ?any_move_table_to_block_start_3 ?any_move_table_to_block_start_4 ?any_move_table_to_block_start_5))) (not (exists
          (?any_move_table_to_block_start_5 - pos ?any_move_table_to_block_start_3 - pos ?any_move_table_to_block_start_4 - pos ?any_move_table_to_block_start_0_0 - agent ?any_move_table_to_block_start_2_0 - block ?any_move_table_to_block_start_6 - pos)
          (moving_table_to_block ?any_move_table_to_block_start_0_0 ?param2 ?any_move_table_to_block_start_2_0 ?any_move_table_to_block_start_3 ?any_move_table_to_block_start_4 ?any_move_table_to_block_start_5 ?any_move_table_to_block_start_6))))
    :effect (and (not (available ?param1)) (not (clear ?param2)) (not (ontable ?param2)) (not (at_ ?param2 ?param4 ?param5)) (moving_table_to_block ?param1 ?param2 ?param3_0 ?param4 ?param5 ?param6 ?param7))
  )
  (:action move_table_to_block_end
    :parameters ( ?param1 - agent ?param2 - block ?param3_0 - block ?param4 - pos ?param5 - pos ?param6 - pos ?param7 - pos)
    :precondition (and (moving_table_to_block ?param1 ?param2 ?param3_0 ?param4 ?param5 ?param6 ?param7) (clear ?param3_0))
    :effect (and (not (clear ?param3_0)) (not (moving_table_to_block ?param1 ?param2 ?param3_0 ?param4 ?param5 ?param6 ?param7)) (on ?param2 ?param3_0) (at_ ?param2 ?param6 ?param7) (clear ?param2) (available ?param1))
  )
  (:action move_onblock_to_table_start
    :parameters ( ?param1 - agent ?param2 - block ?param3 - pos ?param4 - pos ?param5 - pos ?param6 - pos ?param7_0 - block)
    :precondition (and (available ?param1) (on ?param2 ?param7_0) (at_ ?param2 ?param3 ?param4) (at_ ?param7_0 ?param3 ?param4) (clear ?param2) (not (exists
          (?any_move_onblock_to_table_start_2 - pos ?any_move_onblock_to_table_start_0 - agent ?any_move_onblock_to_table_start_5 - pos ?any_move_onblock_to_table_start_4 - pos ?any_move_onblock_to_table_start_3 - pos)
          (moving_onblock_to_table ?any_move_onblock_to_table_start_0 ?param2 ?any_move_onblock_to_table_start_2 ?any_move_onblock_to_table_start_3 ?any_move_onblock_to_table_start_4 ?any_move_onblock_to_table_start_5))) (not (exists
          (?any_move_onblock_to_table_start_0_0 - block)
          (on ?any_move_onblock_to_table_start_0_0 ?param2))) (not (ontable ?param2)) (not (exists
          (?any_move_onblock_to_table_start_0_0 - block)
          (at_ ?any_move_onblock_to_table_start_0_0 ?param5 ?param6))))
    :effect (and (not (available ?param1)) (not (clear ?param2)) (not (on ?param2 ?param7_0)) (not (at_ ?param2 ?param3 ?param4)) (moving_onblock_to_table ?param1 ?param2 ?param3 ?param4 ?param5 ?param6) (clear ?param7_0))
  )
  (:action move_onblock_to_table_end
    :parameters ( ?param1 - agent ?param2 - block ?param3 - pos ?param4 - pos ?param5 - pos ?param6 - pos)
    :precondition (and (moving_onblock_to_table ?param1 ?param2 ?param3 ?param4 ?param5 ?param6) (not (exists
          (?any_move_onblock_to_table_end_0 - block)
          (at_ ?any_move_onblock_to_table_end_0 ?param5 ?param6))))
    :effect (and (not (moving_onblock_to_table ?param1 ?param2 ?param3 ?param4 ?param5 ?param6)) (ontable ?param2) (at_ ?param2 ?param5 ?param6) (clear ?param2) (available ?param1))
  )
  (:action move_onblock_to_block_start
    :parameters ( ?param1 - agent ?param2 - block ?param3_0 - block ?param4 - pos ?param5 - pos ?param6 - pos ?param7 - pos)
    :precondition (and (available ?param1) (on ?param2 ?param3_0) (at_ ?param2 ?param4 ?param5) (at_ ?param3_0 ?param6 ?param7) (clear ?param3_0) (clear ?param2) (not (exists
          (?any_move_onblock_to_block_start_2 - block ?any_move_onblock_to_block_start_6 - pos ?any_move_onblock_to_block_start_3 - pos ?any_move_onblock_to_block_start_4 - pos ?any_move_onblock_to_block_start_5 - pos ?any_move_onblock_to_block_start_0 - agent)
          (moving_onblock_to_block ?any_move_onblock_to_block_start_0 ?param2 ?any_move_onblock_to_block_start_2 ?any_move_onblock_to_block_start_3 ?any_move_onblock_to_block_start_4 ?any_move_onblock_to_block_start_5 ?any_move_onblock_to_block_start_6))) (not (exists
          (?any_move_onblock_to_block_start_0_0 - block)
          (on ?any_move_onblock_to_block_start_0_0 ?param2))) (not (ontable ?param2)))
    :effect (and (not (available ?param1)) (not (clear ?param2)) (not (on ?param2 ?param3_0)) (not (at_ ?param2 ?param4 ?param5)) (moving_onblock_to_block ?param1 ?param2 ?param3_0 ?param4 ?param5 ?param6 ?param7) (clear ?param3_0))
  )
  (:action move_onblock_to_block_end
    :parameters ( ?param1 - agent ?param2 - block ?param3_0 - block ?param4 - pos ?param5 - pos ?param6 - pos ?param7 - pos)
    :precondition (and (moving_onblock_to_block ?param1 ?param2 ?param3_0 ?param4 ?param5 ?param6 ?param7) (clear ?param3_0))
    :effect (and (not (clear ?param3_0)) (not (moving_onblock_to_block ?param1 ?param2 ?param3_0 ?param4 ?param5 ?param6 ?param7)) (on ?param2 ?param3_0) (at_ ?param2 ?param6 ?param7) (clear ?param2) (available ?param1))
  )
)