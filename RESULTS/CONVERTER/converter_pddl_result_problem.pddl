(define (problem blocks-problem)
 (:domain blocks-domain)
 (:objects
   b1 b2 - block
   loc_1_1 loc_2_2 - location
   a1 - agent
 )
 (:init (ontable b1) (ontable b2) (at_ b1 loc_1_1 loc_1_1) (at_ b2 loc_2_2 loc_2_2) (clear b1) (clear b2) (available a1))
 (:goal (and (ontable b2) (on b1 b2) (at_ b1 loc_2_2 loc_2_2) (at_ b2 loc_2_2 loc_2_2) (clear b1) (available a1)))
)
