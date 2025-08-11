% File sperimentale: cucinare_objects_8.pl
% OBIETTIVO: Testare correlazione objects vs Step 7 (Planning) e Step 6 (PDDL)
% BASELINE: cucinare.pl ha 4 oggetti → questo file ha 8 oggetti (doppio)
% MANTIENE: Stesso numero azioni (3), stessa struttura logica, stesse precondizioni

% Definizione di oggetti e tipi (RADDOPPIATI da 4 a 8)
cuoco(mario).
cuoco(luigi).               % NUOVO: secondo cuoco

cibo(pasta).
cibo(riso).                 % NUOVO: secondo cibo

strumento(pentola).
strumento(padella).         % NUOVO: secondo strumento

piano(tavolo).
piano(bancone).             % NUOVO: secondo piano

luce(led).
luce(lampadina).            % NUOVO: seconda luce

% Stato iniziale (esteso per nuovi oggetti)
init_state([
  % Stato originale per oggetti esistenti
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stato per nuovi oggetti (pattern coerente)
  crudo(riso),
  disponibile(padella),
  ha_fame(luigi),
  vuoto(bancone)
]).

% Stato goal (esteso per includere nuovi oggetti)
goal_state([
  % Goal originali
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  
  % Goal per nuovi oggetti
  cotto(riso),
  soddisfatto(luigi),
  pieno(bancone)
]).

% AZIONI: Stesso numero (3) e stessa struttura di cucinare.pl
% Solo i tipi ora hanno più istanze

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
% Questa azione contiene il wildcard che abbiamo nella baseline
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
% - Objects: 4 → 8 (100% aumento)
% - Actions: 3 → 3 (invariato)
% - Pos_precond: 7 → 7 (invariato per azione, ma più combinazioni possibili)
% - Neg_precond: 1 → 1 (invariato)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE dai dati di benchmark:
% - Step 7 (Planning): dovrebbe aumentare significativamente (corr: 0.736)
% - Step 6 (PDDL): dovrebbe aumentare significativamente (corr: 0.702)
% - Step 5 (UP Code): dovrebbe aumentare poco (corr: objects bassa)
% - Step 1-2: dovrebbero rimanere simili (analisi costanza)