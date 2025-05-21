(define (domain extracted_domain-domain)
 (:requirements :strips :typing)
 (:types cibo strumento cuoco)
 (:predicates (cotto ?c1 - cibo) (disponibile ?s1 - strumento) (soddisfatto ?c1_0 - cuoco) (crudo ?c1 - cibo) (ha_fame ?c1_0 - cuoco))
 (:action cucina
  :parameters ( ?p0 - cuoco ?p1 - cibo ?p2 - strumento)
  :precondition (and (crudo ?p1) (disponibile ?p2)))
 (:action mangia
  :parameters ( ?p0 - cuoco ?p1 - cibo)
  :precondition (and (cotto ?p1) (ha_fame ?p0)))
)
