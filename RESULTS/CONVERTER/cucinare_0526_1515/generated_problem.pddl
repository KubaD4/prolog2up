(define (problem from_prolog-problem)
 (:domain from_prolog-domain)
 (:objects
   mario - cuoco
   tavolo - piano
   pasta - cibo
   pentola - strumento
   led - luce
 )
 (:init (crudo pasta) (disponibile pentola) (ha_fame mario) (vuoto tavolo))
 (:goal (and (cotto pasta) (soddisfatto mario) (pieno tavolo)))
)
