% File sperimentale: cucinare_objects_16.pl
% OBIETTIVO: Testare correlazione objects vs Step 7-6 - TEST MASSIMO
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 16 oggetti (quadruplo)
% MANTIENE: Stesso numero azioni (3), stessa struttura logica

% Definizione di oggetti e tipi (QUADRUPLICATI da 4 a 16)
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).
cuoco(sous_chef_marco).     % NUOVO: quarto cuoco

cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(lasagne).              % NUOVO: quarto cibo

strumento(pentola).
strumento(padella).
strumento(forno).
strumento(wok).             % NUOVO: quarto strumento

piano(tavolo).
piano(bancone).
piano(isola_cucina).
piano(piano_servizio).      % NUOVO: quarto piano

luce(led).
luce(lampadina).
luce(spot).
luce(neon).                 % NUOVO: quarta luce

% Stato iniziale (esteso per 16 oggetti con pattern coerente)
init_state([
  % Stato per cuoco 1 (mario) - pattern originale
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stato per cuoco 2 (luigi)
  crudo(riso),
  disponibile(padella),
  ha_fame(luigi),
  vuoto(bancone),
  
  % Stato per cuoco 3 (chef_anna)
  crudo(pizza),
  disponibile(forno),
  ha_fame(chef_anna),
  vuoto(isola_cucina),
  
  % Stato per cuoco 4 (sous_chef_marco)
  crudo(lasagne),
  disponibile(wok),
  ha_fame(sous_chef_marco),
  vuoto(piano_servizio)
]).

% Stato goal (esteso per includere tutti i 16 oggetti)
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
  pieno(isola_cucina),
  
  % Goal per cuoco 4 (sous_chef_marco)
  cotto(lasagne),
  soddisfatto(sous_chef_marco),
  pieno(piano_servizio)
]).

% AZIONI: Stesso numero (3) e stessa struttura di cucinare.pl
% Ma ora con 4^4 = 256 possibili combinazioni base per la prima azione!

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
% - Objects: 4 → 16 (300% aumento) ⭐⭐⭐⭐ MASSIMO TEST
% - Actions: 3 → 3 (invariato)
% - Pos_precond: 7 → 7 (invariato per azione)
% - Neg_precond: 1 → 1 (invariato)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE (da dati benchmark):
% - Step 7 (Planning): dovrebbe aumentare DRASTICAMENTE (corr: 0.736)
% - Step 6 (PDDL): dovrebbe aumentare DRASTICAMENTE (corr: 0.702)
% - Piano minimo: 8 step (2 per ogni cuoco)
% - Spazio di ricerca: 4^3 = 64 possibili combinazioni base
% - QUESTO È IL TEST DEFINITIVO per la correlazione Objects vs Planning Time!