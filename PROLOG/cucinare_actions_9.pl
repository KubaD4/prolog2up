% File sperimentale: cucinare_actions_9.pl  
% OBIETTIVO: Testare correlazione actions vs Step 5 (UP Code Generation)
% BASELINE: cucinare.pl ha 3 azioni → questo file ha 9 azioni (triplo)
% MANTIENE: Stesso numero oggetti (4), stessa struttura logica

% Definizione di oggetti e tipi (INVARIATI rispetto a cucinare.pl)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).
stato(attivo).
stato(inattivo).

% Stato iniziale (esteso per supportare tutte le nuove azioni)
init_state([
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  accesa(led),
  temperatura_alta(inattivo),    % Per azioni di controllo temperatura
  timer_attivo(inattivo)         % Per azioni con timer
]).

% Stato goal (esteso per dimostrare l'uso di tutte le azioni)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  spenta(led),
  temperatura_alta(attivo),
  timer_attivo(attivo)
]).

% AZIONI: Triplicate da 3 a 9
% Mantengono pattern e complessità simili alla baseline

% === AZIONI ORIGINALI (identiche a cucinare.pl) ===

% Azione 1: cucina - IDENTICA alla baseline
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

% Azione 2: mangia - IDENTICA alla baseline
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

% Azione 3: sposta_qualsiasi - IDENTICA alla baseline (con wildcard)
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

% === NUOVE AZIONI 4-6 (Gruppo Illuminazione) ===

% Azione 4: accendi_luce
action(accendi_luce(Persona, Illuminazione),
  [spenta(Illuminazione)],
  [],
  [],
  [cuoco(Persona), luce(Illuminazione)],
  [
    del(spenta(Illuminazione)),
    add(accesa(Illuminazione))
  ]
).

% Azione 5: spegni_luce
action(spegni_luce(Persona, Illuminazione),
  [accesa(Illuminazione)],
  [],
  [],
  [cuoco(Persona), luce(Illuminazione)],
  [
    del(accesa(Illuminazione)),
    add(spenta(Illuminazione))
  ]
).

% Azione 6: regola_intensita_luce
action(regola_intensita_luce(Persona, Illuminazione),
  [accesa(Illuminazione)],
  [],
  [],
  [cuoco(Persona), luce(Illuminazione)],
  [
    add(intensita_regolata(Illuminazione))
  ]
).

% === NUOVE AZIONI 7-9 (Gruppo Controllo) ===

% Azione 7: aumenta_temperatura
action(aumenta_temperatura(Persona, Strumento),
  [disponibile(Strumento), temperatura_alta(inattivo)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(temperatura_alta(inattivo)),
    add(temperatura_alta(attivo))
  ]
).

% Azione 8: diminuisci_temperatura  
action(diminuisci_temperatura(Persona, Strumento),
  [disponibile(Strumento), temperatura_alta(attivo)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(temperatura_alta(attivo)),
    add(temperatura_alta(inattivo))
  ]
).

% Azione 9: avvia_timer
action(avvia_timer(Persona, Strumento),
  [disponibile(Strumento), timer_attivo(inattivo)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(timer_attivo(inattivo)),
    add(timer_attivo(attivo))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 4 (invariato)
% - Actions: 3 → 9 (triplo) ⭐
% - Pos_precond: 7 → ~21 (triplo con le nuove azioni)
% - Neg_precond: 1 → 1 (invariato, solo sposta_qualsiasi ha wildcard)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE dai dati di benchmark:
% - Step 5 (UP Code): dovrebbe aumentare significativamente vs actions_6
% - Step 7 (Planning): dovrebbe aumentare moderatamente vs actions_6