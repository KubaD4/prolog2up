(define (problem blocks-problem)
  (:domain blocks-domain)
  (:objects
    b1 b2 b3 b4 b5 b6 - block
    loc_1_1 loc_2_2 loc_3_3 loc_10_10 - location
    a1 a2 - agent
  )
  (:init
    (ontable b1)
    (on b4 b1)
    (at_ b1 loc_1_1)
    (at_ b4 loc_1_1)
    (clear b4)
    (ontable b2)
    (on b5 b2)
    (at_ b2 loc_2_2)
    (at_ b5 loc_2_2)
    (clear b5)
    (ontable b3)
    (on b6 b3)
    (at_ b3 loc_3_3)
    (at_ b6 loc_3_3)
    (clear b6)
    (available a1)
    (available a2)
  )
  (:goal
    (and (ontable b1) (ontable b2) (ontable b3) (ontable b4) (on b5 b4) (on b6 b3) (at_ b1 loc_1_1) (at_ b2 loc_2_2) (at_ b3 loc_3_3) (at_ b4 loc_10_10) (at_ b5 loc_10_10) (at_ b6 loc_3_3) (clear b1) (clear b2) (clear b5) (clear b6) (available a1) (available a2))
  )
)