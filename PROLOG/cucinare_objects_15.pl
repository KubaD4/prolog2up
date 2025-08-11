% File sperimentale: cucinare_objects_15.pl
% OBIETTIVO: Test soglia critica - tra 12 e 16 objects
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 15 oggetti
% ISOLAMENTO: SOLO objects aumentano, tutto il resto IDENTICO

% Definizione di oggetti e tipi (15 oggetti totali)
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).

cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(lasagne).
cibo(minestrone).

strumento(pentola).
strumento(padella).
strumento(forno).
strumento(mixer).

piano(tavolo).
piano(bancone).
piano(isola_cucina).

luce(led).
luce(lampadina).

% Stato iniziale (pattern IDENTICO a cucinare.pl, replicato per 15 objects)
init_state([
  % Gruppo 1
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Gruppo 2  
  crudo(riso),
  disponibile(padella),
  ha_fame(luigi),
  vuoto(bancone),
  
  % Gruppo 3
  crudo(pizza),
  disponibile(forno),
  ha_fame(chef_anna),
  vuoto(isola_cucina),
  
  % Oggetti extra per arrivare a 15
  crudo(lasagne),
  crudo(minestrone),
  disponibile(mixer)
]).

% Stato goal (esteso per 15 oggetti)
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
  
  % Goal per oggetti extra
  cotto(lasagne),
  cotto(minestrone)
]).

% AZIONI: IDENTICHE a cucinare.pl (3 azioni, stessa struttura)
% NESSUNA modifica alla logica - solo più istanze disponibili

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
% - Objects: 4 → 15 (punto critico vicino a 16)
% - Actions: 3 → 3 (INVARIATO)
% - Pos_precond: 7 → 7 (INVARIATO per azione)
% - Neg_precond: 1 → 1 (INVARIATO)
% - Wildcards: 1 → 1 (INVARIATO)
% - Max_arity: 4 → 4 (INVARIATO)
%
% IPOTESI: Dovrebbe mostrare tempi di planning vicini a objects_16
% se la soglia critica è effettivamente intorno a 15-16 objects