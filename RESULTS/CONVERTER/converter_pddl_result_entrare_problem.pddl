(define (problem extracted_domain-problem)
 (:domain extracted_domain-domain)
 (:objects
   porta_ingresso - porta
   ingresso soggiorno - stanza
   giovanni - persona
 )
 (:init (persona_fuori giovanni) (porta_chiusa porta_ingresso) (porta_collega porta_ingresso ingresso))
 (:goal (and (persona_in giovanni soggiorno)))
)
