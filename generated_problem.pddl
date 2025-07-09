(define (problem from_prolog-problem)
  (:domain from_prolog-domain)
  (:objects
    b1 b2 b3 b4 b5 b6 - block
    x1 x10 x2 x3 - pos
    a1 a2 - agent
  )
  (:init
    (ontable b1)
    (ontable b2)
    (ontable b3)
    (on b4 b1)
    (on b5 b2)
    (on b6 b3)
    (at_ b1 x1 x1)
    (at_ b2 x2 x2)
    (at_ b3 x3 x3)
    (at_ b4 x1 x1)
    (at_ b5 x2 x2)
    (at_ b6 x3 x3)
    (clear b4)
    (clear b5)
    (clear b6)
    (available a1)
    (available a2)
  )
  (:goal
    (and (ontable b1) (ontable b2) (ontable b3) (ontable b4) (on b5 b4) (on b6 b3) (at_ b1 x1 x1) (at_ b2 x2 x2) (at_ b3 x3 x3) (at_ b4 x10 x10) (at_ b5 x10 x10) (at_ b6 x3 x3) (clear b1) (clear b2) (clear b5) (clear b6) (available a1) (available a2))
  )
)