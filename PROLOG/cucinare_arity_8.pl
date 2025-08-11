% File sperimentale: cucinare_arity_8.pl
% OBIETTIVO: Testare correlazione max_arity vs Step 7 (Planning)
% BASELINE: cucinare.pl ha max_arity=4 → questo file ha max_arity=8
% STRATEGIA: Parametri dummy che NON cambiano la logica di base

% Definizione di oggetti e tipi (IDENTICI a cucinare.pl + dummy)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Tipi dummy per arità extra (non influenzano la logica)
dummy1(d1).
dummy2(d2).
dummy3(d3).

% Stato iniziale (IDENTICO a cucinare.pl + dummy sempre true)
init_state([
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Dummy states (sempre veri, non bloccano mai le azioni)
  dummy_ok(d1),
  dummy_ok(d2),
  dummy_ok(d3)
]).

% Stato goal (IDENTICO a cucinare.pl)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo)
]).

% AZIONI: Stesso numero (3) e STESSA LOGICA ESATTA, solo parametri dummy extra

% Azione 1: cucina_extended - ARIETÀ 8 (vs 4 originale)
% Aggiunge 4 parametri dummy che non cambiano il comportamento
action(cucina_extended(Persona, Cibo, Strumento, Tavolo, D1, D2, D3, D4),
  [
    % Precondizioni IDENTICHE a cucinare.pl
    crudo(Cibo), 
    disponibile(Strumento), 
    vuoto(Tavolo),
    
    % Precondizioni dummy (sempre soddisfatte)
    dummy_ok(D1),
    dummy_ok(D2),
    dummy_ok(D3)
  ],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo), 
   dummy1(D1), dummy2(D2), dummy3(D3), dummy1(D4)],
  [
    % Effetti IDENTICI a cucinare.pl (dummy non cambiano)
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

% Azione 2: mangia_extended - ARIETÀ 6 (vs 2 originale)
action(mangia_extended(Persona, Cibo, D1, D2, D3, D4),
  [
    % Precondizioni IDENTICHE a cucinare.pl
    cotto(Cibo), 
    ha_fame(Persona),
    
    % Precondizioni dummy (sempre soddisfatte)
    dummy_ok(D1),
    dummy_ok(D2)
  ],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), dummy1(D1), dummy2(D2), dummy3(D3), dummy1(D4)],
  [
    % Effetti IDENTICI a cucinare.pl
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Azione 3: sposta_qualsiasi_extended - ARIETÀ 7 (vs 3 originale)
action(sposta_qualsiasi_extended(Persona, Strumento, Destinazione, D1, D2, D3, D4),
  [
    % Precondizioni IDENTICHE a cucinare.pl
    disponibile(Strumento), 
    vuoto(Destinazione),
    
    % Precondizioni dummy (sempre soddisfatte)
    dummy_ok(D1),
    dummy_ok(D2)
  ],
  [
    % Wildcard IDENTICA a cucinare.pl
    su(_, Strumento)
  ],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento), 
   dummy1(D1), dummy2(D2), dummy3(D3), dummy1(D4)],
  [
    % Effetti IDENTICI a cucinare.pl
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 7 (aggiunti 3 dummy)
% - Actions: 3 → 3 (invariato)
% - Pos_precond: 7 → ~13 (aggiunte precondizioni dummy sempre vere)
% - Neg_precond: 1 → 1 (invariato)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 8 (100% aumento) ⭐⭐
% - Avg_arity: 3.0 → ~7.0 (aumento drastico)
%
% LOGICA: IDENTICA a cucinare.pl, piano di soluzione:
% 1. cucina_extended(mario, pasta, pentola, tavolo, d1, d2, d3, d1)
% 2. mangia_extended(mario, pasta, d1, d2, d3, d1)
% Piano minimo: 2 step (come cucinare.pl)