(define (problem simplematchproblem-problem)
 (:domain simplematchproblem-domain)
 (:objects
   match0 match1 - match
   fuse0 fuse1 - fuse
 )
 (:init (handfree))
 (:goal (and (fuse_mended fuse0) (fuse_mended fuse1)))
)
