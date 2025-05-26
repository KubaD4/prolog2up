(define (problem from_prolog-problem)
 (:domain from_prolog-domain)
 (:objects
   tavolo - piano
   pentola - strumento
   mario - cuoco
   pasta - cibo
   led - luce
 )
 (:init (crudo pasta) (disponibile pentola) (ha_fame mario) (vuoto tavolo))
 (:goal (and (cotto pasta) (soddisfatto mario) (pieno tavolo)))
)
