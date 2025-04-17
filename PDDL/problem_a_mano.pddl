(define (problem blocks-problem)
  (:domain blocks-world)
  
  (:objects
    b1 b2 b3 b4 b5 b6 - block
    a1 a2 - agent
    loc1 loc2 loc3 loc10 - location
  )
  
  (:init
    ; Block positions
    (ontable b1) (ontable b2) (ontable b3)
    (on b4 b1) (on b5 b2) (on b6 b3)
    
    ; Block locations
    (at b1 loc1) (at b2 loc2) (at b3 loc3)
    (at b4 loc1) (at b5 loc2) (at b6 loc3)
    
    ; Clear blocks (nothing on top)
    (clear b4) (clear b5) (clear b6)
    
    ; Available agents
    (available a1) (available a2)
    
    ; Empty locations
    (empty loc10)
  )
  
  (:goal
    (and
      (ontable b1) (ontable b2)
      (ontable b3) (ontable b4)
      
      (on b5 b4) (on b6 b3)
      
      (at b1 loc1) (at b2 loc2) (at b3 loc3)
      (at b4 loc10) (at b5 loc10) (at b6 loc3)
      
      (clear b1) (clear b2)
      (clear b5) (clear b6)
      
      (available a1) (available a2)
    )
  )
)