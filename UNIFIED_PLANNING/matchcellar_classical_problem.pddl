(define (problem matchcellar_classical-problem)
 (:domain matchcellar_classical-domain)
 (:objects
   m0 m1 m2 - match
   f0 f1 - fuse
   t0 t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 t11 t12 t13 t14 t15 t16 t17 t18 t19 - timestep
 )
 (:init (handfree) (current_time t0))
 (:goal (and (fuse_mended f0) (fuse_mended f1)))
)
