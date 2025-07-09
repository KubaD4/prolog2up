(define (problem from_prolog-problem)
 (:domain from_prolog-domain)
 (:objects 
   b1 b2 - block
   x1 x2 - pos
   m1 - mela
   a1 - agent
   carota1 - vegetale
 )
 (:init (ontable b1) (ontable b2) (at b1 x1 x1) (at b2 x2 x2) (clear b1) (clear b2) (available a1) (intera m1) (cruda carota1))
 (:goal (and (ontable b2) (on b1 b2) (at b1 x2 x2) (at b2 x2 x2) (clear b1) (available a1) (morsa m1) (cotta carota1)))
)
