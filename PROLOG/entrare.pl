% Definizione di oggetti e tipi
persona(giovanni).
stanza(ingresso).
stanza(soggiorno).
porta(porta_ingresso).

% Stato iniziale
init_state([
  persona_fuori(giovanni),
  porta_chiusa(porta_ingresso),
  porta_collega(porta_ingresso, ingresso)
]).

% Stato goal
goal_state([
  persona_in(giovanni, soggiorno)
]).

% Definizione delle azioni
action(apri_porta(Persona, Porta),
  [porta_chiusa(Porta), persona_fuori(Persona)],
  [],
  [],
  [persona(Persona), porta(Porta)],
  [
    del(porta_chiusa(Porta)),
    add(porta_aperta(Porta))
  ]
).

action(entra(Persona, Porta, Stanza1, Stanza2),
  [persona_fuori(Persona), porta_aperta(Porta), porta_collega(Porta, Stanza1)],
  [],
  [],
  [persona(Persona), porta(Porta), stanza(Stanza1), stanza(Stanza2), Stanza1 \= Stanza2],
  [
    del(persona_fuori(Persona)),
    add(persona_in(Persona, Stanza1))
  ]
).

action(vai(Persona, Stanza1, Stanza2),
  [persona_in(Persona, Stanza1)],
  [],
  [],
  [persona(Persona), stanza(Stanza1), stanza(Stanza2), Stanza1 \= Stanza2],
  [
    del(persona_in(Persona, Stanza1)),
    add(persona_in(Persona, Stanza2))
  ]
).