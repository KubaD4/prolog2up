(define (problem blocks_world-problem)
  (:domain blocks_world-domain)
  (:objects
    b1 b2 b3 b4 b5 b6 - block
    pos_1_1 pos_2_2 pos_3_3 pos_10_10 - pos
    a1 a2 - agent
  )
  (:init
    (ontable b1)
    (on b4 b1)
    (at_ b1 pos_1_1)
    (at_ b4 pos_1_1)
    (clear b4)
    (ontable b2)
    (on b5 b2)
    (at_ b2 pos_2_2)
    (at_ b5 pos_2_2)
    (clear b5)
    (ontable b3)
    (on b6 b3)
    (at_ b3 pos_3_3)
    (at_ b6 pos_3_3)
    (clear b6)
    (available a1)
    (available a2)
  )
  (:goal
    (and (ontable b1) (ontable b2) (ontable b3) (ontable b4) (on b5 b4) (on b6 b3) (at_ b1 pos_1_1) (at_ b2 pos_2_2) (at_ b3 pos_3_3) (at_ b4 pos_10_10) (at_ b5 pos_10_10) (at_ b6 pos_3_3) (clear b1) (clear b2) (clear b5) (clear b6) (available a1) (available a2))
  )
)