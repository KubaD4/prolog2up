(define (domain extracted_domain-domain)
 (:requirements :strips :typing)
 (:types porta stanza persona)
 (:predicates (porta_aperta ?p1 - porta) (porta_collega ?p1 - porta ?s2 - stanza) (porta_chiusa ?p1 - porta) (persona_in ?p1_0 - persona ?s2 - stanza) (persona_fuori ?p1_0 - persona))
 (:action apri_porta
  :parameters ( ?p0 - persona ?p1 - porta)
  :precondition (and (porta_chiusa ?p1) (persona_fuori ?p0)))
 (:action entra
  :parameters ( ?p0 - persona ?p1 - porta ?p2 - stanza ?p3 - stanza)
  :precondition (and (persona_fuori ?p0) (porta_aperta ?p1) (porta_collega ?p1 ?p2)))
 (:action vai
  :parameters ( ?p0 - persona ?p1_1 - stanza ?p2 - stanza)
  :precondition (and (persona_in ?p0 ?p1_1)))
)
