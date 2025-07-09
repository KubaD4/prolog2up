(define (problem from_prolog-problem)
 (:domain from_prolog-domain)
 (:objects
   b1 b2 - block
   pos_1 pos_2 - pos
   a1 - agent
   m1 - mela
   carota1 - vegetale
 )
 (:init (ontable b1) (ontable b2) (at_ b1 pos_1 pos_1) (at_ b2 pos_2 pos_2) (clear b1) (clear b2) (available a1) (intera m1) (cruda carota1))
 (:goal (and (ontable b2) (on b1 b2) (at_ b1 pos_2 pos_2) (at_ b2 pos_2 pos_2) (clear b1) (available a1) (morsa m1) (cotta carota1)))
)
