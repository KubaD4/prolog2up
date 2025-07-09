(define (domain from_prolog-domain)
 (:requirements :strips :typing :negative-preconditions :existential-preconditions)
 (:types cibo strumento piano cuoco luce)
 (:predicates (crudo ?p0 - cibo) (disponibile ?p0 - strumento) (vuoto ?p0 - piano) (soddisfatto ?p0 - cuoco) (su ?p0 - piano ?p1 - strumento) (ha_fame ?p0 - cuoco) (cotto ?p0 - cibo) (pieno ?p0 - piano))
 (:action cucina
  :parameters ( ?Param1 - cuoco ?Param2 - cibo ?Param3 - strumento ?Param4 - piano)
  :precondition (and (crudo ?Param2) (disponibile ?Param3) (vuoto ?Param4))
  :effect (and (not (crudo ?Param2)) (not (vuoto ?Param4)) (cotto ?Param2) (pieno ?Param4)))
 (:action mangia
  :parameters ( ?Param1 - cuoco ?Param2 - cibo)
  :precondition (and (cotto ?Param2) (ha_fame ?Param1))
  :effect (and (not (ha_fame ?Param1)) (soddisfatto ?Param1)))
 (:action sposta_qualsiasi
  :parameters ( ?Param1 - cuoco ?Param2 - strumento ?Param3 - piano)
  :precondition (and (disponibile ?Param2) (vuoto ?Param3) (not (exists (?any_sposta_qualsiasi_0 - piano)
 (su ?any_sposta_qualsiasi_0 ?Param2))))
  :effect (and (not (disponibile ?Param2)) (not (vuoto ?Param3)) (su ?Param3 ?Param2)))
)
