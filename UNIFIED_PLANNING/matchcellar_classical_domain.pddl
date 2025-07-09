(define (domain matchcellar_classical-domain)
  (:requirements :strips :typing :negative-preconditions)
  (:types
    match fuse timestep
  )
  (:predicates
    (handfree)
    (light)
    (match_used ?m - match)
    (fuse_mended ?f - fuse)
    (current_time ?t - timestep)
    (light_until ?t - timestep)
    (mending_started ?f - fuse ?t - timestep)
    (mending_duration ?f - fuse ?duration_ - timestep)
  )
  (:action light_match
    :parameters ( ?m - match ?t_start - timestep ?t_end - timestep)
    :precondition (and (not (match_used ?m)) (current_time ?t_start) (not (light)))
    :effect (and (match_used ?m) (light) (light_until ?t_end))
  )
  (:action start_mending
    :parameters ( ?f - fuse ?t - timestep)
    :precondition (and (handfree) (light) (current_time ?t) (not (fuse_mended ?f)))
    :effect (and (not (handfree)) (mending_started ?f ?t))
  )
  (:action complete_mending
    :parameters ( ?f - fuse ?t_start - timestep ?t_current - timestep)
    :precondition (and (mending_started ?f ?t_start) (current_time ?t_current) (light))
    :effect (and (fuse_mended ?f) (handfree) (not (mending_started ?f ?t_start)))
  )
  (:action advance_time
    :parameters ( ?t_from - timestep ?t_to - timestep)
    :precondition (and (current_time ?t_from))
    :effect (and (not (current_time ?t_from)) (current_time ?t_to))
  )
  (:action light_expires
    :parameters ( ?t - timestep)
    :precondition (and (light) (light_until ?t) (current_time ?t))
    :effect (and (not (light)) (not (light_until ?t)))
  )
)