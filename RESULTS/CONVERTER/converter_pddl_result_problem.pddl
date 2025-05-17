(define (problem extracted_domain-problem)
 (:domain extracted_domain-domain)
 (:objects
   a1 - agent
   b1 b2 - block
   m1 - mela
   loc_1_1 loc_2_2 - location
   carota1 - vegetale
 )
 (:init (ontable b1) (ontable b2) (at_ b1 loc_1_1) (at_ b2 loc_2_2) (clear b1) (clear b2) (available a1) (intera m1) (cruda carota1))
 (:goal (and (ontable b2) (on b1 b2) (at_ b1 loc_2_2) (at_ b2 loc_2_2) (clear b1) (available a1) (morsa m1) (cotta carota1)))
)
