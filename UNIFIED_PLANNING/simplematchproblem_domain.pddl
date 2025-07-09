(define (domain simplematchproblem-domain)
 (:requirements :strips :typing :negative-preconditions)
 (:types match fuse)
 (:predicates (handfree) (light_on) (match_used ?m - match) (fuse_mended ?f - fuse))
 (:action light_match
  :parameters ( ?m - match)
  :precondition (and (not (match_used ?m)) (not (light_on)))
  :effect (and (match_used ?m) (light_on)))
 (:action mend_fuse
  :parameters ( ?f - fuse)
  :precondition (and (handfree) (light_on) (not (fuse_mended ?f)))
  :effect (and (fuse_mended ?f)))
)
