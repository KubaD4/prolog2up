% File sperimentale: cucinare_objects_13.pl
% OBIETTIVO: Test soglia critica - tra 12 e 16 objects
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 13 oggetti
% ISOLAMENTO: SOLO objects aumentano, tutto il resto IDENTICO

% Definizione di oggetti e tipi (13 oggetti totali)
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).

cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(lasagne).

strumento(pentola).
strumento(padella).
strumento(forno).

piano(tavolo).
piano(bancone).
piano(isola_cucina).

luce(led).

% Stato iniziale (pattern IDENTICO a cucinare.pl, replicato per 13 objects)
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
  
  % Oggetto extra per arrivare a 13
  crudo(lasagne)
]).

% Stato goal (esteso per 13 oggetti)
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
  
  % Goal per oggetto extra
  cotto(lasagne)
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
% - Objects: 4 → 13 (punto intermedio critico)
% - Actions: 3 → 3 (INVARIATO)
% - Pos_precond: 7 → 7 (INVARIATO per azione)
% - Neg_precond: 1 → 1 (INVARIATO)
% - Wildcards: 1 → 1 (INVARIATO)
% - Max_arity: 4 → 4 (INVARIATO)
%
% IPOTESI: Se soglia critica è tra 12-16, questo dovrebbe mostrare
% l'inizio dell'aumento significativo dei tempi di planning