% File sperimentale: cucinare_objects_25.pl
% OBIETTIVO: Test scalabilità oltre la soglia critica
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 25 oggetti
% ISOLAMENTO: SOLO objects aumentano, tutto il resto IDENTICO

% Definizione di oggetti e tipi (25 oggetti totali - 5 per tipo)
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).
cuoco(sous_chef_marco).
cuoco(pastry_chef_sara).

cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(lasagne).
cibo(minestrone).

strumento(pentola).
strumento(padella).
strumento(forno).
strumento(mixer).
strumento(frullatore).

piano(tavolo).
piano(bancone).
piano(isola_cucina).
piano(piano_servizio).
piano(piano_preparazione).

luce(led).
luce(lampadina).
luce(spot).
luce(neon).
luce(faretto).

% Stato iniziale (pattern IDENTICO a cucinare.pl, replicato per 25 objects)
init_state([
  % Pattern base replicato 5 volte
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  crudo(riso),
  disponibile(padella),
  ha_fame(luigi),
  vuoto(bancone),
  
  crudo(pizza),
  disponibile(forno),
  ha_fame(chef_anna),
  vuoto(isola_cucina),
  
  crudo(lasagne),
  disponibile(mixer),
  ha_fame(sous_chef_marco),
  vuoto(piano_servizio),
  
  crudo(minestrone),
  disponibile(frullatore),
  ha_fame(pastry_chef_sara),
  vuoto(piano_preparazione)
]).

% Stato goal (esteso per 25 oggetti)
goal_state([
  % Goal per ogni gruppo
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  
  cotto(riso),
  soddisfatto(luigi),
  pieno(bancone),
  
  cotto(pizza),
  soddisfatto(chef_anna),
  pieno(isola_cucina),
  
  cotto(lasagne),
  soddisfatto(sous_chef_marco),
  pieno(piano_servizio),
  
  cotto(minestrone),
  soddisfatto(pastry_chef_sara),
  pieno(piano_preparazione)
]).

% AZIONI: IDENTICHE a cucinare.pl (3 azioni, stessa struttura)
% NESSUNA modifica alla logica - solo molte più istanze disponibili

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

action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 25 (oltre soglia critica - 56% aumento)
% - Actions: 3 → 3 (INVARIATO)
% - Pos_precond: 7 → 7 (INVARIATO per azione)
% - Neg_precond: 1 → 1 (INVARIATO)
% - Wildcards: 1 → 1 (INVARIATO)
% - Max_arity: 4 → 4 (INVARIATO)
%
% IPOTESI: Se crescita è esponenziale, dovremmo vedere tempi
% significativamente > objects_16 (possibile timeout o crescita drammatica)
% Piano minimo: 10 step (2 per ogni cuoco)