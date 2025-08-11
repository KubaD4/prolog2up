% File sperimentale: cucinare_objects_12.pl
% OBIETTIVO: Testare correlazione objects vs Step 7 (Planning) e Step 6 (PDDL)
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 12 oggetti (triplo)
% MANTIENE: Stesso numero azioni (3), stessa struttura logica

% Definizione di oggetti e tipi (TRIPLICATI da 4 a 12)
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).           % NUOVO: terzo cuoco

cibo(pasta).
cibo(riso).
cibo(pizza).                % NUOVO: terzo cibo

strumento(pentola).
strumento(padella).
strumento(forno).           % NUOVO: terzo strumento

piano(tavolo).
piano(bancone).
piano(isola_cucina).        % NUOVO: terzo piano

luce(led).
luce(lampadina).
luce(spot).                 % NUOVO: terza luce

% Stato iniziale (esteso per 12 oggetti con pattern coerente)
init_state([
  % Stato per cuoco 1 (mario) - pattern originale
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stato per cuoco 2 (luigi) - pattern replicato
  crudo(riso),
  disponibile(padella),
  ha_fame(luigi),
  vuoto(bancone),
  
  % Stato per cuoco 3 (chef_anna) - pattern replicato
  crudo(pizza),
  disponibile(forno),
  ha_fame(chef_anna),
  vuoto(isola_cucina)
]).

% Stato goal (esteso per includere tutti i 12 oggetti)
goal_state([
  % Goal per cuoco 1 (mario)
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  
  % Goal per cuoco 2 (luigi)
  cotto(riso),
  soddisfatto(luigi),
  pieno(bancone),
  
  % Goal per cuoco 3 (chef_anna)
  cotto(pizza),
  soddisfatto(chef_anna),
  pieno(isola_cucina)
]).

% AZIONI: Stesso numero (3) e stessa struttura di cucinare.pl
% Solo i tipi ora hanno più istanze (4x più combinazioni possibili)

% Azione 1: cucina - IDENTICA alla versione originale
action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

% Azione 2: mangia - IDENTICA alla versione originale  
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

% Azione 3: sposta_qualsiasi - IDENTICA alla versione originale
action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [su(_, Strumento)],  % Wildcard negativa (stesso numero della baseline)
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 12 (200% aumento) ⭐⭐⭐
% - Actions: 3 → 3 (invariato)
% - Pos_precond: 7 → 7 (invariato per azione, ma molte più combinazioni)
% - Neg_precond: 1 → 1 (invariato)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE dai dati di benchmark originali:
% - Step 7 (Planning): dovrebbe aumentare MOLTO significativamente (corr: 0.736)
% - Step 6 (PDDL): dovrebbe aumentare MOLTO significativamente (corr: 0.702)
% - Piano minimo: 6 step (2 per ogni cuoco)
% - Spazio di ricerca: 3^3 = 27 possibili combinazioni base vs 1 originale