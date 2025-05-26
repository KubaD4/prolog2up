(define (problem from_prolog-problem)
 (:domain from_prolog-domain)
 (:objects
   pasta - cibo
   tavolo - piano
   pentola - strumento
   mario - cuoco
   led - luce
 )
 (:init (crudo pasta) (disponibile pentola) (ha_fame mario) (vuoto tavolo))
 (:goal (and (cotto pasta) (soddisfatto mario) (pieno tavolo)))
)
