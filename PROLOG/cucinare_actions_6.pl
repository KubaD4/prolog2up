% File sperimentale: cucinare_actions_6.pl  
% OBIETTIVO: Testare correlazione actions vs Step 5 (UP Code Generation)
% BASELINE: cucinare.pl ha 3 azioni → questo file ha 6 azioni (doppio)
% MANTIENE: Stesso numero oggetti (4), stessa struttura logica

% Definizione di oggetti e tipi (INVARIATI rispetto a cucinare.pl)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Stato iniziale (INVARIATO)
init_state([
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  accesa(led)        % Aggiunto per supportare nuove azioni con luce
]).

% Stato goal (esteso per includere effetti delle nuove azioni)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  spenta(led)        % Goal aggiuntivo per testare nuove azioni
]).

% AZIONI: Raddoppiate da 3 a 6
% Mantengono pattern e complessità simili alla baseline

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

% NUOVA Azione 4: accendi_luce - Simile complessità alle azioni esistenti
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

% NUOVA Azione 5: spegni_luce - Simile complessità alle azioni esistenti  
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

% NUOVA Azione 6: pulisci_piano - Azione con complessità simile a cucina
action(pulisci_piano(Persona, Superficie),
  [pieno(Superficie)],
  [],
  [],
  [cuoco(Persona), piano(Superficie)],
  [
    del(pieno(Superficie)),
    add(vuoto(Superficie)),
    add(pulito(Superficie))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 4 (invariato)
% - Actions: 3 → 6 (100% aumento)
% - Pos_precond: 7 → ~14 (raddoppiate con le nuove azioni)
% - Neg_precond: 1 → 1 (invariato, solo sposta_qualsiasi ha wildcard)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato, nuove azioni hanno arietà ≤ 4)
%
% CORRELAZIONI ATTESE dai dati di benchmark:
% - Step 5 (UP Code): dovrebbe aumentare significativamente (corr: 0.541)
% - Step 7 (Planning): dovrebbe aumentare moderatamente (corr: 0.404)
% - Step 6 (PDDL): dovrebbe aumentare poco (corr: actions bassa)
% - Step 1-2: dovrebbero mostrare variazione limitata