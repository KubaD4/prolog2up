(define (domain from_prolog-domain)
 (:requirements :strips :typing :negative-preconditions :existential-preconditions)
 (:types cuoco piano cibo strumento luce)
 (:predicates (soddisfatto ?p0 - cuoco) (vuoto ?p0_0 - piano) (ha_fame ?p0 - cuoco) (crudo ?p0_1 - cibo) (pieno ?p0_0 - piano) (su ?p0_0 - piano ?p1 - strumento) (disponibile ?p0_2 - strumento) (cotto ?p0_1 - cibo))
 (:action cucina
  :parameters ( ?param1 - cuoco ?param2 - cibo ?param3 - strumento ?param4 - piano)
  :precondition (and (crudo ?param2) (disponibile ?param3) (vuoto ?param4))
  :effect (and (not (crudo ?param2)) (not (vuoto ?param4)) (cotto ?param2) (pieno ?param4)))
 (:action mangia
  :parameters ( ?param1 - cuoco ?param2 - cibo)
  :precondition (and (cotto ?param2) (ha_fame ?param1))
  :effect (and (not (ha_fame ?param1)) (soddisfatto ?param1)))
 (:action sposta_qualsiasi
  :parameters ( ?param1 - cuoco ?param2_0 - strumento ?param3_0 - piano)
  :precondition (and (disponibile ?param2_0) (vuoto ?param3_0) (not (exists (?any_sposta_qualsiasi_0 - piano)
 (su ?any_sposta_qualsiasi_0 ?param2_0))))
  :effect (and (not (disponibile ?param2_0)) (not (vuoto ?param3_0)) (su ?param3_0 ?param2_0)))
)
