% Definizione di oggetti e tipi
cuoco(mario).
cibo(pasta).
strumento(pentola).

% Stato iniziale
init_state([
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario)
]).

% Stato goal
goal_state([
  cotto(pasta),
  soddisfatto(mario)
]).

% Definizione delle azioni
action(cucina(Persona, Cibo, Strumento),
  [crudo(Cibo), disponibile(Strumento)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento)],
  [
    del(crudo(Cibo)),
    add(cotto(Cibo))
  ]
).

action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).