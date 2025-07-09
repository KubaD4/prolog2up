(define (domain from_prolog-domain)
 (:requirements :strips :typing :negative-preconditions :existential-preconditions)
 (:types block mela vegetale agent pos)
 (:predicates (ontable ?p0 - block) (intera ?p0 - mela) (clear ?p0 - block) (cruda ?p0 - vegetale) (on ?p0 - block ?p1 - block) (moving_table_to_block ?p0 - agent ?p1 - block ?p2 - block ?p3 - pos ?p4 - pos ?p5 - pos ?p6 - pos) (cotta ?p0 - vegetale) (available ?p0 - agent) (at ?p0 - block ?p1 - pos ?p2 - pos) (morsa ?p0 - mela))
 (:action move_table_to_block_start
  :parameters ( ?Param1 - agent ?Param2 - block ?Param3 - block ?Param4 - pos ?Param5 - pos ?Param6 - pos ?Param7 - pos)
  :precondition (and (available ?Param1) (ontable ?Param2) (at ?Param2 ?Param4 ?Param5) (at ?Param3 ?Param6 ?Param7) (clear ?Param3) (clear ?Param2) (not (exists (?any_move_table_to_block_start_0 - block)
 (on ?any_move_table_to_block_start_0 ?Param2))) (not (exists (?any_move_table_to_block_start_1 - block)
 (on ?Param2 ?any_move_table_to_block_start_1))) (not (exists (?any_move_table_to_block_start_0 - agent ?any_move_table_to_block_start_2 - block ?any_move_table_to_block_start_3 - pos ?any_move_table_to_block_start_4 - pos ?any_move_table_to_block_start_5 - pos ?any_move_table_to_block_start_6 - pos)
 (moving_table_to_block ?any_move_table_to_block_start_0 ?Param2 ?any_move_table_to_block_start_2 ?any_move_table_to_block_start_3 ?any_move_table_to_block_start_4 ?any_move_table_to_block_start_5 ?any_move_table_to_block_start_6))))
  :effect (and (not (available ?Param1)) (not (clear ?Param2)) (not (ontable ?Param2)) (not (at ?Param2 ?Param4 ?Param5)) (moving_table_to_block ?Param1 ?Param2 ?Param3 ?Param4 ?Param5 ?Param6 ?Param7)))
 (:action move_table_to_block_end
  :parameters ( ?Param1 - agent ?Param2 - block ?Param3 - block ?Param4 - pos ?Param5 - pos ?Param6 - pos ?Param7 - pos)
  :precondition (and (moving_table_to_block ?Param1 ?Param2 ?Param3 ?Param4 ?Param5 ?Param6 ?Param7) (clear ?Param3))
  :effect (and (not (clear ?Param3)) (not (moving_table_to_block ?Param1 ?Param2 ?Param3 ?Param4 ?Param5 ?Param6 ?Param7)) (on ?Param2 ?Param3) (at ?Param2 ?Param6 ?Param7) (clear ?Param2) (available ?Param1)))
 (:action mangia_mela
  :parameters ( ?Param1 - agent ?Param2 - mela)
  :precondition (and (intera ?Param2) (available ?Param1))
  :effect (and (not (intera ?Param2)) (not (available ?Param1)) (morsa ?Param2)))
 (:action cuoci
  :parameters ( ?Param1 - agent ?Param2 - vegetale)
  :precondition (and (available ?Param1) (cruda ?Param2))
  :effect (and (not (cruda ?Param2)) (cotta ?Param2)))
)
