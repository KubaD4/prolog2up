(define (problem extracted_domain-problem)
 (:domain extracted_domain-domain)
 (:objects
   pasta - cibo
   pentola - strumento
   mario - cuoco
 )
 (:init (crudo pasta) (disponibile pentola) (ha_fame mario))
 (:goal (and (cotto pasta) (soddisfatto mario)))
)
