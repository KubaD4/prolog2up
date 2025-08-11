% File sperimentale: cucinare_objects_32.pl
% OBIETTIVO: Test scalabilità massima - stress test finale
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 32 oggetti (8x)
% ISOLAMENTO: SOLO objects aumentano, tutto il resto IDENTICO

% Definizione di oggetti e tipi (32 oggetti totali - 6-7 per tipo)
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).
cuoco(sous_chef_marco).
cuoco(pastry_chef_sara).
cuoco(grill_master_luca).

cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(lasagne).
cibo(minestrone).
cibo(carbonara).
cibo(risotto).

strumento(pentola).
strumento(padella).
strumento(forno).
strumento(mixer).
strumento(frullatore).
strumento(griglia).

piano(tavolo).
piano(bancone).
piano(isola_cucina).
piano(piano_servizio).
piano(piano_preparazione).
piano(piano_cottura).
piano(piano_assemblaggio).

luce(led).
luce(lampadina).
luce(spot).
luce(neon).
luce(faretto).
luce(lampada_work).

% Stato iniziale (pattern IDENTICO a cucinare.pl, replicato per 32 objects)
init_state([
  % Pattern base replicato 6 volte
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
  vuoto(piano_preparazione),
  
  crudo(carbonara),
  disponibile(griglia),
  ha_fame(grill_master_luca),
  vuoto(piano_cottura),
  
  % Oggetti extra per arrivare a 32
  crudo(risotto),
  vuoto(piano_assemblaggio)
]).

% Stato goal (esteso per 32 oggetti)
goal_state([
  % Goal per ogni gruppo principale
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
  pieno(piano_preparazione),
  
  cotto(carbonara),
  soddisfatto(grill_master_luca),
  pieno(piano_cottura),
  
  % Goal per oggetti extra
  cotto(risotto),
  pieno(piano_assemblaggio)
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
% - Objects: 4 → 32 (700% aumento - stress test)
% - Actions: 3 → 3 (INVARIATO)
% - Pos_precond: 7 → 7 (INVARIATO per azione)
% - Neg_precond: 1 → 1 (INVARIATO)
% - Wildcards: 1 → 1 (INVARIATO)
% - Max_arity: 4 → 4 (INVARIATO)
%
% IPOTESI CRITICA: Se crescita è esponenziale, questo file potrebbe:
% 1. Causare timeout nel planning (>300s)
% 2. Mostrare crescita drammatica vs objects_25
% 3. Dimostrare limiti pratici dell'approccio
% Piano minimo: 12-14 step (2 per ogni cuoco attivo)